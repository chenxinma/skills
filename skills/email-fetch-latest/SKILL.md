---
name: email-fetch-latest
description: 提供完整的独立邮件收取功能，包含 IMAP EmailClient 实现，支持从 IMAP 服务器同步最新邮件并以 JSON 格式存储到 assets 目录。
---

# Skill: email-fetch-latest

# 收取最新邮件 Skill

## 概述

这个 skill 提供完整的独立邮件收取功能，包含 IMAP EmailClient 实现，支持从 IMAP 服务器同步最新邮件并以 JSON 格式存储到 assets 目录。IMAP 服务配置从外部 JSON 文件传入。

## 快速使用

脚本调用方式（必须直接执行，不要用 `uv run python` 或 `python`）：

```bash
# 使用配置文件运行
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json \
  --days 3 \
  --output assets/emails
```

!!**注意：不要读取IMAP配置文件`config.json`的具体内容**

## 目录结构

```
skills/email-fetch-latest/
├── SKILL.md                          # 本文档
├── scripts/
│   └── fetch_latest_emails.py        # 主脚本（含完整 IMAP 实现）
└── assets/
    └── emails/                       # 邮件 JSON 存储目录
        ├── INBOX/
        │   ├── 12345.json
        │   └── index.json
        └── Sent/
            ├── 67890.json
            └── index.json
```

## 配置文件格式

```json
{
  "mail": {
    "imapServer": "imap.example.com",
    "imapPort": 993,
    "emailAddress": "your@example.com",
    "emailPassword": "your-app-password",
    "indexedFolders": ["INBOX"]
  }
}
```

## 核心实现

### EmailClient 类

```python
class EmailClient:
    """IMAP 邮件客户端"""
    
    def connect(self) -> bool:
        """连接到 IMAP 服务器"""
        ...
    
    def disconnect(self):
        """断开连接"""
        ...

    def list_folders(self) -> List[str]:
        """获取所有文件夹"""
        ...
    
    def fetch_emails(self, folder: str = "INBOX", days: int = 3, last_uid: int = 0) -> List[Email]:
        """获取指定文件夹的邮件"""
        ...
```

### Email 数据类

```python
@dataclass
class Email:
    uid: str
    subject: str
    sender: str
    recipient: str
    date: datetime
    content: str
    folder: str
```

## 输出格式

邮件以 JSON 格式存储到 assets 目录：

```
assets/emails/
├── INBOX/
│   ├── 12345.json
│   ├── 12346.json
│   └── index.json
└── Sent/
    ├── 67890.json
    └── index.json
```

### 单个邮件 JSON 格式

```json
{
  "uid": "12345",
  "subject": "会议通知",
  "sender": "sender@example.com",
  "recipient": "your@example.com",
  "date": "2026-03-09T10:30:00+08:00",
  "content": "邮件正文内容...",
  "folder": "INBOX",
  "fetched_at": "2026-03-09T16:00:00+08:00"
}
```

### 索引文件 (index.json)

每个文件夹会生成一个索引文件：

```json
{
  "folder": "INBOX",
  "last_uid": 12346,
  "fetched_at": "2026-03-09T16:00:00+08:00",
  "email_count": 2,
  "emails": [
    {"uid": "12345", "subject": "会议通知", "date": "2026-03-09T10:30:00+08:00"},
    {"uid": "12346", "subject": "项目更新", "date": "2026-03-09T11:00:00+08:00"}
  ]
}
```

## 使用示例

### 使用主脚本

脚本调用方式（必须直接执行，不要用 `uv run python` 或 `python`）：

```bash
# 收取最近 2 天的邮件（默认）
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json

# 收取最近 7 天的邮件
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json --days 7

# 指定输出目录
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json --output assets/my-emails

# 指定文件夹
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json --folders "INBOX,Sent"
```

## 脚本参数

| 参数 | 短参数 | 说明 | 默认值 |
|------|--------|------|--------|
| `--config` | `-c` | 配置文件路径 | `data/config.json` |
| `--days` | `-d` | 收取最近 N 天的邮件 | `2` |
| `--output` | `-o` | 输出目录 | `assets/emails` |
| `--folders` | `-f` | 要收取的文件夹（逗号分隔） | 配置文件中的 indexedFolders |
| `--last-uid-file` | | 最后 UID 记录文件 | `{output}/last_uid.json` |

## 增量获取策略

脚本会记录每个文件夹最后处理的 UID，下次运行时只获取新邮件：

```python
# 读取最后 UID
last_uid_file = Path(output_dir) / "last_uid.json"
if last_uid_file.exists():
    with open(last_uid_file) as f:
        last_uids = json.load(f)
else:
    last_uids = {}

# 过滤邮件
last_uid = last_uids.get(folder, 0)
email_ids = [
    eid for eid in email_ids
    if int(eid.decode('utf-8')) > last_uid
]

# 保存新的最后 UID
last_uids[folder] = max_uid
with open(last_uid_file, "w") as f:
    json.dump(last_uids, f, indent=2)
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 连接 IMAP 服务器失败 | 网络问题/凭证错误 | 检查配置和网络 |
| 认证失败 | 密码错误或需要应用专用密码 | 使用应用专用密码 |
| 文件夹不存在 | 配置了不存在的文件夹 | 检查文件夹名称 |
| SSL/TLS 错误 | 端口或加密方式不匹配 | 使用正确的端口（993/SSL） |

## 安全建议

1. **不要使用主密码** - 使用邮箱提供商的应用专用密码
2. **保护配置文件** - 确保配置文件权限设置为 600
3. **不要提交敏感信息** - 将配置文件添加到 .gitignore
4. **定期清理** - 定期清理 assets 目录中的旧邮件
