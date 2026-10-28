# Project operating agreement

The user has authorized development, routine technical decisions, integration, testing, and commits for this platform. Keep one authoritative repository and deliver playable milestones; do not require the user to relay information between chats.

## Read before changing the project

- `docs/SPECIFICATION.md`: product requirements and milestone acceptance.
- `docs/TASK_BOARD.md`: current backlog, ownership, dependencies, and status.
- `docs/DECISIONS.md`: accepted architectural decisions.
- `docs/GAME_DESIGN.md`: canonical case design; contains spoilers.
- `docs/PROGRESS.md`: latest handoff, verification results, and next task.
- `docs/AI_INTEGRATION.md`: optional provider configuration, bounded planning and live-test limitations.

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
