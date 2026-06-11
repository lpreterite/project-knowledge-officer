# Adoption Levels

这套机制分两层使用，避免新用户一开始被完整体系压垮。

## Minimal

适合刚开始使用，目标是先把会议事实、决定、todo 和未决事项维护起来。

Vault：

```text
<vault-root>/
├── vault.yaml
├── inbox/
├── projects/
└── archive/
```

项目：

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

Minimal 也允许在表格里使用 `Domain`，但不要求维护 `by-domain.md`。

## Advanced

适合会议数量多、领域术语多、需要跨项目汇总或团队多人维护的场景。

Advanced 在 Minimal 基础上增加：

Vault：

```text
domain/
global/
```

项目：

```text
knowledge/
├── by-domain.md
├── domain-context.md
├── entity-aliases.md
├── project-taxonomy.md
└── source-map.md
```

## 选择建议

- 新用户默认从 Minimal 开始。
- 当同一个术语、实体、指标或分类反复出现，再打开 Advanced。
- 当需要跨项目看所有 todo、decision、open question，再打开 global registers。
- 不要为了显得完整而维护没人看的文件。

