---
name: email-templater
description: 按mail_template.json格式的邮件模板批量发送技能，支持{{占位符}}动态替换和按部门/收件人发送邮件，每个收件人对应固定附件。适用于指标填报、数据提报等场景。
---

# Email Templater

## Overview

这个技能按照`mail_template.json`格式处理邮件模板，每个模板条目包含：邮件内容、附件路径、部门名称、收件人列表、邮件主题。系统自动解析模板并发送邮件。

## 能力说明

### 1. 模板格式
- 支持`内容(content)`、`附件(attachment)`、`部门(department)`、`收件人(receivers)`、`主题(subject)`完整字段
- 使用 {{variable_name}} 语法定义动态占位符（如{{current_ym}}、{{deadline}}）
- 每个模板条目包含固定的附件文件路径

### 2. 收件人处理
- 支持单个或多个收件人
- 支持带姓名的邮箱格式："'姓名' <email@example.com>"
- 支持纯邮箱格式："email@example.com"
- 自动解析并标准化收件人地址

### 3. 附件管理
- 每个模板条目对应一个附件文件
- 附件路径可以是绝对路径或相对于当前工作目录
- 支持多种文件格式（Excel/PDF/文档等）

### 4. 实际应用场景
- 东兰大数据平台指标填报通知
- 跨部门数据提报 requests
- 周期性指标数据收集
- 部门个性化邮件通知

## 使用流程

### 步骤 1：准备模板 JSON
```json
[
  {
    "content": "\nabc，您好\n\n需要向上级呈报{{current_ym}}以来的相关指标数据，详见附件\n如果有发生，请在{{deadline}}完成填报并反馈给我，谢谢\n\n以上\n",
    "attachment": "path/to/attachment1.xlsx",
    "department": "战略投资部",
    "receivers": "[\"abc.dd@example.com\"]",
    "subject": "示例邮件标题1"
  },
  {
    "content": "\ncc师，您好\n\n需要向上级呈报相关指标数据，详见附件\n{{current_ym}}数据请在{{deadline}}完成填报并反馈给我，谢谢\n\n以上\n",
    "attachment": "path/to/attachment1.xlsx",
    "department": "计划财务部",
    "receivers": "[\"cc@example.com\", \"ee@example.com\"]",
    "subject": "示例邮件标题2"
  }
]
```

### 步骤 2：配置SMTP服务器 (JSON格式)
```json
{
  "server": "smtp.gmail.com",
  "port": 587,
  "username": "your-email@gmail.com",
  "password": "your-app-password"
}
```

### 步骤 3：执行批量发送
```bash
./skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/mail_template.json \
  --smtp-config path/to/smtp_config.json
```

## 技术注意事项

- 收件人字段`receivers`是JSON格式的字符串，包含一个收件人地址列表
- 支持带姓名的邮箱格式和纯邮箱格式
- 附件路径可以是绝对路径或相对于当前工作目录
- 模板中使用 {{variable_name}} 语法定义占位符，需在运行时提供替换值

## 工具脚本

脚本调用方式（必须直接执行，不要用 `uv run python` 或 `python`）：
```bash
./skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/mail_template.json \
  --smtp-config path/to/smtp_config.json \
  --placeholders '...'
```
错误示例：
```bash
uv run python ./skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/mail_template.json \
  --smtp-config path/to/smtp_config.json \
  --placeholders '...'
python ./skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/mail_template.json \
  --smtp-config path/to/smtp_config.json \
  --placeholders '...'
```

### 主批量发送脚本
执行邮件批量发送：
```bash
./skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/mail_template.json \
  --smtp-config path/to/smtp_config.json \
  --placeholders '{"current_ym": "2024 年 10 月", "deadline": "2024-10-31"}'
```

### 模板渲染工具
单独渲染邮件模板，不发送邮件：
```bash
./skills/email-templater/scripts/render_template.py \
  --template path/to/mail_template.json \
  --placeholders '{"current_ym": "2024 年 10 月", "deadline": "2024-10-31"}'
```

## 资源说明

### scripts/
- `send_batch_emails.py`: 主程序，根据指标填报模板发送邮件（依赖自动管理，无需手动安装）
- `render_template.py`: 邮件模板中占位符替换工具（预览用）

### assets/
可存放示例模板文件或参考文档

### references/
可存放邮件服务特殊配置文档或安全使用指南