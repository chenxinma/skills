#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""邮件模板渲染器 - 指标填报专用。"""

import argparse
import json
from typing import Any, Dict


def replace_placeholders(content: str, placeholders: Dict[str, Any]) -> str:
    """替换模板中的{{key}}为实际数据"""
    result = content
    for key, value in placeholders.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def parse_receivers(receivers_str: str) -> str:
    """解析收件人字符串为可读格式"""
    try:
        receivers = json.loads(receivers_str)
        if isinstance(receivers, list):
            return ", ".join(receivers)
    except json.JSONDecodeError:
        pass
    return receivers_str


def render_template(template_file: str, placeholders: Dict[str, Any]) -> None:
    """
    渲染指标填报模板，打印每条模板的渲染结果

    :param template_file: 指标填报模板JSON文件路径
    :param placeholders: 占位符替换值字典
    """

    with open(template_file, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    for idx, template_item in enumerate(template_data, 1):
        content = template_item.get("content", "")
        subject = template_item.get("subject", "默认主题")
        department = template_item.get("department", "未知部门")
        receivers_str = template_item.get("receivers", "[]")
        attachment = template_item.get("attachment", "")

        rendered_content = replace_placeholders(content, placeholders)
        receivers_display = parse_receivers(receivers_str)

        print(f"{'=' * 60}")
        print(f"模板 #{idx}")
        print(f"部门: {department}")
        print(f"主题: {subject}")
        print(f"收件人: {receivers_display}")
        print(f"附件: {attachment}")
        print(f"{'=' * 60}")
        print("渲染后的内容:")
        print(rendered_content)
        print()


def parse_arguments():
    parser = argparse.ArgumentParser(description="邮件模板渲染器（指标填报专用）")
    parser.add_argument("--template", required=True, help="指标填报模板JSON文件路径")
    parser.add_argument(
        "--placeholders",
        required=True,
        help='占位符替换值JSON字符串，例如: \'{"current_ym": "2024年10月", "deadline": "2024-10-31"}\'',
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    placeholders = {}
    try:
        placeholders = json.loads(args.placeholders)
    except json.JSONDecodeError as e:
        print(f"解析占位符失败: {e}")
        return

    render_template(args.template, placeholders)


if __name__ == "__main__":
    main()
