# 图标来源（Lucide）

本站图标统一使用 [Lucide](https://lucide.dev) 图标库（ISC 许可证，全文见同目录 `LUCIDE-LICENSE`，与官方仓库 LICENSE 一致）。

- `lucide/<name>.svg`：从 Lucide 官方仓库 `github.com/lucide-icons/lucide` 的 `icons/` 目录取的 SVG 原件，仅在模板内联时由 Hugo partial `layouts/partials/goclub/icon.html` 去掉 width/height 以便 CSS 控制尺寸，其余路径数据未改。
- 本目录根下的 `chevron-right.svg`、`calendar.svg`、`edit.svg`、`backward.svg`、`forward.svg`、`menu.svg`、`toc.svg`、`translate.svg`：同为 Lucide 原件的副本，文件名沿用 hugo-book 主题 `docs/icon` partial 的约定（站点 assets 优先于主题 assets 同名文件，达到换图不改主题）。其中 `edit.svg` 的内容是 Lucide `pencil`，`backward/forward` 是 `arrow-left/arrow-right`，`toc` 是 `list`，`translate` 是 `languages`。

## 品牌标

站点品牌标是本站原创手绘 SVG（不是 Lucide 图标）。上一版「蓝方块白 G」已被否，当前 `static/logo.svg` 为用户 2026-10-23 挑定的**候选 2（对话气泡+Go）定稿**（先定候选 3，同日改定候选 2；同日再定气泡填充换全站同源的 Gemini 渐变 #3186ff→#346bf0→#4ea0ff）；三候选原件与多尺寸自查图在工作区 `goclub-redesign/logo2/`。顶栏品牌区（`layouts/partials/docs/brand.html`）以 `<img>` 引用 `static/logo.svg`；首页 hero 右侧放大展示同一文件。标签页图标 `static/favicon.svg` 与 `static/favicon.png`（512px）与 favicon.svg 直接使用候选 2 本体（实心气泡自带底形）。`lucide/book-open.svg` 仅保留给首页栏目卡片（八股总结）使用，不再充当品牌标。

## 首页栏目卡片图标

首页栏目卡片按栏目名映射 Lucide 图标（`layouts/index.html` 内按标题关键字选择）：面试真题 `messages-square`、八股总结 `book-open`、资源荟萃 `folder-open`、配套文章 `file-text`、项目学习 `code`、技术博客 `pen-line`、求职就业 `briefcase`、贡献者 `users`，未命中时用 `library`。原件同样在 `lucide/` 目录。

## 例外

顶栏的 GitHub 标志不是 Lucide：Lucide 现行版本已移除全部品牌图标（官方仓库 `icons/github.svg` 不存在），故该处保留原有 GitHub 官方 octocat SVG（填充式），不要用其他图形冒充。
