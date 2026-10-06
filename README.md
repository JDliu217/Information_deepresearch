# Industry DeepResearch 学习项目

这是从原行业信息助手项目重新搭建的学习版。

## 学习目标

逐步实现一个完整的 DeepResearch 后端链路：

```text
用户问题 -> 研究规划 -> 信息搜索 -> 证据整理 -> 报告撰写 -> 质量审核
```

第一阶段只关注代码结构和数据流，不加入数据库、Docker、登录和复杂前端。

## 当前迭代

- iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
- iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
- 后续迭代：加入结构化数据分析、图表、检查点、本地知识库和简化前端。

## 学习方式

每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。

## 当前已跑通的后端链路

```text
用户问题
  -> Planner 生成章节大纲
  -> Researcher 按章节查询搜索来源
  -> FactExtractor 整理带章节关联的事实
  -> Writer 逐章生成草稿，再整合报告
  -> Critic 审核并决定通过、补充搜索或修订
  -> 返回最终报告、评分和引用
```

工作流提供两种调用方式：

- `await workflow.run(...)`：等待整条链路结束，返回 `ResearchState`。
- `async for event in workflow.stream(...)`：按阶段取得进度事件，最后收到完整结果。

事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。

事件类型包括 `research_started`、`phase_started`、`outline_ready`、
`research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
`draft_ready` 事件还包含 `outline` 和 `draft_sections`，可以按章节读取中间结果。
最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。
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
