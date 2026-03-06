# AGENTS.md - Development Guidelines

This file provides guidelines for agentic coding agents working in this repository.

## Project Overview

Repository contains AI assistant skills for opencode, Claude Code, and OpenClaw. Each skill is a self-contained module with scripts, documentation, and tests.

## Repository Structure

```
skills/
├── README.md                 # Main documentation
├── AGENTS.md                 # This file
└── skills/
    ├── email-assistant/      # Email API interaction
    ├── email-templater/      # Batch email templating
    └── etf-grid-trading/     # Grid trading optimization
```

## Build & Test Commands

### Running Tests
```bash
# Run a specific test file
python skills/email-templater/test_skill.py

# Validate and package a skill
python skills/email-templater/package_skill.py
```

### Running Scripts
```bash
# Email templater - render template (preview)
python skills/email-templater/scripts/render_template.py \
  --template path/to/template.json \
  --placeholders '{"current_ym": "2024 年 10 月", "deadline": "2024-10-31"}'

# Email templater - send batch emails
python skills/email-templater/scripts/send_batch_emails.py \
  --template path/to/template.json \
  --smtp-config path/to/smtp_config.json

# Email assistant - query/refresh
python skills/email-assistant/scripts/email_client.py query "今天收到的邮件"
python skills/email-assistant/scripts/email_client.py refresh 7
```

### Dependencies
```bash
pip install httpx requests filetype
# Or with uv
uv add httpx requests filetype
```

## Code Style Guidelines

### Imports
Order: standard library → third-party → local imports, with blank lines between groups.

```python
#!/usr/bin/env python3
"""Module docstring."""

# Standard library
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Third-party
import httpx
```

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters
- **Blank lines**: 2 between top-level functions, 1 between methods and logical sections

### Type Hints
Use type hints for all function parameters and return values:

```python
from typing import List, Dict, Any, Optional

def parse_receivers(receivers_str: str) -> List[str]:
    """Parse receiver string to email list."""
    ...

def send_email(
    self,
    recipients: List[str],
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> None:
    """Send an email."""
    ...
```

### Naming Conventions
- **Functions/Methods**: `snake_case` - `parse_receivers`, `batch_send_emails`
- **Variables**: `snake_case` - `template_data`, `smtp_config`
- **Classes**: `PascalCase` - `EmailSender`, `GridTradingOptimizer`
- **Constants**: `UPPER_CASE` - `BASE_URL`, `DEFAULT_DAYS`
- **Private methods**: Leading underscore - `_get_smtp_connection`

### Docstrings
Use Google-style docstrings:

```python
def batch_send_emails(
    template_file: str,
    smtp_config: Dict,
    placeholders: Optional[Dict[str, Any]] = None,
):
    """
    批量发送邮件主方法

    :param template_file: 指标填报模板 JSON 文件路径
    :param smtp_config: SMTP 服务器配置
    :param placeholders: 占位符替换值字典
    """
```

Include module-level docstrings in all scripts.

### Error Handling
```python
try:
    receivers = json.loads(receivers_str)
    if isinstance(receivers, list):
        return receivers
except json.JSONDecodeError as e:
    print(f"解析收件人失败：{e}, 输入：{receivers_str}")
    return []
```

Guidelines:
- Catch specific exceptions, not bare `except`
- Include context in error messages
- Return sensible defaults when appropriate

### Script Entry Points
All executable scripts must include shebang, module docstring, and `if __name__ == "__main__"` guard.

## Linting & Quality

No formal linting configuration. Follow these:

- Run `python -m py_compile <file>.py` to check syntax
- Avoid unused imports
- Keep functions focused and under 50 lines when possible
- Use descriptive variable names (no single letters except loop counters)

## Skill Structure Requirements

Each skill directory must contain:
- `SKILL.md` - Skill definition with metadata (required)
- `scripts/` - Python scripts for functionality
- `references/` - Reference documentation (optional)
- `test_skill.py` - Basic tests (recommended)
- `package_skill.py` - Validation/packaging (recommended)

## Working with Skills

1. **Understand the skill's purpose** by reading `SKILL.md`
2. **Follow existing patterns** in the skill's scripts
3. **Test changes** with the skill's test script
4. **Update documentation** if behavior changes
5. **Validate structure** using `package_skill.py`

## Environment Notes

- Python 3.7+ compatibility required
- Use `uv` or `pip` as preferred
- Scripts should work standalone without project-level dependencies
- All paths should use `pathlib.Path` for cross-platform compatibility
