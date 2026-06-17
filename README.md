# Meeting Helpers

这是一套给 Codex 或其他本地通用 Agent 使用的会议知识库维护机制。目标是让普通白领不用手敲命令，也能把会议录音、ASR、附件、PDF/PPT、截图和补充信息整理成可追溯、可迭代、可按项目汇总的本地 Markdown 知识库。

第一版默认是本地使用，不是云端 SaaS。`meeting-helpers` 自己是机制包，只保存规则、模板、prompt、脚本和示例结构，不保存真实会议知识。

## 普通版怎么开始

普通版是默认入口。用户只需要在 Codex 或本地 Agent 里说：

```text
帮我为「项目名」建立会议知识库。
```

Agent 只需要向用户确认：

1. 项目叫什么？
2. 使用普通版还是 DIY 版？
3. 此项目默认只给你本人本机使用；如果以后要共享给同事，我会先帮你检查敏感附件和共享范围。是否按这个默认设置？

项目知识文件夹默认建议放在：

```text
~/MeetingKnowledge/<project-id>-knowledge
```

用户可以指定其他路径，但普通版不把路径作为必答问题。

以后有新会议时，用户可以直接把材料交给 Agent，并说明：

```text
把这场会议入库到「项目名」，会议实际日期是 YYYY-MM-DD。
```

普通版每场会议只把两件事作为必答：属于哪个项目、会议实际发生日期。会议主题、地点、材料类型、参会人、owner 和 due 由 Agent 先从材料中提取；提不出来就写 `unknown` 或列为待确认项，不阻塞初稿。会议实际日期不明确时必须先问用户，因为它决定知识排序。

普通版用户只需要理解 4 个概念：

| 概念 | 含义 |
| --- | --- |
| 项目文件夹 | 某个项目的会议和项目知识都在一个本地文件夹中。 |
| 待处理材料 | 新会议文字、录音、PDF、PPT、图片或补充说明都可以交给 Agent。 |
| 当前项目状态 | Agent 维护项目当前总结、决定、待办、未决问题和时间线。 |
| 来源证据 | 重要结论都要能追到会议或附件。 |

`knowledge/index.md` 是 Agent 和项目成员的导航入口，用来快速定位当前摘要、决定、Todo、未决事项、会议和重要材料；正式结论仍以 `current-*`、会议 `analysis.md` 和来源 artifact 为准。

`knowledge/log.md` 是追加式操作日志，用来记录 Agent 对知识库做过哪些 ingest、建会、归档或检查动作；项目事实的时间线仍以 `timeline.md` 为准。

当用户明确要求“把这个回答沉淀/归档/保存为项目理解”时，可以把高质量查询答案保存为 `knowledge/briefs/*.md`。Brief 是带来源引用的二次分析材料，不是正式 decision、todo、open question 或 current summary；如果 brief 中的内容需要进入当前项目状态，必须另行按 rollup 流程更新 `current-*` 并链接回会议或 artifact。

## DIY 版什么时候用

当用户想自己调整模板、分类、脚本、Git、校验、附件策略或协作边界时，切换到 DIY 版。DIY 版不是能力等级标签，而是“用户愿意自己动手配置和维护”的工作方式。

双模式规则见 [docs/ordinary-and-diy-modes.md](docs/ordinary-and-diy-modes.md)。现有脚本和配置里的 `minimal` / `advanced` 是内部 profile 兼容名：`minimal` 是普通版能力底座，`advanced` 是 DIY 版可以启用的结构能力扩展。

项目知识文件之间的链接约定见 [docs/cross-link-conventions.md](docs/cross-link-conventions.md)。普通版用户不需要手工维护这些链接；Agent 在写入 rollup、timeline、brief 和会议分析时负责保留来源链接。

## 机制包包含内容

```text
meeting-helpers/
├── AGENTS.md
├── README.md
├── prompts/
│   ├── analyze-meeting.md
│   └── update-rollups.md
├── domain/
│   ├── glossary.md
│   ├── taxonomy.md
│   ├── entity-registry.md
│   ├── decision-types.md
│   └── writing-style.md
├── templates/
│   ├── vault.yaml
│   ├── project-config.yaml
│   ├── project.md
│   ├── metadata.yaml
│   ├── transcript.md
│   ├── meeting-analysis.md
│   ├── knowledge-index.md
│   ├── knowledge-log.md
│   ├── current-summary.md
│   ├── by-domain.md
│   ├── current-decisions.md
│   ├── current-open-questions.md
│   ├── current-todos.md
│   ├── timeline.md
│   ├── global-register.md
│   └── project-knowledge/
│       ├── domain-context.md
│       ├── entity-aliases.md
│       ├── project-taxonomy.md
│       └── source-map.md
├── checklists/
│   └── meeting-ingest-checklist.md
├── scripts/
│   └── meeting_helpers.py
├── docs/
│   ├── ordinary-and-diy-modes.md
│   ├── adoption-levels.md
│   ├── cross-link-conventions.md
│   └── versioning.md
└── examples/
    └── vault-structure.md
```

## 默认仓库模型

默认模型是“每个项目一个 knowledge Git 仓库”：

```text
project-a-knowledge/
├── project.md
├── project-config.yaml
├── inbox/
├── meetings/
├── knowledge/
└── archive/
```

真实项目知识不默认放进一个统一大 vault。员工共享知识的范围由他们共同参与的项目仓库决定：

- 甲维护 A/B/C。
- 乙维护 B/C/D。
- 丙维护 A/X/Y。
- 甲乙共享 B/C。
- 甲丙共享 A。
- 乙丙没有直接共享项目。

项目 knowledge 仓库默认使用本地 Git 形成可追溯版本历史；远端不是前置条件。普通版中这些动作由 Agent 执行，不要求用户理解 Git。需要多人协作、跨设备同步、备份或审计时，再创建远端仓库，例如 `project-a-knowledge.git`。

每个项目 knowledge 仓库都应在 `project.md` 和 `project-config.yaml` 中声明协作与共享边界。默认语义是：知识只对本项目参与者共享，不存在隐式全局共享；跨项目引用必须保留明确来源，并经用户确认后才进入另一个项目的当前结论。

原来的“一个 vault Git 管多个 `projects/<project-id>/`”现在只作为 portfolio/index 或 legacy/special-case 模式，见 [docs/versioning.md](docs/versioning.md)。

## DIY 版：放到新仓库的方式

如果你要把这套机制下放到另一个机制仓库，最简单方式：

1. 把 `AGENTS.md` 复制到目标机制仓库根目录。
2. 把 `prompts/`、`templates/`、`checklists/` 和 `scripts/` 复制到目标机制仓库。
3. 先按 [docs/adoption-levels.md](docs/adoption-levels.md) 选择普通版或 DIY 版；脚本参数仍使用 `minimal` / `advanced` 作为内部 profile 名。
4. 为每个真实项目创建独立的 `<project-knowledge-root>`。
5. 在团队文档中记录项目知识仓库本地路径；只有需要多人协作时才配置远端地址。

`<project-knowledge-root>` 应是独立目录和独立本地 Git 仓库。不要在 `meeting-helpers` 机制包仓库、legacy vault 的 `projects/` 子目录、或另一个 project knowledge repo 内运行 `init-project`。确需接管已有目录时，必须显式使用 `--adopt-existing`。

## 普通版能力底座

```text
<project-knowledge-root>/
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
    └── superseded/
```

## DIY 版结构扩展

DIY 版需要领域知识、项目 taxonomy 或 source map 时，可以启用脚本里的 `advanced` profile，额外增加：

```text
<project-knowledge-root>/
├── domain/
│   ├── glossary.md
│   ├── taxonomy.md
│   ├── entity-registry.md
│   ├── decision-types.md
│   └── writing-style.md
└── knowledge/
    ├── by-domain.md
    ├── domain-context.md
    ├── entity-aliases.md
    ├── project-taxonomy.md
    └── source-map.md
```

每场会议：

```text
meetings/YYYY/YYYY-MM-DD_<location>_<topic>/
├── metadata.yaml
├── transcript.md
├── analysis.md
└── artifacts/
    └── manifest.yaml
```

## Agent 内部基本流程

1. 新材料进入项目知识仓库的 `inbox/`。
2. 读取 `project-config.yaml` 和当前项目知识文件。
3. 如果启用了 DIY 版结构扩展，再读取项目仓库内 `domain/*` 和 `knowledge/*context` 文件。
4. 普通版只向用户确认项目和会议实际日期；主题、地点、材料类型和 ASR 状态先由 Agent 识别并回显。
5. 创建会议目录，保留原始 transcript 和附件。
6. 用 `prompts/analyze-meeting.md` 生成 `analysis.md`。
7. 用 `prompts/update-rollups.md` 更新项目 `knowledge/current-*`，并维护 `knowledge/index.md` 作为导航入口。
   - 维护 `knowledge/log.md` 作为操作日志；不要把原始 transcript 或敏感附件内容复制进 log。
8. 如果出现新术语、实体、指标口径或项目分类，建议更新领域知识文件。
9. 检查 source、Domain、unknown owner / due、冲突和时间可信度。
10. 验证通过后提交本地 Git 版本；只有多人协作或同步需要时才推送远端。

## DIY 版：可选脚本

如果目标项目知识仓库还没有自己的脚本，可以先用 `scripts/meeting_helpers.py` 创建最小结构。

初始化项目知识仓库：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge init-project \
  --project-id project-a \
  --name "Project A"
```

`init-project` 默认会执行本地 `git init` 并创建初始 baseline commit。baseline commit 只包含本次脚手架生成的文件；如果目录里已有其他材料，不会被自动纳入初始提交。特殊场景不想初始化 Git 时，可加 `--no-git`。如果本机缺少 Git 或 Git 作者配置导致 commit 失败，脚本会保留已创建目录并输出 warning。

初始化 DIY 版结构扩展项目知识仓库：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge init-project \
  --project-id project-a \
  --name "Project A" \
  --profile advanced
```

创建会议：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge new-meeting \
  --date 2026-06-09 \
  --location remote \
  --topic uat-planning \
  --transcript /path/to/project-a-knowledge/inbox/2026-06-09_project-a_uat-planning_transcript.md
```

验证项目知识仓库：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge validate-project
```

检查项目知识健康风险：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge health-lint
```

`health-lint` 不替代 `validate-project`。`validate-project` 检查结构、字段、Domain、来源和 artifact manifest 是否满足硬性规则；`health-lint` 只报告需要人工复核的知识健康 warning，例如重复 open todo、缺少 Markdown source link、open question 未进入 timeline、`active` 决定仍带 `Supersedes`、DIY 版重复术语未进入领域知识、brief 缺少项目或会议来源引用。

验证通过后提交本地版本：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge commit \
  -m "Update project-a rollups"
```

`commit` 命令默认会先运行项目验证；验证失败不会创建本地 commit。只有明确需要保存迁移中间态或 WIP 时，才使用 `--allow-invalid` 跳过验证。

`commit --project-root` 只会自动提交受控知识表面，例如 `project.md`、`project-config.yaml`、`knowledge/*.md`、`domain/*.md`、会议 `metadata.yaml`、`transcript.md`、`analysis.md` 和 `artifacts/manifest.yaml`。未知路径默认拒绝提交；只有用户明确确认后，才使用 `--include-extra`。

项目仓库默认生成 `.gitignore`，并通过 `artifact_git_policy` 约束附件入 Git：Markdown/YAML 知识文件默认提交；录音、视频、压缩包和超过默认阈值的大型 artifact 默认应保存在外部受控位置，并在知识库中记录 source link/hash。只有确认项目附件策略后，才使用 `--include-artifacts` 提交已进入候选提交的大型附件；被 `.gitignore` 忽略的原始媒体需要先按项目策略调整 ignore 规则。

每场会议的 `artifacts/manifest.yaml` 是 artifact 可追溯性的正式索引。即使原始文件不进入 Git，也要提交 `filename`、`storage`、`path`、`size_bytes`、`sha256`、`received_datetime`、`source_note`、`access_note`、`git_policy`，避免结论来源断链或同名文件漂移。`path` 相对会议目录。`sha256` 应为实际 hash；暂时无法计算时只能显式写 `pending`。正式本地 commit 默认拒绝 `sha256: pending`，并会复算本地 artifact 的 size/hash；只有明确要保存不完整中间态时，才使用 `--allow-pending-artifacts`。

只有需要多人协作、同步、备份或审计时，才配置远端并 `git push`。

为项目设置自己的 Domain：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge set-domains \
  "客户目标" "需求范围" "方案决策" "数据材料" "交付推进" "风险依赖" "责任协作"
```

Portfolio/index 或 legacy vault 模式仍然可用：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/portfolio-index init-vault
python3 scripts/meeting_helpers.py --vault-root /path/to/portfolio-index new-project project-a --name "Project A"
python3 scripts/meeting_helpers.py --vault-root /path/to/portfolio-index validate-vault
```

Portfolio/index 默认只保存项目目录、仓库链接、访问边界和同步状态，不复制项目级 decisions、todos 或 open questions。项目 knowledge 仓库仍是 authoritative source。只有用户明确确认 portfolio 本身是有权限边界的汇总知识项目时，才可以维护 special-case global fact register，并且每条摘要都必须链接回来源项目仓库和来源会议或 artifact。

`--vault-root commit` 默认只用于提交 portfolio/index 元数据。检测到 `projects/*` 项目事实或 global fact register 变更时会拒绝提交；只有明确维护 legacy/special-case fact vault 时，才使用 `--legacy-fact-vault`。

从 legacy vault 拆出项目时，先运行 dry-run：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/legacy-vault migrate-project project-a \
  --target-project-root /path/to/project-a-knowledge \
  --dry-run
```

dry-run 只列出复制范围、验证问题和 global fact register 依赖，不自动复制文件。迁移时只复制单项目内容，不复制 sibling projects 或 global fact registers。

## 关键原则

- 会议实际发生时间才是知识排序时间。
- 文件创建时间只能作为 `received_datetime`。
- 旧结论不删除，用 `superseded` 和 `supersedes` 保持追溯。
- 不确定的冲突进入 open question，不擅自覆盖。
- 每条 decision、todo、open question 都必须有主 `Domain`。
- 真实业务 todo 不自动变成工程 issue。
- 本地 Git 是项目知识的默认版本管理手段；Git 远端是协作和同步手段，不是本地知识维护的前置条件。
- 本地 Git 管理知识状态，不等于默认把所有原始媒体、客户附件或大型二进制文件纳入 Git 历史。

## Domain 怎么理解

`Domain` 不是固定行业术语，而是项目知识的分面视图。默认模板使用通用分类：

- `业务目标`
- `范围/需求`
- `方案/决策`
- `数据/证据`
- `交付/执行`
- `风险/依赖`
- `协作/责任`

团队可以按自己的业务替换，比如软件交付项目可以增加 `UAT`、`缺陷`、`部署`，数据项目可以增加 `指标口径`、`数据质量`，营销项目可以增加 `品牌`、`渠道`、`内容`。关键是同一个项目开始后要保持分类稳定，不要每场会议换一套。

`project-config.yaml` 是项目执行时的 authoritative taxonomy。不同客户、行业或项目类型可以使用不同 taxonomy。不要只改 `by-domain.md`，否则 prompt、脚本和验证命令会无法判断哪些 Domain 是合法的。portfolio/index vault 的 `vault.yaml` 只作为批量创建项目时的默认值。

## 领域知识层

为了让纪要有行业和团队语境，而不是泛泛摘要，helper 包提供领域知识模板。

领域知识层属于 DIY 版结构扩展，对应内部 `advanced` profile。普通版能力底座不要求维护这些文件。

项目知识仓库级：

- `domain/glossary.md`：项目内共用术语表。
- `domain/taxonomy.md`：业务分类、会议类型、决定类型。
- `domain/entity-registry.md`：项目内共用实体和别名。
- `domain/decision-types.md`：常见决定类型。
- `domain/writing-style.md`：写作风格和术语处理规则。

项目 knowledge 级：

- `knowledge/domain-context.md`：项目业务背景、流程、指标口径、不能误写成结论的内容。
- `knowledge/entity-aliases.md`：项目特有的人名、系统、平台、缩写别名。
- `knowledge/project-taxonomy.md`：项目自己的分类体系。
- `knowledge/source-map.md`：关键来源材料清单。

领域知识只帮助理解会议，不替代来源证据。正式 decision、todo、current summary 仍必须链接回会议或 artifact。
