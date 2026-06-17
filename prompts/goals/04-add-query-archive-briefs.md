# Goal

## Objective
Add a query-archive brief capability so valuable project Q&A or analysis answers can be saved as sourced `knowledge/briefs/*.md` pages without replacing formal rollups, decisions, todos, or open questions.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/versioning.md`
- `prompts/update-rollups.md`
- `templates/`
- `scripts/meeting_helpers.py`
- Existing source-link, current-state, Domain, and artifact rules.
- Karpathy LLM Wiki query archive pattern only as inspiration for preserving high-value answers.

## Scope
- Define a `knowledge/briefs/` directory and brief template.
- Add helper support for creating or validating archived briefs if consistent with existing script style.
- Require every brief to cite current project files and underlying meeting/artifact sources where relevant.
- Update docs so briefs are clearly secondary analysis artifacts, not authoritative current state.

## Out Of Scope
- Automatically archiving every chat answer.
- Treating briefs as decisions, todos, or open questions.
- Replacing `analysis.md`, `current-*`, or `timeline.md`.
- Saving confidential raw content into briefs without source and sharing checks.

## Deliverables
- Brief template and docs.
- Script and validation support if the repo pattern supports it.
- Tests covering brief validation and source requirements.
- One git commit for this task only.

## Acceptance Criteria
- Briefs can be created under `knowledge/briefs/` with title, question, answer, cited project sources, cited meeting/artifact sources, creation date, and status.
- Validation or linting flags briefs with no project/source citations.
- Docs explain when to archive an answer and when to update formal rollups instead.
- Ordinary-mode behavior remains opt-in: briefs are saved only when the user asks to preserve the answer.

## Verification Evidence
- Follow TDD:
  1. Write a failing test for validating a well-formed sourced brief.
  2. Verify red for missing implementation.
  3. Implement the minimal green path.
  4. Write a failing test for rejecting or warning on an uncited brief.
  5. Verify red, implement green, then refactor.
- Run relevant tests.
- Run project validation or health lint against a fixture containing briefs.
- Show `git diff --stat` before committing.

## Operating Rules
- Treat briefs as derived interpretation with citations.
- Do not promote a brief into current project truth unless a separate rollup update explicitly does so with sources.
- Keep filenames stable, dated or slugged, and friendly to Markdown/Obsidian workflows.

## Prohibited Exit
- Do not create a brief mechanism that bypasses source evidence.
- Do not make query archiving automatic by default.
- Do not commit without tests for cited and uncited brief behavior.

## Exit Conditions
The task is complete only after briefs are templated, tested, documented, verified, and committed as one focused change.
