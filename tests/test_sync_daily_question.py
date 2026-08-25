import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_daily_question import prepare_submission, update_content


class DailyQuestionWhitespaceTests(unittest.TestCase):
    def test_generated_entry_has_no_trailing_whitespace(self):
        existing = "# 每日一问\n\n## 2026.08.24\n\n### 已有题目\n\n已有答案\n"
        submission = prepare_submission(
            "新题目",
            "第一行   \n \n第二行\t\n\n```go\nfmt.Println(\"ok\")   \n```",
            "2026-08-25T08:00:00+08:00",
        )

        updated, changed = update_content(existing, submission)

        self.assertTrue(changed)
        offenders = [
            (line_number, line)
            for line_number, line in enumerate(updated.splitlines(), start=1)
            if re.search(r"[ \t]+$", line)
        ]
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
