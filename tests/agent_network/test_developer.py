"""Offline command-transport tests; these never invoke Codex or GitHub."""
from pathlib import Path

import pytest

from agent_network import developer


def approved():
    return {
        "id": 17, "owner": "development", "status": "approved", "priority": "P1",
        "acceptance": ["Add the bounded, offline fixture"],
        "issue_url": "https://github.com/lotan11/murder-mystery-ai/issues/17",
        "approved_by": "maintainer", "approved_head": "a" * 40,
        "approval_verified": True, "allowed_paths": ["backend/example.py"],
    }


def test_plan_never_executes_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(developer, "_run", lambda *_a, **_kw: pytest.fail("Executed a command in plan mode"))
    result = developer.develop(tmp_path, approved())
    assert result["status"] == "planned" and not result["executed"]
    assert result["automatic_merge"] is False
    assert result["requires_independent_review"] is True


@pytest.mark.parametrize("change", [
    {"id": "17;git reset --hard"}, {"owner": "qa"}, {"status": "open"},
    {"approval_verified": False}, {"approved_by": ""}, {"approved_head": "main"},
    {"allowed_paths": ["../main"]}, {"allowed_paths": ["."]},
    {"allowed_paths": [".github/workflows"]}, {"allowed_paths": ["agent_network"]},
    {"allowed_paths": ["frontend/.env"]}, {"allowed_paths": ["frontend/AGENTS.md"]},
    {"allowed_paths": ["frontend/package.json"]}, {"acceptance": []},
    {"issue_url": "https://github.com/untrusted/project/issues/17"},
])
def test_execution_rejects_unverified_or_unsafe_tasks_before_commands(tmp_path, monkeypatch, change):
    monkeypatch.setattr(developer, "_run", lambda *_a, **_kw: pytest.fail("Reached command execution"))
    task = approved() | change
    result = developer.develop(tmp_path, task, execute=True)
    assert result["status"] == "blocked" and not result["executed"]


def command_fixture(monkeypatch, *, changed=" M backend/example.py", failure=None,
                    stale=False, dirty=False):
    calls = []
    committed = False

    def run(args, cwd, **kwargs):
        nonlocal committed
        args = list(map(str, args))
        calls.append((args, Path(cwd), kwargs))
        if failure and args[:len(failure)] == failure:
            raise developer.DevelopmentBlocked("Injected fixed-check failure")
        if args[:3] == ["git", "status", "--porcelain"]:
            return changed if "agent-worktrees" in str(cwd) else (" M existing.py" if dirty else "")
        if args[:3] == ["gh", "repo", "view"]:
            return developer.REPOSITORY
        if args[:2] == ["git", "ls-remote"]:
            return ("b" if stale else "a") * 40 + "\trefs/heads/main"
        if args[:3] == ["git", "branch", "--list"]:
            return ""
        if args[:3] == ["git", "branch", "--show-current"]:
            return "agent/task-17"
        if args[:2] == ["git", "rev-parse"]:
            return ("c" if committed else "a") * 40
        if "commit" in args:
            committed = True
        if args[:3] == ["gh", "pr", "create"]:
            return "https://github.com/lotan11/murder-mystery-ai/pull/99"
        return ""

    monkeypatch.setattr(developer, "_run", run)
    monkeypatch.setattr(developer.shutil, "which", lambda name: "/tools/" + name)
    monkeypatch.setattr(developer, "_prepare_validation", lambda _path: None)
    monkeypatch.setattr(developer, "_validation_commands", lambda path: [
        (["python", "-m", "pytest", "backend/tests", "-q"], path),
        (["npm", "test"], path / "frontend"),
        (["npm", "run", "build"], path / "frontend"),
        (["npm", "run", "test:e2e"], path / "frontend"),
    ])
    return calls


def test_successful_transport_runs_fixed_checks_then_opens_draft_pr(tmp_path, monkeypatch):
    calls = command_fixture(monkeypatch)
    monkeypatch.setenv("GH_TOKEN", "must-not-reach-model-or-tests")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-reach-model-or-tests")
    result = developer.develop(tmp_path, approved(), execute=True)
    assert result["status"] == "in_review" and result["executed"]
    assert result["commit"] == "c" * 40
    assert len(result["validation"]) == 4
    codex = next(call for call in calls if call[0][0].endswith("codex"))
    assert "workspace-write" in codex[0] and "sandbox_workspace_write.network_access=false" in codex[0]
    assert "GH_TOKEN" not in codex[2]["env"] and "OPENAI_API_KEY" not in codex[2]["env"]
    pytest_call = next(call for call in calls if "pytest" in call[0])
    assert "GH_TOKEN" not in pytest_call[2]["env"]
    assert pytest_call[2]["env"]["MYSTERY_ALLOW_PAID_AI"] == "false"
    assert pytest_call[2]["env"]["OPENAI_API_KEY"] == ""
    pr = next(call for call in calls if call[0][:3] == ["gh", "pr", "create"])
    assert "--draft" in pr[0]
    assert not any("merge" in call[0] or "reset" in call[0] or "--delete" in call[0] for call in calls)


def test_failed_check_preserves_worktree_and_never_pushes(tmp_path, monkeypatch):
    calls = command_fixture(monkeypatch, failure=["npm", "test"])
    result = developer.develop(tmp_path, approved(), execute=True)
    assert result["status"] == "blocked" and result["executed"]
    assert result["worktree"].endswith("task-17")
    assert not any("push" in call[0] or call[0][:3] == ["gh", "pr", "create"] for call in calls)


@pytest.mark.parametrize("changed", [" D backend/example.py", " M frontend/other.py",
                                      " M frontend/package.json", "R  backend/old.py -> backend/example.py"])
def test_worker_cannot_delete_or_widen_scope(tmp_path, monkeypatch, changed):
    calls = command_fixture(monkeypatch, changed=changed)
    task = approved()
    if "package.json" in changed:
        task["allowed_paths"] = ["frontend"]
    result = developer.develop(tmp_path, task, execute=True)
    assert result["status"] == "blocked"
    assert not any("pytest" in call[0] or "push" in call[0] for call in calls)


@pytest.mark.parametrize("kwargs", [{"stale": True}, {"dirty": True}])
def test_changed_main_or_existing_edits_block_before_worktree(tmp_path, monkeypatch, kwargs):
    calls = command_fixture(monkeypatch, **kwargs)
    result = developer.develop(tmp_path, approved(), execute=True)
    assert result["status"] == "blocked" and not result["executed"]
    assert not any(call[0][:3] == ["git", "worktree", "add"] for call in calls)


def test_process_transport_preserves_git_status_leading_space(tmp_path, monkeypatch):
    class Result:
        returncode = 0
        stdout = " M backend/example.py\n"
    monkeypatch.setattr(developer.subprocess, "run", lambda *_args, **_kwargs: Result())
    assert developer._run(["git", "status", "--porcelain"], tmp_path).startswith(" M ")
