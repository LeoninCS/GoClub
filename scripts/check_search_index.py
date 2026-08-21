#!/usr/bin/env python3

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ALLOWED_CATEGORIES = {
    "面试真题",
    "八股总结",
    "资源荟萃",
    "技术博客",
    "配套文章",
    "项目学习",
    "求职就业",
    "其他",
}
REQUIRED_FIELDS = ("href", "title", "category", "type")
SEARCH_EXCLUDE_PATTERN = re.compile(r"(?mi)^\s*bookSearchExclude\s*[:=]\s*true\s*$")


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, _tag, attrs):
        for name, value in attrs:
            if name == "id" and value:
                self.ids.add(value)


def parse_args():
    parser = argparse.ArgumentParser(description="校验 Hugo 搜索索引覆盖范围和结果链接")
    parser.add_argument("--site", default="public", help="Hugo 输出目录，默认 public")
    parser.add_argument("--hugo", default="hugo", help="Hugo 可执行文件，默认 hugo")
    return parser.parse_args()


def configure_output():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def split_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() not in {"---", "+++"}:
        return "", text

    delimiter = lines[0].strip()
    for index in range(1, len(lines)):
        if lines[index].strip() == delimiter:
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return "", text


def normalize_route(value):
    path = unquote(urlsplit(value).path)
    if not path.startswith("/"):
        path = f"/{path}"
    if path != "/" and not Path(path).suffix:
        path = f"{path.rstrip('/')}/"
    return path


def output_path_for_href(site_dir, href):
    path = normalize_route(href).lstrip("/")
    output = site_dir / Path(path)
    if path.endswith("/") or not output.suffix:
        output /= "index.html"
    return output


def load_current_index(site_dir):
    candidates = list(site_dir.glob("*.search-data.min.*.json"))
    if not candidates:
        raise RuntimeError(f"{site_dir} 中没有生成搜索索引，请先运行 hugo --minify")
    index_path = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    with index_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list) or not records:
        raise RuntimeError(f"搜索索引为空或格式错误：{index_path}")
    return index_path, records


def list_published_content(hugo, repo_root):
    result = subprocess.run(
        [hugo, "list", "published"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return list(csv.DictReader(io.StringIO(result.stdout)))


def expected_routes(rows, repo_root):
    expected = {}
    for row in rows:
        if row.get("kind") not in {"page", "section"}:
            continue
        source_value = row.get("path", "")
        permalink = row.get("permalink", "")
        if not source_value or not permalink:
            continue

        source_path = repo_root / Path(source_value)
        if not source_path.is_file():
            continue
        text = source_path.read_text(encoding="utf-8")
        front_matter, body = split_front_matter(text)
        if SEARCH_EXCLUDE_PATTERN.search(front_matter) or not body.strip():
            continue

        route = normalize_route(permalink)
        if route.startswith("/docs/") or route == "/docs/":
            expected[route] = source_value
    return expected


def collect_html_ids(path, cache):
    if path not in cache:
        parser = IdCollector()
        parser.feed(path.read_text(encoding="utf-8"))
        cache[path] = parser.ids
    return cache[path]


def validate_records(records, site_dir):
    errors = []
    indexed_routes = set()
    seen_hrefs = set()
    html_ids = {}

    for position, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"第 {position + 1} 条记录不是对象")
            continue
        missing = [field for field in REQUIRED_FIELDS if not record.get(field)]
        if missing:
            errors.append(f"第 {position + 1} 条记录缺少字段：{', '.join(missing)}")
            continue
        category = record["category"]
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{record['href']} 使用了未归一化栏目：{category}")

        href = record["href"]
        if href in seen_hrefs:
            errors.append(f"搜索记录链接重复：{href}")
        seen_hrefs.add(href)
        indexed_routes.add(normalize_route(href))

        output_path = output_path_for_href(site_dir, href)
        if not output_path.is_file():
            errors.append(f"搜索结果页面不存在：{href} -> {output_path}")
            continue

        fragment = unquote(urlsplit(href).fragment)
        if fragment and fragment not in collect_html_ids(output_path, html_ids):
            errors.append(f"搜索结果锚点不存在：{href}")

    return errors, indexed_routes


def main():
    configure_output()
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    site_dir = (repo_root / args.site).resolve()

    try:
        index_path, records = load_current_index(site_dir)
        rows = list_published_content(args.hugo, repo_root)
        expected = expected_routes(rows, repo_root)
        errors, indexed_routes = validate_records(records, site_dir)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"搜索索引校验失败：{error}", file=sys.stderr)
        return 1

    missing_routes = sorted(set(expected) - indexed_routes)
    errors.extend(
        f"应收录内容未进入搜索索引：{route}（{expected[route]}）"
        for route in missing_routes
    )

    if errors:
        print("搜索索引校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    category_counts = {}
    for record in records:
        category = record["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    summary = "，".join(
        f"{category} {count} 条" for category, count in sorted(category_counts.items())
    )
    print(
        f"搜索索引校验通过：{index_path.name}，{len(records)} 条记录，"
        f"覆盖 {len(expected)} 个内容页面；{summary}。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
