---
title: "常用工具"
aliases:
  - "/s/zm03/"
shortlink: "zm03"
---

# 常用工具

## Git

### Git 的工作区、暂存区和本地仓库分别是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 工作区是你正在编辑的项目文件；暂存区是下一次提交的候选快照；本地仓库是 `.git` 目录里保存提交历史、分支、标签和对象数据库的地方。典型流程是修改工作区文件，用 `git add` 把变更放入暂存区，再用 `git commit` 把暂存区快照写成本地仓库里的一个提交。

**要答的点：**
- 工作区：真实文件目录，承载当前编辑内容。
- 暂存区：index，保存下一次 commit 的内容。
- 本地仓库：`.git` 目录，保存对象、引用和历史。
- `git status`：查看工作区和暂存区状态。
- `git add`：把工作区变更加入暂存区。
- `git commit`：把暂存区快照写入本地仓库。

**重点讲解摘录：**
- Pro Git 把 Git 项目分为 working tree、staging area 和 Git directory。
- Git 官方文档把 index 描述为暂存下一次提交内容的区域。
- `git status` 会同时显示 staged 和 unstaged changes。
- 提交对象记录快照、作者、提交者、父提交和提交信息。

**原文链接：**
- [Pro Git: Getting Started - Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Git Documentation: git-add](https://git-scm.com/docs/git-add)
- [Git Documentation: git-status](https://git-scm.com/docs/git-status)
- [Git Documentation: git-commit](https://git-scm.com/docs/git-commit)

</div>
</details>

### `git pull` 和 `git fetch` 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `git fetch` 只从远程拉取最新对象和远程跟踪分支，不改当前工作分支；`git pull` 等于先 fetch，再把远程分支整合到当前分支，默认通常执行 merge，也可以配置或使用参数执行 rebase。日常协作里想先看远程变化就用 fetch，确定要整合再 merge 或 rebase。

**要答的点：**
- `fetch`：更新远程跟踪引用，如 `origin/main`。
- `pull`：获取远程更新并整合到当前分支。
- 默认整合：常见是 merge，配置后可 rebase。
- 风险：`pull` 会改变当前分支历史或产生合并提交。
- 推荐流程：`git fetch` -> 查看 diff/log -> `git merge` 或 `git rebase`。
- 排查：`git branch -vv` 看本地分支跟踪关系。

**重点讲解摘录：**
- `git-fetch` 文档说明它从远程仓库下载对象和引用。
- `git-pull` 文档说明 pull 会 fetch 并 merge 另一个仓库或本地分支。
- `git pull --rebase` 会在 fetch 后执行 rebase。
- `origin/main` 是远程跟踪分支，代表最近一次 fetch 得到的远程状态。

**原文链接：**
- [Git Documentation: git-fetch](https://git-scm.com/docs/git-fetch)
- [Git Documentation: git-pull](https://git-scm.com/docs/git-pull)
- [Pro Git: Remote Branches](https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches)

</div>
</details>

### `git merge` 和 `git rebase` 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `merge` 是把两个分支的历史合并在一起，保留原始分叉结构，可能产生一个 merge commit；`rebase` 是把当前分支的提交挪到目标分支最新提交之后，让历史看起来更线性。团队主干合并常用 merge 保留上下文，个人特性分支同步主干常用 rebase 整理历史。已经共享给别人的提交做 rebase 会改写提交哈希，需要谨慎。

**要答的点：**
- merge：保留分叉历史，新增合并提交或 fast-forward。
- rebase：重放提交，形成线性历史。
- 冲突处理：两者都可能冲突，都需要解决后继续。
- 适用：公共分支合并偏 merge，个人分支整理偏 rebase。
- 风险：rebase 改写提交哈希，共享分支需团队约定。
- 命令：`git merge main`、`git rebase main`。

**重点讲解摘录：**
- `git-merge` 文档说明 merge 会把多个开发历史连接在一起。
- `git-rebase` 文档说明 rebase 会把提交重新应用到另一个 base 之上。
- Pro Git 把 rebase 作为维护线性历史的方式。
- rebase 后提交内容可能相同，提交对象哈希会变化。

**原文链接：**
- [Git Documentation: git-merge](https://git-scm.com/docs/git-merge)
- [Git Documentation: git-rebase](https://git-scm.com/docs/git-rebase)
- [Pro Git: Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)

</div>
</details>

### 发生代码冲突后如何处理

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 冲突处理流程是先用 `git status` 找到冲突文件，打开文件查看 `<<<<<<<`、`=======`、`>>>>>>>` 标记，结合双方改动决定最终内容，删除冲突标记后运行测试，确认无误后 `git add` 标记已解决，最后继续 `merge` 或 `rebase`。团队协作时要理解业务意图，必要时找改动作者确认。

**要答的点：**
- 定位：`git status` 查看 unmerged paths。
- 理解：比较 ours/theirs 两边改动。
- 编辑：保留正确结果，删除冲突标记。
- 验证：格式化、编译、单测或关键手动验证。
- 标记：`git add <file>` 表示冲突已解决。
- 继续：merge 后 commit；rebase 用 `git rebase --continue`。

**重点讲解摘录：**
- Git 文档说明冲突发生后需要用户手动解决。
- `git status` 会显示哪些路径处于 unmerged 状态。
- `git merge --abort` 和 `git rebase --abort` 可回到操作前状态。
- 冲突解决的核心是产出一个正确的最终文件。

**原文链接：**
- [Git Documentation: git-merge](https://git-scm.com/docs/git-merge)
- [Git Documentation: git-rebase](https://git-scm.com/docs/git-rebase)
- [Pro Git: Basic Merge Conflicts](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)

</div>
</details>

### `git reset`、`git revert` 和 `git checkout` 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `reset` 主要移动当前分支指针，并可同时影响暂存区和工作区；`revert` 会生成一个新的反向提交，用来撤销已有提交的效果；`checkout` 传统上用于切分支或把某个版本的文件检出到工作区。现代 Git 更推荐用 `switch` 切分支，用 `restore` 恢复文件。公共分支撤销历史优先用 `revert`，本地整理历史才考虑 `reset`。

**要答的点：**
- `reset --soft`：移动 HEAD，保留暂存区和工作区。
- `reset --mixed`：默认模式，重置暂存区，保留工作区。
- `reset --hard`：重置分支、暂存区和工作区。
- `revert`：新增反向提交，保留历史可追溯。
- `checkout`：切换分支或恢复文件，语义较多。
- 现代命令：`git switch`、`git restore` 让意图更明确。

**重点讲解摘录：**
- `git-reset` 文档说明 reset 会把当前 HEAD 重置到指定状态。
- `git-revert` 文档说明 revert 会记录一些新的提交来反转已有提交的效果。
- `git-checkout` 文档覆盖切分支和恢复路径两类用途。
- Git 官方引入 `switch` 和 `restore` 是为了拆分 checkout 的多重语义。

**原文链接：**
- [Git Documentation: git-reset](https://git-scm.com/docs/git-reset)
- [Git Documentation: git-revert](https://git-scm.com/docs/git-revert)
- [Git Documentation: git-checkout](https://git-scm.com/docs/git-checkout)
- [Git Documentation: git-switch](https://git-scm.com/docs/git-switch)
- [Git Documentation: git-restore](https://git-scm.com/docs/git-restore)

</div>
</details>

### `git cherry-pick` 的使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `git cherry-pick` 用来把某个已有提交应用到当前分支，生成一个内容相同但哈希新的提交。常见场景是把修复补丁从主干挑到 release 分支，或把某个独立提交从实验分支挑到当前分支。它适合挑单个或少数独立提交，提交依赖复杂时应考虑 merge 或重新整理分支。

**要答的点：**
- 作用：复制提交变更到当前分支。
- 场景：hotfix 回挑、release 补丁、独立功能提取。
- 命令：`git cherry-pick <commit>`。
- 冲突：解决冲突后 `git cherry-pick --continue`。
- 风险：重复提交、依赖缺失、历史分散。
- 选择：连续多个提交可 cherry-pick 范围，复杂分支用 merge/rebase。

**重点讲解摘录：**
- `git-cherry-pick` 文档说明它会应用现有提交引入的更改。
- cherry-pick 生成的是新提交，哈希和原提交不同。
- 版本维护分支经常用 cherry-pick 选择性引入修复。
- 面试里可以用“把一个 commit 拎过来”解释。

**原文链接：**
- [Git Documentation: git-cherry-pick](https://git-scm.com/docs/git-cherry-pick)
- [Pro Git: Distributed Git - Maintaining a Project](https://git-scm.com/book/en/v2/Distributed-Git-Maintaining-a-Project)

</div>
</details>

### `git stash` 的作用和常见用法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `git stash` 用来临时保存当前工作区和暂存区的改动，让工作目录回到干净状态，方便切分支、拉代码或处理紧急任务。常见命令有 `git stash push -m "msg"` 保存，`git stash list` 查看，`git stash show -p` 看内容，`git stash pop` 应用并删除，`git stash apply` 应用但保留。未跟踪文件需要加 `-u`。

**要答的点：**
- 保存：`git stash push -m "message"`。
- 包含未跟踪：`git stash -u`。
- 查看：`git stash list`、`git stash show -p stash@{0}`。
- 恢复：`git stash pop` 或 `git stash apply`。
- 删除：`git stash drop`、`git stash clear`。
- 场景：临时切分支、避免半成品提交、拉取前保存现场。

**重点讲解摘录：**
- `git-stash` 文档说明 stash 会保存 dirty working directory 的状态。
- stash 默认保存 tracked 文件的工作区和暂存区变更。
- `pop` 会应用 stash 并从 stash 列表移除。
- `apply` 会应用 stash，同时保留 stash 记录。

**原文链接：**
- [Git Documentation: git-stash](https://git-scm.com/docs/git-stash)
- [Pro Git: Stashing and Cleaning](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning)

</div>
</details>

### 如何查看某次提交改了什么内容

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 查看某次提交最常用 `git show <commit>`，它会显示提交信息和补丁内容。只看文件列表用 `git show --stat <commit>` 或 `git diff-tree --stat`；比较某次提交和它父提交用 `git diff <commit>^ <commit>`；查看某个文件历史用 `git log -- <path>`，查某行是谁改的用 `git blame <file>`。

**要答的点：**
- 完整补丁：`git show <sha>`。
- 文件统计：`git show --stat <sha>`。
- 仅文件名：`git show --name-only <sha>`。
- 两版本比较：`git diff old new`。
- 文件历史：`git log -- path/to/file`。
- 行级追踪：`git blame path/to/file`。

**重点讲解摘录：**
- `git-show` 文档说明它可以展示对象，包括提交和提交引入的 diff。
- `git-diff` 用于显示提交、工作区和暂存区之间的差异。
- `git-log` 支持按路径过滤历史。
- `git-blame` 可以显示每一行最后一次修改的提交和作者。

**原文链接：**
- [Git Documentation: git-show](https://git-scm.com/docs/git-show)
- [Git Documentation: git-diff](https://git-scm.com/docs/git-diff)
- [Git Documentation: git-log](https://git-scm.com/docs/git-log)
- [Git Documentation: git-blame](https://git-scm.com/docs/git-blame)

</div>
</details>

## CI/CD

### 什么是 CI，什么是 CD

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** CI 是持续集成，核心是开发者频繁合并代码到主干，并通过自动构建、测试和静态检查尽早发现问题。CD 有两层含义：持续交付强调代码始终处于可发布状态，发布到生产通常需要人工确认；持续部署强调通过流水线自动发布到生产。面试里可以说 CI 保证集成质量，CD 保证发布效率和可重复性。

**要答的点：**
- CI：频繁集成、自动构建、自动测试、快速反馈。
- Continuous Delivery：持续交付到可发布状态，生产发布可人工批准。
- Continuous Deployment：持续部署到生产，自动完成发布。
- 价值：减少集成风险、缩短反馈周期、提高发布稳定性。
- 前提：自动化测试、版本管理、制品管理、环境一致性。

**重点讲解摘录：**
- Martin Fowler 把 Continuous Integration 描述为团队成员频繁集成并由自动构建验证。
- GitLab 文档区分 Continuous Delivery 和 Continuous Deployment。
- GitHub Actions 文档说明工作流可自动构建、测试和部署代码。
- 面试里把 CI 和 CD 的边界讲清楚即可。

**原文链接：**
- [Martin Fowler: Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [GitLab: CI/CD](https://docs.gitlab.com/ee/ci/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

</div>
</details>

### 一个典型的 CI/CD 流程包含哪些阶段

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 典型 CI/CD 流程包括代码提交、触发流水线、依赖安装、编译构建、静态检查、单元测试、集成测试、安全扫描、构建制品、推送镜像或包、部署到测试/预发、自动化验收、人工审批、生产发布、健康检查和回滚预案。核心是把质量检查和发布步骤标准化、自动化、可追踪。

**要答的点：**
- 触发：push、PR/MR、tag、定时任务、手动触发。
- 检查：lint、格式化、类型检查、单元测试。
- 构建：编译、打包、Docker 镜像、制品归档。
- 测试：集成测试、E2E、安全扫描、性能冒烟。
- 部署：测试、预发、生产多环境发布。
- 发布后：健康检查、监控告警、回滚或继续灰度。

**重点讲解摘录：**
- GitHub Actions 工作流由 events 触发，并包含 jobs 和 steps。
- GitLab CI 使用 stages 和 jobs 描述流水线。
- Docker 官方建议用镜像作为一致的交付制品。
- Kubernetes 部署通常配合 readiness/liveness 探针做健康检查。

**原文链接：**
- [GitHub Actions: Understanding workflows](https://docs.github.com/en/actions/using-workflows/about-workflows)
- [GitLab CI/CD pipelines](https://docs.gitlab.com/ee/ci/pipelines/)
- [Docker Docs: Build and push images](https://docs.docker.com/build/)
- [Kubernetes: Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

</div>
</details>

### 为什么要在流水线中加入自动化测试

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 自动化测试是流水线的质量闸门，用来在代码合并和发布前快速发现回归问题。它能把依赖人工记忆的检查变成稳定、可重复、可追踪的验证，降低线上事故概率。面试里可以按测试金字塔回答：单元测试覆盖核心逻辑，集成测试覆盖模块协作，E2E 或冒烟测试覆盖关键用户路径。

**要答的点：**
- 快速反馈：提交后尽早发现 bug。
- 防回归：保证旧功能在新改动后仍正常。
- 可重复：同一套验证在不同环境可稳定执行。
- 质量门禁：失败阻断合并或发布。
- 分层：单元、集成、E2E、契约、安全和性能测试。
- 成本控制：高频跑快测试，低频跑慢测试。

**重点讲解摘录：**
- Martin Fowler 的 CI 实践强调自动构建应包含自测试。
- GitHub Actions 文档把自动测试作为常见工作流用途。
- 测试金字塔思想强调底层测试数量多、速度快、反馈早。
- 发布流水线里测试失败要能快速定位到提交和日志。

**原文链接：**
- [Martin Fowler: Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [GitHub Actions: Building and testing](https://docs.github.com/en/actions/automating-builds-and-tests)
- [Google Testing Blog: Test Pyramid](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)

</div>
</details>

### 持续集成和持续部署分别解决了什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 持续集成解决多人协作中的集成风险，通过频繁合并和自动验证，让冲突、编译错误和测试失败尽早暴露。持续部署解决发布慢、发布不稳定、人工步骤多的问题，通过自动化流水线把通过验证的变更发布到生产。前者关注代码质量反馈，后者关注交付到用户的速度和稳定性。

**要答的点：**
- CI 解决：集成冲突、回归缺陷、反馈慢。
- CI 手段：主干集成、自动构建、自动测试、代码扫描。
- CD 解决：发布流程手工化、环境不一致、上线风险高。
- CD 手段：制品不可变、多环境流水线、自动部署、健康检查。
- 共同目标：小步快跑、快速反馈、降低发布风险。

**重点讲解摘录：**
- CI 的核心实践是频繁集成并自动验证。
- Continuous Deployment 把通过流水线的变更自动发布到生产。
- 小批量变更让问题更容易定位和回滚。
- 可重复流水线能降低“某个人会发布”的组织风险。

**原文链接：**
- [Martin Fowler: Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [GitLab: Continuous delivery vs continuous deployment](https://docs.gitlab.com/ee/ci/introduction/)
- [Google Cloud: DevOps tech - Continuous delivery](https://cloud.google.com/architecture/devops/devops-tech-continuous-delivery)

</div>
</details>

### GitHub Actions、GitLab CI、Jenkins 有什么区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** GitHub Actions 和 GitLab CI 都是和代码平台深度集成的 CI/CD，配置通常写在仓库 YAML 里，适合云端协作和代码事件触发。Jenkins 是独立自动化服务器，插件生态大、可定制能力强，适合复杂企业环境和内网系统集成。选择时看代码托管平台、权限模型、Runner 管理、插件需求、内网部署和维护成本。

**要答的点：**
- GitHub Actions：和 GitHub 事件、PR、Marketplace Actions 集成紧。
- GitLab CI：和 GitLab Repo、MR、Runner、环境、制品管理一体化。
- Jenkins：独立部署，插件丰富，自定义自由度高。
- 配置方式：Actions workflow、GitLab `.gitlab-ci.yml`、Jenkinsfile。
- Runner/Agent：三者都支持自托管执行节点。
- 选型：平台原生优先，复杂内网和历史流程可用 Jenkins。

**重点讲解摘录：**
- GitHub Actions 使用 events 触发 workflows。
- GitLab CI 通过 `.gitlab-ci.yml` 定义 jobs 和 stages。
- Jenkins Pipeline 支持用 Jenkinsfile 声明流水线。
- 平台原生 CI 的优势是权限、代码评审和状态检查整合顺滑。

**原文链接：**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)

</div>
</details>

### 如何设计开发、测试、预发、生产多环境发布流程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 多环境发布要做到同一份代码和制品在不同环境逐级验证，配置通过环境变量、配置中心或密钥系统外部化。常见流程是开发环境快速验证功能，测试环境跑集成和回归，预发环境尽量贴近生产做最终验收，生产环境按灰度、滚动或蓝绿发布。每一层都要有准入条件、审批、健康检查、监控和回滚方案。

**要答的点：**
- 制品一致：一次构建，多环境部署同一个镜像或包。
- 配置分离：环境变量、配置中心、Secret 管理差异。
- 权限隔离：不同环境账号、数据库、网络和密钥隔离。
- 准入门禁：测试通过、代码评审、安全扫描、审批。
- 发布策略：开发自动，测试自动，预发审批，生产灰度。
- 回滚：保留上一版本制品和数据库兼容方案。

**重点讲解摘录：**
- Twelve-Factor App 强调配置应存储在环境中。
- Docker 镜像作为不可变制品有利于环境一致性。
- Kubernetes Secret 和 ConfigMap 常用于配置与密钥注入。
- 预发环境价值是尽量复现生产依赖和流量特征。

**原文链接：**
- [The Twelve-Factor App: Config](https://12factor.net/config)
- [Docker Docs: Images](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
- [Kubernetes: ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes: Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

</div>
</details>

### 什么是灰度发布、蓝绿发布和滚动发布

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 滚动发布是分批替换实例，新旧版本在一段时间内同时提供服务；灰度发布是先让少量用户或少量流量访问新版本，验证稳定后逐步扩大；蓝绿发布是准备两套完整环境，蓝环境承载当前生产流量，绿环境部署新版本，验证后一次性切换流量。三者目标都是降低发布风险，区别在流量切换方式、资源成本和回滚速度。

**要答的点：**
- 滚动发布：逐批替换实例，资源成本低，发布时间较长。
- 灰度发布：按用户、地域、比例或规则逐步放量。
- 蓝绿发布：两套环境切换，回滚快，资源成本高。
- 共同要求：健康检查、监控、日志、回滚、数据库兼容。
- 适用：资源有限用滚动，风险控制用灰度，强回滚要求用蓝绿。

**重点讲解摘录：**
- Kubernetes Deployment 默认支持 rolling update。
- Kubernetes readiness probe 能控制新实例就绪后再接流量。
- 蓝绿发布常通过负载均衡或网关切换流量。
- 灰度发布要有指标观测和自动停止条件。

**原文链接：**
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes: Rolling Update](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
- [Martin Fowler: BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Google Cloud: Deployment strategies](https://cloud.google.com/deploy/docs/deployment-strategies)

</div>
</details>

### 发布失败后如何快速回滚

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 快速回滚要提前设计，核心是制品可追溯、配置可恢复、数据库变更兼容、流量可切回。应用层保留上一版本镜像或包，发布失败后通过平台回滚到上一 ReplicaSet 或上一部署版本；配置层保留变更历史；数据库变更采用向前兼容方案，避免新版本一上线就破坏旧版本。回滚后要做健康检查、监控确认和事故复盘。

**要答的点：**
- 制品：每次发布绑定版本号、镜像 digest、Git commit。
- 平台：Kubernetes 可 `rollout undo` 回滚 Deployment。
- 配置：配置中心支持版本记录和回滚。
- 数据库：先加字段再双写，延迟删除旧字段，保证旧版本可运行。
- 流量：灰度或蓝绿可快速切回旧版本。
- 验证：回滚后看错误率、延迟、核心业务指标和日志。

**重点讲解摘录：**
- Kubernetes Deployment 保留 rollout history，可回滚到早期 revision。
- 不可变制品让回滚指向明确，避免现场重新构建。
- 数据库 schema 变更是回滚难点，扩展-迁移-收缩模式更稳。
- 灰度发布减少问题版本影响面，也让回滚更快。

**原文链接：**
- [Kubernetes: Rolling Back a Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment)
- [Kubernetes: kubectl rollout](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/)
- [Martin Fowler: Evolutionary Database Design](https://martinfowler.com/articles/evodb.html)

</div>
</details>

## Docker 与部署

### Docker 镜像和容器的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 镜像是静态的、可复用的只读模板，包含文件系统、运行时依赖和启动配置；容器是镜像运行起来后的实例，本质是带隔离环境的进程，拥有自己的可写层、网络、挂载和运行状态。一个镜像可以启动多个容器，容器删除后运行时状态会消失，持久数据要放到 volume、数据库或对象存储里。

**要答的点：**
- 镜像：分层、只读、可分发、可版本化。
- 容器：运行态实例，有进程、命名空间、cgroups 和可写层。
- 关系：一个镜像可创建多个容器。
- 可写层：容器内部写入落到容器层，生命周期随容器结束。
- 持久化：数据卷和外部存储保存长期数据。
- 命令：`docker image ls`、`docker ps`、`docker run image`。

**重点讲解摘录：**
- Docker 文档把镜像描述为容器的只读模板。
- Docker 文档把容器描述为镜像的可运行实例。
- Union filesystem 分层让镜像复用基础层，降低分发成本。
- 容器运行隔离依赖 Linux namespaces 和 cgroups 等机制。

**原文链接：**
- [Docker Docs: What is an image?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
- [Docker Docs: What is a container?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Docker Docs: Storage](https://docs.docker.com/storage/)

</div>
</details>

### Dockerfile 常见指令有哪些

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Dockerfile 是构建镜像的声明式文件。常见指令包括 `FROM` 指定基础镜像，`WORKDIR` 设置工作目录，`COPY/ADD` 复制文件，`RUN` 在构建阶段执行命令，`ENV/ARG` 设置变量，`EXPOSE` 声明端口，`USER` 指定运行用户，`VOLUME` 声明挂载点，`CMD/ENTRYPOINT` 设置容器启动命令，`HEALTHCHECK` 定义健康检查。面试里最好能说出构建时指令和运行时指令的差异。

**要答的点：**
- 基础：`FROM`、`LABEL`、`ARG`、`ENV`。
- 文件：`COPY`、`ADD`、`.dockerignore`。
- 构建：`RUN`、多阶段 `FROM ... AS`。
- 运行：`CMD`、`ENTRYPOINT`、`EXPOSE`、`USER`。
- 存储和健康：`VOLUME`、`HEALTHCHECK`。
- 最佳实践：少层、缓存友好、最小镜像、非 root 用户。

**重点讲解摘录：**
- Dockerfile reference 说明 Dockerfile 是构建镜像的指令集合。
- `FROM` 初始化新的构建阶段并设置基础镜像。
- `RUN` 在当前镜像之上执行命令并提交新层。
- `CMD` 和 `ENTRYPOINT` 都与容器启动命令有关。
- `.dockerignore` 可以减少构建上下文，提升构建效率和安全性。

**原文链接：**
- [Docker Docs: Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Docker Docs: Build context](https://docs.docker.com/build/concepts/context/)
- [Docker Docs: Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

</div>
</details>

### 什么是多阶段构建，为什么要使用多阶段构建

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 多阶段构建是在一个 Dockerfile 里使用多个 `FROM`，前面的阶段负责编译、测试和生成产物，最后的阶段只复制运行所需文件。这样可以把编译器、源码、缓存和临时依赖留在构建阶段，让最终镜像更小、更安全、更快分发。Go 项目常见做法是 builder 阶段编译静态二进制，runtime 阶段使用 distroless、alpine 或 scratch 运行。

**要答的点：**
- 多个阶段：`FROM golang AS builder`、`FROM alpine AS runtime`。
- 复制产物：`COPY --from=builder /app/server /server`。
- 体积：最终镜像只保留运行必需文件。
- 安全：减少编译器、包管理器和调试工具。
- 缓存：先复制 `go.mod/go.sum` 下载依赖，再复制源码构建。
- 可维护：构建环境和运行环境职责分离。

**重点讲解摘录：**
- Docker 多阶段构建文档说明可以在 Dockerfile 中使用多个 FROM。
- `COPY --from` 可以从前一阶段复制文件到当前阶段。
- 多阶段构建让最终镜像更精简。
- Go 官方镜像常用于 builder，scratch/distroless 常用于运行阶段。

**原文链接：**
- [Docker Docs: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Docs: Dockerfile reference - COPY --from](https://docs.docker.com/reference/dockerfile/#copy---from)
- [Docker Docs: Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

</div>
</details>

### `CMD` 和 `ENTRYPOINT` 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `ENTRYPOINT` 定义容器的主程序，`CMD` 提供默认参数或默认命令。`docker run image arg` 默认会覆盖 `CMD`，并把参数追加给 exec 形式的 `ENTRYPOINT`；如果只写 `CMD`，运行时参数会整体替换默认命令。常见最佳实践是用 `ENTRYPOINT` 固定应用程序，用 `CMD` 提供默认参数。

| 场景 | CMD | ENTRYPOINT |
| --- | --- | --- |
| 作用 | 默认命令或默认参数 | 固定容器入口程序 |
| 被 `docker run` 参数影响 | 通常被覆盖 | 参数通常追加到入口程序后 |
| 常见组合 | `CMD ["--config=/app/config.yaml"]` | `ENTRYPOINT ["/app/server"]` |

**要答的点：**
- `CMD`：为容器提供默认执行内容。
- `ENTRYPOINT`：配置容器作为可执行程序运行。
- exec 形式：`["executable", "arg"]`，信号处理更清晰。
- shell 形式：通过 shell 执行，信号和参数处理要谨慎。
- 覆盖：`docker run --entrypoint` 可覆盖入口。
- 推荐：服务镜像用 `ENTRYPOINT` + `CMD` 默认参数。

**重点讲解摘录：**
- Dockerfile reference 说明一个 Dockerfile 只有最后一个 CMD 生效。
- ENTRYPOINT 允许把容器配置成可执行程序。
- exec 形式通常能让进程直接接收 Unix 信号。
- 生产服务要关注 PID 1 的信号处理和优雅退出。

**原文链接：**
- [Docker Docs: CMD](https://docs.docker.com/reference/dockerfile/#cmd)
- [Docker Docs: ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint)
- [Docker Docs: Run containers](https://docs.docker.com/engine/containers/run/)

</div>
</details>

### 容器启动失败时如何排查问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 容器启动失败先看状态和退出码，再看日志和配置。常用 `docker ps -a` 找容器，`docker logs <container>` 看启动日志，`docker inspect <container>` 看镜像、命令、环境变量、挂载、网络和退出码；如果是端口冲突，用 `ss -ltnp`；如果是权限或文件缺失，检查用户、挂载路径和工作目录；如果启动后立刻退出，确认 `CMD/ENTRYPOINT` 是否以前台方式运行。

**要答的点：**
- 状态：`docker ps -a`、退出码、重启次数。
- 日志：`docker logs --tail=200 container`。
- 配置：`docker inspect container` 看 env、cmd、mount、network。
- 端口：`ss -ltnp` 或 `docker port container`。
- 资源：`docker stats` 看 CPU、内存；OOM 看 inspect 和系统日志。
- 进入调试：覆盖 entrypoint 启动 shell，例如 `docker run --rm -it --entrypoint sh image`。

**重点讲解摘录：**
- Docker `logs` 文档说明它会获取容器日志。
- Docker `inspect` 返回容器和镜像的底层 JSON 信息。
- 容器主进程退出后，容器生命周期也结束。
- 健康检查失败和进程退出是两类不同问题。

**原文链接：**
- [Docker Docs: docker container logs](https://docs.docker.com/reference/cli/docker/container/logs/)
- [Docker Docs: docker inspect](https://docs.docker.com/reference/cli/docker/inspect/)
- [Docker Docs: docker stats](https://docs.docker.com/reference/cli/docker/container/stats/)
- [Docker Docs: Container troubleshooting](https://docs.docker.com/config/containers/logging/)

</div>
</details>

### `docker compose` 的作用是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `docker compose` 是单机多容器应用编排工具，用一个 `compose.yaml` 声明多个服务、镜像、端口、环境变量、网络、卷和依赖关系，然后用 `docker compose up` 一键启动整套应用。它适合本地开发、测试环境和小规模部署，能把数据库、缓存、后端、前端等服务一起管理。

**要答的点：**
- 声明式：用 YAML 描述 services、networks、volumes。
- 多服务：一个命令启动应用栈。
- 网络：同一 compose 项目内服务可用服务名互相访问。
- 配置：支持环境变量、`.env` 文件、端口映射和挂载。
- 命令：`up`、`down`、`logs`、`ps`、`exec`。
- 场景：本地开发、集成测试、演示环境。

**重点讲解摘录：**
- Docker Compose 文档说明 Compose 用于定义和运行多容器 Docker 应用。
- Compose Specification 定义 services、networks、volumes 等核心字段。
- `docker compose up` 会创建并启动服务容器。
- Compose 网络让服务通过名称发现彼此。

**原文链接：**
- [Docker Docs: Docker Compose](https://docs.docker.com/compose/)
- [Compose Specification](https://compose-spec.io/)
- [Docker Docs: docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)

</div>
</details>

### 应用部署时如何管理配置和环境变量

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 配置要外部化，镜像里只放应用和默认配置，环境差异通过环境变量、配置文件挂载、配置中心和密钥系统注入。普通配置可以放环境变量或 ConfigMap，敏感信息放 Secret 或专门的密钥管理系统；同一份镜像在开发、测试、预发、生产使用不同配置运行。部署时还要注意配置版本、回滚、审计和最小权限。

**要答的点：**
- 外部化：同一镜像适配多环境。
- 环境变量：适合简单配置和十二要素应用。
- 配置文件：通过 volume、ConfigMap 或配置中心挂载。
- 密钥：数据库密码、Token、证书放 Secret 或 KMS。
- 版本管理：配置变更要可审计、可回滚。
- 安全：避免把敏感配置写入镜像、Git 仓库和日志。

**重点讲解摘录：**
- Twelve-Factor App 建议把配置存储在环境中。
- Docker 支持 `--env` 和 `--env-file` 注入环境变量。
- Kubernetes ConfigMap 用于非敏感配置，Secret 用于敏感数据。
- 镜像内硬编码配置会导致环境漂移和密钥泄露风险。

**原文链接：**
- [The Twelve-Factor App: Config](https://12factor.net/config)
- [Docker Docs: Environment variables](https://docs.docker.com/compose/environment-variables/)
- [Kubernetes: ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes: Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

</div>
</details>

### 服务发布时如何尽量做到不停机

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 不停机发布靠“新实例先就绪、旧实例后下线、流量平滑切换”。具体做法是先启动新版本实例，readiness 健康检查通过后再接入负载均衡；旧实例先摘除流量，再等待正在处理的请求完成，最后优雅退出。发布策略可以用滚动、灰度或蓝绿，同时配合监控告警、自动回滚和数据库兼容变更。

**要答的点：**
- 健康检查：readiness 通过后才接流量。
- 负载均衡：流量逐步从旧实例切到新实例。
- 优雅停机：收到 SIGTERM 后停止接新请求，等待存量请求完成。
- 滚动更新：控制 max unavailable 和 max surge。
- 灰度验证：小流量先验证错误率和延迟。
- 数据库兼容：先兼容旧新版本，再删除旧字段和旧逻辑。

**重点讲解摘录：**
- Kubernetes Deployment 支持滚动更新。
- Readiness probe 用于判断 Pod 是否可以接收流量。
- Graceful shutdown 需要应用正确处理终止信号。
- 发布稳定性取决于健康检查、监控和回滚路径。

**原文链接：**
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes: Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Docker Docs: Stop containers](https://docs.docker.com/reference/cli/docker/container/stop/)
- [Google Cloud: Deployment strategies](https://cloud.google.com/deploy/docs/deployment-strategies)

</div>
</details>

### 滚动发布、灰度发布、蓝绿发布等策略的目的是什么，核心区别是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这些发布策略的共同目标是降低上线风险、减少停机时间、提升回滚速度。滚动发布按实例批次逐步替换，资源成本低；灰度发布按流量或用户范围逐步放量，风险控制更细；蓝绿发布准备两套完整环境，验证后一次性切流，回滚最快但资源成本最高。面试对比重点看流量切换方式、资源成本、回滚速度和影响范围。

| 对比维度 | 滚动发布 | 灰度发布 | 蓝绿发布 |
| --- | --- | --- | --- |
| 流量切换 | 随实例逐批替换 | 按比例、用户、地域逐步放量 | 通过网关或负载均衡一次切换 |
| 回滚速度 | 逐批回滚 | 停止放量并切回旧版本 | 切回蓝环境 |
| 资源成本 | 较低 | 中等 | 较高 |
| 风险控制 | 实例粒度 | 用户/流量粒度 | 环境粒度 |
| 适用场景 | 常规服务迭代 | 高风险功能和新版本验证 | 强隔离和快速回滚要求 |

**要答的点：**
- 滚动：控制批次，依赖健康检查。
- 灰度：按规则放量，依赖指标观测。
- 蓝绿：双环境切流，依赖环境一致性。
- 共同基础：监控、日志、告警、回滚、数据库兼容。
- 选择依据：风险、成本、流量规模、回滚要求。

**重点讲解摘录：**
- Kubernetes Deployment 的 rolling update 是滚动发布的典型实现。
- Blue-green deployment 通过两套环境降低发布切换风险。
- Canary/灰度发布的关键是逐步扩大暴露面并观察指标。
- 生产发布策略要和数据库迁移、配置变更一起设计。

**原文链接：**
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Martin Fowler: BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Google Cloud: Deployment strategies](https://cloud.google.com/deploy/docs/deployment-strategies)

</div>
</details>
