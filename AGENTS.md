# Project operating agreement

The user has authorized development, routine technical decisions, integration, testing, and commits for this platform. Keep one authoritative repository and deliver playable milestones; do not require the user to relay information between chats.

## Read before changing the project

- `docs/SPECIFICATION.md`: product requirements and milestone acceptance.
- `docs/TASK_BOARD.md`: current backlog, ownership, dependencies, and status.
- `docs/DECISIONS.md`: accepted architectural decisions.
- `docs/GAME_DESIGN.md`: canonical case design; contains spoilers.
- `docs/PROGRESS.md`: latest handoff, verification results, and next task.
- `docs/AI_INTEGRATION.md`: optional provider configuration, bounded planning and live-test limitations.
- `docs/CHARACTER_AUTHORING.md` and `assets/character-production/README.md`: anatomical Scholar source, reproducible build, licenses and rig quality boundaries.

Inspect Git status, remote branches, open PRs, and the latest CI results before implementation. Preserve unrelated edits. Reuse reviewed work from other branches instead of duplicating it. Story facts, role cards, case narration, topic aliases and hints live in `backend/cases/blackthorn.json`; `backend/mystery.py` and `backend/characters.py` are compatibility exports. Read `docs/CASE_AUTHORING.md` before editing a case. Detective delivery is observant, respectful and playfully sarcastic, with restrained dry humor and no slapstick. New candidate portraits/voices stay in the separate casting sandbox until user approval. Story facts stay server-side; all clients receive server projections. Do not introduce a second engine, case package, or frontend for the same responsibility.

## Parallel development and integration

Use independent agents when useful, with explicit, non-overlapping file ownership and agreed protocol changes. The lead integrates, runs cross-component tests, updates the documents above, and commits completed increments. Agents should report contract changes before implementing dependent features. No agent should independently push competing component versions.

## Definition of done

- Application still starts with `start.ps1` and no paid credentials.
- Meaningful backend/client tests and the production build pass; run browser tests for visible flow changes.
- Hidden facts, credentials, and private player data do not enter public snapshots early.
- New integrations clearly disclose whether they are simulated, optional, or real. Automated tests must not invoke paid providers; use the offline fixtures and injected transports. Never commit actual environment files or API credentials.
- Update the backlog, decisions if changed, and progress report with actual test results and limitations.
- Inspect CI after pushing; investigate failures instead of reporting a green milestone from local tests alone.

Ask the user only for a material product preference or unavailable credential/asset that prevents the chosen milestone. Do not silently purchase services, send invitations, or deploy publicly. Do not promise continued background work unless an automation has actually been requested and configured.

## Approved character direction

The Scholar + Lewis +5% pace is selected and approved. Keep the approved portrait/live voice in the game while developing the actual likeness-matched rig. The separate character lab is for real development geometry, not activation or another casting decision. Do not fabricate bones/morphs to satisfy inventory checks or claim a static blockout is a finished speaking avatar. Keep canonical Blender source/settings/build script together and preserve model provenance.

## Integration deadline

November 10, 2026 (America/Denver) is the user-set integration deadline. Read docs/INTEGRATION_PLAN.md and protect the runnable Scholar/Lewis fallback while completing actual rig work. Flag schedule risks early; do not interpret the deadline as permission for spending or public deployment.

## Shared agent coordination

Read `docs/AGENT_NETWORK.md` and the GitHub project dashboard (issue #5) when
coordinating work. GitHub issues carry task owner, priority, acceptance criteria,
dependencies and machine status; PRs and CI carry implementation and verification.
Use those records for handoffs between Work, Listener, QA and integration instead
of asking the owner to transfer chat messages. Preserve the existing Scholar and
Listener responsibilities and reuse reviewed branches before assigning repairs.

Use `python -m agent_network sync` for a read-only plan. `sync --write` is the
bounded issue/dashboard/review-request reconciler when the user has authorized
GitHub coordination. Human issue forms need normalized `record-task` triage;
issue text alone never authorizes execution. Readiness is advisory. Do not merge
or delete any existing development without explicit owner approval, and do not
use administrator bypass autonomously. Main requires verify and one review.

The Development Agent uses an isolated retained worktree and requires a verified
maintainer approval bound to the task scope and current main revision, followed
by explicit local `develop --execute`. An agent must not approve its own change.
Report actual tests and observed blockers in GitHub; distinguish mocked worker
tests from a real Codex run. No automatic paid call, merge or deployment is
enabled. Scheduled privileged reconciliation becomes active only after approved
default-branch installation; before that, live local sync and read-only CI are
the tested execution paths. The existing four-hour reports remain factual.
