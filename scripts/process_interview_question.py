#!/usr/bin/env python3
"""Convert a GitHub Issue interview submission into a Hugo page."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = {"dachang", "zhongchang", "xiaochang"}
CATEGORY_LABELS = {"大厂": "dachang", "中厂": "zhongchang", "小厂": "xiaochang"}
MAX_TITLE_LENGTH = 80


class SubmissionError(ValueError):
    """A user-facing conversion error for an unusable GitHub Issue event."""


def read_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SubmissionError(f"无法读取 GitHub Issue 事件文件：{error}") from error

    issue = payload.get("issue")
    if not isinstance(issue, dict) or not isinstance(issue.get("body"), str):
        raise SubmissionError("Issue 正文为空或格式不正确。")
    if not isinstance(issue.get("number"), int):
        raise SubmissionError("Issue 编号缺失或格式不正确。")
    if not isinstance(issue.get("user"), dict) or not issue["user"].get("login"):
        raise SubmissionError("Issue 提交者信息缺失。")
    return payload


def extract_selected_category(issue_body: str) -> str | None:
    """Read the company-size choice from the Issue Form."""
    match = re.search(
        r"^###\s*请选择面经要收录的目录\s*$\n+\s*(大厂|中厂|小厂)\s*$",
        issue_body,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return CATEGORY_LABELS[match.group(1)]


def extract_textarea_content(
    issue_body: str, field_label: str, next_field_label: str
) -> str | None:
    """Read a textarea up to the next known Issue Form field."""
    match = re.search(
        rf"^###\s*{re.escape(field_label)}\s*$\n"
        rf"(.*?)(?=^###\s*{re.escape(next_field_label)}\s*$|\Z)",
        issue_body,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return None
    content = match.group(1).strip()
    return content or None


def extract_submission_content(issue_body: str) -> str:
    """Get the submitted Markdown without rejecting imperfect formatting."""
    textarea_content = extract_textarea_content(issue_body, "面试内容", "投稿确认")
    if textarea_content is not None:
        return textarea_content

    legacy_content = extract_textarea_content(
        issue_body, "标准化 Markdown", "投稿确认"
    )
    if legacy_content is not None:
        return legacy_content

    return issue_body.strip()


def strip_front_matter(markdown: str) -> str:
    """Remove a leading front-matter block from legacy submissions."""
    if not markdown.startswith("---\n"):
        return markdown
    end = markdown.find("\n---", 3)
    if end == -1:
        return markdown
    front_matter = markdown[4:end]
    if not re.search(r"^title:", front_matter, flags=re.MULTILINE):
        return markdown
    return markdown[end + 4 :].lstrip("\n")


def normalize_title(issue_title: str, issue_number: int) -> str:
    title = re.sub(r"^\s*\[面经\]\s*", "", issue_title).strip()
    title = " ".join(title.split())
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH].rstrip()
    if len(title) < 5:
        title = f"面经投稿 Issue #{issue_number}"
    return title


def page_filename(issue_number: int) -> str:
    return f"issue-{issue_number}.md"


def append_github_output(values: dict[str, str | int]) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with open(output_file, "a", encoding="utf-8") as handler:
        for key, value in values.items():
            handler.write(f"{key}={value}\n")


def process(payload_path: Path, content_root: Path, write: bool) -> int:
    try:
        payload = read_payload(payload_path)
        issue = payload["issue"]
        issue_number = issue["number"]

        category = extract_selected_category(issue["body"])
        if category not in ALLOWED_CATEGORIES:
            category = "zhongchang"
        category_dir = content_root / category
        category_dir.mkdir(parents=True, exist_ok=True)

        title = normalize_title(issue.get("title", ""), issue_number)
        body = strip_front_matter(extract_submission_content(issue["body"])).strip()
        if not body:
            body = "待确认。"

        relative_path = category_dir / page_filename(issue_number)
        page = f'---\ntitle: {json.dumps(title, ensure_ascii=False)}\n---\n\n{body}\n'

        if write:
            relative_path.write_text(page, encoding="utf-8", newline="\n")

        append_github_output(
            {
                "content_path": relative_path.as_posix(),
                "page_title": title,
                "target_branch": f"bot/issue-{issue_number}",
                "pr_title": f"面经收录：{title} (#{issue_number})",
                "submitter": issue["user"]["login"],
                "issue_number": issue_number,
            }
        )
        print(f"已生成：{relative_path}")
        return 0
    except SubmissionError as error:
        print(f"无法生成投稿：{error}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path, help="GitHub issue event JSON")
    parser.add_argument("--content-root", type=Path, default=Path("content/docs/interview"))
    parser.add_argument("--write", action="store_true", help="写入生成的 Markdown 文件")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(process(parse_args().payload, parse_args().content_root, parse_args().write))
