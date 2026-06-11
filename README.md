# Meeting Helpers

这是一套可下放到其他仓库的会议知识库维护辅助文件。把它放进一个新仓库后，Codex 可以按同一套规则维护会议知识库。

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

## 放到新仓库的方式

最简单方式：

1. 把 `AGENTS.md` 复制到目标仓库根目录。
2. 把 `prompts/`、`templates/`、`checklists/` 复制到目标仓库。
3. 先按 [docs/adoption-levels.md](docs/adoption-levels.md) 选择 `minimal` 或 `advanced`。
4. 在目标仓库的 `README.md` 中写明真实 knowledge vault 的路径。
5. 让用户创建或确认一个独立的 `<vault-root>`。

推荐真实知识 vault 不放在产品仓库里，而是单独建目录和 Git 仓库。

版本管理模型见 [docs/versioning.md](docs/versioning.md)：产品仓库管理 helper 机制，knowledge vault 管理真实会议知识；项目级版本默认通过 vault Git 路径历史、`timeline.md` 和 `supersedes` 维护。

## 最小 vault 结构

```text
<vault-root>/
├── vault.yaml
├── inbox/
├── projects/
└── archive/
```

每个项目：

```text
projects/<project-id>/
├── project.md
├── project-config.yaml
├── meetings/
└── knowledge/
    ├── current-summary.md
    ├── current-decisions.md
    ├── current-open-questions.md
    ├── current-todos.md
    └── timeline.md
```

`advanced` profile 会额外增加：

```text
<vault-root>/
├── domain/
└── global/

projects/<project-id>/knowledge/
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
```

## 基本使用流程

1. 新材料进入 `<vault-root>/inbox/`。
2. 读取 vault 级 `domain/*` 和项目级 context 文件。
3. 确认项目、会议实际日期、地点、主题和 ASR 状态。
4. 创建会议目录，保留原始 transcript 和附件。
5. 用 `prompts/analyze-meeting.md` 生成 `analysis.md`。
6. 用 `prompts/update-rollups.md` 更新项目 `knowledge/current-*` 和 `global/*`。
7. 如果出现新术语、实体、指标口径或项目分类，更新领域知识文件。
8. 检查 source、Domain、unknown owner / due、冲突和时间可信度。
9. 在 vault 中提交 Git 版本。

## 可选脚本

如果目标仓库还没有自己的脚本，可以先用 `scripts/meeting_helpers.py` 创建最小结构。

初始化 vault：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault init-vault
```

初始化 advanced vault：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault init-vault --profile advanced
```

创建项目：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault new-project customer-platform --name "Customer Platform"
```

创建会议：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault new-meeting customer-platform \
  --date 2026-06-09 \
  --location remote \
  --topic uat-planning \
  --transcript /path/to/my-vault/inbox/2026-06-09_customer-platform_uat-planning_transcript.md
```

验证 vault：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault validate-vault
```

验证项目：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault validate-project customer-platform
```

## 关键原则

- 会议实际发生时间才是知识排序时间。
- 文件创建时间只能作为 `received_datetime`。
- 旧结论不删除，用 `superseded` 和 `supersedes` 保持追溯。
- 不确定的冲突进入 open question，不擅自覆盖。
- 每条 decision、todo、open question 都必须有主 `Domain`。
- 真实业务 todo 不自动变成工程 issue。

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

`vault.yaml` 和 `project-config.yaml` 是分类和策略锚点。`vault.yaml` 只提供新项目默认值；真正执行时以项目级 `project-config.yaml` 为准。不同客户、行业或项目类型可以有不同 taxonomy。不要只改 `by-domain.md`，否则 prompt、脚本和验证命令会无法判断哪些 Domain 是合法的。

为项目设置自己的 Domain：

```bash
python3 scripts/meeting_helpers.py --vault-root /path/to/my-vault set-project-domains customer-platform \
  "客户目标" "需求范围" "方案决策" "数据材料" "交付推进" "风险依赖" "责任协作"
```

## 领域知识层

为了让纪要有行业和团队语境，而不是泛泛摘要，helper 包提供两层领域知识模板。

领域知识层属于 `advanced` profile。Minimal profile 不要求维护这些文件。

Vault 级：

- `domain/glossary.md`：团队共用术语表。
- `domain/taxonomy.md`：业务分类、会议类型、决定类型。
- `domain/entity-registry.md`：跨项目共用实体和别名。
- `domain/decision-types.md`：常见决定类型。
- `domain/writing-style.md`：写作风格和术语处理规则。

项目级：

- `knowledge/domain-context.md`：项目业务背景、流程、指标口径、不能误写成结论的内容。
- `knowledge/entity-aliases.md`：项目特有的人名、系统、平台、缩写别名。
- `knowledge/project-taxonomy.md`：项目自己的分类体系。
- `knowledge/source-map.md`：关键来源材料清单。

领域知识只帮助理解会议，不替代来源证据。正式 decision、todo、current summary 仍必须链接回会议或 artifact。
