"""Offline independent review of coordination decisions and GitHub write bounds."""
import base64
import copy
import json
from types import SimpleNamespace

import pytest

from agent_network.core import (
    approval_digest, evaluate_pr as evaluate_pr_raw, independent_approvals, parse_task, task_body,
    validate_review, validate_task,
)
from agent_network.github import GitHub
from agent_network.runtime import approved_task, combined_verified, reconcile, record_review


HEAD = "a" * 40
BASE = "b" * 40
MERGE = "c" * 40


def evaluate_pr(pr, checks, reviews, base, combined=False, trusted_reviewers=("independent",)):
    return evaluate_pr_raw(pr, checks, reviews, base, combined, trusted_reviewers)


def integration_task(result):
    return next(item for item in result["tasks"] if item["id"] == "pr:2")


def pull(**updates):
    result = {"number": 2, "title": "Listener", "state": "open", "draft": False,
              "merged": False, "mergeable": True, "head": {"sha": HEAD},
              "base": {"sha": BASE}, "user": {"login": "author"},
              "html_url": "https://github.com/example/game/pull/2", "requested_reviewers": []}
    result.update(updates)
    return result


def check(identifier=1, name="verify", conclusion="success", head=HEAD):
    return {"id": identifier, "name": name, "head_sha": head,
            "conclusion": conclusion, "html_url": f"https://github.com/example/game/runs/{identifier}"}


def review(login="independent", state="APPROVED", head=HEAD, date="2026-10-30T10:00:00Z"):
    return {"user": {"login": login}, "state": state, "commit_id": head, "submitted_at": date}


def task(**updates):
    result = {"id": "repair-test", "title": "Repair a verified defect", "owner": "development",
              "priority": "P0", "status": "queued", "acceptance": ["Regression passes"],
              "allowed_paths": ["backend/tests"], "approved_head": BASE,
              "dependencies": [], "blockers": []}
    result.update(updates)
    return result


def config():
    return {"tracked_pull_requests": [2], "deadline": "2026-11-10", "timezone": "America/Denver",
            "independent_reviewers": ["independent"], "development_approvers": ["maintainer"],
            "policy": {"automatic_merge": False, "automatic_deployment": False,
                       "paid_providers": False, "destructive_actions": False},
            "combined_evidence": {"2": {"head": HEAD, "base": BASE, "commit": MERGE, "run_id": 99}}}


class MemoryGitHub(GitHub):
    """Stateful fake keeps real idempotent issue adapter logic; never calls network."""
    def __init__(self):
        super().__init__("example/game")
        self.pr = pull()
        self.checks = [check()]
        self.reviews = [review()]
        self.issues = []
        self.comments = []
        self.labels = []
        self.mutations = []
        self.run = {"head_sha": MERGE, "conclusion": "success", "path": ".github/workflows/ci.yml",
                    "head_repository": {"full_name": self.repository}}
        self.parents = [{"sha": HEAD}, {"sha": BASE}]
        self.defaults = "MYSTERY_TRANSCRIPTION_ENABLED=false\nMYSTERY_ALLOW_PAID_TRANSCRIPTION=false\n"

    def request(self, path, method="GET", data=None):
        if method != "GET":
            self.mutations.append((method, path, copy.deepcopy(data)))
            if path == "labels":
                self.labels.append(copy.deepcopy(data))
                return copy.deepcopy(data)
            if path == "issues":
                issue = {**copy.deepcopy(data), "number": len(self.issues) + 10, "state": "open"}
                issue["html_url"] = f"https://github.com/example/game/issues/{issue['number']}"
                self.issues.append(issue)
                return copy.deepcopy(issue)
            if path.endswith("/comments"):
                return {"id": 100}
            if path.endswith("requested_reviewers"):
                self.pr["requested_reviewers"] = [{"login": login} for login in data["reviewers"]]
                return {}
            if path.startswith("issues/"):
                number = int(path.split("/")[1])
                issue = next(issue for issue in self.issues if issue["number"] == number)
                issue.update(copy.deepcopy(data))
                return copy.deepcopy(issue)
            raise AssertionError(f"Unexpected mutation: {method} {path}")
        if path.startswith("collaborators/") and path.endswith("/permission"):
            return {"permission": "write"}
        if path == "branches/main":
            return {"commit": {"sha": BASE}}
        if path == "pulls/2":
            return copy.deepcopy(self.pr)
        if path == "actions/runs/99":
            return copy.deepcopy(self.run)
        if path == f"commits/{MERGE}":
            return {"parents": copy.deepcopy(self.parents)}
        if path == f"contents/.env.example?ref={HEAD}":
            return {"content": base64.b64encode(self.defaults.encode()).decode()}
        if path.startswith("issues/"):
            number = int(path.split("/")[1])
            return copy.deepcopy(next(issue for issue in self.issues if issue["number"] == number))
        raise AssertionError(f"Unexpected read: {path}")

    def pages(self, path):
        if path == "pulls?state=open": return [copy.deepcopy(self.pr)]
        if path.startswith("issues?state=all&labels=agent-network"): return copy.deepcopy(self.issues)
        if path == f"commits/{HEAD}/check-runs": return copy.deepcopy(self.checks)
        if path == "pulls/2/reviews": return copy.deepcopy(self.reviews)
        if path.endswith("/comments"): return copy.deepcopy(self.comments)
        if path == "labels": return copy.deepcopy(self.labels)
        raise AssertionError(f"Unexpected pagination: {path}")


def test_listener_is_discovered_with_paid_defaults_and_persistent_dashboard():
    api = MemoryGitHub()
    result = reconcile(api, config(), write=True)
    integration = next(item for item in result["tasks"] if item["id"] == "pr:2")
    assert integration["owner"] == "integration" and integration["priority"] == "P0"
    assert integration["acceptance"] and integration["paid_transcription_default_disabled"]
    assert integration["status"] == "integration_ready"
    assert result["pull_requests"][0]["combined_verified"]
    assert len(api.issues) == 3
    assert any("agent-network-key:dashboard" in issue["body"] for issue in api.issues)


def test_repeated_sync_is_idempotent_and_creates_no_duplicate_issues():
    api = MemoryGitHub()
    first = reconcile(api, config(), write=True)
    api.mutations.clear()
    second = reconcile(api, config(), write=True)
    assert first == second
    assert api.mutations == []
    assert len(api.issues) == 3


def test_failed_current_head_check_becomes_actionable_development_task():
    api = MemoryGitHub()
    api.checks = [check(conclusion="failure")]
    result = reconcile(api, config(), write=True)
    repair = next(item for item in result["tasks"] if item["id"].startswith("repair:"))
    assert repair["owner"] == "development" and repair["status"] == "queued"
    assert repair["head"] == HEAD and repair["evidence_url"].endswith("/1")
    assert "without weakening" in " ".join(repair["acceptance"])
    assert integration_task(result)["status"] == "blocked"


def test_successful_independent_review_releases_advisory_readiness():
    api = MemoryGitHub()
    api.reviews = []
    assert integration_task(reconcile(api, config()))["status"] == "blocked"
    api.reviews = [review()]
    assert integration_task(reconcile(api, config()))["status"] == "integration_ready"
    assert api.mutations == []


@pytest.mark.parametrize("reviews,checks,combined", [
    ([review(login="author")], [check()], True),
    ([review(head="old")], [check()], True),
    ([review()], [], True),
    ([review()], [check(head="old")], True),
    ([review()], [check()], False),
    ([review()], [check(), check(identifier=2, conclusion=None)], True),
])
def test_missing_or_stale_evidence_fails_closed(reviews, checks, combined):
    assert evaluate_pr(pull(), checks, reviews, BASE, combined)["status"] == "blocked"


def test_failing_additional_check_blocks_even_if_verify_succeeds():
    result = evaluate_pr(pull(), [check(), check(2, "security", "failure")], [review()], BASE, True)
    assert result["status"] == "blocked"


def test_latest_approval_supersedes_same_reviewer_old_change_request():
    reviews = [review(state="CHANGES_REQUESTED"), review(date="2026-10-30T11:00:00Z")]
    assert independent_approvals(reviews, HEAD, "author") == ["independent"]
    assert evaluate_pr(pull(), [check()], reviews, BASE, True)["status"] == "integration_ready"


@pytest.mark.parametrize("mutation", [
    lambda api: api.run.update(conclusion="failure"),
    lambda api: api.run.update(head_sha="wrong"),
    lambda api: api.run.update(path=".github/workflows/unrelated.yml"),
    lambda api: api.run.update(head_repository={"full_name": "attacker/fork"}),
    lambda api: api.parents.pop(),
])
def test_combined_evidence_cannot_reuse_unrelated_or_failed_run(mutation):
    api = MemoryGitHub(); mutation(api)
    assert not combined_verified(api, config()["combined_evidence"]["2"], HEAD, BASE)


def test_reviewer_requests_exclude_author_and_do_not_duplicate():
    api = MemoryGitHub(); cfg = config(); cfg["independent_reviewers"] = ["author", "new-reviewer"]
    reconcile(api, cfg, write=True)
    requested = [item for item in api.mutations if item[1].endswith("requested_reviewers")]
    assert requested == [("POST", "pulls/2/requested_reviewers", {"reviewers": ["new-reviewer"]})]
    api.mutations.clear(); reconcile(api, cfg, write=True)
    assert not any(item[1].endswith("requested_reviewers") for item in api.mutations)


def test_declared_unfinished_dependency_blocks_task():
    api = MemoryGitHub()
    pending = task(id="dependent", dependencies=["not-yet-completed"])
    api.issues.append({"number": 8, "body": task_body(pending), "state": "open", "html_url": "https://example/8"})
    result = reconcile(api, config())
    dependent = next(item for item in result["tasks"] if item["id"] == "dependent")
    assert dependent["status"] == "blocked"
    assert dependent["blockers"] == ["Unresolved dependency: not-yet-completed"]


def test_approval_binds_scope_revision_and_actual_comment_author():
    api = MemoryGitHub(); issue_task = task()
    api.issues.append({"number": 8, "body": task_body(issue_task), "state": "open", "html_url": "https://example/8"})
    body = "<!-- agent-network-approval:v1 -->\n" + json.dumps({"task_digest": approval_digest(issue_task), "head": BASE})
    api.comments = [{"user": {"login": "attacker"}, "body": body}]
    with pytest.raises(ValueError): approved_task(api, 8, config())
    api.comments[0]["user"]["login"] = "maintainer"
    assert approved_task(api, 8, config())["approval_verified"] is True
    changed = {**issue_task, "allowed_paths": ["backend"]}
    api.issues[0]["body"] = task_body(changed)
    with pytest.raises(ValueError): approved_task(api, 8, config())


@pytest.mark.parametrize("state,status", [("closed", "queued"), ("open", "blocked"), ("open", "completed")])
def test_old_approval_does_not_revive_closed_or_blocked_tasks(state, status):
    api = MemoryGitHub(); issue_task = task(status=status)
    api.issues.append({"number": 8, "body": task_body(issue_task), "state": state, "html_url": "https://example/8"})
    api.comments = [{"user": {"login": "maintainer"}, "body": "<!-- agent-network-approval:v1 -->\n" + json.dumps(
        {"task_digest": approval_digest(issue_task), "head": BASE})}]
    with pytest.raises(ValueError): approved_task(api, 8, config())


def test_qa_record_checks_identity_and_failed_review_creates_repair(monkeypatch):
    api = MemoryGitHub()
    result = {"reviewer": "independent", "head": HEAD, "base": BASE, "verdict": "fail",
              "summary": "Disconnect loses recovery notification", "tests": ["regression fails"],
              "evidence_url": "https://github.com/example/game/actions/runs/1"}
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: SimpleNamespace(stdout="independent\n"))
    record_review(api, 2, result, write=True)
    assert any(item[1] == "issues/2/comments" for item in api.mutations)
    repair = next(item for item in api.issues if item["title"].startswith("Repair QA"))
    assert parse_task(repair["body"])["owner"] == "development"
    result["reviewer"] = "other-user"
    with pytest.raises(ValueError): record_review(api, 2, result, write=True)


def test_passing_qa_cannot_self_approve_or_use_stale_revisions():
    result = {"reviewer": "author", "head": HEAD, "base": BASE, "verdict": "pass", "summary": "Green",
              "tests": ["regression passes"], "evidence_url": "https://example/evidence"}
    with pytest.raises(ValueError): validate_review(result, HEAD, BASE, "author")
    result["reviewer"] = "independent"
    with pytest.raises(ValueError): validate_review(result, "new-head", BASE, "author")
    assert validate_review(result, HEAD, BASE, "author") == result


@pytest.mark.parametrize("path,method", [
    ("pulls/2/merge", "PUT"), ("pulls/2/merge", "POST"), ("deployments", "POST"),
    ("git/refs/heads/main", "DELETE"), ("contents/backend/main.py", "PUT"),
    ("pulls/2/reviews", "POST"),
])
def test_adapter_has_no_merge_deploy_delete_or_approval_mutation(path, method, monkeypatch):
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: pytest.fail("Forbidden action reached subprocess"))
    with pytest.raises(ValueError): GitHub("example/game").request(path, method, {})


@pytest.mark.parametrize("updates", [{"owner": "nobody"}, {"priority": "urgent"}, {"status": "ready"}, {"acceptance": []}])
def test_machine_records_require_owner_priority_status_acceptance(updates):
    with pytest.raises(ValueError): validate_task(task(**updates))


def test_task_record_round_trip_and_approval_scope_digest():
    original = task()
    assert parse_task(task_body(original)) == original
    assert approval_digest(original) != approval_digest({**original, "allowed_paths": ["frontend/src"]})


@pytest.mark.parametrize("login", ["unaffiliated-outsider", "unconfigured-bot"])
def test_untrusted_reviewer_cannot_release_integration(login):
    result = evaluate_pr(pull(), [check()], [review(login=login)], BASE, True)
    assert result["status"] == "blocked" and result["approvals"] == []


def test_no_configured_trusted_reviewer_leaves_review_gate_blocked():
    api = MemoryGitHub(); cfg = config(); cfg["independent_reviewers"] = []
    result = reconcile(api, cfg)
    assert integration_task(result)["status"] == "blocked"
    qa = next(item for item in result["tasks"] if item["owner"] == "qa")
    assert qa["status"] == "review"
