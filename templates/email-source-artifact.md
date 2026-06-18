# 邮件来源 Artifact

## 基本信息

- Source System: <Apple Mail|Gmail|Outlook|exported .eml|pasted email|other>
- Account / Mailbox: <account-or-mailbox-or-unknown>
- Search Request: <用户指定的标题、近似标题、发件人或时间范围>
- Subject: <email-subject>
- Thread ID: <thread-id-or-unknown>
- Message ID: <message-id-or-unknown>
- Sender: <name-and-email-or-unknown>
- Recipients: <names-and-emails-or-unknown>
- CC: <names-and-emails-or-none>
- Sent Datetime: <datetime-with-timezone-or-unknown>
- Received Datetime: <datetime-with-timezone-or-unknown>
- Local Read Datetime: <datetime-with-timezone>
- Related Project: <project-id>
- Related Meeting: <meeting-id-or-none>

## 来源边界

- Access Mode: user-requested lookup
- Access Scope: <subject|approximate subject|sender|date range|provided message|exported file>
- Privacy Note: <敏感信息、转发限制或访问边界>
- Storage Note: <summary only|body included with explicit user approval|external source only>

## 摘要

- <邮件线程或单封邮件的业务摘要。>

## 关键事实 / 主张

| ID | Assertion | Source Detail | Confidence |
| --- | --- | --- | --- |
| email-assertion-001 | <可作为项目证据的事实或主张> | <发件人、时间、主题或片段摘要> | <high|medium|low> |

## 对项目知识的影响

- `current-summary.md`: <可能需要更新的项目状态。>
- `current-decisions.md`: <可能新增或确认的决定。>
- `current-open-questions.md`: <可能新增或关闭的未决事项。>
- `current-todos.md`: <可能新增或更新的 todo。>
- `timeline.md`: <可能新增的时间线事件。>

## 来源说明

- 本 artifact 默认保存摘要和可追溯元数据，不默认保存完整邮件正文。
- 如需保存完整邮件正文、附件或导出文件，必须有用户明确要求，并按项目 artifact 策略登记 `artifacts/manifest.yaml`。
- 不得把邮箱收件时间当作会议发生时间；邮件只能作为其自身发送、接收或项目沟通时间的来源。
