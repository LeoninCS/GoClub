#!/usr/bin/env python3

import json
import os
import re
import sys
import urllib.request


API_ROOT = "https://api.github.com"
CO_AUTHORED_BY_RE = re.compile(
    r"^Co-authored-by:[ \t]*.+?[ \t]*<(?P<email>[^<>\s]+)>[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)
NOREPLY_EMAIL_RE = re.compile(
    r"(?:(?P<id>[0-9]+)\+)?(?P<login>[a-zA-Z0-9-]+(?:\[bot\])?)@users\.noreply\.github\.com",
    re.IGNORECASE,
)


def request_json(url, token=None):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
            "User-Agent": "GoClub-Contributors-Generator",
        },
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_all_commits(repo, token=None):
    """读取默认分支历史；后续分页固定首个 SHA，避免新提交导致翻页偏移。"""
    page = 1
    commits = []
    head = None

    while True:
        url = f"{API_ROOT}/repos/{repo}/commits?per_page=100&page={page}"
        if head:
            url += f"&sha={head}"
        items = request_json(url, token=token)
        if not items:
            break

        if head is None:
            head = items[0]["sha"]
        commits.extend(items)

        if len(items) < 100:
            break

        page += 1

    return commits


def user_from_noreply_email(email):
    match = NOREPLY_EMAIL_RE.fullmatch(email)
    if not match:
        return None
    login = match.group("login")
    user_id = match.group("id")
    return {
        "login": login,
        "html_url": f"https://github.com/{login}",
        "avatar_url": (
            f"https://avatars.githubusercontent.com/u/{user_id}?v=4"
            if user_id else f"https://github.com/{login}.png"
        ),
    }


def build_contributors(commits):
    grouped = {}
    # 用 API 已确认的邮箱关联识别共同作者，不根据显示名猜测 GitHub 账号。
    users_by_email = {
        item["commit"]["author"]["email"].lower(): item["author"]
        for item in commits
        if item.get("author") and (item["commit"].get("author") or {}).get("email")
    }

    for item in commits:
        # 普通 merge 不额外计数，原分支上的内容提交仍会各计一次。
        if len(item.get("parents", [])) > 1:
            continue

        commit = item["commit"]
        author_email = (commit.get("author") or {}).get("email") or ""
        users = [item.get("author") or users_by_email.get(author_email.lower())
                 or user_from_noreply_email(author_email)]
        for match in CO_AUTHORED_BY_RE.finditer(commit.get("message") or ""):
            email = match.group("email")
            users.append(users_by_email.get(email.lower()) or user_from_noreply_email(email))

        seen = set()
        for user in users:
            if not user or not user.get("login"):
                continue
            login = user["login"]
            key = login.lower()
            if user.get("type") == "Bot" or key.endswith("[bot]") or key in seen:
                continue
            seen.add(key)

            if key not in grouped:
                grouped[key] = {
                    "login": login,
                    "html_url": user["html_url"],
                    "avatar_url": user["avatar_url"],
                    "name": None,
                    "commits": 0,
                }

            grouped[key]["commits"] += 1

    return sorted(grouped.values(), key=lambda item: (-item["commits"], item["login"].lower()))


def merge_maintainers(maintainers, contributors):
    merged = {}

    for contributor in contributors:
        merged[contributor["login"].lower()] = contributor

    for maintainer in maintainers:
        key = maintainer["login"].lower()
        contributor = merged.get(key, {})
        merged[key] = {
            **contributor,
            **maintainer,
            "commits": contributor.get("commits", 0),
        }

    return sorted(
        merged.values(),
        key=lambda item: (
            0 if item.get("pinned") else 1,
            item.get("sort_order", float("inf")),
            -item.get("commits", 0),
            item["login"].lower(),
        ),
    )


def normalize_avatars(contributors, token=None):
    """把 github.com/{login}.png 这类地址换成 avatars.githubusercontent.com 的直链。

    github.com 的图片接口在部分网络环境下不可达（主域名被墙/限流），
    而头像 CDN 通常可用，因此统一走 CDN。
    """
    for item in contributors:
        url = item.get("avatar_url") or ""
        if "github.com/" in url and "avatars.githubusercontent.com" not in url:
            try:
                user = request_json(f"{API_ROOT}/users/{item['login']}", token=token)
                if user.get("avatar_url"):
                    item["avatar_url"] = user["avatar_url"]
            except Exception:
                login = item["login"]
                item["avatar_url"] = f"https://github.com/{login}.png"

    return contributors


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip() or None
    output = os.environ.get("CONTRIBUTORS_OUTPUT", "data/contributors.json")
    maintainers_path = os.environ.get("MAINTAINERS_INPUT", "data/maintainers.json")

    if not repo:
        print("Missing GITHUB_REPOSITORY", file=sys.stderr)
        sys.exit(1)

    commits = fetch_all_commits(repo, token=token)
    contributors = build_contributors(commits)
    maintainers = load_json_file(maintainers_path, [])
    contributors = merge_maintainers(maintainers, contributors)
    contributors = normalize_avatars(contributors, token=token)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(contributors, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {len(contributors)} contributors to {output}")


if __name__ == "__main__":
    main()
