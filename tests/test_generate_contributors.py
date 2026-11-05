import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_contributors import build_contributors, fetch_all_commits, merge_maintainers


def user(login, user_id=1, user_type="User"):
    return {
        "login": login,
        "id": user_id,
        "type": user_type,
        "html_url": f"https://github.com/{login}",
        "avatar_url": f"https://avatars.githubusercontent.com/u/{user_id}?v=4",
    }


def commit(author, message="更新文档", email=None, parents=1):
    return {
        "author": author,
        "commit": {
            "author": {"email": email or "unlinked@example.com"},
            "message": message,
        },
        "parents": [{} for _ in range(parents)],
    }


class ContributorTests(unittest.TestCase):
    def test_counts_commits_by_author_including_direct_and_initial_commits(self):
        commits = [
            commit(user("Alice"), parents=0),
            commit(user("alice")),
            commit(user("Bob", 2)),
            commit(user("Carol", 3)),
        ]
        # 代为推送/合并的人不应获得原作者的贡献计数。
        commits[0]["committer"] = user("Maintainer", 4)

        contributors = build_contributors(commits)

        self.assertEqual(
            [("Alice", 2), ("Bob", 1), ("Carol", 1)],
            [(item["login"], item["commits"]) for item in contributors],
        )

    def test_merge_commits_do_not_add_credit(self):
        contributors = build_contributors([
            commit(user("Alice")),
            commit(user("Maintainer"), parents=2,
                   message="Merge pull request\n\nCo-authored-by: Bob <2+Bob@users.noreply.github.com>"),
        ])

        self.assertEqual([("Alice", 1)], [
            (item["login"], item["commits"]) for item in contributors
        ])

    def test_bot_submission_credits_all_human_coauthors_once(self):
        message = (
            "面经收录\n\n"
            "Co-authored-by: Alice <1+Alice@users.noreply.github.com>\n"
            "co-authored-by: Alice <1+alice@users.noreply.github.com>\n"
            "Co-authored-by: Bob <2+Bob@users.noreply.github.com>\n"
            "Co-authored-by: Bot <3+helper[bot]@users.noreply.github.com>"
        )
        contributors = build_contributors([
            commit(user("github-actions[bot]", 41898282, "Bot"), message=message),
            commit(user("dependabot[bot]")),
            commit(user("Copilot", 4, "Bot")),
        ])

        self.assertEqual([("Alice", 1), ("Bob", 1)], [
            (item["login"], item["commits"]) for item in contributors
        ])
        self.assertEqual("https://github.com/Alice", contributors[0]["html_url"])
        self.assertEqual("https://avatars.githubusercontent.com/u/1?v=4", contributors[0]["avatar_url"])

    def test_author_and_repeated_coauthor_count_only_once_per_commit(self):
        contributors = build_contributors([
            commit(user("Alice"), message=(
                "更新\n\n"
                "Co-authored-by: Alice <1+alice@users.noreply.github.com>\n"
                "Co-authored-by: Alice <1+Alice@users.noreply.github.com>"
            )),
        ])

        self.assertEqual(1, len(contributors))
        self.assertEqual(1, contributors[0]["commits"])

    def test_unlinked_authors_are_skipped_without_crediting_committer(self):
        unknown = commit(None)
        unknown["committer"] = user("Maintainer")
        no_identity = {"author": None, "commit": {"author": None, "message": "更新"}}

        self.assertEqual([], build_contributors([unknown, no_identity]))

    def test_noreply_authors_and_known_coauthor_emails_are_resolved(self):
        contributors = build_contributors([
            commit(None, email="1+Alice@users.noreply.github.com"),
            commit(None, email="Bob@users.noreply.github.com"),
            commit(user("github-actions[bot]"), message=(
                "自动投稿\n\nCo-authored-by: Carol <CAROL@example.com>"
            )),
            commit(user("Carol", 3), email="carol@example.com"),
        ])

        self.assertEqual([("Carol", 2), ("Alice", 1), ("Bob", 1)], [
            (item["login"], item["commits"]) for item in contributors
        ])

    def test_maintainer_metadata_preserves_real_count_and_order(self):
        contributors = build_contributors([
            commit(user("Alice")), commit(user("alice")), commit(user("Bob", 2)),
        ])
        maintainers = [
            {"login": "ALICE", "role": "核心维护者", "sort_order": 2, "commits": 99},
            {"login": "Zero", "role": "核心维护者", "pinned": True, "sort_order": 1},
        ]

        merged = merge_maintainers(maintainers, contributors)

        self.assertEqual([("Zero", 0), ("ALICE", 2), ("Bob", 1)], [
            (item["login"], item["commits"]) for item in merged
        ])
        self.assertEqual("核心维护者", merged[1]["role"])


class CommitPaginationTests(unittest.TestCase):
    @patch("generate_contributors.request_json")
    def test_fetches_all_pages_with_default_branch_head_pinned(self, request):
        first_page = [{"sha": f"commit-{index}"} for index in range(100)]
        last_page = [{"sha": "oldest-commit"}]
        request.side_effect = [first_page, last_page]

        self.assertEqual(first_page + last_page, fetch_all_commits("owner/repo", token="test-token"))
        self.assertEqual([
            call("https://api.github.com/repos/owner/repo/commits?per_page=100&page=1", token="test-token"),
            call("https://api.github.com/repos/owner/repo/commits?per_page=100&page=2&sha=commit-0", token="test-token"),
        ], request.call_args_list)

    @patch("generate_contributors.request_json")
    def test_stops_on_empty_page_after_full_page(self, request):
        first_page = [{"sha": f"commit-{index}"} for index in range(100)]
        request.side_effect = [first_page, []]

        self.assertEqual(first_page, fetch_all_commits("owner/repo"))
        self.assertEqual(2, request.call_count)


if __name__ == "__main__":
    unittest.main()
