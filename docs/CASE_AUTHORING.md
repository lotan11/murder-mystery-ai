# Editing a mystery

The authoritative story is `backend/cases/blackthorn.json`. It is a **server-only authoring file containing the solution and private cards**. Do not copy it to the frontend public directory or share it with players.

## What can be edited together

- `title`, `suspects`: title, names, public descriptions and search topics.
- `evidence`: release act, title, factual description, concise summary, search topics and a spoiler-safe hint.
- `characters`: public introduction, private brief, objectives and performance notes for each role.
- `narration`: welcome, case opening, act transition and reset lines.
- `solution`: the final evidence-based reconstruction.

Detective manner stays separate: `backend/dialogue.py` provides serious, neutral response framing; `backend/ai_dialogue.py` supplies approved neutral remarks. The avatar, local speech and WebSocket interfaces consume the same public dialogue, so they do not need rebuilding for ordinary story text edits. Frontend production rebuilding is unnecessary for JSON-only edits; restart the backend to load the edited package.

## Safe editing workflow

1. Work on a branch or keep a copy of the original package. Keep IDs stable while revising text.
2. Change every affected clue, hint, suspect description, private card and solution together. Ensure a hint never refers to an unreleased clue.
3. Validate the package from the repository folder:

   ```powershell
   .\.venv\Scripts\python.exe -c "from backend.case_package import load_case; print(load_case()['title'])"
   .\.venv\Scripts\python.exe -m pytest -q
   ```

4. Restart the app, create a fresh evening, and rehearse every act. Review and update case-specific timeline expectations together with deliberate story changes, preserving spoiler/privacy checks. Check evidence, private views and finale; an automated structural validator cannot prove narrative consistency.

## Current limits

This increment centralizes the existing case; it is not yet a multi-case editor or selector. The client/assignment flow still requires stable role IDs `ada`, `felix`, `margot`, plus `investigator`, and three investigation acts. Names, descriptions and narrative content can change; entirely different roster IDs or pacing need another implementation step. Some frontend location labels, fallback text and the stage artwork still use the Blackthorn theme.

Keep case `id`/`version` unchanged for this extraction and minor compatible wording revisions. Changing clue meaning, release order, roster or solution can invalidate active saved rooms: use fresh evenings and design an explicit case-version migration before deploying such a change to existing saves. The storage compatibility checks currently target one selected case and deliberately reject mismatched IDs/versions.

The loader rejects duplicate JSON keys, duplicate clue/suspect IDs, missing act coverage, incomplete cards, missing topics/hints and unsupported format/roster. It does not automatically detect contradictions, unfair deductions or early spoiler wording. Those require story review and a full rehearsal.
