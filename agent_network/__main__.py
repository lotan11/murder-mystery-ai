import argparse
import json
import os
import subprocess
from pathlib import Path

from .core import approval_digest, dashboard, parse_task
from .github import GitHub
from .runtime import approved_task, reconcile, record_review, record_task


def main():
    parser = argparse.ArgumentParser(description="GitHub-backed agent coordination; dry-run unless --write/--execute")
    parser.add_argument("command", choices=["sync", "record-task", "record-review", "approve-task", "develop"])
    parser.add_argument("--config", type=Path, default=Path("agent-network/config.json"))
    parser.add_argument("--output", type=Path, default=Path(".agent-network/status.json"))
    parser.add_argument("--file", type=Path)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int, default=2)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if any(config["policy"].get(key) is not False for key in ("automatic_merge", "automatic_deployment", "paid_providers", "destructive_actions")):
        raise ValueError("Unsupported unsafe policy")
    api = GitHub(config["repository"])
    if args.command == "sync":
        result = reconcile(api, config, args.write)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            Path(summary).write_text(dashboard(result), encoding="utf-8")
    elif args.command in {"record-task", "record-review"}:
        if not args.file:
            parser.error("--file is required")
        data = json.loads(args.file.read_text(encoding="utf-8"))
        result = record_task(api, data, args.write) if args.command == "record-task" else record_review(api, args.pr, data, args.write)
    elif args.command == "approve-task":
        if not args.issue:
            parser.error("--issue required")
        task = parse_task(api.request(f"issues/{args.issue}")["body"])
        identity = subprocess.run(["gh", "api", "user", "--jq", ".login"], text=True,
                                  capture_output=True, check=True, timeout=30).stdout.strip()
        if identity not in config["development_approvers"]:
            raise ValueError("Only a configured maintainer can approve development")
        if task.get("approved_head") != api.request("branches/main")["commit"]["sha"]:
            raise ValueError("Task must pin current main in approved_head")
        result = {"task_digest": approval_digest(task), "head": task["approved_head"]}
        if args.write:
            api.request(f"issues/{args.issue}/comments", "POST", {
                "body": "<!-- agent-network-approval:v1 -->\n" + json.dumps(result)})
    else:
        if not args.issue:
            parser.error("--issue required")
        from .developer import develop
        task = approved_task(api, args.issue, config)
        result = develop(Path.cwd(), task, execute=args.execute)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if args.command == "develop" and args.execute and result.get("status") == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
