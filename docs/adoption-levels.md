# Adoption Levels

这套机制面向两种使用方式：普通版和 DIY 版。两种方式都默认使用“每个项目一个 knowledge 仓库”，真实会议知识不放在 `meeting-helpers` 机制包仓库里。

脚本和模板中仍保留 `minimal` / `advanced` 作为内部 profile 兼容名：

- `minimal`：普通版能力底座。
- `advanced`：DIY 版可以启用的结构能力扩展。

面向用户沟通时，优先使用“普通版 / DIY 版”，不要把 `minimal` / `advanced` 当作主称呼。

## 普通版

普通版适合默认用户：他们在 Codex 或其他本地通用 Agent 里交付会议材料，希望 Agent 帮他们管理项目知识，而不是自己维护脚本、YAML 和 Git。

普通版只暴露 4 个概念：

- 项目文件夹。
- 待处理材料。
- 当前项目状态。
- 来源证据。

普通版项目 knowledge 仓库使用 `minimal` profile：

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

普通版也允许在表格里使用 `Domain`，但不要求用户维护 `by-domain.md` 或领域知识文件。

## DIY 版

DIY 版适合愿意动手配置和维护机制的用户。Agent 可以解释目录结构、模板、taxonomy、Git、校验、附件策略和脚本参数，并协助用户修改。

DIY 版可以在普通版结构上启用 `advanced` profile：

项目仓库级：

```text
domain/
├── glossary.md
├── taxonomy.md
├── entity-registry.md
├── decision-types.md
└── writing-style.md
```

项目 knowledge 级：

```text
knowledge/
├── by-domain.md
├── domain-context.md
├── entity-aliases.md
├── project-taxonomy.md
└── source-map.md
```

不要为了显得完整而启用没人看的文件。只有当同一个术语、实体、指标、分类、协作策略或来源材料在项目中反复出现，才建议打开对应结构能力。

## 模式转换

普通版和 DIY 版可以互相转换。转换首先改变 Agent 如何协作，其次才改变项目结构。

- 普通版转 DIY 版：不改变已有会议事实，只增加可配置表面和解释文档。
- DIY 版转普通版：不删除配置、历史或领域文件，只让 Agent 重新接管执行细节。
- 转换前后都应运行项目校验。
- 转换不得改写 existing decisions、todos 或 open questions 的含义。

详细规则见 [ordinary-and-diy-modes.md](ordinary-and-diy-modes.md)。

## Portfolio / Index

跨项目视图不是默认 knowledge 存储模型。只有需要跨项目索引、访问边界记录、同步状态或历史兼容时，才维护 portfolio/index vault。

```text
portfolio-knowledge-index/
├── vault.yaml
├── projects/
├── global/
│   ├── project-index.md
│   ├── access-boundaries.md
│   └── sync-status.md
└── archive/
```

Portfolio/index 默认只保存目录、链接、权限/协作范围和同步状态，不复制项目级 decisions、todos 或 open questions。

如果项目之间有不同参与者、不同客户权限或不同远端同步策略，应拆成独立项目 knowledge 仓库，而不是放进一个统一大 vault。

Legacy fact vault commit 属于迁移或特殊运维能力，不是推荐工作流。默认应使用 `--project-root commit` 提交项目知识仓库；`--vault-root commit --legacy-fact-vault` 只在用户明确要求维护 legacy/special-case fact vault 时使用。

## 选择建议

- 新用户默认从普通版开始。
- 用户要求配置、排错、审计、模板调整或协作策略时，再切到 DIY 版。
- 当同一个术语、实体、指标或分类在项目内反复出现，再启用 `advanced` profile 的结构扩展。
- 当需要跨项目查看目录、权限边界或同步状态，再单独建立 portfolio/index。
- 项目 knowledge 仓库默认初始化本地 Git，并在每次入库或 rollup 验证通过后提交本地 commit。
- Git 远端只在多人协作、跨设备同步、备份或审计需要时配置。
