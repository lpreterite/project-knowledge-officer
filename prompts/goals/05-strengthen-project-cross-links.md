# Goal

## Objective
Strengthen cross-linking across project knowledge files so decisions, todos, open questions, timeline entries, meeting analyses, artifacts, and domain/context pages form a navigable evidence graph.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/versioning.md`
- `checklists/meeting-ingest-checklist.md`
- `templates/`
- `prompts/analyze-meeting.md`
- `prompts/update-rollups.md`
- `scripts/meeting_helpers.py`
- Existing source evidence, Domain, status, and supersedes rules.

## Scope
- Define link conventions for current rollups, meeting analysis, artifacts manifest entries, timeline events, and optional DIY domain/context files.
- Update templates and prompts so new knowledge entries include stable relative links.
- Update validation or health lint to detect important missing links.
- Preserve plain Markdown compatibility.

## Out Of Scope
- Rewriting all legacy project repositories.
- Requiring Obsidian-specific syntax beyond normal Markdown links.
- Creating automated semantic graph visualization.
- Changing the meaning of existing decisions, todos, or open questions.

## Deliverables
- Updated templates/prompts for cross-link conventions.
- Tests for link validation or health lint behavior.
- Docs explaining required versus recommended links.
- One git commit for this task only.

## Acceptance Criteria
- New decision, todo, and open question templates include source links to meeting analysis or artifacts.
- Meeting analysis templates link back to superseded or related current-state entries when applicable.
- Timeline entries include links to the meeting or artifact that caused the project-state change.
- Validation or health lint reports missing critical links without guessing facts.

## Verification Evidence
- Follow TDD:
  1. Write a failing test for a missing required source link.
  2. Verify red for the expected missing-link behavior.
  3. Implement the minimal link check or template change.
  4. Add a failing test for a valid linked entry.
  5. Verify red, implement green, refactor while tests remain green.
- Run relevant tests.
- Generate or inspect a sample project file set with links.
- Show `git diff --stat` before committing.

## Operating Rules
- Links improve navigation; they do not replace explicit source fields.
- Do not invent related links when source relationships are unclear.
- Keep ordinary-mode docs simple and DIY docs precise.

## Prohibited Exit
- Do not claim completion if links are only described in prose and not represented in templates/prompts or checks.
- Do not auto-add speculative cross-links.
- Do not include unrelated refactors in the commit.

## Exit Conditions
The task is complete only after link conventions are implemented, tested, documented, verified, and committed as one focused change.
