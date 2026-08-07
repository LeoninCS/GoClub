# AGENTS.md

GoClub 是一个 Hugo 静态文档站，内容面向 Go 后端面试准备：面试真题、八股总结、学习资料、配套文章和项目拆解。

站点地址 https://goclub.space/ ，通过 GitHub Actions 自动部署到 GitHub Pages。

## 项目结构

```
content/docs/          站点全部内容
  interview/           面试真题（dachang / zhongchang / xiaochang）
  baguwen/             八股总结
  resources/           资料、书籍、网站推荐
  companion/           配套文章
  project-study/       项目学习与拆解
  blog/                实践经验与技术记录
layouts/               模板覆盖（主题为 submodule themes/hugo-book）
scripts/               构建期辅助脚本
.github/workflows/     CI：pr-check / static / daily-question-sync
```

主题通过 Git submodule 管理，首次 clone 后需要执行 `git submodule update --init --recursive`，否则 Hugo 会报 partial 缺失。

## URL 短链规范（重要）

Hugo 默认用文件名生成 URL。**中文文件名会被浏览器 percent-encode，一个汉字变成 9 个字符**，分享到微信时链接极长——改造前站内最长的一条 URL 有 271 个字符。

因此：**文件名含中文的页面，必须在 front matter 里指定纯 ASCII 的 `slug`。**

```yaml
---
title: "布洛克琴字节一面"
slug: "blocke-bytedance-1"
---
```

命名规则：

- 面经：`投稿人-公司-岗位-轮次`，如 `blocke-bytedance-1`、`gogod-didi-growth-backend-2`
- 其他页面：简短英文描述内容，如 `go-backend-roadmap`、`book-recommendations`
- 只允许小写字母、数字和连字符

目录名直接进入 URL 且无法用 slug 覆盖，所以 **`content/` 下的目录名必须是英文**。

### 修改已发布页面的 slug 时

必须在 `aliases` 里保留旧路径，Hugo 会在旧地址生成跳转页，别人之前收藏或转发的链接才不会失效：

```yaml
---
title: "布洛克琴字节一面"
slug: "blocke-bytedance-1"
aliases:
  - "/docs/interview/dachang/布洛克琴字节一面/"
---
```

### 校验

```bash
python3 scripts/check_slugs.py
```

检查目录名、slug 合法性、slug 缺失和同目录 URL 冲突。已接入 `pr-check.yml`，不合规会直接让 PR 失败。

## 分享短链 /s/

可读 slug 把 URL 压到 63 字符，但发微信仍偏长，所以每个主要内容页额外挂一个 `/s/xxxx` 短链（约 28 字符）。

**现有 URL 完全不变**，短链只是额外入口，由 Hugo 的 `aliases` 生成跳转页。

```yaml
---
title: "布洛克琴字节一面"
slug: "blocke-bytedance-1"
aliases:
  - "/docs/interview/dachang/布洛克琴字节一面/"
  - "/s/ltsl/"
shortlink: "ltsl"
---
```

`shortlink` 字段供页面上的「复制短链」按钮读取，模板在 `layouts/partials/goclub/share-shortlink.html`。

短码由**内容文件路径**哈希得到，所以改标题、改正文、改 slug 都不会让短码变化，只有重命名或移动文件才会变。

新增页面后运行下面这条即可自动补齐，脚本是幂等的：

```bash
python3 scripts/gen_shortlinks.py          # 补齐缺失的短链
python3 scripts/gen_shortlinks.py --check  # 只检查（CI 用）
python3 scripts/gen_shortlinks.py --list   # 打印短码对照表
```

整本书的单章（`resources/` 下 web3-books、epub-books、pdf-books、cloud-native-web3-fulltext）不生成短链，书的目录页仍然生成。

**不要手工改动已发布页面的 `shortlink`**，那会让别人手里的短链失效。文件重命名后脚本会提示短码不一致，此时应保留旧短链而不是直接覆盖。

## 新增内容的标准流程

1. 判断内容属于哪个栏目，放到 `content/docs/` 对应目录
2. 补齐 front matter：`title`、`weight`，中文文件名再加 `slug`
3. 面经的 title 和文件名用「名字+公司+岗位（可选）+几面」格式
4. 同步更新所在目录的 `_index.md`，让目录页能点进去
5. 运行 `python3 scripts/gen_shortlinks.py` 自动补上 `/s/` 短链
6. 保持既有文章的标题层级、代码块、引用块和列表风格
7. 站内链接优先用 `{{< relref "path/to/file.md" >}}`，它按文件路径解析，slug 变化时会自动跟随；不要硬编码含中文的页面 URL

## 验证

```bash
python3 scripts/check_slugs.py             # URL 短链校验
python3 scripts/gen_shortlinks.py --check  # 分享短链校验
hugo --minify                              # 构建校验
hugo server                                # 本地预览 http://localhost:1313/
```

提交前确认 `git diff` 只包含本次改动相关的文件。

## 约定

- 站内文档和 PR 交流使用简体中文
- 图片放 `static/pictures/`，页面里用绝对路径 `/pictures/xxx.png` 引用
- 修改 GitHub Actions 时，保持各 workflow 的 `HUGO_VERSION` 一致
- 不要提交 `public/` 和 `resources/` 的构建产物之外的临时文件
