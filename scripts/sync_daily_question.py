#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import html
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


SHANGHAI_TZ = timezone(timedelta(hours=8), "Asia/Shanghai")
MAX_QUESTION_LENGTH = 500
MAX_ANSWER_LENGTH = 20000
INLINE_LINK_DESTINATION = re.compile(
    r"(?P<prefix>\]\(\s*<?\s*)"
    r"(?P<scheme>(?:[A-Za-z0-9+.-]|\\|[\x00-\x20])+):"
)
REFERENCE_LINK_DESTINATION = re.compile(
    r"(?P<prefix>^\s{0,3}\[[^\]\r\n]+\]:\s*<?\s*)"
    r"(?P<scheme>(?:[A-Za-z0-9+.-]|\\|[\x00-\x20])+):"
)
DANGEROUS_URL_SCHEMES = {"javascript", "vbscript", "data", "file"}
PERCENT_SHORTCODE = re.compile(r"{{%(?P<body>.*?)%}}", re.DOTALL)
ANGLE_SHORTCODE = re.compile(r"{{<(?P<body>.*?)>}}", re.DOTALL)
DEFAULT_CONTENT_PATH = (
    Path(__file__).resolve().parents[1]
    / "content"
    / "docs"
    / "baguwen"
    / "每日一问.md"
)


@dataclass(frozen=True)
class Submission:
    question: str
    answer: str
    date: str


def parse_submission_date(value):
    if not isinstance(value, str):
        raise ValueError("提交时间必须是字符串")
    try:
        if re.fullmatch(r"\d{4}/\d{2}/\d{2}", value):
            return datetime.strptime(value, "%Y/%m/%d").strftime("%Y.%m.%d")
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("提交时间格式无效") from error
    if timestamp.tzinfo is None:
        raise ValueError("提交时间必须包含时区")
    return timestamp.astimezone(SHANGHAI_TZ).strftime("%Y.%m.%d")


def prepare_submission(question, answer, submitted_at):
    if not isinstance(question, str):
        raise ValueError("题目必须是字符串")
    if not isinstance(answer, str):
        raise ValueError("答案必须是字符串")
    normalized_question = re.sub(r"\s*[\r\n]+\s*", " ", question.strip())
    normalized_answer = answer.strip().replace("\r\n", "\n").replace("\r", "\n")
    normalized_answer = "\n".join(
        line.rstrip(" \t") for line in normalized_answer.split("\n")
    )
    if not normalized_question:
        raise ValueError("题目不能为空")
    if not normalized_answer:
        raise ValueError("答案不能为空")
    if len(normalized_question) > MAX_QUESTION_LENGTH:
        raise ValueError("题目不能超过 500 个字符")
    if len(normalized_answer) > MAX_ANSWER_LENGTH:
        raise ValueError("答案不能超过 20000 个字符")
    return Submission(
        question=normalized_question,
        answer=normalized_answer,
        date=parse_submission_date(submitted_at),
    )


def _escape_plain_markdown(value):
    def neutralize(match):
        scheme = re.sub(r"[\\\x00-\x20]", "", match.group("scheme"))
        if scheme.lower() not in DANGEROUS_URL_SCHEMES:
            return match.group(0)
        return f"{match.group('prefix')}{scheme}%3A"

    value = INLINE_LINK_DESTINATION.sub(neutralize, value)
    value = REFERENCE_LINK_DESTINATION.sub(neutralize, value)
    return html.escape(value, quote=False)


def _escape_outside_inline_code(line):
    parts = []
    position = 0
    while position < len(line):
        start = line.find("`", position)
        if start < 0:
            parts.append(_escape_plain_markdown(line[position:]))
            break

        parts.append(_escape_plain_markdown(line[position:start]))
        run_length = 1
        while start + run_length < len(line) and line[start + run_length] == "`":
            run_length += 1

        closing = re.compile(rf"(?<!`)`{{{run_length}}}(?!`)").search(
            line,
            start + run_length,
        )
        if closing is None:
            parts.append(_escape_plain_markdown(line[start:]))
            break

        end = closing.end()
        parts.append(line[start:end])
        position = end

    return "".join(parts)


def _neutralize_hugo_shortcodes(value):
    def escape(match, opening, closing):
        body = match.group("body")
        if body.startswith("/*") and body.endswith("*/"):
            return match.group(0)
        body = body.replace("*/", "*&#47;")
        return f"{opening}/*{body}*/{closing}"

    value = PERCENT_SHORTCODE.sub(
        lambda match: escape(match, "{{%", "%}}"),
        value,
    )
    return ANGLE_SHORTCODE.sub(
        lambda match: escape(match, "{{<", ">}}"),
        value,
    )


def sanitize_markdown(value):
    lines = value.split("\n")
    sanitized = []
    fence_character = None
    fence_length = 0
    indented_code = False
    indented_code_minimum = 4
    previous_line_blank = True
    list_code_indent = None

    for line in lines:
        indented = len(line) - len(line.lstrip(" "))
        stripped = line[indented:]

        if fence_character is not None:
            sanitized.append(line)
            closing = re.match(rf"{re.escape(fence_character)}+", stripped)
            if (
                indented <= 3
                and closing is not None
                and len(closing.group(0)) >= fence_length
                and stripped[closing.end() :].strip() == ""
            ):
                fence_character = None
                fence_length = 0
            continue

        if indented_code:
            if not stripped or indented >= indented_code_minimum:
                sanitized.append(line)
                continue
            indented_code = False

        required_code_indent = list_code_indent or 4
        if indented >= required_code_indent and previous_line_blank:
            indented_code = True
            indented_code_minimum = required_code_indent
            sanitized.append(line)
            previous_line_blank = False
            continue

        opening = re.match(r"(`{3,}|~{3,})", stripped) if indented <= 3 else None
        if (
            opening is not None
            and opening.group(0).startswith("`")
            and "`" in stripped[opening.end() :]
        ):
            opening = None
        if opening is not None:
            delimiter = opening.group(0)
            fence_character = delimiter[0]
            fence_length = len(delimiter)
            sanitized.append(line)
            continue

        sanitized.append(_escape_outside_inline_code(line))
        if stripped:
            list_marker = re.match(
                r"(?:[-+*]|\d{1,9}[.)])(?: {1,4}|\t)",
                stripped,
            )
            if list_marker is not None:
                list_code_indent = indented + list_marker.end() + 4
            elif indented == 0:
                list_code_indent = None
            previous_line_blank = False
        else:
            previous_line_blank = True

    return _neutralize_hugo_shortcodes("\n".join(sanitized))


def _find_date_heading(value, date=None):
    expected_date = re.escape(date) if date is not None else r"\d{4}\.\d{2}\.\d{2}"
    heading = re.compile(
        rf"##[ \t]+{expected_date}(?:[ \t]+#+)?[ \t]*$"
    )
    fence_character = None
    fence_length = 0
    offset = 0

    for line_with_ending in value.splitlines(keepends=True):
        line = line_with_ending.rstrip("\r\n")
        indented = len(line) - len(line.lstrip(" "))
        stripped = line[indented:]

        if fence_character is not None:
            closing = re.fullmatch(
                rf"{re.escape(fence_character)}{{{fence_length},}}[ \t]*",
                stripped,
            )
            if indented <= 3 and closing is not None:
                fence_character = None
                fence_length = 0
            offset += len(line_with_ending)
            continue

        opening = re.match(r"(`{3,}|~{3,})(.*)$", stripped) if indented <= 3 else None
        if opening is not None:
            delimiter = opening.group(1)
            if not (delimiter[0] == "`" and "`" in opening.group(2)):
                fence_character = delimiter[0]
                fence_length = len(delimiter)
                offset += len(line_with_ending)
                continue

        if indented <= 3 and heading.fullmatch(stripped) is not None:
            return offset

        offset += len(line_with_ending)

    return None


def update_content(existing, submission):
    if _find_date_heading(existing, submission.date) is not None:
        return existing, False

    newline = "\r\n" if "\r\n" in existing else "\n"
    question = sanitize_markdown(submission.question)
    answer = sanitize_markdown(submission.answer).replace("\n", newline)
    entry = (
        f"## {submission.date}{newline}{newline}"
        f"### {question}{newline}{newline}"
        f"{answer}{newline}{newline}"
    )

    position = _find_date_heading(existing)
    if position is not None:
        return existing[:position] + entry + existing[position:], True

    if not existing or existing.endswith(newline * 2):
        separator = ""
    elif existing.endswith(newline):
        separator = newline
    else:
        separator = newline * 2
    return existing + separator + entry, True


def load_submission(payload_path):
    try:
        payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("投稿载荷不是有效的 JSON") from error

    if not isinstance(payload, dict) or not isinstance(payload.get("inputs"), dict):
        raise ValueError("投稿载荷缺少 inputs 对象")

    inputs = payload["inputs"]
    field_names = {
        "question": "题目",
        "answer": "答案",
        "submitted_at": "提交时间",
    }
    values = {}
    for key, label in field_names.items():
        if key not in inputs:
            raise ValueError(f"投稿载荷缺少{label}字段")
        if not isinstance(inputs[key], str):
            raise ValueError(f"{label}必须是字符串")
        values[key] = inputs[key]

    return prepare_submission(
        values["question"],
        values["answer"],
        values["submitted_at"],
    )


def sync_file(content_path, submission):
    path = Path(content_path)
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    updated, changed = update_content(original, submission)
    if not changed:
        return False

    updated_bytes = updated.encode("utf-8")
    original_mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(updated_bytes)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return True


def build_parser():
    parser = argparse.ArgumentParser(description="将每日一问题投稿同步到内容文件")
    parser.add_argument(
        "--payload",
        required=True,
        help="GitHub workflow_dispatch 事件 JSON 文件",
    )
    parser.add_argument(
        "--content",
        default=DEFAULT_CONTENT_PATH,
        help="每日一问 Markdown 内容文件",
    )
    return parser


def main(argv=None):
    arguments = build_parser().parse_args(argv)
    try:
        submission = load_submission(arguments.payload)
        changed = sync_file(arguments.content, submission)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"同步失败：{error}", file=sys.stderr)
        return 1

    print("已更新" if changed else "无变更")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
