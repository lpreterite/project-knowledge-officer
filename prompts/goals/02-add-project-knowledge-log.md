# Goal

## Objective
Add an append-only project knowledge operation log so each project knowledge repo can record ingest, rollup, query-archive, lint, and validation-relevant maintenance events in `knowledge/log.md`.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/versioning.md`
- `checklists/meeting-ingest-checklist.md`
- `scripts/meeting_helpers.py`
- Existing commit, validation, artifact, and source-tracking rules.
- Karpathy LLM Wiki `log.md` pattern only as inspiration for a chronological operation log.

## Scope
- Define a `knowledge/log.md` template and event format.
- Update project initialization to create the log.
- Update meeting ingest or helper commands where appropriate to append log entries.
- Update validation to verify the log exists and remains append-oriented.
- Document how the log differs from `timeline.md` and Git history.

## Out Of Scope
- Replacing `timeline.md`.
- Recording every filesystem change.
- Building a full audit database or external logging system.
- Auto-logging sensitive artifact contents.

## Deliverables
- `knowledge/log.md` template.
- Helper script behavior for initialization and narrowly scoped append operations.
- Tests for log creation and append format.
- Docs explaining `log.md` versus `timeline.md`.
- One git commit for this task only.

## Acceptance Criteria
- New project knowledge repos include `knowledge/log.md`.
- Log entries use a consistent parseable heading format such as `## [YYYY-MM-DD] <operation> | <summary>`.
- `timeline.md` remains the semantic project-fact timeline; `log.md` records Agent/project-maintenance operations.
- Validation catches a missing log without requiring old projects to fabricate historical entries.

## Verification Evidence
- Follow TDD:
  1. Write a failing test for log creation during initialization.
  2. Verify red for the expected missing-file reason.
  3. Implement the minimal green path.
  4. Add a failing test for append format or validation behavior.
  5. Verify red, implement green, then refactor with tests passing.
- Run relevant tests.
- Generate a temp project and run `validate-project`.
- Inspect resulting `knowledge/log.md` content.
- Show `git diff --stat` before committing.

## Operating Rules
- Keep log entries metadata-oriented; do not copy raw transcript or sensitive artifact content into the log.
- Use Chinese for user-facing docs and headings unless existing templates require field names.
- Preserve local-first and per-project sharing boundaries.

## Prohibited Exit
- Do not merge log semantics into `timeline.md`.
- Do not skip tests because the change looks like a template-only update.
- Do not commit unrelated files.

## Exit Conditions
The task is complete only after red-green-refactor evidence exists, initialization and validation are covered, docs are updated, and the focused commit is created.
