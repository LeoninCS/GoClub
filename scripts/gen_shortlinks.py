#!/usr/bin/env python3
"""为主要内容页生成稳定的 /s/ 短链。

背景：可读 slug 让 URL 从 271 字符降到 63，但发微信时仍偏长。
这里额外给每个页面挂一个 /s/xxxx 短链（约 28 字符），现有 URL 完全不变，
只是多一个入口。Hugo 会用 aliases 在短链地址生成跳转页。

短码由「内容文件路径」哈希得到，因此：
  - 改标题、改正文、改 slug，短码都不变
  - 只有重命名/移动文件才会变（这时应保留旧短链）

用法：
  python3 scripts/gen_shortlinks.py          # 写入缺失的短链
  python3 scripts/gen_shortlinks.py --check  # 只检查，CI 用
  python3 scripts/gen_shortlinks.py --list   # 打印全部短链对照表
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

CONTENT_ROOT = "content/docs"
CODE_LEN = 4
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"

# 整本书的单章不生成短链，避免占用命名空间；书的目录页仍然生成
BOOK_PREFIXES = (
    "resources/web3-books/",
    "resources/epub-books/",
    "resources/pdf-books/",
    "resources/cloud-native-web3-fulltext/",
)

SHORTLINK_RE = re.compile(r'^shortlink:\s*["\']?([a-z0-9]+)["\']?\s*$', re.MULTILINE)


def is_book_chapter(rel: str) -> bool:
    return any(rel.startswith(p) for p in BOOK_PREFIXES) and not rel.endswith("_index.md")


def encode(num: int, length: int) -> str:
    out = []
    for _ in range(length):
        num, rem = divmod(num, len(ALPHABET))
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


def make_code(rel: str, length: int = CODE_LEN) -> str:
    digest = hashlib.sha1(rel.encode("utf-8")).digest()
    return encode(int.from_bytes(digest, "big"), length)


def collect_pages() -> list[str]:
    pages = []
    for root, _dirs, files in os.walk(CONTENT_ROOT):
        for name in files:
            if not name.endswith(".md"):
                continue
            rel = os.path.join(root, name)[len(CONTENT_ROOT) + 1 :]
            if is_book_chapter(rel):
                continue
            pages.append(rel)
    return sorted(pages)


def assign_codes(pages: list[str]) -> dict[str, str]:
    """分配短码，碰撞时对后来者逐位加长，保证结果稳定且唯一。"""
    codes: dict[str, str] = {}
    used: dict[str, str] = {}
    for rel in pages:
        length = CODE_LEN
        code = make_code(rel, length)
        while code in used:
            length += 1
            code = make_code(rel, length)
            if length > 12:
                raise RuntimeError(f"无法为 {rel} 分配唯一短码")
        used[code] = rel
        codes[rel] = code
    return codes


def read_front_matter(text: str) -> tuple[str, int] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[4 : end + 1], end


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查是否有页面缺短链")
    ap.add_argument("--list", action="store_true", help="打印短链对照表")
    args = ap.parse_args()

    pages = collect_pages()
    codes = assign_codes(pages)

    if args.list:
        for rel in pages:
            print(f"{codes[rel]}  {rel}")
        return 0

    missing: list[str] = []
    written = 0

    for rel in pages:
        path = os.path.join(CONTENT_ROOT, rel)
        code = codes[rel]
        text = open(path, encoding="utf-8").read()
        parsed = read_front_matter(text)

        if parsed is None:
            missing.append(f"{path}\n    缺少 front matter，无法写入短链")
            continue

        fm, end = parsed
        found = SHORTLINK_RE.search(fm)

        if found:
            if found.group(1) != code:
                missing.append(
                    f"{path}\n    短链 {found.group(1)} 与按路径计算的 {code} 不一致"
                    f"（文件可能被重命名过，确认后手工处理，别直接改掉已发布的短链）"
                )
            continue

        if args.check:
            missing.append(f"{path}\n    缺少短链，运行 python3 scripts/gen_shortlinks.py 生成")
            continue

        body = fm.rstrip("\n")
        alias = f"/s/{code}/"
        if re.search(r"^aliases:", body, re.MULTILINE):
            body = re.sub(r"^(aliases:\n(?:\s+-.*\n)*)", rf'\1  - "{alias}"\n', body + "\n",
                          count=1, flags=re.MULTILINE).rstrip("\n")
        else:
            body += f'\naliases:\n  - "{alias}"'
        body += f'\nshortlink: "{code}"'

        open(path, "w", encoding="utf-8").write("---\n" + body + "\n" + text[end + 1 :])
        written += 1

    if missing:
        print("短链检查未通过：\n", file=sys.stderr)
        for m in missing:
            print(f"  {m}\n", file=sys.stderr)
        return 1

    if args.check:
        print(f"短链检查通过，{len(pages)} 个页面均已配置。")
    else:
        print(f"完成：新写入 {written} 个短链，共 {len(pages)} 个页面。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
