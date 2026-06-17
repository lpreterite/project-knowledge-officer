# Goal

## Objective
Execute five independent, TDD-driven improvements that borrow the useful parts of Karpathy-style LLM Wiki governance while preserving this repo's meeting/project knowledge governance model.

## Source Of Truth
- `AGENTS.md`
- `README.md`
- `docs/ordinary-and-diy-modes.md`
- `docs/versioning.md`
- `checklists/meeting-ingest-checklist.md`
- `prompts/goals/01-add-project-knowledge-index.md`
- `prompts/goals/02-add-project-knowledge-log.md`
- `prompts/goals/03-add-knowledge-health-lint.md`
- `prompts/goals/04-add-query-archive-briefs.md`
- `prompts/goals/05-strengthen-project-cross-links.md`
- Karpathy LLM Wiki gist as conceptual inspiration only.
- Astro-Han `karpathy-llm-wiki` repository as implementation inspiration only.

## Scope
Complete these five tasks in order, treating each as an independently shippable change:

1. Add project knowledge index: `prompts/goals/01-add-project-knowledge-index.md`
2. Add project knowledge log: `prompts/goals/02-add-project-knowledge-log.md`
3. Add knowledge health lint: `prompts/goals/03-add-knowledge-health-lint.md`
4. Add query archive briefs: `prompts/goals/04-add-query-archive-briefs.md`
5. Strengthen project cross-links: `prompts/goals/05-strengthen-project-cross-links.md`

## Out Of Scope
- Collapsing this repo into a generic `raw/` plus `wiki/` structure.
- Weakening source evidence, artifact manifest, Domain, status, sharing-boundary, validation, or commit rules.
- Combining the five implementation tasks into one broad commit.

## Deliverables
- Five implemented capabilities.
- Tests and verification evidence for each capability.
- Five separate focused commits, one per capability.
- A final summary that lists commit hashes, verification commands, and any remaining risks.

## Acceptance Criteria
- Each child goal's acceptance criteria are satisfied.
- Each child goal follows TDD: failing test first, expected red verified, minimal green implementation, refactor only after green.
- Each child goal is committed independently.
- The final state preserves ordinary-mode simplicity and DIY-mode configurability.

## Verification Evidence
- For each child goal, record:
  - failing test name and expected failure
  - passing test command
  - validation or health-lint command
  - files changed
  - commit hash
- After all five commits, run the full relevant test suite and `git status --short`.

## Operating Rules
- Work sequentially unless a child goal explicitly proves independent enough for parallel research.
- Before each child goal, reread its prompt and the directly relevant repo files.
- Do not carry implementation assumptions from one child goal into the next without tests.
- Protect user work: never revert unrelated changes.
- If user instructions conflict with a child prompt, the newest user instruction wins.

## Prohibited Exit
- Do not stop after creating plans or docs if implementation was requested.
- Do not mark the parent goal complete while any child goal lacks a commit or verification evidence.
- Do not claim TDD if any child goal skipped the red step.
- Do not silently shrink scope; document deferred work explicitly.

## Exit Conditions
The parent goal is complete only after all five child goals are implemented, verified, committed separately, and summarized with evidence.
