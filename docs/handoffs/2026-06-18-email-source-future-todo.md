# 2026-06-18 Email Source Future Todo Handoff

## Scope

本阶段把“邮件可以作为项目来源证据”的方向沉淀为协议和未来开口，但不实现邮箱检索功能。Apple Mail 只是一个可能的本地来源适配器，不是 `meeting-helpers` 的核心依赖。

## Current State

已新增或更新的正式工件：

- `templates/email-source-artifact.md`：邮件来源 artifact 模板，记录来源系统、账号、检索请求、邮件元数据、摘要、关键事实、项目影响和隐私/存储边界。
- `docs/future-todos.md`：记录邮件来源适配器是未来 todo，当前不实现 Apple Mail 自动检索、Gmail / Outlook adapter、后台监控、周期扫描、自动同步或 `.eml` 批量导入 CLI。
- `README.md`：普通版入口说明邮件只是补充来源；当前只定义来源 artifact 协议和 Agent 处理边界。
- `docs/ordinary-and-diy-modes.md`：明确邮件来源必须由用户指定范围触发，不主动扫描邮箱。
- `AGENTS.md`：明确 Agent 不把邮箱当作后台监控对象，且不默认复制完整邮件正文或附件。
- `prompts/analyze-meeting.md`、`prompts/update-rollups.md`、`checklists/meeting-ingest-checklist.md`：把邮件来源处理写成 Agent 执行责任。

## Capability Boundary

当前版本支持：

- 用户提供邮件导出、截图、转发文本或粘贴邮件内容后，Agent 可整理成来源 artifact。
- 用户明确要求按标题、近似标题、发件人、收件人或时间范围检索时，Agent 可使用当前会话中可用工具辅助查找，并把结果整理成来源 artifact。
- 邮件 artifact 可作为 `current-*`、`timeline.md` 或会议分析的来源证据。

当前版本不支持：

- 通用邮箱检索 adapter。
- Apple Mail 自动检索脚本。
- Gmail / Outlook 统一接入。
- 邮箱后台监控、周期扫描或默认同步。
- 自动从邮件生成会议目录或 rollup 的完整流水线。

## Rules To Preserve

- 用户显式触发检索；不做主动邮件监控。
- 检索范围必须由用户提供，例如标题、近似标题、发件人、收件人或时间范围。
- Apple Mail、Gmail、Outlook、`.eml`、粘贴邮件正文只是不同来源适配器；不要把其中任何一个做成核心依赖。
- 默认保存摘要、元数据、关键事实、项目影响和访问边界。
- 完整正文和附件只有在用户明确要求时保存，并按 artifact 策略处理敏感内容。
- 不得把邮件收件时间当作会议发生时间；邮件只能作为邮件沟通、客户确认或项目证据的时间来源。

## Verification Evidence

Latest verification before this handoff:

```bash
python3 -m unittest tests.test_meeting_helpers
```

Result: 17 tests passed.

```bash
python3 scripts/meeting_helpers.py --help | rg "init-project|validate-project|health-lint|commit"
```

Result: expected commands are exposed.

```bash
git diff --check
```

Result: no whitespace errors.

## Open Items

- 本轮没有提交；工作区仍有未提交文档和模板改动。
- 如以后要实现邮件 adapter，应先写独立计划和测试，不要直接把 Apple Mail 能力塞进普通版主路径。
- 没有关联 GitLab issue 或 MR；本次 `neat` 只做 repo 本地交接。

## Learning Decision

无需新增独立 learning。这里是一个明确降级为 future todo 的产品边界调整，复用价值已经写入 `docs/future-todos.md` 和本 handoff。
