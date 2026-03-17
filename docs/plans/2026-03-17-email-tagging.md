# Email Tagging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add IMAP tagging functionality to email-fetch-latest skill, enabling external processes to assign tags that get applied via IMAP STORE commands.

**Architecture:** Modify fetch script to output tag definitions; create new script to apply tags from assignment file using IMAP keywords (RFC 3501).

**Tech Stack:** Python 3.11+, imaplib (stdlib), existing EmailClient class

---

### Task 1: Modify fetch_latest_emails.py to output tag definitions

**Files:**
- Modify: `skills/email-fetch-latest/scripts/fetch_latest_emails.py`
- Modify: `skills/email-fetch-latest/SKILL.md`

**Step 1: Add --tags-config argument**

Add new argument to argument parser (around line 373):

```python
parser.add_argument(
    "--tags-config",
    type=str,
    default=None,
    help="标签配置文件路径，用于输出标签定义到输出目录",
)
```

**Step 2: Add function to copy tag definitions to output directory**

Add after `save_last_uids` function (around line 275):

```python
def copy_tag_definitions(tags_config_path: Optional[str], output_dir: Path):
    """复制标签定义到输出目录"""
    if not tags_config_path:
        return
    
    tags_path = Path(tags_config_path)
    if not tags_path.exists():
        print(f"  ⚠ 标签配置文件不存在：{tags_path}")
        return
    
    output_file = output_dir / "tag_definitions.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_data = json.load(f)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 已输出标签定义到 {output_file}")
```

**Step 3: Call copy_tag_definitions in main function**

Add after line 412 (after creating output_dir):

```python
# 复制标签定义
copy_tag_definitions(args.tags_config, output_dir)
```

**Step 4: Commit**

```bash
git add skills/email-fetch-latest/scripts/fetch_latest_emails.py
git commit -m "feat: add --tags-config argument to output tag definitions"
```

---

### Task 2: Create apply_email_tags.py script

**Files:**
- Create: `skills/email-fetch-latest/scripts/apply_email_tags.py`

**Step 1: Create the script with complete implementation**

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Apply Email Tags

根据标签分配文件，通过 IMAP 为邮件打标签。

Usage:
    ./skills/email-fetch-latest/scripts/apply_email_tags.py \
        --config data/config.json \
        --assignments assets/emails/tag_assignments.json
"""

import argparse
import imaplib
import json
from pathlib import Path
from typing import List, Dict, Optional
import textwrap


class ImapTagger:
    """IMAP 邮件标签器"""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """连接到 IMAP 服务器"""
        try:
            self.client = imaplib.IMAP4_SSL(self.host, self.port)
            self.client.login(self.username, self.password)
            print(f"✓ 已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ 连接失败：{e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.client:
            try:
                self.client.close()
                self.client.logout()
                print("✓ 已断开连接")
            except Exception as e:
                print(f"✗ 断开连接失败：{e}")
            finally:
                self.client = None

    def apply_tags(self, uid: str, folder: str, tags: List[str]) -> bool:
        """为指定邮件应用标签
        
        Args:
            uid: 邮件 UID
            folder: 邮件所在文件夹
            tags: 要应用的标签列表
            
        Returns:
            是否成功
        """
        if not self.client:
            print("✗ 未连接到服务器")
            return False
        
        try:
            # 选择文件夹
            status, _ = self.client.select(folder)
            if status != "OK":
                print(f"  ✗ 无法选择文件夹 {folder}")
                return False
            
            # 将标签转换为 IMAP flags (使用自定义关键字)
            # IMAP 关键字不能包含空格和特殊字符
            flags = [tag.upper().replace("-", "_") for tag in tags]
            
            # 使用 STORE 命令添加标签
            for flag in flags:
                status, response = self.client.store(uid, "+FLAGS", flag)
                if status != "OK":
                    print(f"  ⚠ 标签 {flag} 可能未应用成功")
            
            print(f"  ✓ UID {uid} 已应用标签: {', '.join(tags)}")
            return True
            
        except Exception as e:
            print(f"  ✗ 应用标签失败 (UID: {uid}): {e}")
            return False


def load_assignments(assignments_path: Path) -> List[Dict]:
    """加载标签分配文件"""
    if not assignments_path.exists():
        print(f"✗ 标签分配文件不存在：{assignments_path}")
        return []
    
    with open(assignments_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("assignments", [])


def main():
    parser = argparse.ArgumentParser(
        description="通过 IMAP 为邮件应用标签",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            示例:
                ./skills/email-fetch-latest/scripts/apply_email_tags.py \
                    --config data/config.json \
                    --assignments assets/emails/tag_assignments.json
        """),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="data/config.json",
        help="IMAP 配置文件路径 (默认：data/config.json)",
    )

    parser.add_argument(
        "-a",
        "--assignments",
        type=str,
        required=True,
        help="标签分配 JSON 文件路径",
    )

    args = parser.parse_args()

    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"✗ 配置文件不存在：{config_path}")
        return 1

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    mail_config = config.get("mail", {})
    if not mail_config:
        print("✗ 配置文件中缺少 mail 配置")
        return 1

    # 加载标签分配
    assignments_path = Path(args.assignments)
    assignments = load_assignments(assignments_path)
    if not assignments:
        print("✗ 没有找到标签分配")
        return 1

    print(f"\n标签分配文件：{assignments_path}")
    print(f"待处理邮件数：{len(assignments)}\n")

    # 创建标签器并连接
    tagger = ImapTagger(
        host=mail_config.get("imapServer", ""),
        port=mail_config.get("imapPort", 993),
        username=mail_config.get("emailAddress", ""),
        password=mail_config.get("emailPassword", ""),
    )

    if not tagger.connect():
        return 1

    try:
        success_count = 0
        fail_count = 0

        for assignment in assignments:
            uid = assignment.get("uid")
            folder = assignment.get("folder", "INBOX")
            tags = assignment.get("tags", [])

            if not uid or not tags:
                print(f"  ⚠ 跳过无效分配：{assignment}")
                continue

            if tagger.apply_tags(str(uid), folder, tags):
                success_count += 1
            else:
                fail_count += 1

        print(f"\n✓ 完成：成功 {success_count}，失败 {fail_count}")

    finally:
        tagger.disconnect()

    return 0


if __name__ == "__main__":
    exit(main())
```

**Step 2: Commit**

```bash
git add skills/email-fetch-latest/scripts/apply_email_tags.py
git commit -m "feat: add apply_email_tags.py script for IMAP tagging"
```

---

### Task 3: Update SKILL.md documentation

**Files:**
- Modify: `skills/email-fetch-latest/SKILL.md`

**Step 1: Add tagging section to SKILL.md**

Add after line 177 (after `--last-uid-file` parameter table):

```markdown
## 标签功能

### 标签配置文件

标签定义存储在外部 JSON 文件中：

```json
{
  "tags": [
    {
      "name": "invoice",
      "description": "客户账单、发票相关邮件"
    },
    {
      "name": "urgent",
      "description": "紧急、需要立即处理的邮件"
    }
  ]
}
```

### 标签分配文件

外部流程（如 LLM）分析邮件后创建标签分配文件：

```json
{
  "assignments": [
    {"uid": "12345", "folder": "INBOX", "tags": ["invoice", "urgent"]},
    {"uid": "12346", "folder": "INBOX", "tags": ["invoice"]}
  ]
}
```

### 应用标签

使用 `apply_email_tags.py` 脚本应用标签：

```bash
# 应用标签
./skills/email-fetch-latest/scripts/apply_email_tags.py \
  --config data/config.json \
  --assignments assets/emails/tag_assignments.json
```

### 完整工作流

```bash
# 1. 收取邮件（同时输出标签定义）
./skills/email-fetch-latest/scripts/fetch_latest_emails.py \
  --config data/config.json \
  --tags-config data/tags.json \
  --output assets/emails

# 2. 外部流程（LLM）分析邮件，生成 tag_assignments.json

# 3. 应用标签
./skills/email-fetch-latest/scripts/apply_email_tags.py \
  --config data/config.json \
  --assignments assets/emails/tag_assignments.json
```
```

**Step 2: Update directory structure section**

Replace lines 29-43 with:

```markdown
## 目录结构

```
skills/email-fetch-latest/
├── SKILL.md                          # 本文档
├── scripts/
│   ├── fetch_latest_emails.py        # 邮件收取脚本
│   └── apply_email_tags.py           # 标签应用脚本
└── assets/
    └── emails/                       # 邮件 JSON 存储目录
        ├── INBOX/
        │   ├── 12345.json
        │   └── index.json
        ├── tag_definitions.json      # 标签定义（可选）
        └── tag_assignments.json      # 标签分配（外部生成）
```
```

**Step 3: Commit**

```bash
git add skills/email-fetch-latest/SKILL.md
git commit -m "docs: update SKILL.md with tagging functionality"
```

---

### Task 4: Create test file

**Files:**
- Create: `skills/email-fetch-latest/test_skill.py`

**Step 1: Create test file**

```python
#!/usr/bin/env python3
"""
Test script for email-fetch-latest skill

Run with: python skills/email-fetch-latest/test_skill.py
"""

import json
import sys
from pathlib import Path


def test_tag_config_format():
    """测试标签配置文件格式"""
    tags_config = {
        "tags": [
            {"name": "invoice", "description": "发票相关"},
            {"name": "urgent", "description": "紧急邮件"},
        ]
    }
    
    assert "tags" in tags_config
    assert isinstance(tags_config["tags"], list)
    for tag in tags_config["tags"]:
        assert "name" in tag
        assert "description" in tag
    print("✓ 标签配置格式测试通过")


def test_tag_assignments_format():
    """测试标签分配文件格式"""
    assignments = {
        "assignments": [
            {"uid": "12345", "folder": "INBOX", "tags": ["invoice"]},
            {"uid": "12346", "folder": "INBOX", "tags": ["urgent", "invoice"]},
        ]
    }
    
    assert "assignments" in assignments
    assert isinstance(assignments["assignments"], list)
    for assignment in assignments["assignments"]:
        assert "uid" in assignment
        assert "folder" in assignment
        assert "tags" in assignment
        assert isinstance(assignment["tags"], list)
    print("✓ 标签分配格式测试通过")


def test_scripts_exist():
    """测试脚本文件存在"""
    scripts_dir = Path(__file__).parent / "scripts"
    
    fetch_script = scripts_dir / "fetch_latest_emails.py"
    assert fetch_script.exists(), f"Missing: {fetch_script}"
    
    tag_script = scripts_dir / "apply_email_tags.py"
    assert tag_script.exists(), f"Missing: {tag_script}"
    
    print("✓ 脚本文件存在测试通过")


def main():
    print("Running email-fetch-latest skill tests...\n")
    
    tests = [
        test_scripts_exist,
        test_tag_config_format,
        test_tag_assignments_format,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 错误: {e}")
            failed += 1
    
    print(f"\n{'='*40}")
    if failed:
        print(f"测试失败: {failed}")
        return 1
    print("所有测试通过!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Run test to verify scripts exist**

```bash
python skills/email-fetch-latest/test_skill.py
```

Expected: Tests pass (scripts exist, format validation works)

**Step 3: Commit**

```bash
git add skills/email-fetch-latest/test_skill.py
git commit -m "test: add test_skill.py for email-fetch-latest"
```

---

### Task 5: Final verification

**Step 1: Run full test suite**

```bash
python skills/email-fetch-latest/test_skill.py
```

Expected: All tests pass

**Step 2: Verify script help output**

```bash
./skills/email-fetch-latest/scripts/apply_email_tags.py --help
```

Expected: Shows usage information

**Step 3: Final commit**

```bash
git status
# If any uncommitted changes:
git add -A
git commit -m "feat: complete email tagging feature"
```