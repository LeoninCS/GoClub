#!/usr/bin/env python3
"""校验 content/ 下所有页面的 URL 是否为短链（纯 ASCII）。

背景：Hugo 默认用文件名生成 URL。中文文件名会被浏览器 percent-encode，
一个汉字变成 9 个字符，分享到微信时链接极长（实测最长 271 字符）。
解决办法是在 front matter 里用 slug 指定一个可读的英文短路径。

本脚本在 CI 中运行，PR 引入不合规页面时会失败并给出修复方式。
本地自查：python3 scripts/check_slugs.py
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from collections import defaultdict

CONTENT_DIR = "content"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FM_SLUG_RE = re.compile(r"^slug:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def is_ascii(text: str) -> bool:
    return all(ord(ch) < 128 for ch in text)


def read_front_matter(text: str) -> str | None:
    """返回 YAML front matter 正文；没有 front matter 时返回 None。"""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[4 : end + 1]


def main() -> int:
    errors: list[str] = []
    # 目录 -> [(URL 末段, 来源文件)]，用于查重
    segments: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for root, _dirs, files in os.walk(CONTENT_DIR):
        # 目录名直接构成 URL 路径段，必须是 ASCII
        rel_dir = os.path.relpath(root, CONTENT_DIR)
        if rel_dir != "." and not is_ascii(rel_dir):
            bad = [p for p in rel_dir.split(os.sep) if not is_ascii(p)]
            errors.append(
                f"{root}/\n"
                f"    目录名含非 ASCII 字符：{', '.join(bad)}\n"
                f"    目录名直接进入 URL，无法用 slug 覆盖，请重命名为英文。"
            )

        for name in sorted(files):
            if not name.endswith(".md"):
                continue

            path = os.path.join(root, name)
            stem = name[:-3]

            # _index.md 的 URL 由所在目录决定，上面已检查过目录名
            if stem == "_index":
                continue

            text = open(path, encoding="utf-8").read()
            fm = read_front_matter(text)

            if fm is None:
                # 中文文件名没有 front matter 就无法指定 slug，URL 一定会被编码
                if not is_ascii(stem):
                    errors.append(
                        f"{path}\n"
                        f"    文件名含中文但缺少 front matter，无法指定 slug。\n"
                        f"    请在文件开头补上 front matter 并填写 title 与 slug。"
                    )
                else:
                    # 英文文件名 URL 虽然没问题，但缺 front matter 会导致
                    # title 缺失、无法挂短链，同样需要补上
                    errors.append(
                        f"{path}\n"
                        f"    缺少 front matter。\n"
                        f"    请在文件开头补上 front matter 并填写 title。"
                    )
                continue

            match = FM_SLUG_RE.search(fm)
            slug = match.group(1).strip() if match else None

            if slug is None:
                if not is_ascii(stem):
                    errors.append(
                        f"{path}\n"
                        f"    文件名含中文但没有 slug，生成的 URL 会被编码成一长串 %XX。\n"
                        f"    请在 front matter 里加一行，例如：slug: \"blocke-bytedance-1\""
                    )
                    segments[root].append((stem, path))
                else:
                    segments[root].append((stem, path))
                continue

            if not SLUG_RE.match(slug):
                errors.append(
                    f"{path}\n"
                    f"    slug 不合法：{slug!r}\n"
                    f"    只允许小写字母、数字和连字符，例如：blocke-bytedance-1"
                )
            segments[root].append((slug, path))

    # 同目录下 URL 末段不能重复，否则页面会互相覆盖
    for directory, items in segments.items():
        seen: dict[str, str] = {}
        for seg, path in items:
            key = unicodedata.normalize("NFC", seg)
            if key in seen:
                errors.append(
                    f"{path}\n"
                    f"    URL 末段 {seg!r} 与 {seen[key]} 冲突，两个页面会指向同一地址。\n"
                    f"    请给其中一个换一个更具体的 slug。"
                )
            else:
                seen[key] = path

    if errors:
        print("URL 短链校验未通过：\n", file=sys.stderr)
        for err in errors:
            print(f"  {err}\n", file=sys.stderr)
        print(
            "命名规范（面经）：投稿人-公司-岗位-轮次，例如 blocke-bytedance-1\n"
            "命名规范（其他）：用简短英文描述内容，例如 go-backend-roadmap\n"
            "改动已发布过的页面 slug 时，记得在 aliases 里保留旧路径，避免已分享的链接失效。\n"
            f"\n共 {len(errors)} 处问题。",
            file=sys.stderr,
        )
        return 1

    print("URL 短链校验通过，所有页面路径均为 ASCII 短链。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
