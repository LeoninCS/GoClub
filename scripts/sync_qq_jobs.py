#!/usr/bin/env python3

import base64
import argparse
import asyncio
import hashlib
import html
import http.client
import json
import os
import socket
import ssl
import sys
import tempfile
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class IntegrityError(ValueError):
    """Raised when a source snapshot cannot be proven complete."""


class SourceDeletionError(IntegrityError):
    """Raised when records disappear without explicit operator approval."""


@dataclass(frozen=True)
class DatasetSpec:
    view_name: str
    data_path: Path
    content_path: Path
    weight: int
    hidden_fields: tuple = ()
    slug: str = ""
    shortlink: str = ""
    field_labels: tuple = ()


FIELD_TYPES = {
    1: "text",
    4: "date",
    5: "checkbox",
    8: "url",
    9: "multi_select",
    23: "user",
}
SHANGHAI_TZ = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_ID = "DUXJLSnZoTVFhVUVs"
DEFAULT_SOURCE_URL = f"https://docs.qq.com/smartsheet/{DOCUMENT_ID}?tab=sc_K49vrh"
DATASETS = (
    DatasetSpec(
        "每日更新",
        ROOT / "data" / "jobs" / "daily-updates.json",
        ROOT / "content" / "docs" / "jobs" / "每日更新.md",
        1,
        slug="daily-updates",
        shortlink="553e",
    ),
    DatasetSpec(
        "秋招提前批（内推）",
        ROOT / "data" / "jobs" / "early-recruitment.json",
        ROOT / "content" / "docs" / "jobs" / "秋招提前批.md",
        2,
        hidden_fields=("内推码", "对接人"),
        slug="early-recruitment",
        shortlink="9qrj",
        field_labels=(("内推链接", "投递链接"),),
    ),
)


def validate_snapshot(snapshot):
    metadata = snapshot.get("snapshot", {})
    if metadata.get("pagination_complete") is not True:
        raise IntegrityError("源数据分页未完整结束")
    record_count = len(snapshot.get("records", []))
    if metadata.get("source_total") != record_count or metadata.get("fetched_count") != record_count:
        raise IntegrityError("源端总量、抓取记录数与唯一记录数不一致")
    record_ids = [record.get("record_id") for record in snapshot["records"]]
    if any(not record_id for record_id in record_ids) or len(record_ids) != len(set(record_ids)):
        raise IntegrityError("record_id 缺失或重复")
    schema_ids = [field.get("field_id") for field in snapshot.get("schema", [])]
    if any(not field_id for field_id in schema_ids) or len(schema_ids) != len(set(schema_ids)):
        raise IntegrityError("schema field_id 缺失或重复")
    known_fields = set(schema_ids)
    for record in snapshot["records"]:
        record_field_ids = [field.get("field_id") for field in record.get("fields", [])]
        if (
            any(field_id not in known_fields for field_id in record_field_ids)
            or len(record_field_ids) != len(set(record_field_ids))
        ):
            raise IntegrityError(f"记录 {record['record_id']} 的 field_id 缺失、重复或不在视图 schema 中")


def _scan_fingerprint(snapshot):
    records = []
    for record in snapshot.get("records", []):
        fields = []
        for field in record.get("fields", []):
            links = field.get("links", [])
            fields.append(
                {
                    "field_id": field.get("field_id"),
                    "value": field.get("value"),
                    "raw_value": field.get("raw_value"),
                    "links": links,
                }
            )
        records.append(
            {
                "record_id": record.get("record_id"),
                "fields": sorted(fields, key=lambda field: field.get("field_id", "")),
            }
        )
    metadata = snapshot.get("snapshot", {})
    canonical = {
        "source": snapshot.get("source", {}),
        "schema": sorted(
            snapshot.get("schema", []),
            key=lambda field: (field.get("order", 0), field.get("field_id", "")),
        ),
        "snapshot": {
            "source_total": metadata.get("source_total"),
            "fetched_count": metadata.get("fetched_count"),
            "pagination_complete": metadata.get("pagination_complete"),
        },
        "records": records,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def assert_matching_scans(first, second):
    validate_snapshot(first)
    validate_snapshot(second)
    if _scan_fingerprint(first) != _scan_fingerprint(second):
        raise IntegrityError("两次全量读取结果不一致")


def _decode_sheet_operations(payload):
    try:
        attributed = payload["data"]["initialAttributedText"]["text"]
        if len(attributed) != 1:
            raise ValueError
        encoded = attributed[0]["smartsheet"]
        compressed = base64.b64decode(encoded + "=" * (-len(encoded) % 4))
        decoded = json.loads(zlib.decompress(compressed).decode("utf-8"))
    except (KeyError, TypeError, ValueError, UnicodeError, zlib.error, json.JSONDecodeError) as error:
        raise IntegrityError("腾讯文档 smartsheet 响应编码无法解析") from error
    if not isinstance(decoded, list) or len(decoded) != 1 or not isinstance(decoded[0], list):
        raise IntegrityError("腾讯文档 smartsheet 操作结构发生变化")
    return attributed[0], decoded[0]


def _workbook_from_payload(payload):
    try:
        attributed = payload["data"]["initialAttributedText"]["text"]
        if len(attributed) != 1 or "workbook" not in attributed[0]:
            return None
        workbook = json.loads(attributed[0]["workbook"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise IntegrityError("workbook 元数据无法解析") from error
    if not isinstance(workbook, list):
        raise IntegrityError("workbook 视图清单结构无效")
    return workbook


def _extract_structured_links(value):
    links = []

    def visit(item):
        if isinstance(item, dict):
            if item.get("k1") == "url" and isinstance(item.get("k3"), str):
                links.append({"text": str(item.get("k2") or item["k3"]), "url": item["k3"]})
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    unique = []
    seen = set()
    for link in links:
        marker = (link["text"], link["url"])
        if marker not in seen:
            seen.add(marker)
            unique.append(link)
    return unique


def _cell_value(cell, field_type, option_names):
    raw_value = None
    if field_type == 1:
        value = "".join(
            str(segment.get("k2", ""))
            for segment in cell.get("k1", [])
            if isinstance(segment, dict)
        )
    elif field_type == 4:
        raw_value = cell.get("k4", "")
        try:
            value = datetime.fromtimestamp(int(raw_value) / 1000, tz=SHANGHAI_TZ).strftime("%Y-%m-%d")
        except (TypeError, ValueError, OSError, OverflowError):
            value = str(raw_value)
    elif field_type == 8:
        value = "\n".join(
            str(item.get("k2") or item.get("k3") or "")
            for item in cell.get("k8", [])
            if isinstance(item, dict)
        )
    elif field_type == 9:
        raw_value = [str(option_id) for option_id in cell.get("k9", [])]
        value = [option_names.get(option_id, option_id) for option_id in raw_value]
    elif field_type == 23:
        value = [
            str(user.get("k2") or user.get("k1") or "")
            for user in cell.get("k23", [])
            if isinstance(user, dict)
        ]
    else:
        value = {
            key: child for key, child in cell.items() if key not in {"k30", "k31", "k32"}
        }
    return value, raw_value


def parse_sheet_pages(view_name, payloads, source_url, document_id):
    if not payloads:
        raise IntegrityError(f"视图 {view_name} 没有返回结构化分页数据")

    sheet_id = None
    view_id = None
    revision = None
    total = None
    max_columns = None
    ranges = []
    workbook = None
    field_definitions = None
    field_order = None
    row_order = None
    raw_records = {}

    for payload in payloads:
        if payload.get("retcode") != 0:
            raise IntegrityError("腾讯文档 get/sheet 返回非零 retcode")
        data = payload.get("data", {})
        values = (data.get("sheetId"), data.get("viewID"), data.get("rev"), data.get("maxrow"), data.get("maxcol"))
        if sheet_id is None:
            sheet_id, view_id, revision, total, max_columns = values
        elif values != (sheet_id, view_id, revision, total, max_columns):
            raise IntegrityError("分页之间的 sheet/view/revision/总量不一致")
        start = data.get("startrow")
        end = data.get("endrow")
        if not isinstance(start, int) or not isinstance(end, int):
            raise IntegrityError("分页缺少稳定的起止行号")
        ranges.append((start, end))

        attributed, operations = _decode_sheet_operations(payload)
        if "workbook" in attributed:
            try:
                candidate = json.loads(attributed["workbook"])
            except (TypeError, json.JSONDecodeError) as error:
                raise IntegrityError("workbook 元数据无法解析") from error
            if workbook is None:
                workbook = candidate
            elif workbook != candidate:
                raise IntegrityError("分页之间的 workbook 元数据不一致")

        for operation in operations:
            if operation.get("c", {}).get("k1") != sheet_id:
                raise IntegrityError("smartsheet 操作绑定到了错误的 sheetId")
            if operation.get("t") == 3005:
                model = operation.get("c", {}).get("k3", {})
                definitions = model.get("k3")
                views = model.get("k4", [])
                if not isinstance(definitions, dict) or not views:
                    raise IntegrityError("缺少字段 schema 或行顺序元数据")
                candidate_view = views[0].get("k1", {})
                candidate_rows = candidate_view.get("k1")
                candidate_fields = candidate_view.get("k2")
                if not isinstance(candidate_rows, list) or not isinstance(candidate_fields, list):
                    raise IntegrityError("视图缺少稳定的记录 ID 或字段 ID 顺序")
                if field_definitions is not None and (
                    field_definitions != definitions
                    or field_order != candidate_fields
                    or row_order != candidate_rows
                ):
                    raise IntegrityError("分页之间的 schema 或记录顺序不一致")
                field_definitions = definitions
                field_order = candidate_fields
                row_order = candidate_rows
            elif operation.get("t") == 3028:
                records = operation.get("c", {}).get("k2", {}).get("k1")
                if not isinstance(records, dict):
                    raise IntegrityError("记录操作缺少 record_id 映射")
                duplicates = set(raw_records).intersection(records)
                if duplicates:
                    raise IntegrityError(f"分页返回重复 record_id：{sorted(duplicates)[0]}")
                raw_records.update(records)

    if not sheet_id or not view_id or not isinstance(total, int) or total < 0:
        raise IntegrityError("sheetId、viewID 或源端总量缺失")
    sorted_ranges = sorted(ranges)
    expected_start = 0
    for start, end in sorted_ranges:
        if start != expected_start or end < start:
            raise IntegrityError("分页范围存在缺口、重叠或倒序")
        expected_start = end + 1
    if expected_start != total:
        raise IntegrityError("分页范围未覆盖源端总量")
    if not isinstance(workbook, list):
        raise IntegrityError("缺少 workbook 视图清单")
    matches = [item for item in workbook if item.get("name") == view_name]
    if len(matches) != 1 or matches[0].get("id") != sheet_id:
        raise IntegrityError(f"workbook 中无法唯一定位视图：{view_name}")
    if field_definitions is None or field_order is None or row_order is None:
        raise IntegrityError("完整分页中缺少 schema 元数据")
    if len(row_order) != total or set(row_order) != set(raw_records):
        raise IntegrityError("记录 ID 清单、分页记录和源端总量不一致")

    schema = []
    option_maps = {}
    for order, field_id in enumerate(field_order):
        definition = field_definitions.get(field_id)
        if not isinstance(definition, dict):
            raise IntegrityError(f"字段 ID 不在 schema 中：{field_id}")
        type_code = definition.get("k31")
        options = definition.get("k9", {}).get("k3", []) if type_code == 9 else []
        option_map = {
            str(option.get("k1")): str(option.get("k2", option.get("k1")))
            for option in options
            if isinstance(option, dict) and option.get("k1") is not None
        }
        option_maps[field_id] = option_map
        schema.append(
            {
                "field_id": field_id,
                "name": str(definition.get("k30") or field_id),
                "type": FIELD_TYPES.get(type_code, f"type_{type_code}"),
                "type_code": type_code,
                "order": order,
                "options": [{"id": key, "name": value} for key, value in option_map.items()],
            }
        )

    records = []
    for record_id in row_order:
        cells = raw_records[record_id].get("k1", {})
        if not isinstance(cells, dict):
            raise IntegrityError(f"记录 {record_id} 缺少字段映射")
        fields = []
        for field_id in field_order:
            cell = cells.get(field_id, {})
            if not isinstance(cell, dict):
                raise IntegrityError(f"记录 {record_id} 的字段 {field_id} 结构无效")
            type_code = field_definitions[field_id].get("k31")
            value, raw_value = _cell_value(cell, type_code, option_maps[field_id])
            field = {
                "field_id": field_id,
                "value": value,
                "links": _extract_structured_links(cell),
            }
            if raw_value is not None:
                field["raw_value"] = raw_value
            fields.append(field)
        records.append({"record_id": record_id, "fields": fields})

    snapshot = {
        "source": {
            "document_id": document_id,
            "source_url": source_url,
            "sheet_id": sheet_id,
            "view_id": view_id,
            "view_name": view_name,
            "revision": revision,
        },
        "schema": schema,
        "snapshot": {
            "source_total": total,
            "fetched_count": len(records),
            "pagination_complete": True,
            "page_ranges": [[start, end] for start, end in sorted_ranges],
            "max_columns": max_columns,
        },
        "records": records,
    }
    validate_snapshot(snapshot)
    return snapshot


def _url_with_tab(source_url, tab):
    parsed = urlsplit(source_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["tab"] = tab
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _deduplicate_pages(payloads, sheet_id):
    pages = {}
    for payload in payloads:
        data = payload.get("data", {})
        if data.get("sheetId") != sheet_id:
            continue
        key = (data.get("startrow"), data.get("endrow"), data.get("rev"))
        encoded = data.get("initialAttributedText", {}).get("text", [{}])[0].get("smartsheet")
        if key in pages and pages[key].get("data", {}).get("initialAttributedText") != data.get("initialAttributedText"):
            raise IntegrityError("同一分页范围返回了不同响应")
        if encoded:
            pages[key] = payload
    return list(pages.values())


def _ranges_complete(payloads, sheet_id):
    pages = _deduplicate_pages(payloads, sheet_id)
    if not pages:
        return False
    totals = {payload.get("data", {}).get("maxrow") for payload in pages}
    if len(totals) != 1 or not isinstance(next(iter(totals)), int):
        return False
    total = next(iter(totals))
    ranges = sorted(
        (payload["data"].get("startrow"), payload["data"].get("endrow"))
        for payload in pages
    )
    expected = 0
    for start, end in ranges:
        if not isinstance(start, int) or not isinstance(end, int) or start != expected or end < start:
            return False
        expected = end + 1
    return expected == total


class QQDocsSource:
    def __init__(
        self,
        source_url,
        storage_state,
        *,
        browser_channel=None,
        headless=True,
        timeout_seconds=90,
    ):
        self.source_url = source_url
        self.storage_state = Path(storage_state)
        self.browser_channel = browser_channel
        self.headless = headless
        self.timeout_seconds = timeout_seconds

    async def collect(self, specs):
        if not self.storage_state.is_file():
            raise IntegrityError("storage state 文件不存在")
        try:
            from playwright.async_api import async_playwright
        except ImportError as error:
            raise RuntimeError("缺少 Playwright，请先安装 playwright 并安装 Chromium") from error

        captures = []
        response_tasks = set()

        async def capture(response):
            if urlsplit(response.url).path != "/dop-api/get/sheet" or response.status != 200:
                return
            try:
                payload = await response.json()
            except Exception:
                return
            if isinstance(payload, dict):
                captures.append(payload)

        def schedule_capture(response):
            task = asyncio.create_task(capture(response))
            response_tasks.add(task)
            task.add_done_callback(response_tasks.discard)

        async with async_playwright() as playwright:
            launch_options = {"headless": self.headless}
            if self.browser_channel:
                launch_options["channel"] = self.browser_channel
            browser = await playwright.chromium.launch(**launch_options)
            try:
                context = await browser.new_context(storage_state=str(self.storage_state))
                page = await context.new_page()
                page.on("response", schedule_capture)
                page.set_default_timeout(self.timeout_seconds * 1000)
                await page.goto(
                    self.source_url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout_seconds * 1000,
                )
                workbook = await self._wait_for_workbook(page, captures)
                target_sheets = {}
                for spec in specs:
                    matches = [item for item in workbook if item.get("name") == spec.view_name]
                    if len(matches) != 1 or not matches[0].get("id"):
                        raise IntegrityError(f"workbook 中无法唯一定位视图：{spec.view_name}")
                    target_sheets[spec.view_name] = matches[0]["id"]

                grace_deadline = time.monotonic() + min(30, self.timeout_seconds / 2)
                while time.monotonic() < grace_deadline:
                    if all(_ranges_complete(captures, sheet_id) for sheet_id in target_sheets.values()):
                        break
                    await page.wait_for_timeout(250)

                for sheet_id in target_sheets.values():
                    if not _ranges_complete(captures, sheet_id):
                        await page.goto(
                            _url_with_tab(self.source_url, sheet_id),
                            wait_until="domcontentloaded",
                            timeout=self.timeout_seconds * 1000,
                        )
                    await self._wait_for_pages(page, captures, sheet_id, encourage_loading=True)

                if response_tasks:
                    await asyncio.gather(*tuple(response_tasks), return_exceptions=True)
                snapshots = {}
                for spec in specs:
                    sheet_id = target_sheets[spec.view_name]
                    pages = _deduplicate_pages(captures, sheet_id)
                    snapshots[spec.view_name] = parse_sheet_pages(
                        spec.view_name,
                        pages,
                        source_url=_url_with_tab(self.source_url, sheet_id),
                        document_id=DOCUMENT_ID,
                    )
                return snapshots
            finally:
                await browser.close()

    async def _wait_for_workbook(self, page, captures):
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            for payload in captures:
                workbook = _workbook_from_payload(payload)
                if workbook is not None:
                    return workbook
            await page.wait_for_timeout(250)
        title = await page.title()
        if "登录" in title or "安全" in title:
            raise IntegrityError("腾讯文档会话失效或触发安全拦截")
        raise IntegrityError("未收到腾讯文档 workbook 结构化响应")

    async def _wait_for_pages(self, page, captures, sheet_id, encourage_loading=False):
        deadline = time.monotonic() + self.timeout_seconds
        next_scroll = 0
        while time.monotonic() < deadline:
            if _ranges_complete(captures, sheet_id):
                return
            if encourage_loading and time.monotonic() >= next_scroll:
                await page.mouse.wheel(0, 100000)
                await page.keyboard.press("End")
                await page.evaluate(
                    """() => {
                        for (const element of document.querySelectorAll('*')) {
                            if (element.scrollHeight > element.clientHeight) {
                                element.scrollTop = element.scrollHeight;
                            }
                        }
                    }"""
                )
                next_scroll = time.monotonic() + 2
            await page.wait_for_timeout(250)
        raise IntegrityError(f"sheet {sheet_id} 的分页未完整返回")


def merge_history(previous, current, now, accept_source_deletions=False):
    validate_snapshot(current)
    previous_by_id = {
        record["record_id"]: record for record in previous.get("records", [])
    }
    current_ids = {record["record_id"] for record in current["records"]}
    missing_ids = sorted(
        record["record_id"]
        for record in previous.get("records", [])
        if record.get("status", "active") == "active" and record["record_id"] not in current_ids
    )
    removed_history = [
        deepcopy(record)
        for record in previous.get("records", [])
        if record.get("status") == "source_removed" and record["record_id"] not in current_ids
    ]
    if missing_ids and not accept_source_deletions:
        raise SourceDeletionError(f"源记录消失，需人工确认：{', '.join(missing_ids)}")
    merged = deepcopy(current)
    for record in merged["records"]:
        previous_record = previous_by_id.get(record["record_id"], {})
        record["status"] = "active"
        record["first_seen_at"] = previous_record.get("first_seen_at", now)
        record["last_seen_at"] = now
        record["removed_at"] = None
    merged["records"].extend(removed_history)
    if accept_source_deletions:
        for record_id in missing_ids:
            removed = deepcopy(previous_by_id[record_id])
            removed["status"] = "source_removed"
            removed["removed_at"] = now
            merged["records"].append(removed)
    return merged


def _plain_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            return "、".join(str(item) for item in value)
        if not value:
            return ""
    if isinstance(value, dict) and not value:
        return ""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _safe_html_text(value):
    return (
        html.escape(str(value), quote=False)
        .replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("\r\n", "<br>")
        .replace("\r", "<br>")
        .replace("\n", "<br>")
    )


def _anchor(url, text):
    escaped_url = (
        html.escape(url, quote=True)
        .replace("\t", "&#9;")
        .replace("\n", "&#10;")
        .replace("\r", "&#13;")
    )
    return f'<a href="{escaped_url}">{_safe_html_text(text)}</a>'


def _render_table_cell(field):
    links = field.get("links", [])
    if links:
        return "<br>".join(
            _anchor(link["url"], str(link.get("text") or link["url"]))
            for link in links
        )
    return _safe_html_text(_plain_text(field.get("value")))


def _field_is_hidden(name, hidden_fields):
    return any(name == hidden or name.startswith(f"{hidden}（") for hidden in hidden_fields)


def _visible_schema(snapshot, hidden_fields):
    return [
        field
        for field in sorted(
            snapshot.get("schema", []),
            key=lambda item: (item.get("order", 0), item.get("field_id", "")),
        )
        if not _field_is_hidden(field.get("name", ""), hidden_fields)
    ]


def _records_for_display(snapshot, schema):
    records = snapshot.get("records", [])
    date_field_id = next(
        (field.get("field_id") for field in schema if field.get("name") == "更新日期"),
        None,
    )
    if not date_field_id:
        return records

    def date_key(record):
        value = next(
            (
                field.get("value")
                for field in record.get("fields", [])
                if field.get("field_id") == date_field_id
            ),
            "",
        )
        date_value = _plain_text(value)
        return bool(date_value), date_value

    return sorted(records, key=date_key, reverse=True)


def render_markdown(title, weight, snapshot, hidden_fields=(), field_labels=(), slug="", shortlink=""):
    metadata = snapshot.get("snapshot", {})
    schema = _visible_schema(snapshot, hidden_fields)
    display_labels = dict(field_labels)
    lines = [
        "---",
        f'title: "{title}"',
        f"weight: {weight}",
        "type: docs",
        "---",
        "",
        f"# {title}",
        "",
    ]
    if slug:
        lines.insert(2, f'slug: "{slug}"')
    if shortlink:
        type_index = lines.index("type: docs")
        lines[type_index:type_index] = ["aliases:", f'  - "/s/{shortlink}/"', f'shortlink: "{shortlink}"']
    if metadata.get("synced_at"):
        lines.append(f"最后成功同步：{html.escape(str(metadata['synced_at']), quote=False)}")
        lines.append("")

    records = _records_for_display(snapshot, schema)
    if not records:
        lines.extend(["当前暂无记录。", ""])
        return "\n".join(lines)

    page_size = 15
    page_count = (len(records) + page_size - 1) // page_size
    lines.extend([
        f'<div class="job-list" data-job-list data-page-size="{page_size}" data-page-count="{page_count}">',
        f'<div class="job-table-scroll" tabindex="0" role="region" aria-label="{_safe_html_text(title)}招聘信息表格，可横向滚动">',
        '<table class="job-table">', "<thead>", "<tr>"])
    for definition in schema:
        name = definition.get("name") or definition.get("field_id") or "未命名字段"
        name = display_labels.get(name, name)
        lines.append(f'<th scope="col">{_safe_html_text(name)}</th>')
    lines.extend(["</tr>", "</thead>", "<tbody>"])
    for record_index, record in enumerate(records):
        page_number = record_index // page_size + 1
        hidden = " hidden" if page_number > 1 else ""
        fields = {field.get("field_id"): field for field in record.get("fields", [])}
        lines.append(f'<tr data-job-page="{page_number}"{hidden}>')
        for column_index, definition in enumerate(schema):
            field = fields.get(definition.get("field_id"), {})
            value = _render_table_cell(field)
            if column_index == 0 and record.get("status") == "source_removed":
                value = f"{value}<br><small>源表已移除</small>"
            lines.append(f"<td>{value}</td>")
        lines.extend(["</tr>"])
    lines.extend(
        [
            "</tbody>",
            "</table>",
            "</div>",
        ]
    )
    if page_count > 1:
        lines.extend(
            [
                '<nav class="job-pagination" aria-label="招聘信息分页">',
                '<button type="button" data-job-page-action="first" aria-label="首页" title="首页" disabled>&laquo;</button>',
                '<button type="button" data-job-page-action="previous" aria-label="上一页" title="上一页" disabled>&lsaquo;</button>',
                f'<span class="job-pagination-status" data-job-page-status aria-live="polite">第 1 / {page_count} 页</span>',
                '<button type="button" data-job-page-action="next" aria-label="下一页" title="下一页">&rsaquo;</button>',
                '<button type="button" data-job-page-action="last" aria-label="末页" title="末页">&raquo;</button>',
                "</nav>",
            ]
        )
    lines.append("</div>")
    if page_count > 1:
        lines.extend(
            [
                "<script>",
                "(() => {",
                "  const root = document.currentScript.previousElementSibling;",
                "  const pageCount = Number(root.dataset.pageCount);",
                "  let currentPage = 1;",
                '  const rows = root.querySelectorAll("[data-job-page]");',
                '  const status = root.querySelector("[data-job-page-status]");',
                '  const buttons = root.querySelectorAll("[data-job-page-action]");',
                '  const scroll = root.querySelector(".job-table-scroll");',
                "  const showPage = (page, moveToTop = true) => {",
                "    currentPage = Math.min(pageCount, Math.max(1, page));",
                "    rows.forEach((row) => { row.hidden = Number(row.dataset.jobPage) !== currentPage; });",
                "    status.textContent = `第 ${currentPage} / ${pageCount} 页`;",
                "    buttons.forEach((button) => {",
                "      const action = button.dataset.jobPageAction;",
                '      button.disabled = (["first", "previous"].includes(action) && currentPage === 1)',
                '        || (["next", "last"].includes(action) && currentPage === pageCount);',
                "    });",
                "    scroll.scrollLeft = 0;",
                '    if (moveToTop) root.scrollIntoView({ behavior: "auto", block: "start" });',
                "  };",
                '  root.addEventListener("click", (event) => {',
                '    const button = event.target.closest("[data-job-page-action]");',
                "    if (!button || button.disabled) {",
                "      return;",
                "    }",
                "    const action = button.dataset.jobPageAction;",
                '    if (action === "first") showPage(1);',
                '    else if (action === "previous") showPage(currentPage - 1);',
                '    else if (action === "next") showPage(currentPage + 1);',
                '    else if (action === "last") showPage(pageCount);',
                "  });",
                "  showPage(1, false);",
                "})();",
                "</script>",
            ]
        )
    lines.append("")
    return "\n".join(lines)


class _RenderedLinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and "href" in dict(attrs):
            self.links.append(dict(attrs)["href"])


def _assert_rendered_links(snapshot, markdown, hidden_fields=()):
    expected = []
    schema = _visible_schema(snapshot, hidden_fields)
    for record in _records_for_display(snapshot, schema):
        fields = {field.get("field_id"): field for field in record.get("fields", [])}
        for definition in schema:
            expected.extend(
                link["url"]
                for link in fields.get(definition.get("field_id"), {}).get("links", [])
            )
    collector = _RenderedLinkCollector()
    collector.feed(markdown)
    if collector.links != expected:
        raise IntegrityError("生成页面的链接与快照原始链接不一致")


def _sha256_lines(values):
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def _previous_links_by_key(previous):
    return {
        link["key"]: link
        for record in previous.get("records", [])
        for field in record.get("fields", [])
        for link in field.get("links", [])
        if isinstance(link.get("key"), str)
    }


class _HeadRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        redirected = super().redirect_request(
            request,
            file_pointer,
            code,
            message,
            headers,
            new_url,
        )
        if redirected is not None and request.get_method() == "HEAD":
            redirected.method = "HEAD"
        return redirected


def _enrich_snapshot(snapshot, now, scan_hash, previous=None):
    enriched = deepcopy(snapshot)
    previous_links = _previous_links_by_key(previous or {})
    link_bindings = []
    active_record_ids = []
    view_id = enriched["source"]["view_id"]
    for record in enriched["records"]:
        if record.get("status") != "source_removed":
            active_record_ids.append(record["record_id"])
        for field in record.get("fields", []):
            unique_links = []
            seen_keys = set()
            for link in field.get("links", []):
                url = link.get("url")
                if not isinstance(url, str) or not url.lower().startswith(("http://", "https://")):
                    raise IntegrityError("招聘链接必须是完整的 HTTP 或 HTTPS URL")
                binding = [view_id, record["record_id"], field["field_id"], url]
                key = hashlib.sha256(
                    json.dumps(binding, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                stored_link = deepcopy(link)
                stored_link["key"] = key
                previous_link = previous_links.get(key, {})
                if (
                    previous_link.get("url") == stored_link.get("url")
                    and previous_link.get("text") == stored_link.get("text")
                    and isinstance(previous_link.get("availability"), dict)
                ):
                    stored_link["availability"] = deepcopy(previous_link["availability"])
                unique_links.append(stored_link)
                if record.get("status") != "source_removed":
                    link_bindings.append(json.dumps(binding, ensure_ascii=False, separators=(",", ":")))
            field["links"] = unique_links
    metadata = enriched.setdefault("snapshot", {})
    metadata.update(
        {
            "synced_at": now,
            "active_count": len(active_record_ids),
            "historical_count": len(enriched["records"]),
            "record_id_hash": _sha256_lines(sorted(active_record_ids)),
            "link_hash": _sha256_lines(sorted(link_bindings)),
            "scan_hash": scan_hash,
        }
    )
    return enriched


def _check_one_link(url, now, timeout_seconds):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (compatible; GoClubLinkChecker/1.0)",
    }
    opener = build_opener(_HeadRedirectHandler())
    try:
        try:
            response = opener.open(
                Request(url, headers=headers, method="HEAD"),
                timeout=timeout_seconds,
            )
        except HTTPError as error:
            if error.code not in (405, 501):
                raise
            get_headers = {**headers, "Range": "bytes=0-0"}
            response = opener.open(
                Request(url, headers=get_headers, method="GET"),
                timeout=timeout_seconds,
            )
        with response:
            status_code = response.getcode()
        return {
            "checked_at": now,
            "result": "reachable",
            "status_code": status_code,
            "error_category": None,
        }
    except HTTPError as error:
        return {
            "checked_at": now,
            "result": "unreachable",
            "status_code": error.code,
            "error_category": "http_error",
        }
    except (TimeoutError, socket.timeout):
        category = "timeout"
    except URLError as error:
        reason = error.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            category = "timeout"
        elif isinstance(reason, ssl.SSLError):
            category = "tls_error"
        elif isinstance(reason, socket.gaierror):
            category = "dns_error"
        else:
            category = "connection_error"
    except (http.client.HTTPException, OSError, ValueError):
        category = "request_error"
    return {
        "checked_at": now,
        "result": "unknown",
        "status_code": None,
        "error_category": category,
    }


def check_link_accessibility(snapshot, now, max_workers=12, timeout_seconds=5):
    pending = [
        link
        for record in snapshot.get("records", [])
        if record.get("status", "active") == "active"
        for field in record.get("fields", [])
        for link in field.get("links", [])
        if not isinstance(link.get("availability"), dict)
    ]
    if not pending:
        return 0
    worker_count = max(1, min(max_workers, len(pending)))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = executor.map(
            lambda link: _check_one_link(link["url"], now, timeout_seconds),
            pending,
        )
        for link, availability in zip(pending, results):
            link["availability"] = availability
    return len(pending)


def _load_previous(path):
    if not path.exists():
        return {"records": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise IntegrityError(f"现有快照无法读取：{path}") from error


def _stage_bytes(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _replace_outputs(outputs):
    staged = []
    originals = {}
    replaced = []
    try:
        for path, content in outputs:
            originals[path] = path.read_bytes() if path.exists() else None
            staged.append((path, _stage_bytes(path, content)))
        for path, temporary in staged:
            os.replace(temporary, path)
            replaced.append(path)
    except BaseException:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                rollback = _stage_bytes(path, original)
                os.replace(rollback, path)
        raise
    finally:
        for _, temporary in staged:
            temporary.unlink(missing_ok=True)


def _prepare_dataset(
    spec,
    first_scan,
    second_scan,
    now,
    accept_source_deletions=False,
    check_links=False,
):
    assert_matching_scans(first_scan, second_scan)
    if first_scan.get("source", {}).get("view_name") != spec.view_name:
        raise IntegrityError(f"缺少目标视图：{spec.view_name}")
    scan_hash = _scan_fingerprint(first_scan)
    previous = _load_previous(spec.data_path)
    if previous.get("snapshot", {}).get("scan_hash") == scan_hash:
        enriched = deepcopy(previous)
    else:
        merged = merge_history(
            previous,
            first_scan,
            now=now,
            accept_source_deletions=accept_source_deletions,
        )
        enriched = _enrich_snapshot(merged, now, scan_hash, previous=previous)
    if check_links:
        check_link_accessibility(enriched, now)
    data_bytes = (
        json.dumps(enriched, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    markdown = render_markdown(
        spec.content_path.stem,
        spec.weight,
        enriched,
        hidden_fields=spec.hidden_fields,
        field_labels=spec.field_labels,
        slug=spec.slug,
        shortlink=spec.shortlink,
    )
    _assert_rendered_links(enriched, markdown, hidden_fields=spec.hidden_fields)
    content_bytes = markdown.encode("utf-8")
    outputs = [(spec.data_path, data_bytes), (spec.content_path, content_bytes)]
    changed_outputs = [
        (path, content)
        for path, content in outputs
        if not path.exists() or path.read_bytes() != content
    ]
    return changed_outputs, enriched


def sync_dataset(
    spec,
    first_scan,
    second_scan,
    now,
    accept_source_deletions=False,
    check_links=False,
):
    outputs, _ = _prepare_dataset(
        spec,
        first_scan,
        second_scan,
        now,
        accept_source_deletions=accept_source_deletions,
        check_links=check_links,
    )
    if not outputs:
        return False
    _replace_outputs(outputs)
    return True


def sync_datasets(
    specs,
    first_scans,
    second_scans,
    now,
    accept_source_deletions=False,
    check_links=False,
):
    outputs = []
    changed = []
    for spec in specs:
        dataset_outputs, _ = _prepare_dataset(
            spec,
            first_scans[spec.view_name],
            second_scans[spec.view_name],
            now,
            accept_source_deletions=accept_source_deletions,
            check_links=check_links,
        )
        if dataset_outputs:
            outputs.extend(dataset_outputs)
            changed.append(spec.view_name)
    if outputs:
        _replace_outputs(outputs)
    return changed


def _configured_specs(data_dir, content_dir):
    data_dir = Path(data_dir)
    content_dir = Path(content_dir)
    return tuple(
        DatasetSpec(
            spec.view_name,
            data_dir / spec.data_path.name,
            content_dir / spec.content_path.name,
            spec.weight,
            hidden_fields=spec.hidden_fields,
            slug=spec.slug,
            shortlink=spec.shortlink,
            field_labels=spec.field_labels,
        )
        for spec in DATASETS
    )


def build_parser():
    parser = argparse.ArgumentParser(description="同步腾讯文档招聘信息到 GoClub")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--storage-state", required=True)
    parser.add_argument("--data-dir", default=ROOT / "data" / "jobs")
    parser.add_argument("--content-dir", default=ROOT / "content" / "docs" / "jobs")
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--check-links", action="store_true")
    parser.add_argument("--accept-source-deletions", action="store_true")
    parser.add_argument("--browser-channel")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    return parser


async def _collect_twice(source, specs):
    first = await source.collect(specs)
    second = await source.collect(specs)
    return first, second


def _probe_summary(spec, snapshot):
    links = [
        link["url"]
        for record in snapshot["records"]
        for field in record["fields"]
        for link in field.get("links", [])
    ]
    return {
        "page": spec.content_path.stem,
        "source_view": spec.view_name,
        "sheet_id": snapshot["source"]["sheet_id"],
        "view_id": snapshot["source"]["view_id"],
        "records": len(snapshot["records"]),
        "fields": len(snapshot["schema"]),
        "links": len(links),
        "page_ranges": snapshot["snapshot"]["page_ranges"],
        "scan_hash": _scan_fingerprint(snapshot),
    }


def main(argv=None):
    arguments = build_parser().parse_args(argv)
    if arguments.timeout_seconds < 10:
        print("同步失败：timeout-seconds 不能小于 10", file=sys.stderr)
        return 2
    specs = _configured_specs(arguments.data_dir, arguments.content_dir)
    source = QQDocsSource(
        arguments.source_url,
        arguments.storage_state,
        browser_channel=arguments.browser_channel,
        headless=not arguments.headed,
        timeout_seconds=arguments.timeout_seconds,
    )
    try:
        first, second = asyncio.run(_collect_twice(source, specs))
        for spec in specs:
            assert_matching_scans(first[spec.view_name], second[spec.view_name])
        if arguments.probe_only:
            summaries = [_probe_summary(spec, first[spec.view_name]) for spec in specs]
            print(json.dumps(summaries, ensure_ascii=False, indent=2))
            return 0
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        changed = sync_datasets(
            specs,
            first,
            second,
            now,
            accept_source_deletions=arguments.accept_source_deletions,
            check_links=arguments.check_links,
        )
    except (IntegrityError, OSError, UnicodeError, RuntimeError) as error:
        print(f"同步失败：{error}", file=sys.stderr)
        return 1
    if changed:
        print("已更新：" + "、".join(changed))
    else:
        print("无数据变更")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
