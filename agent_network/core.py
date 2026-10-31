"""Pure, fail-closed coordination decisions. GitHub remains the source of facts."""
import hashlib
import json
import re

ROLES = {"orchestrator", "development", "qa", "integration"}
STATUSES = {"queued", "approved", "in_progress", "review", "blocked", "integration_ready", "completed"}
MARKER = "<!-- agent-network:v1 -->"


def validate_task(task):
    if not isinstance(task, dict):
        raise ValueError("Task must be an object")
    for field in ("id", "title", "owner", "priority", "status", "acceptance"):
        if field not in task:
            raise ValueError(f"Task requires {field}")
    if not isinstance(task["id"], str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9:_-]{0,140}", task["id"]):
        raise ValueError("Invalid task id")
    if not isinstance(task["title"], str) or not task["title"].strip() or len(task["title"]) > 240:
        raise ValueError("Task title required (at most 240 characters)")
    if not isinstance(task["owner"], str) or not isinstance(task["status"], str) or task["owner"] not in ROLES or task["status"] not in STATUSES:
        raise ValueError("Unknown role/status")
    if not isinstance(task["priority"], str) or task["priority"] not in {"P0", "P1", "P2"}:
        raise ValueError("Unknown priority")
    if not isinstance(task["acceptance"], list) or not task["acceptance"] or any(
        not isinstance(item, str) or not item.strip() for item in task["acceptance"]
    ):
        raise ValueError("Acceptance criteria must be nonempty strings")
    for field in ("dependencies", "allowed_paths", "blockers"):
        if field in task and (not isinstance(task[field], list) or any(not isinstance(item, str) for item in task[field])):
            raise ValueError(f"{field} must be a list of strings")
    return task


def task_body(task):
    validate_task(task)
    criteria = "\n".join(f"- [ ] {item}" for item in task["acceptance"])
    blockers = "\n".join(f"- {item}" for item in task.get("blockers", [])) or "None recorded."
    return (f"{MARKER}\n## {task['title']}\n\nOwner: **{task['owner']}** | "
            f"Priority: **{task['priority']}** | Status: **{task['status']}**\n\n"
            f"### Acceptance\n{criteria}\n\n### Blockers\n{blockers}\n\n"
            "Machine record (authoritative fields; approvals require separate trusted evidence):\n"
            f"```json\n{json.dumps(task, indent=2, sort_keys=True)}\n```\n")


def parse_task(body):
    if not isinstance(body, str) or not body.startswith(MARKER):
        raise ValueError("Not an agent-network record")
    # Human-rendered PR titles/criteria can contain fences. Only the final
    # generated machine block is authoritative; JSON strings escape newlines.
    data = body.rsplit("\n```json\n", 1)[1].split("\n```", 1)[0]
    return validate_task(json.loads(data))


def approval_digest(task):
    fields = {key: task.get(key) for key in ("id", "title", "owner", "priority", "acceptance", "allowed_paths", "approved_head", "dependencies")}
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def independent_approvals(reviews, head, author):
    latest = {}
    for review in sorted(reviews, key=lambda item: item.get("submitted_at") or ""):
        if review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[review["user"]["login"]] = review
    return [login for login, item in latest.items() if login != author
            and item.get("commit_id") == head and item["state"] == "APPROVED"]


def evaluate_pr(pr, checks, reviews, base, combined=False, trusted_reviewers=()):
    blockers = []
    if pr.get("state") != "open":
        return {"status": "completed" if pr.get("merged") else "blocked", "blockers": [] if pr.get("merged") else ["PR closed without integration"], "approvals": []}
    if pr.get("draft"):
        blockers.append("Draft pull request")
    if pr.get("mergeable") is not True:
        blockers.append("Merge conflict or GitHub mergeability not yet known")
    # Latest run for each check, not an old successful run at the same revision.
    latest = {}
    for check in checks:
        if check.get("head_sha") == pr["head"]["sha"]:
            key = check["name"]
            if check.get("id", 0) > latest.get(key, {}).get("id", -1):
                latest[key] = check
    required = latest.get("verify")
    if not required or required.get("conclusion") != "success":
        blockers.append("Current-head verify check has not succeeded")
    failures = [item for item in latest.values() if item.get("conclusion") in {"failure", "timed_out", "action_required", "startup_failure"}]
    if failures:
        blockers.append("Current-head CI failures require repair")
    trusted_reviews = [item for item in reviews if item["user"]["login"] in trusted_reviewers]
    approvals = independent_approvals(trusted_reviews, pr["head"]["sha"], pr["user"]["login"])
    if not approvals:
        blockers.append("Independent current-head approval required (author cannot self-approve)")
    if not combined:
        blockers.append(f"Successful combined regression evidence required against main {base[:12]}")
    latest_reviews = {}
    for item in sorted(trusted_reviews, key=lambda item: item.get("submitted_at") or ""):
        if item.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest_reviews[item["user"]["login"]] = item
    if any(item.get("state") == "CHANGES_REQUESTED" and item.get("commit_id") == pr["head"]["sha"] for item in latest_reviews.values()):
        blockers.append("Current-head change request must be resolved")
    return {"status": "blocked" if blockers else "integration_ready", "blockers": blockers,
            "approvals": approvals, "failures": failures}


def validate_review(result, head, base, author):
    required = {"reviewer", "head", "base", "verdict", "summary", "tests", "evidence_url"}
    if not required <= result.keys() or not result["summary"].strip():
        raise ValueError("Review requires identity, revisions, verdict, summary, tests and evidence URL")
    if result["head"] != head or result["base"] != base:
        raise ValueError("Stale review evidence")
    if result["verdict"] not in {"pass", "fail"}:
        raise ValueError("Review verdict must be pass or fail")
    if result["verdict"] == "pass" and (result["reviewer"] == author or not result["tests"]):
        raise ValueError("Passing QA requires independent identity and test evidence")
    return result


def dashboard(status):
    lines = ["# Agent network status", "", f"Repository: {status['repository']}",
             f"Integration deadline: {status['deadline']} ({status['timezone']})", "",
             "No automatic merge, deployment, paid provider or destructive action is enabled.", "",
             "| Task | Owner | Priority | Status |", "| --- | --- | --- | --- |"]
    for task in status["tasks"]:
        lines.append(f"| {task['id']} | {task['owner']} | {task['priority']} | {task['status']} |")
        lines.extend(f"\n- {task['id']}: {reason}" for reason in task.get("blockers", []))
    lines.extend(["", "## Decisions", "- GitHub issues and reviews carry shared state; chat history is not a dependency.",
                  "- Integration readiness is advisory; a human must separately authorize merging.",
                  "- Coding requires a revision-bound maintainer approval and explicit local execution.",
                  "", "```json", json.dumps(status, indent=2, sort_keys=True), "```"])
    return "\n".join(lines) + "\n"
