#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4>=4.13.4",
# ]
# ///
"""
Fetch Latest Emails

独立脚本，包含完整的 IMAP 实现，收取最新邮件并保存为 JSON 格式。

Usage:
    python fetch_latest_emails.py --config data/config.json --days 3 --output assets/emails
"""

import argparse
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
import email
import imaplib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
import textwrap
from bs4 import BeautifulSoup


@dataclass
class Email:
    """邮件数据类"""

    uid: str
    subject: str
    sender: str
    recipient: str
    date: str
    content: str
    folder: str


class EmailClient:
    """IMAP 邮件客户端"""

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

    def list_folders(self) -> List[str]:
        """获取所有文件夹"""
        if self.client:
            try:
                status, folders = self.client.list()
                if status == "OK" and folders:
                    folder_list = []
                    for folder in folders:
                        if isinstance(folder, bytes):
                            folder_name = folder.decode().split(' "/" ')[-1]
                            folder_list.append(folder_name)
                    return folder_list
            except Exception as e:
                print(f"✗ 获取文件夹失败：{e}")
        return []

    def _decode_text(self, text: str) -> str:
        """解码邮件主题或正文"""
        if not text:
            return ""

        decoded_parts = decode_header(text)
        decoded_text = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_text += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_text += part

        return decoded_text

    def _decode_header(self, encoded: str) -> str:
        """解码邮件头"""
        if "=?" in encoded:
            decoded_parts = decode_header(encoded)
            decoded_texts = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_texts.append(
                        part.decode(encoding or "utf-8", errors="ignore")
                    )
                else:
                    decoded_texts.append(part)
            return "".join(decoded_texts)
        return encoded

    def _get_email_content(self, msg: Message) -> str:
        """获取邮件正文内容"""
        content = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == "text/plain":
                    encoding = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    if payload and isinstance(payload, bytes):
                        content = payload.decode(encoding, errors="ignore")
                        break

                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload and isinstance(payload, bytes):
                        html = payload.decode("utf-8", errors="ignore")
                        soup = BeautifulSoup(html, "html.parser")
                        content = soup.get_text()

                elif content_type == "BEGIN:VCALENDAR":
                    payload = part.get_payload(decode=True)
                    if payload and isinstance(payload, bytes):
                        content = payload.decode("utf-8", errors="ignore")
        else:
            encoding = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload and isinstance(payload, bytes):
                content = payload.decode(encoding, errors="ignore")

        # 清理内容
        if content and not content.startswith("BEGIN:VCALENDAR"):
            dedented_text = textwrap.dedent(content).strip()
            lines = [
                line
                for line in dedented_text.splitlines()
                if line.strip()
                and not line.startswith("发件人：")
                and not line.startswith("收件人：")
                and not line.startswith("抄送：")
            ]
            content = "\n".join(lines)

        return content

    def _parse_email(self, email_id: int) -> Optional[Email]:
        """解析单个邮件"""
        if not self.client:
            return None

        try:
            status, msg_data = self.client.fetch(str(email_id), "(RFC822)")  # type: ignore
            if status != "OK" or not msg_data or not msg_data[0]:
                return None

            raw_email = msg_data[0][1]  # type: ignore
            msg = email.message_from_bytes(raw_email)  # type: ignore

            # 解码主题
            subject = self._decode_text(msg.get("subject", ""))

            # 获取发件人和收件人
            sender = self._decode_header(msg.get("From", ""))
            recipient = self._decode_header(msg.get("To", ""))

            # 获取日期
            date_str = msg.get("Date", "")
            try:
                date_obj = parsedate_to_datetime(date_str)
                date = date_obj.isoformat()
            except Exception:
                date = datetime.now().isoformat()

            # 获取正文
            content = self._get_email_content(msg)
            if not content.strip():
                return None

            return Email(
                uid=str(email_id),
                subject=subject,
                sender=sender,
                recipient=recipient,
                date=date,
                content=content,
                folder="",
            )

        except Exception as e:
            print(f"✗ 解析邮件失败 (ID: {email_id}): {e}")
            return None

    def fetch_emails(
        self, folder: str = "INBOX", days: int = 3, last_uid: int = 0
    ) -> List[Email]:
        """获取指定文件夹的邮件"""
        if not self.client:
            raise Exception("未连接到邮件服务器")

        # 选择文件夹
        self.client.select(folder)

        # 计算日期范围
        date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        search_criteria = f"(SINCE {date})"

        # 搜索邮件
        status, messages = self.client.search(None, search_criteria)
        if status != "OK":
            raise Exception("搜索邮件失败")

        email_ids = messages[0].split()  # type: ignore

        # 过滤已处理的邮件
        if last_uid > 0:
            email_ids = [eid for eid in email_ids if int(eid) > last_uid]

        if not email_ids:
            print(f"  ℹ 文件夹 {folder} 没有新邮件")
            return []

        print(f"  ℹ 文件夹 {folder} 发现 {len(email_ids)} 封新邮件")

        # 获取邮件内容
        emails = []
        for email_id in email_ids:
            email_obj = self._parse_email(int(email_id))
            if email_obj:
                email_obj.folder = folder
                emails.append(email_obj)
                print(f"  ✓ {email_obj.subject[:50]}...")

        return emails


def load_last_uids(last_uid_file: Path) -> Dict[str, int]:
    """读取最后 UID 记录"""
    if last_uid_file.exists():
        with open(last_uid_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last_uids(last_uids: Dict[str, int], last_uid_file: Path):
    """保存最后 UID 记录"""
    last_uid_file.parent.mkdir(parents=True, exist_ok=True)
    with open(last_uid_file, "w", encoding="utf-8") as f:
        json.dump(last_uids, f, indent=2, ensure_ascii=False)


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


def save_emails_to_json(emails: List[Email], output_dir: Path, folder: str):
    """保存邮件到 JSON 文件"""
    output_dir.mkdir(parents=True, exist_ok=True)

    fetched_at = datetime.now().isoformat()
    email_summaries = []
    max_uid = 0

    for email_obj in emails:
        email_data = asdict(email_obj)
        email_data["fetched_at"] = fetched_at

        # 保存单个邮件
        email_file = output_dir / f"{email_obj.uid}.json"
        with open(email_file, "w", encoding="utf-8") as f:
            json.dump(email_data, f, ensure_ascii=False, indent=2)

        # 收集摘要信息
        email_summaries.append(
            {
                "uid": email_obj.uid,
                "subject": email_obj.subject,
                "sender": email_obj.sender,
                "date": email_obj.date,
            }
        )

        # 更新最大 UID
        try:
            uid_int = int(email_obj.uid)
            if uid_int > max_uid:
                max_uid = uid_int
        except ValueError:
            pass

    # 保存索引文件
    index_data = {
        "folder": folder,
        "last_uid": max_uid,
        "fetched_at": fetched_at,
        "email_count": len(emails),
        "emails": email_summaries,
    }

    index_file = output_dir / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 已保存 {len(emails)} 封邮件到 {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="收取最新邮件并保存为 JSON 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            示例:
                python fetch_latest_emails.py --config data/config.json
                python fetch_latest_emails.py --config data/config.json --days 7
                python fetch_latest_emails.py --config data/config.json --output assets/my-emails
        """),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="data/config.json",
        help="配置文件路径 (默认：data/config.json)",
    )

    parser.add_argument(
        "-d", "--days", type=int, default=2, help="收取最近 N 天的邮件 (默认：2)"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="assets/emails",
        help="输出目录 (默认：assets/emails)",
    )

    parser.add_argument(
        "-f",
        "--folders",
        type=str,
        default=None,
        help="要收取的文件夹，逗号分隔 (默认：使用配置文件中的 indexedFolders)",
    )

    parser.add_argument(
        "--last-uid-file",
        type=str,
        default=None,
        help="最后 UID 记录文件 (默认：{output}/last_uid.json)",
    )

    parser.add_argument(
        "--tags-config",
        type=str,
        default=None,
        help="标签配置文件路径，用于输出标签定义到输出目录",
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

    # 创建客户端
    client = EmailClient(
        host=mail_config.get("imapServer", ""),
        port=mail_config.get("imapPort", 993),
        username=mail_config.get("emailAddress", ""),
        password=mail_config.get("emailPassword", ""),
    )

    # 连接
    if not client.connect():
        return 1

    try:
        # 确定要处理的文件夹
        if args.folders:
            folders = [f.strip() for f in args.folders.split(",")]
        else:
            folders = mail_config.get("indexedFolders", ["INBOX"])

        # 输出目录
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 复制标签定义
        copy_tag_definitions(args.tags_config, output_dir)

        # 最后 UID 文件
        last_uid_file = (
            Path(args.last_uid_file)
            if args.last_uid_file
            else output_dir / "last_uid.json"
        )
        last_uids = load_last_uids(last_uid_file)

        print(f"\n开始收取邮件...")
        print(f"  配置文件：{config_path}")
        print(f"  输出目录：{output_dir}")
        print(f"  收取天数：{args.days} 天")
        print(f"  文件夹：{', '.join(folders)}\n")

        total_emails = 0

        for folder in folders:
            print(f"处理文件夹：{folder}")

            # 获取最后 UID
            last_uid = last_uids.get(folder, 0)
            if last_uid > 0:
                print(f"  ℹ 最后 UID: {last_uid}")

            # 获取邮件
            emails = client.fetch_emails(
                folder=folder, days=args.days, last_uid=last_uid
            )

            if emails:
                # 保存邮件
                folder_output_dir = output_dir / folder
                save_emails_to_json(emails, folder_output_dir, folder)

                # 更新最后 UID
                max_uid = max(int(e.uid) for e in emails if e.uid.isdigit())
                last_uids[folder] = max_uid
                total_emails += len(emails)

        # 保存最后 UID
        save_last_uids(last_uids, last_uid_file)

        print(f"\n✓ 完成，共收取 {total_emails} 封新邮件")

    finally:
        client.disconnect()

    return 0


if __name__ == "__main__":
    exit(main())
