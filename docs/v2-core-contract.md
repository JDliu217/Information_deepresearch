# V2 核心功能对照契约

这份文档用来约束学习版的长期方向。

原项目的位置是 `D:\课\s4-6\industry_information_assistant`，学习版的位置是
`D:\课\s4-6\information_deepresearch`。学习版会重新组织代码，但必须保留原项目
V2 的核心研究行为。

## 1. 最终核心链路

```text
用户问题
  -> ChiefArchitect：规划大纲、研究问题和假设
  -> DeepScout：搜索来源、深读内容、提取事实和数据
  -> DataAnalyst：整理数据点、洞察、知识图谱和图表配置
  -> CodeWizard：执行分析代码并生成图表
  -> LeadWriter：撰写带引用的研究报告
  -> CriticMaster：审核报告质量
  -> 通过 / 补充搜索后重写 / 根据意见修订
```

学习版当前使用更容易理解的名称：

| 原项目 V2 角色 | 学习版角色 | 当前状态 |
| --- | --- | --- |
| ChiefArchitect | `PlannerAgent` | 已有简化版 |
| DeepScout | `ResearcherAgent` + `FactExtractorAgent` | 已有简化版 |
| DataAnalyst | `DataAnalystAgent` | 已有 Mock 版：从数据点生成洞察和 ECharts 配置 |
| CodeWizard | `CodeWizardAgent` | 已有受限统计执行版；Docker 隔离待后续实现 |
| LeadWriter | `WriterAgent` | 已有简化版 |
| CriticMaster | `CriticAgent` | 已有简化版 |
| V2 Graph | `ResearchGraphRuntime` + `app.graph` | I8 已删除 ResearchWorkflow，LangGraph runtime 是唯一入口 |

## 2. 必须保留的状态数据

最终的 `ResearchState` 至少要能表达这些内容：

- 用户问题、会话 ID、当前阶段和迭代次数
- 章节大纲、研究子问题、研究假设和关键实体
- 原始来源、结构化事实和数据点
- 洞察、知识图谱、图表配置和代码执行记录
- 草稿、最终报告和参考文献
- 审核意见、质量评分和待补充搜索查询
- 事件消息、日志、错误和任务状态

当前 `iteration-04` 已经把假设证据、数据点和基础知识图谱接入 `FactExtractorAgent`，
并由 `DataAnalystAgent` 生成洞察和 ECharts 配置，交给 CodeWizard、Writer 和 Critic 使用。
当前 CodeWizard 只解释少量统计表达式，记录执行状态、输出和错误；它不是最终的安全沙箱，
复杂 Python、Pandas 和图像生成要在后续 Docker 执行器中实现。

`iteration-06` 已经把 CriticMaster 的审核输入和输出细化为章节级结构：审核上下文包含章节草稿、
章节事实、章节来源、完整报告、数据点、洞察、图表和代码执行记录；审核结果包含总体结论、质量
评分、逐条结构化问题、事实核查、遗漏方面、优点、补充搜索查询和是否需要新研究。旧的
`review_result["issues"]` 字符串列表仍然保留，完整问题保存在 `structured_issues` 中。

## 3. 必须保留的审核路由

审核结束后必须支持三种结果：

1. `pass`：研究完成。
2. `needs_revision` 且需要新证据：补充搜索，重新写作，再次审核。
3. `needs_revision` 但不需要新证据：根据审核意见修订报告，再次审核。

达到最大迭代次数时，流程可以结束，但必须保留最后一次审核结果和质量评分。

审核路由按以下规则执行：缺少来源、内容不完整或信息过期等重大问题会进入补充搜索；其他问题
直接进入 Writer 修订。补充搜索查询会合并 Critic 给出的查询、问题级查询和遗漏方面，并去重后
限制数量，避免一次审核产生无限查询。

`iteration-07` 使用 LangGraph 的 `StateGraph` 编排同一条 V2 主链路。I8 删除了旧的
`ResearchWorkflow`，由 `ResearchGraphRuntime` 负责创建 Agent、运行编译后的图、适配
事件并可选地接入 Repository。图状态只使用一种 `ResearchState` 业务模型；每个 Agent
节点调用 I1 到 I6 已有的 Agent，并显式写回更新后的状态。审核后的条件边分别进入补充
研究、Writer 修订或完成节点，并在下一轮回到 Critic。阶段开始事件在 Agent 执行前由
独立节点发出。`ResearchGraphRuntime.run()` 返回最终 `ResearchState`，
`ResearchGraphRuntime.stream()` 只转发 `ResearchEvent`，所以后续 FastAPI SSE 不需要
读取 LangGraph 的内部更新对象。

I8 的 `ResearchRepository` 使用 SQLAlchemy 保存研究状态快照和有序事件；PostgreSQL
表结构由 Alembic 管理。runtime 负责在图节点更新后调用 Repository，Agent 不直接访问
数据库。

`iteration-09` 增加 `RunControlStore`，用 Redis 保存短期运行摘要和取消标志。runtime
在开始、节点更新、完成和异常时更新摘要；收到取消请求后，在下一个 LangGraph 节点边界
停止。内存实现用于 Mock 测试，Redis 实现用于真实部署。本轮尚未启用检查点、恢复和
SSE 接口。

## 4. 必须保留的对外结果

最终结果必须包含：

- 研究报告
- 报告引用的来源
- 结构化事实
- 数据点和洞察（如果问题产生了数据）
- 图表结果（如果问题需要图表）
- 审核结论和质量评分
- 研究迭代次数

## 5. 版本边界

学习版最终只保留 V2 研究入口：

- 不保留 `version: v1/v2` 切换参数。
- 不复制 V1 的 ReAct 研究服务和旧路由。
- 不复制与核心研究无关的新闻、招投标、复杂知识库管理页面。
- 前端只展示问题输入、研究进度、报告、引用和图表。

## 6. 迭代验收顺序

| 迭代 | 验收重点 |
| --- | --- |
| `iteration-01` | Mock 环境下跑通规划、搜索、事实、写作、审核和内部事件流 |
| `iteration-02` | 对齐状态模型和事件协议，建立本契约对应的领域对象 |
| `iteration-03` | 增加假设驱动研究、数据点和知识图谱基础 |
| `iteration-04` | 实现 DataAnalyst，输出洞察和 ECharts 配置，并接入报告与事件流 |
| `iteration-05` | 实现 CodeWizard，完成受限统计执行、错误重试、执行记录和工作流接入 |
| `iteration-06` | 完善章节级审核上下文、引用追踪、结构化 CriticMaster 反馈和审核路由 |
| `iteration-07` | 使用 LangGraph 编排唯一的 V2 主工作流，保留 `run()`、`stream()` 和事件协议 |
| `iteration-08` | PostgreSQL、SQLAlchemy、Alembic、Repository 和 LangGraph runtime 持久化接入 |
| `iteration-09` | Redis 运行状态、取消标志、内存测试实现和 runtime 控制接口 |
| `iteration-10` | FastAPI SSE 接口、检查点、恢复和取消 |
| `iteration-11` | 真实 LLM、Bocha 搜索和网页来源提取 |
| `iteration-12` | RAG、Embedding、Milvus 和本地知识库 |
| `iteration-13` | Text2SQL 和数据库探索 |
| `iteration-14` | 长期记忆层；根据核心链路实际需要确定接入点 |
| `iteration-15` | 简化前端和研究历史展示 |
| `iteration-16` | Docker 执行隔离、端到端测试和文档整理 |

每个迭代都必须先通过 Mock 测试，再考虑真实服务或外部基础设施。
