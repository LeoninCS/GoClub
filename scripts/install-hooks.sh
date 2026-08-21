#!/usr/bin/env bash
#
# 启用仓库自带的 git hooks（.githooks/）。
# 每个 clone 只需要跑一次：bash scripts/install-hooks.sh
#
# 原理是把 core.hooksPath 指到仓库内的 .githooks 目录，
# 这样 hook 能跟着仓库一起分发，不用手工往 .git/hooks 里拷。
#
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks

echo "已启用 .githooks，当前生效的 hook："
for f in .githooks/*; do
  [[ -f "$f" ]] && echo "  - $(basename "$f")"
done
echo
echo "提交时会自动校验 URL 短链规范。临时跳过：git commit --no-verify"
echo "关闭：git config --unset core.hooksPath"
