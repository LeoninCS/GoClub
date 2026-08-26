#!/usr/bin/env python3

import json
import os
import sys
import re
import urllib.request


API_ROOT = "https://api.github.com"
CO_AUTHORED_BY_RE = re.compile(
    r"^Co-authored-by:\s*.+?\s*<(?P<id>[0-9]+)\+(?P<login>[a-zA-Z0-9-]+)@users\.noreply\.github\.com>\s*$",
    re.MULTILINE,
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


def fetch_all_merged_prs(repo, token=None):
    page = 1
    merged = []

    while True:
        url = f"{API_ROOT}/repos/{repo}/pulls?state=closed&per_page=100&page={page}"
        items = request_json(url, token=token)
        if not items:
            break

        for item in items:
            if item.get("merged_at") and item.get("user"):
                merged.append(item)

        if len(items) < 100:
            break

        page += 1

    return merged


def build_contributors(prs):
    grouped = {}

    for pr in prs:
        user = pr["user"]
        login = user["login"]
        user_id = user.get("id")

        if login == "github-actions[bot]":
            co_authors = CO_AUTHORED_BY_RE.search(pr.get("body") or "")
            if co_authors:
                user_id = co_authors.group("id")
                login = co_authors.group("login")

        if login == "github-actions[bot]":
            continue

        if login not in grouped:
            grouped[login] = {
                "login": login,
                "html_url": user["html_url"] if user_id == user.get("id") else f"https://github.com/{login}",
                "avatar_url": user["avatar_url"] if user_id == user.get("id") else f"https://avatars.githubusercontent.com/u/{user_id}?v=4",
                "name": None,
                "merged_prs": 0,
            }

        grouped[login]["merged_prs"] += 1

    return sorted(grouped.values(), key=lambda item: (-item["merged_prs"], item["login"].lower()))


def merge_maintainers(maintainers, contributors):
    merged = {}

    for contributor in contributors:
        merged[contributor["login"]] = contributor

    for maintainer in maintainers:
        login = maintainer["login"]
        if login in merged:
            merged[login] = {
                **merged[login],
                **maintainer,
                "merged_prs": merged[login].get("merged_prs", 0),
            }
        else:
            merged[login] = maintainer

    return sorted(
        merged.values(),
        key=lambda item: (
            0 if item.get("pinned") else 1,
            item.get("sort_order", float("inf")),
            -item.get("merged_prs", 0),
            item["login"].lower(),
        ),
    )


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip() or None
    output = os.environ.get("CONTRIBUTORS_OUTPUT", "data/contributors.json")
    maintainers_path = os.environ.get("MAINTAINERS_INPUT", "data/maintainers.json")

    if not repo:
        print("Missing GITHUB_REPOSITORY", file=sys.stderr)
        sys.exit(1)

    prs = fetch_all_merged_prs(repo, token=token)
    contributors = build_contributors(prs)
    maintainers = load_json_file(maintainers_path, [])
    contributors = merge_maintainers(maintainers, contributors)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(contributors, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {len(contributors)} contributors to {output}")


if __name__ == "__main__":
    main()
