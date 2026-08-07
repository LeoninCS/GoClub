# GoClub

GoClub 是一个围绕技术面试准备与系统复习搭建的内容站点，主要整理面试真题、八股总结、资料视频、项目推荐，以及视频配套文章等内容。

当前站点基于 Hugo 构建，部署在 GitHub Pages，自定义域名为 `goclub.space`。

- 站点地址：https://goclub.space
- 在线提交流程页：https://goclub.space/docs/blog/contributing/
- 仓库地址：https://github.com/LeoninCS/GoClub

## 如何提交内容

如果你想给 GoClub 补充面试题、八股、配套文章、项目经验，或者修正文档中的错误，可以使用下面两种方式提交。

### 方式一：把内容交给 AI 添加（推荐）

把原始内容交给支持读写仓库的 AI 编程工具，让 AI 按 GoClub 的项目规范完成整理、归档和目录更新。

你可以直接使用下面这段提示词：

```text
请把下面内容添加到 GoClub 仓库中，并按项目规范处理：

1. 判断内容属于哪个栏目，并放到 content/docs 对应目录。
2. 新增 Markdown 页面时，补齐 title、weight 等必要 front matter。
3. 新增面经页面时，title 和文件名使用「名字+公司+岗位（可选）+几面」格式，例如「lynpt字节SRE三面」或「Shio字节一面」。
4. 文件名含中文时，必须在 front matter 里加一个纯英文小写的 slug，否则分享出去的链接会变成一长串编码字符。面经的 slug 用「投稿人-公司-岗位-轮次」格式，例如 blocke-bytedance-1；其他页面用简短英文描述，例如 go-backend-roadmap。
5. 新增页面后，同步更新对应目录下的 _index.md，让目录页能看到入口。
6. 运行 python3 scripts/gen_shortlinks.py 给新页面补上分享短链。
7. 保持现有文章的标题层级、代码块、引用块和列表风格。
8. 完成后运行 python3 scripts/check_slugs.py 和 hugo --minify 检查结果。

内容如下：

<把你的面试题、八股总结、文章或修正文案贴在这里>
```

AI 处理完成后，重点检查这些内容：

- 文件是否放在合适栏目
- 新增页面是否出现在目录页
- 标题、代码块、图片、链接是否正常
- `git diff` 是否只包含本次贡献相关改动

检查通过后，按下面“方式二”的第 6 步和第 7 步提交 Pull Request。

### 方式二：手动添加并提交 PR

#### 1. Fork 仓库

先 Fork 这个仓库到你自己的 GitHub 账号下。

#### 2. Clone 到本地

```bash
git clone --recursive https://github.com/<your-github-name>/GoClub.git
cd GoClub
```

如果你已经执行过普通 `git clone`，也没关系，进入项目后补一下主题子模块：

```bash
git submodule update --init --recursive
```

> GoClub 的主题 `hugo-book` 是通过 Git submodule 管理的。  
> 初始化子模块后，`themes/hugo-book` 会包含主题文件，`hugo server` 才能正常加载主题模板和布局文件。

#### 3. 新建分支

请在新分支上修改：

```bash
git checkout -b docs/your-topic
```

分支名可以参考：

```text
docs/add-tencent-interview
docs/fix-companion-links
docs/update-mysql-notes
```

#### 4. 添加或修改文档

把内容放到 `content/docs` 对应的栏目下面：

- `content/docs/interview/`：面试真题
- `content/docs/baguwen/`：八股总结
- `content/docs/resources/`：资料、书籍、网站推荐
- `content/docs/companion/`：配套文章
- `content/docs/project-study/`：项目学习与项目拆解
- `content/docs/blog/`：实践经验或技术记录

新增页面时，同步修改对应目录下的 `_index.md`，把新文章加入目录入口。

#### 5. 本地预览

安装 Hugo 后，在项目根目录执行：

```bash
hugo server
```

遇到主题、模板缺失，或者类似 `partial "docs/html-head" not found` 的报错时，先执行：

```bash
git submodule update --init --recursive
```

默认访问地址通常为：

```text
http://localhost:1313/
```

提交前建议至少检查这些内容：

- 页面能否正常打开
- 目录页能否点到新文章
- 标题、图片、代码块、链接是否正常显示
- 是否有明显错别字、断链或排版问题

另外跑一下这两个校验，它们也接在 PR 检查里，不通过会让 PR 失败：

```bash
python3 scripts/check_slugs.py             # 中文文件名是否都配了英文 slug
python3 scripts/gen_shortlinks.py --check  # 新页面是否都有 /s/ 分享短链
```

第二个如果报缺失，去掉 `--check` 再跑一次就会自动补上。

首次 clone 后建议启用仓库自带的 git hook，提交时会自动跑上面两个校验：

```bash
bash scripts/install-hooks.sh
```

#### 6. 提交代码并推送

```bash
git add .
git commit -m "docs: add your topic"
git push origin docs/your-topic
```

#### 7. 发起 Pull Request

回到 GitHub，在你 Fork 的仓库页面发起 PR，到上游仓库的 `main` 分支。

PR 描述里建议写清楚：

- 这次新增或修改了什么内容
- 文档放在哪个目录
- 是否同步更新了对应目录的 `_index.md`

#### 8. 等待合并与部署

PR 被合并后，站点会通过 GitHub Actions 自动构建并发布。

如果你的 PR 被成功合并，部署完成后，你也会出现在贡献者页面中。

## 内容范围

GoClub 当前主要覆盖以下方向：

- 面试真题
- 八股知识总结
- 资料与视频推荐
- 项目推荐
- 视频配套文章

目标是把零散、重复、难以检索的内容，整理成更适合复习和查阅的知识库。

## 本地运行与构建

本地运行：

```bash
git submodule update --init --recursive
hugo server
```

构建静态文件：

```bash
git submodule update --init --recursive
hugo --minify
```

## 项目结构

```text
content/
  _index.md            # 站点首页
  docs/
    _index.md          # 文档分区首页
    interview/         # 面试真题
    baguwen/           # 八股总结
    resources/         # 资料、书籍、网站推荐
    companion/         # 配套文章
    project-study/     # 项目学习与项目拆解
    blog/              # 技术博客与提交流程

.github/workflows/
  static.yml           # GitHub Pages 自动部署
```

## 补充说明

- 仓库推送到 `main` 后，会通过 GitHub Actions 自动构建并发布到 GitHub Pages
- 站点当前使用的主题是 `hugo-book`，通过 Git submodule 管理
- 如果你是首次拉取仓库，建议直接使用 `git clone --recursive`
- 如果你只是想快速查看详细步骤，也可以直接打开 [投稿与提交流程](content/docs/blog/提交流程.md)
