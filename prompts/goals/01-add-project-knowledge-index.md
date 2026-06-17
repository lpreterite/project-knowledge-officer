# Goal

## Objective
Add a project-level `knowledge/index.md` capability so each project knowledge repo has a compact navigation surface for meetings, current decisions, todos, open questions, important artifacts, and last knowledge update dates.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/ordinary-and-diy-modes.md`
- `docs/versioning.md`
- `templates/`
- `scripts/meeting_helpers.py`
- Existing project knowledge repository rules for source links, Domain, status, artifact policy, and validated commits.
- Karpathy LLM Wiki pattern only as inspiration for `index.md`; do not replace this repo's meeting/project governance model.

## Scope
- Define and generate a `knowledge/index.md` template for new project knowledge repos.
- Update initialization behavior so new project repos include the index.
- Update validation so missing or malformed project indexes are reported.
- Update docs and prompts so agents read the index as a navigation aid, not as an authoritative replacement for `current-*` files.

## Out Of Scope
- Replacing `current-summary.md`, `current-decisions.md`, `current-todos.md`, `current-open-questions.md`, or `timeline.md`.
- Adding search infrastructure, embeddings, or Obsidian-specific dependencies.
- Migrating existing project knowledge repos unless tests define a narrow compatibility path.

## Deliverables
- Updated template(s) for `knowledge/index.md`.
- Script support in `scripts/meeting_helpers.py`.
- Focused tests covering project initialization and validation behavior.
- Documentation updates explaining the role of `knowledge/index.md`.
- One git commit for this task only.

## Acceptance Criteria
- New ordinary-mode and DIY-mode project repos include `knowledge/index.md`.
- The index lists stable sections for current status, meetings, decisions, todos, open questions, artifacts, and last update metadata.
- Validation detects a missing index and does not treat the index as the source of truth for project facts.
- Existing validation semantics for decisions, todos, open questions, Domain, source links, and artifacts remain intact.

## Verification Evidence
- Follow TDD:
  1. Write a failing test for index creation during project initialization.
  2. Verify the test fails for the expected reason.
  3. Implement the minimal change.
  4. Verify the test passes.
  5. Add failing validation tests for missing or malformed index behavior.
  6. Verify red, implement green, then refactor only while tests stay green.
- Run the relevant test suite.
- Run `python3 scripts/meeting_helpers.py --project-root <temp-project> validate-project` against a generated sample project.
- Show `git diff --stat` before committing.

## Operating Rules
- Prefer repo-local patterns over new abstractions.
- Keep ordinary-mode language simple; users should only understand that the index helps Agent find current project knowledge.
- Do not overwrite or reinterpret existing project facts.
- Preserve Chinese as the default documentation language.

## Prohibited Exit
- Do not exit after writing only documentation.
- Do not claim TDD if tests were written after implementation.
- Do not mark complete if index validation is untested.
- Do not include unrelated files in the commit.

## Exit Conditions
The task is complete only after tests pass, validation evidence is recorded, docs are updated, and a single focused commit exists for this capability.
