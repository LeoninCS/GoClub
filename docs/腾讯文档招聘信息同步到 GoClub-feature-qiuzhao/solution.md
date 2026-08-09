# 腾讯文档招聘信息同步到 GoClub 技术方案

## 需求概述

从公开腾讯智能表格 DUXJLSnZoTVFhVUVs 的“每日更新”和“秋招提前批”完整同步招聘信息与原始投递链接到 GoClub 现有的“求职就业”一级栏目；两个数据集独立存放；在 feature/qiuzhao 分支实施；每 3 小时自动更新；以专用腾讯账号会话作为 GitHub Actions Secret；要求完整性校验、避免重复和错链、失败保留旧数据、最小改动并保留轻量扩展点。

## 项目上下文

- 项目：GoClub
- 项目路径：`D:\APP\Path_for_ide\Go\item\GoClub`
- 开始分支：`feature/qiuzhao`

## 已确认项目事实

- Project contains 2000 scannable files.（位置：`D:\APP\Path_for_ide\Go\item\GoClub`）
- GoClub 是 Hugo 静态站，主内容位于 content/docs，推送 main 后由 GitHub Pages workflow 构建发布。（位置：`hugo.toml; .github/workflows/static.yml`）
- 仓库已有 Python 内容同步、Hugo 全站构建、限制变更文件、由 github-actions[bot] 提交并触发发布的自动化模式，可直接复用其结构。（位置：`scripts/sync_daily_question.py; .github/workflows/daily-question-sync.yml`）
- 目标腾讯智能表格公开链接可匿名读取文档元信息，文档 ID 为 DUXJLSnZoTVFhVUVs，内部 padId 为 QrKJvhMQaUEl，给定视图 ID 为 sc_K49vrh。（位置：`https://docs.qq.com/smartsheet/DUXJLSnZoTVFhVUVs?tab=sc_K49vrh`）
- 该公开链接权限明确关闭复制和普通导出；canRead 为 true，canCopy/canExport/canExportOnline 为 false。（位置：`腾讯文档 basicClientVars.authInfo.attribute`）
- 腾讯智能表格当前使用 newOpenSvc 数据链路；公开 opendoc 只返回权限、表 ID 与临时会话信息，自动化 Chromium 被导向安全拦截页，未获得完整行数据。（位置：`腾讯文档公开页面及 /dop-api/opendoc 只读探测`）
- 用户确认招聘信息不放在 resources 下，需在 content/docs 中新建与现有一级栏目同级的独立栏目。（位置：`用户确认 2026-08-03`）
- 用户无法联系腾讯文档所有者，当前无法获得导出、官方 API 授权或 CSV/JSON 镜像等稳定入口。（位置：`用户确认 2026-08-03`）
- “招聘信息”一级栏目下分为“每日更新”和“秋招提前批”两个独立子部分；两者字段不同，各自独立存储和展示，不强制合并成统一字段表。（位置：`用户确认 2026-08-04`）
- 最新 main 已新增“求职就业”一级栏目；用户确认取消单独的“招聘信息”一级栏目，将“每日更新”和“秋招提前批”直接放在“求职就业”下并与“内推”并列。（位置：`用户确认 2026-08-09`）
- 一个源记录或单元格包含多个招聘链接时全部保留，并按各自源字段标注。（位置：`用户确认 2026-08-04`）
- 源记录修改时按记录 ID 更新；源记录删除时保留历史并标记源表已移除。（位置：`用户确认 2026-08-04`）
- 保留腾讯文档中的原始链接并单独检测可访问性，不使用跳转后的地址改写原链接。（位置：`用户确认 2026-08-04`）
- 首次上线前执行两个数据集的全量人工对账并建立记录 ID、数量和链接哈希基线。（位置：`用户确认 2026-08-04`）
- 同步失败或记录数异常下降时创建 GitHub Issue；在当前 feature/qiuzhao 分支实施，并每 3 小时运行一次。（位置：`用户确认 2026-08-04；分支更新 2026-08-07`）
- 首版只使用 GitHub Actions；用户电脑无需开机。公开数据链路探针不满足完整性门槛时停止发布、保留旧数据并创建 GitHub Issue，再单独决定其他运行方式。（位置：`用户确认 2026-08-04`）
- 2026-08-04 使用全新无登录态 Chrome 只读探测目标链接时，页面标题可读取，但正文明确显示“此文档已设置权限，请登录后使用”，未发起任何包含表格记录的数据请求。（位置：`Chrome DevTools Protocol 公开页面探针 2026-08-04`）
- canRead=true 只表示文档权限元数据允许读取，实际记录仍受腾讯账号登录门槛保护；纯匿名 GitHub Actions 当前无法取得“每日更新”和“秋招提前批”数据。（位置：`公开页面 basicClientVars 与实际页面探针联合验证`）
- 用户已使用专用腾讯账号登录腾讯文档，并确认该账号打开原链接后可以看到“每日更新”和“秋招提前批”的实际行数据与链接。（位置：`用户确认 2026-08-06`）
- 用户最终确认生成方案，并再次要求保持最小改动，同时为未来增加同类招聘数据集保留清晰扩展点。（位置：`用户确认 2026-08-06`）
- 本需求已明确在当前 feature/qiuzhao 分支实施。（位置：`用户确认 2026-08-07`）

## 最终方案

### 采用专用账号会话的双数据集招聘同步
在 main 现有的 content/docs/jobs“求职就业”一级栏目下新增两个独立子页面，并在栏目首页增加入口；每个页面以一条企业一行的宽表展示，每 15 条分页并由独立容器提供横向滚动，不展示腾讯源表入口；使用专用账号会话驱动每 3 小时一次的 GitHub Actions，同步两个独立数据集，并以失败关闭、历史保留和哈希对账防止遗漏、重复与链接错写。

选择理由：目标文档的实际记录要求登录，匿名探针只能读取标题和权限元数据。专用账号已经确认可看到两个数据集；GitHub Actions 可复用仓库已有的默认分支检出、Hugo 全站构建、白名单提交和 Pages 触发模式，同时避免用户电脑持续开机。两个源数据集字段不同，独立快照和独立页面可以保留源字段含义并减少页面框架改动。

### 以 DatasetSpec 保留轻量扩展点
扩展边界保持在单脚本的声明式数据集清单，当前配置视图、目标文件、隐藏字段和显示标签；未来新增同类数据集时增加一项配置和对应内容文件。

选择理由：该边界消除两个数据集之间的流程复制，同时避免引入插件系统、通用 ETL 框架、数据库或额外服务，符合仓库规模和最小改动要求。

## 接口与数据调整

- 新增 scripts/sync_qq_jobs.py 命令行入口，支持 source URL、storage state、数据目录、内容目录、只读探针、链接检查和显式确认源删除。
- 新增 GitHub Actions Secret QQ_DOCS_STORAGE_STATE_B64，内容为专用腾讯账号 Playwright storage state 的 Base64。
- 新增 qq-jobs-sync workflow_dispatch 手动入口和每 3 小时 schedule。
- 新增 data/jobs/daily-updates.json，独立保存“每日更新”的源视图、字段 schema、同步摘要、记录和原始链接。
- 新增 data/jobs/early-recruitment.json，独立保存“秋招提前批”的源视图、字段 schema、同步摘要、记录和原始链接。
- 复用 content/docs/jobs 下的“求职就业”栏目索引并新增两个生成页面。

## 联调边界

- 不修改 themes、layouts、assets、SCSS、现有栏目内容和现有每日一问同步职责。
- 不新增后端服务、数据库、管理后台或本机常驻定时任务。
- 不提交、打印或上传腾讯账号密码、Cookie、Token 和 storage state。
- 结构化数据无法提供稳定记录 ID、字段 ID、完整分页结束条件和可核对总量时，停止发布并保留上次成功内容。
- 不实现插件系统、通用同步框架或动态配置中心。

## 风险与注意事项

- 腾讯文档登录会话会过期；workflow 会将登录页识别为会话失效并告警，需要人工刷新 Secret。
- 腾讯可能拦截 GitHub 云端 IP 或修改 newOpenSvc 协议；同步将失败关闭并保留旧数据，无法在无稳定官方接口时承诺永久自动运行。
- storage state 属于敏感凭据；专用账号应只用于该公开文档，Secret 不进入 PR、日志、Artifact 或仓库文件。
- 源端在两次采集之间发生修改会造成结果不一致；workflow 重试后仍不一致则延后到下一轮。
- HTML 会按标准规范化 URL 属性中的控制回车和首尾空白；JSON 快照与生成 Markdown 逐字保留源值，并在写入前回读校验全部链接。当前 1726 条链接中有 4 条源值包含这类空白，其余链接在 Hugo 最终 HTML 中逐字符一致。
- 首次全量对账通过前只允许探针和测试，不发布未经核验的数据。
- 腾讯协议差异应封装在 QQDocsSource 内，避免 DatasetSpec 承担协议解析逻辑。
