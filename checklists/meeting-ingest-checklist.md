# Meeting Ingest Checklist

## 入库前

- [ ] 已确认 `<vault-root>`。
- [ ] 新材料已放入 `<vault-root>/inbox/`。
- [ ] 已读取 vault 级 `domain/*` 文件。
- [ ] 已确认项目 ID。
- [ ] 已读取项目级 `domain-context.md`、`entity-aliases.md`、`project-taxonomy.md`、`source-map.md`。
- [ ] 已确认会议实际发生日期。
- [ ] 已确认会议地点或渠道。
- [ ] 已确认会议主题。
- [ ] 已确认是否已有 ASR / transcript。
- [ ] 如果只有文件创建时间，已停止入库并询问用户会议实际时间。

## 创建会议目录

- [ ] 目录格式为 `projects/<project-id>/meetings/YYYY/YYYY-MM-DD_<location>_<topic>/`。
- [ ] 已创建 `metadata.yaml`。
- [ ] 已创建或复制 `transcript.md`。
- [ ] 已创建 `analysis.md`。
- [ ] 附件已放入 `artifacts/`。

## 单场分析

- [ ] `analysis.md` 回答了会议目的、背景、共识、决定、未决事项、todo、风险、项目知识更新。
- [ ] 区分了事实、推断、决定和 todo。
- [ ] 每条 decision、todo、open question 都有稳定 ID。
- [ ] 每条 decision、todo、open question 都有 Domain。
- [ ] 未知 owner / due 已写 `unknown`，没有猜。
- [ ] 重要结论有 source。

## Rollup 更新

- [ ] 更新 `current-summary.md`。
- [ ] 更新 `by-domain.md`。
- [ ] 更新 `current-decisions.md`。
- [ ] 更新 `current-open-questions.md`。
- [ ] 更新 `current-todos.md`。
- [ ] 更新 `timeline.md`。
- [ ] 如有跨项目意义，更新 `global/*`。
- [ ] 如出现新术语、实体别名、指标口径或分类，已更新领域知识文件或记录待确认项。

## 冲突和版本

- [ ] 知识排序使用 `meeting_datetime`，不是 `received_datetime`。
- [ ] 明确替代旧结论时已写 `supersedes`。
- [ ] 被替代旧结论已标 `superseded`。
- [ ] 不确定冲突已进入 open question，没有覆盖。
- [ ] 同一天冲突但无具体时间时，已向用户确认先后顺序。

## 完成前

- [ ] `rg -n "meeting_datetime|received_datetime|supersedes|Domain|unknown" .` 已检查。
- [ ] `git diff --stat` 已检查。
- [ ] 剩余风险已告知用户。
- [ ] 如使用 Git，已提交 vault 变更。
