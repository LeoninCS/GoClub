# GoClub Copilot 审查说明

GoClub 是一个 Hugo 静态文档站，内容面向 Go 后端面试准备、学习笔记、资源推荐、项目学习页和视频配套文章。

审查 Pull Request 时，请使用简体中文回复。重点关注会影响站点发布、内容质量或读者体验的具体问题：

- Hugo 构建正确性，包括 front matter、shortcodes、模板、依赖子模块的主题用法，以及 `content/`、`layouts/`、`assets/`、`static/`、`data/`、`scripts/` 下的路径。
- 中文文档质量，包括技术表述准确性、标题清晰度、术语一致性、结构可读性、明显错别字、病句、低俗词、冒犯性表达，以及不适合公开文档的口语化玩笑，并给出更正式的替代表达。
- 导航一致性：`content/docs/**` 下新增页面如需出现在分区导航中，应同步更新相关 `_index.md`。
- URL 短链规范：文件名含中文的页面必须在 front matter 里指定 ASCII `slug`，否则 URL 会被 percent-encode 成一长串字符，分享体验很差。面经用「投稿人-公司-岗位-轮次」格式，如 `blocke-bytedance-1`；其他页面用简短英文描述，如 `go-backend-roadmap`。修改已发布页面的 `slug` 时，必须在 `aliases` 中保留旧路径，避免已分享出去的链接失效。校验脚本是 `scripts/check_slugs.py`，已接入 PR 检查。
- 分享短链：每个主要内容页还有一个 `/s/xxxx` 短链，由 `scripts/gen_shortlinks.py` 按文件路径哈希生成，写在 front matter 的 `shortlink` 字段和 `aliases` 里。本地 hook 和 `shortlink-sync.yml` 都会自动补齐，PR 里缺短链不算问题、不要求投稿者处理；**不要手工修改已发布页面的 `shortlink`**，那会让已经分享出去的短链失效。
- 链接和资源正确性，包括相对链接、`static/` 下的图片路径、外部 URL、锚点和中文文件名。站内页面链接优先用 `{{< relref >}}`，不要硬编码含中文的路径。
- 贡献者数据流程：涉及 `scripts/generate_contributors.py`、`data/contributors.json`、`data/maintainers.json` 的改动，应保持 GitHub Pages 构建路径可用。
- GitHub Actions 改动应保持 Hugo 版本与发布 workflow 一致；有意升级 Hugo 时，请说明升级原因和影响范围。

评论要简洁，包含具体文件、行号、影响和建议修复方式。站点能正常构建且信息架构保持一致时，减少宽泛的风格评论。
