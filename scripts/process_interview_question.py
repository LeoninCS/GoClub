#!/usr/bin/env python3
"""Validate an Issue Form interview submission and create a Hugo page."""

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
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_METADATA_KEYS = {"title", "category", "difficulty", "tags", "slug"}
MAX_MARKDOWN_LENGTH = 60_000
MAX_TITLE_LENGTH = 80
MAX_SLUG_LENGTH = 72
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SubmissionError(ValueError):
    """A user-facing validation error for an interview submission."""


@dataclass(frozen=True)
class ParsedSubmission:
    title: str
    category: str
    difficulty: str
    tags: tuple[str, ...]
    submitted_slug: str | None
    body_markdown: str
    slug: str


def read_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SubmissionError(f"无法读取 GitHub Issue 事件文件：{error}") from error

    issue = payload.get("issue")
    if not isinstance(issue, dict):
        raise SubmissionError("事件Payload中缺少 Issue 信息。")
    if not isinstance(issue.get("body"), str):
        raise SubmissionError("Issue 正文为空或格式不正确。")
    labels = issue.get("labels", [])
    label_names = {label.get("name") for label in labels if isinstance(label, dict)}
    if "question-submission" not in label_names:
        raise SubmissionError("这个 Issue 没有 question-submission 标签。")
    if not isinstance(issue.get("number"), int):
        raise SubmissionError("Issue 编号缺失或格式不正确。")
    if not isinstance(issue.get("user"), dict) or not issue["user"].get("login"):
        raise SubmissionError("Issue 提交者信息缺失。")
    return payload


def confirm_submission_rules(issue_body: str) -> None:
    if not re.search(
        r"^[-*]\s+\[[xX]\]\s+我已通过 interview-question Skill 格式化",
        issue_body,
        re.MULTILINE,
    ):
        raise SubmissionError("请先勾选“我已通过 interview-question Skill 格式化”。")
    if not re.search(
        r"^[-*]\s+\[[xX]\]\s+我确认内容不包含保密信息",
        issue_body,
        re.MULTILINE,
    ):
        raise SubmissionError("请先勾选内容安全和版权确认项。")


def extract_fenced_markdown(issue_body: str) -> str:
    """Extract the outer fenced block containing standardized interview Markdown."""
    if len(issue_body) > MAX_MARKDOWN_LENGTH + 8_000:
        raise SubmissionError("Issue 内容过长，请只提交一场面试。")

    candidates: list[str] = []
    lines = issue_body.splitlines()
    index = 0
    while index < len(lines):
        opening = re.fullmatch(r"(`{3,})[ \t]*(?:markdown|md|yaml)?[ \t]*", lines[index])
        if opening is None:
            index += 1
            continue

        fence_length = len(opening.group(1))
        content: list[str] = []
        index += 1
        while index < len(lines):
            if re.fullmatch(r"`{%d,}[ \t]*" % fence_length, lines[index]):
                candidates.append("\n".join(content))
                break
            content.append(lines[index])
            index += 1
        index += 1

    for candidate in candidates:
        if candidate.startswith("---\n"):
            if len(candidate) > MAX_MARKDOWN_LENGTH:
                raise SubmissionError("标准化 Markdown 超过 60,000 字符，请精简内容。")
            return candidate + "\n"

    raise SubmissionError(
        "没有找到包含 YAML Frontmatter 的 Markdown 代码块。"
        "请把 Skill 输出的完整面经放在四个反引号代码块内。"
    )


def split_front_matter(markdown: str) -> tuple[str, str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SubmissionError("Markdown 开头必须是 YAML Frontmatter 分隔线 ---。")

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            front_matter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :]).strip("\r\n")
            return front_matter, body

    raise SubmissionError("YAML Frontmatter 没有结束分隔线 ---。")


def decode_scalar(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise SubmissionError(f"{field} 不能为空。")
    try:
        if value.startswith('"') and value.endswith('"'):
            decoded = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            decoded = value[1:-1].replace("''", "'")
        else:
            decoded = value
    except json.JSONDecodeError as error:
        raise SubmissionError(f"{field} 的引号格式不正确。") from error
    if not isinstance(decoded, str) or not decoded.strip():
        raise SubmissionError(f"{field} 不能为空。")
    return decoded.strip()


def parse_inline_tags(value: str) -> list[str]:
    tags = decode_scalar(value, "tags")
    if tags.startswith("[") and tags.endswith("]"):
        try:
            decoded = json.loads(tags)
        except json.JSONDecodeError as error:
            raise SubmissionError("tags 必须是 YAML 列表。") from error
        if not isinstance(decoded, list) or any(not isinstance(tag, str) for tag in decoded):
            raise SubmissionError("tags 中每一项都必须是字符串。")
        return decoded
    raise SubmissionError("tags 必须使用列表格式，例如 [\"Go\", \"MySQL\"] 或多行列表。")


def parse_front_matter(front_matter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in front_matter.splitlines():
        if not raw_line.strip():
            current_key = None
            continue
        if raw_line.lstrip().startswith("#"):
            raise SubmissionError("Frontmatter 中不支持注释，请删除 # 注释行。")

        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(.*)", raw_line)
        if match:
            key = match.group(1)
            if key in result:
                raise SubmissionError(f"Frontmatter 字段 {key} 重复。")
            if key not in ALLOWED_METADATA_KEYS:
                raise SubmissionError(
                    f"Frontmatter 不支持字段 {key}。"
                    "只能包含 title、category、difficulty、tags 和可选 slug。"
                )
            value = match.group(2).strip()
            if value:
                result[key] = parse_inline_tags(value) if key == "tags" else decode_scalar(value, key)
                current_key = None
            else:
                result[key] = []
                current_key = key
            continue

        item = re.fullmatch(r"[ \t]+-[ \t]+(.+)", raw_line)
        if item and current_key == "tags":
            result["tags"].append(decode_scalar(item.group(1), "tags 项"))
            continue

        raise SubmissionError(f"Frontmatter 第 {raw_line!r} 无法解析。")

    if "tags" in result and not isinstance(result["tags"], list):
        raise SubmissionError("tags 必须是列表。")
    return result


def validate_metadata(metadata: dict[str, Any], issue_number: int, category_dir: Path) -> ParsedSubmission:
    required = {"title", "category", "difficulty", "tags"}
    missing = sorted(required - set(metadata))
    if missing:
        raise SubmissionError(f"Frontmatter 缺少必要字段：{', '.join(missing)}。")

    title = metadata["title"]
    category = metadata["category"]
    difficulty = metadata["difficulty"]
    tags = metadata["tags"]
    submitted_slug = metadata.get("slug")

    if not isinstance(title, str) or not (5 <= len(title) <= MAX_TITLE_LENGTH):
        raise SubmissionError("title 长度必须在 5 到 80 个字符之间。")
    if title != title.strip() or re.search(r"[\r\n\t]", title):
        raise SubmissionError("title 首尾不能有空格，也不能包含换行或制表符。")

    if category not in ALLOWED_CATEGORIES:
        allowed = "、".join(sorted(ALLOWED_CATEGORIES))
        raise SubmissionError(f"category 必须是以下之一：{allowed}。")

    if difficulty not in ALLOWED_DIFFICULTIES:
        raise SubmissionError("difficulty 只能是 easy、medium 或 hard。")

    if not isinstance(tags, list) or not tags:
        raise SubmissionError("tags 至少需要一个标签。")
    if len(tags) > 6:
        raise SubmissionError("tags 最多只能有 6 个。")
    if any(not isinstance(tag, str) for tag in tags):
        raise SubmissionError("tags 中每一项都必须是字符串。")
    normalized_tags = [tag.strip() for tag in tags]
    if any(not (2 <= len(tag) <= 24) for tag in normalized_tags):
        raise SubmissionError("每个 tag 长度必须在 2 到 24 个字符之间。")
    if len(set(normalized_tags)) != len(normalized_tags):
        raise SubmissionError("tags 不能重复。")

    if submitted_slug is not None:
        if not isinstance(submitted_slug, str) or not SLUG_RE.match(submitted_slug):
            raise SubmissionError("slug 只能包含小写字母、数字和连字符，且不能以连字符开头或结尾。")
        if len(submitted_slug) > MAX_SLUG_LENGTH:
            raise SubmissionError("slug 不能超过 72 个字符。")
        if (category_dir / f"{submitted_slug}.md").exists():
            raise SubmissionError(f"目标文件 {submitted_slug}.md 已存在，请更换 slug。")
        slug = submitted_slug
    else:
        normalized_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
        base = re.sub(r"[^A-Za-z0-9]+", "-", normalized_title).strip("-").lower()
        base = re.sub(r"-{2,}", "-", base)[:MAX_SLUG_LENGTH].rstrip("-")
        base = base if len(base) >= 2 else f"interview-issue-{issue_number}"
        slug = base
        if (category_dir / f"{slug}.md").exists():
            slug = f"{base}-issue-{issue_number}"
        if not SLUG_RE.match(slug) or len(slug) > MAX_SLUG_LENGTH:
            raise SubmissionError("无法生成合法的 ASCII slug，请在 Frontmatter 提供 slug 字段。")

    return ParsedSubmission(
        title=title,
        category=category,
        difficulty=difficulty,
        tags=tuple(normalized_tags),
        submitted_slug=submitted_slug,
        body_markdown="",
        slug=slug,
    )


def validate_content(markdown: str, parsed: ParsedSubmission) -> ParsedSubmission:
    """Validate only page safety and non-emptiness; do not enforce article structure."""
    if not markdown.strip():
        raise SubmissionError("正文不能为空。")

    forbidden_patterns = {
        "Hugo shortcode": r"\{\{[<%]",
        "script 标签": r"<\s*script\b",
        "iframe 标签": r"<\s*iframe\b",
        "style 标签": r"<\s*style\b",
        "内联事件属性": r"\bon[a-z]+\s*=",
        "javascript 链接": r"(?i)javascript[ \t]*:",
    }
    for label, pattern in forbidden_patterns.items():
        if re.search(pattern, markdown):
            raise SubmissionError(f"内容不允许包含{label}。")

    return ParsedSubmission(
        title=parsed.title,
        category=parsed.category,
        difficulty=parsed.difficulty,
        tags=parsed.tags,
        submitted_slug=parsed.submitted_slug,
        body_markdown=markdown.strip() + "\n",
        slug=parsed.slug,
    )


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
        confirm_submission_rules(issue["body"])
        source_markdown = extract_fenced_markdown(issue["body"])
        front_matter, body = split_front_matter(source_markdown)
        metadata = parse_front_matter(front_matter)

        issue_number = issue["number"]
        category = metadata.get("category")
        if category not in ALLOWED_CATEGORIES:
            allowed = "、".join(sorted(ALLOWED_CATEGORIES))
            raise SubmissionError(f"category 必须是以下之一：{allowed}。")
        category_dir = content_root / str(category)
        category_dir.mkdir(parents=True, exist_ok=True)
        parsed = validate_metadata(metadata, issue_number, category_dir)
        parsed = validate_content(body, parsed)

        relative_path = category_dir / f"{parsed.slug}.md"
        if relative_path.exists():
            raise SubmissionError("目标文件已存在，请更换 slug。")
        page = render_page(parsed, issue_number)
        if write:
            relative_path.write_text(page, encoding="utf-8", newline="\n")

        append_github_output(
            {
                "content_path": relative_path.as_posix(),
                "page_title": parsed.title,
                "page_slug": parsed.slug,
                "target_branch": f"bot/issue-{issue_number}",
                "pr_title": f"面经收录：{parsed.title} (#{issue_number})",
                "submitter": issue["user"]["login"],
                "issue_number": issue_number,
            }
        )
        print(f"校验通过：{relative_path}")
        return 0
    except SubmissionError as error:
        print(f"格式校验失败：{error}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path, help="GitHub issue event JSON")
    parser.add_argument("--content-root", type=Path, default=Path("content/docs/interview"))
    parser.add_argument("--write", action="store_true", help="写入生成的 Markdown 文件")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(process(parse_args().payload, parse_args().content_root, parse_args().write))
