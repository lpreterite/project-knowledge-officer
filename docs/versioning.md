# Versioning Model

这套机制有三层版本：机制包版本、项目知识仓库版本和知识语义版本。三者解决的问题不同。

## 1. 机制包版本

`project-knowledge-officer` 是机制包，只保存 helper、脚本、模板、prompt、AGENTS、checklist、docs 和示例结构。

适合用一个普通 Git 仓库管理：

```text
project-knowledge-officer/
├── AGENTS.md
├── prompts/
├── templates/
├── scripts/
├── checklists/
├── docs/
└── examples/
```

机制包提交的是规则和工具变化，例如：

- 更新 prompt。
- 修改模板。
- 增加 validator。
- 调整 AGENTS 规则。
- 发布 helper 新版本。

不要把真实会议 transcript、客户附件或项目结论放进机制包仓库。

## 2. 项目知识仓库版本

真实会议知识默认按项目拆成独立 knowledge Git 仓库，例如：

```text
project-a-knowledge.git
project-b-knowledge.git
project-c-knowledge.git
```

每个项目仓库只保存该项目的真实会议材料、项目 rollup、项目领域知识和附件：

```text
project-a-knowledge/
├── project.md
├── project-config.yaml
├── inbox/
├── meetings/
├── knowledge/
│   ├── index.md
│   ├── log.md
│   ├── briefs/
│   │   └── _template.md
│   ├── current-summary.md
│   ├── current-decisions.md
│   ├── current-open-questions.md
│   ├── current-todos.md
│   └── timeline.md
└── archive/
```

项目 knowledge root 应是独立目录和独立本地 Git 仓库，不应嵌套在 `project-knowledge-officer` 机制包、legacy vault 的 `projects/` 子目录或另一个 project knowledge repo 内。`project-config.yaml` 使用 `repository_role: "project_knowledge"` 标识仓库角色。

默认使用项目仓库边界表达共享范围。谁参与同一个项目，谁共享该项目知识仓库；没有共同项目，就不默认共享真实知识。

示例：

- 甲维护 A/B/C。
- 乙维护 B/C/D。
- 丙维护 A/X/Y。
- 甲乙共享 B/C。
- 甲丙共享 A。
- 乙丙没有直接共享项目。

每个项目知识仓库必须声明自己的共享边界。`project.md` 应包含“协作与共享边界”章节，`project-config.yaml` 应包含 `collaboration_scope`、`remote_policy` 和 `cross_project_references`。这些字段用于提醒维护者和 agent：项目知识不是隐式全局事实，跨项目引用必须有来源链接和用户确认。

项目知识仓库默认应初始化本地 Git，用本地 commit 记录知识如何演进。初始化时的 baseline commit 只应包含脚手架生成的配置、模板和空知识文件，不应把目录中已有的 inbox 材料或外部附件自动纳入初始提交。远端不是本地知识维护的前置条件；需要多人协作、跨设备同步、审计或备份时，再创建远端仓库并控制访问权限。

项目知识仓库 Git 记录文件如何变化：

- 新增会议目录。
- 新增 transcript、analysis、artifacts。
- 更新 `current-*`。
- 更新 `knowledge/index.md` 导航入口。
- 追加 `knowledge/log.md` 操作日志。
- 更新项目 `domain/` 或 `knowledge/*` context。

本地 commit 默认表示 validated knowledge snapshot，而不是任意文件快照。建议每次入库或 rollup 验证通过后提交一次本地 commit：

跨文件链接使用普通 Markdown 链接，约定见 [cross-link-conventions.md](cross-link-conventions.md)。链接帮助 Agent 和人类审阅证据图，但正式事实仍由 `current-*`、`timeline.md`、会议 `analysis.md` 和 artifact manifest 表达。

```bash
git status --short
git diff --stat
git add .
git commit -m "Update <project-id> meeting rollups"
```

如果使用 `scripts/meeting_helpers.py commit`，脚本会在提交前默认运行验证；验证失败时拒绝提交。只有明确需要保存迁移中间态或 WIP 时，才使用 `--allow-invalid`。

`validate-project` 是硬性结构校验。`health-lint` 是独立的知识健康检查，只报告 warning，不自动改写项目事实。它适合在入库、复盘或分享前检查重复 open todo、缺少 source link、open question 是否进入 timeline、`active` 决定是否仍带 `Supersedes`、以及 DIY 版重复术语是否需要沉淀到领域知识。

`commit --project-root` 只自动提交 validated knowledge surface：项目配置、项目说明、知识 rollup、领域知识、会议分析文件和 artifact manifest。未知路径默认拒绝提交，防止初始化前遗留文件、临时导出或本地笔记混入知识版本；只有用户明确确认后，才使用 `--include-extra`。

本地 Git 管理知识状态，不等于默认提交所有原始媒体和客户附件。项目仓库应通过 `.gitignore` 和 `artifact_git_policy` 控制附件策略：Markdown/YAML 知识文件默认入 Git；录音、视频、压缩包和大型二进制 artifact 默认放在外部受控存储，并在知识库中记录 source link/hash。只有确认项目策略后，才显式使用 `--include-artifacts` 提交已进入候选提交的大型附件；被 `.gitignore` 忽略的原始媒体需要先按项目策略调整 ignore 规则。

如果 artifact 本体不进入 Git，Git 中仍必须保留可追溯的 metadata。每场会议的 `artifacts/manifest.yaml` 是 artifact 正式索引，应登记 `filename`、`storage`、`path`、`size_bytes`、`sha256`、`received_datetime`、`source_note`、`access_note`、`git_policy`。`path` 相对会议目录。`sha256` 应为实际 hash；暂时无法计算时只能显式写 `pending`。正式本地 commit 默认拒绝 `sha256: pending`，并会复算本地 artifact 的 size/hash；只有明确要保存不完整中间态时，才使用 `--allow-pending-artifacts`。外部不可访问 artifact 需要由来源系统或人工确认 hash。正式结论引用 artifact 时，应优先引用 manifest 中的稳定条目，而不是只写一个不可验证的本地路径。

是否推送远端取决于协作方式。只有当项目需要多人共享、备份或远端审计时才执行 `git push`。

## 3. Portfolio / Index Vault

原来的“一个 vault Git 管多个 `projects/<project-id>/`”不再是默认项目知识模型。它降级为 portfolio/index 或 legacy/special-case 模式。

适用场景：

- 只保存项目仓库索引、权限说明、链接和跨项目视图。
- 团队明确需要一个 portfolio 仓库管理多个低敏项目。
- 历史 vault 已经按 `projects/<project-id>/` 运行，短期迁移成本高。
- 有专门的跨项目运营团队维护项目目录、访问边界和同步状态。

portfolio/index vault 可以长这样：

```text
portfolio-knowledge-index/
├── vault.yaml
├── projects/
│   ├── project-a/
│   └── project-b/
├── global/
│   ├── project-index.md
│   ├── access-boundaries.md
│   └── sync-status.md
└── archive/
```

Portfolio/index 默认不是事实汇总仓库，不应复制项目级 decisions、todos 或 open questions。项目 knowledge 仓库仍是 authoritative source。只有当用户明确确认 portfolio 本身是一个有权限边界的汇总知识项目时，才可以维护 special-case global fact register；每条摘要都必须链接回来源项目仓库和来源会议或 artifact。

`--vault-root commit` 默认只提交 portfolio/index 元数据。如果工作区包含 `projects/*` 项目事实或 global fact register 变更，脚本应拒绝提交。只有迁移或维护 legacy/special-case fact vault 时，才显式使用 `--legacy-fact-vault`。

如果使用这种模式，必须明确它是 portfolio/index 或 legacy 模式，而不是默认推荐。不同项目如果有不同参与者、不同客户权限或不同远端同步策略，应拆成项目知识仓库。

## 4. 会议材料版本

## 4. Legacy Vault 迁移

当历史数据仍在 `<vault-root>/projects/<project-id>/` 中时，默认目标是拆成独立项目 knowledge 仓库，而不是继续扩展 legacy vault。

推荐迁移流程：

1. 识别要迁移的单个 `project-id`。
2. 运行 dry-run 检查：

   ```bash
   python3 scripts/meeting_helpers.py --vault-root /path/to/legacy-vault migrate-project <project-id> \
     --target-project-root /path/to/<project-id>-knowledge \
     --dry-run
   ```

3. 只复制该项目目录内的 `project.md`、`project-config.yaml`、`meetings/`、`knowledge/` 和必要的项目级 `domain/` 文件；不要复制 sibling projects 或 global fact registers。
4. 补齐 `project.md` 的“协作与共享边界”、`project-config.yaml` 的 collaboration/artifact policy 字段、会议 `artifacts/manifest.yaml`。
5. 在新项目仓库运行 `validate-project`。
6. 创建本地 baseline commit。
7. 将旧 vault 标为只读、archive，或仅保留 portfolio/index 元数据。

如果旧 vault 中存在 `global/decision-register.md`、`global/todo-register.md` 等事实 register，迁移前必须检查它们是否包含该项目仍需保留的来源链接。不要把 global register 当作 authoritative source；应回到项目会议和 artifact。

## 5. 会议材料版本

原始材料原则上只追加，不覆盖。

推荐：

- 原始 ASR 保存在 `transcript.md` 或 `artifacts/`。
- 如果 ASR 修订，保留修订说明，不静默覆盖无法追溯的原文。
- PDF/PPT/图片/表格作为 artifact 保留。
- 用户补充信息保存为 dated note，例如 `artifacts/user-note-YYYY-MM-DD.md`。

## 6. 语义版本规则

Git 能说明文件怎么变，但不能说明“哪个结论当前有效”。当前有效性由知识文件表达：

- `current-summary.md`：当前摘要。
- `index.md`：导航入口，帮助 Agent 和项目成员定位当前摘要、决定、Todo、未决事项、会议和重要材料；不作为正式结论来源。
- `log.md`：追加式操作日志，记录 ingest、建会、归档、lint 等维护动作；不记录原始 transcript 或敏感附件正文。
- `briefs/*.md`：用户明确要求归档的查询答案或二次分析；必须引用项目文件和会议或 artifact 来源，不替代正式 rollup。
- `current-decisions.md`：当前有效和已替代决定。
- `current-open-questions.md`：当前未决事项。
- `current-todos.md`：当前行动项。
- `timeline.md`：结论变化过程。

当新会议替代旧结论：

- 新条目写 `supersedes: <old-id>` 或在表格中填 `Supersedes`。
- 旧条目标记为 `superseded`。
- 不删除旧来源。

如果无法确认是否替代，进入 open question。

## 7. Commit 建议

项目知识仓库 commit 信息应按知识变化写，不按工具动作写。

示例：

```text
Ingest <project-id> <YYYY-MM-DD> meeting
Update <project-id> rollups
Add <project-id> domain context
Resolve <project-id> open questions
```

机制包仓库 commit 信息应按工具能力写：

```text
Add project knowledge repository mode
Update meeting analysis prompt
Split helper profiles into minimal and advanced
```
