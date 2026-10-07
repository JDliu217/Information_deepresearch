# Industry DeepResearch 学习项目

这是从原行业信息助手项目重新搭建的学习版。

## 学习目标

逐步实现一个完整的 DeepResearch 后端链路：

```text
用户问题 -> 研究规划 -> 信息搜索 -> 证据整理 -> 数据分析 -> 报告撰写 -> 质量审核
```

第一阶段只关注代码结构和数据流，不加入数据库、Docker、登录和复杂前端。

## 当前迭代

- iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
- iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
- iteration-03：完成假设证据关联、结构化数据点和基础知识图谱。
- iteration-04：加入 DataAnalyst，从数据点生成洞察和 ECharts 配置，并接入报告和事件流。
- iteration-05：加入 CodeWizard、受限统计表达式执行、错误重试和代码执行记录。
- iteration-06：完善章节级审核上下文、结构化 Critic 反馈、事实核查和审核路由。
- 后续迭代：加入 LangGraph、检查点、本地知识库和简化前端。

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
是否需要新搜索等字段。这样后续接入真实 LLM 或 LangGraph 时，旧调用方仍可工作，新的路由
逻辑也能使用完整审核信息。

当 Critic 发现缺少来源、内容不完整或信息过期等重大问题时，工作流会去重并限制补充查询，
重新执行研究阶段；只有逻辑表达、偏差或其他不需要新证据的问题时，才直接交给 Writer 修订。
审核事件还会带出事实核查结果、遗漏方面、报告优点和未解决问题数量。

工作流提供两种调用方式：

- `await workflow.run(...)`：等待整条链路结束，返回 `ResearchState`。
- `async for event in workflow.stream(...)`：按阶段取得进度事件，最后收到完整结果。

事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。

事件类型包括 `research_started`、`phase_started`、`outline_ready`、
`research_evidence_ready`、`analysis_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
`draft_ready` 事件还包含 `outline` 和 `draft_sections`，可以按章节读取中间结果。
`analysis_ready` 事件包含洞察、数据点和 ECharts 配置；最终的 `research_completed`
事件还包含 CodeWizard 的执行记录；最终的 `research_completed` 事件包含报告、审核结果、质量评分、引用和分析结果。
所有事件都有 `type`、`session_id`、`phase` 和 `iteration`；每种事件的必需业务字段
见 `backend/app/domain/events.py` 中的 `EVENT_REQUIRED_FIELDS`。

测试事件流：

```powershell
$env:PYTHONPATH = "backend"
python -m unittest discover -s backend/tests -v
```

## 命令行运行

在项目根目录执行：

```powershell
$env:PYTHONPATH = "backend"
python -m app.scripts.run_research "中国新能源汽车行业的发展趋势是什么？"
```

不传问题时，会进入交互式输入：

```powershell
python -m app.scripts.run_research
```
