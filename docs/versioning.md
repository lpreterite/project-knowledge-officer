# Versioning Model

这套机制有两种版本：Git 文件版本和知识语义版本。两者都需要，但解决的问题不同。

## 1. 产品仓库版本

产品仓库保存 helper、脚本、模板、prompt、AGENTS 和治理文档。

适合用一个普通 Git 仓库管理：

```text
product-repo/
├── AGENTS.md
├── prompts/
├── templates/
├── scripts/
└── docs/
```

产品仓库提交的是机制变化，例如：

- 更新 prompt。
- 修改模板。
- 增加 validator。
- 调整 AGENTS 规则。
- 发布 helper 新版本。

不要把真实会议 transcript、客户附件或项目结论放进产品仓库。

## 2. Knowledge Vault 版本

真实会议知识放在独立 `<vault-root>`，建议作为独立 Git 仓库管理。

Vault Git 记录文件如何变化：

- 新增会议目录。
- 新增 transcript、analysis、artifacts。
- 更新 `current-*`。
- 更新 `domain/*` 或项目 context。
- 更新 global registers。

建议每次入库或 rollup 后提交一次：

```bash
git status --short
git diff --stat
git add .
git commit -m "Update <project-id> meeting rollups"
```

## 3. 项目级版本

默认不建议每个项目都创建独立 Git 仓库。推荐先用一个 vault Git 管理所有项目，通过目录隔离：

```text
projects/<project-id>/
```

项目级版本主要通过三类机制实现：

1. Git 路径历史：查看某个项目目录的文件变化。
2. `timeline.md`：记录项目知识变化的业务时间线。
3. `supersedes` / `superseded`：记录新结论如何替代旧结论。

只有在以下情况才考虑项目单独 Git 仓库：

- 不同项目有完全不同访问权限。
- 不同客户数据不能放在同一个 Git 仓库。
- 项目需要独立远端同步或独立审计。
- 项目制品体量很大，必须拆仓。

如果拆成项目独立仓库，产品仓库仍然只放 helper；vault 可以退化成项目仓库集合索引。

## 4. 会议材料版本

原始材料原则上只追加，不覆盖。

推荐：

- 原始 ASR 保存在 `transcript.md` 或 `artifacts/`。
- 如果 ASR 修订，保留修订说明，不静默覆盖无法追溯的原文。
- PDF/PPT/图片/表格作为 artifact 保留。
- 用户补充信息保存为 dated note，例如 `artifacts/user-note-YYYY-MM-DD.md`。

## 5. 语义版本规则

Git 能说明文件怎么变，但不能说明“哪个结论当前有效”。当前有效性由知识文件表达：

- `current-summary.md`：当前摘要。
- `current-decisions.md`：当前有效和已替代决定。
- `current-open-questions.md`：当前未决事项。
- `current-todos.md`：当前行动项。
- `timeline.md`：结论变化过程。

当新会议替代旧结论：

- 新条目写 `supersedes: <old-id>` 或在表格中填 `Supersedes`。
- 旧条目标记为 `superseded`。
- 不删除旧来源。

如果无法确认是否替代，进入 open question。

## 6. Commit 建议

知识 vault commit 信息应按知识变化写，不按工具动作写。

示例：

```text
Ingest <project-id> <YYYY-MM-DD> meeting
Update <project-id> rollups
Add <project-id> domain context
Resolve <project-id> open questions
```

产品仓库 commit 信息应按工具能力写：

```text
Add meeting vault validator
Update meeting analysis prompt
Split helper profiles into minimal and advanced
```

