# Meeting Ingest Checklist

## 入库前

- [ ] 已确认 `<project-knowledge-root>`。
- [ ] 新材料已放入 `<project-knowledge-root>/inbox/`。
- [ ] 已确认项目 ID。
- [ ] 已读取 `project.md`、`project-config.yaml` 和 `knowledge/current-*`。
- [ ] 如启用 advanced profile，已读取项目仓库级 `domain/*` 和项目级 `domain-context.md`、`entity-aliases.md`、`project-taxonomy.md`、`source-map.md`。
- [ ] 已确认会议实际发生日期。
- [ ] 已确认会议地点或渠道。
- [ ] 已确认会议主题。
- [ ] 已确认是否已有 ASR / transcript。
- [ ] 已确认 artifacts 是否应进入 Git；大型/敏感原始材料是否改用外部受控存储并记录 source link/hash。
- [ ] 外部或 ignored artifact 已登记 `artifacts/manifest.yaml`，并补齐 `filename`、`storage`、`path`、`size_bytes`、`sha256`、`received_datetime`、`source_note`、`access_note`、`git_policy`。
- [ ] 如果只有文件创建时间，已停止入库并询问用户会议实际时间。

## 创建会议目录

- [ ] 目录格式为 `meetings/YYYY/YYYY-MM-DD_<location>_<topic>/`。
- [ ] 已创建 `metadata.yaml`。
- [ ] 已创建或复制 `transcript.md`。
- [ ] 已创建 `analysis.md`。
- [ ] 附件已放入 `artifacts/`。
- [ ] `artifacts/manifest.yaml` 已创建并登记所有 artifact 或外部 artifact metadata；`sha256` 为实际 hash 或显式 `pending`。

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
- [ ] 如明确启用 portfolio/index 模式且有跨项目意义，更新 `global/*`。
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
- [ ] `validate-project` 已通过。
- [ ] 已确认提交边界是完整会议 ingest、analysis、rollup 和验证后的知识更新，不是单纯创建 meeting skeleton。
- [ ] 已创建本地 Git commit；commit 命令会再次运行验证。
- [ ] 未使用 `--allow-invalid`，除非用户明确要求保存不完整状态。
- [ ] 未使用 `--include-artifacts`，除非已确认项目 `artifact_git_policy` 允许提交这些原始/大型附件。
- [ ] manifest 中无 `sha256: pending`；如仍为 pending，已有用户明确批准并使用 `--allow-pending-artifacts` 保存中间态。
- [ ] 无未知 untracked/modified 文件混入提交；未使用 `--include-extra`，除非用户明确确认。
- [ ] 已单独判断是否需要配置 remote 或 `git push`；只有多人协作、同步、备份或审计需要时才推送。
- [ ] 剩余风险已告知用户。
