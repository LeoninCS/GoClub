#!/usr/bin/env python3
"""Convert an Issue Form interview submission into a Hugo page."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_CATEGORIES = {"dachang", "zhongchang", "xiaochang"}
CATEGORY_LABELS = {"大厂": "dachang", "中厂": "zhongchang", "小厂": "xiaochang"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
MAX_TITLE_LENGTH = 80
MAX_SLUG_LENGTH = 72
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SubmissionError(ValueError):
    """A user-facing conversion error for an unusable GitHub Issue event."""


@dataclass(frozen=True)
class ParsedSubmission:
    title: str
    category: str
    difficulty: str
    tags: tuple[str, ...]
    body_markdown: str
    slug: str


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


def extract_fenced_blocks(issue_body: str) -> list[str]:
    blocks: list[str] = []
    lines = issue_body.splitlines()
    index = 0
    while index < len(lines):
        opening = re.fullmatch(r"(`{3,})[ \t]*(?:markdown|md)?[ \t]*", lines[index])
        if opening is None:
            index += 1
            continue

        fence_length = len(opening.group(1))
        content: list[str] = []
        index += 1
        while index < len(lines):
            if re.fullmatch(r"`{%d,}[ \t]*" % fence_length, lines[index]):
                blocks.append("\n".join(content).strip("\n"))
                break
            content.append(lines[index])
            index += 1
        index += 1
    return blocks


def extract_selected_category(issue_body: str) -> str | None:
    """Read the company-size choice from the Issue Form."""
    match = re.search(
        r"^###[^\n]*\n+\s*(大厂|中厂|小厂)\s*$",
        issue_body,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return CATEGORY_LABELS[match.group(1)]


def extract_submission_content(issue_body: str) -> str:
    """Get the submitted Markdown without rejecting imperfect formatting."""
    blocks = extract_fenced_blocks(issue_body)
    if blocks:
        return max(blocks, key=len)

    match = re.search(
        r"^###\s+标准化 Markdown\s*$\n(.*?)(?=^###\s+|\Z)",
        issue_body,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match and match.group(1).strip():
        return match.group(1).strip()

    lines = []
    for line in issue_body.splitlines():
        if line.startswith("### ") or re.match(r"^[-*]\s+\[[ xX]\]", line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def split_front_matter(markdown: str) -> tuple[dict[str, Any], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            front_matter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :]).strip("\r\n")
            metadata = parse_metadata(front_matter)
            return metadata, body
    return {}, markdown


def decode_scalar(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} is empty")
    if value.startswith('"') and value.endswith('"'):
        value = json.loads(value)
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1].replace("''", "'")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is empty")
    return value.strip()


def parse_metadata(front_matter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in front_matter.splitlines():
        if not raw_line.strip():
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(.*)", raw_line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            if value:
                result[key] = decode_scalar(value, key) if key != "tags" else [decode_scalar(value, "tags")]
            else:
                result[key] = []
                current_key = key
            continue
        item = re.fullmatch(r"[ \t]+-[ \t]+(.+)", raw_line)
        if item and current_key == "tags":
            result[current_key].append(decode_scalar(item.group(1), "tags item"))
            continue
        raise ValueError(f"unsupported front matter line: {raw_line!r}")
    return result


def normalize_title(metadata: dict[str, Any], issue_title: str, issue_number: int) -> str:
    title = metadata.get("title") if isinstance(metadata.get("title"), str) else ""
    if not title.strip():
        title = re.sub(r"^\s*\[面经\]\s*", "", issue_title).strip()
    title = " ".join(title.split())
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH].rstrip()
    if len(title) < 5:
        title = f"面经投稿 Issue #{issue_number}"
    return title


def normalize_tags(metadata: dict[str, Any], body: str) -> tuple[str, ...]:
    raw_tags = metadata.get("tags", [])
    if isinstance(raw_tags, str):
        raw_tags = [raw_tags]
    if not isinstance(raw_tags, list):
        raw_tags = []

    tags = []
    for tag in raw_tags:
        if not isinstance(tag, str):
            continue
        tag = tag.strip()
        if 2 <= len(tag) <= 24 and tag not in tags:
            tags.append(tag)

    candidates = (
        ("Go", ("go ", "golang", "goroutine")),
        ("MySQL", ("mysql",)),
        ("Redis", ("redis",)),
        ("Kubernetes", ("kubernetes", "k8s")),
        ("分布式", ("分布式",)),
    )
    lowered = body.lower()
    for tag, keywords in candidates:
        if len(tags) >= 6:
            break
        if tag not in tags and any(keyword in lowered for keyword in keywords):
            tags.append(tag)
    if not tags:
        tags = ["Go"]
    return tuple(tags[:6])


def normalize_slug(metadata: dict[str, Any], title: str, issue_number: int, category_dir: Path) -> str:
    submitted = metadata.get("slug") if isinstance(metadata.get("slug"), str) else ""

    def ascii_slug(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^A-Za-z0-9]+", "-", normalized).strip("-").lower()
        return re.sub(r"-{2,}", "-", slug)[:MAX_SLUG_LENGTH].rstrip("-")

    slug = ascii_slug(submitted) or ascii_slug(title) or f"interview-issue-{issue_number}"
    if not SLUG_RE.match(slug):
        slug = f"interview-issue-{issue_number}"
    if (category_dir / f"{slug}.md").exists():
        slug = f"{slug[: MAX_SLUG_LENGTH - len(str(issue_number)) - 7]}-issue-{issue_number}"
    return slug


def normalize_body(body: str, title: str) -> str:
    lines = body.strip().splitlines()
    if not lines:
        lines = [title, "", "待确认。"]

    if lines and not lines[0].lstrip().startswith("#"):
        lines[0] = f"# {lines[0].strip() or title}"

    output: list[str] = []
    in_answers = False
    for line in lines:
        stripped = line.strip()
        if stripped == "参考答案（AI 生成）":
            output.append("## 参考答案（AI 生成）")
            in_answers = True
            continue
        if in_answers and re.match(r"^\d+[.、]\s*", stripped):
            output.append(re.sub(r"^(\d+)[.、]\s*", r"### \1. ", stripped))
            continue
        if in_answers and stripped == "以下答案由 AI 生成，仅供面试复盘参考。":
            output.append("> 以下答案由 AI 生成，仅供面试复盘参考。")
            continue
        output.append(line)
    return "\n".join(output).strip() + "\n"


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_page(submission: ParsedSubmission, issue_number: int) -> str:
    front_matter = [
        "---",
        f"title: {yaml_quote(submission.title)}",
        f"category: {yaml_quote(submission.category)}",
        f"difficulty: {yaml_quote(submission.difficulty)}",
        "tags:",
        *(f"  - {yaml_quote(tag)}" for tag in submission.tags),
        f"weight: {issue_number}",
        f"slug: {yaml_quote(submission.slug)}",
        "---",
    ]
    return "\n".join(front_matter) + "\n\n" + submission.body_markdown


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
        source_markdown = extract_submission_content(issue["body"])
        try:
            metadata, body = split_front_matter(source_markdown)
        except (ValueError, json.JSONDecodeError):
            metadata, body = {}, source_markdown

        issue_number = issue["number"]
        category = extract_selected_category(issue["body"])
        if category is None:
            category = metadata.get("category") if isinstance(metadata.get("category"), str) else ""
        if category not in ALLOWED_CATEGORIES:
            category = "zhongchang"
        category_dir = content_root / category
        category_dir.mkdir(parents=True, exist_ok=True)

        title = normalize_title(metadata, issue.get("title", ""), issue_number)
        difficulty = metadata.get("difficulty") if isinstance(metadata.get("difficulty"), str) else ""
        if difficulty not in ALLOWED_DIFFICULTIES:
            difficulty = "medium"
        tags = normalize_tags(metadata, source_markdown)
        slug = normalize_slug(metadata, title, issue_number, category_dir)
        body = normalize_body(body, title)
        submission = ParsedSubmission(title, category, difficulty, tags, body, slug)

        relative_path = category_dir / f"{submission.slug}.md"
        page = render_page(submission, issue_number)
        if write:
            relative_path.write_text(page, encoding="utf-8", newline="\n")

        append_github_output(
            {
                "content_path": relative_path.as_posix(),
                "page_title": submission.title,
                "page_slug": submission.slug,
                "target_branch": f"bot/issue-{issue_number}",
                "pr_title": f"面经收录：{submission.title} (#{issue_number})",
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
