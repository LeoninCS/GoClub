import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from process_interview_question import (
    extract_submission_content,
    normalize_markdown_headings,
)


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


class NormalizeMarkdownHeadingsTests(unittest.TestCase):
    def test_adds_missing_space_after_hashes(self):
        markdown = "##一面\n###算法\n"

        self.assertEqual("## 一面\n### 算法\n", normalize_markdown_headings(markdown))

    def test_keeps_already_valid_headings_unchanged(self):
        markdown = "## 一面\n\n### 项目经历\n\n1. 介绍项目\n"

        self.assertEqual(markdown, normalize_markdown_headings(markdown))

    def test_keeps_indentation_of_headings_inside_lists(self):
        markdown = "1. 介绍项目\n\n   ### 详细设计\n"

        self.assertEqual(
            "1. 介绍项目\n\n   ### 详细设计\n", normalize_markdown_headings(markdown)
        )

    def test_keeps_hash_comments_inside_fenced_code_blocks(self):
        markdown = "```go\n## 这不是标题\n```\n\n##一面\n"

        self.assertEqual(
            "```go\n## 这不是标题\n```\n\n## 一面\n", normalize_markdown_headings(markdown)
        )

    def test_keeps_more_than_six_hashes_unchanged(self):
        markdown = "####### 不是标题\n"

        self.assertEqual(markdown, normalize_markdown_headings(markdown))

    def test_does_not_rewrite_body_text(self):
        markdown = "1.讲一下 redis 缓存穿透是什么\n2. jwt 鉴权如何实现\n"

        self.assertEqual(markdown, normalize_markdown_headings(markdown))


if __name__ == "__main__":
    unittest.main()
