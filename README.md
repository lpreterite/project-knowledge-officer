# Meeting Helpers

这是一套可下放到其他仓库的会议知识库维护辅助文件。`meeting-helpers` 自己是机制包，不保存真实会议知识。

## 包含内容

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
│   ├── adoption-levels.md
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

项目 knowledge 仓库默认使用本地 Git 形成可追溯版本历史；远端不是前置条件。需要多人协作、跨设备同步、备份或审计时，再创建远端仓库，例如 `project-a-knowledge.git`。

每个项目 knowledge 仓库都应在 `project.md` 和 `project-config.yaml` 中声明协作与共享边界。默认语义是：知识只对本项目参与者共享，不存在隐式全局共享；跨项目引用必须保留明确来源，并经用户确认后才进入另一个项目的当前结论。

原来的“一个 vault Git 管多个 `projects/<project-id>/`”现在只作为 portfolio/index 或 legacy/special-case 模式，见 [docs/versioning.md](docs/versioning.md)。

## 放到新仓库的方式

最简单方式：

1. 把 `AGENTS.md` 复制到目标机制仓库根目录。
2. 把 `prompts/`、`templates/`、`checklists/` 和 `scripts/` 复制到目标机制仓库。
3. 先按 [docs/adoption-levels.md](docs/adoption-levels.md) 选择 `minimal` 或 `advanced`。
4. 为每个真实项目创建独立的 `<project-knowledge-root>`。
5. 在团队文档中记录项目知识仓库本地路径；只有需要多人协作时才配置远端地址。

`<project-knowledge-root>` 应是独立目录和独立本地 Git 仓库。不要在 `meeting-helpers` 机制包仓库、legacy vault 的 `projects/` 子目录、或另一个 project knowledge repo 内运行 `init-project`。确需接管已有目录时，必须显式使用 `--adopt-existing`。

## 最小项目知识仓库结构

```text
<project-knowledge-root>/
├── project.md
├── project-config.yaml
├── inbox/
├── meetings/
├── knowledge/
│   ├── current-summary.md
│   ├── current-decisions.md
│   ├── current-open-questions.md
│   ├── current-todos.md
│   └── timeline.md
└── archive/
    └── superseded/
```

`advanced` profile 会额外增加：

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

## 基本使用流程

1. 新材料进入项目知识仓库的 `inbox/`。
2. 读取 `project-config.yaml` 和当前项目知识文件。
3. 如果启用了 advanced profile，再读取项目仓库内 `domain/*` 和 `knowledge/*context` 文件。
4. 确认项目、会议实际日期、地点、主题和 ASR 状态。
5. 创建会议目录，保留原始 transcript 和附件。
6. 用 `prompts/analyze-meeting.md` 生成 `analysis.md`。
7. 用 `prompts/update-rollups.md` 更新项目 `knowledge/current-*`。
8. 如果出现新术语、实体、指标口径或项目分类，建议更新领域知识文件。
9. 检查 source、Domain、unknown owner / due、冲突和时间可信度。
10. 验证通过后提交本地 Git 版本；只有多人协作或同步需要时才推送远端。

## 可选脚本

如果目标项目知识仓库还没有自己的脚本，可以先用 `scripts/meeting_helpers.py` 创建最小结构。

初始化项目知识仓库：

```bash
python3 scripts/meeting_helpers.py --project-root /path/to/project-a-knowledge init-project \
  --project-id project-a \
  --name "Project A"
```

`init-project` 默认会执行本地 `git init` 并创建初始 baseline commit。baseline commit 只包含本次脚手架生成的文件；如果目录里已有其他材料，不会被自动纳入初始提交。特殊场景不想初始化 Git 时，可加 `--no-git`。如果本机缺少 Git 或 Git 作者配置导致 commit 失败，脚本会保留已创建目录并输出 warning。

初始化 advanced 项目知识仓库：

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

领域知识层属于 `advanced` profile。Minimal profile 不要求维护这些文件。

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
