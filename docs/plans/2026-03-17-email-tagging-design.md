# Email Tagging Feature Design

## Overview

Add IMAP tagging functionality to the `email-fetch-latest` skill. After fetching emails, an external process (e.g., LLM) can assign tags, and a new script applies those tags via IMAP.

## Components

### 1. Tag Configuration File (`data/tags.json`)

Defines available tags and their descriptions for LLM reference:

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

### 2. Enhanced Fetch Output

The existing `fetch_latest_emails.py` script outputs:
- Email JSON files (current behavior, unchanged)
- `tag_definitions.json` - copy of tag config for reference in the output directory

### 3. Tag Assignment File (`assets/emails/tag_assignments.json`)

External process/LLM creates this file after analyzing emails:

```json
{
  "assignments": [
    {"uid": "12345", "folder": "INBOX", "tags": ["invoice", "urgent"]},
    {"uid": "12346", "folder": "INBOX", "tags": ["invoice"]}
  ]
}
```

### 4. New Script: `apply_email_tags.py`

Applies tags via IMAP STORE command:

```bash
./skills/email-fetch-latest/scripts/apply_email_tags.py \
  --config data/config.json \
  --assignments assets/emails/tag_assignments.json
```

#### Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--config` | `-c` | IMAP config file path | `data/config.json` |
| `--assignments` | `-a` | Tag assignments JSON file | Required |

#### Implementation Details

- Uses IMAP `STORE` command with `+FLAGS` to add keywords
- Supports generic IMAP servers (RFC 3501 keywords)
- Tags are applied as IMAP flags/keywords
- Processes each assignment in the assignments file
- Reports success/failure for each email

## Workflow

1. **Fetch emails**: `fetch_latest_emails.py` retrieves emails and outputs JSON + tag definitions
2. **External tagging**: LLM or external process reads emails and `tags.json`, creates `tag_assignments.json`
3. **Apply tags**: `apply_email_tags.py` reads assignments and applies tags via IMAP

## File Structure After Implementation

```
skills/email-fetch-latest/
├── SKILL.md
├── scripts/
│   ├── fetch_latest_emails.py    # Modified: output tag_definitions.json
│   └── apply_email_tags.py       # New: apply tags via IMAP
└── assets/
    └── emails/
        ├── INBOX/
        │   ├── 12345.json
        │   └── index.json
        ├── tag_definitions.json   # Copy of tags config
        └── tag_assignments.json   # Created by external process
```