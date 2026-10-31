"""Small GitHub adapter. No merge, delete, deployment, branch or contents-write API."""
import json
import re
import subprocess


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Invalid repository")
        self.repository = repository

    def request(self, path, method="GET", data=None):
        # Mutation allowlist is deliberately narrower than the token's capabilities.
        allowed = re.fullmatch(r"issues(?:/\d+(?:/comments|/labels)?)?|pulls/\d+/requested_reviewers|labels", path)
        if method != "GET" and (method not in {"POST", "PATCH"} or not allowed):
            raise ValueError("Forbidden GitHub mutation")
        command = ["gh", "api", f"repos/{self.repository}/{path}", "--method", method,
                   "-H", "Accept: application/vnd.github+json"]
        if data is not None:
            command.extend(["--input", "-"])
        result = subprocess.run(command, input=None if data is None else json.dumps(data),
                                text=True, encoding="utf-8", capture_output=True, timeout=90, check=True)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def pages(self, path):
        rows = []
        for page in range(1, 21):
            data = self.request(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            batch = data["check_runs"] if isinstance(data, dict) else data
            rows.extend(batch)
            if len(batch) < 100:
                return rows
        raise ValueError("Pagination limit reached; refusing an incomplete coordination snapshot")

    def upsert_issue(self, key, title, body, existing):
        marker = f"<!-- agent-network-key:{key} -->"
        body = body + "\n" + marker
        matches = [item for item in existing if marker in (item.get("body") or "")]
        if len(matches) > 1:
            raise ValueError(f"Duplicate network key {key}; reconcile explicitly")
        if matches:
            issue = matches[0]
            if issue.get("body") != body:
                issue = self.request(f"issues/{issue['number']}", "PATCH", {"body": body})
            return issue
        issue = self.request("issues", "POST", {"title": title, "body": body, "labels": ["agent-network"]})
        existing.append(issue)
        return issue
