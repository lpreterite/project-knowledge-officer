# Cross-Link Conventions

项目知识库使用普通 Markdown 链接建立证据图。链接帮助导航，但不替代 `Source` 字段、artifact manifest 或正式状态字段。

## Required Links

- `current-decisions.md`、`current-todos.md`、`current-open-questions.md` 的 `Source` 单元格必须链接到来源会议 `analysis.md`，或链接到相关 artifact manifest。
- `timeline.md` 的 `Source` 必须链接到导致项目状态变化的会议 `analysis.md` 或 artifact manifest。
- `knowledge/briefs/*.md` 必须同时包含项目来源链接和会议或 artifact 来源链接。

## Recommended Links

- 会议 `analysis.md` 中的决定、Todo、未决事项优先链接到 `transcript.md` 或 `artifacts/manifest.yaml`。
- 替代旧结论时，在新条目的 `Supersedes` 字段保留旧 ID，并在相关说明中链接回旧条目的来源。
- DIY 版领域知识文件可以链接到首次出现该术语、实体或指标口径的会议 `analysis.md`。

## Health Lint

`health-lint` 会报告缺少 Markdown source link、断开的本地 source link、brief 缺少引用等 warning。它不会自动补链，因为不清楚的来源关系必须由 Agent 回到会议或 artifact 判断。
