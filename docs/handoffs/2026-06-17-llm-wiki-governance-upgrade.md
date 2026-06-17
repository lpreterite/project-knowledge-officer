# 2026-06-17 LLM Wiki Governance Upgrade Handoff

## Scope

本阶段把 Karpathy-style LLM Wiki 中适合本仓库的治理机制落到 `meeting-helpers`，但保留本仓库的会议/项目知识治理边界：来源证据、项目独立 knowledge repo、Domain、状态、artifact manifest、validate/commit 纪律仍是核心约束。

## Implemented Commits

| Commit | Change |
| --- | --- |
| `e0190c8` | Add project-level `knowledge/index.md` navigation surface. |
| `256d271` | Add append-only `knowledge/log.md` operation log. |
| `a0d6e5b` | Add independent `health-lint` warning layer. |
| `697f3e5` | Add sourced `knowledge/briefs/*.md` query archive briefs. |
| `08c28a2` | Strengthen Markdown cross-link conventions and lint checks. |

Planning prompt commits immediately before implementation:

| Commit | Change |
| --- | --- |
| `2176728` | Define project knowledge index goal. |
| `6e9b81f` | Define project knowledge log goal. |
| `7199349` | Define knowledge health lint goal. |
| `568a9e4` | Define query archive briefs goal. |
| `b1f2fd8` | Define project cross-linking goal. |
| `b5f9c11` | Define parent LLM wiki governance upgrade goal. |

## Current Capabilities

- New project repos include `knowledge/index.md`, `knowledge/log.md`, and `knowledge/briefs/_template.md`.
- `validate-project` now checks required index/log structures.
- `health-lint` reports heuristic knowledge risks without mutating project facts.
- Briefs are opt-in derived analysis artifacts and must cite both project files and meeting/artifact sources.
- Rollup, timeline, meeting analysis, brief, and artifact links use plain Markdown link conventions documented in `docs/cross-link-conventions.md`.

## Verification Evidence

Latest verification before this handoff:

```bash
python3 -m unittest tests.test_meeting_helpers
```

Result: 17 tests passed.

```bash
python3 scripts/meeting_helpers.py --help | rg "health-lint|init-project|validate-project|commit"
```

Result: expected commands are exposed, including `health-lint`.

Earlier implementation smoke tests generated temp project repos and ran:

```bash
init-project
new-meeting
validate-project
health-lint
```

Result: generated project validation returned `OK`; clean health lint returned `OK`; intentionally incomplete brief/link fixtures produced warnings as expected.

## Source Of Truth For Next Agent

Read first:

- `AGENTS.md`
- `README.md`
- `docs/versioning.md`
- `docs/cross-link-conventions.md`
- `checklists/meeting-ingest-checklist.md`
- `scripts/meeting_helpers.py`
- `tests/test_meeting_helpers.py`

Task contracts live in:

- `prompts/goals/00-llm-wiki-governance-upgrade.md`
- `prompts/goals/01-add-project-knowledge-index.md`
- `prompts/goals/02-add-project-knowledge-log.md`
- `prompts/goals/03-add-knowledge-health-lint.md`
- `prompts/goals/04-add-query-archive-briefs.md`
- `prompts/goals/05-strengthen-project-cross-links.md`

## Known Boundaries

- Do not collapse the project model into generic `raw/` plus `wiki/`.
- Do not let `knowledge/index.md`, `knowledge/log.md`, or `knowledge/briefs/*.md` replace formal `current-*`, `timeline.md`, meeting `analysis.md`, or artifact manifests.
- `health-lint` warnings are review prompts. They must not auto-rewrite decisions, todos, open questions, rollups, or domain files.
- Briefs are saved only when the user explicitly asks to archive or preserve an answer.
- Markdown links improve navigation but do not replace explicit source fields.

## Open Items

- Remote sync is not done in this handoff. Local `main` is ahead of `origin/main`; push when the user wants remote publication.
- `health-lint` remains intentionally heuristic. Future checks should be added with TDD and should default to warnings unless the existing governance model requires hard errors.
- No separate `docs/learnings/` entry was created. The reusable patterns are already captured in `docs/cross-link-conventions.md`, the goal prompts, and this handoff.

## Learning Decision

无需新增独立 learning。This was a planned repo capability upgrade with stable writeback into source docs, templates, tests, and handoff. No workflow failure or reusable badcase was observed beyond the already codified TDD and governance rules.
