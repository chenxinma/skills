#!/usr/bin/env python3
"""
邮件批量发送工具 - 指标填报专用

此脚本按照指标填报_mail_template.json格式处理邮件模板，
每个模板条目包含：内容、附件、部门、收件人、主题。
"""

import json
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
import smtplib
import argparse
import filetype
from typing import List, Dict, Any, Optional


def parse_receivers(receivers_str: str) -> List[str]:
    """解析收件人字符串为邮箱地址列表"""
    try:
        receivers = json.loads(receivers_str)
        if isinstance(receivers, list):
            email_list = []
            for receiver in receivers:
                if isinstance(receiver, str):
                    if "<" in receiver and ">" in receiver:
                        email = receiver.split("<")[1].split(">")[0].strip()
                    else:
                        email = receiver.strip()
                    email_list.append(email)
            return email_list
    except json.JSONDecodeError as e:
        print(f"解析收件人失败: {e}, 输入: {receivers_str}")
    return []


def replace_placeholders(content: str, placeholders: Dict[str, Any]) -> str:
    """替换模板中的{{key}}为实际数据"""
    result = content
    for key, value in placeholders.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


class EmailSender:
    """邮件发送器"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def _get_smtp_connection(self):
        """获取SMTP连接"""
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        return server

    def send_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
    ):
        """发送邮件"""
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # 添加附件（如果有）
        if attachment_path and os.path.isfile(attachment_path):
            file_name = os.path.basename(attachment_path)
            # 检测文件类型
            kind = filetype.guess(attachment_path)
            if kind:
                maintype, subtype = kind.mime.split('/')
                with open(attachment_path, 'rb') as file:
                    part = MIMEBase(maintype, subtype, name=file_name)
                    part.set_payload(file.read())
                # 对附件进行编码
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=Header(file_name, 'utf-8').encode())
            else:
                # 如果无法检测到文件类型，使用默认的 MIMEApplication
                with open(attachment_path, "rb") as file:
                    part = MIMEApplication(file.read(), name=file_name)
                part['Content-Disposition'] = f'attachment; filename="{Header(file_name, "utf-8").encode()}"'
            msg.attach(part)


        server = self._get_smtp_connection()
        text = msg.as_string()
        server.sendmail(self.username, recipients, text)
        server.quit()


def batch_send_emails(
    template_file: str,
    smtp_config: Dict,
    placeholders: Optional[Dict[str, Any]] = None,
):
    """
    批量发送邮件主方法

    :param template_file: 指标填报模板JSON文件路径
    :param smtp_config: SMTP服务器配置
    :param placeholders: 占位符替换值字典
    """

    if placeholders is None:
        placeholders = {}

    with open(template_file, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    sender = EmailSender(
        smtp_config["server"],
        smtp_config["port"],
        smtp_config["username"],
        smtp_config["password"],
    )

    for template_item in template_data:
        content = template_item.get("content", "")
        subject = template_item.get("subject", "默认主题")
        attachment = template_item.get("attachment", "")
        receivers_str = template_item.get("receivers", "[]")

        rendered_content = replace_placeholders(content, placeholders)
        recipients = parse_receivers(receivers_str)

        if recipients:
            sender.send_email(
                recipients,
                subject,
                rendered_content,
                attachment if attachment else None,
            )
            print(f"邮件已发送至: {', '.join(recipients)}")
        else:
            print(
                f"跳过: 未解析到有效收件人, 部门: {template_item.get('department', '未知')}"
            )


def parse_arguments():
    parser = argparse.ArgumentParser(description="批量发送指标填报邮件")
    parser.add_argument("--template", required=True, help="指标填报模板JSON文件路径")
    parser.add_argument(
        "--smtp-config", required=True, help="SMTP服务器配置JSON文件路径"
    )
    parser.add_argument(
        "--placeholders",
        help='占位符替换值JSON字符串，例如: \'{"current_ym": "2024年10月", "deadline": "2024-10-31"}\'',
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    with open(args.smtp_config, "r", encoding="utf-8") as f:
        smtp_config = json.load(f)

    placeholders = {}
    if args.placeholders:
        try:
            placeholders = json.loads(args.placeholders)
        except json.JSONDecodeError as e:
            print(f"解析占位符失败: {e}")

    batch_send_emails(args.template, smtp_config, placeholders)


if __name__ == "__main__":
    main()
