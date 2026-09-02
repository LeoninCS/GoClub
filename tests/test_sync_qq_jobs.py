import asyncio
import base64
import http.server
import json
import sys
import tempfile
import threading
import types
import unittest
import zlib
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_qq_jobs import (
    DatasetSpec,
    IntegrityError,
    QQDocsSource,
    _resolve_sheet_id,
    assert_matching_scans,
    check_link_accessibility,
    merge_history,
    parse_sheet_pages,
    render_markdown,
    sync_dataset,
    validate_snapshot,
)


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attributes = dict(attrs)
            if "href" in attributes:
                self.links.append(attributes["href"])


class ValidateSnapshotTests(unittest.TestCase):
    def test_rejects_incomplete_pagination(self):
        snapshot = {
            "source": {
                "document_id": "DUXJLSnZoTVFhVUVs",
                "view_id": "sc_daily",
                "view_name": "每日更新",
                "source_url": "https://docs.qq.com/smartsheet/DUXJLSnZoTVFhVUVs",
            },
            "schema": [
                {"field_id": "fld_company", "name": "公司", "type": "text", "order": 0}
            ],
            "snapshot": {
                "source_total": 1,
                "fetched_count": 1,
                "pagination_complete": False,
            },
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [{"field_id": "fld_company", "value": "示例公司", "links": []}],
                }
            ],
        }

        with self.assertRaisesRegex(IntegrityError, "分页"):
            validate_snapshot(snapshot)

    def test_rejects_record_count_mismatch(self):
        snapshot = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_company", "name": "公司", "type": "text", "order": 0}],
            "snapshot": {
                "source_total": 2,
                "fetched_count": 1,
                "pagination_complete": True,
            },
            "records": [{"record_id": "rec_1", "fields": []}],
        }

        with self.assertRaisesRegex(IntegrityError, "记录数"):
            validate_snapshot(snapshot)

    def test_rejects_duplicate_record_ids(self):
        snapshot = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_company", "name": "公司", "type": "text", "order": 0}],
            "snapshot": {
                "source_total": 2,
                "fetched_count": 2,
                "pagination_complete": True,
            },
            "records": [
                {"record_id": "rec_1", "fields": []},
                {"record_id": "rec_1", "fields": []},
            ],
        }

        with self.assertRaisesRegex(IntegrityError, "record_id"):
            validate_snapshot(snapshot)

    def test_rejects_one_character_link_difference_between_scans(self):
        first = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_apply", "name": "投递链接", "type": "url", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [
                        {
                            "field_id": "fld_apply",
                            "value": "官网投递",
                            "links": [{"text": "投递", "url": "https://jobs.example/apply?id=A0O1lI#campus"}],
                        }
                    ],
                }
            ],
        }
        second = {
            **first,
            "records": [
                {
                    **first["records"][0],
                    "fields": [
                        {
                            **first["records"][0]["fields"][0],
                            "links": [{"text": "投递", "url": "https://jobs.example/apply?id=AOO1lI#campus"}],
                        }
                    ],
                }
            ],
        }

        with self.assertRaisesRegex(IntegrityError, "两次全量读取"):
            assert_matching_scans(first, second)

    def test_rejects_record_order_difference_between_scans(self):
        first = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {"source_total": 2, "fetched_count": 2, "pagination_complete": True},
            "records": [
                {"record_id": "rec_1", "fields": []},
                {"record_id": "rec_2", "fields": []},
            ],
        }
        second = {
            **first,
            "records": [first["records"][1], first["records"][0]],
        }

        with self.assertRaisesRegex(IntegrityError, "两次全量读取"):
            assert_matching_scans(first, second)


    def test_rejects_field_id_that_is_not_in_view_schema(self):
        snapshot = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_company", "name": "公司", "type": "text", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [{"field_id": "fld_apply", "value": "错位值", "links": []}],
                }
            ],
        }

        with self.assertRaisesRegex(IntegrityError, "field_id"):
            validate_snapshot(snapshot)


class ResolveSheetTests(unittest.TestCase):
    def test_prefers_stable_sheet_id_when_source_view_is_renamed(self):
        workbook = [
            {"id": "sheet_daily", "name": "每日更新", "type": "smartsheet"},
            {"id": "sheet_early", "name": "27届秋招提前批（内推）", "type": "smartsheet"},
        ]

        self.assertEqual(
            "sheet_early",
            _resolve_sheet_id(workbook, "秋招提前批（内推）", "sheet_early"),
        )

    def test_falls_back_to_unique_view_name_without_saved_sheet_id(self):
        workbook = [
            {"id": "sheet_daily", "name": "每日更新", "type": "smartsheet"},
        ]

        self.assertEqual("sheet_daily", _resolve_sheet_id(workbook, "每日更新", None))

    def test_stable_sheet_id_disambiguates_duplicate_view_names(self):
        workbook = [
            {"id": "sheet_old", "name": "秋招提前批（内推）", "type": "smartsheet"},
            {"id": "sheet_current", "name": "秋招提前批（内推）", "type": "smartsheet"},
        ]

        self.assertEqual(
            "sheet_current",
            _resolve_sheet_id(workbook, "秋招提前批（内推）", "sheet_current"),
        )


class QQDocsSourceSessionTests(unittest.TestCase):
    def test_complete_collection_persists_refreshed_browser_session(self):
        class FakePage:
            def on(self, _event, _callback):
                pass

            def set_default_timeout(self, _timeout):
                pass

            async def goto(self, _url, **_kwargs):
                pass

        class FakeContext:
            def __init__(self):
                self.saved_path = None

            async def new_page(self):
                return FakePage()

            async def storage_state(self, *, path):
                self.saved_path = Path(path)
                self.saved_path.write_text(
                    json.dumps({"cookies": [{"name": "refreshed"}], "origins": []}),
                    encoding="utf-8",
                )

        class FakeBrowser:
            def __init__(self, context):
                self.context = context

            async def new_context(self, **_kwargs):
                return self.context

            async def close(self):
                pass

        class FakeChromium:
            def __init__(self, browser):
                self.browser = browser

            async def launch(self, **_kwargs):
                return self.browser

        class FakePlaywrightManager:
            def __init__(self, chromium):
                self.playwright = types.SimpleNamespace(chromium=chromium)

            async def __aenter__(self):
                return self.playwright

            async def __aexit__(self, *_args):
                pass

        class ImmediateSource(QQDocsSource):
            async def _wait_for_workbook(self, _page, _captures):
                return [{"id": "sheet_daily", "name": "每日更新"}]

            async def _wait_for_pages(
                self, _page, _captures, _sheet_id, encourage_loading=False
            ):
                pass

        snapshot = {
            "source": {"sheet_id": "sheet_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {
                "source_total": 0,
                "fetched_count": 0,
                "pagination_complete": True,
            },
            "records": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            storage_state = Path(directory) / "storage-state.json"
            storage_state.write_text('{"cookies": [], "origins": []}', encoding="utf-8")
            spec = DatasetSpec(
                "每日更新",
                Path(directory) / "daily.json",
                Path(directory) / "每日更新.md",
                1,
            )
            context = FakeContext()
            manager = FakePlaywrightManager(FakeChromium(FakeBrowser(context)))
            async_api = types.ModuleType("playwright.async_api")
            async_api.async_playwright = lambda: manager
            playwright_module = types.ModuleType("playwright")
            playwright_module.__path__ = []

            with patch.dict(
                sys.modules,
                {"playwright": playwright_module, "playwright.async_api": async_api},
            ), patch("sync_qq_jobs.parse_sheet_pages", return_value=snapshot):
                source = ImmediateSource(
                    "https://docs.qq.com/smartsheet/example",
                    storage_state,
                    timeout_seconds=0,
                )
                asyncio.run(source.collect((spec,)))

            self.assertEqual(storage_state, context.saved_path)
            self.assertEqual(
                "refreshed",
                json.loads(storage_state.read_text(encoding="utf-8"))["cookies"][0]["name"],
            )


class MergeHistoryTests(unittest.TestCase):
    def test_first_missing_observation_keeps_record_and_marks_pending(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "last_seen_at": "2026-08-06T00:00:00Z",
                    "removed_at": None,
                    "fields": [],
                }
            ],
        }
        current = {
            "source": previous["source"],
            "schema": [],
            "snapshot": {"source_total": 0, "fetched_count": 0, "pagination_complete": True},
            "records": [],
        }

        merged = merge_history(previous, current, now="2026-08-07T00:00:00Z")

        self.assertEqual(["rec_1"], [record["record_id"] for record in merged["records"]])
        self.assertEqual("active", merged["records"][0]["status"])
        self.assertEqual(["rec_1"], merged["snapshot"]["pending_source_deletions"])

    def test_second_consecutive_missing_observation_marks_record_removed(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {
                "source_total": 1,
                "fetched_count": 1,
                "pagination_complete": True,
                "pending_source_deletions": ["rec_1"],
            },
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "last_seen_at": "2026-08-06T00:00:00Z",
                    "removed_at": None,
                    "fields": [],
                }
            ],
        }
        current = {
            "source": previous["source"],
            "schema": [],
            "snapshot": {"source_total": 0, "fetched_count": 0, "pagination_complete": True},
            "records": [],
        }

        merged = merge_history(previous, current, now="2026-08-08T00:00:00Z")

        self.assertEqual("source_removed", merged["records"][0]["status"])
        self.assertEqual("2026-08-08T00:00:00Z", merged["records"][0]["removed_at"])
        self.assertEqual([], merged["snapshot"]["pending_source_deletions"])

    def test_returned_record_clears_pending_deletion(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {
                "source_total": 1,
                "fetched_count": 1,
                "pagination_complete": True,
                "pending_source_deletions": ["rec_1"],
            },
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "last_seen_at": "2026-08-06T00:00:00Z",
                    "removed_at": None,
                    "fields": [],
                }
            ],
        }
        current = {
            "source": previous["source"],
            "schema": [],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [{"record_id": "rec_1", "fields": []}],
        }

        merged = merge_history(previous, current, now="2026-08-08T00:00:00Z")

        self.assertEqual("active", merged["records"][0]["status"])
        self.assertEqual([], merged["snapshot"]["pending_source_deletions"])

    def test_manual_confirmation_preserves_and_marks_removed_record(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "last_seen_at": "2026-08-06T00:00:00Z",
                    "removed_at": None,
                    "fields": [],
                }
            ],
        }
        current = {
            "source": previous["source"],
            "schema": [],
            "snapshot": {"source_total": 0, "fetched_count": 0, "pagination_complete": True},
            "records": [],
        }

        merged = merge_history(
            previous,
            current,
            now="2026-08-07T00:00:00Z",
            accept_source_deletions=True,
        )

        self.assertEqual(["rec_1"], [record["record_id"] for record in merged["records"]])
        self.assertEqual("source_removed", merged["records"][0]["status"])
        self.assertEqual("2026-08-07T00:00:00Z", merged["records"][0]["removed_at"])

    def test_removed_history_survives_a_later_source_change(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_active",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "fields": [],
                },
                {
                    "record_id": "rec_removed",
                    "status": "source_removed",
                    "first_seen_at": "2026-07-01T00:00:00Z",
                    "removed_at": "2026-08-01T00:00:00Z",
                    "fields": [],
                },
            ],
        }
        current = {
            "source": previous["source"],
            "schema": [],
            "snapshot": {"source_total": 2, "fetched_count": 2, "pagination_complete": True},
            "records": [
                {"record_id": "rec_active", "fields": []},
                {"record_id": "rec_new", "fields": []},
            ],
        }

        merged = merge_history(previous, current, now="2026-08-09T00:00:00Z")

        records = {record["record_id"]: record for record in merged["records"]}
        self.assertEqual({"rec_active", "rec_new", "rec_removed"}, set(records))
        self.assertEqual("source_removed", records["rec_removed"]["status"])
        self.assertEqual("2026-08-01T00:00:00Z", records["rec_removed"]["removed_at"])

    def test_updates_existing_record_by_id_and_preserves_first_seen(self):
        previous = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_company", "name": "公司", "type": "text", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "first_seen_at": "2026-08-01T00:00:00Z",
                    "last_seen_at": "2026-08-06T00:00:00Z",
                    "removed_at": None,
                    "fields": [{"field_id": "fld_company", "value": "旧名称", "links": []}],
                }
            ],
        }
        current = {
            "source": previous["source"],
            "schema": previous["schema"],
            "snapshot": {"source_total": 2, "fetched_count": 2, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [{"field_id": "fld_company", "value": "新名称", "links": []}],
                },
                {
                    "record_id": "rec_2",
                    "fields": [{"field_id": "fld_company", "value": "第二家公司", "links": []}],
                },
            ],
        }

        merged = merge_history(previous, current, now="2026-08-07T00:00:00Z")

        records = {record["record_id"]: record for record in merged["records"]}
        self.assertEqual("新名称", records["rec_1"]["fields"][0]["value"])
        self.assertEqual("2026-08-01T00:00:00Z", records["rec_1"]["first_seen_at"])
        self.assertEqual("2026-08-07T00:00:00Z", records["rec_1"]["last_seen_at"])
        self.assertEqual("2026-08-07T00:00:00Z", records["rec_2"]["first_seen_at"])
        self.assertEqual("active", records["rec_2"]["status"])


class RenderMarkdownTests(unittest.TestCase):
    def test_renders_paginated_scrollable_table_without_source_entry(self):
        source_url = "https://docs.qq.com/smartsheet/example?tab=sc_daily"
        snapshot = {
            "source": {"source_url": source_url, "view_name": "每日更新"},
            "schema": [
                {"field_id": "company", "name": "公告标题", "type": "text", "order": 0},
                {"field_id": "date", "name": "更新日期", "type": "date", "order": 1},
            ],
            "snapshot": {"synced_at": "2026-08-09T00:00:00Z"},
            "records": [
                {
                    "record_id": f"rec_{day}",
                    "status": "active",
                    "fields": [
                        {"field_id": "company", "value": f"企业 {day}", "links": []},
                        {"field_id": "date", "value": f"2026-08-{day:02d}", "links": []},
                    ],
                }
                for day in range(1, 17)
            ],
        }

        markdown = render_markdown(
            "每日更新",
            1,
            snapshot,
            slug="daily-updates",
            shortlink="553e",
        )

        self.assertNotIn(source_url, markdown)
        self.assertIn('slug: "daily-updates"', markdown)
        self.assertIn('  - "/s/553e/"', markdown)
        self.assertIn('shortlink: "553e"', markdown)
        self.assertIn('<div class="job-table-scroll"', markdown)
        self.assertIn('data-page-size="15"', markdown)
        self.assertEqual(15, markdown.count('data-job-page="1"'))
        self.assertIn('<tr data-job-page="2" hidden>', markdown)
        self.assertIn('data-job-page-action="first"', markdown)
        self.assertIn('data-job-page-action="previous"', markdown)
        self.assertIn('data-job-page-action="next"', markdown)
        self.assertIn('data-job-page-action="last"', markdown)
        self.assertIn('第 1 / 2 页', markdown)
        script = markdown.split("<script>", 1)[1].split("</script>", 1)[0]
        self.assertNotIn("\n\n", script)

    def test_pagination_controls_show_every_page_in_browser(self):
        try:
            from playwright.sync_api import Error as PlaywrightError, sync_playwright
        except ImportError:
            self.skipTest("Playwright is not installed")
        snapshot = {
            "source": {"view_name": "每日更新"},
            "schema": [
                {"field_id": "company", "name": "公告标题", "type": "text", "order": 0}
            ],
            "snapshot": {},
            "records": [
                {
                    "record_id": f"rec_{index}",
                    "status": "active",
                    "fields": [
                        {"field_id": "company", "value": f"企业 {index}", "links": []}
                    ],
                }
                for index in range(31)
            ],
        }

        markdown = render_markdown("每日更新", 1, snapshot)

        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True)
            except PlaywrightError:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
            try:
                page = browser.new_page()
                page.set_content(markdown)

                first = page.locator('[data-job-page-action="first"]')
                previous = page.locator('[data-job-page-action="previous"]')
                next_page = page.locator('[data-job-page-action="next"]')
                last = page.locator('[data-job-page-action="last"]')
                status = page.locator("[data-job-page-status]")

                self.assertEqual(15, page.locator("tbody tr:visible").count())
                self.assertEqual("第 1 / 3 页", status.inner_text())
                self.assertTrue(first.is_disabled())
                self.assertTrue(previous.is_disabled())
                self.assertFalse(next_page.is_disabled())
                self.assertFalse(last.is_disabled())

                next_page.click()
                self.assertEqual(15, page.locator("tbody tr:visible").count())
                self.assertEqual("第 2 / 3 页", status.inner_text())
                self.assertFalse(first.is_disabled())
                self.assertFalse(previous.is_disabled())

                last.click()
                self.assertEqual(1, page.locator("tbody tr:visible").count())
                self.assertEqual("第 3 / 3 页", status.inner_text())
                self.assertTrue(next_page.is_disabled())
                self.assertTrue(last.is_disabled())

                previous.click()
                self.assertEqual("第 2 / 3 页", status.inner_text())
                first.click()
                self.assertEqual("第 1 / 3 页", status.inner_text())
            finally:
                browser.close()

    def test_renders_one_company_per_table_row_with_newest_first(self):
        snapshot = {
            "source": {"view_name": "每日更新"},
            "schema": [
                {"field_id": "fld_company", "name": "公告标题", "type": "text", "order": 0},
                {"field_id": "fld_date", "name": "更新日期", "type": "date", "order": 1},
            ],
            "snapshot": {"synced_at": "2026-08-07T00:00:00Z"},
            "records": [
                {
                    "record_id": "rec_old",
                    "status": "active",
                    "fields": [
                        {"field_id": "fld_company", "value": "较早企业", "links": []},
                        {"field_id": "fld_date", "value": "2026-08-06", "links": []},
                    ],
                },
                {
                    "record_id": "rec_new",
                    "status": "active",
                    "fields": [
                        {"field_id": "fld_company", "value": "较新企业", "links": []},
                        {"field_id": "fld_date", "value": "2026-08-07", "links": []},
                    ],
                },
            ],
        }

        markdown = render_markdown("每日更新", 1, snapshot)

        self.assertIn('<table class="job-table">', markdown)
        self.assertEqual(3, markdown.count("<tr"))
        self.assertIn('<th scope="col">公告标题</th>', markdown)
        self.assertLess(markdown.index("较新企业"), markdown.index("较早企业"))
        self.assertNotIn("<h2>", markdown)

    def test_early_recruitment_hides_referral_code_and_contact_and_renames_link(self):
        snapshot = {
            "source": {"view_name": "秋招提前批（内推）"},
            "schema": [
                {"field_id": "company", "name": "公司名称", "order": 0},
                {"field_id": "link", "name": "内推链接", "order": 1},
                {"field_id": "code", "name": "内推码（注意区分大小写）", "order": 2},
                {"field_id": "contact", "name": "对接人", "order": 3},
            ],
            "snapshot": {},
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "fields": [
                        {"field_id": "company", "value": "示例企业", "links": []},
                        {
                            "field_id": "link",
                            "value": "点击内推",
                            "links": [{"text": "点击内推", "url": "https://jobs.example/apply"}],
                        },
                        {"field_id": "code", "value": "A0O1lI", "links": []},
                        {"field_id": "contact", "value": "联系人姓名", "links": []},
                    ],
                }
            ],
        }

        markdown = render_markdown(
            "秋招提前批",
            2,
            snapshot,
            hidden_fields=("内推码", "对接人"),
            field_labels=(("内推链接", "投递链接"),),
        )

        self.assertIn('<th scope="col">投递链接</th>', markdown)
        self.assertNotIn("内推链接", markdown)
        self.assertNotIn("内推码", markdown)
        self.assertNotIn("A0O1lI", markdown)
        self.assertNotIn("对接人", markdown)
        self.assertNotIn("联系人姓名", markdown)
        self.assertIn('href="https://jobs.example/apply"', markdown)

    def test_preserves_every_raw_link_character_and_multiple_links(self):
        urls = [
            "https://jobs.example/apply?id=A0O1lI&source=campus#backend",
            "https://jobs.example/referral?token=Oo0Il1&role=Go%20Engineer",
            "https://jobs.example/instructions\r\nemail@example.com\r",
        ]
        snapshot = {
            "source": {
                "source_url": "https://docs.qq.com/smartsheet/DUXJLSnZoTVFhVUVs?tab=sc_daily",
                "view_id": "sc_daily",
                "view_name": "每日更新",
            },
            "schema": [{"field_id": "fld_apply", "name": "投递链接", "type": "url", "order": 0}],
            "snapshot": {"synced_at": "2026-08-07T00:00:00Z"},
            "records": [
                {
                    "record_id": "rec_1",
                    "status": "active",
                    "fields": [
                        {
                            "field_id": "fld_apply",
                            "value": "投递入口",
                            "links": [
                                {"text": "官网投递", "url": urls[0]},
                                {"text": "内推", "url": urls[1]},
                                {"text": "邮件投递", "url": urls[2]},
                            ],
                        }
                    ],
                }
            ],
        }

        markdown = render_markdown("每日更新", 1, snapshot)
        collector = LinkCollector()
        collector.feed(markdown)

        self.assertEqual(urls, collector.links)
        self.assertEqual(2, markdown.count("<tr"))
        self.assertIn("<td><a ", markdown)
        self.assertIn(">官网投递</a><br><a ", markdown)
        self.assertIn(">内推</a><br><a ", markdown)


class SyncDatasetTests(unittest.TestCase):
    def test_success_sorts_dated_rows_and_keeps_links_with_their_company(self):
        source_url = "https://docs.qq.com/smartsheet/example"
        scan = {
            "source": {"source_url": source_url, "view_id": "view_1", "view_name": "每日更新"},
            "schema": [
                {"field_id": "company", "name": "公告标题", "type": "text", "order": 0},
                {"field_id": "date", "name": "更新日期", "type": "date", "order": 1},
                {"field_id": "link", "name": "投递链接", "type": "url", "order": 2},
            ],
            "snapshot": {"source_total": 2, "fetched_count": 2, "pagination_complete": True},
            "records": [
                {
                    "record_id": "old",
                    "fields": [
                        {"field_id": "company", "value": "较早企业", "links": []},
                        {"field_id": "date", "value": "2026-08-06", "links": []},
                        {
                            "field_id": "link",
                            "value": "投递",
                            "links": [{"text": "投递", "url": "https://jobs.example/old"}],
                        },
                    ],
                },
                {
                    "record_id": "new",
                    "fields": [
                        {"field_id": "company", "value": "较新企业", "links": []},
                        {"field_id": "date", "value": "2026-08-07", "links": []},
                        {
                            "field_id": "link",
                            "value": "投递",
                            "links": [{"text": "投递", "url": "https://jobs.example/new"}],
                        },
                    ],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = DatasetSpec("每日更新", root / "daily.json", root / "每日更新.md", 1)

            changed = sync_dataset(spec, scan, scan, now="2026-08-07T00:00:00Z")

            self.assertTrue(changed)
            markdown = spec.content_path.read_text(encoding="utf-8")
            collector = LinkCollector()
            collector.feed(markdown)
            self.assertEqual(
                ["https://jobs.example/new", "https://jobs.example/old"],
                collector.links,
            )
            self.assertLess(markdown.index("较新企业"), markdown.index("较早企业"))

    def test_scan_mismatch_keeps_existing_outputs_byte_for_byte(self):
        first = {
            "source": {"view_id": "sc_daily", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_link", "name": "链接", "type": "url", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [
                        {
                            "field_id": "fld_link",
                            "value": "投递",
                            "links": [{"text": "投递", "url": "https://jobs.example/apply?id=0"}],
                        }
                    ],
                }
            ],
        }
        second = {
            **first,
            "records": [
                {
                    **first["records"][0],
                    "fields": [
                        {
                            **first["records"][0]["fields"][0],
                            "links": [{"text": "投递", "url": "https://jobs.example/apply?id=O"}],
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path = root / "daily.json"
            content_path = root / "每日更新.md"
            data_path.write_bytes(b"previous-json-bytes")
            content_path.write_bytes(b"previous-markdown-bytes")
            spec = DatasetSpec("每日更新", data_path, content_path, 1)

            with self.assertRaises(IntegrityError):
                sync_dataset(spec, first, second, now="2026-08-07T00:00:00Z")

            self.assertEqual(b"previous-json-bytes", data_path.read_bytes())
            self.assertEqual(b"previous-markdown-bytes", content_path.read_bytes())

    def test_success_writes_auditable_snapshot_and_page(self):
        raw_url = "https://jobs.example/apply?id=A0O1lI&source=campus#backend"
        scan = {
            "source": {
                "document_id": "DUXJLSnZoTVFhVUVs",
                "source_url": "https://docs.qq.com/smartsheet/DUXJLSnZoTVFhVUVs?tab=sc_daily",
                "view_id": "sc_daily",
                "view_name": "每日更新",
            },
            "schema": [{"field_id": "fld_link", "name": "链接", "type": "url", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [
                        {
                            "field_id": "fld_link",
                            "value": "投递",
                            "links": [{"text": "投递", "url": raw_url}],
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = DatasetSpec("每日更新", root / "daily.json", root / "每日更新.md", 1)

            changed = sync_dataset(spec, scan, scan, now="2026-08-07T00:00:00Z")

            self.assertTrue(changed)
            stored = __import__("json").loads(spec.data_path.read_text(encoding="utf-8"))
            stored_link = stored["records"][0]["fields"][0]["links"][0]
            self.assertEqual(raw_url, stored_link["url"])
            self.assertRegex(stored_link["key"], r"^[0-9a-f]{64}$")
            self.assertRegex(stored["snapshot"]["record_id_hash"], r"^[0-9a-f]{64}$")
            self.assertRegex(stored["snapshot"]["link_hash"], r"^[0-9a-f]{64}$")
            collector = LinkCollector()
            collector.feed(spec.content_path.read_text(encoding="utf-8"))
            self.assertEqual([raw_url], collector.links)


class ParseTencentSheetTests(unittest.TestCase):
    @staticmethod
    def _payload(sheet_id, view_id, start, end, total, operations, workbook=None):
        encoded = base64.b64encode(
            zlib.compress(json.dumps([operations], ensure_ascii=False).encode("utf-8"))
        ).decode("ascii")
        attributed = {"smartsheet": encoded}
        if workbook is not None:
            attributed["workbook"] = json.dumps(workbook, ensure_ascii=False)
        return {
            "retcode": 0,
            "data": {
                "sheetId": sheet_id,
                "viewID": view_id,
                "rev": 42,
                "maxrow": total,
                "maxcol": 2,
                "startrow": start,
                "endrow": end,
                "initialAttributedText": {"text": [attributed], "referenceData": "{}"},
            },
        }

    def test_parses_crdt_pages_with_stable_ids_and_raw_links(self):
        fields = {
            "fld_name": {"k1": {"k9": {}}, "k30": "公司", "k31": 1},
            "fld_apply": {"k8": {"k1": 2, "k9": {}}, "k30": "投递链接", "k31": 8},
        }
        view = {
            "k1": ["rec_1", "rec_2"],
            "k2": ["fld_name", "fld_apply"],
        }
        metadata_op = {
            "t": 3005,
            "v": 5,
            "c": {"k1": "sheet_1", "k3": {"k3": fields, "k4": [{"k1": view}]}},
        }
        first_record = {
            "k1": {
                "fld_name": {"k1": [{"k1": "text", "k2": "甲公司"}], "k30": 1},
                "fld_apply": {
                    "k8": [
                        {"k1": "url", "k2": "官网", "k3": "https://jobs.example/apply?id=A0O"},
                        {"k1": "url", "k2": "内推", "k3": "https://jobs.example/referral?id=1lI"},
                    ],
                    "k30": 8,
                },
            }
        }
        second_record = {
            "k1": {
                "fld_name": {"k1": [{"k1": "text", "k2": "乙公司"}], "k30": 1},
                "fld_apply": {"k8": [], "k30": 8},
            }
        }
        first_page = self._payload(
            "sheet_1",
            "view_1",
            0,
            0,
            2,
            [metadata_op, {"t": 3028, "v": 5, "c": {"k1": "sheet_1", "k2": {"k1": {"rec_1": first_record}}}}],
            workbook=[{"id": "sheet_1", "name": "已改名的每日更新", "type": "smartsheet"}],
        )
        second_page = self._payload(
            "sheet_1",
            "view_1",
            1,
            1,
            2,
            [{"t": 3028, "v": 5, "c": {"k1": "sheet_1", "k2": {"k1": {"rec_2": second_record}}}}],
        )

        snapshot = parse_sheet_pages(
            "每日更新",
            [first_page, second_page],
            source_url="https://docs.qq.com/smartsheet/doc?tab=sheet_1",
            document_id="doc",
        )

        self.assertEqual("sheet_1", snapshot["source"]["sheet_id"])
        self.assertEqual("view_1", snapshot["source"]["view_id"])
        self.assertEqual(["fld_name", "fld_apply"], [field["field_id"] for field in snapshot["schema"]])
        self.assertEqual(["rec_1", "rec_2"], [record["record_id"] for record in snapshot["records"]])
        self.assertEqual(
            ["https://jobs.example/apply?id=A0O", "https://jobs.example/referral?id=1lI"],
            [link["url"] for link in snapshot["records"][0]["fields"][1]["links"]],
        )
        self.assertEqual([[0, 0], [1, 1]], snapshot["snapshot"]["page_ranges"])


class LinkAccessibilityTests(unittest.TestCase):
    def test_redirect_check_keeps_the_original_url(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_HEAD(self):
                if self.path == "/original?id=A0O1lI":
                    self.send_response(302)
                    self.send_header("Location", "/target")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        original = f"http://127.0.0.1:{server.server_port}/original?id=A0O1lI"
        snapshot = {
            "records": [
                {
                    "fields": [
                        {
                            "links": [{"key": "a" * 64, "text": "投递", "url": original}],
                        }
                    ]
                }
            ]
        }
        try:
            checked = check_link_accessibility(snapshot, now="2026-08-07T00:00:00Z")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        link = snapshot["records"][0]["fields"][0]["links"][0]
        self.assertEqual(1, checked)
        self.assertEqual(original, link["url"])
        self.assertEqual("reachable", link["availability"]["result"])
        self.assertEqual(200, link["availability"]["status_code"])
        self.assertNotIn("final_url", link["availability"])

    def test_http_error_is_recorded_without_removing_the_link(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_HEAD(self):
                self.send_response(404)
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        original = f"http://127.0.0.1:{server.server_port}/missing?id=0O"
        snapshot = {
            "records": [{"fields": [{"links": [{"key": "b" * 64, "url": original}]}]}]
        }
        try:
            checked = check_link_accessibility(snapshot, now="2026-08-07T00:00:00Z")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        link = snapshot["records"][0]["fields"][0]["links"][0]
        self.assertEqual(1, checked)
        self.assertEqual(original, link["url"])
        self.assertEqual("unreachable", link["availability"]["result"])
        self.assertEqual(404, link["availability"]["status_code"])
        self.assertEqual("http_error", link["availability"]["error_category"])

    def test_unchanged_link_inherits_result_and_changed_label_is_checked_again(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            requests = 0

            def do_HEAD(self):
                type(self).requests += 1
                self.send_response(200)
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        original = f"http://127.0.0.1:{server.server_port}/apply?id=0O1lI"
        scan = {
            "source": {"view_id": "view_1", "view_name": "每日更新"},
            "schema": [{"field_id": "fld_link", "name": "链接", "type": "url", "order": 0}],
            "snapshot": {"source_total": 1, "fetched_count": 1, "pagination_complete": True},
            "records": [
                {
                    "record_id": "rec_1",
                    "fields": [
                        {
                            "field_id": "fld_link",
                            "value": "投递",
                            "links": [{"text": "官网投递", "url": original}],
                        }
                    ],
                }
            ],
        }
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                spec = DatasetSpec("每日更新", root / "daily.json", root / "每日更新.md", 1)
                self.assertTrue(
                    sync_dataset(
                        spec,
                        scan,
                        scan,
                        now="2026-08-07T00:00:00Z",
                        check_links=True,
                    )
                )
                self.assertFalse(
                    sync_dataset(
                        spec,
                        scan,
                        scan,
                        now="2026-08-07T01:00:00Z",
                        check_links=True,
                    )
                )
                changed_scan = json.loads(json.dumps(scan))
                changed_scan["records"][0]["fields"][0]["links"][0]["text"] = "内推"
                self.assertTrue(
                    sync_dataset(
                        spec,
                        changed_scan,
                        changed_scan,
                        now="2026-08-07T02:00:00Z",
                        check_links=True,
                    )
                )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(2, Handler.requests)


if __name__ == "__main__":
    unittest.main()
