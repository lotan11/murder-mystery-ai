"""Reconcile GitHub facts into assignment issues and a persistent dashboard."""
import base64
import json
import re
from pathlib import Path

from .core import MARKER, approval_digest, dashboard, evaluate_pr, parse_task, task_body, validate_review, validate_task


def combined_verified(api, evidence, head, base):
    if not evidence or evidence.get("head") != head or evidence.get("base") != base:
        return False
    run = api.request(f"actions/runs/{int(evidence['run_id'])}")
    if (run.get("head_sha") != evidence["commit"] or run.get("conclusion") != "success"
            or run.get("path") != ".github/workflows/ci.yml"
            or run.get("head_repository", {}).get("full_name") != api.repository):
        return False
    commit = api.request(f"commits/{evidence['commit']}")
    return {head, base} <= {parent["sha"] for parent in commit.get("parents", [])}


def reconcile(api, config, write=False):
    base = api.request("branches/main")["commit"]["sha"]
    pulls = api.pages("pulls?state=open")
    indexed = {item["number"]: item for item in pulls}
    for number in config["tracked_pull_requests"]:
        indexed[number] = api.request(f"pulls/{number}")
    issues = [item for item in api.pages("issues?state=all&labels=agent-network") if "pull_request" not in item]
    tasks, review_requests, observations = [], [], []
    trusted_reviewers = []
    for login in config["independent_reviewers"]:
        if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", login):
            raise ValueError("Invalid configured reviewer login")
        permission = api.request(f"collaborators/{login}/permission")
        if permission.get("permission") in {"write", "maintain", "admin"}:
            trusted_reviewers.append(login)
    for number in sorted(indexed):
        # List responses may have unknown mergeability. Fetch each current PR explicitly.
        pr = api.request(f"pulls/{number}")
        head = pr["head"]["sha"]
        checks = api.pages(f"commits/{head}/check-runs")
        reviews = api.pages(f"pulls/{number}/reviews")
        evidence = config.get("combined_evidence", {}).get(str(number))
        combined = combined_verified(api, evidence, head, base)
        evaluation = evaluate_pr(pr, checks, reviews, base, combined, trusted_reviewers)
        qa_id = f"qa-review:{number}"
        qa_passed = bool(pr.get("merged")) or (bool(evaluation["approvals"]) and not evaluation.get("failures") and not any(
            "verify check" in reason or "change request" in reason for reason in evaluation["blockers"]))
        tasks.append({"id": qa_id, "title": f"Independent QA and regression review for PR #{number}",
                      "owner": "qa", "priority": "P0", "status": "completed" if qa_passed else "review",
                      "acceptance": ["Review current-head code and targeted/full CI evidence",
                                     "Check privacy, saved-room compatibility and approved Lewis continuity",
                                     "Independent reviewer records current-head GitHub approval or actionable defects"],
                      "blockers": [] if qa_passed else ["Independent current-head approval and successful checks required"],
                      "dependencies": [], "pull_request": number, "head": head, "base": base})
        observations.append({"pr": number, "url": pr["html_url"], "head": head,
                             "base_snapshot": pr["base"]["sha"], "current_main": base,
                             "mergeable": pr.get("mergeable"), "combined_verified": combined,
                             "approvals": evaluation["approvals"]})
        task = {"id": f"pr:{number}", "title": f"Coordinate PR #{number}: {pr['title']}"[:240],
                "owner": "integration", "priority": "P0" if number in config["tracked_pull_requests"] else "P1",
                "status": evaluation["status"], "acceptance": [
                    "Current-head CI passes", "Independent current-head review passes",
                    "Combined game/Listener/avatar/interface regression evidence matches current main and PR",
                    "Paid transcription remains disabled by default", "Obtain explicit owner approval before any merge"],
                "blockers": evaluation["blockers"], "dependencies": [qa_id], "pull_request": number,
                "head": head, "base": base, "issue_url": None}
        if number == 2:
            contents = api.request(f"contents/.env.example?ref={head}")
            text = base64.b64decode(contents["content"]).decode("utf-8")
            defaults = {line.split("=", 1)[0]: line.split("=", 1)[1].strip() for line in text.splitlines() if "=" in line and not line.startswith("#")}
            task["paid_transcription_default_disabled"] = all(defaults.get(key) == "false" for key in
                ("MYSTERY_TRANSCRIPTION_ENABLED", "MYSTERY_ALLOW_PAID_TRANSCRIPTION"))
            if not task["paid_transcription_default_disabled"]:
                task["status"] = "blocked"
                task["blockers"].append("Repository transcription defaults are not both disabled")
        tasks.append(task)
        if pr.get("state") == "open":
            requested = {item["login"] for item in pr.get("requested_reviewers", [])}
            reviewed = {item["user"]["login"] for item in reviews if item.get("commit_id") == head}
            candidates = [login for login in trusted_reviewers if login != pr["user"]["login"]
                          and login not in requested | reviewed]
            if candidates:
                review_requests.append({"pr": number, "reviewers": candidates})
                if write:
                    api.request(f"pulls/{number}/requested_reviewers", "POST", {"reviewers": candidates})
        for failure in evaluation.get("failures", []):
            tasks.append({"id": f"repair:{number}:{head}:{failure['id']}",
                "title": f"Investigate verified CI failure on PR #{number}: {failure['name']}"[:240],
                "owner": "development", "priority": "P0", "status": "queued",
                "acceptance": [f"Inspect failing check {failure.get('html_url', '')}",
                               "Reproduce and repair the failing test without weakening coverage",
                               "Submit tested PR and obtain independent review"],
                "blockers": [], "dependencies": [], "head": head, "pull_request": number,
                "evidence_url": failure.get("html_url"), "failure_conclusion": failure["conclusion"]})
    generated = {task["id"] for task in tasks}
    for issue in issues:
        if not (issue.get("body") or "").startswith(MARKER):
            continue
        try:
            task = parse_task(issue["body"])
        except (ValueError, IndexError, KeyError):
            continue  # Human edits cannot become executable instructions.
        if task["id"] not in generated:
            task["issue_url"] = issue["html_url"]
            if issue["state"] == "closed":
                task["status"] = "completed"
            tasks.append(task)
    by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        unresolved = [dep for dep in task.get("dependencies", []) if dep not in by_id or by_id[dep]["status"] != "completed"]
        if unresolved:
            task["status"] = "blocked"
            task["blockers"] = sorted(set(task.get("blockers", []) + ["Unresolved dependency: " + dep for dep in unresolved]))
    status = {"version": 1, "repository": api.repository, "deadline": config["deadline"],
              "timezone": config["timezone"], "main": base, "policy": config["policy"],
              "tasks": tasks, "pull_requests": observations, "review_requests": review_requests,
              "coding_execution": "Explicit local invocation only; no unattended paid model calls",
              "event_automation": "Workflow active only after approved installation on default branch"}
    if write:
        labels = api.pages("labels")
        if not any(label["name"] == "agent-network" for label in labels):
            api.request("labels", "POST", {"name": "agent-network", "color": "5319e7", "description": "Agent-network assignments and status"})
        for task in tasks:
            # Do not rewrite ordinary human-authored tasks or their accepted scope.
            if task["id"].startswith(("pr:", "repair:", "qa-review:")):
                issue = api.upsert_issue(task["id"], task["title"], task_body(task), issues)
                task["issue_url"] = issue["html_url"]
        api.upsert_issue("dashboard", "Agent network: project status dashboard", dashboard(status), issues)
    return status


def record_task(api, task, write=False):
    validate_task(task)
    if task["id"].startswith(("pr:", "repair:", "qa-review:")):
        raise ValueError("Reserved coordinator task identifier")
    if write:
        issues = api.pages("issues?state=all&labels=agent-network")
        return api.upsert_issue(task["id"], task["title"], task_body(task), issues)
    return task


def record_review(api, number, result, write=False):
    pr = api.request(f"pulls/{number}")
    base = api.request("branches/main")["commit"]["sha"]
    validate_review(result, pr["head"]["sha"], base, pr["user"]["login"])
    # CLI identity is verified by GitHub, never by a supplied JSON reviewer string.
    import subprocess
    identity = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True,
                              text=True, encoding="utf-8", check=True, timeout=30).stdout.strip()
    if identity != result["reviewer"]:
        raise ValueError("Review identity does not match authenticated GitHub user")
    body = "<!-- agent-network-review:v1 -->\n```json\n" + json.dumps(result, indent=2) + "\n```"
    if write:
        api.request(f"issues/{number}/comments", "POST", {"body": body})
        if result["verdict"] == "fail":
            task = {"id": f"qa:{number}:{pr['head']['sha']}", "title": f"Repair QA finding on PR #{number}",
                    "owner": "development", "priority": "P0", "status": "queued",
                    "acceptance": [result["summary"], "Reproduce defect, add regression and request independent verification"],
                    "blockers": [], "dependencies": [], "evidence_url": result["evidence_url"]}
            record_task(api, task, write=True)
    # A recorded QA pass never substitutes for GitHub's independent APPROVED review.
    return result


def approved_task(api, number, config):
    issue = api.request(f"issues/{number}")
    task = parse_task(issue["body"])
    if issue.get("state") != "open" or task["owner"] != "development" or task["status"] not in {"queued", "approved"}:
        raise ValueError("Development task must be open, eligible and assigned to development")
    if task.get("dependencies"):
        completed = set()
        for other in api.pages("issues?state=all&labels=agent-network"):
            try:
                record = parse_task(other.get("body", ""))
            except (ValueError, KeyError, IndexError):
                continue
            if other["state"] == "closed":
                completed.add(record["id"])
        if not set(task["dependencies"]) <= completed:
            raise ValueError("Development task has unresolved dependencies")
    base = api.request("branches/main")["commit"]["sha"]
    if task.get("approved_head") != base:
        raise ValueError("Development approval must match current main")
    comments = api.pages(f"issues/{number}/comments")
    for comment in reversed(comments):
        if comment["user"]["login"] not in config["development_approvers"]:
            continue
        try:
            record = json.loads(comment["body"].split("<!-- agent-network-approval:v1 -->\n", 1)[1])
        except (ValueError, IndexError):
            continue
        if record.get("task_digest") == approval_digest(task) and record.get("head") == base:
            return {**task, "id": str(number), "status": "approved", "approved_by": comment["user"]["login"],
                    "approval_verified": True, "issue_url": issue["html_url"]}
    raise ValueError("No matching maintainer-authored revision/scope-bound approval comment")
