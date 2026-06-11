# Example Project Knowledge Structure

默认示例是一项目一 knowledge 仓库。

```text
customer-platform-knowledge/
├── project.md
├── project-config.yaml
├── inbox/
│   └── 2026-06-09_customer-platform_uat-planning_transcript.md
├── domain/
│   ├── glossary.md
│   ├── taxonomy.md
│   ├── entity-registry.md
│   ├── decision-types.md
│   └── writing-style.md
├── meetings/
│   └── 2026/
│       └── 2026-06-09_remote_uat-planning/
│           ├── metadata.yaml
│           ├── transcript.md
│           ├── analysis.md
│           └── artifacts/
│               ├── manifest.yaml
│               └── source-deck.pdf
├── knowledge/
│   ├── current-summary.md
│   ├── by-domain.md
│   ├── current-decisions.md
│   ├── current-open-questions.md
│   ├── current-todos.md
│   ├── timeline.md
│   ├── domain-context.md
│   ├── entity-aliases.md
│   ├── project-taxonomy.md
│   └── source-map.md
└── archive/
    └── superseded/
```

## Example Meeting Directory Name

```text
YYYY-MM-DD_<location>_<topic>
2026-06-09_remote_uat-planning
2026-06-10_client-site_solution-review
```

## Example Source Link

从项目 rollup 链接回单场会议：

```markdown
../meetings/2026/2026-06-09_remote_uat-planning/analysis.md
```

从会议分析链接到附件：

```markdown
artifacts/source-deck.pdf
```

## Portfolio / Index Example

原来的大 vault 结构只用于 portfolio/index 或 legacy/special-case 模式：

```text
portfolio-knowledge-index/
├── vault.yaml
├── projects/
│   ├── customer-platform/
│   └── internal-ai-agent/
├── global/
│   ├── current-summary.md
│   ├── decision-register.md
│   ├── open-question-register.md
│   ├── todo-register.md
│   └── timeline.md
└── archive/
    └── superseded/
```

Legacy vault 迁移后应拆成多个独立项目仓库：

```text
customer-platform-knowledge/
internal-ai-agent-knowledge/
```

不要继续把新项目默认追加到同一个 legacy vault。
