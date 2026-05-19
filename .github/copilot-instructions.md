# GoClub Copilot 审查说明

GoClub 是一个 Hugo 静态文档站，内容面向 Go 后端面试准备、学习笔记、资源推荐、项目学习页和视频配套文章。

审查 Pull Request 时，请使用简体中文回复。重点关注会影响站点发布、内容质量或读者体验的具体问题：

- Hugo 构建正确性，包括 front matter、shortcodes、模板、依赖子模块的主题用法，以及 `content/`、`layouts/`、`assets/`、`static/`、`data/`、`scripts/` 下的路径。
- 中文文档质量，包括技术表述准确性、标题清晰度、术语一致性、结构可读性和明显错别字。
- 导航一致性：`content/docs/**` 下新增页面如需出现在分区导航中，应同步更新相关 `_index.md`。
- 链接和资源正确性，包括相对链接、`static/` 下的图片路径、外部 URL、锚点和中文文件名。
- 贡献者数据流程：涉及 `scripts/generate_contributors.py`、`data/contributors.json`、`data/maintainers.json` 的改动，应保持 GitHub Pages 构建路径可用。
- GitHub Actions 改动应保持 Hugo 版本与发布 workflow 一致；有意升级 Hugo 时，请说明升级原因和影响范围。

评论要简洁，包含具体文件、行号、影响和建议修复方式。站点能正常构建且信息架构保持一致时，减少宽泛的风格评论。
