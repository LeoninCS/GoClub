# 腾讯文档招聘信息同步到 GoClub - 详细实施计划

> 本文档根据需求资料和当前项目代码编写。
> 核心思路：专用账号会话仅以 GitHub Secret 注入临时浏览器；同步程序对两个数据集分别执行结构化全量读取、双遍一致性校验、历史合并、原始链接哈希校验和原子生成，随后由独立 workflow 构建、白名单提交并触发 Pages。；用 DatasetSpec 数据清单驱动共享同步管线，扩展数据集时只增加配置与目标文件。

---

## 设计决策（Q&A）

### Q1：如何在无法获得文档所有者 API 或导出授权的条件下，将两个字段不同的数据集准确、完整、可持续地同步到 GoClub？

使用专用腾讯账号的一次性浏览器会话作为 GitHub Actions Secret。同步程序读取腾讯文档结构化网络数据，分别维护“每日更新”和“秋招提前批”的版本化 JSON 快照与生成页面；只有登录、视图、字段、分页、总量、唯一键和原始链接哈希全部通过校验时才写入。

> 选择理由：目标文档的实际记录要求登录，匿名探针只能读取标题和权限元数据。专用账号已经确认可看到两个数据集；GitHub Actions 可复用仓库已有的默认分支检出、Hugo 全站构建、白名单提交和 Pages 触发模式，同时避免用户电脑持续开机。两个源数据集字段不同，独立快照和独立页面可以保留源字段含义并减少页面框架改动。

> 复用结论：复用 .github/workflows/daily-question-sync.yml 的并发控制、默认分支、Hugo 构建、变更白名单、机器人提交和 Pages 触发结构；借鉴 scripts/sync_daily_question.py 的确定性生成、输入校验与原子替换方式；继续使用 Hugo Book 的 section 自动发现和 Markdown 渲染。

### Q2：如何兼顾最小改动与未来增加同类招聘数据集？

在同一个同步脚本中定义轻量 DatasetSpec，保存视图名、数据文件、页面文件、排序权重和必要的展示投影；全部数据集共享采集、完整性校验、历史合并与表格渲染流程。

> 选择理由：该边界消除两个数据集之间的流程复制，同时避免引入插件系统、通用 ETL 框架、数据库或额外服务，符合仓库规模和最小改动要求。

> 复用结论：继续复用同一个 QQDocsSource、校验器、历史合并器和 Markdown 渲染器。

---

## 改动总览

| 序号 | 文件或平台 | 改动类型 | 说明 |
|---|---|---|---|
| 1 | `content/docs/jobs/_index.md` | 修改 | 复用 main 的“求职就业”一级栏目，保留“内推”并增加两个招聘数据入口。 |
| 2 | `content/docs/jobs/每日更新.md` | 新增 | 生成并展示每日更新数据集，字段按该数据集自身 schema 输出。 |
| 3 | `content/docs/jobs/秋招提前批.md` | 新增 | 生成并展示秋招提前批数据集，字段按该数据集自身 schema 输出。 |
| 5 | `data/jobs/daily-updates.json` | 新增 | 保存每日更新的可审计源快照和历史记录。 |
| 6 | `data/jobs/early-recruitment.json` | 新增 | 保存秋招提前批的可审计源快照和历史记录。 |
| 7 | `scripts/sync_qq_jobs.py` | 新增 | 实现登录态加载、结构化响应采集、完整性校验、历史合并、链接检查和原子生成。 |
| 8 | `tests/test_sync_qq_jobs.py` | 新增 | 覆盖分页完整性、双数据集 schema、去重、多个链接、0/O 原样性、删除保护、原子写入和渲染回读。 |
| 9 | `.github/workflows/qq-jobs-sync.yml` | 新增 | 每 3 小时或手动同步，失败创建或更新 GitHub Issue，成功后白名单提交并触发 Pages。 |
| 10 | `scripts/sync_qq_jobs.py` | 新增 | 定义 DatasetSpec 和 DATASETS 清单，两个数据集共享完整同步管线。 |
| 11 | `assets/_custom.scss` | 修改 | 仅为招聘宽表增加稳定列宽、横向滚动和分页控件样式，其他页面表格保持原样。 |

---

## 步骤 1：接入求职就业一级栏目并新增两个子页面

**文件**：`content/docs/jobs/_index.md；content/docs/jobs/每日更新.md；content/docs/jobs/秋招提前批.md`

**位置**：Hugo front matter 与生成内容

复用 main 中 weight 7 的“求职就业”section，保留“内推”子栏目，并增加每日更新和秋招提前批子页面。子页面由同步脚本确定性生成，不增加 layout，并只增加招聘表格专用的分页与横向滚动样式。

**当前代码**：
```markdown
最新 main 已提供 content/docs/jobs“求职就业”栏目和“内推”子栏目，贡献者栏目 weight 已为 8。
```

**修改后代码**：
```markdown
保留求职就业 _index.md 的 title、weight、短链与“内推”入口；新增“每日更新”和“秋招提前批”入口，两个子页面分别使用独立标题和排序权重。
```

**执行说明**：

- 两个子页面分别读取各自 JSON 快照中的 schema，避免字段错位。
- 页面展示最后成功同步时间、活动记录和已从源表移除的历史记录，不提供腾讯文档源表入口；JSON 快照保留源 URL 用于同步审计。
- 每条企业记录生成一个表格行，每 15 条分页，首页始终容纳排序后的最新记录，后续新增记录自动推动旧记录后移；每日更新按更新日期降序，同日保持腾讯源顺序；秋招没有更新日期字段时保持腾讯源顺序。
- 秋招展示层隐藏“内推码”和“对接人”，并将“内推链接”表头显示为“投递链接”；JSON 快照继续保留全部原始字段和值。

---

## 步骤 2：定义两个独立且可审计的数据快照

**文件**：`data/jobs/daily-updates.json；data/jobs/early-recruitment.json`

**位置**：source、schema、snapshot、records

每个数据集独立保存文档 ID、视图 ID、视图名、字段 ID/名称/类型/顺序、源端总数、抓取数、记录集合和链接哈希。记录以源 record_id 为主键，字段以 field_id 绑定，链接以 view_id + record_id + field_id + 原始 URL 为唯一键。

**当前代码**：
```json
data/jobs 目录当前不存在。
```

**修改后代码**：
```json
每个快照包含 source、schema、snapshot 和 records；records 保存 status、first_seen_at、last_seen_at、removed_at 与字段值/原始链接数组。
```

**执行说明**：

- 原始 URL 不做大小写、查询参数、片段或字符纠错。
- 跨数据集相同记录分别保留；同一字段内完全相同的链接唯一键只保留一次。

---

## 步骤 3：实现登录态结构化采集与完整性门槛

**文件**：`scripts/sync_qq_jobs.py`

**位置**：QQDocsSource、probe_dataset、validate_snapshot

通过 Playwright 加载临时 storage state 和原文档，捕获腾讯文档结构化网络响应；按视图名称定位两个数据集并遍历到结束游标。连续采集两遍，记录 ID、字段 ID、源总量和原始链接哈希一致后才返回快照。

**当前代码**：
```python
当前只有 scripts/sync_daily_question.py，负责每日一问文本写入，不包含腾讯文档读取能力。
```

**修改后代码**：
```python
新增独立 QQDocsSource 适配器和 probe/sync CLI；登录页、安全拦截、缺失视图、缺失稳定 ID、分页未结束、总量不一致或双遍结果不一致均抛出明确错误且不写文件。
```

**执行说明**：

- 禁止从截图、OCR、单元格展示文本或视觉行号重建 URL。
- 结构化协议变化时失败关闭，避免把部分数据当作完整数据。
- 日志只输出数据集名、数量、哈希摘要和错误类别。

---

## 步骤 4：实现历史合并、删除保护与原子生成

**文件**：`scripts/sync_qq_jobs.py`

**位置**：merge_history、render_markdown、atomic_replace

将完整新快照与上次成功快照按 record_id 合并。新增记录追加，现有记录覆盖字段更新，缺失记录保留历史；计划任务检测到源记录缺失时先失败并告警，只有手动触发显式确认删除后才标记为源表已移除。所有 JSON 和 Markdown 在临时目录完成并通过回读校验后统一替换。

**当前代码**：
```python
仓库没有招聘数据历史合并或生成逻辑。
```

**修改后代码**：
```python
新增确定性 JSON/Markdown 生成、原子替换和 --accept-source-deletions 手动开关；生成后解析页面链接并与源链接集合及 SHA-256 完全比对。
```

**执行说明**：

- 链接可访问性单独检查并记录，不以跳转后的地址覆盖原链接。
- 目标站点拒绝 HEAD/GET 时只记录检查结果，不删除源链接。

---

## 步骤 5：补充聚焦测试

**文件**：`tests/test_sync_qq_jobs.py`

**位置**：unittest 测试类与结构化响应 fixtures

使用本地 fixtures 验证两个视图字段不同、分页结束、源总量核对、稳定 ID、重复记录、多链接、URL 字符原样、源删除保护、历史保留、原子写入和 HTML href 回读。

**当前代码**：
```python
仓库当前没有 tests 目录。
```

**修改后代码**：
```python
新增标准库 unittest 测试；包含 0/O、1/l/I、大小写、查询参数、片段、Markdown 特殊字符和多个链接的回归用例。
```

**执行说明**：

- 网络协议解析测试使用脱敏 fixtures，不依赖实时腾讯文档。
- 实时探针作为受 Secret 保护的集成验证，不在 pull_request 事件中运行。

---

## 步骤 6：新增定时同步与失败告警 workflow

**文件**：`.github/workflows/qq-jobs-sync.yml`

**位置**：schedule、workflow_dispatch、sync 与 report_failure jobs

每 3 小时和手动触发时检出默认分支，在 runner 临时目录解码 storage state，安装固定版本 Playwright/Chromium，执行测试和同步，初始化主题、构建 Hugo、校验变更白名单后提交数据与页面并触发 static.yml。失败 job 创建或更新一个招聘同步故障 Issue。

**当前代码**：
```yaml
现有 daily-question-sync.yml 只处理 workflow_dispatch 的单条每日一问投稿。
```

**修改后代码**：
```yaml
新增独立 workflow，permissions 包含 contents: write、actions: write、issues: write；concurrency 禁止并行；Secret 缺失、会话过期、完整性门槛失败或白名单外改动均终止。
```

**执行说明**：

- storage state 只写入 RUNNER_TEMP，任务结束由 runner 清理。
- pull_request 和 fork 工作流不会读取该 Secret。
- Issue 只包含运行 URL、数据集和错误类别，不包含响应正文或凭据。

---

## 步骤 7：增加轻量数据集描述

**文件**：`scripts/sync_qq_jobs.py`

**位置**：DatasetSpec 与 DATASETS

使用不可变 dataclass 声明 view_name、data_path、content_path、weight、hidden_fields 和 field_labels；循环执行共享 probe、validate、merge、render。

**当前代码**：
```python
scripts/sync_qq_jobs.py 当前不存在。
```

**修改后代码**：
```python
定义 DatasetSpec dataclass，并在 DATASETS 中声明每日更新和秋招提前批两项及各自展示投影。
```

**执行说明**：

- 不增加插件加载、动态模块发现或外部配置文件。
- 字段 schema 继续从源数据结构读取并保存在各自快照中。

---

## 配置文件调整

- 文件：`GitHub Repository Secret`；位置：Settings > Secrets and variables > Actions；调整：创建 QQ_DOCS_STORAGE_STATE_B64，保存专用账号 Playwright storage state 的 Base64；会话过期后重复一次可见登录并覆盖该 Secret。；检查：手动运行 probe-only workflow，确认两个数据集名称、记录数和哈希摘要通过。
- 文件：`.github/workflows/qq-jobs-sync.yml`；位置：on.schedule；调整：使用 0 */3 * * *，按 UTC 每 3 小时运行一次。
- 文件：`.github/workflows/qq-jobs-sync.yml`；位置：workflow_dispatch.inputs.accept_source_deletions；调整：默认 false；人工核对源表后才允许将缺失记录标记为源表已移除。

---

## PB 协议调整

- 本需求不涉及

---

## 无极表调整

- 本需求不涉及

---

## 数据流总结

专用账号可见登录 -> Playwright storage state -> GitHub Actions 加密 Secret -> runner 临时文件 -> 腾讯文档结构化网络响应 -> 两次全量采集与一致性校验 -> 两个独立 JSON 快照 -> 历史合并与删除保护 -> 两个 Markdown 页面 -> Hugo 全站构建 -> 白名单提交默认分支 -> 触发 Pages 发布。

DATASETS 清单 -> 逐数据集调用同一采集/校验/合并/渲染流程 -> 独立 JSON 与 Markdown。

---

## 测试步骤

- 文件：`tests/test_sync_qq_jobs.py`；调整：运行 python3 -m unittest discover -s tests -p test_sync_qq_jobs.py。
- 文件：`scripts/sync_qq_jobs.py`；调整：使用专用账号会话执行 probe-only，两次采集的视图、schema、记录 ID、总数和链接哈希必须一致。
- 文件：`Hugo`；调整：运行 hugo --minify，并解析生成 HTML，确认两个页面存在；有效 URL 与快照逐字一致，源值中的控制回车和首尾空白允许按 HTML 标准规范化。
- 文件：`Git 变更白名单`；调整：workflow 只允许两个 JSON 和两个生成页面发生变化。
- 文件：`tests/test_sync_qq_jobs.py`；调整：验证两个不同 schema 的 DatasetSpec 共用同步逻辑、一条企业一行、日期降序、秋招字段隐藏与标签改名。

## 手工验证

- 调整：在当前 feature/qiuzhao 分支实施；首次发布前逐数据集核对源端记录总数、字段名、每行链接数与快照哈希。
- 调整：在一次性可见浏览器中使用专用账号登录并确认两个数据集可见，生成 storage state 后立即写入 QQ_DOCS_STORAGE_STATE_B64，随后删除本地会话文件。
- 调整：手动运行 probe-only 验证 GitHub runner 能加载登录态和完整数据，再运行正式同步；任何门槛失败均不发布。
- 调整：确认 goclub.space 的求职就业、每日更新、秋招提前批页面可访问，且原有内推入口保留；抽查包含 0/O、查询参数和多链接的记录与源文档完全一致。

---

## 改动风险与注意事项

- 腾讯文档登录会话会过期；workflow 会将登录页识别为会话失效并告警，需要人工刷新 Secret。
- 腾讯可能拦截 GitHub 云端 IP 或修改 newOpenSvc 协议；同步将失败关闭并保留旧数据，无法在无稳定官方接口时承诺永久自动运行。
- storage state 属于敏感凭据；专用账号应只用于该公开文档，Secret 不进入 PR、日志、Artifact 或仓库文件。
- 源端在两次采集之间发生修改会造成结果不一致；workflow 重试后仍不一致则延后到下一轮。
- HTML 会按标准规范化 URL 属性中的控制回车和首尾空白；JSON 快照与生成 Markdown 逐字保留源值，并在写入前回读校验全部链接。当前 1726 条链接中有 4 条源值包含这类空白，其余链接在 Hugo 最终 HTML 中逐字符一致。
- 首次全量对账通过前只允许探针和测试，不发布未经核验的数据。
- 腾讯协议差异应封装在 QQDocsSource 内，避免 DatasetSpec 承担协议解析逻辑。
