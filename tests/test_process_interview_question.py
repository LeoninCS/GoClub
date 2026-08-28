import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from process_interview_question import extract_submission_content


class ExtractSubmissionContentTests(unittest.TestCase):
    def test_issue_form_preserves_markdown_subheadings(self):
        issue_body = """### 请选择面经要收录的目录

大厂

### 面试内容

## 一面

### 项目经历

1. 介绍项目

### Go 与并发

2. Channel 有哪些使用场景？

### 投稿确认

- [X] 我确认内容可以公开。
"""

        self.assertEqual(
            """## 一面

### 项目经历

1. 介绍项目

### Go 与并发

2. Channel 有哪些使用场景？""",
            extract_submission_content(issue_body),
        )

    def test_legacy_field_preserves_subheadings_and_excludes_confirmation(self):
        issue_body = """### 标准化 Markdown

## 二面

### 数据库

1. MySQL 索引如何设计？

### 投稿确认

- [X] 我确认内容可以公开。
"""

        self.assertEqual(
            """## 二面

### 数据库

1. MySQL 索引如何设计？""",
            extract_submission_content(issue_body),
        )


if __name__ == "__main__":
    unittest.main()
