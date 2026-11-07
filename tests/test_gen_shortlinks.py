import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gen_shortlinks


class ShortlinkMigrationTests(unittest.TestCase):
    def run_generator(self, root, *args):
        output = io.StringIO()
        with patch.object(gen_shortlinks, "CONTENT_ROOT", str(root)), \
                patch.object(sys, "argv", ["gen_shortlinks.py", *args]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = gen_shortlinks.main()
        return status, output.getvalue()

    def test_moved_page_keeps_published_shortlink_during_check_generate_and_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "blog" / "Go后端学习路线.md"
            page.parent.mkdir()
            original = (
                '---\ntitle: "Go后端学习路线"\nslug: "go-backend-roadmap"\n'
                'aliases:\n  - "/docs/companion/go-backend-roadmap/"\n  - "/s/kiun/"\n'
                'shortlink_source: "companion/Go后端学习路线.md"\n'
                'shortlink: "kiun"\n---\n\n正文\n'
            )
            page.write_text(original, encoding="utf-8")

            for args in [("--check",), (), ("--list",)]:
                with self.subTest(args=args):
                    status, output = self.run_generator(root, *args)
                    self.assertEqual(0, status, output)
                    self.assertEqual(original, page.read_text(encoding="utf-8"))
                    if args == ("--list",):
                        self.assertEqual("kiun  blog/Go后端学习路线.md\n", output)

    def test_unacknowledged_path_change_still_fails_without_overwriting_shortlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "moved.md"
            original = '---\ntitle: Test\nshortlink: "kiun"\naliases:\n  - "/s/kiun/"\n---\n'
            page.write_text(original, encoding="utf-8")

            status, output = self.run_generator(root)

            self.assertEqual(1, status)
            self.assertIn("不一致", output)
            self.assertEqual(original, page.read_text(encoding="utf-8"))

    def test_new_page_gets_stable_shortlink_and_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "new.md"
            page.write_text('---\ntitle: New\n---\n\n正文\n', encoding="utf-8")

            status, output = self.run_generator(root)
            self.assertEqual(0, status, output)
            generated = page.read_text(encoding="utf-8")
            code = gen_shortlinks.make_code("new.md")
            self.assertIn(f'shortlink: "{code}"', generated)
            self.assertIn(f'  - "/s/{code}/"', generated)
            status, output = self.run_generator(root, "--check")
            self.assertEqual(0, status, output)
            status, output = self.run_generator(root)
            self.assertEqual(0, status, output)
            self.assertEqual(generated, page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
