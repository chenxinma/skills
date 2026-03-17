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
