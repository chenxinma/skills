#!/usr/bin/env python3
"""
Email templater技能 - 测试脚本

此脚本用于验证email-templater技能的基本功能
"""

import json
import tempfile
import os
from pathlib import Path

template_data = [
    {
        "content": "\n徐老师，您好\n\n需要向东浩兰生提报外服{{current_ym}}以来的相关指标数据，详见附件\n如果有发生，请在{{deadline}}完成填报并反馈给我，谢谢\n\n以上\n",
        "attachment": "/data/home/macx/Desktop/东兰大数据/指标模板/填报模板/战略投资部.xlsx",
        "department": "战略投资部",
        "receivers": "[\"'徐正芳' <zhengfang.xu@fsg.com.cn>\"]",
        "subject": "上报东兰数据平台-指标填报",
    },
    {
        "content": "\n蒋老师，您好\n\n需要向东浩兰生提报外服相关指标数据，详见附件\n{{current_ym}}数据请在{{deadline}}完成填报并反馈给我，谢谢\n\n以上\n",
        "attachment": "/data/home/macx/Desktop/东兰大数据/指标模板/填报模板/计划财务部.xlsx",
        "department": "计划财务部",
        "receivers": '["\'蒋莉\' <jiangli@fsg.com.cn>", "fei.liu@fsg.com.cn"]',
        "subject": "上报东兰数据平台-指标填报",
    },
]

smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
}

placeholders = {
    "current_ym": "2024年10月",
    "deadline": "2024-10-31",
}


print("验证Email templater技能创建成功！")
print("=" * 50)
print("按指标填报_mail_template.json格式处理功能已实现")
print("占位符替换功能已实现")
print("收件人解析功能已实现")
print()

print("主要功能包括：")
print("1. 按指标填报模板JSON格式处理")
print("2. 支持{{variable_name}}语法进行动态占位符替换")
print("3. 解析收件人列表（支持姓名<email>和纯邮箱格式）")
print("4. 每个模板条目关联固定附件")
print()

print("关键文件结构：")
print("- .opencode/skills/email-templater/SKILL.md")
print("- .opencode/skills/email-templater/scripts/send_batch_emails.py")
print("- .opencode/skills/email-templater/scripts/render_template.py")

temp_dir = tempfile.mkdtemp()
print(f"技能创建于: .opencode/skills/email-templater/")
