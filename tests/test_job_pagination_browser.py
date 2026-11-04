import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_qq_jobs import render_markdown


class JobPaginationBrowserTests(unittest.TestCase):
    def test_pagination_controls_show_every_page_in_browser(self):
        from playwright.sync_api import sync_playwright

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
            browser = playwright.chromium.launch(headless=True)
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


if __name__ == "__main__":
    unittest.main()
