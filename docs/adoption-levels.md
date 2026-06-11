# Adoption Levels

这套机制分两层使用，避免新用户一开始被完整体系压垮。两层都以“每个项目一个 knowledge 仓库”为默认边界。

## Minimal

适合刚开始使用，目标是先把会议事实、决定、todo 和未决事项维护起来。

项目 knowledge 仓库：

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

Minimal 也允许在表格里使用 `Domain`，但不要求维护 `by-domain.md`。

## Advanced

适合会议数量多、领域术语多、项目内部多人维护或需要更强追溯的场景。

Advanced 在 Minimal 基础上增加：

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

- 新用户默认从 Minimal 项目仓库开始。
- 当同一个术语、实体、指标或分类在项目内反复出现，再打开 Advanced。
- 当需要跨项目查看目录、权限边界或同步状态，再单独建立 portfolio/index。
- 项目 knowledge 仓库默认初始化本地 Git，并在每次入库或 rollup 验证通过后提交本地 commit。
- Git 远端只在多人协作、跨设备同步、备份或审计需要时配置。
- 不要为了显得完整而维护没人看的文件。
