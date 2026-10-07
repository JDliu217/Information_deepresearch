# Industry DeepResearch 学习项目

这是从原行业信息助手项目重新搭建的学习版。

## 学习目标

逐步实现一个完整的 DeepResearch 后端链路：

```text
用户问题 -> 研究规划 -> 信息搜索 -> 证据整理 -> 数据分析 -> 报告撰写 -> 质量审核
```

早期迭代先关注代码结构和数据流；当前已经加入 PostgreSQL 持久化，Docker、登录和复杂前端仍放在后续迭代。

## 当前迭代

- iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
- iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
- iteration-03：完成假设证据关联、结构化数据点和基础知识图谱。
- iteration-04：加入 DataAnalyst，从数据点生成洞察和 ECharts 配置，并接入报告和事件流。
- iteration-05：加入 CodeWizard、受限统计表达式执行、错误重试和代码执行记录。
- iteration-06：完善章节级审核上下文、结构化 Critic 反馈、事实核查和审核路由。
- iteration-07：使用 LangGraph 编排唯一的 V2 主工作流，保留原有事件流接口。
- iteration-08：加入 SQLAlchemy 持久化模型、Repository 和 Alembic 迁移，并接入 LangGraph runtime。
- iteration-09：加入 Redis 运行状态、取消标志和 runtime 控制接口。
- 后续迭代：加入 SSE、检查点、本地知识库、真实服务和简化前端。

## 学习方式

每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。

## 当前已跑通的后端链路

```text
用户问题
  -> Planner 生成章节大纲
  -> Researcher 按章节查询搜索来源
  -> FactExtractor 整理带章节关联的事实、假设证据、数据点和知识图谱
  -> DataAnalyst 生成数据洞察和 ECharts 配置
  -> CodeWizard 生成并执行受限统计表达式，记录代码结果
  -> Writer 逐章生成草稿，再整合报告
  -> Critic 按章节审核、核查事实，并决定通过、补充搜索或修订
  -> 返回最终报告、评分和引用
```

I6 的审核结果同时保留两种形式：`review_result["issues"]` 继续提供旧的字符串列表，
`review_result["structured_issues"]` 提供问题类型、严重程度、章节位置、证据、修复建议和
是否需要新搜索等字段。这样后续接入真实 LLM 时，旧调用方仍可工作，新的路由
逻辑也能使用完整审核信息。

当 Critic 发现缺少来源、内容不完整或信息过期等重大问题时，工作流会去重并限制补充查询，
重新执行研究阶段；只有逻辑表达、偏差或其他不需要新证据的问题时，才直接交给 Writer 修订。
审核事件还会带出事实核查结果、遗漏方面、报告优点和未解决问题数量。

`ResearchGraphRuntime` 提供两种调用方式：

- `await runtime.run(...)`：等待整条链路结束，返回 `ResearchState`。
- `async for event in runtime.stream(...)`：按阶段取得进度事件，最后收到完整结果。

事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。

从 I7 开始，节点编排由 `backend/app/graph/research_graph.py` 中的 LangGraph
`StateGraph` 负责。I8 删除了 `ResearchWorkflow`，`ResearchGraphRuntime` 是唯一的
V2 运行入口，并把图节点更新转换为对外研究事件，因此调用方不需要了解 LangGraph
的内部格式。LangGraph 负责流程和分支；Planner、Researcher、Writer、Critic 等 Agent
仍然是独立的业务组件。每个 Agent 节点显式写回 `ResearchState`，阶段开始事件在耗时
Agent 运行前发出。

I8 的 Repository 接在 runtime 和数据库之间：runtime 保存研究状态快照并追加事件，
`ResearchRepository` 负责 SQLAlchemy 数据访问，Agent 不直接操作数据库。PostgreSQL
表结构由 Alembic 迁移创建；本地测试使用 SQLite 验证相同的数据访问契约。检查点和
恢复将在后续迭代接入。

I9 增加了 `RunControlStore`。`InMemoryRunControlStore` 用于本地测试，
`RedisRunControlStore` 用于真实运行环境。runtime 会在开始、节点更新、完成和异常时更新
运行摘要；调用 `runtime.request_cancel(session_id)` 会设置取消标志，流程在下一个图节点
边界停止并标记为 `cancelled`。Redis 只保存短期运行控制数据，完整状态和事件仍由 I8
的 PostgreSQL Repository 保存。

事件类型包括 `research_started`、`phase_started`、`outline_ready`、
`research_evidence_ready`、`analysis_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
`draft_ready` 事件还包含 `outline` 和 `draft_sections`，可以按章节读取中间结果。
`analysis_ready` 事件包含洞察、数据点和 ECharts 配置；最终的 `research_completed`
事件还包含 CodeWizard 的执行记录；最终的 `research_completed` 事件包含报告、审核结果、质量评分、引用和分析结果。
所有事件都有 `type`、`session_id`、`phase` 和 `iteration`；每种事件的必需业务字段
见 `backend/app/domain/events.py` 中的 `EVENT_REQUIRED_FIELDS`。

## 本地验证

在本机 Windows 环境中，LangGraph 1.2.14 的依赖使用 64 位 Python 安装。本机默认的
`python` 是 32 位，因此先用已安装的
64 位 Python 3.13 建立虚拟环境：

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv\Scripts\python.exe -r backend\requirements.txt
```

测试事件流：

```powershell
$env:PYTHONPATH = "backend"
.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
```

## 命令行运行

在项目根目录执行：

```powershell
$env:PYTHONPATH = "backend"
.venv\Scripts\python.exe -m app.scripts.run_research "中国新能源汽车行业的发展趋势是什么？"
```

不传问题时，会进入交互式输入：

```powershell
.venv\Scripts\python.exe -m app.scripts.run_research
```

## 数据库迁移

默认数据库地址来自 `DATABASE_URL` 环境变量：

```text
postgresql+psycopg://postgres:postgres@localhost:5432/information_deepresearch
```

初始化或升级表结构：

```powershell
$env:PYTHONPATH = "backend"
.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

I8 的持久化对象是 `research_runs`（最新状态快照）和 `research_events`（按序事件记录）。
