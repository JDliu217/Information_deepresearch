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
| DataAnalyst | 待建立 `DataAnalystAgent` | 未实现 |
| CodeWizard | 待建立 `CodeWizardAgent` | 未实现 |
| LeadWriter | `WriterAgent` | 已有简化版 |
| CriticMaster | `CriticAgent` | 已有简化版 |
| V2 Graph | `ResearchWorkflow` | 已有简化版 |

## 2. 必须保留的状态数据

最终的 `ResearchState` 至少要能表达这些内容：

- 用户问题、会话 ID、当前阶段和迭代次数
- 章节大纲、研究子问题、研究假设和关键实体
- 原始来源、结构化事实和数据点
- 洞察、知识图谱、图表配置和代码执行记录
- 草稿、最终报告和参考文献
- 审核意见、质量评分和待补充搜索查询
- 事件消息、日志、错误和任务状态

当前 `iteration-03` 已经把假设证据、数据点和基础知识图谱接入 `FactExtractorAgent`；
数据分析、图表和检查点仍在后续迭代逐步补齐，避免一次性复制原项目的大状态对象。

## 3. 必须保留的审核路由

审核结束后必须支持三种结果：

1. `pass`：研究完成。
2. `needs_revision` 且需要新证据：补充搜索，重新写作，再次审核。
3. `needs_revision` 但不需要新证据：根据审核意见修订报告，再次审核。

达到最大迭代次数时，流程可以结束，但必须保留最后一次审核结果和质量评分。

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
| `iteration-04` | 实现 DataAnalyst，输出洞察和 ECharts 配置 |
| `iteration-05` | 实现 CodeWizard，完成受限代码执行和图表记录 |
| `iteration-06` | 完善章节写作、引用和结构化审核反馈 |
| `iteration-07` | 增加 FastAPI SSE 单一研究接口 |
| `iteration-08` | 增加检查点、恢复和取消 |
| `iteration-09` | 接入真实 LLM、Bocha 搜索和可选本地知识库 |
| `iteration-10` | 建立简化前端 |
| `iteration-11` | 完成端到端测试、V1 清理和文档整理 |

每个迭代都必须先通过 Mock 测试，再考虑真实服务或外部基础设施。
