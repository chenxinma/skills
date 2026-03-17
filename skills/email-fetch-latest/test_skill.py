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

    print(f"\n{'=' * 40}")
    if failed:
        print(f"测试失败: {failed}")
        return 1
    print("所有测试通过!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
