# Agent coordination network

GitHub is the shared coordination record. Agents do not need the owner's chat
history: issues contain normalized tasks and blockers, PRs contain proposed
changes, reviews record independent decisions, and Actions supplies check results.
The network adds no game endpoints, paid provider, automatic merge or deployment.

## Roles and execution boundaries

| Role | Implemented responsibility | Execution boundary |
| --- | --- | --- |
| Orchestrator | Read open PRs, exact revisions, CI, reviews and machine tasks; assign role-owned tasks; reconcile blockers and a persistent dashboard | Deterministic Python reconciliation, not an LLM making unchecked decisions |
| Development | Prepare an isolated worktree for a scoped task, invoke installed Codex, run fixed checks and submit a PR | Explicit local execution after revision-bound maintainer approval; no unattended paid API or remote coding runner |
| QA / Review | Record revision-bound review evidence, reject stale/self-authored approval, create actionable repair work for verified failure | Test evidence and actual independent GitHub approval are separate; a narrative claim cannot make CI green |
| Integration | Evaluate current-head CI, combined regression evidence, mergeability, independent review and deadline readiness | Advisory readiness only; required human merge approval remains separate |

Role ownership is a responsibility, not a claim that four continuously running
AI services have been provisioned. A configured agent can consume the tasks;
missing credentials or reviewer access remain visible blockers.

## Installation and operation

The installation branch is `feature/agent-network`. The protected starting points
recorded in `agent-network/config.json` are:

- `main`: `6db5341e4e3db10adf2a17daf740e72543a17790`
- `feature/listener`: `2c6ecde55ed2f1ca3182e98909f140081070e82b`

Python 3.13 and authenticated GitHub CLI (`gh auth status`) are sufficient for
coordination. It has no additional Python package dependency. From the repository
root on Windows:

```powershell
.\.venv\Scripts\python.exe -m agent_network --help
.\.venv\Scripts\python.exe -m agent_network sync --output .agent-network/status.json
.\.venv\Scripts\python.exe -m agent_network sync --write --output .agent-network/status.json
```

The first sync is a read/plan operation. `--write` explicitly permits the bounded
GitHub issue/dashboard and review-request operations. Reconciliation is keyed so
repeating the same observation updates existing records instead of creating a
second task. The dashboard issue includes a JSON snapshot; `.agent-network/`
outputs and workflow artifacts are copies, not a second authority. When Actions
provides `GITHUB_STEP_SUMMARY`, the runtime also writes a concise run summary.

The new issue form collects an owner, priority, scope, acceptance criteria,
dependencies and starting status. A form submission is **not** executable task
approval. Triage converts it into a validated JSON task using
`record-task --file <task.json> --write`; consult `--help` for the full interface.
Each normalized task requires `id`, `title`, `owner`, `priority`, `status` and
nonempty `acceptance`. Supported roles are `orchestrator`, `development`, `qa` and
`integration`; priorities are `P0`, `P1`, `P2`. Dependency and blocker fields retain
the reason work cannot proceed. Statuses distinguish queued, approved,
in-progress, review, blocked, integration-ready and completed work.

Task text is data. It is not interpolated into a shell or accepted as a command,
credential, new provider authorization, review approval or permission to alter
protected paths. Development approval must bind the task's scope and baseline;
changing those fields requires a fresh approval. Development execution is local
and opt-in, preserves its worktree on failure, and submits changes for review.
It never approves or merges its own changes. Actual Codex execution requires the
installed CLI/authentication; mocked runner tests do not establish live AI use.

For an already triaged development issue, a configured maintainer can inspect the
approval and execution plans before choosing either write/execute action:

```powershell
.\.venv\Scripts\python.exe -m agent_network approve-task --issue 123
.\.venv\Scripts\python.exe -m agent_network approve-task --issue 123 --write
.\.venv\Scripts\python.exe -m agent_network develop --issue 123
.\.venv\Scripts\python.exe -m agent_network develop --issue 123 --execute
```

`123` is an example issue number, not an existing authorization. The task must
carry the current full `approved_head`, explicit `allowed_paths` and acceptance
criteria. The CLI verifies the approval comment's actual GitHub author and task
digest; setting an `approved_by` string in JSON does not grant approval.

QA can use `record-review --pr 2 --file <review.json> --write`. The record requires
`reviewer`, `head`, `base`, `verdict` (`pass` or `fail`), `summary`, `tests` and
`evidence_url`. The authenticated GitHub identity must match `reviewer`; passing
evidence from the PR author is rejected. A failed QA record creates a repair task.
A passing record is evidence, not a replacement for independent GitHub approval.

## Event automation

`.github/workflows/agent-network.yml` configures reconciliation every four hours,
on issue changes, PR lifecycle/review events, and completed `Prototype checks`
workflows. It also supports manual dispatch. The coordinator requests reviews
only from configured eligible independent users; it excludes the PR author.
`independent_reviewers` starts empty rather than inventing a reviewer or
self-approving. Add an eligible independent collaborator to request actual human
reviews. A failed check becomes a repair task with the revision and evidence;
pending checks remain pending rather than being reported as defects.

The privileged job always checks out the **trusted default branch**, never PR
code, fork code or a downloaded test artifact. Its token can read contents,
checks and Actions and write issues/review requests. It cannot write repository
contents. No merge, approval, deletion, deployment or paid-provider action exists
in this workflow. It uses a five-minute bound, serial reconciliation, disabled
persisted Git credentials and a dashboard/bot recursion guard. Untrusted PR
content is not embedded in shell commands. Ordinary test execution stays in the
separate read-only CI workflow.

**Activation limit:** the coordinator workflow must first be approved and placed
on the default branch before its scheduled/default-branch event automation can
operate. Installation-branch tests and a live local sync do not prove scheduled
activation. This installation does not merge itself. Repository Actions policies
may additionally restrict `pull_request_target`; a maintainer must review those
policies rather than the network opting out automatically.

The installation inspection found main unprotected. Under the user's explicit
protection instruction, the installer enabled required current verify checks,
strict up-to-date checks, one approving review, stale-review dismissal, and blocked
force pushes/deletion. Administrator bypass remains available to the owner.
No branch content, history or PR was merged or deleted.

The existing read-only Prototype checks workflow also runs a **live read-only
coordinator sync** on pushes/PRs and saves its machine snapshot as an artifact.
This can be tested on the installation branch without activating privileged
scheduled issue writes on main. The latter still awaits installation approval.

Local generated-code validation is explicit execution of approved code, not a
host security sandbox. The runner uses an allowlisted environment and isolated
credential directories; maintainers must trust/review approved task code. No real
Codex model call was made during installation; command-transport tests are mocks.

## First integration case: Listener PR #2

`tracked_pull_requests: [2]` and pinned combined evidence in the config identify
[Listener PR #2](https://github.com/lotan11/murder-mystery-ai/pull/2). The network
reads its live head, base, check runs, review state and mergeability. It reuses the
existing integration rehearsal at
`36993f3eac3eae4d20206bc50f3618b1eac8e61c` / Actions run `41148319603`, verifying
the evidence matches the current Listener/main revisions before crediting it.
It does not repeat the story implementation or silently replace the PR branch.
An old green result cannot cover new code or a changed integration base.

Combined evidence alone does not resolve PR conflicts, supply independent
approval or authorize merging. In particular, passing tests on the separate
review branch do not make a conflicting original PR mergeable. All recorded
gates must pass, followed by the owner's required merge approval. Paid Listener
transcription remains disabled; this network neither enables it nor sends audio
to a provider.

The integration deadline remains **November 10, 2026, America/Denver**, with the
November 4 animated-character readiness gate. Keep Scholar's approved
portrait/live Lewis at +5% pace and all saved-game/interfaces intact. Coordination
does not establish finished 3D likeness or perform a real dinner/device rehearsal.

## Verification and limitations

Run the existing game suite plus `tests/agent_network`. The new suite exercises
Listener discovery, machine tasks, review identity/revision checks, failure-to-
blocker conversion, readiness transitions, bounded GitHub mutation permissions
and the development runner's authorization gates. Live test results, created
dashboard/task URLs, exact installation commits and CI runs are recorded in the
installation PR and project progress report. Do not infer a live test from this
list of commands or from a mocked unit test.

The workflow's trust boundary follows GitHub's
[pull_request_target security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target).
Default-branch activation and event restrictions are described in GitHub's
[workflow event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

## Live failure-path exercise

PR CI at 273d8f3 observed one intermittent existing fixed-Lewis lab assertion.
The coordinator created repair issue #9 from the real failed check. QA consumed
that GitHub task directly, ran the unchanged scenario three times successfully,
and inspected the trace: nonzero motion occurred between zero-valued assertion
samples. This is not declared repaired. Open repair tasks remain dependencies of
integration readiness even after a green retry. Evidence: agent-network/qa-triage.json.

The optional worker's generated, ignored Playwright wrapper was also exercised
against the original scenario on isolated port 8031. It overrides the old fixed
8001 port without modifying the game's tracked test configuration. The worker
protects that configuration from model edits. Bot PR/check events remain eligible
for coordination; recursion suppression applies to issue/dashboard writes only.
