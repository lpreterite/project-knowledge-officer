# Goal

## Objective
Add a project knowledge health lint layer that reports higher-level consistency risks such as stale current facts, missing cross-links, unresolved contradictions, duplicate todos, orphan knowledge pages, and long-running open questions.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/versioning.md`
- `checklists/meeting-ingest-checklist.md`
- `prompts/analyze-meeting.md`
- `prompts/update-rollups.md`
- `scripts/meeting_helpers.py`
- Existing `validate-project` behavior and status/domain/source rules.
- Astro-Han's deterministic-versus-heuristic lint split only as inspiration; this repo's governance model remains authoritative.

## Scope
- Add a separate health lint command or mode without weakening strict structural validation.
- Report heuristic issues without auto-rewriting project facts.
- Cover at least these checks: missing expected links, duplicate open todos by title/source, open questions with no recent timeline reference, superseded decisions still appearing as active, and repeated terminology not reflected in domain/context files when DIY structure exists.
- Document which findings are warnings versus errors.

## Out Of Scope
- Replacing `validate-project`.
- Auto-resolving conflicting project facts.
- Introducing embeddings or a semantic search dependency.
- Enforcing one global taxonomy across projects.

## Deliverables
- Script command or option for knowledge health lint.
- Tests for deterministic warning detection.
- Documentation describing health lint output and expected user workflow.
- One git commit for this task only.

## Acceptance Criteria
- Existing `validate-project` remains strict for structural correctness.
- Health lint can run independently and returns clear warnings with file paths.
- The command does not rewrite decisions, todos, open questions, or rollups automatically.
- Tests cover at least two high-value lint findings and one clean project case.

## Verification Evidence
- Follow TDD:
  1. Write a failing test for one health warning using a minimal fixture.
  2. Verify red for the expected missing lint behavior.
  3. Implement the minimal command/check.
  4. Add a second failing warning test and a clean-case test.
  5. Verify red, implement green, refactor with the suite passing.
- Run relevant tests.
- Run the new lint command against a generated sample project.
- Run existing validation tests to prove no regression.
- Show `git diff --stat` before committing.

## Operating Rules
- Separate facts from suspicions: health lint findings are review prompts, not automatic truth changes.
- Preserve uncertainty explicitly; unclear conflict resolution must become an open question only when a human or separate ingest workflow confirms it.
- Keep output useful for ordinary-mode users while allowing DIY users to inspect details.

## Prohibited Exit
- Do not claim done if health lint mutates project facts without explicit user confirmation.
- Do not mark heuristic warnings as hard errors unless existing governance requires it.
- Do not commit without tests demonstrating the new command.

## Exit Conditions
The task is complete only after the health lint behavior is tested, documented, verified on a sample project, and committed as a single focused change.
