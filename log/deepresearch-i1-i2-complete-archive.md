# Information DeepResearch：iteration-01 到 iteration-02 完整开发与问答归档

> 这是一份可独立保存、以后反复查阅的学习档案。原始问答不压缩、不改写、不删重复内容；修改过程说明、校订说明与原文分别存放。

## 目录

- [一、归档范围与阅读方法](#archive-scope)
- [二、全部修改节点与问答索引](#archive-index)
- [三、按修改过程整理的详细说明](#archive-stages)
- [四、历次提问、过程说明与回答完整原文](#archive-qa)
- [五、版本区别与校订注释](#archive-corrections)
- [六、全部 Git 文件差异](#archive-diffs)
- [七、i1 与 i2 全部跟踪文件完整快照](#archive-snapshots)
- [八、两个正式完成版的测试证据](#archive-tests)
- [九、i2 之后的单独补充](#archive-after-i2)
- [十、完整性检查与归档说明](#archive-integrity)

<a id="archive-scope"></a>
## 一、归档范围与阅读方法

### 1. 固定的是历史版本，不是持续更新的当前目录

项目位置：`D:\课\s4-6\information_deepresearch`。

正式归档从仓库初始化开始，包含 iteration-01 的搭建、iteration-01 到 iteration-02 的升级及 iteration-02 收尾：

| 边界 | Git 标签 | 固定提交 | 完成时间（北京时间） |
| --- | --- | --- | --- |
| i1 完成版 | `iteration-01` | `787cd9a4ecfd496e17efbf522f765d013607e0db` | 2026-10-06 18:55:38 |
| i2 完成版 | `iteration-02`（本地显示为 `tags/iteration-02`） | `79db291dc0a1a7825b846d05516bce556f8976dc` | 2026-10-06 22:46:06 |

整理时项目已经进入 iteration-03，且存在 i2 之后的 `fccf339`。因此正文按上述提交固定；后续内容只放在第九部分，不混入 i2 的源码、差异和测试结果。

### 2. 这份记录包含什么

- 26 个 Git 历史节点：25 个主线节点及 1 个 GitHub 初始提交旁支；每个节点有修改目的、文件列表、差异统计、详细解释及完整 patch。
- 29 条历史聊天记录：28 条用户消息、36 条助手过程说明、27 条助手最终回答，共 91 段用户可见消息；按聊天原始时间顺序保留。
- i1 的全部 33 个、i2 的全部 37 个 Git 跟踪文本文件，共 70 份完整文件快照；包括源码、测试、初始化文件、README、忽略规则和契约文档。
- i1 的 39 项、i2 的 55 项测试实际执行结果，以及旧回答中需要补充或修正的概念。

“记录”按产品返回的历史 turn 划分，不等于完整的一问一答：第 4 条只有“agent”，没有独立回答；第 23 条是提问，第 24 条接续该提问给出回答。这里保留原来的分段，不擅自合并，也不补造不存在的回答。

### 3. 原文与归档者说明如何区分

第三部分是本次整理的修改过程说明；第四部分是过去的用户消息和助手回复原文；第五部分是根据固定源码重新核对后的校订。原回答的旧字段、旧行号、错字、重复内容、当时的判断及原有 Markdown 都不改写。原文中的文件链接指向实时项目，其行号和文件内容以后可能变化；需要核对当时代码时，请用本文件第六、七部分的固定历史内容。

原始聊天包含过程说明和最终回答，不包含内部推理、系统或开发者指令。工具执行本身不属于回答正文；可恢复的源码变化用 Git patch 和版本快照完整附录保存。没有证据的内容不会伪装成过去实际说过的话。

完整性的边界：Git 能恢复的是已经提交的文件修改，不能恢复每次未提交的临时编辑或保存动作。聊天也只能保留当前聊天工具实际返回的历史消息。本档案对已取回的这些记录逐项保留，不声称能凭空恢复不存在于历史中的临时版本。

### 4. 建议查阅顺序

第一次复习，先看第三部分的阶段说明，再沿“对应问答”跳到当时解释；想追代码怎么变化，查看第六部分完整 diff；想直接研究整个版本，查看第七部分完整源码。看到原文与现在源码不同，先查第五部分，不要把 i1、i2 和后续迭代的字段混用。

<a id="archive-index"></a>
## 二、全部修改节点与问答索引

### 1. 修改节点目录

以下时间都是北京时间。静态测试数指该提交里以 `test_` 开头的测试方法数量，只用于说明覆盖规模；不表示每个中间提交都在本次重新执行过。实际运行的两个正式完成版见第八部分。

| 节点 | 北京时间 | 提交 | 修改主题 | 静态测试数 |
| --- | --- | --- | --- | ---: |
| 1 | 2026-10-06 01:30:03 | [`2b63f68`](#commit-2b63f68) | 初始化学习项目：先划定范围 | 0 |
| 2 | 2026-10-06 01:33:37 | [`5c13222`](#commit-5c13222) | 共享状态 ResearchState：给一次研究任务建立总档案 | 2 |
| 3 | 2026-10-06 01:38:35 | [`3c5fca4`](#commit-3c5fca4) | BaseAgent：建立每个研究角色都遵守的接口 | 4 |
| 4 | 2026-10-06 02:19:07 | [`72a6f09`](#commit-72a6f09) | LLMClient 和 MockLLMClient：先接通大模型接口形状 | 8 |
| 5 | 2026-10-06 17:13:17 | [`45049a2`](#commit-45049a2) | PlannerAgent：把用户问题拆成可执行规划 | 11 |
| 6 | 2026-10-06 17:28:56 | [`7a483d7`](#commit-7a483d7) | SearchClient：定义统一来源格式与模拟搜索 | 15 |
| 7 | 2026-10-06 17:46:17 | [`b352eb6`](#commit-b352eb6) | ResearcherAgent：把规划子问题连接到搜索服务 | 18 |
| 8 | 2026-10-06 17:55:04 | [`13b6ffe`](#commit-13b6ffe) | FactExtractor：来源约束事实，不是客观真实性验证 | 22 |
| 9 | 2026-10-06 18:04:29 | [`63e065b`](#commit-63e065b) | Writer：第一次生成有引用链接的完整报告 | 25 |
| 10 | 2026-10-06 18:08:55 | [`87f7acf`](#commit-87f7acf) | Critic：审核结果和评分成为独立状态 | 29 |
| 11 | 2026-10-06 18:14:22 | [`861a4fa`](#commit-861a4fa) | ResearchWorkflow：五个 Agent 由同一编排器顺序调用 | 31 |
| 12 | 2026-10-06 18:20:01 | [`99f39af`](#commit-99f39af) | 命令行运行入口：不用写测试也能观察任务结果 | 33 |
| 13 | 2026-10-06 18:32:49 | [`64b3d07`](#commit-64b3d07) | 审核路由与修订循环：通过、补搜、仅重写三条路径 | 37 |
| 14 | 2026-10-06 18:55:38 | [`787cd9a`](#commit-787cd9a) | 内部进度事件流：iteration-01 完成版 | 39 |
| 15 | 2026-10-06 19:10:03 | [`ab7ffa3`](#commit-ab7ffa3) | V2 长期契约：把未来目标与当前实现分开 | 39 |
| 16（旁支） | 2026-10-06 19:16:41 | [`3986b40`](#commit-3986b40) | GitHub 旁支 Initial commit：不是第二次开发研究功能 | 0 |
| 17 | 2026-10-06 19:31:24 | [`0a892dc`](#commit-0a892dc) | README 合并：连接独立历史 | 39 |
| 18 | 2026-10-06 19:40:23 | [`39171ba`](#commit-39171ba) | V2 领域模型：Section、Hypothesis、DataPoint、Chart、CriticFeedback | 43 |
| 19 | 2026-10-06 20:26:52 | [`a974120`](#commit-a974120) | 扩展 ResearchState：先为 V2 产物预留位置 | 43 |
| 20 | 2026-10-06 21:01:20 | [`6bf3f4b`](#commit-6bf3f4b) | 全链路统一改名：plan→outline、sources→raw_sources、review→review_result | 43 |
| 21 | 2026-10-06 21:12:28 | [`b582dec`](#commit-b582dec) | Planner 使用 V2 数据对象并扩展规划输出 | 43 |
| 22 | 2026-10-06 21:30:02 | [`0c0ecb5`](#commit-0c0ecb5) | 来源与事实绑定章节：让资料知道自己服务哪一章 | 44 |
| 23 | 2026-10-06 21:43:26 | [`0387dc8`](#commit-0387dc8) | 章节级草稿：先逐章写，再整合整篇报告 | 45 |
| 24 | 2026-10-06 22:27:08 | [`99fe715`](#commit-99fe715) | 事件公共外壳校验：尽早拒绝错误通知单 | 52 |
| 25 | 2026-10-06 22:40:13 | [`fad4cdb`](#commit-fad4cdb) | 必需业务字段：每种事件不仅要有名字，也要带齐内容 | 54 |
| 26 | 2026-10-06 22:46:06 | [`79db291`](#commit-79db291) | 公共字段防覆盖、文档收尾与 iteration-02 正式标签 | 55 |


### 2. 完整聊天目录

“对应修改”表示该问答讨论的主要代码节点，不表示那条回答必然发生在提交之后。实时读取可能看到了尚未提交的变更，例如第 28 条已经读到后来进入 `79db291` 的公共字段防覆盖代码。

| 记录 | 北京时间 | 用户问题主题 | 对应修改 |
| --- | --- | --- | --- |
| [记录 1](#qa-1) | 2026-10-06 01:53:06 | 首次完整阅读项目 | `2b63f68`、`5c13222` |
| [记录 2](#qa-2) | 2026-10-06 01:56:02 | state.py 与 @dataclass 语法详解 | `5c13222` |
| [记录 3](#qa-3) | 2026-10-06 02:03:07 | Planner 等未来角色的判断依据 | `5c13222` |
| [记录 4](#qa-4) | 2026-10-06 02:04:12 | 单字补充 agent（无独立回答） | `3c5fca4` |
| [记录 5](#qa-5) | 2026-10-06 02:04:57 | __init__.py 是什么 | `3c5fca4` |
| [记录 6](#qa-6) | 2026-10-06 02:07:27 | BaseAgent 语法与职责 | `3c5fca4` |
| [记录 7](#qa-7) | 2026-10-06 02:21:25 | LLMClient 与 Mock 接口 | `72a6f09` |
| [记录 8](#qa-8) | 2026-10-06 17:19:31 | PlannerAgent 新增 | `45049a2` |
| [记录 9](#qa-9) | 2026-10-06 17:40:53 | SearchClient 新增 | `7a483d7` |
| [记录 10](#qa-10) | 2026-10-06 17:48:11 | ResearcherAgent 新增 | `b352eb6` |
| [记录 11](#qa-11) | 2026-10-06 17:57:53 | Researcher 如何调用 SearchClient | `7a483d7`、`b352eb6` |
| [记录 12](#qa-12) | 2026-10-06 18:00:39 | FactExtractor 新增 | `13b6ffe` |
| [记录 13](#qa-13) | 2026-10-06 18:06:17 | 事实提取是真的吗 | `13b6ffe` |
| [记录 14](#qa-14) | 2026-10-06 18:10:03 | Writer 和 Critic 新增 | `63e065b`、`87f7acf` |
| [记录 15](#qa-15) | 2026-10-06 18:15:16 | ResearchWorkflow 新增 | `861a4fa` |
| [记录 16](#qa-16) | 2026-10-06 18:20:04 | reviewing 如何变 completed | `87f7acf`、`861a4fa` |
| [记录 17](#qa-17) | 2026-10-06 18:26:59 | 命令行研究入口 | `99f39af` |
| [记录 18](#qa-18) | 2026-10-06 18:34:26 | 审核失败后的路由与循环 | `64b3d07` |
| [记录 19](#qa-19) | 2026-10-06 18:56:36 | 内部事件流新增 | `787cd9a` |
| [记录 20](#qa-20) | 2026-10-06 19:04:17 | 流与 SSE 的小白解释 | `787cd9a` |
| [记录 21](#qa-21) | 2026-10-06 20:17:55 | V2 领域模型与长期契约 | `ab7ffa3`、`39171ba` |
| [记录 22](#qa-22) | 2026-10-06 20:31:23 | 扩展共享状态 | `a974120` |
| [记录 23](#qa-23) | 2026-10-06 21:05:01 | 更新较多的提问（回答在下一记录） | `6bf3f4b` |
| [记录 24](#qa-24) | 2026-10-06 21:05:08 | 全链路 V2 字段改名 | `6bf3f4b` |
| [记录 25](#qa-25) | 2026-10-06 21:15:22 | V2 Planner 与章节来源关联 | `b582dec`、`0c0ecb5` |
| [记录 26](#qa-26) | 2026-10-06 22:15:05 | 章节草稿写作 | `0387dc8` |
| [记录 27](#qa-27) | 2026-10-06 22:28:43 | 事件公共外壳校验 | `99fe715` |
| [记录 28](#qa-28) | 2026-10-06 22:41:01 | 必需字段和公共字段保护 | `fad4cdb`、`79db291` |
| [记录 29](#qa-29) | 2026-10-06 22:50:29 | iteration-02 正式收尾 | `79db291` |


<a id="archive-stages"></a>
## 三、按修改过程整理的详细说明

以下按 Git 历史节点展开。i1 的搭建和升级不是一次性出现的：先建状态和接口，再把规划、搜索、事实、写作、审核串起来，最后加入修订和进度事件；i2 在这个基础上升级领域数据结构、章节关联、章节草稿和事件契约。

<a id="commit-2b63f68"></a>
### 修改节点 1：初始化学习项目：先划定范围

提交：`2b63f6879790ffa9f15df34ef876d61c32d92165`。时间：2026-10-06 01:30:03（北京时间）。

原始提交标题：chore: initialize learning project

父提交：无，根提交。

对应问答：[记录 1](#qa-1)。完整代码变化：[查看本节点 patch](#diff-2b63f68)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	.gitignore
A	README.md
```

差异统计：

```text
 .gitignore |  7 +++++++
 README.md  | 22 ++++++++++++++++++++++
 2 files changed, 29 insertions(+)
```

### 修改目的与前后变化
此前没有独立学习仓库；这次建立 README 和忽略规则，明确先做后端最小链路，不在第一轮同时引入数据库、Docker、登录和复杂前端。
README 中的流程图是目标说明，不表示所有 Agent 已经实现。这个区别正是后面用户追问“你从哪里知道未来要有 Planner 等角色”的背景。
.gitignore 忽略 __pycache__/、*.py[cod]、.venv/、.env、node_modules/、dist/、*.log。这是版本管理规则；.gitignore 文件不是 Planner 提交才首次出现，首次建立就在本次。
### 当前实际功能与测试
尚无 Python 研究链路、客户端或 Agent，静态测试数为 0。


<a id="commit-5c13222"></a>
### 修改节点 2：共享状态 ResearchState：给一次研究任务建立总档案

提交：`5c13222393099a5fe2dc98106e0a29f7f88c654d`。时间：2026-10-06 01:33:37（北京时间）。

原始提交标题：feat: add shared research state

父提交：2b63f6879790ffa9f15df34ef876d61c32d92165。

对应问答：[记录 1](#qa-1)、[记录 2](#qa-2)、[记录 3](#qa-3)。完整代码变化：[查看本节点 patch](#diff-5c13222)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/__init__.py
A	backend/app/domain/__init__.py
A	backend/app/domain/state.py
A	backend/tests/__init__.py
A	backend/tests/test_state.py
```

差异统计：

```text
 backend/app/__init__.py        |  1 +
 backend/app/domain/__init__.py |  1 +
 backend/app/domain/state.py    | 45 ++++++++++++++++++++++++++++++++++++++++++
 backend/tests/__init__.py      |  1 +
 backend/tests/test_state.py    | 27 +++++++++++++++++++++++++
 5 files changed, 75 insertions(+)
```

### 修改目的与前后变化
新增 app、domain、tests 的 __init__.py 和 state.py/test_state.py，开始表达一次任务的身份、输入和研究产物。
初始版本字段为 query、session_id、phase、iteration、max_iterations、plan、research_questions、sources、facts、references、final_report、review、quality_score、errors。此时合法历史名称确实是 plan/sources/review，不能把后来统一改名后的名称倒填进当时源码。
### 关键语法与数据流
@dataclass 为数据类生成构造函数、表示方法、比较方法等常用样板；ResearchState("一个研究问题") 因此能把位置参数填入 query。类型标注如 query: str 是类型提示，不会自动验证运行时输入。
field(default_factory=list/dict) 在每次创建状态时调用工厂，产生独立可变容器；default_factory 不是把 list 类本身保存为字段。session_id 的 lambda 每次调用 str(uuid4())，生成任务编号。state 不是全局数据库，每次 Workflow 创建一个任务状态，任务内多个 Agent 共享它。
### 用户追问的证据
“后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象”直接来自这个历史版本 state.py 顶部说明；README 也写了规划→搜索→证据整理→写作→审核。它是项目文本证据，不是猜测用户下一步意图。这时具体 Agent 尚未实现。
### 测试
新增两个测试：初始状态正确、不同实例的可变字段不共享。


<a id="commit-3c5fca4"></a>
### 修改节点 3：BaseAgent：建立每个研究角色都遵守的接口

提交：`3c5fca4848f93e9dedd744d5b1baf12f8b7c3058`。时间：2026-10-06 01:38:35（北京时间）。

原始提交标题：feat: add base research agent

父提交：5c13222393099a5fe2dc98106e0a29f7f88c654d。

对应问答：[记录 4](#qa-4)、[记录 5](#qa-5)、[记录 6](#qa-6)。完整代码变化：[查看本节点 patch](#diff-3c5fca4)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/__init__.py
A	backend/app/agents/base.py
A	backend/tests/test_base_agent.py
```

差异统计：

```text
 backend/app/agents/__init__.py   |  1 +
 backend/app/agents/base.py       | 22 ++++++++++++++++++++++
 backend/tests/test_base_agent.py | 33 +++++++++++++++++++++++++++++++++
 3 files changed, 56 insertions(+)
```

### 修改目的与前后变化
新增 agents/__init__.py、base.py、test_base_agent.py。此前只有数据容器；现在定义统一的角色接口，但没有任何真正的研究动作。
### 关键语法与调用约定
BaseAgent(ABC) 是抽象基类，name 默认 "base"；@abstractmethod 要求具体子类实现 async run(self, state) -> ResearchState。基类方法体的 raise NotImplementedError 表达“这里没有实现”；抽象类实例化检查和执行时的 NotImplementedError 是两个不同机制。
self 是实例；state 是外部传进来的同一个任务对象；return state 返回对象引用，并不重新创建一份状态。async def 定义协程，需要 await 或由事件循环运行；不是自动开启后台线程。具体 Agent 通过继承实现各自职责，Workflow 可以统一调用 agent.run(state)。
### __init__.py 和 __init__ 的区别
__init__.py 是包初始化模块，本项目文件里只有说明字符串，不执行研究业务。__init__ 是类实例的初始化方法，用来把传入客户端保存到 self.llm/self.search，两者不是同一回事。现代 Python 也支持没有 __init__.py 的命名空间包，原问答“没有这个文件绝对不能导入”的简化说法应按本节修正。
### 测试
不能直接实例化 BaseAgent；DemoAgent 能修改并返回原状态。总测试数增至 4。


<a id="commit-72a6f09"></a>
### 修改节点 4：LLMClient 和 MockLLMClient：先接通大模型接口形状

提交：`72a6f099a633217e33574f368fb7ff074d5bec56`。时间：2026-10-06 02:19:07（北京时间）。

原始提交标题：feat: add llm client abstraction

父提交：3c5fca4848f93e9dedd744d5b1baf12f8b7c3058。

对应问答：[记录 7](#qa-7)。完整代码变化：[查看本节点 patch](#diff-72a6f09)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/core/__init__.py
A	backend/app/core/llm_client.py
A	backend/tests/test_llm_client.py
```

差异统计：

```text
 backend/app/core/__init__.py     |  1 +
 backend/app/core/llm_client.py   | 85 ++++++++++++++++++++++++++++++++++++++++
 backend/tests/test_llm_client.py | 42 ++++++++++++++++++++
 3 files changed, 128 insertions(+)
```

### 修改目的与前后变化
新增 core 包、llm_client.py 和客户端测试。Agent 将依赖统一接口，而不是把某家模型 SDK 的细节混在业务代码里。
### 两种返回能力
complete_json(role, payload) 返回 dict，用来表达大纲、事实、审核结果等结构化数据；complete_text(role, payload) 返回 str，用来写报告。JSON 结构、Python 字典、JSON 文本不是完全同一概念；这里的接口直接返回 Python dict，不是已经发出的 HTTP 响应。
### Mock 的实际作用
MockLLMClient 是不联网的确定性实现。role 为 planner 时按固定模板产生三个章节和三个研究问题；最初 writer 只返回简单草稿。payload 的 instruction 不会使 Mock 获得智能理解能力。依赖注入的好处是后面可替换客户端实现，而 Agent 不需要改业务入口。
### 测试
四个客户端测试验证接口实现、规划结构、未知角色拒绝、写作文本，合计 8 个。此时还没有真实 LLM 请求、API key、token 调用或联网推理。


<a id="commit-45049a2"></a>
### 修改节点 5：PlannerAgent：把用户问题拆成可执行规划

提交：`45049a246c795bc0758e9fb985daafa17e909537`。时间：2026-10-06 17:13:17（北京时间）。

原始提交标题：feat: add planner agent

父提交：72a6f099a633217e33574f368fb7ff074d5bec56。

对应问答：[记录 8](#qa-8)。完整代码变化：[查看本节点 patch](#diff-45049a2)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/planner.py
A	backend/tests/test_planner.py
```

差异统计：

```text
 backend/app/agents/planner.py | 68 +++++++++++++++++++++++++++++++++++++++++++
 backend/tests/test_planner.py | 40 +++++++++++++++++++++++++
 2 files changed, 108 insertions(+)
```

### 修改目的与前后变化
新增 planner.py 和 test_planner.py，第一次真正把 BaseAgent、LLMClient、ResearchState 接起来。
### 实际执行顺序
构造函数接收 llm 并保存为 self.llm；run 从 state.query 取输入、strip 清理空白，空问题抛 ValueError；await complete_json(role="planner", payload=...)；_validate_plan 校验非空列表、每项字典、标题和描述；_validate_questions 校验研究问题；最后写 state.plan/state.research_questions，phase="planning"，返回原对象。
.get 用来带默认值读取字典；enumerate(..., start=1) 生成从 1 开始的编号；@staticmethod 表示校验帮助函数不需要实例状态。方法名以下划线开头是内部使用约定，不是 Python 强制访问限制。
### 范围与测试
生成的是固定 Mock 模板，不是理解行业之后推理出的规划；prompt 提到 2–4 个不重复问题，但校验并未严格验证数量、不重复和可搜索性。三个测试覆盖正常写回、空输入、无效返回，总 11。


<a id="commit-7a483d7"></a>
### 修改节点 6：SearchClient：定义统一来源格式与模拟搜索

提交：`7a483d72fb48acf4e1ea23869f7ab405c586ebce`。时间：2026-10-06 17:28:56（北京时间）。

原始提交标题：feat: add search client abstraction

父提交：45049a246c795bc0758e9fb985daafa17e909537。

对应问答：[记录 9](#qa-9)、[记录 11](#qa-11)。完整代码变化：[查看本节点 patch](#diff-7a483d7)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/core/search_client.py
A	backend/tests/test_search_client.py
```

差异统计：

```text
 backend/app/core/search_client.py   | 62 +++++++++++++++++++++++++++++++++++++
 backend/tests/test_search_client.py | 41 ++++++++++++++++++++++++
 2 files changed, 103 insertions(+)
```

### 修改目的与前后变化
新增 search_client.py/test_search_client.py。此前 Planner 能产出子问题但不能获取资料；现在定义可替换搜索服务接口。
### 数据对象和接口
SearchResult dataclass 包含 title、url、snippet、query、content，to_dict() 调用 asdict。SearchClient(ABC) 定义 async search(query, limit=3) -> list[SearchResult]，统一多个服务的返回结构。
### Mock 实际工作
MockSearchClient 校验查询非空、limit≥1，然后计算 SHA1 查询摘要的前 10 个字符，拼出 https://example.com/research/...，并生成固定摘要和正文。同查询的 URL 稳定便于测试去重，不代表抓取过网页、网址实际可访问或内容为真。limit 默认 3 是接口上限意图，当前 Mock 始终返回一条。
### 名称纠正与测试
项目文件叫 search_client.py，没有 research_client.py。后面 ResearcherAgent 调用的是真实接口对象的 search 方法；“调用了搜索接口”不等于“已经联网搜索”。四个新测试验证接口、格式、稳定 URL、输入校验，总 15。


<a id="commit-b352eb6"></a>
### 修改节点 7：ResearcherAgent：把规划子问题连接到搜索服务

提交：`b352eb6dba98266a2451f7767c129cba45c08c08`。时间：2026-10-06 17:46:17（北京时间）。

原始提交标题：feat: add researcher agent

父提交：7a483d72fb48acf4e1ea23869f7ab405c586ebce。

对应问答：[记录 10](#qa-10)、[记录 11](#qa-11)。完整代码变化：[查看本节点 patch](#diff-b352eb6)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/researcher.py
A	backend/tests/test_researcher.py
```

差异统计：

```text
 backend/app/agents/researcher.py | 61 ++++++++++++++++++++++++++++++++++++++++
 backend/tests/test_researcher.py | 46 ++++++++++++++++++++++++++++++
 2 files changed, 107 insertions(+)
```

### 修改目的与前后变化
新增 researcher.py/test_researcher.py，串联 Planner→Researcher。Researcher 不再只是设计名词，而是能把子问题逐一传给搜索对象。
### 如何调用客户端
外部创建 MockSearchClient()，再 ResearcherAgent(search_client)；__init__ 保存为 self.search。run 遍历 state.research_questions，调用 await self.search.search(query=question, limit=self.results_per_question)。Python 根据传入实例的实际类型执行 MockSearchClient.search；不是按变量名字寻找某个文件。
### 来源写回与去重
保留已有 sources，追加 result.to_dict()，按 URL 去重，保留第一次出现及原顺序；references 只收 title/url。phase 设 researching。初版一次查询接着一次查询顺序 await，不是所有查询并行发出。
### 实际边界与测试
只做搜索、格式转换、去重和引用整理，不做事实抽取、可信度判断或报告写作。三个测试覆盖接通规划、重复 URL、无研究问题，总 18。


<a id="commit-13b6ffe"></a>
### 修改节点 8：FactExtractor：来源约束事实，不是客观真实性验证

提交：`13b6ffead73ef582feaf2bf669067a94433ccf84`。时间：2026-10-06 17:55:04（北京时间）。

原始提交标题：feat: add source grounded fact extraction

父提交：b352eb6dba98266a2451f7767c129cba45c08c08。

对应问答：[记录 12](#qa-12)、[记录 13](#qa-13)。完整代码变化：[查看本节点 patch](#diff-13b6ffe)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/fact_extractor.py
M	backend/app/core/llm_client.py
A	backend/tests/test_fact_extractor.py
M	backend/tests/test_llm_client.py
```

差异统计：

```text
 backend/app/agents/fact_extractor.py | 88 ++++++++++++++++++++++++++++++++++++
 backend/app/core/llm_client.py       | 72 ++++++++++++++++++-----------
 backend/tests/test_fact_extractor.py | 64 ++++++++++++++++++++++++++
 backend/tests/test_llm_client.py     | 22 +++++++++
 4 files changed, 219 insertions(+), 27 deletions(-)
```

### 修改目的与前后变化
新增 fact_extractor.py/test_fact_extractor.py，扩展 MockLLMClient 和客户端测试。来源和事实从此分开保存，避免把网页资料直接当报告结论。
### 真实执行的校验
来源不能为空；complete_json(role="fact_extractor") 接收 query、sources、instruction；facts 必须列表，每项必须字典，content/source_url 非空，URL 必须属于来源列表，confidence 可以转 float 且在 0–1；用 (source_url, content) 去重，累积到 state.facts。
### 用户问题“它一下子就提取事实，是真的吗”
不是。Mock 将 source.content 或 source.snippet 原样取出，再附标题、URL、web 类型和固定 0.7 的置信度。这个过程是数据包装，不是阅读网页后提炼断言，更不是事实核查。URL 属于允许来源只证明引用指向已收集记录，不证明网页存在、说法准确或引用内容真正支持断言。
### 测试
新增事实链路、拒绝未知 URL、缺来源报错三个测试，客户端增加一个提取测试，总 22。


<a id="commit-63e065b"></a>
### 修改节点 9：Writer：第一次生成有引用链接的完整报告

提交：`63e065b3cd690ff03325dc94b36a67e26643f024`。时间：2026-10-06 18:04:29（北京时间）。

原始提交标题：feat: add cited report writer

父提交：13b6ffead73ef582feaf2bf669067a94433ccf84。

对应问答：[记录 14](#qa-14)。完整代码变化：[查看本节点 patch](#diff-63e065b)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/writer.py
M	backend/app/core/llm_client.py
M	backend/tests/test_llm_client.py
A	backend/tests/test_writer.py
```

差异统计：

```text
 backend/app/agents/writer.py     | 41 +++++++++++++++++++++++++++++++++++
 backend/app/core/llm_client.py   | 31 +++++++++++++++++++++++++-
 backend/tests/test_llm_client.py | 16 +++++++++++++-
 backend/tests/test_writer.py     | 47 ++++++++++++++++++++++++++++++++++++++++
 4 files changed, 133 insertions(+), 2 deletions(-)
```

### 修改目的与前后变化
新增 writer.py/test_writer.py，扩展 Mock 文本实现。此前只能拿到结构化事实；现在能看到 Markdown 报告。
### 初版写作流程
plan 和 facts 必须非空；将 query、plan、facts、references、instruction 交给 complete_text(role="writer")；清理返回空白，空文本报错；写入 state.final_report，phase="writing"。此时一次 Writer.run 只调用一次 complete_text。
### Mock 报告内容
固定执行摘要、研究发现、结论模板，把每条事实拼成带 [来源标题](URL) 的 Markdown。可以点击的链接是输出格式能力，不说明内容经过真实检索验证。把事实编进报告不等于报告结论自动可靠。
### 测试
新增三个 Writer 测试，客户端已有写作测试增强内容和 URL 断言，总 25。


<a id="commit-87f7acf"></a>
### 修改节点 10：Critic：审核结果和评分成为独立状态

提交：`87f7acf3a9594f833496b6f70d9d3d6586aa9887`。时间：2026-10-06 18:08:55（北京时间）。

原始提交标题：feat: add research report critic

父提交：63e065b3cd690ff03325dc94b36a67e26643f024。

对应问答：[记录 14](#qa-14)、[记录 16](#qa-16)。完整代码变化：[查看本节点 patch](#diff-87f7acf)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/agents/critic.py
M	backend/app/core/llm_client.py
A	backend/tests/test_critic.py
M	backend/tests/test_llm_client.py
```

差异统计：

```text
 backend/app/agents/critic.py     | 67 ++++++++++++++++++++++++++++++++++++++++
 backend/app/core/llm_client.py   | 16 ++++++++++
 backend/tests/test_critic.py     | 54 ++++++++++++++++++++++++++++++++
 backend/tests/test_llm_client.py | 18 +++++++++++
 4 files changed, 155 insertions(+)
```

### 修改目的与前后变化
新增 critic.py/test_critic.py，扩展 Mock 审核分支。Writer 产出报告后可调用 Critic，但这一提交尚未统一编排整个任务。
### 审核协议
要求 final_report 非空；complete_json(role="critic") 接收 query、report、facts、sources；校验 verdict 只能 pass/needs_revision，quality_score 数字且0–10，issues 为字符串列表；写 state.review 和 state.quality_score，phase="reviewing"。
### Mock 实际判断
bool(facts and sources and "http" in report) 决定 pass，评分固定8.0或4.0。它不逐条查引用、不验证逻辑、不判断偏见或时代变化。代码标签叫 Critic 不表示已经拥有专家审核能力。
### 测试
三个 Agent 测试及一个客户端测试使总数到29。Critic 只把状态设 reviewing，最终 completed 是后来 Workflow 的职责。


<a id="commit-861a4fa"></a>
### 修改节点 11：ResearchWorkflow：五个 Agent 由同一编排器顺序调用

提交：`861a4faafba0788552bd0a013c452c2f447dfcc8`。时间：2026-10-06 18:14:22（北京时间）。

原始提交标题：feat: orchestrate complete research workflow

父提交：87f7acf3a9594f833496b6f70d9d3d6586aa9887。

对应问答：[记录 15](#qa-15)、[记录 16](#qa-16)。完整代码变化：[查看本节点 patch](#diff-861a4fa)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/workflow/__init__.py
A	backend/app/workflow/research_workflow.py
A	backend/tests/test_workflow.py
```

差异统计：

```text
 backend/app/workflow/__init__.py          |  1 +
 backend/app/workflow/research_workflow.py | 54 +++++++++++++++++++++++++++++++
 backend/tests/test_workflow.py            | 36 +++++++++++++++++++++
 3 files changed, 91 insertions(+)
```

### 修改目的与前后变化
新增 workflow 包、research_workflow.py、test_workflow.py。此前只能手动拼调用；现在一条 run 即可完成整个最小链路。
### 统一状态的数据流
__init__ 创建 Planner/Researcher/FactExtractor/Writer/Critic，run 创建 ResearchState 并顺序 await 每个 Agent。一次任务中传的是同一个 state，所以前一步写的数据后一步可以读取。状态存数据，Workflow 决定顺序，Client 负责模型或搜索能力。
### reviewing 怎么变 completed
await self.critic.run(state) 返回后，Workflow 执行 state.phase="completed"，最后 return state。不是 Critic 再调用一个“完成 Agent”，也不是数据类自己自动改变。
### 边界与测试
初版无审核重试循环，流程结束即 completed，不表示一定 pass。两个测试验证整链路和显式会话编号，总31。


<a id="commit-99f39af"></a>
### 修改节点 12：命令行运行入口：不用写测试也能观察任务结果

提交：`99f39af09ec67e00ef19fdbac008123305abee7d`。时间：2026-10-06 18:20:01（北京时间）。

原始提交标题：feat: add command line research runner

父提交：861a4faafba0788552bd0a013c452c2f447dfcc8。

对应问答：[记录 17](#qa-17)。完整代码变化：[查看本节点 patch](#diff-99f39af)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	README.md
A	backend/app/scripts/__init__.py
A	backend/app/scripts/run_research.py
A	backend/tests/test_run_research.py
```

差异统计：

```text
 README.md                           | 15 ++++++++
 backend/app/scripts/__init__.py     |  1 +
 backend/app/scripts/run_research.py | 75 +++++++++++++++++++++++++++++++++++++
 backend/tests/test_run_research.py  | 32 ++++++++++++++++
 4 files changed, 123 insertions(+)
```

### 修改目的与前后变化
新增 scripts 包、run_research.py 和测试，README 加操作命令，给用户一个直接运行的入口。
### CLI 语法
argparse 创建可选位置参数 query，nargs="?" 允许不传；没传时 input 提示输入；清理空白后空问题 SystemExit；asyncio.run 驱动异步 run。if __name__=="__main__" 只在作为程序入口执行时调用 main。
### 运行与打印
项目根目录先设 PYTHONPATH=backend，再 python -m app.scripts.run_research "研究问题"。PYTHONPATH 让 Python 找到 backend/app；-m 使用模块路径。print_state 输出计划、来源、事实、报告、审核结论、评分、阶段、会话ID。
### 范围与测试
仍是 Mock 研究，不是 Web API，也没有浏览器 UI。两个测试检查状态完成和输出章节，总33。


<a id="commit-64b3d07"></a>
### 修改节点 13：审核路由与修订循环：通过、补搜、仅重写三条路径

提交：`64b3d07216bc83c6ca62686fedab204df42a119c`。时间：2026-10-06 18:32:49（北京时间）。

原始提交标题：feat: add critic routing and revision loop

父提交：99f39af09ec67e00ef19fdbac008123305abee7d。

对应问答：[记录 18](#qa-18)。完整代码变化：[查看本节点 patch](#diff-64b3d07)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/agents/critic.py
M	backend/app/agents/researcher.py
M	backend/app/agents/writer.py
M	backend/app/core/llm_client.py
M	backend/app/domain/state.py
M	backend/app/workflow/research_workflow.py
M	backend/tests/test_workflow.py
```

差异统计：

```text
 backend/app/agents/critic.py              |  14 +++-
 backend/app/agents/researcher.py          |   6 +-
 backend/app/agents/writer.py              |   4 +-
 backend/app/core/llm_client.py            |   7 ++
 backend/app/domain/state.py               |   1 +
 backend/app/workflow/research_workflow.py |  29 +++++++-
 backend/tests/test_workflow.py            | 107 ++++++++++++++++++++++++++++++
 7 files changed, 163 insertions(+), 5 deletions(-)
```

### 修改目的与前后变化
此前 Workflow 只审核一次；现在允许不通过后补充资料或仅修文。State 新增 pending_search_queries；Critic 增 needs_more_research 和 search_queries；Writer 接收审核结果和迭代次数。
### 路由规则
每轮 Critic 后：verdict=pass 则退出；iteration≥max_iterations 也退出；否则先 iteration+=1。需要新证据时选择 review.search_queries or review.issues or research_questions，Researcher 补搜并清空 pending 队列，FactExtractor 再提取，再 Writer。无需新证据时跳过搜索，直接 Writer，再次 Critic。
### 上限不是总执行次数
默认 max_iterations=1 表示最多一次追加修订，不是总共只能运行一次：初稿一次、修订一次，因此最多两次审核。max_iterations=0 仍会初次研究和审核，只是不追加修订。达到上限仍把 phase 设 completed，同时保留 needs_revision 和质量评分；“流程结束”和“质量通过”必须分开理解。
### 测试
四个新增场景验证补搜路径、仅重写、上限停止、负数上限拒绝，总37。Mock 的“已处理：问题”只是文本拼接，不是真正修正了逻辑缺陷。


<a id="commit-787cd9a"></a>
### 修改节点 14：内部进度事件流：iteration-01 完成版

提交：`787cd9a4ecfd496e17efbf522f765d013607e0db`。时间：2026-10-06 18:55:38（北京时间）。

原始提交标题：feat: add research workflow event stream

父提交：64b3d07216bc83c6ca62686fedab204df42a119c。

对应问答：[记录 19](#qa-19)、[记录 20](#qa-20)。完整代码变化：[查看本节点 patch](#diff-787cd9a)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	README.md
A	backend/app/domain/events.py
M	backend/app/workflow/research_workflow.py
A	backend/tests/test_stream_workflow.py
```

差异统计：

```text
 README.md                                 |  31 ++++++
 backend/app/domain/events.py              |  38 +++++++
 backend/app/workflow/research_workflow.py | 162 ++++++++++++++++++++++++++++--
 backend/tests/test_stream_workflow.py     | 102 +++++++++++++++++++
 4 files changed, 326 insertions(+), 7 deletions(-)
```

### 修改目的与前后变化
此前调用者只能等待 run 返回最终状态；现在可以在运行过程中逐步取得进度事件。新增 ResearchEvent 和流测试；Workflow 提取共享内部生成器。
### 两种入口共用一套业务
run 创建 state，用 async for 消费 _stream_state 并忽略中间事件，最终返回 state。stream 创建 state，转发 _stream_state 的 event。不是 run 和 stream 各写一套五个 Agent 顺序，也不是调用 run 会自动把事件推到网络。
### yield 与 async for
yield 交出一条事件，调用者继续迭代时生成器从该处继续。async for 逐条异步消费；await 等待具体协程。正常一次研究的10条事件是开始→阶段→plan_ready→阶段→证据→阶段→草稿→阶段→审核→完成。此时名字还是 plan_ready。
### SSE 小白解释与边界
内部事件流像研究员边工作边汇报；SSE 则是未来把这些消息经 HTTP 持续发送给浏览器的一种方式。这次没有实现 SSE 服务器、FastAPI、网页监听、WebSocket、数据库；先准备可测试的消息序列。
### 快照与测试
ResearchEvent(frozen=True) 禁止重新给外层字段赋值，to_dict 展开 deepcopy(data)；不会深度冻结嵌套对象。两个新测试验证事件顺序/最终产物和补充搜索轮次，总39。本次归档实际从该提交导出独立副本运行39个测试，全部通过。


<a id="commit-ab7ffa3"></a>
### 修改节点 15：V2 长期契约：把未来目标与当前实现分开

提交：`ab7ffa3f2c696844ff1dd5ebc359f1efe927ce3b`。时间：2026-10-06 19:10:03（北京时间）。

原始提交标题：docs: define v2 core contract

父提交：787cd9a4ecfd496e17efbf522f765d013607e0db。

对应问答：[记录 21](#qa-21)。完整代码变化：[查看本节点 patch](#diff-ab7ffa3)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	docs/v2-core-contract.md
```

差异统计：

```text
 docs/v2-core-contract.md | 95 ++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 95 insertions(+)
```

### 修改目的与前后变化
新建 docs/v2-core-contract.md，不改 Python 功能。记录原项目复杂角色与学习版角色的映射，以及最终状态、审核路由、对外产物和迭代计划。
### 角色关系
ChiefArchitect→Planner；DeepScout→Researcher+FactExtractor；LeadWriter→Writer；CriticMaster→Critic；V2 Graph→ResearchWorkflow。DataAnalyst/CodeWizard 仍待建立，不是看到文档中的角色名就已经实现。
### 项目边界
只保留V2研究入口，不复制V1 ReAct旧服务、无关新闻/招投标/复杂知识库页面。以后按顺序加入假设、数据点、知识图谱、分析图表、受限代码、细化写作审核、FastAPI SSE、检查点、真实服务和简化前端。
### 测试
仅文档提交，39个静态测试不变。


<a id="commit-3986b40"></a>
### 修改节点 16：GitHub 旁支 Initial commit：不是第二次开发研究功能

提交：`3986b40e2f0cf7fc9fa725a10d77ee16e959ab76`。时间：2026-10-06 19:16:41（北京时间）。

原始提交标题：Initial commit

父提交：无，根提交。

对应问答：该节点没有单独的业务问答；仍保留其完整变更。。完整代码变化：[查看本节点 patch](#diff-3986b40)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	README.md
```

差异统计：

```text
 README.md | 1 +
 1 file changed, 1 insertion(+)
```

### 历史关系
这是一条独立根历史，仅新增一行 README.md。它随后通过0a892dc与主线合并，不能当成删除了已有后端再重建。
### 归档方式
保留此节点和完整差异，因为它属于关联Git历史；但将其标为旁支，不把其静态测试0解释成主线测试回退。


<a id="commit-0a892dc"></a>
### 修改节点 17：README 合并：连接独立历史

提交：`0a892dc6be673de6fa17057c1906dfd00c3d32a1`。时间：2026-10-06 19:31:24（北京时间）。

原始提交标题：chore: resolve README merge

父提交：ab7ffa3f2c696844ff1dd5ebc359f1efe927ce3b 3986b40e2f0cf7fc9fa725a10d77ee16e959ab76。

对应问答：该节点没有单独的业务问答；仍保留其完整变更。。完整代码变化：[查看本节点 patch](#diff-0a892dc)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

本节点相对第一父提交没有文件内容差异。

差异统计：

无文件内容差异。

### 两个父提交
这是合并提交，第一父提交ab7ffa3是学习项目主线，另一个父提交3986b40是GitHub独立Initial commit。
### 文件实际变化
相对第一父提交的工作树差异为空，说明主线内容没有新的业务变动；作用是连接两条历史。归档中的文件差异和统计均按第一父提交比较，避免把整个后端误认为“合并中新建”。
### 测试
主线39个静态测试不变；无需推测新的研究能力。


<a id="commit-39171ba"></a>
### 修改节点 18：V2 领域模型：Section、Hypothesis、DataPoint、Chart、CriticFeedback

提交：`39171ba5b4729c8e6783c31103ab18c4af140324`。时间：2026-10-06 19:40:23（北京时间）。

原始提交标题：feat: add v2 domain models

父提交：0a892dc6be673de6fa17057c1906dfd00c3d32a1。

对应问答：[记录 21](#qa-21)。完整代码变化：[查看本节点 patch](#diff-39171ba)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
A	backend/app/domain/models.py
A	backend/tests/test_domain_models.py
```

差异统计：

```text
 backend/app/domain/models.py        | 116 ++++++++++++++++++++++++++++++++++++
 backend/tests/test_domain_models.py |  76 +++++++++++++++++++++++
 2 files changed, 192 insertions(+)
```

### 修改目的与前后变化
新增 models.py 和 test_domain_models.py，先把数据形状定义清楚，尚未全部接入 Agent。
### 五个标准数据对象
Section 表示章节：id/title/description、类型、状态、正文、来源、子章节、数据和图表需求、优先级、搜索词。Hypothesis 表示假设及正反证据列表。DataPoint 表示名称/值/单位/年份/来源/置信度。Chart 表示类型/数据/代码/图片/章节。CriticFeedback 表示问题编号、目标章节、类型、严重度、描述、建议、已解决标记。
### 语法与真正的运行时保障
Literal 列出类型提示允许的文字，并不会自动抛运行时错误；dataclass 也不自动验证所有字段。asdict 递归把嵌套Section转字典，default_factory 保持容器独立。from __future__ import annotations 让类定义中的自引用标注更易处理。模型定义了字段不等于存在分析、绘图或审核执行逻辑。
### 测试
四个新测试覆盖嵌套序列化、集合不共享、数据图表字段保留、反馈默认未解决，总43。priority 的大小方向没有调度实现规定，不能仅凭字段宣称“越大越重要”。


<a id="commit-a974120"></a>
### 修改节点 19：扩展 ResearchState：先为 V2 产物预留位置

提交：`a974120410e932d25f74a97b1fd2d818d86eae85`。时间：2026-10-06 20:26:52（北京时间）。

原始提交标题：feat: extend research state for v2 data

父提交：39171ba5b4729c8e6783c31103ab18c4af140324。

对应问答：[记录 22](#qa-22)。完整代码变化：[查看本节点 patch](#diff-a974120)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/domain/state.py
M	backend/tests/test_state.py
```

差异统计：

```text
 backend/app/domain/state.py | 24 ++++++++++++++++++++++--
 backend/tests/test_state.py | 18 ++++++++++++++++++
 2 files changed, 40 insertions(+), 2 deletions(-)
```

### 修改目的与前后变化
State 增 outline、key_entities、hypotheses、mind_map、knowledge_graph、raw_sources、data_points、insights、draft_sections、charts、code_executions、critic_feedback、unresolved_issues、logs、messages。knowledge_graph 默认是独立的 nodes/edges 列表。
### 过渡版本特别注意
这一提交仍保留plan/sources/review，新增outline/raw_sources是并存的过渡字段；当时旧Agent仍主要写旧字段。并存不表示两个字段自动同步，也不表示领域模型和状态对象已经完成一体化迁移。
### 实际能力
多数新增容器仍为空。数据点、图表、代码执行、知识图谱、日志等不是新增相应Agent；只是任务档案有位置可存这些数据。
### 测试
修改已有两个State测试，增加默认值和独立可变对象断言，测试总数仍43。


<a id="commit-6bf3f4b"></a>
### 修改节点 20：全链路统一改名：plan→outline、sources→raw_sources、review→review_result

提交：`6bf3f4b25678cb8c6f8c00c230795c3ce096d79a`。时间：2026-10-06 21:01:20（北京时间）。

原始提交标题：refactor: align workflow state with v2 terminology

父提交：a974120410e932d25f74a97b1fd2d818d86eae85。

对应问答：[记录 23](#qa-23)、[记录 24](#qa-24)。完整代码变化：[查看本节点 patch](#diff-6bf3f4b)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	README.md
M	backend/app/agents/critic.py
M	backend/app/agents/fact_extractor.py
M	backend/app/agents/planner.py
M	backend/app/agents/researcher.py
M	backend/app/agents/writer.py
M	backend/app/core/llm_client.py
M	backend/app/domain/state.py
M	backend/app/scripts/run_research.py
M	backend/app/workflow/research_workflow.py
M	backend/tests/test_critic.py
M	backend/tests/test_fact_extractor.py
M	backend/tests/test_llm_client.py
M	backend/tests/test_planner.py
M	backend/tests/test_researcher.py
M	backend/tests/test_state.py
M	backend/tests/test_stream_workflow.py
M	backend/tests/test_workflow.py
M	backend/tests/test_writer.py
```

差异统计：

```text
 README.md                                 |  4 ++--
 backend/app/agents/critic.py              | 12 ++++++++++--
 backend/app/agents/fact_extractor.py      |  6 +++---
 backend/app/agents/planner.py             | 14 +++++++-------
 backend/app/agents/researcher.py          |  6 +++---
 backend/app/agents/writer.py              |  8 ++++----
 backend/app/core/llm_client.py            |  4 ++--
 backend/app/domain/state.py               | 15 ++++++---------
 backend/app/scripts/run_research.py       | 12 ++++++------
 backend/app/workflow/research_workflow.py | 24 +++++++++++++-----------
 backend/tests/test_critic.py              |  4 ++--
 backend/tests/test_fact_extractor.py      |  6 +++---
 backend/tests/test_llm_client.py          |  2 +-
 backend/tests/test_planner.py             |  8 ++++----
 backend/tests/test_researcher.py          |  6 +++---
 backend/tests/test_state.py               | 12 ++++++------
 backend/tests/test_stream_workflow.py     |  4 ++--
 backend/tests/test_workflow.py            | 18 +++++++++---------
 backend/tests/test_writer.py              |  6 +++---
 19 files changed, 89 insertions(+), 82 deletions(-)
```

### 修改目的与前后变化
19个文件同时更新，取消过渡期重复名称，让State、Agent、Client、Workflow、CLI、README、测试使用同一套V2词汇。state旧字段不再存在，测试明确检查无plan/sources/review属性。
### 精确名称映射
state.plan→state.outline；state.sources→state.raw_sources；state.review→state.review_result；plan_ready→outline_ready。Writer payload 的plan/review同步变outline/review_result。FactExtractor和Critic的payload键"sources"、证据事件的"sources"仍可以装state.raw_sources；payload键不是State属性。
### 新的简化审核反馈
Critic把issues转成{"description": issue, "resolved": False}列表，unresolved_issues等于条数，事件增加critic_feedback。这尚不是完整CriticFeedback领域对象，因为缺id/target_section/issue_type/severity/suggestion。
### 测试和风险边界
所有旧断言和样例同步改名，总43不变。核心算法没有因改名变智能，但旧字段或旧事件名称的调用者需要跟着更新，属于跨模块接口调整。


<a id="commit-b582dec"></a>
### 修改节点 21：Planner 使用 V2 数据对象并扩展规划输出

提交：`b582dec64be7658856b155a32cce98cd08b88406`。时间：2026-10-06 21:12:28（北京时间）。

原始提交标题：feat: normalize planner output into v2 models

父提交：6bf3f4b25678cb8c6f8c00c230795c3ce096d79a。

对应问答：[记录 25](#qa-25)。完整代码变化：[查看本节点 patch](#diff-b582dec)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/agents/planner.py
M	backend/app/core/llm_client.py
M	backend/app/workflow/research_workflow.py
M	backend/tests/test_llm_client.py
M	backend/tests/test_planner.py
M	backend/tests/test_stream_workflow.py
```

差异统计：

```text
 backend/app/agents/planner.py             | 97 +++++++++++++++++++++++++++++--
 backend/app/core/llm_client.py            |  8 +++
 backend/app/workflow/research_workflow.py |  3 +
 backend/tests/test_llm_client.py          |  1 +
 backend/tests/test_planner.py             |  4 ++
 backend/tests/test_stream_workflow.py     |  2 +
 6 files changed, 110 insertions(+), 5 deletions(-)
```

### 修改目的与前后变化
Planner不再只接受title/description简单字典，而是先校验后创建Section和Hypothesis，再to_dict写回State。增加hypotheses/key_entities/mind_map的规划数据和事件字段。
### 章节处理
补sec_N、pending、mixed、优先级index，检查章节类型和状态，search_queries必须列表，去空白，未提供/空列表时用标题兜底。存入State的仍是list[dict]，不是list[Section]。模型的content/sources/subsections暂为默认值，Writer后来用draft_sections存正文。
### 假设和实体处理
假设内容非空、状态合法，默认h_N/unverified，证据数组初始化；实体允许字符串或带name的字典，统一为名称列表。mind_map直接取返回值，未校验内部结构。
### 时间点区别与测试
本提交Mock新增一条unverified假设和空实体，章节的明确研究查询词在下一提交才新增；本提交只靠标题兜底。已有测试加字段断言，总43。正式i2内这些假设还没有后续证据更新代码。


<a id="commit-0c0ecb5"></a>
### 修改节点 22：来源与事实绑定章节：让资料知道自己服务哪一章

提交：`0c0ecb52b0bce9ef272ae0604a195a166368dc15`。时间：2026-10-06 21:30:02（北京时间）。

原始提交标题：feat: associate research sources with outline sections

父提交：b582dec64be7658856b155a32cce98cd08b88406。

对应问答：[记录 25](#qa-25)。完整代码变化：[查看本节点 patch](#diff-0c0ecb5)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/agents/fact_extractor.py
M	backend/app/agents/researcher.py
M	backend/app/core/llm_client.py
M	backend/tests/test_fact_extractor.py
M	backend/tests/test_researcher.py
```

差异统计：

```text
 backend/app/agents/fact_extractor.py | 26 +++++++++++------
 backend/app/agents/researcher.py     | 55 ++++++++++++++++++++++++++++++------
 backend/app/core/llm_client.py       |  3 ++
 backend/tests/test_fact_extractor.py |  5 ++++
 backend/tests/test_researcher.py     | 27 ++++++++++++++++++
 5 files changed, 98 insertions(+), 18 deletions(-)
```

### 修改目的与前后变化
Mock为三章添加具体search_queries；Researcher新增_build_search_tasks，遍历每章全部查询，来源增加section_id/section_title；FactExtractor按source_url查来源，复制章节归属。
### 搜索优先级与数据流
pending_search_queries非空时优先补搜，不附章节；否则构建大纲任务；没有可用大纲任务才回退research_questions。Source章节标签→按URL校验Fact→Fact章节标签，为后续Writer按章分配证据提供基础。
### 去重限制
同一URL被多个章节搜到仍只保留第一次来源及其章节，尚未建一个来源关联多个章节的结构。补充事实暂时没有章节，后续Writer有兼容策略。
### 测试
来源/事实链路断言section_id/title，新增单章两个查询都执行测试，总44。数据分组是真的运行逻辑，网页和事实内容仍是Mock。


<a id="commit-0387dc8"></a>
### 修改节点 23：章节级草稿：先逐章写，再整合整篇报告

提交：`0387dc8b7cd2694cb5f2277c57ef0426863e93d3`。时间：2026-10-06 21:43:26（北京时间）。

原始提交标题：feat: add section level drafting

父提交：0c0ecb52b0bce9ef272ae0604a195a166368dc15。

对应问答：[记录 26](#qa-26)。完整代码变化：[查看本节点 patch](#diff-0387dc8)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	README.md
M	backend/app/agents/writer.py
M	backend/app/core/llm_client.py
M	backend/app/workflow/research_workflow.py
M	backend/tests/test_stream_workflow.py
M	backend/tests/test_workflow.py
M	backend/tests/test_writer.py
M	docs/v2-core-contract.md
```

差异统计：

```text
 README.md                                 |  8 +--
 backend/app/agents/writer.py              | 87 +++++++++++++++++++++++++++++--
 backend/app/core/llm_client.py            | 51 ++++++++++++++++++
 backend/app/workflow/research_workflow.py |  6 ++-
 backend/tests/test_stream_workflow.py     |  4 ++
 backend/tests/test_workflow.py            | 12 +++--
 backend/tests/test_writer.py              | 37 +++++++++++++
 docs/v2-core-contract.md                  |  3 +-
 8 files changed, 197 insertions(+), 11 deletions(-)
```

### 修改目的与前后变化
Writer由一次complete_text改为每章一次mode=section，再一次mode=report；填充State原先预留draft_sections，更新大纲状态drafted。
### 每章执行的细节
为章节补id/title，dict(raw_section)复制一层，按section_id选事实。无匹配时_facts_for_section回退全部facts；无归属或归属不存在的事实并入第一章，用(source_url,content)去重。每章正文不能为空，草稿用章节ID作为字典键。
### 整报告与审核重写
整合请求接收大纲、全部事实、各章草稿、引用、数据点/洞察/图表、审核结果、iteration。三个章节每次写作4次客户端调用；审核修订再次运行Writer，仍重写所有章节再整合，不是仅重写问题章节。Mock按固定模板拼接，mode是传给客户端的业务分支，不是模型自动理解的特殊系统功能。
### 事件粒度和测试
初稿/修订两处draft_ready都加outline/draft_sections，但事件仍在全部章节及整报告写完后一次发出，不逐章发。数据点、图表只有输入位置，没有生成者。新增按章事实隔离测试，Workflow测试改为筛mode=report统计整报告次数，总45。


<a id="commit-99fe715"></a>
### 修改节点 24：事件公共外壳校验：尽早拒绝错误通知单

提交：`99fe7155aa0436a04fd26470fccc34614652522e`。时间：2026-10-06 22:27:08（北京时间）。

原始提交标题：feat: validate research event envelope

父提交：0387dc8b7cd2694cb5f2277c57ef0426863e93d3。

对应问答：[记录 27](#qa-27)。完整代码变化：[查看本节点 patch](#diff-99fe715)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/domain/events.py
A	backend/tests/test_events.py
```

差异统计：

```text
 backend/app/domain/events.py | 54 +++++++++++++++++++++++++++++++++++++
 backend/tests/test_events.py | 63 ++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 117 insertions(+)
```

### 修改目的与前后变化
ResearchEvent新增ResearchEventType常量类、EVENT_TYPES/RESEARCH_PHASES白名单和__post_init__。之前只打包数据，现在创建事件时就检查格式。
### 校验顺序与语法
检查type为字符串且已登记、session_id非空字符串、phase合法、iteration整数且非负、data为字典。特别排除bool，因为Python isinstance(True,int)为True。__post_init__由dataclass生成的构造函数在字段赋值后自动调用；异常会阻止事件创建，不自动生成错误事件继续运行。
### 不变之处
Workflow仍用字符串调用_event，ResearchEventType不是Enum；只定义合法值不自动替换所有字符串。事件数/研究顺序/输出格式不变。合法phase白名单只是允许列表，不验证状态转换顺序或type与phase是否匹配。
### 测试
新增test_events.py七项测试，总52。此时还没检查各事件专属业务字段，也没有HTTP SSE。


<a id="commit-fad4cdb"></a>
### 修改节点 25：必需业务字段：每种事件不仅要有名字，也要带齐内容

提交：`fad4cdb1fff6ef301705d3af461a88e46c7fba35`。时间：2026-10-06 22:40:13（北京时间）。

原始提交标题：feat: define required research event fields

父提交：99fe7155aa0436a04fd26470fccc34614652522e。

对应问答：[记录 28](#qa-28)。完整代码变化：[查看本节点 patch](#diff-fad4cdb)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	backend/app/domain/events.py
M	backend/tests/test_events.py
```

差异统计：

```text
 backend/app/domain/events.py | 24 ++++++++++++++++++++++++
 backend/tests/test_events.py | 29 +++++++++++++++++++++++++++--
 2 files changed, 51 insertions(+), 2 deletions(-)
```

### 修改目的与前后变化
新增EVENT_REQUIRED_FIELDS映射，为7种事件分别指定data必须出现的键名；改变了此前空data也能创建合法type事件的情况。
### 新核心语句
missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()：左边是规定集合，右边是实际字典键视图，集合差集算缺项。缺项非空就sorted排稳定顺序，再", ".join组成错误文本，抛ValueError。必须有键不等于必须有非空内容，[]/{}也可以；类型错误但键齐仍可能通过。
### 测试
序列化样例补齐outline_ready的5个键；新增“所有事件都有规则”和“缺少专属字段拒绝”两个测试，本提交精确静态数量54。原答复后来提到55，是同一轮读取了下一次防覆盖的未提交代码；不能把55归到本提交。
### 范围
规则提供字段契约，不验证report真假、评分类型、计数与列表长度一致性、JSON可序列化或事件时序。


<a id="commit-79db291"></a>
### 修改节点 26：公共字段防覆盖、文档收尾与 iteration-02 正式标签

提交：`79db291dc0a1a7825b846d05516bce556f8976dc`。时间：2026-10-06 22:46:06（北京时间）。

原始提交标题：chore: complete iteration 02 contract

父提交：fad4cdb1fff6ef301705d3af461a88e46c7fba35。

对应问答：[记录 28](#qa-28)、[记录 29](#qa-29)。完整代码变化：[查看本节点 patch](#diff-79db291)。

修改文件（`A`＝新增，`M`＝修改；以第一父提交为比较基准）：

```text
M	README.md
M	backend/app/domain/events.py
M	backend/tests/test_events.py
M	docs/v2-core-contract.md
```

差异统计：

```text
 README.md                    | 4 +++-
 backend/app/domain/events.py | 6 ++++++
 backend/tests/test_events.py | 9 +++++++++
 docs/v2-core-contract.md     | 4 ++--
 4 files changed, 20 insertions(+), 3 deletions(-)
```

### 修改目的与前后变化
新增EVENT_ENVELOPE_FIELDS={type,session_id,phase,iteration}与交集检查，阻止data抢占公共字段。README去掉iteration-02“进行中”，描述稳定协议，路线图不再把章节大纲当未完成目标，章节写作改为后续完善。
### 为什么防覆盖是运行时改动
to_dict先建公共字段，再event.update(deepcopy(data))；同名键会被data覆盖，甚至让已经校验的session_id/type被替换。reserved_fields=EVENT_ENVELOPE_FIELDS & self.data.keys()找交集，有交集立即报错。它不仅是纯文档收尾；虽然提交标题chore，里面确实多了代码保护。
### 与聊天轮次的关系
22:41的回答已经读到这批未提交内容并解释；22:46它才正式进入79db291。22:50回答主要说明“正式收尾”，并不意味着新增了第二套防覆盖代码。
### 测试和阶段终点
新增一项session_id覆盖拒绝测试，总55。iteration-02标签固定在本提交。此次归档导出独立历史副本实际运行55项，全部通过；后来的fccf339不属于本正式完成版。



<a id="archive-qa"></a>
## 四、历次提问、过程说明与回答完整原文

下面是从当前聊天历史逐项取回的可见原文。为便于定位，每条都保留原始记录 ID、时间、用户消息、助手过程说明和最终回答。助手的过程说明也保留，因为用户明确要求每一次回答和分析过程都记录；内部推理、系统提示和开发者提示不在可见聊天正文中，因此不伪造加入。

<a id="qa-1"></a>
### 记录 1：首次完整阅读项目

开始时间（北京时间）：2026-10-06 01:53:06。结束时间：2026-10-06 01:53:54。原始记录 ID：`01a10d32-aaa1-7091-b9c7-1d2b937a4053`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_1_1_START -->
```text
D:\课\s4-6\information_deepresearch这个文件的内容 你先阅读然后阅读完了跟我说

```
<!-- ORIGINAL_USER_1_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_1_2_START -->
我先定位并读取 `D:\课\s4-6\information_deepresearch`，确认文件类型和内容范围；读完后我会直接告诉你。
<!-- ORIGINAL_ASSISTANT_1_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_1_3_START -->
已确认这不是单个文件，而是一个小型项目目录，共有 README、后端源码和测试文件。我现在把这些文件逐一通读。
<!-- ORIGINAL_ASSISTANT_1_3_END -->

#### 原文 4：助手最终回答

<!-- ORIGINAL_ASSISTANT_1_4_START -->
我已经完整阅读了 `D:\课\s4-6\information_deepresearch` 目录下的全部文件，包括：

- `README.md`
- `ResearchState` 研究状态模型
- `BaseAgent` Agent 基类
- 两组单元测试
- 各目录初始化文件

整体内容是一个 DeepResearch 后端学习项目的第一阶段，主要实现研究状态管理和 Agent 基础接口，目前还没有具体的 Planner、Researcher、Writer、Critic 实现。
<!-- ORIGINAL_ASSISTANT_1_4_END -->



<a id="qa-2"></a>
### 记录 2：state.py 与 @dataclass 语法详解

开始时间（北京时间）：2026-10-06 01:56:02。结束时间：2026-10-06 01:57:13。原始记录 ID：`01a10d35-592b-7051-8e5a-5f82f58d2162`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_2_1_START -->
```text
以后我问你问题的时候你先第一步阅读这个文件中的更新的内容
因为这个文件会实时更新 你之前的经验不准确
第一个问题
state.py语法详解 我是新手小白 我几乎不懂后端 比如说这里为什么@dataclass

```
<!-- ORIGINAL_USER_2_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_2_2_START -->
我会先按你的要求重新读取项目当前内容，重点确认最新的 `state.py`，再基于最新版本讲解。之后你每次提问时，我都会先做这一步。
<!-- ORIGINAL_ASSISTANT_2_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_2_3_START -->
我已经先重新阅读了当前目录的最新内容。现在讲 `state.py`。

## 1. `state.py` 是做什么的？

它定义了一个叫 `ResearchState` 的“研究状态对象”。

你可以把它理解成一个大盒子，里面保存一次研究任务的所有信息：

```python
state = ResearchState("人工智能的发展趋势")
```

这个对象里面会保存：

- 用户的问题
- 当前研究阶段
- 研究计划
- 搜索到的资料
- 整理出的事实
- 最终报告
- 审核结果
- 错误信息

后面的 Planner、Researcher、Writer、Critic 都会读取和修改这个对象。

## 2. `@dataclass` 是什么？

代码中：

```python
@dataclass
class ResearchState:
```

`@dataclass` 是 Python 提供的一个“装饰器”。

它的作用是：这个类主要用来保存数据，所以 Python 自动帮我们生成一些重复代码，例如：

- `__init__`：初始化对象
- `__repr__`：方便打印对象
- `__eq__`：比较两个对象是否相等

没有 `@dataclass` 时，我们可能要手动写：

```python
class ResearchState:
    def __init__(
        self,
        query,
        phase="init",
        iteration=0,
    ):
        self.query = query
        self.phase = phase
        self.iteration = iteration
```

使用 `@dataclass` 后，只需要声明字段：

```python
@dataclass
class ResearchState:
    query: str
    phase: str = "init"
    iteration: int = 0
```

Python 会自动生成类似的初始化代码：

```python
state = ResearchState("测试问题")
```

等价于：

```python
state.query = "测试问题"
state.phase = "init"
state.iteration = 0
```

这里使用 `@dataclass`，是因为 `ResearchState` 的主要职责是“保存研究数据”，而不是执行复杂行为。

## 3. `query: str` 是什么意思？

```python
query: str
```

这叫“类型标注”。

意思是：

```python
query 这个变量应该是字符串
```

例如：

```python
state = ResearchState("测试问题")
```

这里 `"测试问题"` 是字符串，符合要求。

但要注意，类型标注默认不会强制检查类型：

```python
state = ResearchState(123)
```

Python 通常也不会立刻报错。`str` 主要是给开发者、编辑器和类型检查工具看的。

## 4. 为什么 `query` 没有默认值？

```python
query: str
session_id: str = ...
phase: str = "init"
```

`query` 没有默认值，所以创建对象时必须提供：

```python
ResearchState("测试问题")
```

如果不提供：

```python
ResearchState()
```

就会报错。

因为一个研究任务至少应该知道用户问了什么。

## 5. `session_id` 和 `default_factory`

代码：

```python
session_id: str = field(default_factory=lambda: str(uuid4()))
```

可以拆开看。

### `uuid4`

```python
from uuid import uuid4
```

`uuid4()` 会生成一个随机的唯一编号，例如：

```text
6f5c6d18-5f1c-4f45-9a4d-9b1d3c8e42ab
```

它可以用来区分不同的研究任务。

### `lambda`

```python
lambda: str(uuid4())
```

这是一个没有名字的小函数，意思大致是：

```python
def create_session_id():
    return str(uuid4())
```

### `default_factory`

```python
field(default_factory=...)
```

意思是：如果用户没有提供这个字段，就调用这个函数生成默认值。

所以：

```python
first = ResearchState("问题一")
second = ResearchState("问题二")
```

两个对象会得到不同的 `session_id`。

## 6. 为什么列表要写 `default_factory=list`？

例如：

```python
plan: list[dict[str, Any]] = field(default_factory=list)
```

意思是：

```python
plan 是一个列表
列表中的每一项是字典
字典的值可以是任意类型
```

`default_factory=list` 表示每次创建对象时，都创建一个新的空列表。

这是非常重要的。

如果直接写：

```python
plan: list = []
```

多个对象可能错误地共享同一个列表：

```python
first = ResearchState("问题一")
second = ResearchState("问题二")

first.plan.append({"title": "计划一"})
```

正确情况下：

```python
first.plan  # 有数据
second.plan # 仍然为空
```

当前代码通过：

```python
field(default_factory=list)
```

保证了每个 `ResearchState` 都拥有自己的列表。

字典也是同样道理：

```python
review: dict[str, Any] = field(default_factory=dict)
```

每个对象都会拥有独立的空字典。

## 7. 这些字段分别是什么？

```python
phase: str = "init"
```

当前阶段，初始值是 `"init"`。

```python
iteration: int = 0
max_iterations: int = 1
```

审核循环次数和最大循环次数。

```python
plan: list[dict[str, Any]]
```

研究计划，例如：

```python
[
    {"title": "收集行业数据", "status": "todo"}
]
```

```python
research_questions: list[str]
```

拆分后的研究问题。

```python
sources: list[dict[str, Any]]
facts: list[dict[str, Any]]
references: list[dict[str, Any]]
```

分别保存来源、事实和引用信息。

```python
final_report: str = ""
```

最终生成的报告，初始为空字符串。

```python
quality_score: float = 0.0
```

质量分数，使用浮点数。

```python
errors: list[str]
```

错误信息列表。

## 8. 最后可以这样使用

```python
state = ResearchState("研究新能源汽车行业")

print(state.query)
print(state.phase)
print(state.session_id)

state.phase = "planning"
state.plan.append({
    "title": "分析市场规模"
})

print(state)
```

这里的流程是：

1. 创建一个研究状态对象
2. 保存用户问题
3. 自动生成任务编号
4. 当前阶段默认为 `init`
5. 后续 Agent 修改 `phase`、`plan`、`sources` 等字段

简单说，`@dataclass` 让 `ResearchState` 很适合充当一个“结构清晰的数据容器”。
<!-- ORIGINAL_ASSISTANT_2_3_END -->



<a id="qa-3"></a>
### 记录 3：Planner 等未来角色的判断依据

开始时间（北京时间）：2026-10-06 02:03:07。结束时间：2026-10-06 02:03:32。原始记录 ID：`01a10d3b-d722-70b0-b3f6-12c08f24b4ca`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_3_1_START -->
```text
后面的 Planner、Researcher、Writer、Critic 都会读取和修改这个对象。
你怎么知道我后续要写Planner、Researcher、Writer、Critic 你从哪里看到的？

```
<!-- ORIGINAL_USER_3_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_3_2_START -->
我先按约定重新读取项目当前内容，确认这几个名称是否确实写在文件里，再回答你我引用它们的依据。
<!-- ORIGINAL_ASSISTANT_3_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_3_3_START -->
你问得对，我应该明确说明来源。

我是在当前最新的 `state.py` 文件顶部注释中看到的：

```python
后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象，
```

所以我不是根据外部经验推测的，而是根据你项目里的说明来讲的。

另外，`README.md` 也写了后续流程：

```text
用户问题 -> 研究规划 -> 信息搜索 -> 证据整理 -> 报告撰写 -> 质量审核
```

不过需要区分：

- `Planner`、`Researcher`、`Writer`、`Critic` 目前只是注释中提到的后续角色；
- 当前代码里还没有这些具体类；
- 现在实际存在的 Agent 只有 `BaseAgent`，测试里还有一个 `DemoAgent`。

我之前说“后面的 Planner……都会读取和修改”时，应该说成“根据当前文件注释，项目计划让它们这样做”，这样更准确。
<!-- ORIGINAL_ASSISTANT_3_3_END -->



<a id="qa-4"></a>
### 记录 4：单字补充 agent（无独立回答）

开始时间（北京时间）：2026-10-06 02:04:12。结束时间：2026-10-06 02:04:19。原始记录 ID：`01a10d3c-d2ef-7791-b09b-f1b9002494e8`。

归档注：本条只有用户的补充词“agent”，没有独立助手回复；没有为了凑成问答而补写答案。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_4_1_START -->
```text
agent

```
<!-- ORIGINAL_USER_4_1_END -->



<a id="qa-5"></a>
### 记录 5：__init__.py 是什么

开始时间（北京时间）：2026-10-06 02:04:57。结束时间：2026-10-06 02:05:34。原始记录 ID：`01a10d3d-827b-7263-b80a-9ebdef67176e`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_5_1_START -->
```text
agent下的`base.py`  的内容
init.py是什么？

```
<!-- ORIGINAL_USER_5_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_5_2_START -->
我先重新读取当前项目的最新内容，重点确认 `backend/app/agents/__init__.py` 和 `base.py` 的实际内容，再用新手能理解的方式解释。
<!-- ORIGINAL_ASSISTANT_5_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_5_3_START -->
当前 `backend/app/agents/__init__.py` 的内容是：

```python
"""Research agents used by the workflow."""
```

## `__init__.py` 是什么？

`__init__.py` 是 Python 的特殊文件，用来告诉 Python：

> `agents` 这个目录是一个 Python 包，可以被导入。

目录结构是：

```text
app/
└── agents/
    ├── __init__.py
    └── base.py
```

因此可以这样导入 `base.py`：

```python
from app.agents.base import BaseAgent
```

导入过程中，Python 会依次识别：

```text
app       是一个包
agents    是 app 下面的一个包
base.py   是 agents 包中的一个模块
```

## 当前这个文件具体做了什么？

目前它只包含一段说明文字：

```python
"""Research agents used by the workflow."""
```

这叫“模块文档字符串”，只是对这个目录进行说明，目前没有实际功能。

以后也可以在这里统一导出内容，例如：

```python
from .base import BaseAgent
```

这样就可以写：

```python
from app.agents import BaseAgent
```

而不需要写：

```python
from app.agents.base import BaseAgent
```

## 注意：`__init__.py` 和 `__init__` 不一样

`__init__.py`：

```text
包的初始化文件
```

类里面的 `__init__`：

```python
class User:
    def __init__(self):
        pass
```

这是创建对象时自动调用的方法。

另外，当前项目没有 `init.py`，只有名字带“双下划线”的特殊文件：

```text
__init__.py
```
<!-- ORIGINAL_ASSISTANT_5_3_END -->



<a id="qa-6"></a>
### 记录 6：BaseAgent 语法与职责

开始时间（北京时间）：2026-10-06 02:07:27。结束时间：2026-10-06 02:08:18。原始记录 ID：`01a10d3f-cbc6-7630-b717-8dbba7597af4`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_6_1_START -->
```text
agent下的`base.py`  的内容  

```
<!-- ORIGINAL_USER_6_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_6_2_START -->
我先重新读取当前项目最新内容，重点查看 `agents/base.py` 以及它依赖的 `state.py`，然后逐行解释 `base.py`。
<!-- ORIGINAL_ASSISTANT_6_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_6_3_START -->
下面详细解释当前 `backend/app/agents/base.py`。

## 1. 文件整体作用

`base.py` 定义了一个基础类：

```python
class BaseAgent(ABC):
```

它不是一个真正执行研究的 Agent，而是一个“规则模板”。

以后具体的 Agent 都可以继承它，并且必须实现一个统一的方法：

```python
run()
```

这样工作流就可以用统一方式调用不同 Agent。

## 2. 第一行：文件说明

```python
"""所有研究 Agent 共享的最小接口。"""
```

这是模块文档字符串，用来说明这个文件的用途。

它不会执行研究，也不会改变程序逻辑。

## 3. 延迟处理类型标注

```python
from __future__ import annotations
```

这会让 Python 延迟处理类型标注。

当前文件中有：

```python
state: ResearchState
```

这个设置可以让类型标注更灵活，尤其是在类之间互相引用时有帮助。

初学阶段可以先理解为：

> 让类型标注不会过早影响程序运行。

## 4. 导入抽象类工具

```python
from abc import ABC, abstractmethod
```

这里导入两个东西：

### `ABC`

```python
class BaseAgent(ABC):
```

表示 `BaseAgent` 是一个“抽象基类”。

抽象基类通常用来制定规范，而不是直接创建对象。

### `abstractmethod`

```python
@abstractmethod
```

表示下面这个方法是“必须由子类实现的方法”。

## 5. 导入研究状态

```python
from app.domain.state import ResearchState
```

这表示从 `state.py` 中导入 `ResearchState`。

因为 Agent 的工作对象就是这个状态：

```python
state: ResearchState
```

Agent 会读取和修改这个状态对象。

## 6. 定义 `BaseAgent`

```python
class BaseAgent(ABC):
```

这句话可以拆成：

```text
定义一个叫 BaseAgent 的类
它继承自 ABC
它是一个抽象类
```

下面的说明文字：

```python
"""Agent 的基础约定。

每个具体 Agent 只需要实现 ``run``：读取当前状态，完成自己的工作，
再返回更新后的状态。这样工作流不需要知道每个 Agent 的内部细节。
"""
```

这里说明了设计规则：

1. Agent 接收一个 `ResearchState`
2. Agent 完成自己的任务
3. Agent 返回更新后的 `ResearchState`

## 7. `name` 属性

```python
name: str = "base"
```

这表示类有一个叫 `name` 的属性。

```python
name
```

是属性名。

```python
: str
```

表示它应该是字符串。

```python
= "base"
```

表示默认值是 `"base"`。

子类可以修改它：

```python
class DemoAgent(BaseAgent):
    name = "demo"
```

## 8. `run` 方法

```python
@abstractmethod
async def run(self, state: ResearchState) -> ResearchState:
```

这是整个文件最重要的部分。

### `@abstractmethod`

```python
@abstractmethod
```

表示：

> 任何具体 Agent 都必须自己实现 `run` 方法。

因此不能直接创建：

```python
agent = BaseAgent()
```

会报错，因为 `BaseAgent` 还没有真正实现 `run`。

### `async def`

```python
async def run(...)
```

表示这是一个异步方法。

异步方法通常适合搜索网页、调用接口等可能需要等待的工作。

调用时通常需要：

```python
result = await agent.run(state)
```

如果在普通同步代码里调用，可以使用：

```python
asyncio.run(agent.run(state))
```

### `self`

```python
async def run(self, state):
```

`self` 表示当前 Agent 对象本身。

例如：

```python
agent = DemoAgent()
```

调用：

```python
agent.run(state)
```

Python 会自动把 `agent` 传给 `self`。

### `state: ResearchState`

```python
state: ResearchState
```

表示这个方法接收一个研究状态对象。

也就是：

```python
state = ResearchState("测试问题")
agent.run(state)
```

### `-> ResearchState`

```python
-> ResearchState
```

表示这个方法应该返回一个 `ResearchState` 对象。

## 9. `NotImplementedError`

```python
raise NotImplementedError
```

意思是：

> 这个方法现在没有具体实现，子类必须重写它。

当前 `BaseAgent` 只是规定方法长什么样，不知道具体应该如何搜索、写作或审核，所以这里故意不实现。

## 10. 测试中的具体实现

测试文件里定义了一个真正的子类：

```python
class DemoAgent(BaseAgent):
    name = "demo"

    async def run(self, state: ResearchState) -> ResearchState:
        state.phase = "demo_completed"
        return state
```

它做了三件事：

1. 继承 `BaseAgent`
2. 把名字改成 `"demo"`
3. 实现了 `run` 方法

运行时：

```python
state = ResearchState("测试问题")
agent = DemoAgent()

result = asyncio.run(agent.run(state))
```

执行过程是：

```text
创建研究状态
    ↓
创建 DemoAgent
    ↓
调用 run
    ↓
把 state.phase 改成 "demo_completed"
    ↓
返回 state
```

所以，`BaseAgent` 可以理解为：

> 所有具体 Agent 必须遵守的一份接口规范或模板。
<!-- ORIGINAL_ASSISTANT_6_3_END -->



<a id="qa-7"></a>
### 记录 7：LLMClient 与 Mock 接口

开始时间（北京时间）：2026-10-06 02:21:25。结束时间：2026-10-06 02:22:54。原始记录 ID：`01a10d4c-9471-73c0-89b6-6539ffd659dc`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_7_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_7_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_7_2_START -->
我会先重新读取整个项目目录的最新版本，确保讲解的是当前内容，而不是之前记忆的版本。然后我会按文件逐个解释它们的作用、语法和相互关系。
<!-- ORIGINAL_ASSISTANT_7_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_7_3_START -->
我已经重新阅读了项目当前的全部内容。相比上次，新增了三个重要文件：

```text
backend/app/core/__init__.py
backend/app/core/llm_client.py
backend/tests/test_llm_client.py
```

这次项目开始加入“大模型客户端接口”。

## 一、项目当前整体结构

```text
information_deepresearch/
├── README.md
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── domain/
    │   │   ├── __init__.py
    │   │   └── state.py
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   └── base.py
    │   └── core/
    │       ├── __init__.py
    │       └── llm_client.py
    └── tests/
        ├── __init__.py
        ├── test_state.py
        ├── test_base_agent.py
        └── test_llm_client.py
```

可以先这样理解：

```text
state.py       保存研究过程中的数据
base.py        规定 Agent 应该遵守的接口
llm_client.py  规定如何调用大模型
tests/         检查这些代码是否符合预期
```

---

# 二、`core/__init__.py`

内容是：

```python
"""外部服务和基础设施适配器。"""
```

`core` 可以理解为“核心基础设施”目录。

以后这里可能放：

- 大模型客户端
- 数据库连接
- 搜索服务
- 文件存储
- 外部 API 适配器

当前它只是一个说明文件，没有实际代码。

---

# 三、`llm_client.py`

这是这次新增的核心文件。

## 1. 文件说明

```python
"""统一的大模型客户端接口。

Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
"""
```

这里表达了一个重要设计思想：

> Agent 不直接调用 OpenAI、Claude 或其他模型服务，而是统一通过 `LLMClient` 调用。

这样以后更换模型服务时，Agent 不需要跟着大改。

---

## 2. 导入内容

```python
from __future__ import annotations
```

让类型标注延迟处理。

```python
from abc import ABC, abstractmethod
```

用于创建抽象基类和抽象方法。

```python
from typing import Any
```

`Any` 表示任意类型。

---

# 四、`LLMClient` 类

```python
class LLMClient(ABC):
```

这表示定义一个抽象基类。

它不是具体的大模型客户端，而是一份“能力规定”。

它规定所有真正的 LLM 客户端必须提供两个方法：

```python
complete_json()
complete_text()
```

## 为什么要设计这个接口？

假设以后有两个客户端：

```python
OpenAIClient
MockLLMClient
```

只要它们都继承 `LLMClient`，并实现规定的方法，Agent 就可以统一调用：

```python
client.complete_json(...)
client.complete_text(...)
```

Agent 不需要知道底层到底是 OpenAI 还是测试模拟器。

---

## 1. `complete_json`

```python
@abstractmethod
async def complete_json(
    self,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
```

逐部分看：

```python
@abstractmethod
```

表示子类必须实现这个方法。

```python
async def
```

表示这是异步方法。

```python
self
```

表示当前客户端对象本身。

```python
role: str
```

表示调用角色，例如：

```python
"planner"
```

```python
payload: dict[str, Any]
```

表示传给模型的数据是一个字典。

例如：

```python
{
    "query": "新能源汽车行业的发展趋势是什么？"
}
```

```python
-> dict[str, Any]
```

表示返回值应该是一个字典。

方法内部：

```python
"""让模型返回结构化 JSON 数据。"""
raise NotImplementedError
```

`LLMClient` 只规定方法，不提供具体实现，所以这里抛出：

```python
NotImplementedError
```

意思是：

> 这个方法必须由子类实现。

---

## 2. `complete_text`

```python
@abstractmethod
async def complete_text(
    self,
    role: str,
    payload: dict[str, Any],
) -> str:
```

这个方法和前面的区别是：

```python
complete_json -> 返回字典
complete_text -> 返回字符串
```

例如：

```python
complete_json(...)
```

可能返回：

```python
{
    "plan": [...],
    "research_questions": [...]
}
```

而：

```python
complete_text(...)
```

可能返回：

```text
关于新能源汽车行业的研究报告草稿。
```

---

# 五、`MockLLMClient`

```python
class MockLLMClient(LLMClient):
```

这表示：

> `MockLLMClient` 继承 `LLMClient`，并且实现它规定的方法。

`Mock` 的意思是“模拟”。

它不是联网调用真正的大模型，而是直接返回预先写好的结果。

这样做的优点是：

- 不需要 API Key
- 不需要联网
- 测试速度快
- 每次输出一致
- 方便先测试业务流程

---

## 1. `complete_json`

```python
async def complete_json(
    self,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
```

这是对父类方法的具体实现。

### 检查角色

```python
if role != "planner":
    raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
```

当前模拟客户端只支持：

```python
role == "planner"
```

如果传入：

```python
"unknown"
```

就抛出 `ValueError`。

`ValueError` 表示：

> 传入的值不符合要求。

---

### 读取用户问题

```python
query = str(payload.get("query", "")).strip()
```

这句话可以拆成四步：

#### `payload.get("query", "")`

从字典中取出 `query`。

如果没有找到，就使用空字符串：

```python
""
```

#### `str(...)`

把结果转成字符串。

#### `.strip()`

去掉字符串前后的空格。

例如：

```python
"  测试问题  ".strip()
```

结果是：

```python
"测试问题"
```

---

### 检查问题是否为空

```python
if not query:
    raise ValueError("planner 请求缺少 query")
```

如果 `query` 是空字符串，就报错。

也就是说，下面这种调用是不允许的：

```python
client.complete_json("planner", {})
```

因为没有提供用户问题。

---

### 返回结构化结果

```python
return {
    "plan": [
        {
            "title": "现状与定义",
            "description": f"明确“{query}”的研究范围和当前现状。",
        },
        ...
    ],
    "research_questions": [
        f"{query} 的当前现状和关键定义是什么？",
        ...
    ],
}
```

返回值是一个字典，包含两个字段：

```python
"plan"
"research_questions"
```

`plan` 是研究计划列表：

```python
[
    {
        "title": "现状与定义",
        "description": "..."
    }
]
```

`research_questions` 是研究问题列表：

```python
[
    "新能源汽车行业的当前现状和关键定义是什么？",
    "新能源汽车行业面临哪些主要问题，有哪些公开证据？",
    "新能源汽车行业的未来趋势和改进建议是什么？"
]
```

---

## 2. `f"..."` 是什么？

例如：

```python
f"{query} 的未来趋势和改进建议是什么？"
```

这是 Python 的格式化字符串。

如果：

```python
query = "新能源汽车行业"
```

最终结果就是：

```text
新能源汽车行业的未来趋势和改进建议是什么？
```

花括号中的 `query` 会被变量值替换。

---

## 3. `complete_text`

```python
async def complete_text(
    self,
    role: str,
    payload: dict[str, Any],
) -> str:
```

这是模拟生成普通文本的方法。

先检查角色：

```python
if role != "writer":
    raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")
```

当前它只支持：

```python
role == "writer"
```

然后读取问题：

```python
query = str(payload.get("query", "")).strip()
```

最后返回：

```python
return f"关于“{query}”的研究报告草稿。"
```

例如输入：

```python
{
    "query": "新能源汽车行业"
}
```

返回：

```text
关于“新能源汽车行业”的研究报告草稿。
```

当前这个输出只是测试用的简单文本，不是真正经过大模型分析的报告。

---

# 六、`state.py` 和 `llm_client.py` 如何配合？

目前还没有真正的 Planner 或 Writer 类，但未来流程大概会是：

```text
用户输入问题
    ↓
创建 ResearchState
    ↓
Planner 调用 complete_json()
    ↓
把 plan 和 research_questions 写入 state
    ↓
Writer 调用 complete_text()
    ↓
把结果写入 state.final_report
```

例如：

```python
state = ResearchState("新能源汽车行业的发展趋势是什么？")
client = MockLLMClient()
```

Planner 可能得到：

```python
result = await client.complete_json(
    "planner",
    {"query": state.query},
)
```

然后写入状态：

```python
state.plan = result["plan"]
state.research_questions = result["research_questions"]
```

Writer 可能这样调用：

```python
report = await client.complete_text(
    "writer",
    {"query": state.query},
)
```

然后保存报告：

```python
state.final_report = report
```

需要注意：这些 Planner、Writer 的具体类目前还没有写出来。现在只是 `LLMClient` 接口和模拟实现已经准备好了。

---

# 七、`test_llm_client.py`

这个文件用来测试新的 LLM 客户端。

## 1. 测试是否继承正确

```python
def test_mock_client_implements_llm_interface(self):
    self.assertIsInstance(MockLLMClient(), LLMClient)
```

检查：

```python
MockLLMClient()
```

是不是：

```python
LLMClient
```

的实例。

因为 `MockLLMClient` 继承了 `LLMClient`，所以应该通过。

---

## 2. 测试规划结果

```python
result = asyncio.run(
    client.complete_json(
        "planner",
        {"query": "新能源汽车行业的发展趋势是什么？"},
    )
)
```

这里使用：

```python
asyncio.run(...)
```

因为 `complete_json` 是异步方法。

之后检查：

```python
self.assertEqual(len(result["plan"]), 3)
```

确认规划结果有三个计划。

```python
self.assertEqual(len(result["research_questions"]), 3)
```

确认研究问题有三个。

```python
self.assertIn("新能源汽车", result["research_questions"][0])
```

确认第一个问题中包含“新能源汽车”。

---

## 3. 测试未知角色会报错

```python
with self.assertRaises(ValueError):
    asyncio.run(client.complete_json("unknown", {"query": "测试"}))
```

这表示：

> 这段代码应该抛出 `ValueError`，如果没有报错，测试就失败。

因为当前 `MockLLMClient` 不支持 `"unknown"` 角色。

---

## 4. 测试 Writer 文本

```python
result = asyncio.run(
    client.complete_text("writer", {"query": "测试行业"})
)
```

然后检查：

```python
self.assertIn("测试行业", result)
```

确认返回的报告文本包含输入的问题。

---

# 八、当前项目的核心设计

目前项目已经形成了三层分工：

```text
ResearchState
    保存研究数据

BaseAgent
    规定 Agent 的统一行为

LLMClient
    规定大模型调用方式
```

它们之间的关系可以表示为：

```text
Agent
  ↓
使用 LLMClient
  ↓
读取或修改 ResearchState
```

这样做的好处是各部分职责清楚：

- `state.py` 不负责调用模型
- `llm_client.py` 不负责管理整个研究流程
- `base.py` 不负责具体研究内容
- 测试文件负责验证每个部分是否正常

当前项目仍然是学习版，真正的 Planner、Researcher、Writer、Critic 和工作流还没有实现。
<!-- ORIGINAL_ASSISTANT_7_3_END -->



<a id="qa-8"></a>
### 记录 8：PlannerAgent 新增

开始时间（北京时间）：2026-10-06 17:19:31。结束时间：2026-10-06 17:20:54。原始记录 ID：`01a11082-d339-7462-b5b8-b213d8c475cc`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_8_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_8_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_8_2_START -->
我先重新扫描并读取整个项目，找出相对上次新增或修改的文件；这次只重点解释最新变化，同时补足新手容易卡住的语法和执行流程。
<!-- ORIGINAL_ASSISTANT_8_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_8_3_START -->
我已经重新读取了最新项目。相比上次，真正新增的核心内容是：

- [planner.py](D:\课\s4-6\information_deepresearch\backend\app\agents\planner.py)：真正的研究规划 Agent
- [test_planner.py](D:\课\s4-6\information_deepresearch\backend\tests\test_planner.py)：Planner 的测试
- `.gitignore`：告诉 Git 忽略哪些自动生成或敏感文件
- `__pycache__/*.pyc`：Python 自动生成的缓存，不是你需要阅读或手写的代码

下面重点讲 `planner.py`。

# 一、`PlannerAgent` 是干什么的？

它负责把用户提出的一个大问题，拆成：

1. 一份研究计划 `plan`
2. 一组可以继续搜索的研究子问题 `research_questions`

整体过程是：

```text
ResearchState 中的 query
        ↓
PlannerAgent.run()
        ↓
调用 LLMClient
        ↓
得到 plan 和 research_questions
        ↓
检查返回的数据是否合法
        ↓
写回 ResearchState
```

例如用户的问题是：

```text
中国新能源汽车行业的发展趋势是什么？
```

Planner 最后可能产生：

```python
plan = [
    {
        "title": "现状与定义",
        "description": "明确研究范围和当前现状",
    },
    {
        "title": "问题与证据",
        "description": "整理事实、数据和主要争议",
    },
]
```

以及：

```python
research_questions = [
    "当前现状和关键定义是什么？",
    "主要问题和公开证据有哪些？",
    "未来趋势和建议是什么？",
]
```

# 二、文件开头

```python
"""研究规划 Agent。"""
```

这是文件的说明文字，叫作“模块文档字符串”。

```python
from __future__ import annotations
```

让 Python 延迟处理类型标注。当前项目多个文件都采用了这种写法。

```python
from typing import Any
```

导入 `Any`，表示某个值暂时可以是任意类型。

为什么需要 `Any`？

因为大模型返回的内容并不一定可靠。在验证以前，程序不能确定它是列表、字典还是字符串，所以先标记为：

```python
value: Any
```

# 三、导入其他类

```python
from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent
```

分别表示：

```text
LLMClient       负责调用大模型
ResearchState   保存整个研究任务的数据
BaseAgent       规定所有 Agent 的统一接口
```

## `from .base` 中的点是什么意思？

```python
from .base import BaseAgent
```

`.` 表示“当前包”。

当前文件位于：

```text
app/agents/planner.py
```

所以 `.base` 表示同一个 `agents` 目录下的：

```text
app/agents/base.py
```

它也可以写成：

```python
from app.agents.base import BaseAgent
```

当前的相对导入写法更简洁。

# 四、定义 `PlannerAgent`

```python
class PlannerAgent(BaseAgent):
```

意思是：

> 创建一个 `PlannerAgent` 类，并继承 `BaseAgent`。

因为 `BaseAgent` 规定子类必须实现：

```python
async def run(...)
```

所以 `PlannerAgent` 也必须实现自己的 `run()`。

```python
"""把一个用户问题拆成可执行的研究计划。"""
```

这是类的文档字符串，解释这个类负责什么。

# 五、`name = "planner"`

```python
name = "planner"
```

这是 Agent 的角色名称。

后面调用大模型时：

```python
role=self.name
```

实际传入的就是：

```python
role="planner"
```

`MockLLMClient` 正是通过这个角色判断应该返回什么：

```python
if role != "planner":
    raise ValueError(...)
```

# 六、构造方法 `__init__`

```python
def __init__(self, llm: LLMClient):
    self.llm = llm
```

当我们创建 Planner 时：

```python
client = MockLLMClient()
agent = PlannerAgent(client)
```

Python 会自动调用：

```python
PlannerAgent.__init__(agent, client)
```

然后：

```python
self.llm = llm
```

把传进来的大模型客户端保存在 Agent 里面。

所以后面可以使用：

```python
self.llm.complete_json(...)
```

## 为什么不在 Planner 内部直接创建客户端？

现在的设计是从外面传入：

```python
PlannerAgent(MockLLMClient())
```

以后也可以传入真正的客户端：

```python
PlannerAgent(OpenAIClient())
```

Planner 本身不需要修改。

这种做法叫“依赖注入”。对新手来说，先理解成：

> Planner 需要一个大模型客户端，但具体使用哪个客户端，由外部决定。

# 七、`run()` 方法

```python
async def run(self, state: ResearchState) -> ResearchState:
```

它表示：

- `async def`：这是异步方法
- `self`：当前 Planner 对象
- `state`：传入的研究状态
- `state: ResearchState`：期望接收 `ResearchState`
- `-> ResearchState`：期望返回 `ResearchState`

调用方式是：

```python
result = await agent.run(state)
```

测试的普通同步代码中使用：

```python
result = asyncio.run(agent.run(state))
```

# 八、检查用户问题

```python
query = state.query.strip()
```

从状态中读取用户问题，并用 `.strip()` 去掉前后空格。

例如：

```python
"  新能源汽车  ".strip()
```

结果是：

```python
"新能源汽车"
```

然后检查：

```python
if not query:
    raise ValueError("研究问题不能为空")
```

假设用户输入：

```python
ResearchState("   ")
```

去掉空格后就是空字符串：

```python
""
```

`not query` 就是 `True`，程序会主动报错。

这样可以避免把空问题发给大模型。

# 九、调用大模型

```python
result = await self.llm.complete_json(
    role=self.name,
    payload={
        "query": query,
        "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
    },
)
```

## `await` 是什么？

`complete_json()` 是异步方法，所以调用它时需要：

```python
await
```

可以暂时理解为：

> 等待模型完成工作并返回结果，然后继续执行下面的代码。

## `role=self.name`

因为：

```python
self.name == "planner"
```

所以相当于：

```python
role="planner"
```

## `payload={...}`

`payload` 是发送给大模型的数据：

```python
{
    "query": query,
    "instruction": "...",
}
```

例如：

```python
{
    "query": "新能源汽车的发展趋势是什么？",
    "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
}
```

## 为什么使用参数名？

代码写的是：

```python
role=self.name
payload={...}
```

这种叫“关键字参数”。

它比下面的位置参数更清楚：

```python
self.llm.complete_json(self.name, {...})
```

# 十、验证大模型结果

```python
plan = self._validate_plan(result.get("plan"))
research_questions = self._validate_questions(
    result.get("research_questions")
)
```

大模型返回的内容不应该直接相信，因为它可能：

- 缺少字段
- 返回空列表
- 返回错误的数据类型
- 计划中缺少标题
- 产生空的研究问题

因此先执行两个验证方法。

## `result.get("plan")`

如果 `result` 是：

```python
{
    "plan": [...],
    "research_questions": [...]
}
```

那么：

```python
result.get("plan")
```

会取得 `plan`。

如果没有 `plan`，`.get()` 默认返回：

```python
None
```

然后 `_validate_plan()` 会发现它不是有效列表并报错。

# 十一、写回共享状态

```python
state.plan = plan
state.research_questions = research_questions
state.phase = "planning"
return state
```

验证成功后，把结果保存到原来的 `ResearchState` 中。

注意这里没有创建新的状态对象，而是直接修改传入的对象。

所以：

```python
result is state
```

结果为 `True`。

最后状态从：

```python
ResearchState(
    query="测试问题",
    phase="init",
    plan=[],
    research_questions=[],
)
```

变成类似：

```python
ResearchState(
    query="测试问题",
    phase="planning",
    plan=[...],
    research_questions=[...],
)
```

# 十二、`@staticmethod`

两个验证方法前都有：

```python
@staticmethod
```

例如：

```python
@staticmethod
def _validate_plan(value: Any) -> list[dict[str, str]]:
```

普通实例方法需要 `self`：

```python
def run(self, state):
```

但 `_validate_plan()` 不需要使用：

```python
self.llm
self.name
```

它只验证传入的 `value`，所以将它声明为静态方法。

调用时仍然可以写：

```python
self._validate_plan(...)
```

## 方法名前面的 `_`

```python
_validate_plan
_validate_questions
```

单下划线表示：

> 这是类内部使用的辅助方法，不希望外部把它当成主要公开接口。

这只是 Python 命名约定，不是强制权限控制。

# 十三、详细理解 `_validate_plan`

```python
if not isinstance(value, list) or not value:
    raise ValueError("Planner 返回的 plan 必须是非空列表")
```

这里检查两个条件：

```python
not isinstance(value, list)
```

表示它不是列表。

```python
not value
```

表示列表为空。

`or` 表示只要其中一个条件成立，就报错。

所以下面这些都不合格：

```python
None
"计划"
{}
[]
```

只有非空列表才能继续。

## 创建验证后的新列表

```python
validated: list[dict[str, str]] = []
```

它表示：

- `validated` 是一个列表
- 列表中的元素是字典
- 字典的键和值都应该是字符串

## 遍历计划

```python
for index, item in enumerate(value, start=1):
```

`enumerate()` 可以同时得到序号和元素。

例如：

```python
value = ["a", "b"]
```

执行：

```python
enumerate(value, start=1)
```

会依次得到：

```python
index = 1, item = "a"
index = 2, item = "b"
```

从 `1` 开始是为了让错误提示更符合人的习惯。

## 检查元素是不是字典

```python
if not isinstance(item, dict):
    raise ValueError(f"Planner 的第 {index} 个计划不是对象")
```

计划中的每一项必须像这样：

```python
{
    "title": "...",
    "description": "...",
}
```

不能是：

```python
"研究现状"
```

## 提取并清理字段

```python
title = str(item.get("title", "")).strip()
description = str(item.get("description", "")).strip()
```

这里做了三层保护：

1. `.get("title", "")`：没有标题就使用空字符串
2. `str(...)`：转换为字符串
3. `.strip()`：去掉前后空格

## 检查必需字段

```python
if not title or not description:
    raise ValueError(...)
```

标题或描述只要有一个为空，就拒绝这条计划。

## 保存标准化结果

```python
validated.append({
    "title": title,
    "description": description,
})
```

`.append()` 把清理后的计划加入新列表。

最后：

```python
return validated
```

把验证完成的列表返回。

# 十四、详细理解 `_validate_questions`

```python
if not isinstance(value, list) or not value:
```

同样要求结果必须是非空列表。

然后：

```python
questions = [str(item).strip() for item in value]
```

这是“列表推导式”。

它等价于：

```python
questions = []

for item in value:
    question = str(item).strip()
    questions.append(question)
```

作用是把每一个子问题：

1. 转成字符串
2. 去掉前后空格
3. 放进新列表

接着：

```python
if any(not question for question in questions):
```

`any()` 表示：

> 只要里面有一个条件为真，结果就是真。

所以这句话检查的是：

> 是否存在至少一个空的研究问题。

例如：

```python
questions = ["问题一", "", "问题三"]
```

第二项为空，于是抛出异常。

最后：

```python
return questions
```

返回清理后的问题列表。

# 十五、最新的 `test_planner.py`

这个文件负责验证 Planner 是否真的按照上述规则运行。

## `BrokenPlannerClient`

```python
class BrokenPlannerClient(LLMClient):
```

这是一个故意返回错误内容的测试客户端。

```python
async def complete_json(self, role, payload):
    return {"plan": [], "research_questions": []}
```

它始终返回空列表，用来检查 Planner 能否识别非法结果。

它还必须实现：

```python
async def complete_text(...)
```

因为父类 `LLMClient` 规定两个抽象方法都必须实现。即使这次测试不用 `complete_text()`，也不能省略，否则无法创建 `BrokenPlannerClient` 对象。

# 十六、三个 Planner 测试

## 正常情况

```python
state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
agent = PlannerAgent(MockLLMClient())
result = asyncio.run(agent.run(state))
```

然后检查：

```python
self.assertIs(result, state)
```

确认返回的是原来的同一个状态对象。

```python
self.assertEqual(result.phase, "planning")
```

确认阶段被更新。

```python
self.assertEqual(len(result.plan), 3)
```

确认生成三项计划。

```python
self.assertEqual(len(result.research_questions), 3)
```

确认生成三个研究问题。

```python
self.assertIn("新能源汽车", result.plan[0]["description"])
```

确认计划内容确实包含用户问题的信息。

## 空问题测试

```python
with self.assertRaises(ValueError):
```

意思是：

> 下面的代码必须抛出 `ValueError`，否则测试失败。

传入的是：

```python
ResearchState("   ")
```

Planner 使用 `.strip()` 后发现问题为空，因此应该报错。

## 非法模型结果测试

```python
with self.assertRaisesRegex(ValueError, "非空列表"):
```

这里不只要求出现 `ValueError`，还要求错误信息里包含：

```text
非空列表
```

然后使用故意返回空列表的：

```python
BrokenPlannerClient()
```

这证明 `_validate_plan()` 确实阻止了错误数据进入 `ResearchState`。

# 十七、这次更新后，真实调用链已经形成

之前只有接口：

```text
BaseAgent
LLMClient
ResearchState
```

现在第一次出现了真正工作的 Agent：

```text
创建 ResearchState
        ↓
创建 MockLLMClient
        ↓
把客户端交给 PlannerAgent
        ↓
执行 PlannerAgent.run(state)
        ↓
调用 complete_json()
        ↓
验证模型结果
        ↓
更新 state.plan
更新 state.research_questions
更新 state.phase
        ↓
返回同一个 state
```

这次更新最重要的意义是：项目不再只有“接口和数据盒子”，已经有了第一段真正连接起来的业务流程。
<!-- ORIGINAL_ASSISTANT_8_3_END -->



<a id="qa-9"></a>
### 记录 9：SearchClient 新增

开始时间（北京时间）：2026-10-06 17:40:53。结束时间：2026-10-06 17:42:55。原始记录 ID：`01a11096-63fa-7432-aa81-8447826f44fc`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_9_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_9_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_9_2_START -->
我先重新读取项目当前版本，并排除 Python 自动生成的 `__pycache__` 缓存文件，重点找出这次新增加或修改的源码与测试，再逐段解释。
<!-- ORIGINAL_ASSISTANT_9_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_9_3_START -->
我已经重新读取了当前项目。相比上次，最新增加的是：

- [search_client.py](D:\课\s4-6\information_deepresearch\backend\app\core\search_client.py)
- [test_search_client.py](D:\课\s4-6\information_deepresearch\backend\tests\test_search_client.py)

这次更新的主题是：为研究流程增加“搜索客户端”。

之前的流程是：

```text
用户问题
  ↓
PlannerAgent
  ↓
研究计划
```

现在多了一步：

```text
用户问题
  ↓
PlannerAgent 拆分研究问题
  ↓
SearchClient 搜索每个研究问题
  ↓
得到候选资料来源
```

---

# 一、`search_client.py` 文件整体作用

文件开头是：

```python
"""统一的搜索客户端接口。

搜索客户端只负责获取候选来源。
它不负责判断来源是否可信，也不负责把来源写成研究报告。
这些职责会交给后面的 Researcher 和 Writer。
"""
```

这里定义了搜索模块的职责边界。

搜索客户端只负责：

```text
输入：一个研究问题
输出：若干搜索结果
```

它不负责：

- 判断资料是否可信
- 提取事实
- 组织研究证据
- 撰写报告

这样每个模块只负责自己的工作，代码更容易理解和修改。

---

# 二、导入的内容

```python
from __future__ import annotations
```

让类型标注延迟处理。

```python
import hashlib
```

用于根据查询内容生成稳定的摘要值。

```python
from abc import ABC, abstractmethod
```

用于创建抽象类和抽象方法。

```python
from dataclasses import asdict, dataclass
```

- `dataclass`：自动生成数据类的初始化等方法
- `asdict`：把数据类对象转换成字典

```python
from typing import Any
```

`Any` 表示任意类型。

---

# 三、`SearchResult` 数据类

```python
@dataclass
class SearchResult:
```

这表示定义一个“搜索结果的数据容器”。

它对应搜索结果中的一条资料。

## 字段定义

```python
title: str
url: str
snippet: str
query: str
content: str = ""
```

分别表示：

```text
title    资料标题
url      资料链接
snippet  搜索结果摘要
query    这条结果是由什么问题搜索出来的
content  资料正文，默认为空字符串
```

其中前四个字段没有默认值：

```python
title: str
url: str
snippet: str
query: str
```

所以创建对象时必须提供：

```python
result = SearchResult(
    title="资料标题",
    url="https://example.com",
    snippet="资料摘要",
    query="研究问题",
)
```

`content` 有默认值：

```python
content: str = ""
```

所以可以不写：

```python
result.content
```

默认就是：

```python
""
```

## 为什么用 `SearchResult`，而不是直接用字典？

也可以直接使用字典：

```python
{
    "title": "...",
    "url": "...",
    "snippet": "...",
    "query": "...",
}
```

但数据类更清晰：

```python
result.title
result.url
result.snippet
```

而不是：

```python
result["title"]
result["url"]
result["snippet"]
```

数据类还能让字段结构更加明确。

---

# 四、`to_dict()` 方法

```python
def to_dict(self) -> dict[str, Any]:
    """转换成适合放进 ResearchState 的字典。"""
    return asdict(self)
```

这个方法把 `SearchResult` 对象转换成字典。

例如：

```python
result = SearchResult(
    title="新能源汽车行业资料",
    url="https://example.com",
    snippet="行业资料摘要",
    query="新能源汽车行业的市场规模是什么？",
)
```

调用：

```python
result.to_dict()
```

得到：

```python
{
    "title": "新能源汽车行业资料",
    "url": "https://example.com",
    "snippet": "行业资料摘要",
    "query": "新能源汽车行业的市场规模是什么？",
    "content": "",
}
```

## 为什么需要转换成字典？

`ResearchState` 中的 `sources` 定义为：

```python
sources: list[dict[str, Any]]
```

它保存的是字典列表，而搜索客户端返回的是：

```python
list[SearchResult]
```

因此需要：

```python
source_dict = result.to_dict()
state.sources.append(source_dict)
```

这就是 `to_dict()` 的用途。

---

# 五、`SearchClient` 抽象类

```python
class SearchClient(ABC):
```

这是所有搜索客户端的统一接口。

它规定：

> 不管以后使用哪种搜索服务，都必须提供一个 `search()` 方法。

## `search()` 方法

```python
@abstractmethod
async def search(
    self,
    query: str,
    limit: int = 3
) -> list[SearchResult]:
```

逐部分看。

### `query: str`

搜索问题应该是字符串。

例如：

```python
"新能源汽车行业的市场规模是什么？"
```

### `limit: int = 3`

`limit` 是最多希望返回多少条结果。

默认值为：

```python
3
```

所以：

```python
await client.search("研究问题")
```

等价于：

```python
await client.search("研究问题", limit=3)
```

### `-> list[SearchResult]`

表示方法应该返回：

```python
SearchResult 对象组成的列表
```

例如：

```python
[
    SearchResult(...),
    SearchResult(...),
]
```

### 方法体

```python
raise NotImplementedError
```

抽象类不提供具体搜索逻辑，所以这里表示：

> 具体的搜索客户端必须自己实现这个方法。

---

# 六、`MockSearchClient`

```python
class MockSearchClient(SearchClient):
```

这个类继承了 `SearchClient`，是一个模拟搜索客户端。

它不会联网，也不会访问真实搜索引擎。

用途是：

- 先测试业务流程
- 不依赖网络
- 不需要搜索 API Key
- 每次测试结果相同
- 方便新手观察数据流

---

# 七、`MockSearchClient.search()`

```python
async def search(
    self,
    query: str,
    limit: int = 3
) -> list[SearchResult]:
```

这是具体的搜索实现。

## 第一步：清理问题

```python
query = query.strip()
```

去掉查询字符串前后的空格。

例如：

```python
"  测试问题  "
```

会变成：

```python
"测试问题"
```

注意，这里的 `query` 是方法内部的局部变量，不会修改调用者外部的原始字符串。

## 第二步：检查问题是否为空

```python
if not query:
    raise ValueError("搜索问题不能为空")
```

如果输入：

```python
"   "
```

经过 `.strip()` 后变成：

```python
""
```

就会抛出 `ValueError`。

这可以避免搜索无意义的空问题。

## 第三步：检查 `limit`

```python
if limit < 1:
    raise ValueError("limit 必须大于 0")
```

如果调用：

```python
await client.search("测试", limit=0)
```

就会报错。

因为返回数量不能设置为零或负数。

需要注意：当前 Mock 实现虽然检查了 `limit`，但实际上始终只返回一条结果。也就是说，下面两次调用当前结果数量都一样：

```python
await client.search("测试", limit=1)
await client.search("测试", limit=10)
```

都会返回一个 `SearchResult`。

这是当前模拟版本的简化实现，未来真实搜索客户端可能会真正使用 `limit`。

---

# 八、使用 `hashlib.sha1` 生成稳定链接

```python
digest = hashlib.sha1(
    query.encode("utf-8")
).hexdigest()[:10]
```

这行看起来比较复杂，可以拆开理解。

## `query.encode("utf-8")`

把字符串转换成字节。

例如：

```python
"稳定查询".encode("utf-8")
```

得到的是计算机内部使用的字节数据。

## `hashlib.sha1(...)`

对查询内容计算一个 SHA-1 摘要。

可以把它理解成：

> 把一段文字转换成一串固定格式的字符。

相同的查询会产生相同的摘要。

## `.hexdigest()`

把摘要转换成十六进制字符串。

## `[:10]`

只取前 10 个字符。

所以：

```python
digest
```

可能类似：

```text
a3f72c91de
```

这里不是为了安全加密，而是为了得到一个稳定、简短的标识。

---

# 九、创建搜索结果

```python
result = SearchResult(
    title=f"公开资料：{query}",
    url=f"https://example.com/research/{digest}",
    snippet=f"这是针对“{query}”的模拟公开资料摘要，用于验证研究流程。",
    query=query,
    content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。",
)
```

这里创建了一个 `SearchResult` 对象。

假设：

```python
query = "新能源汽车行业的市场规模是什么？"
```

那么结果大致是：

```python
SearchResult(
    title="公开资料：新能源汽车行业的市场规模是什么？",
    url="https://example.com/research/某个摘要",
    snippet="这是针对该问题的模拟公开资料摘要，用于验证研究流程。",
    query="新能源汽车行业的市场规模是什么？",
    content="模拟资料正文：该问题需要结合公开数据、行业实践和政策环境综合判断。",
)
```

## 为什么 URL 每次相同？

因为 URL 使用查询内容生成：

```python
digest = sha1(query)
```

同一个查询：

```python
"稳定查询"
```

每次计算出的摘要都相同。

所以：

```python
first.url == second.url
```

这就是注释中所说的：

```text
同一个查询每次都会得到同一个来源
```

## 这有什么好处？

测试更稳定。

如果每次 URL 都随机生成，那么测试很难判断两次搜索是否得到同一个结果。

---

# 十、返回结果

```python
return [result]
```

注意这里返回的是列表，不是单个对象。

结果类型是：

```python
list[SearchResult]
```

所以即使当前只有一条结果，也要写成：

```python
[result]
```

而不是：

```python
result
```

未来可以改成：

```python
return [result1, result2, result3]
```

---

# 十一、`test_search_client.py`

这个文件用来测试搜索客户端。

## 1. 测试是否实现接口

```python
def test_mock_client_implements_search_interface(self):
    self.assertIsInstance(MockSearchClient(), SearchClient)
```

检查：

```python
MockSearchClient()
```

是不是：

```python
SearchClient
```

的实例。

如果继承关系正确，这个测试就通过。

---

## 2. 测试返回格式

```python
results = asyncio.run(
    client.search("新能源汽车行业的市场规模是什么？")
)
```

因为 `search()` 是异步方法，所以测试中使用：

```python
asyncio.run(...)
```

然后检查：

```python
self.assertEqual(len(results), 1)
```

当前 Mock 搜索应该返回一条结果。

```python
self.assertIsInstance(results[0], SearchResult)
```

确认列表中的元素确实是 `SearchResult` 对象。

```python
self.assertTrue(results[0].title)
```

确认标题不是空的。

```python
self.assertTrue(results[0].url.startswith("https://"))
```

确认 URL 以 HTTPS 开头。

```python
self.assertTrue(results[0].snippet)
```

确认摘要不是空的。

```python
self.assertEqual(
    results[0].query,
    "新能源汽车行业的市场规模是什么？"
)
```

确认返回结果中保存的原始查询是正确的。

---

## 3. 测试同一个查询的 URL 稳定

```python
first = asyncio.run(client.search("稳定查询"))[0]
second = asyncio.run(client.search("稳定查询"))[0]

self.assertEqual(first.url, second.url)
```

这里的 `[0]` 表示取列表中的第一项。

两次使用完全相同的查询，所以应该得到相同 URL。

这个测试验证的是：

```text
相同输入 -> 相同摘要 -> 相同 URL
```

---

## 4. 测试非法输入

```python
with self.assertRaises(ValueError):
    asyncio.run(client.search("   "))
```

确认空问题会报错。

```python
with self.assertRaises(ValueError):
    asyncio.run(client.search("测试", limit=0))
```

确认 `limit=0` 会报错。

`with self.assertRaises(...)` 的意思是：

> 这段代码必须抛出指定异常，否则测试失败。

---

# 十二、这次更新和 `ResearchState` 的关系

`ResearchState` 中已经有：

```python
sources: list[dict[str, Any]] = field(default_factory=list)
```

搜索客户端返回：

```python
list[SearchResult]
```

如果以后写 Researcher，可能会这样处理：

```python
results = await search_client.search(question)

for result in results:
    state.sources.append(result.to_dict())
```

数据流就是：

```text
研究问题
    ↓
SearchClient.search()
    ↓
SearchResult
    ↓
to_dict()
    ↓
ResearchState.sources
```

其中：

- `SearchClient` 负责搜索
- `SearchResult` 负责统一描述一条结果
- `to_dict()` 负责转换格式
- `ResearchState.sources` 负责保存结果

---

# 十三、当前各个模块的职责

现在项目可以分成四个核心部分：

```text
ResearchState
保存整个研究任务的数据

LLMClient
规定如何调用大模型

PlannerAgent
调用 LLM，把大问题拆成研究计划

SearchClient
根据研究问题获取候选资料
```

当前完整流程还没有串成一个总工作流，但各个零件已经在逐步建立。

另外，当前搜索实现是模拟版：

- 不联网
- 不访问真实搜索引擎
- 返回固定格式的模拟资料
- `limit` 目前只做输入校验，还没有控制返回数量

这些是当前代码的实际状态。
<!-- ORIGINAL_ASSISTANT_9_3_END -->



<a id="qa-10"></a>
### 记录 10：ResearcherAgent 新增

开始时间（北京时间）：2026-10-06 17:48:11。结束时间：2026-10-06 17:49:02。原始记录 ID：`01a1109d-1029-7e71-819f-35d5bfc61f74`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_10_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_10_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_10_2_START -->
我先按约定重新扫描并读取项目当前版本，只分析相对上一轮新增或变更的源码和测试，自动生成的缓存文件会排除。
<!-- ORIGINAL_ASSISTANT_10_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_10_3_START -->
我已经重新读取了整个项目。相比上一轮，最新增加的是：

- [researcher.py](D:\课\s4-6\information_deepresearch\backend\app\agents\researcher.py)
- [test_researcher.py](D:\课\s4-6\information_deepresearch\backend\tests\test_researcher.py)

这次更新把“规划”和“搜索”真正连接起来了：

```text
用户问题
→ PlannerAgent 生成研究子问题
→ ResearcherAgent 逐个搜索
→ 去除重复来源
→ 写入 state.sources 和 state.references
```

## `ResearcherAgent` 的作用

```python
class ResearcherAgent(BaseAgent):
```

它继承 `BaseAgent`，所以必须实现异步的 `run()` 方法。它当前只负责搜索和去重，还没有提取事实，因此 `state.facts` 暂时不会被修改。

```python
name = "researcher"
```

这是该 Agent 的身份名称。目前没有用它调用 LLM，但为后续统一管理 Agent 做准备。

## 构造方法

```python
def __init__(self, search: SearchClient, results_per_question: int = 3):
```

创建 Researcher 时，需要从外部传入搜索客户端：

```python
agent = ResearcherAgent(MockSearchClient())
```

其中：

- `search: SearchClient`：搜索服务
- `results_per_question: int = 3`：每个问题最多请求三条结果

```python
if results_per_question < 1:
    raise ValueError("results_per_question 必须大于 0")
```

这是提前检查配置，避免出现 `0` 或负数。

```python
self.search = search
self.results_per_question = results_per_question
```

把传入的值保存到当前对象中，后面的 `run()` 可以通过 `self.search` 使用它们。

## 清理研究问题

```python
questions = [question.strip() for question in state.research_questions]
```

这是列表推导式，等价于：

```python
questions = []
for question in state.research_questions:
    questions.append(question.strip())
```

作用是删除每个问题前后的空格。

接着：

```python
questions = [question for question in questions if question]
```

只保留非空问题。例如：

```python
["问题一", "   ", "问题二"]
```

处理后变成：

```python
["问题一", "问题二"]
```

如果最后没有任何问题：

```python
if not questions:
    raise ValueError("没有可执行的研究子问题")
```

这也意味着 Researcher 通常应该在 Planner 之后运行。

## 为什么复制原有来源？

```python
collected_sources = list(state.sources)
```

`list(...)` 创建一个新的列表，把已有来源复制进去。

如果直接写：

```python
collected_sources = state.sources
```

两个变量会指向同一个列表，后续修改 `collected_sources` 时会立刻修改 `state.sources`。当前写法会先在独立列表中收集数据，最后再统一写回状态。

注意这里只复制列表外层，列表里面的字典仍然是原来的对象，属于“浅拷贝”。

## 逐个搜索问题

```python
for question in questions:
```

遍历所有研究子问题。

```python
results = await self.search.search(
    query=question,
    limit=self.results_per_question,
)
```

调用搜索客户端。因为 `search()` 是异步方法，所以需要 `await`。

参数采用关键字写法：

```python
query=question
limit=self.results_per_question
```

这样能清楚看出每个值对应哪个参数。

## 把结果转换成字典

搜索结果的类型是：

```python
list[SearchResult]
```

而 `ResearchState.sources` 保存的是：

```python
list[dict]
```

因此需要：

```python
collected_sources.extend(result.to_dict() for result in results)
```

这里包含两个知识点。

`result.to_dict()` 把 `SearchResult` 转成字典：

```python
{
    "title": "...",
    "url": "...",
    "snippet": "...",
    "query": "...",
    "content": "...",
}
```

`extend()` 会将多项加入列表：

```python
sources.extend([result1, result2])
```

而 `append()` 会把整个列表作为一项加入：

```python
sources.append([result1, result2])
```

这里需要的是 `extend()`。

圆括号里的：

```python
result.to_dict() for result in results
```

叫生成器表达式，会逐个转换结果，不必先建立额外列表。

## 按 URL 去重

```python
state.sources = self._deduplicate_sources(collected_sources)
```

调用内部辅助方法，删除 URL 相同的来源。

```python
@staticmethod
def _deduplicate_sources(sources: list[dict]) -> list[dict]:
```

这是静态方法，因为它只处理传入的数据，不需要使用 `self.search` 等对象属性。

```python
unique: dict[str, dict] = {}
```

创建一个字典：

- 键是 URL
- 值是完整来源字典

然后遍历：

```python
for source in sources:
    url = str(source.get("url", "")).strip()
```

这一步：

1. 用 `.get()` 读取 URL，不存在时返回空字符串；
2. 用 `str()` 转为字符串；
3. 用 `.strip()` 删除两端空格。

```python
if url and url not in unique:
    unique[url] = source
```

只有同时满足两个条件才保存：

- `url` 不是空字符串；
- 这个 URL 之前没有出现过。

因此相同 URL 只保留第一次出现的来源。Python 字典会保留插入顺序，所以最终顺序也与首次出现的顺序一致。

```python
return list(unique.values())
```

取出字典中的所有来源，再转换回列表。

## 生成精简引用

```python
state.references = [
    {
        "title": source["title"],
        "url": source["url"],
    }
    for source in state.sources
    if source.get("url")
]
```

这是一个多行列表推导式。它从完整来源中只留下：

```python
title
url
```

完整来源 `sources` 适合后续研究：

```python
{
    "title": "...",
    "url": "...",
    "snippet": "...",
    "query": "...",
    "content": "...",
}
```

精简引用 `references` 适合最后报告列出参考资料：

```python
{
    "title": "...",
    "url": "...",
}
```

`if source.get("url")` 表示只为存在 URL 的来源生成引用。

## 更新研究阶段

```python
state.phase = "researching"
return state
```

Researcher 完成后，将阶段设置为 `"researching"`，然后返回同一个状态对象。

此时状态变化大致是：

```text
运行前：
research_questions = [...]
sources = []
references = []
phase = "planning"

运行后：
research_questions = [...]
sources = [完整来源...]
references = [精简引用...]
phase = "researching"
```

## 新增测试详解

第一个测试把 Planner 和 Researcher 串起来：

```python
async def run_chain():
    state = ResearchState(...)
    await PlannerAgent(MockLLMClient()).run(state)
    await ResearcherAgent(MockSearchClient()).run(state)
    return state
```

这里定义异步函数，是因为一个异步流程中需要连续使用两次 `await`。外层再用：

```python
state = asyncio.run(run_chain())
```

启动整个异步流程。

测试确认 Planner 生成三个问题，Researcher 对三个问题各搜索一次，所以最终有：

```python
3 个 research_questions
3 个 sources
3 个 references
```

第二个测试故意设置重复问题：

```python
state.research_questions = ["相同问题", "相同问题"]
```

`MockSearchClient` 对相同查询生成相同 URL，因此虽然搜索了两次，去重后只有：

```python
1 个 source
1 个 reference
```

第三个测试没有设置研究子问题：

```python
state = ResearchState("还没有规划的问题")
```

此时 `state.research_questions` 是空列表，Researcher 应抛出 `ValueError`。`assertRaisesRegex` 还要求错误信息包含“研究子问题”。

这次更新后，项目已经出现第一条完整的小链路：

```text
ResearchState.query
→ PlannerAgent
→ state.research_questions
→ ResearcherAgent
→ SearchClient
→ state.sources
→ state.references
```

目前的边界也很明确：Researcher 只收集和去重资料，还没有判断可信度，也没有向 `state.facts` 写入事实。
<!-- ORIGINAL_ASSISTANT_10_3_END -->



<a id="qa-11"></a>
### 记录 11：Researcher 如何调用 SearchClient

开始时间（北京时间）：2026-10-06 17:57:53。结束时间：2026-10-06 17:58:49。原始记录 ID：`01a110a5-f255-7812-887a-c03b7befbe47`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_11_1_START -->
```text
research agent 是如何调用research_client的

```
<!-- ORIGINAL_USER_11_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_11_2_START -->
我先重新读取项目当前版本，重点核对 `researcher.py` 和搜索客户端文件。你说的 `research_client`，我也会确认项目里实际对应的文件和类名。
<!-- ORIGINAL_ASSISTANT_11_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_11_3_START -->
我已重新读取最新项目。先纠正一个名称：项目里没有 `research_client.py`，实际文件是 [search_client.py](D:\课\s4-6\information_deepresearch\backend\app\core\search_client.py)，里面定义了 `SearchClient` 和 `MockSearchClient`。

`ResearcherAgent` 调用它的核心过程可以概括为：

```text
外部创建 MockSearchClient
        ↓
把它传给 ResearcherAgent
        ↓
ResearcherAgent 保存为 self.search
        ↓
run() 中调用 self.search.search(...)
        ↓
获得 SearchResult 列表
        ↓
转换成字典并写入 state.sources
```

## 1. 先导入搜索接口

[researcher.py](D:\课\s4-6\information_deepresearch\backend\app\agents\researcher.py) 中有：

```python
from app.core.search_client import SearchClient
```

这行只是导入 `SearchClient` 类，方便：

- 给参数添加类型标注；
- 说明 Researcher 需要什么样的搜索客户端。

它并没有在这里创建搜索客户端。

## 2. 构造方法接收搜索客户端

```python
def __init__(
    self,
    search: SearchClient,
    results_per_question: int = 3,
):
```

这里的：

```python
search: SearchClient
```

表示：

> `search` 参数应该是一个符合 `SearchClient` 接口的对象。

注意：`SearchClient` 是抽象类，不能直接创建：

```python
SearchClient()  # 会报错
```

实际传入的是实现了这个接口的具体对象，比如：

```python
MockSearchClient()
```

## 3. 把客户端保存到对象中

```python
self.search = search
```

假设外部这样创建 Researcher：

```python
search_client = MockSearchClient()
agent = ResearcherAgent(search_client)
```

执行构造方法后，可以理解成：

```python
agent.search = search_client
```

因此，`agent` 内部记住了这个搜索客户端。

这就是“依赖注入”：Researcher 需要搜索能力，但不在内部决定使用哪一种搜索服务，而是由外部把搜索客户端交给它。

## 4. 测试中实际是这样传入的

[test_researcher.py](D:\课\s4-6\information_deepresearch\backend\tests\test_researcher.py) 中：

```python
await ResearcherAgent(MockSearchClient()).run(state)
```

这句可以拆成下面几步：

```python
# 第一步：创建模拟搜索客户端
search_client = MockSearchClient()

# 第二步：把搜索客户端交给 ResearcherAgent
researcher = ResearcherAgent(search_client)

# 第三步：让 ResearcherAgent 开始工作
await researcher.run(state)
```

所以不是 `ResearcherAgent` 自己创建了 `MockSearchClient`，而是测试代码创建以后传给它。

## 5. `run()` 中调用搜索方法

Researcher 先取得研究子问题：

```python
questions = [
    question.strip()
    for question in state.research_questions
]
```

然后逐个处理：

```python
for question in questions:
```

真正调用搜索客户端的是：

```python
results = await self.search.search(
    query=question,
    limit=self.results_per_question,
)
```

这里两个 `search` 很容易混淆。

第一个：

```python
self.search
```

是保存在 Researcher 中的搜索客户端对象，相当于：

```python
MockSearchClient()
```

第二个：

```python
.search(...)
```

是该客户端对象拥有的方法。

因此整句可以理解为：

```python
搜索结果 = 等待搜索客户端搜索当前问题
```

假设：

```python
self.search = MockSearchClient()
question = "新能源汽车行业的市场规模是什么？"
self.results_per_question = 3
```

那么实际效果类似于：

```python
results = await MockSearchClient().search(
    query="新能源汽车行业的市场规模是什么？",
    limit=3,
)
```

## 6. 为什么需要 `await`？

`SearchClient` 中的方法定义为：

```python
async def search(...)
```

所以调用时必须使用：

```python
await self.search.search(...)
```

真实搜索通常需要等待网络返回结果。`await` 的意思可以暂时理解为：

> 等待这次搜索完成，拿到结果后，再继续执行下面的代码。

虽然现在的 `MockSearchClient` 不联网，但它保持异步形式，以便以后替换成真实搜索服务时，Researcher 的调用方式不需要修改。

## 7. `MockSearchClient.search()` 做了什么？

当前模拟搜索实现是：

```python
async def search(
    self,
    query: str,
    limit: int = 3,
) -> list[SearchResult]:
```

它接收 Researcher 传来的：

```python
query=question
limit=self.results_per_question
```

然后检查输入：

```python
query = query.strip()

if not query:
    raise ValueError("搜索问题不能为空")

if limit < 1:
    raise ValueError("limit 必须大于 0")
```

接着创建一条模拟搜索结果：

```python
result = SearchResult(
    title=...,
    url=...,
    snippet=...,
    query=query,
    content=...,
)
```

最后返回一个列表：

```python
return [result]
```

因此 Researcher 中的：

```python
results
```

实际是：

```python
[
    SearchResult(...)
]
```

## 8. 搜索结果如何进入 `ResearchState`？

SearchClient 返回的是 `SearchResult` 对象，但 `state.sources` 保存的是字典，所以 Researcher 执行：

```python
collected_sources.extend(
    result.to_dict() for result in results
)
```

它等价于：

```python
for result in results:
    source_dict = result.to_dict()
    collected_sources.append(source_dict)
```

`to_dict()` 会把：

```python
SearchResult(
    title="...",
    url="...",
    snippet="...",
    query="...",
    content="...",
)
```

转换成：

```python
{
    "title": "...",
    "url": "...",
    "snippet": "...",
    "query": "...",
    "content": "...",
}
```

全部问题搜索完成后，再去重并写入状态：

```python
state.sources = self._deduplicate_sources(collected_sources)
```

随后生成精简引用：

```python
state.references = [
    {
        "title": source["title"],
        "url": source["url"],
    }
    for source in state.sources
    if source.get("url")
]
```

最后修改阶段：

```python
state.phase = "researching"
```

## 9. 完整执行链

测试中的真实执行顺序是：

```python
state = ResearchState("中国新能源汽车行业的发展趋势是什么？")

await PlannerAgent(MockLLMClient()).run(state)
```

Planner 先写入：

```python
state.research_questions = [
    "问题一",
    "问题二",
    "问题三",
]
```

然后：

```python
await ResearcherAgent(MockSearchClient()).run(state)
```

Researcher 内部执行：

```text
读取 state.research_questions
           ↓
遍历每一个 question
           ↓
self.search.search(question)
           ↓
MockSearchClient 返回 SearchResult
           ↓
SearchResult.to_dict()
           ↓
按 URL 去重
           ↓
写入 state.sources
           ↓
生成 state.references
```

最关键的三行就是：

```python
# 外部把搜索客户端传入 Researcher
researcher = ResearcherAgent(MockSearchClient())

# Researcher 内部保存客户端
self.search = search

# run() 中通过保存的客户端执行搜索
results = await self.search.search(...)
```

这种设计使得以后把 `MockSearchClient` 换成真实客户端时，`ResearcherAgent` 的主要代码无需改变。
<!-- ORIGINAL_ASSISTANT_11_3_END -->



<a id="qa-12"></a>
### 记录 12：FactExtractor 新增

开始时间（北京时间）：2026-10-06 18:00:39。结束时间：2026-10-06 18:04:03。原始记录 ID：`01a110a8-7b91-70a0-8293-81e8dbabd196`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_12_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_12_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_12_2_START -->
我先重新读取当前项目的全部源码和测试，确认这次相对上一轮新增了哪些内容；我会重点关注新出现的 Agent、客户端接口、状态字段和对应测试。
<!-- ORIGINAL_ASSISTANT_12_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_12_3_START -->
我已经重新阅读了项目当前版本。相比上一轮，最新更新主要有三部分：

1. 新增 [fact_extractor.py](D:\课\s4-6\information_deepresearch\backend\app\agents\fact_extractor.py)
2. 修改 [llm_client.py](D:\课\s4-6\information_deepresearch\backend\app\core\llm_client.py)，让模拟大模型支持 `fact_extractor`
3. 新增 [test_fact_extractor.py](D:\课\s4-6\information_deepresearch\backend\tests\test_fact_extractor.py)，并扩展了 `test_llm_client.py`

现在研究流程从：

```text
规划问题
→ 搜索来源
```

扩展为：

```text
规划问题
→ 搜索来源
→ 从来源中提取带引用的事实
```

---

# 一、新增的 `FactExtractorAgent`

文件开头：

```python
"""从候选来源中提取带来源的结构化事实。"""
```

这里的关键词是：

```text
结构化事实
```

搜索得到的来源是资料，事实是从资料中提取出来、以后可以写进报告的内容。

例如来源：

```python
{
    "title": "某行业报告",
    "url": "https://example.com/report",
    "content": "2025 年该行业市场规模达到 100 亿元。",
}
```

提取出的事实可能是：

```python
{
    "content": "2025 年该行业市场规模达到 100 亿元。",
    "source_title": "某行业报告",
    "source_url": "https://example.com/report",
    "source_type": "web",
    "confidence": 0.7,
}
```

这里事实不只是文字，还带有它来自哪个 URL 的信息。

---

# 二、定义 `FactExtractorAgent`

```python
class FactExtractorAgent(BaseAgent):
```

这表示：

- 创建一个叫 `FactExtractorAgent` 的类；
- 它继承 `BaseAgent`；
- 因此必须实现 `run()` 方法。

```python
"""把网页来源转换成报告可以引用的事实。"""
```

这个类的职责非常明确：

```text
输入：state.sources
输出：state.facts
```

当前它不负责：

- 搜索网页；
- 写最终报告；
- 判断整个报告质量。

它只负责从已有来源中提取事实。

```python
name = "fact_extractor"
```

这个名字之后会传给 LLM：

```python
role=self.name
```

也就是：

```python
role="fact_extractor"
```

---

# 三、构造方法

```python
def __init__(self, llm: LLMClient):
    self.llm = llm
```

创建时需要传入一个大模型客户端：

```python
agent = FactExtractorAgent(MockLLMClient())
```

可以拆成：

```python
client = MockLLMClient()
agent = FactExtractorAgent(client)
```

构造方法执行后，相当于：

```python
agent.llm = client
```

以后 `FactExtractorAgent` 就能调用：

```python
self.llm.complete_json(...)
```

这和 `PlannerAgent` 的设计一样，都是把依赖的客户端从外部传入。

---

# 四、`run()` 方法的整体流程

```python
async def run(self, state: ResearchState) -> ResearchState:
```

它接收共享状态：

```python
state
```

并且最终返回同一个状态对象。

执行过程是：

```text
检查是否有来源
    ↓
调用 LLM
    ↓
要求 LLM 返回 facts
    ↓
验证每一条 fact
    ↓
去除重复事实
    ↓
写入 state.facts
    ↓
返回 state
```

---

# 五、首先检查来源是否存在

```python
if not state.sources:
    raise ValueError("没有可供事实提取的来源")
```

`state.sources` 是一个列表。

如果它是：

```python
[]
```

那么：

```python
not state.sources
```

就是 `True`。

于是程序报错。

这是合理的，因为没有来源就没有办法提取事实。

正确顺序应该是：

```text
先运行 ResearcherAgent
再运行 FactExtractorAgent
```

也就是：

```python
await ResearcherAgent(MockSearchClient()).run(state)
await FactExtractorAgent(MockLLMClient()).run(state)
```

不能一开始直接运行事实提取器。

---

# 六、调用大模型提取事实

```python
result = await self.llm.complete_json(
    role=self.name,
    payload={
        "query": state.query,
        "sources": state.sources,
        "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
    },
)
```

这里调用的是：

```python
self.llm.complete_json(...)
```

因为事实提取结果需要结构化 JSON，而不是普通字符串。

## `role=self.name`

因为：

```python
self.name == "fact_extractor"
```

所以实际传入：

```python
role="fact_extractor"
```

`MockLLMClient` 会根据这个角色进入事实提取逻辑。

## `payload`

传给模型的内容包括：

```python
{
    "query": state.query,
    "sources": state.sources,
    "instruction": "...",
}
```

分别表示：

- 用户最初的问题；
- 搜索得到的来源；
- 给模型的任务要求。

例如：

```python
{
    "query": "中国新能源汽车行业的发展趋势是什么？",
    "sources": [
        {
            "title": "...",
            "url": "https://example.com/...",
            "content": "...",
        }
    ],
    "instruction": "只提取来源正文中明确表达..."
}
```

---

# 七、从返回结果中取出 `facts`

```python
facts = self._validate_facts(
    result.get("facts"),
    state.sources,
)
```

`result` 预期是：

```python
{
    "facts": [...]
}
```

所以：

```python
result.get("facts")
```

取得事实列表。

如果返回结果没有 `"facts"`，`.get()` 会得到：

```python
None
```

然后 `_validate_facts()` 会检查它是否合法。

同时把 `state.sources` 传进去，是为了验证每个事实引用的 URL 是否真的来自已有来源。

---

# 八、写回状态并去重

```python
state.facts = self._deduplicate_facts(state.facts + facts)
```

这句很重要。

它不是直接：

```python
state.facts = facts
```

而是把旧事实和新事实合并：

```python
state.facts + facts
```

例如原来状态中已有：

```python
state.facts = [旧事实]
```

这次新提取出：

```python
facts = [新事实]
```

合并后：

```python
[旧事实, 新事实]
```

然后再去重。

这样可以支持重复运行 FactExtractor，而不会简单覆盖以前保存的事实。

```python
state.phase = "researching"
return state
```

事实提取完成后，阶段仍然设为：

```python
"researching"
```

因为当前项目还没有单独的 `"extracting_facts"` 阶段。提取事实仍然属于研究阶段的一部分。

---

# 九、`_validate_facts()` 方法

```python
@staticmethod
def _validate_facts(
    value: Any,
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
```

这是一个静态方法。

它需要两个输入：

```text
value    LLM 返回的 facts
sources  当前已有的来源
```

返回：

```python
list[dict[str, Any]]
```

也就是验证过的事实字典列表。

## 1. 检查 facts 是否为列表

```python
if not isinstance(value, list):
    raise ValueError("FactExtractor 返回的 facts 必须是列表")
```

要求模型返回：

```python
[
    {...},
    {...}
]
```

下面这些都不合格：

```python
None
{}
"一条事实"
```

和 Planner 不同，这里没有要求列表必须非空。

所以：

```python
[]
```

在当前实现中是允许的。

这表示模型可以判断：

```text
当前来源没有提取出合适的事实
```

---

## 2. 建立允许使用的 URL 集合

```python
allowed_urls = {
    str(source.get("url", "")).strip()
    for source in sources
    if source.get("url")
}
```

这是集合推导式。

假设来源是：

```python
sources = [
    {"url": "https://a.com"},
    {"url": "https://b.com"},
]
```

得到：

```python
allowed_urls = {
    "https://a.com",
    "https://b.com",
}
```

为什么使用集合？

因为后面要频繁检查：

```python
source_url not in allowed_urls
```

集合特别适合做“是否存在”的判断。

`if source.get("url")` 会过滤没有 URL 的来源。

---

## 3. 创建验证后的列表

```python
validated: list[dict[str, Any]] = []
```

后面每条事实经过检查后，都会被放进这里。

---

## 4. 遍历每一条事实

```python
for index, item in enumerate(value, start=1):
```

例如：

```python
value = [事实一, 事实二]
```

循环过程中：

```text
第一次：index = 1，item = 事实一
第二次：index = 2，item = 事实二
```

`start=1` 是为了让错误消息中的编号从第 1 条开始，而不是第 0 条。

---

## 5. 检查每条事实是不是字典

```python
if not isinstance(item, dict):
    raise ValueError(
        f"FactExtractor 的第 {index} 个事实不是对象"
    )
```

每条事实必须是类似这样的字典：

```python
{
    "content": "...",
    "source_url": "...",
    "confidence": 0.8,
}
```

不能直接返回字符串：

```python
"这是一条事实"
```

---

## 6. 读取事实内容和来源 URL

```python
content = str(item.get("content", "")).strip()
source_url = str(item.get("source_url", "")).strip()
```

这两项是必需的。

例如：

```python
content = "2025 年市场规模达到 100 亿元"
source_url = "https://example.com/report"
```

这里依次做了：

1. 从字典中取字段；
2. 没有字段时使用空字符串；
3. 转成字符串；
4. 去掉前后空格。

---

## 7. 检查必需字段

```python
if not content or not source_url:
    raise ValueError(
        f"FactExtractor 的第 {index} 个事实缺少 content 或 source_url"
    )
```

事实至少必须有：

```text
content
source_url
```

缺少任何一个都不允许保存。

---

## 8. 检查来源 URL 是否真实存在

```python
if source_url not in allowed_urls:
    raise ValueError(
        f"FactExtractor 的第 {index} 个事实引用了未知来源"
    )
```

这是这次更新最重要的安全检查之一。

假设当前已有来源：

```python
state.sources = [
    {
        "url": "https://known.example.com"
    }
]
```

但模型返回：

```python
{
    "content": "一条事实",
    "source_url": "https://unknown.example.com",
}
```

这个 URL 不在 `allowed_urls` 中，程序就拒绝它。

这样可以防止模型生成一个看似有引用、但实际上不在研究材料里的来源。

---

# 十、处理 `confidence`

```python
try:
    confidence = float(item.get("confidence", 0.0))
except (TypeError, ValueError) as exc:
    raise ValueError(
        f"FactExtractor 的第 {index} 个事实 confidence 无效"
    ) from exc
```

`confidence` 表示置信度。

例如：

```python
0.7
```

可以理解为 70% 的置信程度。

## 为什么使用 `float()`？

模型可能返回：

```python
0.8
```

也可能返回：

```python
"0.8"
```

通过：

```python
float(...)
```

可以把字符串 `"0.8"` 转成数字 `0.8`。

如果返回：

```python
"很高"
```

就无法转换，会进入 `except`。

## `except (...)`

```python
except (TypeError, ValueError) as exc:
```

这里同时捕获两种错误：

- `TypeError`：类型不适合转换；
- `ValueError`：值不能转换成数字。

```python
raise ... from exc
```

表示抛出更适合业务阅读的新错误，同时保留原始错误原因。

---

## 检查范围

```python
if not 0 <= confidence <= 1:
    raise ValueError(
        f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间"
    )
```

这里要求：

```python
0 <= confidence <= 1
```

例如下面合法：

```python
0
0.5
1
```

下面不合法：

```python
-0.1
1.5
```

---

# 十一、标准化保存事实

```python
validated.append(
    {
        "content": content,
        "source_title": str(item.get("source_title", "")).strip(),
        "source_url": source_url,
        "source_type": str(item.get("source_type", "web")).strip() or "web",
        "confidence": confidence,
    }
)
```

这一步会建立一个统一格式的事实。

字段含义：

```text
content       事实内容
source_title  来源标题
source_url    来源链接
source_type   来源类型
confidence    置信度
```

## `source_type` 的默认逻辑

```python
str(item.get("source_type", "web")).strip() or "web"
```

它有两层默认保护：

第一层：

```python
item.get("source_type", "web")
```

如果没有这个字段，就使用 `"web"`。

第二层：

```python
... or "web"
```

如果模型明确返回空字符串：

```python
""
```

也改成 `"web"`。

所以：

```python
source_type = ""
```

最终也会保存为：

```python
"web"
```

最后：

```python
return validated
```

返回所有验证通过的事实。

---

# 十二、`_deduplicate_facts()` 去重

```python
@staticmethod
def _deduplicate_facts(
    facts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
```

它负责去除重复事实。

## 去重键

```python
unique: dict[tuple[str, str], dict[str, Any]] = {}
```

字典的键是一个二元组：

```python
(source_url, content)
```

也就是说，程序认为：

```text
同一个来源 URL + 相同事实内容
```

就是重复事实。

## 生成键

```python
key = (
    str(fact.get("source_url", "")).strip(),
    str(fact.get("content", "")).strip(),
)
```

例如：

```python
(
    "https://example.com/report",
    "2025 年市场规模达到 100 亿元"
)
```

## 排除完全空的事实

```python
if key != ("", ""):
```

如果来源 URL 和事实内容都为空，就不保存。

## `setdefault`

```python
unique.setdefault(key, fact)
```

意思是：

> 如果这个键还不存在，就保存当前事实；如果已经存在，就保留原来的事实。

所以第一次出现的事实会被保留，后面重复的事实会被忽略。

最后：

```python
return list(unique.values())
```

把去重字典中的事实重新转换成列表。

---

# 十三、`llm_client.py` 的最新变化

之前 `MockLLMClient.complete_json()` 只支持：

```python
role == "planner"
```

现在改成了分支结构：

```python
if role == "planner":
    ...
    
if role == "fact_extractor":
    ...
    
raise ValueError(...)
```

## 新增 `fact_extractor` 分支

```python
if role == "fact_extractor":
    facts = []
    for source in payload.get("sources", []):
```

它从 payload 中读取来源列表，并逐个处理。

## 获取正文内容

```python
content = str(
    source.get("content") or source.get("snippet") or ""
).strip()
```

这里使用了 `or`：

```python
source.get("content") or source.get("snippet") or ""
```

意思是：

1. 优先使用 `content`；
2. 如果 `content` 为空，再使用 `snippet`；
3. 如果两者都没有，再使用空字符串。

例如：

```python
source = {
    "content": "正文内容",
    "snippet": "摘要内容",
}
```

使用正文。

如果：

```python
source = {
    "content": "",
    "snippet": "摘要内容",
}
```

则使用摘要。

## 获取 URL

```python
url = str(source.get("url", "")).strip()
```

如果正文或 URL 缺失：

```python
if not content or not url:
    continue
```

`continue` 表示跳过当前这条来源，继续处理下一条来源。

## 生成模拟事实

```python
facts.append(
    {
        "content": content,
        "source_title": str(source.get("title", "")).strip(),
        "source_url": url,
        "source_type": "web",
        "confidence": 0.7,
    }
)
```

当前 Mock 客户端并没有真的进行智能提取，它只是把来源正文直接作为事实内容，并统一设置：

```python
confidence = 0.7
source_type = "web"
```

这只是为了验证流程，不代表真实模型的判断能力。

最终返回：

```python
return {"facts": facts}
```

---

# 十四、新增 `test_fact_extractor.py`

## 第一个测试：完整链路

```python
async def run_chain():
    state = ResearchState(...)
    await PlannerAgent(MockLLMClient()).run(state)
    await ResearcherAgent(MockSearchClient()).run(state)
    await FactExtractorAgent(MockLLMClient()).run(state)
    return state
```

现在完整链路是：

```text
ResearchState
    ↓
PlannerAgent
    ↓
ResearcherAgent
    ↓
FactExtractorAgent
```

执行完后检查：

```python
self.assertEqual(state.phase, "researching")
```

当前事实提取完成后，阶段仍为 `researching`。

```python
self.assertEqual(len(state.sources), 3)
```

Planner 生成三个研究问题，MockSearchClient 为每个问题生成一个来源，因此有三个来源。

```python
self.assertEqual(len(state.facts), 3)
```

每个来源生成一条事实，因此有三个事实。

```python
self.assertTrue(all(fact["source_url"] for fact in state.facts))
```

`all(...)` 表示所有事实都必须满足条件，这里要求每条事实都有来源 URL。

```python
self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
```

确认所有事实的置信度都在合法范围内。

---

## 第二个测试：拒绝未知来源

`BrokenFactClient` 故意返回：

```python
{
    "content": "这条事实引用了不存在的来源。",
    "source_url": "https://unknown.example.com",
    "confidence": 0.8,
}
```

但状态中只有：

```python
"https://known.example.com"
```

因此：

```python
source_url not in allowed_urls
```

结果为真，程序抛出：

```python
ValueError("...引用了未知来源")
```

这个测试证明 FactExtractor 不会接受任意伪造 URL。

---

## 第三个测试：没有来源时拒绝运行

```python
FactExtractorAgent(MockLLMClient()).run(
    ResearchState("测试问题")
)
```

新创建的 `ResearchState` 中：

```python
state.sources == []
```

所以应该抛出包含“来源”的错误。

---

# 十五、`test_llm_client.py` 的更新

新增测试：

```python
def test_mock_fact_extractor_returns_source_grounded_facts(self):
```

它直接调用：

```python
client.complete_json(
    "fact_extractor",
    {
        "query": "测试行业",
        "sources": [
            {
                "title": "测试来源",
                "url": "https://example.com/source",
                "content": "测试来源中的明确事实。",
            }
        ],
    },
)
```

然后检查：

```python
self.assertEqual(len(result["facts"]), 1)
```

确认生成了一条事实。

```python
self.assertEqual(
    result["facts"][0]["source_url"],
    "https://example.com/source",
)
```

确认事实引用的 URL 与输入来源一致。

这就是“带来源的事实”，也可以叫“来源支撑的事实”。

---

# 十六、当前完整数据流

现在项目已经有了这条流程：

```text
用户输入 query
       ↓
ResearchState
       ↓
PlannerAgent
       ↓
plan
research_questions
       ↓
ResearcherAgent
       ↓
sources
references
       ↓
FactExtractorAgent
       ↓
facts
```

状态中的几个字段可以这样区分：

```python
state.plan
```

研究计划，回答：

```text
准备从哪些角度研究？
```

```python
state.research_questions
```

具体的研究子问题，回答：

```text
每个角度要搜索什么？
```

```python
state.sources
```

搜索得到的原始候选资料。

```python
state.references
```

给报告使用的简化引用信息。

```python
state.facts
```

从来源中提取出的、带 URL 支撑的事实。

当前还没有新增 Writer，所以 `final_report` 仍然不会被 FactExtractor 修改。
<!-- ORIGINAL_ASSISTANT_12_3_END -->



<a id="qa-13"></a>
### 记录 13：事实提取是真的吗

开始时间（北京时间）：2026-10-06 18:06:17。结束时间：2026-10-06 18:06:53。原始记录 ID：`01a110ad-a3d7-7431-aacf-ccb205660992`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_13_1_START -->
```text
所以它的事实提取过程是真的吗 他是如何一下子就把传入的source变成了事实的？

```
<!-- ORIGINAL_USER_13_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_13_2_START -->
我先重新读取当前版本中 `fact_extractor.py`、`llm_client.py` 和搜索客户端，核对这条链路到底有没有真实模型推理或真实网页内容参与。
<!-- ORIGINAL_ASSISTANT_13_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_13_3_START -->
不是真的。当前项目的“事实提取”只是一个用于测试数据流的模拟过程，没有调用真实大模型，也没有访问真实网页，更没有判断内容是否符合客观事实。

关键证据在 `MockLLMClient` 的说明中：

```python
class MockLLMClient(LLMClient):
    """不联网的确定性客户端。

    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
    """
```

## 它实际上做了什么？

`FactExtractorAgent` 调用：

```python
result = await self.llm.complete_json(
    role="fact_extractor",
    payload={
        "query": state.query,
        "sources": state.sources,
        ...
    },
)
```

测试中传入的是：

```python
FactExtractorAgent(MockLLMClient())
```

所以真正执行的是 `MockLLMClient.complete_json()` 里的这一段：

```python
if role == "fact_extractor":
    facts = []

    for source in payload.get("sources", []):
        content = str(
            source.get("content")
            or source.get("snippet")
            or ""
        ).strip()

        url = str(source.get("url", "")).strip()

        if not content or not url:
            continue

        facts.append(
            {
                "content": content,
                "source_title": str(source.get("title", "")).strip(),
                "source_url": url,
                "source_type": "web",
                "confidence": 0.7,
            }
        )

    return {"facts": facts}
```

它只是遍历每个 `source`，然后：

```text
source.content      → fact.content
source.title        → fact.source_title
source.url          → fact.source_url
固定的 "web"        → fact.source_type
固定的 0.7          → fact.confidence
```

没有真正理解或提炼文本。

## 一个具体例子

假设传入的来源是：

```python
source = {
    "title": "新能源汽车资料",
    "url": "https://example.com/123",
    "content": "新能源汽车需要结合政策和市场环境综合判断。",
}
```

代码会直接生成：

```python
fact = {
    "content": "新能源汽车需要结合政策和市场环境综合判断。",
    "source_title": "新能源汽车资料",
    "source_url": "https://example.com/123",
    "source_type": "web",
    "confidence": 0.7,
}
```

可以看到，`content` 基本是原样复制，并没有从长文章中提炼出一句事实。

如果没有 `content`，它才会改用 `snippet`：

```python
source.get("content") or source.get("snippet") or ""
```

优先顺序是：

```text
content
↓ 如果为空
snippet
↓ 如果也为空
""
```

## 来源本身也不是真的

当前使用的还是：

```python
MockSearchClient
```

它没有联网搜索，而是在本地拼出模拟内容：

```python
content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。"
```

URL 也是程序生成的：

```python
url=f"https://example.com/research/{digest}"
```

所以整个过程实际上是：

```text
程序生成模拟来源
        ↓
把模拟来源的 content 原样复制
        ↓
包装成 fact 字典
        ↓
固定 confidence = 0.7
```

## `FactExtractorAgent` 验证了什么？

它会检查：

- `facts` 是否是列表；
- 每条事实是否是字典；
- 是否有 `content`；
- 是否有 `source_url`；
- URL 是否存在于 `state.sources`；
- `confidence` 是否在 0 到 1 之间；
- 是否存在重复事实。

但它不能检查：

- 内容是否真实；
- 来源是否权威；
- 文字是否真的支持该结论；
- 事实是否过时；
- `confidence=0.7` 是否合理。

特别是这个置信度：

```python
"confidence": 0.7
```

是代码写死的，不是模型计算出来的。

## 真正的事实提取应该怎样工作？

真实版本通常需要：

```text
真实搜索服务
→ 获取真实网页 URL
→ 下载并解析网页正文
→ 将正文和用户问题发送给真实 LLM
→ 要求 LLM 提取原文明确支持的事实
→ 保存原文片段、URL和引用位置
→ 程序验证返回结构和引用
```

目前项目只完成了这套流程的“接口和数据流骨架”。它证明了资料能够从 `sources` 流入 `facts`，但尚未证明这些 `facts` 是真实、准确或经过智能提取的。
<!-- ORIGINAL_ASSISTANT_13_3_END -->



<a id="qa-14"></a>
### 记录 14：Writer 和 Critic 新增

开始时间（北京时间）：2026-10-06 18:10:03。结束时间：2026-10-06 18:10:46。原始记录 ID：`01a110b1-1716-7193-b07a-1ec7a77d3e7d`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_14_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_14_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_14_2_START -->
我先重新读取整个项目的当前版本，并和上一轮已知内容对照；重点找新增或改动的源码、测试及它们之间的数据流。
<!-- ORIGINAL_ASSISTANT_14_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_14_3_START -->
我已经重新读取了项目最新版本。相比上一轮，这次主要新增：

- `WriterAgent`：根据计划和事实生成 Markdown 报告
- `CriticAgent`：审核报告并给出评分
- `MockLLMClient`：新增 Writer 和 Critic 的模拟逻辑
- 对应的 Writer、Critic 测试

现在最小研究链路已经基本接通：

```text
Planner → Researcher → FactExtractor → Writer → Critic
```

## 一、WriterAgent：生成报告

[writer.py](D:\课\s4-6\information_deepresearch\backend\app\agents\writer.py) 定义：

```python
class WriterAgent(BaseAgent):
    name = "writer"
```

它接收一个 `LLMClient`：

```python
def __init__(self, llm: LLMClient):
    self.llm = llm
```

运行前先检查数据：

```python
if not state.plan:
    raise ValueError("没有可用于写作的研究计划")
if not state.facts:
    raise ValueError("没有可用于写作的事实")
```

也就是说 Writer 不能单独运行，必须先有：

```python
state.plan
state.facts
```

然后调用：

```python
report = await self.llm.complete_text(
    role=self.name,
    payload={
        "query": state.query,
        "plan": state.plan,
        "facts": state.facts,
        "references": state.references,
        "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告。",
    },
)
```

由于：

```python
self.name == "writer"
```

实际相当于：

```python
await self.llm.complete_text(role="writer", ...)
```

生成结果后：

```python
report = report.strip()
```

删除报告首尾空白。如果报告为空就报错：

```python
if not report:
    raise ValueError("Writer 没有生成报告内容")
```

最后写入共享状态：

```python
state.final_report = report
state.phase = "writing"
return state
```

## 二、当前 Writer 并没有真正调用大模型

测试传入的是：

```python
WriterAgent(MockLLMClient())
```

因此实际执行的是 `MockLLMClient.complete_text()`。它先建立一个字符串列表：

```python
lines = [
    "## 执行摘要",
    "",
    f"本报告围绕“{query}”整理公开资料...",
    "",
    "## 研究发现",
    "",
]
```

这里的 `##` 是 Markdown 二级标题，空字符串用于产生空行。

接着遍历事实：

```python
for index, fact in enumerate(facts, start=1):
```

将每条事实拼成：

```python
lines.append(
    f"{index}. {content} ([{title}]({url}))"
)
```

最终效果类似：

```markdown
1. 某项事实。([某来源](https://example.com/source))
```

最后：

```python
return "\n".join(lines)
```

`"\n".join(lines)` 会用换行符连接所有字符串，形成完整报告。

需要特别注意：Writer 收到了 `plan` 和 `references`，但当前 Mock 实现实际上没有使用它们。它只是把 `facts` 按固定模板拼接起来，因此不是真正的智能写作。

## 三、CriticAgent：审核报告

[critic.py](D:\课\s4-6\information_deepresearch\backend\app\agents\critic.py) 定义：

```python
class CriticAgent(BaseAgent):
    name = "critic"
```

运行前检查报告：

```python
if not state.final_report.strip():
    raise ValueError("没有可供审核的报告")
```

然后调用：

```python
result = await self.llm.complete_json(
    role=self.name,
    payload={
        "query": state.query,
        "report": state.final_report,
        "facts": state.facts,
        "sources": state.sources,
        "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
    },
)
```

预期得到这样的审核结果：

```python
{
    "verdict": "pass",
    "quality_score": 8.0,
    "summary": "报告中的事实都关联了来源。",
    "needs_more_research": False,
    "issues": [],
}
```

审核结果通过验证后写入：

```python
state.review = review
state.quality_score = review["quality_score"]
state.phase = "reviewing"
```

## 四、Critic 如何验证返回格式？

```python
if not isinstance(value, dict):
```

要求整个审核结果必须是字典。

```python
verdict = str(value.get("verdict", "")).strip()
if verdict not in {"pass", "needs_revision"}:
```

`verdict` 只能是：

```text
pass
needs_revision
```

花括号创建的是集合，适合判断某个值是否属于允许范围。

评分转换为浮点数：

```python
quality_score = float(value.get("quality_score"))
```

然后限制在 0 到 10：

```python
if not 0 <= quality_score <= 10:
```

问题列表必须是字符串列表：

```python
issues = value.get("issues", [])

if not isinstance(issues, list) or not all(
    isinstance(issue, str) for issue in issues
):
```

`all(...)` 表示每一个元素都必须满足条件。

最后只返回标准化后的字段：

```python
{
    "verdict": verdict,
    "quality_score": quality_score,
    "summary": ...,
    "needs_more_research": ...,
    "issues": issues,
}
```

## 五、当前 Critic 是如何“审核”的？

`MockLLMClient` 使用了一条非常简单的规则：

```python
passed = bool(facts and sources and "http" in report)
```

只有同时满足下面三项才通过：

```text
facts 不为空
sources 不为空
报告中包含 "http"
```

通过时返回：

```python
verdict = "pass"
quality_score = 8.0
issues = []
```

不通过时返回：

```python
verdict = "needs_revision"
quality_score = 4.0
issues = ["需要补充带来源的事实"]
```

因此这不是真正的质量审核。它不会判断：

- 事实是否正确；
- URL 是否真的支持对应结论；
- 报告逻辑是否合理；
- 内容是否完整；
- 引用是否权威。

它只是通过简单条件验证流程能否运转。

## 六、测试新增了什么？

`test_writer.py` 验证完整执行到 Writer 后：

```python
state.phase == "writing"
state.final_report 以 "## 执行摘要" 开头
报告包含 "研究发现"
报告包含来源 URL
```

它还检查没有计划或没有事实时，Writer 会拒绝运行。

`test_critic.py` 把整条流程连接起来：

```python
PlannerAgent
→ ResearcherAgent
→ FactExtractorAgent
→ WriterAgent
→ CriticAgent
```

最后检查：

```python
state.phase == "reviewing"
state.review["verdict"] == "pass"
state.quality_score == 8.0
state.review["issues"] == []
```

`BrokenCriticClient` 故意返回错误格式：

```python
{
    "verdict": "unknown",
    "quality_score": 20,
    "issues": "错误格式",
}
```

Critic 首先发现 `verdict` 不合法并抛出错误。

当前项目已经完成“数据流骨架”，但搜索、事实提取、写作和审核仍然都是本地 Mock 模拟逻辑，不代表真实研究结果。
<!-- ORIGINAL_ASSISTANT_14_3_END -->



<a id="qa-15"></a>
### 记录 15：ResearchWorkflow 新增

开始时间（北京时间）：2026-10-06 18:15:16。结束时间：2026-10-06 18:16:22。原始记录 ID：`01a110b5-dbbc-7932-b3a6-2fce7abbb3a1`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_15_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_15_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_15_2_START -->
我先重新读取项目当前全部源码和测试，并排除缓存文件；随后只讲相对上一轮新增或改动的部分，以及它们如何把现有链路继续连接起来。
<!-- ORIGINAL_ASSISTANT_15_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_15_3_START -->
已确认这次新增的是工作流编排层：它不再要求测试或调用方手工依次运行五个 Agent，而是用一个 `ResearchWorkflow` 统一串联。我再精确读取该目录及对应测试，避免遗漏被长输出截断的文件头。
<!-- ORIGINAL_ASSISTANT_15_3_END -->

#### 原文 4：助手最终回答

<!-- ORIGINAL_ASSISTANT_15_4_START -->
我已经重新读取最新内容。这次新增的是“工作流编排层”：

- [research_workflow.py](D:\课\s4-6\information_deepresearch\backend\app\workflow\research_workflow.py)
- [workflow/__init__.py](D:\课\s4-6\information_deepresearch\backend\app\workflow\__init__.py)
- [test_workflow.py](D:\课\s4-6\information_deepresearch\backend\tests\test_workflow.py)

它把之前分散的五个 Agent 串成了一次完整研究任务：

```text
Planner
→ Researcher
→ FactExtractor
→ Writer
→ Critic
→ completed
```

## `ResearchWorkflow` 的职责

以前需要手动写：

```python
await PlannerAgent(llm).run(state)
await ResearcherAgent(search).run(state)
await FactExtractorAgent(llm).run(state)
await WriterAgent(llm).run(state)
await CriticAgent(llm).run(state)
```

现在调用方只需要：

```python
workflow = ResearchWorkflow(llm, search)
state = await workflow.run("研究问题")
```

`ResearchWorkflow` 就是“总调度员”，本身不规划、不搜索、不写报告，只负责按正确顺序调用各 Agent。

## 导入部分

```python
from uuid import uuid4
```

用于生成任务唯一编号。

下面这些导入五个具体 Agent：

```python
from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
```

还导入两个客户端接口：

```python
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
```

以及共享状态：

```python
from app.domain.state import ResearchState
```

## 构造方法

```python
def __init__(
    self,
    llm: LLMClient,
    search: SearchClient,
    results_per_question: int = 3,
):
```

创建工作流时必须提供：

- `llm`：大模型客户端；
- `search`：搜索客户端；
- `results_per_question`：每个研究问题请求多少条搜索结果，默认是 3。

测试中使用：

```python
workflow = ResearchWorkflow(
    MockLLMClient(),
    MockSearchClient(),
)
```

所以当前仍然是本地模拟流程，不是真实大模型和真实搜索。

## 创建各个 Agent

```python
self.planner = PlannerAgent(llm)
self.researcher = ResearcherAgent(search, results_per_question)
self.fact_extractor = FactExtractorAgent(llm)
self.writer = WriterAgent(llm)
self.critic = CriticAgent(llm)
```

同一个 `llm` 对象被交给四个 Agent：

```text
Planner
FactExtractor
Writer
Critic
```

Researcher 不需要 LLM，它需要的是搜索客户端：

```python
ResearcherAgent(search, results_per_question)
```

这表示所有外部依赖都由工作流统一创建和分配。以后换成真实客户端时，Agent 调用顺序不需要改变：

```python
ResearchWorkflow(
    RealLLMClient(...),
    RealSearchClient(...),
)
```

## `run()` 参数

```python
async def run(
    self,
    query: str,
    session_id: str | None = None,
) -> ResearchState:
```

含义分别是：

- `async def`：异步方法；
- `query: str`：用户研究问题；
- `session_id: str | None`：可以是字符串，也可以是 `None`；
- `= None`：调用时可以不传；
- `-> ResearchState`：最终返回完整的研究状态。

例如：

```python
await workflow.run("新能源汽车发展趋势")
```

或者指定任务编号：

```python
await workflow.run(
    "新能源汽车发展趋势",
    session_id="session-001",
)
```

## 创建共享状态

```python
state = ResearchState(
    query=query,
    session_id=session_id or str(uuid4()),
)
```

`or` 在这里表示：

- 如果 `session_id` 有值，就使用它；
- 如果没有值，就生成新的 UUID。

例如：

```python
session_id = "session-001"
```

得到：

```python
state.session_id == "session-001"
```

如果：

```python
session_id = None
```

就会执行：

```python
str(uuid4())
```

生成类似：

```text
7d7aeb82-e660-44a5-a662-29ad7066b46e
```

注意：空字符串 `""` 也会被视为没有值，从而自动生成 UUID。

## 五个 Agent 如何共享数据？

接下来按顺序执行：

```python
await self.planner.run(state)
await self.researcher.run(state)
await self.fact_extractor.run(state)
await self.writer.run(state)
await self.critic.run(state)
```

传给每个 Agent 的都是同一个 `state` 对象。

数据变化过程如下：

```text
初始：
query

Planner 后：
plan、research_questions

Researcher 后：
sources、references

FactExtractor 后：
facts

Writer 后：
final_report

Critic 后：
review、quality_score
```

`await` 会等待当前步骤完成后才执行下一步，因此不会出现 Writer 在 Facts 生成之前运行的情况。

这里注释称它为“同步编排器”，更准确地说是“顺序编排器”：`run()` 本身是异步的，但各 Agent 按顺序依次执行，没有并行运行。

## 最后完成任务

```python
state.phase = "completed"
return state
```

Critic 运行后会先把阶段设置为：

```python
"reviewing"
```

工作流确认所有步骤都执行成功后，再改成：

```python
"completed"
```

如果中途任何 Agent 抛出异常，后续代码不会执行，因此状态不会进入 `completed`。当前工作流也还没有捕获异常并写入 `state.errors`。

## 测试验证了什么？

完整链路测试确认最终状态中：

```python
state.phase == "completed"
state.plan[0]["title"] == "现状与定义"
len(state.sources) == 3
len(state.facts) == 3
state.final_report 不是空字符串
state.review["verdict"] == "pass"
state.quality_score == 8.0
```

另一个测试检查手动传入的任务编号不会被覆盖：

```python
state = asyncio.run(
    workflow.run("测试问题", session_id="session-001")
)

self.assertEqual(state.session_id, "session-001")
```

当前最重要的变化是：项目已经从多个独立组件变成了一条可以一次调用完成的最小链路。不过它仍然没有审核失败后的修订循环，也没有真实联网搜索和真实大模型调用。
<!-- ORIGINAL_ASSISTANT_15_4_END -->



<a id="qa-16"></a>
### 记录 16：reviewing 如何变 completed

开始时间（北京时间）：2026-10-06 18:20:04。结束时间：2026-10-06 18:20:41。原始记录 ID：`01a110ba-427b-7d22-8a79-8b05fb80afa9`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_16_1_START -->
````text
Critic 运行后会先把阶段设置为：
```
"reviewing"
之后呢？ 如何变成completed的？
```

````
<!-- ORIGINAL_USER_16_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_16_2_START -->
我先按你的要求重新读取当前最新的 `critic.py`、工作流文件和对应测试，再沿着代码执行顺序说明 `reviewing` 是怎么变成 `completed` 的。
<!-- ORIGINAL_ASSISTANT_16_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_16_3_START -->
在当前代码里，`"reviewing"` 是审核阶段的临时状态，随后由**工作流**把它改成 `"completed"`。

执行顺序在 [research_workflow.py](D:\课\s4-6\information_deepresearch\backend\app\workflow\research_workflow.py) 的 `run()` 方法中：

```python
await self.critic.run(state)

state.phase = "completed"
return state
```

第一行会等待 Critic 审核完成。Critic 在 [critic.py](D:\课\s4-6\information_deepresearch\backend\app\agents\critic.py) 中做了：

```python
state.phase = "reviewing"
return state
```

它返回后，工作流继续执行下一行：

```python
state.phase = "completed"
```

因为传给 Critic 的是同一个 `state` 对象，所以这行直接把它的阶段从 `"reviewing"` 改成 `"completed"`，然后返回这个状态。

可以把这段流程想成：

```text
Critic：审核完成，把阶段标成 reviewing
工作流：所有步骤都执行完了，把阶段改成 completed
```

有个重要细节：**当前工作流没有根据审核结论分支处理。**即使 `state.review["verdict"]` 是 `"needs_revision"`，只要 Critic 没报错、正常返回，工作流仍会把阶段设为 `"completed"`。因此这里的 `completed` 目前只表示“这次工作流跑完了”，不代表“审核通过了”。

测试中也分别检查了两件事：

```python
self.assertEqual(state.phase, "completed")
self.assertEqual(state.review["verdict"], "pass")
```

审核修订循环目前还没有实现。
<!-- ORIGINAL_ASSISTANT_16_3_END -->



<a id="qa-17"></a>
### 记录 17：命令行研究入口

开始时间（北京时间）：2026-10-06 18:26:59。结束时间：2026-10-06 18:30:23。原始记录 ID：`01a110c0-9712-7a71-810f-3acc83b4e4b7`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_17_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_17_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_17_2_START -->
我先重新扫描并读取项目当前版本，重点确认自上次工作流说明后新增或修改了哪些文件；缓存文件会排除。读完后我会按“新增内容 → 代码作用 → 流程变化 → 测试验证”详细讲解。
<!-- ORIGINAL_ASSISTANT_17_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_17_3_START -->
我已经重新阅读了当前项目。相比上一轮，最新更新主要是增加了命令行运行入口：

- [run_research.py](D:\课\s4-6\information_deepresearch\backend\app\scripts\run_research.py)
- [scripts/__init__.py](D:\课\s4-6\information_deepresearch\backend\app\scripts\__init__.py)
- [test_run_research.py](D:\课\s4-6\information_deepresearch\backend\tests\test_run_research.py)
- [README.md](D:\课\s4-6\information_deepresearch\README.md) 增加了运行命令

现在项目除了能被测试调用，也可以在命令行中直接运行。

## 一、`scripts/__init__.py`

内容：

```python
"""Executable learning scripts."""
```

它的作用是把 `scripts` 目录标记为 Python 包。

目录结构：

```text
app/
└── scripts/
    ├── __init__.py
    └── run_research.py
```

这样 Python 才可以用模块形式运行：

```powershell
python -m app.scripts.run_research
```

这里的 `-m` 意思是：

> 按 Python 模块路径运行，而不是直接按文件路径运行。

---

## 二、`run_research.py` 的作用

这个文件是命令行入口，负责：

```text
接收用户问题
    ↓
创建 Mock LLM 和 Mock 搜索客户端
    ↓
创建 ResearchWorkflow
    ↓
运行完整研究流程
    ↓
把结果打印到终端
```

注意：它使用的仍然是：

```python
MockLLMClient()
MockSearchClient()
```

所以这是一个本地演示程序，不是真实联网研究程序。

---

# 三、导入部分

```python
import argparse
import asyncio
```

`argparse` 用来解析命令行参数。

`asyncio` 用来运行异步函数。

然后导入：

```python
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.workflow.research_workflow import ResearchWorkflow
```

它们分别负责：

- 模拟大模型；
- 模拟搜索；
- 研究状态类型；
- 完整研究工作流。

---

# 四、`build_parser()`

```python
def build_parser() -> argparse.ArgumentParser:
```

这个函数创建命令行参数解析器。

```python
parser = argparse.ArgumentParser(
    description="运行一次 Iteration 01 DeepResearch"
)
```

`ArgumentParser` 会帮助程序读取命令行参数，并且自动支持：

```powershell
python -m app.scripts.run_research --help
```

## 添加 `query` 参数

```python
parser.add_argument(
    "query",
    nargs="?",
    help="研究问题；不传时会进入交互式输入",
)
```

这里的 `"query"` 是位置参数。

例如：

```powershell
python -m app.scripts.run_research "新能源汽车行业的发展趋势是什么？"
```

字符串会被放到：

```python
args.query
```

### `nargs="?"`

问号表示这个参数是可选的。

因此下面两种写法都可以：

```powershell
python -m app.scripts.run_research "测试问题"
```

或者：

```powershell
python -m app.scripts.run_research
```

如果不传，`args.query` 会是：

```python
None
```

最后：

```python
return parser
```

返回解析器对象。

---

# 五、`print_state(state)`

```python
def print_state(state: ResearchState) -> None:
```

这个函数负责把完整的研究状态打印到终端。

`-> None` 表示它不返回结果，只负责输出。

## 1. 打印研究计划

```python
print("\n" + "=" * 60)
print("研究计划")
print("=" * 60)
```

这里：

```python
"=" * 60
```

表示把字符串 `"="` 重复 60 次，用于制作分隔线。

然后：

```python
for index, item in enumerate(state.plan, start=1):
    print(f"{index}. {item['title']}：{item['description']}")
```

遍历研究计划。

例如：

```python
state.plan = [
    {
        "title": "现状与定义",
        "description": "明确研究范围",
    }
]
```

输出大致是：

```text
1. 现状与定义：明确研究范围
```

`item['title']` 使用字典键取得标题。

---

## 2. 打印搜索来源

```python
print(f"搜索来源（{len(state.sources)} 条）")
```

`len(state.sources)` 统计来源数量。

然后：

```python
for index, source in enumerate(state.sources, start=1):
    print(f"{index}. {source['title']}")
    print(f"   URL: {source['url']}")
```

打印每个来源的标题和 URL。

例如：

```text
1. 公开资料：某个研究问题
   URL: https://example.com/research/abc
```

---

## 3. 打印结构化事实

```python
print(f"结构化事实（{len(state.facts)} 条）")
```

然后：

```python
for index, fact in enumerate(state.facts, start=1):
    print(f"{index}. {fact['content']}")
    print(f"   来源: {fact['source_url']}")
```

每条事实都会同时显示：

- 事实内容；
- 支撑它的来源 URL。

这体现了项目想实现的“带来源事实”。

---

## 4. 打印最终报告

```python
print("最终报告")
print(state.final_report)
```

`state.final_report` 是 Writer 生成的 Markdown 文本。

当前 Mock Writer 会生成类似：

```markdown
## 执行摘要

本报告围绕某个问题整理公开资料。

## 研究发现

1. 某条事实。([来源](https://example.com/...))

## 结论

以上结论需要继续验证。
```

---

## 5. 打印审核结果

```python
print(f"结论: {state.review['verdict']}")
print(f"评分: {state.quality_score}/10")
print(f"摘要: {state.review['summary']}")
print(f"任务阶段: {state.phase}")
print(f"会话 ID: {state.session_id}")
```

最后会显示：

- 审核结论，例如 `pass`；
- 质量分数，例如 `8.0/10`；
- 审核摘要；
- 当前阶段；
- 本次任务的会话 ID。

正常完成时：

```text
任务阶段: completed
```

---

# 六、`run(query)`

```python
async def run(query: str) -> ResearchState:
```

这是一个异步辅助函数，用来运行完整工作流。

```python
workflow = ResearchWorkflow(
    MockLLMClient(),
    MockSearchClient(),
)
```

这里创建：

```text
MockLLMClient
MockSearchClient
ResearchWorkflow
```

然后：

```python
return await workflow.run(query)
```

调用工作流，最终返回 `ResearchState`。

它相当于把之前需要手动写的流程集中起来：

```text
Planner
→ Researcher
→ FactExtractor
→ Writer
→ Critic
→ completed
```

---

# 七、`main()`

```python
def main() -> None:
```

这是同步的命令行入口。

## 1. 解析命令行参数

```python
args = build_parser().parse_args()
```

例如运行：

```powershell
python -m app.scripts.run_research "测试行业"
```

得到：

```python
args.query == "测试行业"
```

## 2. 支持交互输入

```python
query = (args.query or input("请输入研究问题：")).strip()
```

这句话可以拆成：

```python
args.query or input(...)
```

如果命令行传了问题，就使用命令行问题。

如果没有传，就显示：

```text
请输入研究问题：
```

让用户手动输入。

最后 `.strip()` 去掉前后空格。

## 3. 检查空问题

```python
if not query:
    raise SystemExit("研究问题不能为空")
```

如果用户什么都没输入，程序直接退出并显示错误信息。

这里的 `SystemExit` 是让命令行程序正常结束，不是普通业务异常。

## 4. 运行异步流程

```python
state = asyncio.run(run(query))
```

`run(query)` 是异步函数，不能直接普通调用。

```python
asyncio.run(...)
```

负责创建事件循环、执行异步任务、等待完成，然后返回结果。

## 5. 打印结果

```python
print_state(state)
```

把最终研究状态完整展示出来。

---

# 八、最后两行是什么意思？

```python
if __name__ == "__main__":
    main()
```

这是 Python 脚本的常见入口判断。

当文件被直接作为程序运行时：

```python
python -m app.scripts.run_research
```

此时：

```python
__name__ == "__main__"
```

所以会调用：

```python
main()
```

但是如果其他代码导入它：

```python
from app.scripts.run_research import run
```

此时不会自动执行 `main()`，只会导入里面的函数。

这样可以同时支持：

```text
命令行运行
代码导入和测试
```

---

# 九、README 中新增的运行方式

项目根目录下执行：

```powershell
$env:PYTHONPATH = "backend"
python -m app.scripts.run_research "中国新能源汽车行业的发展趋势是什么？"
```

## 为什么要设置 `PYTHONPATH`？

源代码在：

```text
backend/app/
```

但当前终端的工作目录是项目根目录：

```text
information_deepresearch/
```

设置：

```powershell
$env:PYTHONPATH = "backend"
```

后，Python 才能找到：

```python
import app
```

否则可能报：

```text
ModuleNotFoundError: No module named 'app'
```

## 为什么使用模块路径？

运行：

```powershell
python -m app.scripts.run_research
```

对应目录：

```text
backend/
└── app/
    └── scripts/
        └── run_research.py
```

Python 按包结构加载文件，因此项目中的导入：

```python
from app.core.llm_client import MockLLMClient
```

可以正常工作。

---

# 十、新增测试

[test_run_research.py](D:\课\s4-6\information_deepresearch\backend\tests\test_run_research.py) 有两个测试。

## 1. 测试脚本是否返回完整状态

```python
state = asyncio.run(run("测试行业的现状是什么？"))
```

调用脚本中的 `run()` 函数。

然后检查：

```python
self.assertEqual(state.phase, "completed")
self.assertTrue(state.final_report)
```

说明：

- 完整工作流执行成功；
- 最终报告不是空的。

## 2. 测试打印内容是否完整

```python
output = StringIO()
```

`StringIO` 是内存中的文本缓冲区。

```python
with redirect_stdout(output):
    print_state(state)
```

`redirect_stdout` 会暂时把 `print()` 输出重定向到 `output`，而不是直接打印到终端。

然后：

```python
text = output.getvalue()
```

取出打印出来的全部文字。

测试确认输出包含：

```python
"研究计划"
"搜索来源"
"结构化事实"
"最终报告"
"审核结果"
```

这说明命令行输出包含完整的五个重要部分。

---

# 十一、当前可以怎样运行？

在项目根目录：

```powershell
$env:PYTHONPATH = "backend"
python -m app.scripts.run_research "测试行业的现状是什么？"
```

不传参数时：

```powershell
$env:PYTHONPATH = "backend"
python -m app.scripts.run_research
```

程序会提示：

```text
请输入研究问题：
```

---

# 十二、这次更新后的完整关系

```text
run_research.py
       ↓
ResearchWorkflow
       ↓
PlannerAgent
       ↓
ResearcherAgent
       ↓
FactExtractorAgent
       ↓
WriterAgent
       ↓
CriticAgent
       ↓
state.phase = "completed"
       ↓
print_state()
```

这次更新的意义是：

> 项目现在不仅能通过单元测试验证内部逻辑，还提供了一个人可以直接运行和观察结果的命令行入口。

不过仍需注意：命令行运行的搜索、事实提取、写作和审核全部使用 Mock 实现，所以它目前是“可运行的学习演示链路”，还不是连接真实搜索引擎和真实大模型的产品。  

我还验证了当前测试集：共 33 个测试，全部通过。
<!-- ORIGINAL_ASSISTANT_17_3_END -->



<a id="qa-18"></a>
### 记录 18：审核失败后的路由与循环

开始时间（北京时间）：2026-10-06 18:34:26。结束时间：2026-10-06 18:41:36。原始记录 ID：`01a110c7-68a6-7860-ac15-15c456546987`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_18_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_18_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_18_2_START -->
我先重新读取项目当前版本，确认这次新增或修改了哪些内容；我会把自动生成的缓存排除，只基于最新源码和测试讲解。
<!-- ORIGINAL_ASSISTANT_18_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_18_3_START -->
我已经重新读取了项目当前版本。相对上一次，最新更新的核心不是新增一个 Agent，而是加入了：

> Critic 审核失败后，可以决定“补充搜索”或“只修改报告”，并且限制最多循环多少次。

相关修改主要在：

- [state.py](D:\课\s4-6\information_deepresearch\backend\app\domain\state.py)
- [critic.py](D:\课\s4-6\information_deepresearch\backend\app\agents\critic.py)
- [researcher.py](D:\课\s4-6\information_deepresearch\backend\app\agents\researcher.py)
- [writer.py](D:\课\s4-6\information_deepresearch\backend\app\agents\writer.py)
- [llm_client.py](D:\课\s4-6\information_deepresearch\backend\app\core\llm_client.py)
- [research_workflow.py](D:\课\s4-6\information_deepresearch\backend\app\workflow\research_workflow.py)
- [test_workflow.py](D:\课\s4-6\information_deepresearch\backend\tests\test_workflow.py)

现在流程变成：

```text
Planner
    ↓
Researcher
    ↓
FactExtractor
    ↓
Writer
    ↓
Critic
    ↓
审核通过？────是────→ completed
    │
    否
    ↓
需要补充搜索？
    ├── 是 → Researcher → FactExtractor → Writer → Critic
    └── 否 → Writer → Critic
```

---

# 一、`ResearchState` 新增了什么？

新增字段：

```python
pending_search_queries: list[str] = field(default_factory=list)
```

它表示：

> Critic 要求补充搜索时，暂时存放的新搜索问题。

之前已经有：

```python
research_questions
```

它表示 Planner 最初规划出的研究问题。

现在有两个不同的字段：

```python
research_questions
```

最初的研究问题，比较稳定。

```python
pending_search_queries
```

审核后临时产生的补充搜索问题。

例如最开始 Planner 产生：

```python
state.research_questions = [
    "行业当前状态是什么？",
    "行业面临哪些问题？",
    "未来趋势是什么？",
]
```

Critic 审核后认为缺少最新数据，于是可能产生：

```python
state.pending_search_queries = [
    "2025年新能源汽车行业数据"
]
```

这个列表只用于下一轮补充搜索。

使用：

```python
field(default_factory=list)
```

是为了保证每个 `ResearchState` 都拥有独立的列表，不会互相共享。

---

# 二、Critic 现在不只是评分了

之前 Critic 主要返回：

```python
{
    "verdict": "pass",
    "quality_score": 8.0,
    "summary": "...",
    "needs_more_research": False,
    "issues": [],
}
```

现在新增了：

```python
"search_queries": []
```

一个失败审核结果可能是：

```python
{
    "verdict": "needs_revision",
    "quality_score": 4.0,
    "summary": "报告缺少最新行业数据。",
    "needs_more_research": True,
    "issues": ["补充最新行业数据"],
    "search_queries": ["2025年新能源汽车行业数据"],
}
```

这就相当于 Critic 给工作流发了一张“下一步行动指令”：

```text
审核结论：需要修改
是否补充搜索：是
应该搜索什么：2025年新能源汽车行业数据
存在的问题：缺少最新行业数据
```

---

# 三、Critic 的 `run()` 变化

现在传给 LLM 的数据多了一项：

```python
"iteration": state.iteration,
```

完整的 payload 大致是：

```python
{
    "query": state.query,
    "report": state.final_report,
    "facts": state.facts,
    "sources": state.sources,
    "iteration": state.iteration,
    "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
}
```

`iteration` 的意思是：

> 当前是第几轮修订。

初始值是：

```python
0
```

第一次报告生成后进行的初始审核，也是在 `iteration == 0` 时进行。

如果审核失败并进入修订：

```python
state.iteration += 1
```

那么下一轮就是：

```python
iteration == 1
```

---

# 四、Critic 新增的格式验证

## 1. 验证 `needs_more_research`

```python
needs_more_research = value.get("needs_more_research", False)

if not isinstance(needs_more_research, bool):
    raise ValueError(
        "Critic needs_more_research 必须是布尔值"
    )
```

它要求这个字段必须是真正的布尔值：

```python
True
False
```

不能是字符串：

```python
"true"
"false"
```

因为在 Python 中：

```python
bool("false")
```

结果其实是：

```python
True
```

所以这里严格检查类型，避免模型返回字符串后被错误理解。

## 2. 验证 `search_queries`

```python
search_queries = value.get("search_queries", [])
```

然后检查：

```python
if not isinstance(search_queries, list) or not all(
    isinstance(query, str) and query.strip()
    for query in search_queries
):
    raise ValueError(
        "Critic search_queries 必须是非空字符串列表"
    )
```

每个搜索问题必须是非空字符串：

```python
[
    "2025年新能源汽车行业数据",
    "新能源汽车销量官方统计",
]
```

不能是：

```python
[123]
```

也不能是：

```python
[""]
```

当前代码中空列表 `[]` 实际上可以通过检查，因为：

```python
all(... for query in [])
```

会返回 `True`。

所以错误信息说“非空字符串列表”，但代码实际上允许空列表。空列表在审核通过时是合理的，因为不需要补充搜索。

---

# 五、Critic 返回的数据被标准化

最后返回：

```python
return {
    "verdict": verdict,
    "quality_score": quality_score,
    "summary": str(value.get("summary", "")).strip(),
    "needs_more_research": needs_more_research,
    "issues": issues,
    "search_queries": [query.strip() for query in search_queries],
}
```

这里把搜索问题统一清理空格：

```python
[query.strip() for query in search_queries]
```

所以：

```python
["  补充官方数据  "]
```

会变成：

```python
["补充官方数据"]
```

---

# 六、Researcher 现在支持“补充搜索”

以前 Researcher 总是搜索：

```python
state.research_questions
```

现在改成：

```python
if state.pending_search_queries:
    questions = [
        query.strip()
        for query in state.pending_search_queries
    ]
else:
    questions = [
        question.strip()
        for question in state.research_questions
    ]
```

意思是：

```text
如果有审核产生的补充问题，就只搜索补充问题；
否则，搜索最初规划的问题。
```

这是非常关键的优先级设计。

## 第一次运行

此时：

```python
state.pending_search_queries == []
```

所以 Researcher 搜索：

```python
state.research_questions
```

例如 3 个初始问题。

## 审核失败后

如果 Critic 设置：

```python
state.pending_search_queries = [
    "2025年新能源汽车行业数据"
]
```

下一次 Researcher 运行时，就只搜索：

```python
"2025年新能源汽车行业数据"
```

不会再次搜索之前的 3 个问题。

这样可以避免重复搜索。

---

## 搜索完成后清空临时列表

```python
state.pending_search_queries = []
```

这表示：

> 这些补充搜索问题已经被执行过了，不要下一轮重复使用。

注意，搜索结果不会被覆盖：

```python
collected_sources = list(state.sources)
```

它会先保留旧来源，再加入新来源：

```text
旧来源 3 条
+
新搜索来源 1 条
=
总来源 4 条
```

然后继续去重。

---

# 七、Writer 现在可以接收审核意见

以前 Writer 的 payload 是：

```python
{
    "query": state.query,
    "plan": state.plan,
    "facts": state.facts,
    "references": state.references,
}
```

现在新增：

```python
"review": state.review,
"iteration": state.iteration,
```

完整结构大致是：

```python
{
    "query": state.query,
    "plan": state.plan,
    "facts": state.facts,
    "references": state.references,
    "review": state.review,
    "iteration": state.iteration,
    "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
}
```

这样 Writer 就知道：

- 当前是第几轮；
- 上一轮审核提出了什么问题；
- 是否需要根据审核意见重写报告。

---

# 八、Mock Writer 如何模拟“修订”？

当前仍然不是实际大模型，只是 Mock。

它读取：

```python
review = payload.get("review", {})
issues = review.get("issues", []) if isinstance(review, dict) else []
```

如果有审核问题：

```python
if issues:
    lines.extend(
        [
            "",
            "## 根据审核意见修订",
            "",
        ]
    )
    lines.extend(
        f"- 已处理：{issue}"
        for issue in issues
    )
```

例如审核问题是：

```python
["补充结论与证据之间的说明"]
```

Mock Writer 会在报告中追加：

```markdown
## 根据审核意见修订

- 已处理：补充结论与证据之间的说明
```

这只是演示数据流，并不代表它真的完成了内容修改。

实际真实 LLM 应该根据问题重新组织正文，而不是简单打印“已处理”。

---

# 九、`ResearchWorkflow` 新增 `max_iterations`

构造方法现在是：

```python
def __init__(
    self,
    llm: LLMClient,
    search: SearchClient,
    results_per_question: int = 3,
    max_iterations: int = 1,
):
```

新增：

```python
max_iterations: int = 1
```

意思是：

> 最多允许进行多少轮修订。

## 检查不能是负数

```python
if max_iterations < 0:
    raise ValueError("max_iterations 不能小于 0")
```

例如：

```python
ResearchWorkflow(
    llm,
    search,
    max_iterations=-1,
)
```

会直接报错。

可以设置：

```python
max_iterations=0
```

这表示：

> 允许首次审核，但不允许审核失败后再次修订。

---

# 十、把限制写入状态

创建状态时：

```python
state = ResearchState(
    query=query,
    session_id=session_id or str(uuid4()),
    max_iterations=self.max_iterations,
)
```

所以工作流配置和状态中的配置保持一致：

```python
workflow.max_iterations
state.max_iterations
```

都表示允许的最大修订轮数。

---

# 十一、工作流现在使用 `while True`

之前是固定顺序：

```python
await self.critic.run(state)
state.phase = "completed"
```

现在变成：

```python
while True:
    await self.critic.run(state)

    if state.review["verdict"] == "pass":
        break

    if state.iteration >= state.max_iterations:
        break

    state.iteration += 1

    ...
    await self.writer.run(state)
```

`while True` 的意思是：

> 先不断循环，直到代码主动执行 `break`。

这里有两个退出条件。

---

## 第一个退出条件：审核通过

```python
if state.review["verdict"] == "pass":
    break
```

如果 Critic 返回：

```python
"verdict": "pass"
```

立即退出循环。

然后执行：

```python
state.phase = "completed"
return state
```

---

## 第二个退出条件：达到修订上限

```python
if state.iteration >= state.max_iterations:
    break
```

假设：

```python
state.iteration = 1
state.max_iterations = 1
```

说明已经完成了一轮修订，不能再继续。

即使这次审核仍然是：

```python
"needs_revision"
```

也会退出循环。

然后工作流仍然会：

```python
state.phase = "completed"
```

所以要注意：

> `completed` 表示工作流停止运行，不一定表示审核通过。

最终是否通过，要看：

```python
state.review["verdict"]
```

---

# 十二、完整解释三种情况

## 情况一：第一次就通过

默认的 `MockLLMClient` 在有事实、有来源、报告中有 URL 时会返回：

```python
{
    "verdict": "pass",
    "quality_score": 8.0,
    "needs_more_research": False,
    "issues": [],
    "search_queries": [],
}
```

执行过程：

```text
iteration = 0
Critic 审核
verdict = pass
退出 while
phase = completed
```

最终：

```python
state.iteration == 0
state.phase == "completed"
state.review["verdict"] == "pass"
```

---

## 情况二：审核失败，需要补充搜索

第一次审核返回：

```python
{
    "verdict": "needs_revision",
    "needs_more_research": True,
    "issues": ["补充最新行业数据"],
    "search_queries": ["2025年新能源汽车行业数据"],
}
```

当前状态：

```text
iteration = 0
max_iterations = 1
```

执行：

```python
if state.iteration >= state.max_iterations:
```

也就是：

```python
0 >= 1
```

结果是 `False`，所以可以修订。

然后：

```python
state.iteration += 1
```

变成：

```python
iteration = 1
```

设置补充查询：

```python
state.pending_search_queries = [
    "2025年新能源汽车行业数据"
]
```

然后执行：

```python
await self.researcher.run(state)
```

Researcher 只搜索这个新问题。

接着：

```python
await self.fact_extractor.run(state)
```

从全部来源中重新整理事实。

然后：

```python
await self.writer.run(state)
```

Writer 将新事实和审核意见一起用于生成新报告。

最后再次 Critic：

```text
第二次审核通过
→ break
→ phase = completed
```

这种情况下：

```python
state.iteration == 1
```

表示发生过一轮修订。

测试中还记录了搜索次数：

```python
3 个初始问题 + 1 个补充查询 = 4 次搜索
```

最终来源数量也从 3 变为 4。

---

## 情况三：审核失败，但不需要新搜索

第一次审核返回：

```python
{
    "verdict": "needs_revision",
    "needs_more_research": False,
    "issues": ["补充结论与证据之间的说明"],
    "search_queries": [],
}
```

工作流会：

```python
state.iteration += 1
```

但不会执行：

```python
ResearcherAgent
FactExtractorAgent
```

只会重新执行：

```python
await self.writer.run(state)
```

Writer 读取：

```python
state.review["issues"]
```

根据问题重写报告。

所以：

```text
搜索次数仍然是 3
Writer 执行两次
```

这适合处理：

- 结构不清晰；
- 结论解释不够；
- Markdown 格式不合适；
- 需要补充说明但不需要新资料。

---

## 情况四：达到最大修订次数仍未通过

假设：

```python
max_iterations = 1
```

第一次审核失败：

```text
iteration = 0
```

允许一次修订：

```text
iteration = 1
```

第二次审核仍然返回：

```python
"needs_revision"
```

此时：

```python
state.iteration >= state.max_iterations
```

就是：

```python
1 >= 1
```

于是退出循环。

最终状态可能是：

```python
state.phase == "completed"
state.review["verdict"] == "needs_revision"
state.iteration == 1
```

这再次说明：

```text
completed = 工作流结束
pass = 审核通过
```

两者不是同一个概念。

---

# 十三、为什么测试里要写 `SequencedReviewLLM`？

在 [test_workflow.py](D:\课\s4-6\information_deepresearch\backend\tests\test_workflow.py) 中：

```python
class SequencedReviewLLM(MockLLMClient):
```

这是一个测试专用的 LLM 客户端。

它保存一组预先安排好的审核结果：

```python
self.reviews = iter(reviews)
```

每次 Critic 调用时：

```python
if role == "critic":
    return next(self.reviews)
```

第一次返回第一个审核结果，第二次返回第二个审核结果。

例如：

```python
[
    review("needs_revision", ...),
    review("pass", score=8.0),
]
```

就能模拟：

```text
第一轮：不通过
第二轮：通过
```

因为真正的 `MockLLMClient` 默认第一次就通过，所以必须用这个测试类才能测试修订循环。

---

# 十四、为什么要有 `RecordingSearchClient`？

```python
class RecordingSearchClient(MockSearchClient):
```

它继承模拟搜索客户端，但多记录一个列表：

```python
self.queries = []
```

每次搜索时：

```python
self.queries.append(query)
```

然后继续调用父类真正的模拟搜索：

```python
return await super().search(query, limit)
```

这样测试可以检查：

```python
len(search.queries)
```

以及：

```python
search.queries[-1]
```

从而确认：

- 是否真的进行了补充搜索；
- 补充搜索使用的到底是什么查询；
- 没有补充搜索时，搜索次数是否保持不变。

---

# 十五、当前测试覆盖了什么？

最新测试一共有 37 个，全部通过。

新增或扩展的工作流测试包括：

## 补充研究后通过

验证：

```python
state.phase == "completed"
state.review["verdict"] == "pass"
state.iteration == 1
搜索次数 == 4
来源数量 == 4
事实数量 == 4
```

## 只修改报告后通过

验证：

```python
搜索次数 == 3
Writer 调用次数 == 2
第二次 Writer 收到了审核问题
最终报告包含审核意见
```

## 达到最大循环次数

验证：

```python
state.iteration == 1
state.review["verdict"] == "needs_revision"
state.phase == "completed"
```

## 拒绝负数循环上限

验证：

```python
max_iterations=-1
```

会抛出 `ValueError`。

---

# 十六、这次更新的本质

之前的流程是：

```text
Critic 审核
→ 不管通过还是失败
→ 直接 completed
```

现在变成：

```text
Critic 审核
→ 通过：结束
→ 失败且未达到上限：修订
→ 失败且需要资料：补充搜索、提取事实、写作
→ 失败但不需要资料：直接重写
→ 达到上限：停止
```

不过再次强调，目前仍然使用 `MockLLMClient`：

- Critic 的判断是固定规则；
- Writer 的“修订”只是根据 issues 增加一段文字；
- SearchClient 不联网；
- FactExtractor 也不是真正的大模型事实提取。

这次更新主要验证的是：

> 审核结果如何在 Agent 之间传递，以及工作流如何根据审核结果选择下一步。
<!-- ORIGINAL_ASSISTANT_18_3_END -->



<a id="qa-19"></a>
### 记录 19：内部事件流新增

开始时间（北京时间）：2026-10-06 18:56:36。结束时间：2026-10-06 19:01:04。原始记录 ID：`01a110db-b60a-7930-beba-8a34c0c4722e`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_19_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_19_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_19_2_START -->
我先重新读取项目当前版本，确认这次相对上一轮又新增或修改了什么；会排除 `__pycache__`，只依据最新源码和测试解释。
<!-- ORIGINAL_ASSISTANT_19_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_19_3_START -->
我已经重新读取了项目最新版本。相比上一轮，这次新增的是“工作流进度事件”功能：

- 新增 [events.py](D:\课\s4-6\information_deepresearch\backend\app\domain\events.py)
- 大幅更新 [research_workflow.py](D:\课\s4-6\information_deepresearch\backend\app\workflow\research_workflow.py)
- 新增 [test_stream_workflow.py](D:\课\s4-6\information_deepresearch\backend\tests\test_stream_workflow.py)
- [README.md](D:\课\s4-6\information_deepresearch\README.md) 增加了事件流说明

以前只能等整个流程结束：

```python
state = await workflow.run(query)
```

现在还可以边运行边收到进度：

```python
async for event in workflow.stream(query):
    print(event)
```

---

# 一、新增 `ResearchEvent`

文件：

```text
backend/app/domain/events.py
```

## 1. 文件用途

```python
"""研究工作流对外发布的事件格式。
...
这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
字典格式。
"""
```

它的作用是规定：

> 工作流每完成一个重要步骤，应该向外部发送什么格式的消息。

例如：

```python
{
    "type": "plan_ready",
    "session_id": "abc-123",
    "phase": "planning",
    "iteration": 0,
    "plan": [...],
    "research_questions": [...],
}
```

当前只是普通 Python 字典，还没有接 FastAPI、SSE 或 WebSocket。

---

## 2. `ResearchEvent` 数据类

```python
@dataclass(frozen=True)
class ResearchEvent:
```

这是一个数据类。

`frozen=True` 表示事件创建后不能重新给字段赋值：

```python
event.type = "other"
```

理论上会报错。

为什么事件需要尽量不可变？

因为事件代表某个时间点发生的事情。例如：

```text
第 1 个事件：规划已经完成
第 2 个事件：搜索已经完成
```

事件发出后，不希望后续代码再修改它的内容。

---

## 3. 事件字段

```python
type: str
session_id: str
phase: str
iteration: int = 0
data: dict[str, Any] = field(default_factory=dict)
```

### `type`

事件类型，例如：

```text
research_started
phase_started
plan_ready
research_evidence_ready
draft_ready
review_completed
research_completed
```

### `session_id`

当前研究任务的会话 ID。

同一次研究流程产生的所有事件，都有相同的 `session_id`，这样前端可以知道这些事件属于同一个任务。

### `phase`

当前阶段，例如：

```text
planning
researching
writing
reviewing
completed
```

### `iteration`

当前是第几轮修订。

第一次运行通常是：

```python
iteration = 0
```

如果 Critic 要求修订，下一轮会变成：

```python
iteration = 1
```

### `data`

事件附带的额外信息。

例如 `plan_ready` 事件需要携带：

```python
{
    "plan": [...],
    "research_questions": [...],
}
```

而 `draft_ready` 事件需要携带：

```python
{
    "report": "...",
    "revision": False,
}
```

不同事件需要的数据不同，所以统一放在 `data` 字典里。

---

# 二、`to_dict()` 方法

```python
def to_dict(self) -> dict[str, Any]:
```

它把 `ResearchEvent` 对象转换成普通字典。

先建立固定字段：

```python
event = {
    "type": self.type,
    "session_id": self.session_id,
    "phase": self.phase,
    "iteration": self.iteration,
}
```

然后把 `data` 中的字段展开到最外层：

```python
event.update(deepcopy(self.data))
```

假设创建事件时：

```python
ResearchEvent(
    type="plan_ready",
    session_id="abc",
    phase="planning",
    iteration=0,
    data={
        "plan": [...],
        "research_questions": [...],
    },
)
```

转换后不是：

```python
{
    "type": "...",
    "data": {
        "plan": [...],
        "research_questions": [...]
    }
}
```

而是：

```python
{
    "type": "plan_ready",
    "session_id": "abc",
    "phase": "planning",
    "iteration": 0,
    "plan": [...],
    "research_questions": [...],
}
```

这样调用方可以直接写：

```python
event["plan"]
event["report"]
event["references"]
```

不需要再写：

```python
event["data"]["plan"]
```

---

## 为什么使用 `deepcopy()`？

工作流中的数据通常来自共享状态：

```python
state.plan
state.sources
state.facts
```

如果事件直接保存这些列表，后续状态变化可能影响事件中的内容。

`deepcopy()` 会复制一份独立的数据快照。

例如：

```python
event = ResearchEvent(
    ...,
    data={"facts": state.facts},
).to_dict()
```

即使后面 `state.facts` 增加了新事实，之前已经生成的事件仍然保存当时的内容。

可以理解为：

```text
事件 = 某个时间点的截图
```

---

# 三、`ResearchWorkflow.run()` 的变化

以前 `run()` 里面直接写全部 Agent：

```python
await self.planner.run(state)
await self.researcher.run(state)
...
```

现在改成：

```python
state = self._new_state(query, session_id)

async for _ in self._stream_state(state):
    pass

return state
```

这里的 `pass` 表示：

> 事件产生了，但 `run()` 不关心中间事件，只等待整个流程完成。

这样 `run()` 仍然返回最终状态：

```python
state = await workflow.run(query)
```

但是实际业务逻辑已经统一放到：

```python
_stream_state()
```

中。

这是很重要的设计：

```text
run() 和 stream()
都使用同一套工作流逻辑
```

避免写两份代码。

如果分别为 `run()` 和 `stream()` 写两套流程，很容易一个修复了，另一个忘记修复。

---

# 四、新增 `stream()` 方法

```python
async def stream(
    self,
    query: str,
    session_id: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
```

它是异步生成器。

和普通函数返回一个值不同，它可以多次产生值：

```python
yield event
```

调用方式是：

```python
async for event in workflow.stream("研究问题"):
    print(event)
```

不能这样写：

```python
event = await workflow.stream("研究问题")
```

因为 `stream()` 返回的是“可以异步遍历的事件流”，不是单个结果。

也可以一次收集所有事件：

```python
events = [
    event
    async for event in workflow.stream("研究问题")
]
```

---

# 五、`_new_state()`

```python
def _new_state(
    self,
    query: str,
    session_id: str | None,
) -> ResearchState:
```

这个方法负责创建初始状态。

```python
return ResearchState(
    query=query,
    session_id=session_id or str(uuid4()),
    max_iterations=self.max_iterations,
)
```

它被 `run()` 和 `stream()` 共用。

这样两种调用方式创建的状态规则完全一致：

```text
run() 使用同一个初始状态逻辑
stream() 使用同一个初始状态逻辑
```

---

# 六、`_stream_state()` 是新的核心

```python
async def _stream_state(
    self,
    state: ResearchState,
) -> AsyncIterator[dict[str, Any]]:
```

这个方法一边执行 Agent，一边 `yield` 事件。

---

## 1. 研究开始事件

```python
yield self._event(
    state,
    "research_started",
    query=state.query,
    max_iterations=state.max_iterations,
)
```

输出大致是：

```python
{
    "type": "research_started",
    "session_id": "...",
    "phase": "init",
    "iteration": 0,
    "query": "新能源汽车行业趋势",
    "max_iterations": 1,
}
```

表示：

```text
研究任务已经创建，准备开始。
```

---

## 2. 开始规划事件

```python
yield self._event(
    state,
    "phase_started",
    phase="planning",
    agent=self.planner.name,
)
```

输出大致是：

```python
{
    "type": "phase_started",
    "session_id": "...",
    "phase": "planning",
    "iteration": 0,
    "agent": "planner",
}
```

这里显式传入：

```python
phase="planning"
```

因为此时 Planner 还没有执行，`state.phase` 可能仍然是 `"init"`，但事件要提前告诉外部：

```text
接下来正在进入 planning 阶段。
```

---

## 3. 执行 Planner

```python
await self.planner.run(state)
```

Planner 执行完后，状态里有：

```python
state.plan
state.research_questions
```

然后发送：

```python
yield self._event(
    state,
    "plan_ready",
    plan=state.plan,
    research_questions=state.research_questions,
)
```

这个事件告诉外部：

```text
研究计划已经生成，可以继续搜索。
```

---

# 七、`_run_research_phase()` 辅助方法

搜索和事实提取会在初始阶段执行一次，也可能在审核失败后执行补充搜索。

因此代码把它们抽成了一个公共方法：

```python
async def _run_research_phase(
    self,
    state: ResearchState,
    *,
    supplementary: bool,
) -> AsyncIterator[dict[str, Any]]:
```

这里的：

```python
*
```

表示 `supplementary` 必须用关键字传入：

```python
_run_research_phase(
    state,
    supplementary=False,
)
```

不能只靠位置传参。

---

## 1. 发送研究阶段开始事件

```python
yield self._event(
    state,
    "phase_started",
    phase="researching",
    agent=self.researcher.name,
    supplementary=supplementary,
)
```

初始搜索时：

```python
supplementary=False
```

补充搜索时：

```python
supplementary=True
```

这样外部可以区分：

```text
这是第一次搜索
还是 Critic 要求的补充搜索
```

---

## 2. 执行 Researcher 和 FactExtractor

```python
await self.researcher.run(state)
await self.fact_extractor.run(state)
```

顺序是：

```text
Researcher 搜索来源
    ↓
FactExtractor 提取事实
```

然后产生：

```python
yield self._event(
    state,
    "research_evidence_ready",
    supplementary=supplementary,
    source_count=len(state.sources),
    fact_count=len(state.facts),
    sources=state.sources,
    facts=state.facts,
    references=state.references,
)
```

这个事件携带：

- 是否补充搜索；
- 来源数量；
- 事实数量；
- 完整来源；
- 完整事实；
- 引用列表。

例如：

```python
{
    "type": "research_evidence_ready",
    "phase": "researching",
    "iteration": 0,
    "supplementary": False,
    "source_count": 3,
    "fact_count": 3,
    "sources": [...],
    "facts": [...],
    "references": [...],
}
```

---

# 八、Writer 阶段事件

进入写作前：

```python
yield self._event(
    state,
    "phase_started",
    phase="writing",
    agent=self.writer.name,
)
```

然后执行：

```python
await self.writer.run(state)
```

报告生成后：

```python
yield self._event(
    state,
    "draft_ready",
    report=state.final_report,
    revision=False,
)
```

`revision=False` 表示这是第一次生成草稿。

如果是 Critic 之后重新写作：

```python
yield self._event(
    state,
    "phase_started",
    phase="writing",
    agent=self.writer.name,
    revision=True,
)
```

以及：

```python
yield self._event(
    state,
    "draft_ready",
    report=state.final_report,
    revision=True,
)
```

这能让外部知道：

```text
这是初稿
还是修订后的报告
```

---

# 九、审核阶段事件

进入 Critic 前：

```python
yield self._event(
    state,
    "phase_started",
    phase="reviewing",
    agent=self.critic.name,
)
```

然后：

```python
await self.critic.run(state)
```

审核结束后：

```python
yield self._event(
    state,
    "review_completed",
    review=state.review,
    quality_score=state.quality_score,
)
```

事件中包含：

```python
{
    "review": {
        "verdict": "pass",
        "quality_score": 8.0,
        "summary": "...",
        "needs_more_research": False,
        "issues": [],
        "search_queries": [],
    },
    "quality_score": 8.0,
}
```

前端可以在这里显示：

```text
审核已完成
评分：8.0
结论：通过
```

---

# 十、最终完成事件

审核通过或者达到最大修订次数后：

```python
state.phase = "completed"
```

然后发送：

```python
yield self._event(
    state,
    "research_completed",
    report=state.final_report,
    quality_score=state.quality_score,
    references=state.references,
    review=state.review,
)
```

最终事件包含：

- 最终报告；
- 评分；
- 引用；
- 审核结果；
- `phase="completed"`。

示意：

```python
{
    "type": "research_completed",
    "session_id": "...",
    "phase": "completed",
    "iteration": 0,
    "report": "...",
    "quality_score": 8.0,
    "references": [...],
    "review": {...},
}
```

它是整个事件流中的最后一个事件。

---

# 十一、正常情况下的事件顺序

如果第一次审核就通过，事件顺序是：

```text
1. research_started
2. phase_started          planning
3. plan_ready
4. phase_started          researching
5. research_evidence_ready
6. phase_started          writing
7. draft_ready
8. phase_started          reviewing
9. review_completed
10. research_completed
```

这正是测试中验证的顺序。

---

# 十二、补充搜索时的事件顺序

如果第一次 Critic 返回：

```python
{
    "verdict": "needs_revision",
    "needs_more_research": True,
    "search_queries": ["2025年新能源汽车行业数据"],
}
```

那么后面会多出一组事件：

```text
review_completed
    ↓
phase_started          researching
    supplementary=True
    ↓
research_evidence_ready
    supplementary=True
    ↓
phase_started          writing
    revision=True
    ↓
draft_ready
    revision=True
    ↓
phase_started          reviewing
    ↓
review_completed
    ↓
research_completed
```

第二次 `research_evidence_ready` 会有：

```python
"iteration": 1
```

测试明确检查了这一点。

---

# 十三、`_event()` 方法

```python
@staticmethod
def _event(
    state: ResearchState,
    event_type: str,
    *,
    phase: str | None = None,
    **data: Any,
) -> dict[str, Any]:
```

这是一个统一创建事件的辅助函数。

它接收：

- 当前状态；
- 事件类型；
- 可选的阶段；
- 任意附加字段。

```python
return ResearchEvent(
    type=event_type,
    session_id=state.session_id,
    phase=phase or state.phase,
    iteration=state.iteration,
    data=data,
).to_dict()
```

这里：

```python
phase or state.phase
```

表示：

- 如果调用时传入了 `phase`，就用传入的；
- 如果没有传，就使用当前状态中的阶段。

例如：

```python
_event(state, "plan_ready")
```

使用：

```python
state.phase
```

而：

```python
_event(
    state,
    "phase_started",
    phase="planning",
)
```

使用手动指定的：

```python
"planning"
```

`**data` 会收集所有额外的关键字参数。

例如：

```python
_event(
    state,
    "draft_ready",
    report=state.final_report,
    revision=False,
)
```

在方法内部：

```python
data == {
    "report": "...",
    "revision": False,
}
```

---

# 十四、为什么 `run()` 和 `stream()` 共用 `_stream_state()`？

这是本次更新最重要的设计点之一。

## `run()`

```python
async def run(...):
    state = self._new_state(query, session_id)

    async for _ in self._stream_state(state):
        pass

    return state
```

它消费所有事件，但不使用事件，只返回最终状态。

适合：

```text
后台任务
单元测试
不需要实时进度的调用
```

## `stream()`

```python
async def stream(...):
    state = self._new_state(query, session_id)

    async for event in self._stream_state(state):
        yield event
```

它把每个事件逐个交给调用方。

适合：

```text
实时进度页面
聊天界面
SSE
WebSocket
```

这样两种调用方式执行的是同一套业务逻辑。

---

# 十五、测试中的 `collect_events()`

测试定义：

```python
async def collect_events(workflow, query, session_id=None):
    return [
        event
        async for event in workflow.stream(
            query,
            session_id=session_id,
        )
    ]
```

它把异步事件流收集成普通列表，方便测试：

```python
events = asyncio.run(
    collect_events(workflow, "研究问题")
)
```

之后就可以访问：

```python
events[0]
events[-1]
```

---

# 十六、测试验证了什么？

目前测试总数是 39 个，全部通过。

新增测试主要验证两点。

## 1. 事件顺序正确

测试检查：

```python
[event["type"] for event in events]
```

必须等于预期顺序。

这说明事件没有乱序，也没有漏发。

## 2. 会话 ID 一致

```python
self.assertTrue(
    all(event["session_id"] == "stream-001" for event in events)
)
```

同一次工作流产生的所有事件，都必须使用相同的会话 ID。

## 3. 事件中有正确数据

例如：

```python
self.assertEqual(events[4]["source_count"], 3)
self.assertEqual(events[4]["fact_count"], 3)
```

确认研究证据事件带有来源和事实数量。

最后一个事件：

```python
self.assertEqual(events[-1]["phase"], "completed")
self.assertIn("## 执行摘要", events[-1]["report"])
self.assertEqual(events[-1]["quality_score"], 8.0)
self.assertEqual(len(events[-1]["references"]), 3)
```

确认最终事件包含完整结果。

## 4. 补充研究被正确标记

测试检查：

```python
self.assertFalse(evidence_events[0]["supplementary"])
self.assertTrue(evidence_events[1]["supplementary"])
self.assertEqual(evidence_events[1]["iteration"], 1)
```

含义是：

```text
第一次搜索：不是补充搜索
第二次搜索：是补充搜索
第二次搜索：属于第 1 轮修订
```

---

# 十七、当前事件系统还不是什么？

目前它还不是：

```text
FastAPI SSE 服务
WebSocket 服务
前端实时页面
```

当前只是：

```text
异步 Python 事件生成器
```

后续如果接入 FastAPI SSE，可以把：

```python
async for event in workflow.stream(query):
    yield event
```

转换成网络上的实时事件。

也就是说，现在已经把“业务层事件格式”准备好了，但传输层还没有实现。

这次更新的核心意义是：

> 工作流不仅能最终返回结果，还能在每个阶段完成时向外部发布进度，并且支持把补充搜索、报告修订和最终完成过程完整地传出去。
<!-- ORIGINAL_ASSISTANT_19_3_END -->



<a id="qa-20"></a>
### 记录 20：流与 SSE 的小白解释

开始时间（北京时间）：2026-10-06 19:04:17。结束时间：2026-10-06 19:05:34。原始记录 ID：`01a110e2-bdf1-7db1-964c-adaf20ee9f7f`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_20_1_START -->
```text
这个地方我完全没有看懂 因为我是个小白 我不清楚什么流 SSE 这次修改的思想 这次修改的目的 等等一系列东西我都不懂 请你用最合适小白能听懂的话 让我清楚这次修改到底是什么

```
<!-- ORIGINAL_USER_20_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_20_2_START -->
我先重新读取当前最新的事件模型、工作流和测试，确认这次修改的真实代码，再完全不使用默认术语，先从“为什么要改”讲起。
<!-- ORIGINAL_ASSISTANT_20_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_20_3_START -->
你可以先把这次修改浓缩成一句话：

> 研究过程本身没有变，这次修改只是让程序在研究过程中不断汇报“现在做到哪一步了”，而不是让用户一直等到最后。

## 一、修改前有什么问题？

修改前调用：

```python
state = await workflow.run("新能源汽车发展趋势")
```

程序会依次执行：

```text
规划
→ 搜索
→ 提取事实
→ 写报告
→ 审核
→ 返回最终结果
```

但调用者只能看到两种状态：

```text
开始前：什么都没有
结束后：拿到完整结果
```

假设真实研究要花两分钟，用户在这两分钟内不知道程序正在做什么：

```text
是在规划？
是在搜索？
是不是卡住了？
报告写到哪里了？
审核通过了吗？
```

这就像你下单以后，页面一直没有任何变化，两分钟后突然显示“已送达”。

## 二、这次修改想达到什么效果？

现在程序可以不断发出进度消息：

```text
研究开始了
正在制定计划
计划已经生成
正在搜索资料
资料和事实已经准备好
正在写报告
报告草稿已经生成
正在审核
审核完成
整个研究任务结束
```

类似外卖软件不断更新状态：

```text
商家已接单
正在制作
骑手已取餐
正在配送
已经送达
```

这里每一条进度消息就叫作一个“事件”。

所以“事件”并不神秘，它就是：

> 程序在某个重要步骤发生后，向外发送的一条状态消息。

## 三、什么叫“流”？

这里的“流”不是文件流，也不是网络流量。

它表示：

> 结果不是一次性全部给你，而是按照时间顺序，一条一条给你。

普通 `run()` 像一次性领取完整快递：

```text
等待……
等待……
等待……
最终结果
```

`stream()` 像查看实时物流：

```text
消息 1：任务开始
消息 2：规划开始
消息 3：规划完成
消息 4：搜索开始
消息 5：搜索完成
……
消息 10：任务完成
```

这些连续出现的消息合起来，就叫“事件流”。

## 四、`run()` 和 `stream()` 的区别

现在工作流提供两种使用方式。

### `run()`：只关心最终结果

```python
state = await workflow.run("研究问题")
```

调用者会一直等待，最后拿到完整的 `ResearchState`。

适合：

- 命令行程序；
- 后台程序；
- 不需要显示实时进度的场景。

### `stream()`：一边执行，一边拿到进度

```python
async for event in workflow.stream("研究问题"):
    print(event)
```

程序每完成一步，就产生一个事件。

适合：

- 网页显示实时进度；
- 聊天界面；
- 显示“正在搜索资料”；
- 显示“正在生成报告”；
- 显示审核和修订次数。

两者执行的是同一套研究流程，只是获得结果的方式不同。

## 五、为什么会有 `yield`？

普通函数通常只用一次 `return`：

```python
def get_number():
    return 1
```

调用后一次性得到结果：

```python
number = get_number()
```

但工作流要连续提供多个结果，所以使用：

```python
yield
```

可以先简单理解为：

> `yield` 是“先交出一条结果，然后暂停；下次继续从这里执行”。

例如：

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

它不是一次性返回：

```python
[1, 2, 3]
```

而是先产生 `1`，之后产生 `2`，最后产生 `3`。

项目中的：

```python
yield self._event(state, "research_started", ...)
```

意思是：

> 先向调用者发一条“研究开始”的消息，然后继续执行研究。

## 六、为什么是 `async for`？

因为研究步骤是异步的：

```python
await self.planner.run(state)
await self.researcher.run(state)
await self.writer.run(state)
```

真实情况下，搜索和调用大模型都需要等待网络。

因此读取事件时使用：

```python
async for event in workflow.stream(query):
```

可以先把它理解为：

> 每当工作流产生一条新消息，就取出这条消息并处理，然后等待下一条。

## 七、`ResearchEvent` 是什么？

[events.py](D:\课\s4-6\information_deepresearch\backend\app\domain\events.py) 统一规定每条进度消息的基本格式：

```python
@dataclass(frozen=True)
class ResearchEvent:
    type: str
    session_id: str
    phase: str
    iteration: int = 0
    data: dict[str, Any] = field(default_factory=dict)
```

例如“规划完成”事件可能包含：

```python
{
    "type": "plan_ready",
    "session_id": "session-001",
    "phase": "planning",
    "iteration": 0,
    "plan": [...],
    "research_questions": [...],
}
```

各字段的意思是：

```text
type        发生了什么
session_id  属于哪一次研究任务
phase       当前处于哪个阶段
iteration   当前是第几轮修订
其他字段     这个事件附带的具体结果
```

`ResearchEvent` 就像一张统一格式的快递通知单。

## 八、为什么需要统一格式？

如果每个步骤随便返回不同格式，调用方会很难处理：

```python
"规划完成"
{"搜索结束": True}
["报告", "..."]
```

现在所有事件至少都有：

```python
type
session_id
phase
iteration
```

调用方可以统一判断：

```python
if event["type"] == "plan_ready":
    # 显示研究计划

if event["type"] == "draft_ready":
    # 显示报告草稿

if event["type"] == "research_completed":
    # 显示最终结果
```

这相当于先约定了一套共同语言。

## 九、`data` 为什么会被展开？

创建事件时，额外内容先放在：

```python
data={
    "report": "...",
    "references": [...],
}
```

`to_dict()` 执行：

```python
event.update(deepcopy(self.data))
```

最终得到：

```python
{
    "type": "research_completed",
    "session_id": "...",
    "phase": "completed",
    "iteration": 0,
    "report": "...",
    "references": [...],
}
```

调用者可以直接读取：

```python
event["report"]
```

不需要写：

```python
event["data"]["report"]
```

## 十、`deepcopy()` 是为了什么？

事件应该记录“当时”的状态。

例如第一次搜索后有 3 条来源，发出一个事件：

```python
source_count = 3
sources = [...]
```

后来补充搜索，来源变成 4 条。

如果事件和 `state.sources` 使用同一个列表，旧事件有可能也跟着变化。使用：

```python
deepcopy(self.data)
```

就是给事件保存一份独立副本。

可以把事件理解为一张截图：

> 截图记录的是那个时刻的内容，后面状态改变也不会修改旧截图。

## 十一、现在真正执行工作的地方在哪里？

现在真正的主流程集中在：

```python
_stream_state()
```

它一边工作，一边发消息：

```python
yield 任务开始事件

yield 规划开始事件
await Planner
yield 规划完成事件

yield 搜索开始事件
await Researcher
await FactExtractor
yield 证据准备完成事件

yield 写作开始事件
await Writer
yield 草稿完成事件

yield 审核开始事件
await Critic
yield 审核完成事件

yield 研究完成事件
```

所以 `_stream_state()` 同时承担两件事：

1. 调度各个 Agent；
2. 在关键节点产生进度事件。

## 十二、为什么 `run()` 里有一个空的 `pass`？

现在的 `run()` 是：

```python
state = self._new_state(query, session_id)

async for _ in self._stream_state(state):
    pass

return state
```

`_stream_state()` 会真正运行整个研究流程，同时不断产生事件。

但是 `run()` 不需要这些中间事件，它只想等到最后拿到 `state`。

所以：

```python
async for _ in ...:
    pass
```

意思是：

> 让工作流继续运行，把所有事件都取出来，但不处理这些事件。

这里的 `_` 是常见命名，表示：

```text
这个值我拿到了，但不会使用。
```

这样 `run()` 和 `stream()` 共用同一套业务代码。

## 十三、为什么不写两套流程？

如果分别写：

```python
run() 里一套研究流程
stream() 里另一套研究流程
```

以后修改审核逻辑时，很可能只改其中一套，造成：

```text
run() 的结果和 stream() 的结果不一样
```

现在统一成：

```text
              _stream_state()
              /             \
run() 忽略事件                stream() 把事件交给调用者
```

研究步骤只有一份，因此更不容易出错。

## 十四、SSE 到底是什么？

SSE 全名是：

```text
Server-Sent Events
```

中文可以理解为：

> 服务器持续向浏览器发送消息的一种方式。

假设未来有一个网页，用户点击“开始研究”。

普通请求可能是：

```text
浏览器发送问题
→ 等待两分钟
→ 服务器一次性返回最终报告
```

使用 SSE 后可以变成：

```text
浏览器发送问题
→ 服务器保持连接
→ 发来“正在规划”
→ 发来“正在搜索”
→ 发来“找到 3 个来源”
→ 发来“报告已生成”
→ 发来“审核完成”
```

网页收到每条消息后，就能立即更新界面。

但当前项目**还没有实现 SSE**。

现在只完成了 SSE 前面需要的准备：

```text
先让 Python 工作流能够一条一条产生事件
```

以后再把这些事件通过 SSE 发送到浏览器。

## 十五、这次修改到底改了什么？

没有改变这些 Agent 的基本职责：

```text
Planner 仍然负责规划
Researcher 仍然负责搜索
FactExtractor 仍然负责事实
Writer 仍然负责写报告
Critic 仍然负责审核
```

改变的是“工作流如何把过程告诉外部”。

修改前：

```text
调用工作流
→ 中间完全不可见
→ 最后返回结果
```

修改后：

```text
调用工作流
→ 告诉你研究开始
→ 告诉你计划完成
→ 告诉你证据完成
→ 告诉你报告完成
→ 告诉你审核完成
→ 返回最终结果
```

## 十六、为什么现在就做这次修改？

因为以后做网页时，DeepResearch 通常需要较长时间。

如果没有事件系统，网页只能：

```text
正在加载……
```

如果有事件系统，网页可以显示真实进度：

```text
正在规划研究方向
已生成 3 个研究问题
正在搜索公开资料
已找到 3 个来源
正在整理事实
正在生成报告
正在审核报告
研究完成
```

所以这次修改的目的不是让研究“更聪明”，而是让研究过程：

- 看得见；
- 可以被前端展示；
- 可以跟踪当前阶段；
- 可以区分初稿和修订稿；
- 可以看到补充研究发生在哪一轮；
- 以后容易接入 SSE。

最应该记住的是：

> `state` 是研究任务不断变化的“总档案”；`event` 是从这份档案中截取的一张“进度通知”；`stream()` 负责把这些通知按照时间顺序一张张交出去；SSE 将来负责把这些通知从服务器送到浏览器。
<!-- ORIGINAL_ASSISTANT_20_3_END -->



<a id="qa-21"></a>
### 记录 21：V2 领域模型与长期契约

开始时间（北京时间）：2026-10-06 20:17:55。结束时间：2026-10-06 20:23:52。原始记录 ID：`01a11126-2517-77a1-adbc-ac9d1bbda616`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_21_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_21_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_21_2_START -->
我先重新读取项目当前版本，确认这次相对上一轮新增或修改了哪些内容；我会继续排除自动生成的缓存文件，只基于最新源码和测试讲解。
<!-- ORIGINAL_ASSISTANT_21_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_21_3_START -->
我已按你的要求重新读取了最新项目内容，并确认这次最新增加的核心内容是：

- [models.py](D:\课\s4-6\information_deepresearch\backend\app\domain\models.py)
- [test_domain_models.py](D:\课\s4-6\information_deepresearch\backend\tests\test_domain_models.py)
- [v2-core-contract.md](D:\课\s4-6\information_deepresearch\docs\v2-core-contract.md)

这次修改的核心思想是：

> 之前项目主要使用普通字典保存数据；现在开始为“章节、假设、数据、图表、审核问题”建立更清楚的数据模型。

可以把它理解成：

```text
以前：一个大纸箱，里面什么都可以放
现在：为章节、数据、图表等分别制作标准表格
```

---

# 一、为什么需要 `models.py`？

之前的代码中，研究计划是这样保存的：

```python
state.plan = [
    {
        "title": "现状与定义",
        "description": "分析行业现状",
    }
]
```

这只是一个普通字典。

问题是，普通字典非常自由，下面这种数据 Python 也可能接受：

```python
{
    "abc": 123,
    "hello": True,
}
```

但是它不一定符合研究系统的要求。

未来项目会出现很多复杂对象：

- 报告章节；
- 研究假设；
- 数据点；
- 图表；
- 审核意见。

如果所有内容都用普通字典，代码会越来越混乱。

因此新增：

```python
backend/app/domain/models.py
```

专门描述这些数据应该长什么样。

注意：

> 当前这些模型主要是“数据结构定义”，还没有完全接入现有的 Planner、Researcher 和 Workflow。

---

# 二、文件开头

```python
"""DeepResearch V2 使用的基础领域对象。

这些对象先只描述数据形状，不负责调用 LLM、搜索服务或数据库。
把数据形状单独放在这里，可以让后续 Agent 共享同一套结构。
"""
```

这里明确说了，这个文件目前只负责：

```text
定义数据长什么样
```

不负责：

```text
调用大模型
搜索网页
连接数据库
执行研究流程
```

这叫“领域对象”。

例如：

```text
Section       章节对象
Hypothesis    假设对象
DataPoint     数据对象
Chart         图表对象
CriticFeedback 审核反馈对象
```

---

# 三、导入内容

```python
from dataclasses import asdict, dataclass, field
```

这里导入三个工具。

## `dataclass`

让 Python 自动生成对象初始化方法。

例如：

```python
@dataclass
class DataPoint:
    id: str
    name: str
```

就可以这样创建：

```python
point = DataPoint(
    id="dp-1",
    name="市场规模",
)
```

不需要自己写 `__init__()`。

## `field`

用于设置复杂默认值，例如独立的空列表：

```python
evidence_for: list[str] = field(default_factory=list)
```

## `asdict`

把数据类对象转换成字典：

```python
point.to_dict()
```

内部就是调用：

```python
asdict(self)
```

---

```python
from typing import Any, Literal
```

## `Any`

表示任意类型。

例如：

```python
value: Any
```

表示 `value` 可以是：

```python
100
"120亿元"
[1, 2, 3]
{"x": 1}
```

## `Literal`

表示某个字段建议只能使用指定的几个值。

例如：

```python
ChartType = Literal[
    "line",
    "bar",
    "pie",
    "scatter",
    "table",
    "heatmap",
]
```

意思是图表类型可以是：

```text
line      折线图
bar       柱状图
pie       饼图
scatter   散点图
table     表格
heatmap   热力图
```

不过要注意：

> `Literal` 主要是类型提示，不是运行时强制检查。

也就是说，当前代码中：

```python
Chart(
    id="chart-1",
    title="测试",
    chart_type="unknown",
)
```

Python 可能仍然允许创建。真正的运行时校验还需要以后额外编写。

---

# 四、这些类型别名是什么？

## 1. 章节类型

```python
SectionType = Literal[
    "qualitative",
    "quantitative",
    "mixed",
]
```

表示一个章节属于哪种研究类型：

```text
qualitative   定性研究
quantitative   定量研究
mixed          混合研究
```

例如：

```python
section_type="quantitative"
```

表示该章节主要处理数字、统计数据等内容。

---

## 2. 章节状态

```python
SectionStatus = Literal[
    "pending",
    "researching",
    "drafted",
    "reviewed",
    "final",
]
```

表示章节当前进行到哪一步：

```text
pending       待处理
researching   正在研究
drafted       已有草稿
reviewed      已审核
final         已定稿
```

---

## 3. 假设状态

```python
HypothesisStatus = Literal[
    "unverified",
    "supported",
    "refuted",
    "partially_supported",
]
```

表示研究假设目前的证据状态：

```text
unverified            尚未验证
supported             得到证据支持
refuted               被证据否定
partially_supported   部分支持
```

---

## 4. 图表类型

```python
ChartType = Literal[
    "line",
    "bar",
    "pie",
    "scatter",
    "table",
    "heatmap",
]
```

表示系统支持的图表类型。

---

## 5. 审核问题类型

```python
IssueType = Literal[
    "missing_source",
    "logic_error",
    "bias",
    "hallucination",
    "outdated",
    "incomplete",
]
```

表示报告存在什么问题：

```text
missing_source   缺少来源
logic_error      逻辑错误
bias             偏见
hallucination    幻觉或无依据内容
outdated         内容过时
incomplete       内容不完整
```

---

## 6. 问题严重程度

```python
IssueSeverity = Literal[
    "critical",
    "major",
    "minor",
]
```

表示问题有多严重：

```text
critical   致命问题
major      主要问题
minor      次要问题
```

---

# 五、`Section`：报告章节对象

代码：

```python
@dataclass
class Section:
    """研究报告中的一个章节。"""

    id: str
    title: str
    description: str = ""
    section_type: SectionType = "mixed"
    status: SectionStatus = "pending"
    content: str = ""
    sources: list[str] = field(default_factory=list)
    subsections: list[Section] = field(default_factory=list)
    requires_data: bool = False
    requires_chart: bool = False
    priority: int = 0
    search_queries: list[str] = field(default_factory=list)
```

它表示报告中的一个章节。

可以这样创建：

```python
section = Section(
    id="sec-1",
    title="行业概况",
    description="研究行业规模和定义",
)
```

## 每个字段的意思

### `id`

```python
id: str
```

章节的唯一编号：

```text
sec-1
sec-2
sec-1-1
```

### `title`

```python
title: str
```

章节标题：

```text
行业概况
市场规模
未来趋势
```

这两个字段没有默认值，所以创建时必须提供。

---

### `description`

```python
description: str = ""
```

章节说明。

默认是空字符串。

例如：

```python
description="研究行业规模、定义和发展阶段"
```

---

### `section_type`

```python
section_type: SectionType = "mixed"
```

章节类型，默认是：

```python
"mixed"
```

也就是混合类型。

---

### `status`

```python
status: SectionStatus = "pending"
```

章节状态默认是：

```python
"pending"
```

也就是还没有开始处理。

---

### `content`

```python
content: str = ""
```

章节正文内容。

刚创建时还没有内容，所以默认是空字符串。

---

### `sources`

```python
sources: list[str] = field(default_factory=list)
```

保存这个章节使用的来源 URL：

```python
[
    "https://example.com/report-1",
    "https://example.com/report-2",
]
```

使用 `default_factory=list` 很重要，因为每个章节必须有自己的来源列表。

---

### `subsections`

```python
subsections: list[Section] = field(default_factory=list)
```

表示章节下面还可以有子章节。

例如：

```text
第一章 行业概况
    1.1 市场定义
    1.2 市场规模
```

可以写成：

```python
section = Section(
    id="sec-1",
    title="行业概况",
    subsections=[
        Section(
            id="sec-1-1",
            title="市场定义",
        ),
        Section(
            id="sec-1-2",
            title="市场规模",
        ),
    ],
)
```

这里的：

```python
list[Section]
```

表示：

```text
一个 Section 里面可以包含多个 Section
```

这叫递归结构。

代码顶部有：

```python
from __future__ import annotations
```

它让这种类型标注可以更顺利地引用当前正在定义的 `Section` 类。

---

### `requires_data`

```python
requires_data: bool = False
```

这个章节是否需要数据分析。

```python
True
```

表示需要数字、统计数据等。

---

### `requires_chart`

```python
requires_chart: bool = False
```

这个章节是否需要图表。

例如：

```python
requires_chart=True
```

表示未来需要生成折线图、柱状图等。

---

### `priority`

```python
priority: int = 0
```

章节优先级。

数字越大，可以表示越重要。

---

### `search_queries`

```python
search_queries: list[str] = field(default_factory=list)
```

专门为该章节准备的搜索问题。

例如：

```python
[
    "2025年新能源汽车市场规模",
    "新能源汽车销量官方统计",
]
```

---

## `Section.to_dict()`

```python
def to_dict(self) -> dict[str, Any]:
    """转换成可以放入 ResearchState 的普通字典。"""
    return asdict(self)
```

把对象转换成字典。

例如：

```python
section = Section(
    id="sec-1",
    title="行业概况",
)
```

调用：

```python
section.to_dict()
```

得到类似：

```python
{
    "id": "sec-1",
    "title": "行业概况",
    "description": "",
    "section_type": "mixed",
    "status": "pending",
    "content": "",
    "sources": [],
    "subsections": [],
    "requires_data": False,
    "requires_chart": False,
    "priority": 0,
    "search_queries": [],
}
```

如果有子章节，`asdict()` 会递归转换子章节。

---

# 六、`Hypothesis`：研究假设对象

代码：

```python
@dataclass
class Hypothesis:
    """研究开始时提出、再由证据验证的假设。"""

    id: str
    content: str
    status: HypothesisStatus = "unverified"
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)
```

它表示：

> 在正式研究前，先提出一个猜想，然后用证据验证它。

例如：

```python
hypothesis = Hypothesis(
    id="h-1",
    content="新能源汽车市场仍将保持增长",
)
```

刚创建时：

```python
hypothesis.status == "unverified"
```

表示还没有验证。

找到支持证据后：

```python
hypothesis.evidence_for.append(
    "某官方报告显示销量连续增长"
)
hypothesis.status = "supported"
```

如果找到相反证据：

```python
hypothesis.evidence_against.append(
    "某地区销量连续下降"
)
```

## 字段解释

```python
id
```

假设编号。

```python
content
```

假设的具体内容。

```python
status
```

当前验证状态，默认是 `"unverified"`。

```python
evidence_for
```

支持该假设的证据。

```python
evidence_against
```

反对该假设的证据。

---

# 七、`DataPoint`：数据点对象

代码：

```python
@dataclass
class DataPoint:
    """可以被分析或绘图使用的结构化数据点。"""

    id: str
    name: str
    value: Any
    unit: str = ""
    year: int | None = None
    source: str = ""
    confidence: float = 0.0
```

它表示一个可以进行分析或画图的数据。

例如：

```python
data_point = DataPoint(
    id="dp-1",
    name="市场规模",
    value=120.5,
    unit="亿元",
    year=2025,
    source="https://example.com/source",
    confidence=0.9,
)
```

表示：

```text
名称：市场规模
数值：120.5
单位：亿元
年份：2025
来源：https://example.com/source
置信度：0.9
```

## 字段解释

### `id`

数据点编号。

### `name`

数据名称：

```text
市场规模
销量
增长率
用户数量
```

### `value`

```python
value: Any
```

数据值可以是很多类型：

```python
120.5
"120亿元"
[100, 110, 120]
```

当前没有限制具体类型。

### `unit`

单位：

```text
亿元
万辆
%
```

### `year`

```python
year: int | None = None
```

表示年份可以是整数，也可以是 `None`。

```python
2025
```

表示数据属于 2025 年。

```python
None
```

表示没有年份信息。

### `source`

数据来源 URL。

### `confidence`

数据置信度，默认是：

```python
0.0
```

注意，当前代码不会自动检查它是否在 0 到 1 之间。它只是一个字段。

---

# 八、`Chart`：图表对象

代码：

```python
@dataclass
class Chart:
    """DataAnalyst 或 CodeWizard 生成的图表结果。"""

    id: str
    title: str
    chart_type: ChartType
    data: dict[str, Any] = field(default_factory=dict)
    code: str = ""
    image_path: str | None = None
    image_base64: str | None = None
    section_id: str | None = None
```

它表示一张图表及其生成信息。

例如：

```python
chart = Chart(
    id="chart-1",
    title="市场规模趋势",
    chart_type="line",
    data={
        "x": [2024, 2025],
        "y": [100, 120.5],
    },
    section_id="sec-1",
)
```

## 字段解释

```python
id
```

图表编号。

```python
title
```

图表标题。

```python
chart_type
```

图表类型，例如：

```python
"line"
"bar"
"pie"
```

```python
data
```

绘图数据。

例如：

```python
{
    "x": [2024, 2025],
    "y": [100, 120.5],
}
```

```python
code
```

生成图表时使用的代码。

例如未来可能保存：

```python
import matplotlib.pyplot as plt
...
```

```python
image_path
```

图表生成后的图片文件路径。

```python
image_base64
```

图像的 Base64 内容，适合直接传输给前端。

```python
section_id
```

这张图属于哪个报告章节。

---

# 九、`CriticFeedback`：审核反馈对象

代码：

```python
@dataclass
class CriticFeedback:
    """审核 Agent 针对报告或章节提出的一条问题。"""

    id: str
    target_section: str
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    suggestion: str
    resolved: bool = False
```

它表示 Critic 发现的一条具体问题。

例如：

```python
feedback = CriticFeedback(
    id="issue-1",
    target_section="sec-1",
    issue_type="missing_source",
    severity="major",
    description="关键数据缺少来源",
    suggestion="补充官方统计来源",
)
```

含义是：

```text
问题编号：issue-1
问题所在章节：sec-1
问题类型：缺少来源
严重程度：主要问题
问题描述：关键数据缺少来源
修改建议：补充官方统计来源
是否解决：否
```

默认：

```python
resolved = False
```

表示刚发现的问题还没有解决。

之后可以修改：

```python
feedback.resolved = True
```

表示已经处理完成。

---

# 十、为什么所有对象都有 `to_dict()`？

这些对象是 Python 数据类，但后续可能需要：

- 放进 `ResearchState`；
- 返回 API；
- 转成 JSON；
- 保存到数据库；
- 传给前端；
- 写入测试结果。

普通 Python 对象不一定能直接被 JSON 序列化。

所以提供：

```python
to_dict()
```

例如：

```python
chart.to_dict()
```

就能得到普通字典。

以后如果要返回 JSON，就更方便。

---

# 十一、`test_domain_models.py` 测试什么？

## 1. 测试嵌套章节

```python
section = Section(
    id="sec-1",
    title="行业概况",
    description="研究行业规模和定义",
    requires_data=True,
    search_queries=["行业规模"],
    subsections=[
        Section(id="sec-1-1", title="市场定义")
    ],
)
```

这里创建了一个父章节：

```text
行业概况
```

里面有一个子章节：

```text
市场定义
```

转换后检查：

```python
self.assertEqual(result["subsections"][0]["title"], "市场定义")
```

说明 `to_dict()` 能正确转换嵌套结构。

---

## 2. 测试列表不会共享

```python
first = Hypothesis(id="h-1", content="第一个假设")
second = Hypothesis(id="h-2", content="第二个假设")

first.evidence_for.append("支持证据")
```

然后检查：

```python
first.evidence_for == ["支持证据"]
second.evidence_for == []
```

这证明：

```python
field(default_factory=list)
```

为每个对象创建了独立列表。

---

## 3. 测试数据和图表字段

```python
data_point = DataPoint(...)
chart = Chart(...)
```

检查：

```python
data_point.to_dict()["year"] == 2025
data_point.to_dict()["confidence"] == 0.9
chart.to_dict()["chart_type"] == "line"
chart.to_dict()["section_id"] == "sec-1"
```

说明数据类没有丢失这些分析字段。

---

## 4. 测试审核问题默认未解决

```python
feedback = CriticFeedback(...)
```

检查：

```python
self.assertFalse(feedback.resolved)
```

说明新的审核问题默认是未解决状态。

---

# 十二、新增的 `v2-core-contract.md` 是什么？

文件：

```text
docs/v2-core-contract.md
```

它不是程序代码，而是一份“项目方向和约束文档”。

可以把它理解成：

> 以后继续开发时，大家必须遵守的一份设计合同。

它说明：

- 项目最终要实现什么；
- 每个 Agent 负责什么；
- 状态里必须保存什么；
- 审核失败后如何处理；
- 哪些旧项目内容不需要复制；
- 每个迭代先做什么。

---

# 十三、原项目角色和学习版角色的对应关系

文档中有一张表：

| 原项目 V2 角色 | 学习版角色 | 当前状态 |
| --- | --- | --- |
| ChiefArchitect | `PlannerAgent` | 已有简化版 |
| DeepScout | `ResearcherAgent` + `FactExtractorAgent` | 已有简化版 |
| DataAnalyst | 待建立 `DataAnalystAgent` | 未实现 |
| CodeWizard | 待建立 `CodeWizardAgent` | 未实现 |
| LeadWriter | `WriterAgent` | 已有简化版 |
| CriticMaster | `CriticAgent` | 已有简化版 |
| V2 Graph | `ResearchWorkflow` | 已有简化版 |

这张表告诉我们：

```text
原项目中的复杂角色
        ↓
学习版中的简单实现
```

例如：

```text
DeepScout
```

在学习版中被拆成：

```text
ResearcherAgent
FactExtractorAgent
```

因为这样更容易一步一步学习。

需要注意：

> 这张表只是项目设计对应关系，不表示原项目的全部功能已经实现。

目前明确还没有实现：

```text
DataAnalystAgent
CodeWizardAgent
```

---

# 十四、最终状态未来要保存什么？

文档要求最终的 `ResearchState` 至少能够表达：

```text
用户问题
会话 ID
当前阶段
迭代次数
章节大纲
研究子问题
研究假设
关键实体
原始来源
结构化事实
数据点
洞察
知识图谱
图表配置
代码执行记录
草稿
最终报告
参考文献
审核意见
质量评分
待补充搜索查询
事件消息
日志
错误
任务状态
```

但当前的 `state.py` 还没有全部字段。

目前已经有：

```python
query
session_id
phase
iteration
plan
research_questions
pending_search_queries
sources
facts
references
final_report
review
quality_score
errors
```

还没有正式加入：

```text
hypotheses
data_points
insights
charts
knowledge_graph
execution_records
```

新增的 `models.py` 是在为这些未来字段准备标准对象。

---

# 十五、审核流程必须保留三种情况

文档明确规定审核结束后要支持三种路线：

## 1. 审核通过

```text
pass
→ 研究完成
```

## 2. 需要新证据

```text
needs_revision
→ 补充搜索
→ 重新提取事实
→ 重新写报告
→ 再次审核
```

当前工作流已经实现了这条路线。

## 3. 不需要新证据，只需修改文字

```text
needs_revision
→ 根据审核意见修改报告
→ 再次审核
```

当前工作流也已经实现了这条路线。

## 4. 达到最大迭代次数

即使仍然没有通过，也可以结束，但必须保留：

```python
state.review
state.quality_score
state.iteration
```

这样调用者知道：

```text
流程结束了
但最后一次审核仍然认为需要修改
```

---

# 十六、最终结果必须包含什么？

文档要求最终结果至少有：

```text
研究报告
报告引用的来源
结构化事实
数据点和洞察
图表结果
审核结论
质量评分
迭代次数
```

当前项目已经有：

```python
final_report
references
facts
review
quality_score
iteration
```

还没有真正实现：

```text
data_points
insights
charts
```

所以新增的 `DataPoint` 和 `Chart` 是为未来输出做准备的。

---

# 十七、迭代路线是什么意思？

文档列出了 11 个阶段：

```text
iteration-01：Mock 环境跑通基本链路
iteration-02：对齐状态模型和事件协议
iteration-03：加入章节、假设、数据点和知识图谱
iteration-04：实现 DataAnalyst
iteration-05：实现 CodeWizard
iteration-06：完善章节写作和审核
iteration-07：接入 FastAPI SSE
iteration-08：检查点、恢复和取消
iteration-09：接入真实 LLM 和真实搜索
iteration-10：简化前端
iteration-11：端到端测试和文档整理
```

当前这次新增的 `models.py` 主要是在为后面的领域模型打基础。

尤其对应：

```text
iteration-02：建立领域对象
iteration-03：加入章节、假设、数据点和知识图谱基础
```

但现在还不是说这些功能全部完成了。

---

# 十八、最重要的现实状态

当前项目有两套数据表达方式：

## 现有第一阶段代码

主要使用：

```python
list[dict[str, Any]]
```

例如：

```python
state.sources
state.facts
state.plan
```

## 新增的 V2 领域模型

开始提供：

```python
Section
Hypothesis
DataPoint
Chart
CriticFeedback
```

但是目前它们还没有全部接入：

```python
ResearchState
PlannerAgent
ResearcherAgent
WriterAgent
ResearchWorkflow
```

所以现在更准确地说：

> 这次更新是“先把未来需要的数据结构定义好并测试通过”，而不是已经把整个系统切换到这些新模型。

当前测试总数为 43 个，并且全部通过。此次新测试主要证明这些新数据对象可以：

- 正确创建；
- 正确转换成字典；
- 正确保存嵌套章节；
- 正确保存数据和图表字段；
- 不共享默认列表；
- 正确记录未解决的审核问题。

一句话总结：

> 之前项目已经有了“研究流程”；这次新增的是“未来研究系统需要使用的标准数据表格和整体设计契约”，让后续的数据分析、图表、章节写作和更复杂审核有明确基础。
<!-- ORIGINAL_ASSISTANT_21_3_END -->



<a id="qa-22"></a>
### 记录 22：扩展共享状态

开始时间（北京时间）：2026-10-06 20:31:23。结束时间：2026-10-06 20:36:17。原始记录 ID：`01a11132-7b06-7b91-bdd1-24a5c85e3ed6`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_22_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_22_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_22_2_START -->
我先重新扫描项目当前版本，确认这次相对上一轮又新增或修改了哪些文件；仍然只依据最新源码、文档和测试来解释。
<!-- ORIGINAL_ASSISTANT_22_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_22_3_START -->
我已经重新读取了当前项目。相对上一轮，最新修改集中在：

- [state.py](D:\课\s4-6\information_deepresearch\backend\app\domain\state.py)
- [test_state.py](D:\课\s4-6\information_deepresearch\backend\tests\test_state.py)

这次的核心不是新增一个 Agent，而是把 `ResearchState` 扩展成更完整的“研究任务总档案”。

目前 43 个测试全部通过。

---

# 一、先理解：`ResearchState` 是什么？

可以把它想象成一个文件夹：

```text
一次研究任务 = 一个文件夹
```

里面放着：

```text
用户问题
研究计划
搜索问题
网页来源
事实
数据
图表
报告
审核结果
错误日志
```

之前这个文件夹内容比较少：

```text
问题
计划
来源
事实
报告
审核结果
```

这次给它增加了很多未来需要的栏目：

```text
章节大纲
关键实体
研究假设
思维导图
知识图谱
数据点
洞察
图表
代码执行记录
章节草稿
审核反馈
日志
消息
```

---

# 二、阶段 `phase` 扩展了

以前注释是：

```python
# 当前阶段：init / planning / researching / writing /
# reviewing / completed
```

现在变成：

```python
# 当前阶段：init / planning / researching / analyzing / writing /
# reviewing / re_researching / revising / completed
```

新增了三个阶段：

```text
analyzing          数据分析中
re_researching    重新搜索中
revising          修订报告中
```

完整含义：

```text
init              刚创建
planning          正在制定计划
researching       正在搜索和整理资料
analyzing         正在分析数据
writing           正在撰写报告
reviewing         正在审核报告
re_researching    审核后补充搜索
revising          根据意见修改报告
completed         整个任务结束
```

但是要特别注意：

> 这些阶段名称现在只是提前写入状态模型，当前工作流还没有全部使用它们。

当前 `ResearchWorkflow` 主要仍然使用：

```text
planning
researching
writing
reviewing
completed
```

以后实现数据分析和更细的修订流程时，才会用到：

```text
analyzing
re_researching
revising
```

---

# 三、规划相关的新字段

## 1. `plan`

```python
plan: list[dict[str, Any]] = field(default_factory=list)
```

这是原来已有的研究计划。

例如：

```python
[
    {
        "title": "行业现状",
        "description": "分析行业规模和发展阶段",
    }
]
```

---

## 2. `outline`

```python
outline: list[dict[str, Any]] = field(default_factory=list)
```

这是新增的“报告章节大纲”。

`plan` 和 `outline` 很相似，但侧重点不同。

### `plan`

回答：

```text
研究过程准备做什么？
```

例如：

```text
搜索行业规模
分析发展趋势
寻找主要问题
```

### `outline`

回答：

```text
最终报告准备写哪些章节？
```

例如：

```python
[
    {
        "id": "sec-1",
        "title": "行业概况",
    },
    {
        "id": "sec-2",
        "title": "市场规模",
    },
    {
        "id": "sec-3",
        "title": "未来趋势",
    },
]
```

当前代码中 `outline` 仍然是普通字典列表。

注释也明确写了：

```python
# V2 章节大纲。当前仍用字典保存，后续 Planner 会逐步使用 Section。
```

也就是说，未来可能改成使用前面新增的：

```python
Section
```

对象。

---

## 3. `research_questions`

```python
research_questions: list[str] = field(default_factory=list)
```

这是需要搜索的具体研究问题。

例如：

```python
[
    "新能源汽车行业当前规模是多少？",
    "行业面临哪些主要问题？",
    "未来趋势是什么？",
]
```

---

## 4. `key_entities`

```python
key_entities: list[str] = field(default_factory=list)
```

这是研究中出现的关键实体。

“实体”可以理解为重要的人、公司、机构、地点、产品或概念。

例如：

```python
[
    "新能源汽车",
    "比亚迪",
    "特斯拉",
    "中国汽车工业协会",
]
```

以后可以用它来：

- 建立知识图谱；
- 组织搜索；
- 分析实体之间的关系；
- 让报告更有结构。

当前还没有 Agent 往这个字段里写数据。

---

## 5. `hypotheses`

```python
hypotheses: list[dict[str, Any]] = field(default_factory=list)
```

这是研究假设列表。

假设就是：

> 在研究开始时提出的一个猜想，之后用资料验证它。

例如：

```python
[
    {
        "id": "h-1",
        "content": "新能源汽车市场仍然会继续增长",
        "status": "unverified",
    }
]
```

它对应前面新增的 `Hypothesis` 类。

当前仍然先使用字典保存，未来可以转换为：

```python
Hypothesis(...)
```

---

# 四、思维导图和知识图谱

## 1. `mind_map`

```python
mind_map: dict[str, Any] = field(default_factory=dict)
```

这是思维导图数据。

它可能描述研究主题的层级关系：

```text
新能源汽车
├── 市场规模
├── 技术发展
├── 政策环境
└── 未来趋势
```

当前默认是空字典：

```python
{}
```

还没有规定具体格式。

---

## 2. `knowledge_graph`

```python
knowledge_graph: dict[str, Any] = field(
    default_factory=lambda: {"nodes": [], "edges": []}
)
```

这是知识图谱。

它通常由两部分组成：

```text
nodes   节点
edges   关系
```

例如：

```python
{
    "nodes": [
        {"id": "n1", "name": "新能源汽车"},
        {"id": "n2", "name": "政策支持"},
    ],
    "edges": [
        {
            "source": "n2",
            "target": "n1",
            "relation": "促进",
        }
    ],
}
```

可以理解为：

```text
政策支持 ──促进──> 新能源汽车
```

当前默认值是：

```python
{
    "nodes": [],
    "edges": [],
}
```

---

## 为什么这里使用 `lambda`？

代码是：

```python
field(
    default_factory=lambda: {
        "nodes": [],
        "edges": [],
    }
)
```

`lambda` 是一个没有名字的小函数。

它大致等价于：

```python
def create_empty_graph():
    return {
        "nodes": [],
        "edges": [],
    }
```

`default_factory` 会在每次创建 `ResearchState` 时调用这个函数。

因此：

```python
first = ResearchState("问题一")
second = ResearchState("问题二")
```

两者拥有不同的知识图谱：

```python
first.knowledge_graph is not second.knowledge_graph
```

如果直接写：

```python
knowledge_graph = {
    "nodes": [],
    "edges": [],
}
```

就可能导致多个任务共享同一个可变字典，这是危险的。

---

# 五、研究证据相关的新字段

## 1. `sources`

```python
sources: list[dict[str, Any]] = field(default_factory=list)
```

这是当前工作流正在使用的来源列表。

Researcher 会把搜索结果写入这里。

例如：

```python
[
    {
        "title": "行业报告",
        "url": "https://example.com/report",
        "content": "报告正文",
    }
]
```

---

## 2. `raw_sources`

```python
raw_sources: list[dict[str, Any]] = field(default_factory=list)
```

这是新增的“原始搜索结果”保存位置。

注释写得很清楚：

```python
# raw_sources 保留原始搜索结果，sources 继续兼容 iteration-01 Agent。
```

可以这样区分：

```text
raw_sources   搜索服务原样返回的资料
sources       经过整理、去重或标准化后的来源
```

例如搜索服务可能返回：

```python
{
    "title": "...",
    "url": "...",
    "snippet": "...",
    "content": "...",
    "query": "...",
    "search_engine_score": 0.83,
}
```

未来程序可能：

```text
raw_sources 保存完整原始数据
sources 只保存研究流程需要的数据
```

这样即使后面整理过程改变，也不会丢失原始结果。

当前 Researcher 仍然主要写入：

```python
state.sources
```

还没有正式使用：

```python
state.raw_sources
```

---

## 3. `facts`

```python
facts: list[dict[str, Any]] = field(default_factory=list)
```

保存从来源中提取出的事实。

例如：

```python
[
    {
        "content": "某行业在 2025 年增长了 20%。",
        "source_url": "https://example.com/report",
        "confidence": 0.8,
    }
]
```

---

## 4. `data_points`

```python
data_points: list[dict[str, Any]] = field(default_factory=list)
```

保存可以用于分析或画图的数字数据。

例如：

```python
[
    {
        "id": "dp-1",
        "name": "2025年市场规模",
        "value": 120.5,
        "unit": "亿元",
        "year": 2025,
        "source": "https://example.com/report",
    }
]
```

它对应新增的：

```python
DataPoint
```

对象。

`facts` 和 `data_points` 的区别是：

```text
fact        一条文字事实
data_point  可以进行计算或画图的结构化数字
```

例如：

```text
事实：市场规模在 2025 年继续增长。
数据点：2025 年市场规模 = 120.5 亿元。
```

---

## 5. `insights`

```python
insights: list[str] = field(default_factory=list)
```

这是数据分析后得到的洞察。

例如：

```python
[
    "市场规模连续三年增长，但增速正在下降。",
    "政策支持主要集中在一线城市。",
]
```

可以这样区分：

```text
facts       资料明确说了什么
data_points 资料中有哪些数字
insights    根据事实和数据可以看出什么
```

当前还没有 `DataAnalystAgent`，所以这个字段还不会自动填充。

---

## 6. `references`

```python
references: list[dict[str, Any]] = field(default_factory=list)
```

这是报告中使用的简化引用列表。

当前 Researcher 会写入：

```python
[
    {
        "title": "来源标题",
        "url": "https://example.com",
    }
]
```

---

# 六、写作和审核相关的新字段

## 1. `draft_sections`

```python
draft_sections: dict[str, str] = field(default_factory=dict)
```

这是“各章节草稿”。

例如：

```python
{
    "sec-1": "这是行业概况章节的草稿。",
    "sec-2": "这是市场规模章节的草稿。",
}
```

当前 Writer 生成的是整体报告：

```python
state.final_report
```

未来可能先分别写章节：

```text
章节一草稿
章节二草稿
章节三草稿
```

最后再合并成完整报告。

---

## 2. `final_report`

```python
final_report: str = ""
```

完整的最终报告。

这个字段之前已经存在，目前 Writer 会写入它。

---

## 3. `charts`

```python
charts: list[dict[str, Any]] = field(default_factory=list)
```

保存图表结果。

它对应新增的：

```python
Chart
```

对象。

可能包含：

```python
{
    "id": "chart-1",
    "title": "市场规模趋势",
    "chart_type": "line",
    "data": {...},
    "image_path": "...",
}
```

当前还没有真正生成图表的 Agent。

---

## 4. `code_executions`

```python
code_executions: list[dict[str, Any]] = field(default_factory=list)
```

保存代码执行记录。

未来 CodeWizard 可能执行分析代码，记录：

```python
{
    "code": "绘图代码",
    "status": "success",
    "output": "...",
    "chart_id": "chart-1",
}
```

这样系统能知道：

```text
执行过什么代码
是否成功
产生了什么输出
```

当前没有 `CodeWizardAgent`，所以还是空列表。

---

## 5. `review`

```python
review: dict[str, Any] = field(default_factory=dict)
```

保存总体审核结果。

例如：

```python
{
    "verdict": "pass",
    "quality_score": 8.0,
    "issues": [],
}
```

当前 Critic 会使用这个字段。

---

## 6. `critic_feedback`

```python
critic_feedback: list[dict[str, Any]] = field(default_factory=list)
```

这是更细致的审核问题列表。

`review` 更像总体结论：

```python
{
    "verdict": "needs_revision",
    "quality_score": 5.0,
}
```

`critic_feedback` 则可以保存每一条具体问题：

```python
[
    {
        "id": "issue-1",
        "target_section": "sec-2",
        "issue_type": "missing_source",
        "severity": "major",
        "description": "关键数据缺少来源",
        "suggestion": "补充官方来源",
        "resolved": False,
    }
]
```

它对应新增的：

```python
CriticFeedback
```

对象。

---

## 7. `unresolved_issues`

```python
unresolved_issues: int = 0
```

表示还有多少审核问题没有解决。

例如：

```python
unresolved_issues = 3
```

表示当前还有三个问题未处理。

它比直接遍历 `critic_feedback` 更方便统计。

---

## 8. `quality_score`

```python
quality_score: float = 0.0
```

报告质量评分。

当前 Critic 使用 0 到 10 的评分：

```python
8.0
```

---

# 七、运行记录字段

## 1. `logs`

```python
logs: list[dict[str, Any]] = field(default_factory=list)
```

保存程序运行日志。

例如：

```python
[
    {
        "agent": "planner",
        "message": "规划完成",
        "timestamp": "...",
    }
]
```

日志主要面向开发者或系统维护者。

---

## 2. `messages`

```python
messages: list[dict[str, Any]] = field(default_factory=list)
```

保存可以展示给用户的进度消息。

例如：

```python
[
    {
        "type": "progress",
        "message": "正在搜索资料",
    }
]
```

它和之前的 `ResearchEvent` 有关系，但不完全一样：

```text
messages 可能保存到任务状态中
events    是工作流向外发送的实时事件
```

当前 `stream()` 主要通过事件发送进度，还没有自动把事件全部写入：

```python
state.messages
```

---

## 3. `errors`

```python
errors: list[str] = field(default_factory=list)
```

保存错误信息。

例如：

```python
[
    "搜索服务暂时不可用",
    "模型返回格式错误",
]
```

当前 Agent 主要直接抛出 `ValueError`，还没有统一把异常写入 `state.errors`。

---

# 八、为什么这次要扩展 `ResearchState`？

因为 V2 研究系统不只是：

```text
搜索 → 写报告
```

还希望逐步支持：

```text
章节规划
→ 研究假设
→ 关键实体
→ 来源和事实
→ 数据分析
→ 洞察
→ 知识图谱
→ 图表
→ 章节写作
→ 审核反馈
→ 修订
```

如果 `ResearchState` 不提前准备这些位置，各个 Agent 就会各自保存数据，最后很难连接起来。

现在所有 Agent 都可以围绕同一个状态对象合作：

```text
Planner 写入 outline、hypotheses
Researcher 写入 sources、raw_sources
FactExtractor 写入 facts、data_points
DataAnalyst 写入 insights、knowledge_graph
CodeWizard 写入 charts、code_executions
Writer 写入 draft_sections、final_report
Critic 写入 review、critic_feedback
```

---

# 九、为什么新增字段仍然使用字典，而不是直接使用 `Section` 等类？

目前代码中写的是：

```python
outline: list[dict[str, Any]]
hypotheses: list[dict[str, Any]]
data_points: list[dict[str, Any]]
charts: list[dict[str, Any]]
```

而不是：

```python
outline: list[Section]
hypotheses: list[Hypothesis]
data_points: list[DataPoint]
charts: list[Chart]
```

这是因为项目目前处于逐步迁移阶段。

注释已经说明：

```python
# 当前仍用字典保存，后续 Planner 会逐步使用 Section。
```

也就是说：

```text
先扩展状态字段
→ 再逐步让 Agent 使用专门的数据类
```

这样学习难度更低，不会一次性修改整个项目。

---

# 十、`test_state.py` 新增测试

## 1. 检查新的初始状态

```python
self.assertEqual(state.outline, [])
self.assertEqual(state.hypotheses, [])
self.assertEqual(
    state.knowledge_graph,
    {"nodes": [], "edges": []},
)
self.assertEqual(state.data_points, [])
self.assertEqual(state.charts, [])
self.assertEqual(state.messages, [])
```

这确认每个新字段创建时都有正确的默认值。

---

## 2. 检查不同任务之间不共享数据

测试把数据加入第一个状态：

```python
first.plan.append(...)
first.outline.append(...)
first.hypotheses.append(...)
first.knowledge_graph["nodes"].append(...)
first.data_points.append(...)
first.charts.append(...)
first.messages.append(...)
```

然后检查第二个状态仍然为空：

```python
self.assertEqual(second.plan, [])
self.assertEqual(second.outline, [])
self.assertEqual(second.hypotheses, [])
self.assertEqual(
    second.knowledge_graph,
    {"nodes": [], "edges": []},
)
self.assertEqual(second.data_points, [])
self.assertEqual(second.charts, [])
self.assertEqual(second.messages, [])
```

这尤其验证了知识图谱的嵌套列表没有共享。

如果默认对象错误地被多个任务共享，就可能出现：

```text
第一个研究任务加入一个节点
第二个研究任务也突然看到了这个节点
```

当前测试确保不会发生这种问题。

---

# 十一、当前实际完成到什么程度？

这次更新主要完成的是：

```text
把 ResearchState 的“档案栏目”补齐
```

但是下面这些功能目前还没有真正实现：

```text
DataAnalystAgent
CodeWizardAgent
真正的数据分析
真正的图表生成
知识图谱自动构建
章节级写作
结构化 CriticFeedback
```

当前已有的工作流仍然主要使用：

```text
Planner
Researcher
FactExtractor
Writer
Critic
```

而且搜索、事实提取、写作和审核仍然使用 Mock 实现。

所以这次不是“系统突然已经会做数据分析和画图了”，而是：

> 先为未来这些功能准备好统一的存储位置和数据结构。

最重要的一句话是：

> 之前的 `ResearchState` 是一个能跑通第一阶段的简化状态；这次把它扩展成能够逐步容纳 V2 研究系统全部信息的状态框架，但新字段大部分还只是准备好了，尚未被具体 Agent 使用。
<!-- ORIGINAL_ASSISTANT_22_3_END -->



<a id="qa-23"></a>
### 记录 23：更新较多的提问（回答在下一记录）

开始时间（北京时间）：2026-10-06 21:05:01。结束时间：2026-10-06 21:05:05。原始记录 ID：`01a11151-4587-7a61-9e43-c9b267f0373e`。

归档注：这条提问的接续回答保留在下一条记录（记录 24）。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_23_1_START -->
```text
详细解释最新更新的那些内容
这次更新的有些多
```
<!-- ORIGINAL_USER_23_1_END -->



<a id="qa-24"></a>
### 记录 24：全链路 V2 字段改名

开始时间（北京时间）：2026-10-06 21:05:08。结束时间：2026-10-06 21:09:53。原始记录 ID：`01a11151-636a-7320-a431-096e315b3ccf`。

归档注：本条没有新的用户消息，是上一条“这次更新的有些多”的接续回答。

#### 原文 1：助手过程说明

<!-- ORIGINAL_ASSISTANT_24_1_START -->
我先重新读取当前项目的最新文件，先确认这次到底新增和修改了哪些内容，再按“小白能跟上的顺序”分层讲解，避免一次把所有代码混在一起。
<!-- ORIGINAL_ASSISTANT_24_1_END -->

#### 原文 2：助手最终回答

<!-- ORIGINAL_ASSISTANT_24_2_START -->
我已经重新读取了最新项目。你说得对，这次更新比较多，而且它不是新增一个单独的小功能，而是一次“全链路统一改名和对齐”。

目前 43 个测试全部通过。

这次最重要的变化，可以先看成下面这张对照表：

| 以前的名称 | 现在的名称 | 含义 |
|---|---|---|
| `state.plan` | `state.outline` | 报告章节大纲 |
| `state.sources` | `state.raw_sources` | 原始搜索来源 |
| `state.review` | `state.review_result` | 审核结果 |
| `plan_ready` | `outline_ready` | 大纲生成完成事件 |
| `event["review"]` | `event["review_result"]` | 事件里的审核结果 |

这不是简单换几个变量名，而是整个 Planner、Researcher、FactExtractor、Writer、Critic、Workflow、命令行脚本和测试一起改了。

---

## 一、为什么把 `plan` 改成 `outline`？

以前 Planner 返回：

```python
{
    "plan": [
        {
            "title": "现状与定义",
            "description": "分析当前情况",
        }
    ]
}
```

现在返回：

```python
{
    "outline": [
        {
            "title": "现状与定义",
            "description": "分析当前情况",
        }
    ]
}
```

`plan` 的意思比较宽泛，可能表示：

```text
准备搜索什么
准备调用哪些 Agent
准备执行哪些步骤
```

而 `outline` 更明确，表示：

```text
最终报告由哪些章节组成
```

例如：

```python
state.outline = [
    {
        "title": "行业概况",
        "description": "介绍行业定义和当前规模",
    },
    {
        "title": "问题与证据",
        "description": "整理行业主要问题和公开数据",
    },
    {
        "title": "趋势与建议",
        "description": "分析未来趋势并提出建议",
    },
]
```

所以现在 Planner 的职责更准确：

```text
用户问题
    ↓
Planner
    ↓
报告章节大纲 + 研究子问题
```

在 [planner.py](D:\课\s4-6\information_deepresearch\backend\app\agents\planner.py) 中，原本的：

```python
plan = self._validate_plan(result.get("plan"))
state.plan = plan
```

已经改成：

```python
outline = self._validate_outline(result.get("outline"))
state.outline = outline
```

验证方法也从：

```python
_validate_plan()
```

改成：

```python
_validate_outline()
```

它仍然会检查：

- 返回值是不是列表；
- 列表是否为空；
- 每一项是不是字典；
- 是否有 `title`；
- 是否有 `description`。

只是现在它表达的是“章节大纲”。

---

## 二、为什么把 `sources` 改成 `raw_sources`？

以前：

```python
state.sources
```

现在：

```python
state.raw_sources
```

`raw` 的意思是：

```text
原始的、未经进一步整理的
```

搜索服务返回的结果可能包含：

```python
{
    "title": "资料标题",
    "url": "https://example.com",
    "snippet": "搜索摘要",
    "query": "搜索问题",
    "content": "资料正文",
}
```

这些结果刚刚搜索回来，还没有经过事实提取、数据分析或筛选，所以称为：

```python
raw_sources
```

现在 Researcher 使用：

```python
collected_sources = list(state.raw_sources)
```

搜索完后保存：

```python
state.raw_sources = self._deduplicate_sources(collected_sources)
```

FactExtractor 也改成从这里读取：

```python
if not state.raw_sources:
    raise ValueError("没有可供事实提取的来源")
```

调用 LLM 时：

```python
"sources": state.raw_sources
```

这里要特别注意：

```python
"sources": state.raw_sources
```

里面的 `"sources"` 只是传给客户端的字典键名，真正的状态字段是：

```python
state.raw_sources
```

也就是说：

```text
状态字段：raw_sources
发送给模型的 payload 字段：sources
```

这是两件事。

这样设计以后，未来可以同时保存：

```python
state.raw_sources
```

原始搜索结果。

```python
state.facts
```

从来源中提取出的事实。

```python
state.data_points
```

从事实中提取出的数字数据。

```python
state.insights
```

从数据中分析出的洞察。

数据会越来越清楚：

```text
原始来源 → 事实 → 数据点 → 洞察
```

---

## 三、为什么把 `review` 改成 `review_result`？

以前：

```python
state.review
```

这个名字太模糊。

它可能被理解为：

```text
正在审核的过程
审核意见
审核结果
```

现在改成：

```python
state.review_result
```

表示：

> Critic 已经完成审核后产生的结果。

例如：

```python
state.review_result = {
    "verdict": "pass",
    "quality_score": 8.0,
    "summary": "报告中的事实都关联了来源。",
    "needs_more_research": False,
    "issues": [],
    "search_queries": [],
}
```

在 Critic 中：

```python
state.review_result = review
```

在 Workflow 中判断：

```python
if state.review_result["verdict"] == "pass":
    break
```

Writer 也读取：

```python
"review_result": state.review_result
```

这样 Writer 在重新写报告时，能知道上一轮审核提出了什么问题。

---

## 四、旧字段被故意删除了

在 [test_state.py](D:\课\s4-6\information_deepresearch\backend\tests\test_state.py) 中有：

```python
self.assertFalse(hasattr(state, "plan"))
self.assertFalse(hasattr(state, "sources"))
self.assertFalse(hasattr(state, "review"))
```

`hasattr()` 是检查对象有没有某个属性。

例如：

```python
hasattr(state, "plan")
```

意思是：

```text
state 里面还有没有 plan 这个字段？
```

现在测试明确要求：

```text
plan 不应该存在
sources 不应该存在
review 不应该存在
```

这是一次有意的“破坏性改名”。

也就是说，以后不能再写：

```python
state.plan
state.sources
state.review
```

否则会报：

```text
AttributeError
```

必须改成：

```python
state.outline
state.raw_sources
state.review_result
```

为什么要删除旧名称？

因为如果新旧字段同时存在：

```python
state.plan
state.outline
```

就可能发生：

```text
Planner 更新了 outline
Writer 却还读取 plan
```

这样两个字段的内容可能不一致。

现在只保留一套名称，能够避免这种混乱。

---

## 五、`ResearchState` 现在保存什么？

最新的 [state.py](D:\课\s4-6\information_deepresearch\backend\app\domain\state.py) 已经变成一个更完整的研究任务档案。

### 规划部分

```python
outline
research_questions
key_entities
hypotheses
mind_map
knowledge_graph
pending_search_queries
```

分别表示：

```text
outline                报告章节大纲
research_questions     具体研究问题
key_entities           关键实体，例如公司、机构、产品
hypotheses             研究假设
mind_map               思维导图
knowledge_graph        知识图谱
pending_search_queries 审核后需要补充搜索的问题
```

知识图谱初始值是：

```python
{
    "nodes": [],
    "edges": [],
}
```

其中：

```text
nodes 代表实体
edges 代表实体之间的关系
```

---

### 证据部分

```python
raw_sources
facts
data_points
insights
references
```

数据流可以理解为：

```text
原始搜索来源
    ↓
事实
    ↓
数据点
    ↓
洞察
```

例如：

```text
raw_sources：
某份行业报告

facts：
报告明确说市场规模增长

data_points：
2025 年市场规模为 120 亿元

insights：
市场规模增长，但增长速度放缓
```

当前代码已经真正使用：

```python
raw_sources
facts
references
```

但：

```python
data_points
insights
```

还只是为未来 DataAnalystAgent 准备的位置。

---

### 写作和审核部分

```python
draft_sections
final_report
charts
code_executions
review_result
critic_feedback
unresolved_issues
quality_score
```

含义是：

```text
draft_sections     每个章节的草稿
final_report       完整报告
charts             图表
code_executions    图表或数据分析代码的执行记录
review_result      总体审核结果
critic_feedback    具体审核问题列表
unresolved_issues  尚未解决的问题数量
quality_score      质量评分
```

---

### 运行记录部分

```python
logs
messages
errors
```

分别用于：

```text
logs       程序运行日志
messages   给用户看的进度消息
errors     错误信息
```

当前事件流仍然主要通过 `ResearchEvent` 发送进度，暂时不会自动把所有事件写入 `state.messages`。

---

## 六、Critic 现在多做了两件事

以前 Critic 只保存：

```python
state.review = review
state.quality_score = review["quality_score"]
```

现在变成：

```python
state.review_result = review
```

然后额外建立审核反馈：

```python
state.critic_feedback = [
    {
        "description": issue,
        "resolved": False,
    }
    for issue in review["issues"]
]
```

假设模型返回：

```python
{
    "issues": [
        "缺少最新行业数据",
        "结论解释不够充分",
    ]
}
```

Critic 会生成：

```python
state.critic_feedback = [
    {
        "description": "缺少最新行业数据",
        "resolved": False,
    },
    {
        "description": "结论解释不够充分",
        "resolved": False,
    },
]
```

然后：

```python
state.unresolved_issues = len(state.critic_feedback)
```

结果是：

```python
state.unresolved_issues == 2
```

这里可以区分：

```text
review_result      一次整体审核的结果
critic_feedback    审核提出的每个具体问题
unresolved_issues  还有多少问题没有解决
```

当前的 `critic_feedback` 还是简化字典，还没有完整使用前面 `models.py` 中的 `CriticFeedback` 类。

---

## 七、Planner、Researcher、FactExtractor、Writer、Critic 现在如何连接？

当前完整流程变成：

```text
用户输入 query
        ↓
创建 ResearchState
        ↓
Planner
        ↓
state.outline
state.research_questions
        ↓
Researcher
        ↓
state.raw_sources
state.references
        ↓
FactExtractor
        ↓
state.facts
        ↓
Writer
        ↓
state.final_report
        ↓
Critic
        ↓
state.review_result
state.critic_feedback
state.unresolved_issues
        ↓
Workflow 判断是否重新搜索或重新写作
```

具体看每一步。

### Planner

Mock LLM 现在返回：

```python
{
    "outline": [...],
    "research_questions": [...],
}
```

Planner 保存：

```python
state.outline = outline
state.research_questions = research_questions
```

### Researcher

优先处理补充搜索问题：

```python
if state.pending_search_queries:
    questions = state.pending_search_queries
else:
    questions = state.research_questions
```

搜索结束后保存：

```python
state.raw_sources = ...
```

### FactExtractor

读取：

```python
state.raw_sources
```

然后生成：

```python
state.facts
```

### Writer

现在要求：

```python
if not state.outline:
    raise ValueError("没有可用于写作的研究大纲")
```

以前检查的是：

```python
state.plan
```

Writer 传给 LLM 的内容也改成：

```python
{
    "query": state.query,
    "outline": state.outline,
    "facts": state.facts,
    "references": state.references,
    "review_result": state.review_result,
    "iteration": state.iteration,
}
```

### Critic

读取：

```python
state.final_report
state.facts
state.raw_sources
```

并将结果写入：

```python
state.review_result
state.critic_feedback
state.unresolved_issues
state.quality_score
```

---

## 八、事件名称也跟着变了

之前事件顺序中有：

```text
plan_ready
```

现在变成：

```text
outline_ready
```

工作流中现在是：

```python
yield self._event(
    state,
    "outline_ready",
    outline=state.outline,
    research_questions=state.research_questions,
)
```

因为现在 Planner 生成的是：

```text
报告章节大纲
```

所以事件也应该叫：

```text
outline_ready
```

研究证据事件现在使用：

```python
source_count=len(state.raw_sources)
sources=state.raw_sources
```

审核完成事件现在发送：

```python
yield self._event(
    state,
    "review_completed",
    review_result=state.review_result,
    critic_feedback=state.critic_feedback,
    quality_score=state.quality_score,
)
```

最终完成事件也包含：

```python
review_result=state.review_result,
critic_feedback=state.critic_feedback,
```

这样外部调用者收到最终事件后，可以同时拿到：

```text
最终报告
引用
审核结果
具体审核问题
质量评分
```

---

## 九、命令行脚本也同步更新了

[run_research.py](D:\课\s4-6\information_deepresearch\backend\app\scripts\run_research.py) 原来读取：

```python
state.plan
state.sources
state.review
```

现在改成：

```python
state.outline
state.raw_sources
state.review_result
```

所以命令行输出的内容仍然一样：

```text
研究计划
搜索来源
结构化事实
最终报告
审核结果
```

只是它从新的状态字段读取数据。

这说明这次不是只改了某一个文件，而是把所有使用旧名称的地方都一起迁移了。

---

## 十、测试为什么改了很多？

这次测试修改的目的，是防止项目只改了一半。

例如 Planner 测试现在检查：

```python
result.outline
```

而不是：

```python
result.plan
```

Researcher 测试检查：

```python
state.raw_sources
```

而不是：

```python
state.sources
```

Critic 测试检查：

```python
state.review_result
```

而不是：

```python
state.review
```

工作流测试检查：

```python
state.outline[0]["title"]
len(state.raw_sources)
state.review_result["verdict"]
```

事件流测试检查：

```python
"outline_ready"
```

以及：

```python
events[-1]["review_result"]["verdict"]
```

状态测试更严格：

```python
self.assertFalse(hasattr(state, "plan"))
self.assertFalse(hasattr(state, "sources"))
self.assertFalse(hasattr(state, "review"))
```

它确保旧字段真的被移除了。

---

## 十一、这次更新和 `models.py` 的关系

之前新增的 [models.py](D:\课\s4-6\information_deepresearch\backend\app\domain\models.py) 定义了：

```python
Section
Hypothesis
DataPoint
Chart
CriticFeedback
```

这次 `ResearchState` 增加了对应的存储位置：

```python
outline
hypotheses
data_points
charts
critic_feedback
```

不过当前仍然保存为字典：

```python
list[dict[str, Any]]
```

还没有改成：

```python
list[Section]
list[Hypothesis]
list[DataPoint]
list[Chart]
list[CriticFeedback]
```

这是因为项目正在分步迁移：

```text
第一步：先统一状态字段名称和位置
第二步：再让 Agent 生成这些结构化对象
第三步：再实现数据分析、图表和更复杂审核
```

---

这次更新的本质是：

```text
原来的第一阶段字段命名
        ↓
统一成 V2 设计中的字段命名
        ↓
所有 Agent、Workflow、事件、命令行和测试同步迁移
```

现在这条链路使用的正式名称是：

```text
Planner 生成 outline
Researcher 写入 raw_sources
FactExtractor 读取 raw_sources 并生成 facts
Writer 使用 outline 和 facts
Critic 写入 review_result 和 critic_feedback
Workflow 根据 review_result 决定是否重做
```

当前最需要记住的三个替换是：

```python
state.plan          → state.outline
state.sources       → state.raw_sources
state.review        → state.review_result
```

这三处是本次更新中最核心、也最容易混淆的变化。
<!-- ORIGINAL_ASSISTANT_24_2_END -->



<a id="qa-25"></a>
### 记录 25：V2 Planner 与章节来源关联

开始时间（北京时间）：2026-10-06 21:15:22。结束时间：2026-10-06 21:32:02。原始记录 ID：`01a1115a-c075-7883-926f-1e725dba8f74`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_25_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_25_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_25_2_START -->
我先重新读取当前项目的最新内容，确认这次又有哪些文件被更新；我会重点找出与上一轮相比真正新增的部分，再分层解释。
<!-- ORIGINAL_ASSISTANT_25_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_25_3_START -->
我先按你的要求重新读取项目当前的最新文件，重点检查最近修改过的 Planner、LLM 客户端、工作流和对应测试，然后再把“这次到底改了什么、为什么改、当前实际是否生效”逐项讲清楚。
<!-- ORIGINAL_ASSISTANT_25_3_END -->

#### 原文 4：助手过程说明

<!-- ORIGINAL_ASSISTANT_25_4_START -->
我已经定位到真正“最新”的修改了：当前工作区最近新增的不是另一个全新 Agent，而是让 Researcher 按“章节大纲里的搜索任务”工作，并把来源归属到章节；同时 Planner 的 Mock 输出开始提供这些搜索词。接下来我会把这部分和刚刚提交的 V2 Planner 结构化改造连起来解释，并跑一遍测试核对实际行为。
<!-- ORIGINAL_ASSISTANT_25_4_END -->

#### 原文 5：助手过程说明

<!-- ORIGINAL_ASSISTANT_25_5_START -->
这次更新的主线已经清楚了：从“列出研究问题再搜索”，变成“先规划报告章节，再为每个章节搜索资料”。我还读到一处衔接：来源的章节编号会继续保留到提取出的事实里，这样后续才知道每条证据属于哪一章。
<!-- ORIGINAL_ASSISTANT_25_5_END -->

#### 原文 6：助手最终回答

<!-- ORIGINAL_ASSISTANT_25_6_START -->
我刚刚重新读取了 `D:\课\s4-6\information_deepresearch` 的最新内容。当前最新修改比上一轮又多了 `fact_extractor.py`，现在这次更新的核心是：

> 从“先列研究问题，再搜索”升级为“先设计报告章节，再为每个章节安排搜索任务，并给每条资料标记所属章节”。

涉及的主要文件：

- [planner.py](D:/课/s4-6/information_deepresearch/backend/app/agents/planner.py:22)
- [llm_client.py](D:/课/s4-6/information_deepresearch/backend/app/core/llm_client.py:50)
- [researcher.py](D:/课/s4-6/information_deepresearch/backend/app/agents/researcher.py:26)
- [fact_extractor.py](D:/课/s4-6/information_deepresearch/backend/app/agents/fact_extractor.py:45)
- [research_workflow.py](D:/课/s4-6/information_deepresearch/backend/app/workflow/research_workflow.py:104)

## 一、先看修改前后的区别

| 修改前 | 修改后 |
|---|---|
| Planner 只生成章节标题和描述 | Planner 生成完整的 `Section` 结构 |
| Researcher 直接遍历 `research_questions` | Researcher 优先遍历每个章节的 `search_queries` |
| 来源只有标题、URL、内容 | 来源还带 `section_id`、`section_title` |
| Fact 只保存来源 URL | Fact 还会继承来源所属章节 |
| `outline_ready` 事件只有大纲和研究问题 | 还包含假设、关键实体、思维导图 |

可以把它想象成写一本书：

以前：

```text
研究问题
  ├── 搜索问题 1
  ├── 搜索问题 2
  └── 搜索问题 3
```

现在：

```text
研究报告
  ├── 第一章：现状与定义
  │     └── 搜索：当前现状、关键定义
  ├── 第二章：问题与证据
  │     └── 搜索：主要问题、公开证据
  └── 第三章：趋势与建议
        └── 搜索：未来趋势、改进建议
```

## 二、Planner 现在做了什么

### 1. Planner 不再只生成简单字典

现在 Planner 会读取 LLM 返回结果：

```python
result = await self.llm.complete_json(...)
```

然后分别处理：

```python
outline = self._validate_outline(result.get("outline"))
hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
research_questions = self._validate_questions(
    result.get("research_questions")
)
key_entities = self._validate_key_entities(
    result.get("key_entities", [])
)
```

也就是说，Planner 现在会处理四类内容：

- `outline`：报告章节
- `hypotheses`：待验证假设
- `research_questions`：研究子问题
- `key_entities`：重要实体

最后写回共享状态：

```python
state.outline = outline
state.hypotheses = hypotheses
state.research_questions = research_questions
state.key_entities = key_entities
state.mind_map = result.get("mind_map", {})
```

这些数据仍然放在同一个 `ResearchState` 对象里。

---

### 2. `outline` 现在使用 `Section` 模板

以前可能只是：

```python
{
    "title": "现状与定义",
    "description": "介绍当前情况"
}
```

现在会创建一个 `Section`：

```python
section = Section(
    id="sec_1",
    title="现状与定义",
    description="明确研究范围和当前现状",
    section_type="mixed",
    status="pending",
    requires_data=False,
    requires_chart=False,
    priority=1,
    search_queries=["当前现状和关键定义"],
)
```

然后转换成普通字典：

```python
validated.append(section.to_dict())
```

这里要特别注意：

> 当前代码虽然使用了 `Section` 对象进行校验，但最终放入 `state.outline` 的仍然是字典，不是 `Section` 对象。

原因是当前 `ResearchState` 定义的是：

```python
outline: list[dict[str, Any]]
```

这样更方便后续转成 JSON、事件或 API 响应。

`Section` 的作用更像一张统一的表格模板，保证每个章节都具有稳定格式。

---

### 3. 每个章节多了 `search_queries`

这部分是本次很重要的变化：

```python
search_queries = item.get("search_queries", [title])
```

意思是：

- 如果 LLM 给了这个章节的搜索词，就使用它们；
- 如果没有，就退回使用章节标题；
- 如果列表为空，也退回使用章节标题。

例如：

```python
{
    "id": "sec_1",
    "title": "现状与定义",
    "description": "...",
    "search_queries": [
        "新能源汽车行业当前现状",
        "新能源汽车行业关键定义"
    ]
}
```

一个章节可以有多个搜索词。

这样 Researcher 就不会只搜索一个模糊问题，而是能围绕这个章节收集多组资料。

---

### 4. 新增假设 `hypotheses`

Mock Planner 现在会返回：

```python
{
    "id": "h_1",
    "content": "行业趋势会受到政策和市场需求共同影响。",
    "status": "unverified"
}
```

`status` 允许的值有：

```text
unverified             尚未验证
supported              得到证据支持
refuted                被证据推翻
partially_supported    部分得到支持
```

刚开始 Planner 只能说：

> 这是一个需要后续搜索验证的猜想。

它还不能直接说这个假设是真的。

当前阶段只有 Planner 创建假设，Researcher 和 Critic 还没有真正更新假设状态。

---

### 5. 新增 `key_entities` 和 `mind_map`

`key_entities` 用来存放重要对象，例如：

```python
[
    "比亚迪",
    "新能源汽车",
    "国家政策"
]
```

代码允许两种输入：

```python
["新能源汽车", "比亚迪"]
```

或者：

```python
[
    {"name": "新能源汽车"},
    {"name": "比亚迪"}
]
```

最后统一成：

```python
["新能源汽车", "比亚迪"]
```

不过当前 Mock LLM 返回的是：

```python
"key_entities": []
```

所以这个功能目前只是接口和数据格式已经准备好了。

`mind_map` 也只是直接保存：

```python
state.mind_map = result.get("mind_map", {})
```

目前还没有进一步校验它的内部结构。

## 三、MockLLMClient 为什么也要修改

[llm_client.py](D:/课/s4-6/information_deepresearch/backend/app/core/llm_client.py:50) 中的 Mock Planner 现在增加了：

```python
"search_queries": [
    f"{query} 的当前现状和关键定义"
]
```

每个章节都有自己的搜索词。

这是因为 `PlannerAgent` 只是调用 LLM，它并不自己创造研究内容：

```text
PlannerAgent
    ↓ 调用
LLMClient
    ↓ 返回
outline、hypotheses、search_queries
```

真实 LLM 以后也应该返回类似结构。

当前的 `MockLLMClient` 不联网，也不具备真正理解能力。它只是按照固定模板返回结果，用来测试代码流程。

## 四、Researcher 现在最大的变化

[researcher.py](D:/课/s4-6/information_deepresearch/backend/app/agents/researcher.py:26) 以前大概是：

```python
for question in state.research_questions:
    await self.search.search(question)
```

现在变成了先创建搜索任务。

### 1. 如果有补充搜索任务

```python
if state.pending_search_queries:
```

说明 Critic 之前认为资料不够，需要补充搜索。

这时会创建：

```python
{
    "query": "2025年新能源汽车行业数据",
    "section_id": "",
    "section_title": ""
}
```

因为当前 Critic 只告诉了它一个搜索词，并没有告诉它属于哪一章。

---

### 2. 如果没有补充任务，就根据章节大纲创建任务

```python
tasks = self._build_search_tasks(state)
```

`_build_search_tasks()` 会遍历：

```python
for section in state.outline:
```

读取：

```python
section_id = section.get("id")
section_title = section.get("title")
queries = section.get("search_queries")
```

然后生成：

```python
{
    "query": "新能源汽车行业当前现状和关键定义",
    "section_id": "sec_1",
    "section_title": "现状与定义"
}
```

如果一个章节有两个搜索词，就会生成两个任务。

例如：

```python
state.outline = [
    {
        "id": "sec-market",
        "title": "市场规模",
        "search_queries": [
            "市场规模 2024",
            "市场规模 2025"
        ]
    }
]
```

会生成两个搜索任务，而不是只使用第一个。

---

### 3. 搜索结果现在会带章节信息

搜索得到 `SearchResult` 后：

```python
source = result.to_dict()
```

如果这个任务属于某个章节：

```python
source["section_id"] = task["section_id"]
source["section_title"] = task["section_title"]
```

于是原来的来源：

```python
{
    "title": "...",
    "url": "...",
    "content": "..."
}
```

现在变成：

```python
{
    "title": "...",
    "url": "...",
    "content": "...",
    "section_id": "sec_1",
    "section_title": "现状与定义"
}
```

这相当于给每份资料贴了一个标签：

> 这份资料是为报告的“现状与定义”章节找的。

---

### 4. 搜索结果仍然会去重

```python
state.raw_sources = self._deduplicate_sources(collected_sources)
```

去重规则是 URL：

```python
unique[url] = source
```

同一个 URL 只保留第一次出现的来源。

当前的 MockSearchClient 根据搜索词生成不同 URL，所以三个章节通常会得到三个来源。

但实际搜索时可能出现这种情况：

```text
第一章找到 example.com/a
第二章也找到 example.com/a
```

当前实现会只保留一次，而且保留它第一次出现时的章节标签。这是现在的一个限制。

## 五、FactExtractor 的最新变化

这是刚刚新增的修改，位于 [fact_extractor.py](D:/课/s4-6/information_deepresearch/backend/app/agents/fact_extractor.py:45)。

以前 FactExtractor 只保留：

```python
{
    "content": "...",
    "source_title": "...",
    "source_url": "...",
    "confidence": 0.7
}
```

现在它先建立一个“URL 到来源”的对应表：

```python
source_by_url = {
    source["url"]: source
    for source in sources
}
```

例如：

```python
{
    "https://example.com/a": {
        "section_id": "sec_1",
        "section_title": "现状与定义"
    }
}
```

FactExtractor 生成事实时，先检查：

```python
if source_url not in allowed_urls:
    raise ValueError(...)
```

意思是：

> 事实引用的 URL 必须确实存在于原始搜索来源中。

然后通过 URL 找回来源：

```python
source_context = source_by_url[source_url]
```

把章节信息复制到事实中：

```python
fact["section_id"] = source_context["section_id"]
fact["section_title"] = source_context["section_title"]
```

所以现在数据可以这样传递：

```text
来源 Source
  ├── section_id = sec_1
  └── section_title = 现状与定义
          ↓
事实 Fact
  ├── source_url = 同一个 URL
  ├── section_id = sec_1
  └── section_title = 现状与定义
```

需要注意：

> 这次并没有让 FactExtractor 变得更“聪明”，它只是把已有的章节标签从来源复制到事实中。

它仍然依赖 `MockLLMClient` 返回事实。

## 六、Workflow 和事件也同步扩展了

[research_workflow.py](D:/课/s4-6/information_deepresearch/backend/app/workflow/research_workflow.py:104) 中的 `outline_ready` 事件现在多了：

```python
hypotheses=state.hypotheses,
key_entities=state.key_entities,
mind_map=state.mind_map,
```

所以这个事件现在大致包含：

```python
{
    "type": "outline_ready",
    "outline": [...],
    "research_questions": [...],
    "hypotheses": [...],
    "key_entities": [...],
    "mind_map": {}
}
```

这只是把更多信息通知给外部调用者，并不会创建新的状态对象。

整体实际流程是：

```text
ResearchState
    ↓
Planner
    ↓
outline + search_queries + hypotheses
    ↓
Researcher
    ↓
raw_sources + section_id
    ↓
FactExtractor
    ↓
facts + section_id
    ↓
Writer
    ↓
final_report
    ↓
Critic
    ↓
review_result
```

## 七、当前代码实际运行时的例子

以：

```text
新能源汽车行业趋势
```

为例，当前 Mock 流程大概会产生：

```text
sec_1：现状与定义
搜索：新能源汽车行业趋势的当前现状和关键定义

sec_2：问题与证据
搜索：新能源汽车行业趋势的主要问题和公开证据

sec_3：趋势与建议
搜索：新能源汽车行业趋势的未来趋势和改进建议
```

Researcher 搜索后：

```text
来源 A → sec_1
来源 B → sec_2
来源 C → sec_3
```

FactExtractor 后：

```text
事实 A → sec_1
事实 B → sec_2
事实 C → sec_3
```

但是当前 Writer 的 Mock 实现还没有真正按照章节组织报告。它主要是把事实列表拼接成 Markdown。

所以：

> 章节归属现在已经被保存了，但 Writer 还没有充分使用这些信息。

这说明这次更新主要是在为后续功能打基础，例如：

- 每章单独写作；
- 每章引用不同来源；
- 每章生成图表；
- Critic 针对具体章节提出问题。

## 八、当前哪些是真功能，哪些仍是 Mock

目前已经真正实现的：

- Planner 输出结构化章节；
- 章节包含多个搜索词；
- Researcher 按章节搜索；
- 来源带章节信息；
- 事实继承章节信息；
- 来源按 URL 去重；
- 事件流输出新增字段；
- 数据格式校验；
- 审核失败后的补充搜索循环。

目前仍然是模拟的：

- `MockLLMClient` 不是真实大模型；
- `MockSearchClient` 不是真实联网搜索；
- FactExtractor 不是智能事实抽取；
- Writer 不是复杂报告生成；
- Critic 的判断规则很简单；
- 还没有真正的 FastAPI SSE；
- `DataPoint`、`Chart` 等模型还没有接入实际 Agent；
- 补充搜索目前没有章节归属；
- `mind_map` 目前没有严格校验。

我重新运行了整个测试套件：

```text
Ran 44 tests
OK
```

说明当前这些修改在现有测试范围内是可以运行的。
<!-- ORIGINAL_ASSISTANT_25_6_END -->



<a id="qa-26"></a>
### 记录 26：章节草稿写作

开始时间（北京时间）：2026-10-06 22:15:05。结束时间：2026-10-06 22:22:58。原始记录 ID：`01a11191-6c50-7ed0-a92d-41a6c5b5be55`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_26_1_START -->
```text
详细解释最新更新的那些内容 比上一次更新的内容

```
<!-- ORIGINAL_USER_26_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_26_2_START -->
我先重新读取当前项目，专门找出“上一次讲解之后又新增/修改了什么”，然后只讲这次相对上一版的差异，避免把已经讲过的内容重复一遍。
<!-- ORIGINAL_ASSISTANT_26_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_26_3_START -->
我已经确认：上一次讲解的“来源按章节关联”现在已经正式提交；这一次真正新增的重点是“Writer 开始逐章写草稿，再把各章草稿整合成最终报告”。我正在用最新测试和一次实际运行结果核对这条新链路。
<!-- ORIGINAL_ASSISTANT_26_3_END -->

#### 原文 4：助手最终回答

<!-- ORIGINAL_ASSISTANT_26_4_START -->
我刚刚重新读取了最新版本。和上一次相比，最重要的新变化是：

> 上一次已经实现了“资料属于哪个章节”；这一次 Writer 真正开始“按章节分别写草稿，再合并成最终报告”。

当前最新提交是 `0387dc8 feat: add section level drafting`。

## 一、和上一次相比，核心变化是什么

| 部分 | 上一次 | 这一次 |
|---|---|---|
| Researcher | 按章节搜索，并给来源添加 `section_id` | 基本不变，之前的修改正式提交 |
| FactExtractor | 给事实添加章节信息 | 基本不变，并增加测试 |
| Writer | 把所有事实一次性写成报告 | 先逐章写草稿，再整合报告 |
| `draft_sections` | State 中只是预留的空字典 | 现在真正被 Writer 填充 |
| `draft_ready` 事件 | 主要包含完整报告 | 还包含章节大纲和各章草稿 |
| Mock LLM | 只有一种写作模板 | 增加 `section` 和 `report` 两种写作模式 |

相关文件：

- [writer.py](D:/课/s4-6/information_deepresearch/backend/app/agents/writer.py:19)
- [llm_client.py](D:/课/s4-6/information_deepresearch/backend/app/core/llm_client.py:134)
- [research_workflow.py](D:/课/s4-6/information_deepresearch/backend/app/workflow/research_workflow.py:123)

---

## 二、以前 Writer 是怎么工作的

之前的 Writer 大致是：

```text
所有 facts
    ↓
调用一次 LLM
    ↓
final_report
```

也就是说，所有事实一起交给 LLM：

```python
report = await self.llm.complete_text(
    role=self.name,
    payload={
        "query": state.query,
        "outline": state.outline,
        "facts": state.facts,
        ...
    },
)
```

以前 Writer 不会分别处理：

```text
sec_1 的事实
sec_2 的事实
sec_3 的事实
```

它只会把所有事实整体写成一篇报告。

---

## 三、现在 Writer 的工作方式

现在变成了两步：

```text
每个章节分别生成草稿
    ↓
把所有章节草稿合并成最终报告
```

假设有三个章节：

```text
sec_1：现状与定义
sec_2：问题与证据
sec_3：趋势与建议
```

Writer 会执行：

```text
调用 LLM 写 sec_1
调用 LLM 写 sec_2
调用 LLM 写 sec_3
调用 LLM 合并三个章节
```

所以现在有 3 个章节时，一次写作阶段会调用 4 次 `complete_text()`。

---

## 四、Writer 的第一部分：准备章节草稿

代码首先创建两个变量：

```python
draft_sections: dict[str, str] = {}
normalized_outline: list[dict] = []
```

它们分别表示：

### `draft_sections`

保存每一章的草稿：

```python
{
    "sec_1": "第一章正文...",
    "sec_2": "第二章正文...",
    "sec_3": "第三章正文..."
}
```

### `normalized_outline`

保存处理后的章节大纲：

```python
[
    {
        "id": "sec_1",
        "title": "现状与定义",
        "status": "drafted"
    }
]
```

这里的 `normalized` 可以理解成：

> 把章节格式整理成统一格式。

---

## 五、Writer 如何找到某个章节对应的事实

代码：

```python
related_facts = self._facts_for_section(
    state.facts,
    section_id,
)
```

`_facts_for_section()` 会按照 `section_id` 筛选事实：

```python
related = [
    fact
    for fact in facts
    if str(fact.get("section_id", "")).strip() == section_id
]
```

例如：

```python
state.facts = [
    {
        "content": "A 事实",
        "section_id": "sec-a"
    },
    {
        "content": "B 事实",
        "section_id": "sec-b"
    }
]
```

处理 `sec-a` 时，只会得到：

```python
[
    {
        "content": "A 事实",
        "section_id": "sec-a"
    }
]
```

处理 `sec-b` 时，只会得到：

```python
[
    {
        "content": "B 事实",
        "section_id": "sec-b"
    }
]
```

这样就不会把 B 章节的事实写进 A 章节。

测试也专门验证了这一点：

```python
self.assertIn("A 事实", state.draft_sections["sec-a"])
self.assertNotIn("B 事实", state.draft_sections["sec-a"])
```

---

## 六、如果某个章节没有对应事实怎么办

代码是：

```python
return related or facts
```

意思是：

- 如果找到了属于当前章节的事实，就只使用这些事实；
- 如果一个都没找到，就退回使用全部事实。

例如：

```text
sec_1 有事实
sec_2 没有事实
```

那么：

- sec_1 使用自己的事实；
- sec_2 没有专属事实时，会暂时使用全部事实。

这是一个兼容策略，避免某个章节完全没有内容。

但它也意味着：

> 当前实现还不能严格保证每一章都只使用本章资料。

以后可以改成没有对应事实时只生成“当前没有足够证据”，而不是使用全部事实。

---

## 七、什么是 `unassigned_facts`

代码还会找出没有章节归属的事实：

```python
unassigned_facts = [
    fact
    for fact in state.facts
    if str(fact.get("section_id", "")).strip()
    not in outline_ids
]
```

例如：

```python
{
    "content": "一条旧数据",
    "section_id": ""
}
```

它没有归属任何章节，就属于 `unassigned_facts`。

当前代码会把这些没有归属的事实放到第一章：

```python
if index == 1 and unassigned_facts:
    related_facts = self._merge_facts(
        related_facts,
        unassigned_facts,
    )
```

这样做主要是为了兼容以前没有章节标签的旧数据。

---

## 八、Writer 如何生成单个章节

代码调用：

```python
section_content = await self.llm.complete_text(
    role=self.name,
    payload={
        "mode": "section",
        "query": state.query,
        "section": section,
        "facts": related_facts,
        ...
    },
)
```

这里新增了：

```python
"mode": "section"
```

这个字段的作用是告诉 LLM 客户端：

> 这次不是要写整篇报告，而是只写一个章节。

传进去的内容包括：

- 当前研究问题；
- 当前章节；
- 当前章节相关事实；
- 数据点；
- 洞察；
- 图表；
- 审核意见；
- 当前迭代次数。

在 MockLLMClient 中，如果发现：

```python
payload.get("mode") == "section"
```

就会返回类似：

```text
本章节围绕“现状与定义”整理研究证据。

- 事实一（来源链接）
- 事实二（来源链接）
```

注意：

> 当前 Mock 并没有真正理解章节内容，只是按照固定模板拼接文字。

---

## 九、章节写完后，状态发生了什么变化

生成章节后：

```python
section["status"] = "drafted"
```

这表示：

```text
pending → drafted
```

以前 Planner 创建章节时，默认状态是：

```text
pending
```

现在 Writer 写完后变成：

```text
drafted
```

然后保存：

```python
draft_sections[section_id] = section_content
normalized_outline.append(section)
```

最后：

```python
state.outline = normalized_outline
state.draft_sections = draft_sections
```

所以当前实际状态会变成：

```python
state.draft_sections = {
    "sec_1": "...第一章草稿...",
    "sec_2": "...第二章草稿...",
    "sec_3": "...第三章草稿..."
}
```

而：

```python
state.outline[0]["status"] == "drafted"
```

这说明 `draft_sections` 以前只是预留字段，现在真正被使用了。

---

## 十、Writer 的第二部分：合并整篇报告

所有章节草稿生成后，Writer 再调用一次 LLM：

```python
report = await self.llm.complete_text(
    role=self.name,
    payload={
        "mode": "report",
        "query": state.query,
        "outline": normalized_outline,
        "facts": state.facts,
        "draft_sections": draft_sections,
        ...
    },
)
```

这次：

```python
"mode": "report"
```

意思是：

> 现在要把所有章节草稿合并成最终报告。

MockLLMClient 会依次生成：

```markdown
## 执行摘要

...

## 研究发现

### 1. 现状与定义

第一章草稿内容

### 2. 问题与证据

第二章草稿内容

### 3. 趋势与建议

第三章草稿内容

## 结论
```

所以现在最终报告中的章节标题，不是 Writer 的 Python 代码直接写死的，而是 MockLLMClient 根据 `outline` 和 `draft_sections` 组合出来的。

---

## 十一、为什么要增加 `mode`

`complete_text()` 还是同一个函数：

```python
await self.llm.complete_text(...)
```

但是它现在有两种用途：

```text
mode="section" → 写单个章节
mode="report"  → 合并完整报告
```

可以把 `mode` 理解成一张说明纸：

```python
{
    "mode": "section"
}
```

告诉客户端：

> 请写章节。

或者：

```python
{
    "mode": "report"
}
```

告诉客户端：

> 请整合报告。

以后换成真实 LLM 时，也可以根据不同模式使用不同提示词。

---

## 十二、工作流事件发生了什么变化

以前的 `draft_ready` 事件主要包含：

```python
{
    "report": state.final_report,
    "revision": False
}
```

现在增加了：

```python
{
    "report": state.final_report,
    "outline": state.outline,
    "draft_sections": state.draft_sections,
    "revision": False
}
```

这意味着前端或其他调用者可以看到：

```text
完整报告
第一章草稿
第二章草稿
第三章草稿
```

而不仅仅是最后拼好的报告。

如果是审核后重新写作，事件中会变成：

```python
"revision": True
```

表示这是修订版草稿。

事件顺序没有改变：

```text
research_started
phase_started
outline_ready
phase_started
research_evidence_ready
phase_started
draft_ready
phase_started
review_completed
research_completed
```

只是 `draft_ready` 里面的数据更多了。

---

## 十三、审核修订时有什么变化

如果 Critic 认为报告需要修改：

```text
Critic
  ↓
Writer 再次运行
```

现在 Writer 不只是重新生成一篇完整报告，而是：

```text
重新生成每个章节草稿
    ↓
重新合并成完整报告
```

如果 Critic 提供了审核问题：

```python
state.review_result["issues"]
```

这些内容会同时传给：

- 每个章节的写作请求；
- 最终报告的整合请求。

所以后续真实 LLM 可以针对每一章分别修改。

---

## 十四、测试为什么要修改

以前测试可能统计：

```python
len(llm.writer_payloads) == 2
```

因为两次写作就只有两次调用：

```text
第一次写作：1 次
第二次修订：1 次
```

现在每次写作有：

```text
3 次章节写作 + 1 次整合报告 = 4 次调用
```

所以测试不能简单统计所有 Writer 调用，而是筛选：

```python
payload.get("mode") == "report"
```

这样只统计真正的“整合报告”调用。

新增测试还验证了：

- `draft_sections` 包含 `sec_1`、`sec_2`、`sec_3`；
- 所有章节状态变成 `drafted`；
- 每个章节的事实没有串到其他章节；
- `draft_ready` 事件包含章节草稿。

当前测试结果：

```text
Ran 45 tests
OK
```

---

## 十五、这次更新仍然没有实现什么

虽然 Writer 现在按章节工作了，但以下仍然是预留状态：

- 仍然使用 `MockLLMClient`；
- 仍然使用 `MockSearchClient`；
- 章节内容仍然是固定模板；
- `DataAnalystAgent` 还没有实现；
- `CodeWizardAgent` 还没有实现；
- `data_points`、`insights`、`charts` 目前只是传给 Writer；
- 还没有真实图表；
- 还没有 FastAPI；
- 还没有真正的 SSE；
- Critic 还没有对每个章节单独审核；
- `reviewed` 和 `final` 章节状态还没有真正使用。

最准确地说，这次更新完成的是：

```text
资料按章节归类
    ↓
事实按章节归类
    ↓
草稿按章节生成
    ↓
章节草稿合并成报告
```

但“真正理解内容、判断事实、生成高质量报告”仍然要等真实 LLM 和后续 Agent 接入。
<!-- ORIGINAL_ASSISTANT_26_4_END -->



<a id="qa-27"></a>
### 记录 27：事件公共外壳校验

开始时间（北京时间）：2026-10-06 22:28:43。结束时间：2026-10-06 22:33:50。原始记录 ID：`01a1119d-e59b-7553-88aa-c97b9f4c1d34`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_27_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_27_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_27_2_START -->
我先重新读取项目当前内容，比较上一次讲解之后新增的提交和文件变化，再只解释这次最新增加的部分。
<!-- ORIGINAL_ASSISTANT_27_2_END -->

#### 原文 3：助手最终回答

<!-- ORIGINAL_ASSISTANT_27_3_START -->
我刚刚重新读取了项目最新内容。和上一次“按章节生成草稿”的更新相比，这一次新增的核心是：

> 给研究事件增加统一的格式检查，防止工作流发布错误的事件。

最新提交是：

```text
99fe715 feat: validate research event envelope
```

主要修改：

- [events.py](D:/课/s4-6/information_deepresearch/backend/app/domain/events.py:14)
- [test_events.py](D:/课/s4-6/information_deepresearch/backend/tests/test_events.py:11)

## 一、先理解“事件”是什么

工作流执行过程中会不断发布进度：

```text
研究开始
规划开始
大纲完成
搜索完成
草稿完成
审核完成
研究完成
```

每一个进度通知就是一个事件，例如：

```python
{
    "type": "outline_ready",
    "session_id": "session-001",
    "phase": "planning",
    "iteration": 0,
    "outline": [...]
}
```

可以把事件理解成一张“进度通知单”。

这张通知单有两部分：

```text
固定外壳：type、session_id、phase、iteration
具体内容：outline、report、facts 等
```

这次更新主要检查的是固定外壳，所以提交信息里叫：

```text
validate research event envelope
```

`envelope` 就是“信封、外层格式”的意思。

---

## 二、以前的问题是什么

以前创建事件时，代码直接接受任何值：

```python
ResearchEvent(
    type="随便写",
    session_id="",
    phase="不存在的阶段",
    iteration=-1,
    data="错误数据",
)
```

虽然 Python 可以创建这个对象，但它实际上已经不是一个合法的研究事件了。

问题可能会延迟到很后面才出现：

```text
工作流发布错误事件
    ↓
事件被传给前端
    ↓
前端无法识别
    ↓
才发现问题
```

这次修改后，事件在创建时就会检查：

```text
错误事件
    ↓
立即抛出 ValueError
```

这样更容易定位错误。

---

## 三、新增了 `ResearchEventType`

代码：

```python
class ResearchEventType:
    RESEARCH_STARTED = "research_started"
    PHASE_STARTED = "phase_started"
    OUTLINE_READY = "outline_ready"
    RESEARCH_EVIDENCE_READY = "research_evidence_ready"
    DRAFT_READY = "draft_ready"
    REVIEW_COMPLETED = "review_completed"
    RESEARCH_COMPLETED = "research_completed"
```

它的作用是集中保存所有合法事件类型。

以前可能直接写：

```python
"outline_ready"
```

现在也可以写：

```python
ResearchEventType.OUTLINE_READY
```

这样做的好处是：

1. 不需要到处手写字符串；
2. 不容易把 `"outline_ready"` 拼成 `"outlie_ready"`；
3. 所有事件名称集中在一个地方；
4. IDE 更容易提示这些可用选项。

它目前不是 Python 的 `Enum`，只是一个保存字符串常量的类。

---

## 四、`EVENT_TYPES` 是什么

代码：

```python
EVENT_TYPES = frozenset(
    {
        ResearchEventType.RESEARCH_STARTED,
        ResearchEventType.PHASE_STARTED,
        ResearchEventType.OUTLINE_READY,
        ResearchEventType.RESEARCH_EVIDENCE_READY,
        ResearchEventType.DRAFT_READY,
        ResearchEventType.REVIEW_COMPLETED,
        ResearchEventType.RESEARCH_COMPLETED,
    }
)
```

运行后，它大致相当于：

```python
{
    "research_started",
    "phase_started",
    "outline_ready",
    "research_evidence_ready",
    "draft_ready",
    "review_completed",
    "research_completed",
}
```

它用来判断：

```python
self.type in EVENT_TYPES
```

也就是：

> 当前事件类型是不是系统允许的类型？

### 为什么使用 `frozenset`

`frozenset` 是“不可修改的集合”。

普通集合：

```python
event_types = {"a", "b"}
event_types.add("c")
```

可以被修改。

`frozenset`：

```python
event_types = frozenset({"a", "b"})
```

创建后不能添加或删除元素。

这里使用它，是因为合法事件类型应该是固定规则，不希望程序运行过程中随意改变。

---

## 五、新增了 `RESEARCH_PHASES`

代码：

```python
RESEARCH_PHASES = frozenset(
    {
        "init",
        "planning",
        "researching",
        "analyzing",
        "writing",
        "reviewing",
        "re_researching",
        "revising",
        "completed",
    }
)
```

它定义了研究任务可能处于哪些阶段。

例如：

```text
init          刚创建
planning      规划中
researching   搜索和整理资料
writing       写作中
reviewing     审核中
revising      修订中
completed     已完成
```

现在事件的 `phase` 必须属于这个集合。

例如：

```python
ResearchEvent(
    type="phase_started",
    session_id="session-001",
    phase="planning",
)
```

是合法的。

但是：

```python
ResearchEvent(
    type="phase_started",
    session_id="session-001",
    phase="random",
)
```

会报错：

```text
ValueError: 不支持的研究阶段: 'random'
```

---

## 六、`__post_init__` 是这次最重要的部分

代码：

```python
def __post_init__(self) -> None:
```

你可以把它理解成：

> `dataclass` 对象刚刚创建完成之后，自动执行的检查函数。

当执行：

```python
event = ResearchEvent(
    type="outline_ready",
    session_id="session-001",
    phase="planning",
)
```

Python 会先给对象赋值，然后自动调用：

```python
event.__post_init__()
```

这次新增的所有检查都在这里。

---

## 七、检查事件类型

```python
if not isinstance(self.type, str) or self.type not in EVENT_TYPES:
    raise ValueError(
        f"不支持的研究事件类型: {self.type!r}"
    )
```

分成两个条件：

### 第一部分

```python
not isinstance(self.type, str)
```

检查 `type` 是不是字符串。

错误例子：

```python
type=123
```

### 第二部分

```python
self.type not in EVENT_TYPES
```

检查字符串是不是合法事件类型。

错误例子：

```python
type="unknown"
```

如果不合法，就停止创建对象：

```python
raise ValueError(...)
```

---

## 八、检查 `session_id`

```python
if not isinstance(self.session_id, str) or not self.session_id.strip():
    raise ValueError("研究事件 session_id 不能为空")
```

`session_id` 是一次研究任务的身份编号。

例如：

```python
"session-001"
```

它可以帮助系统区分不同研究任务：

```text
任务 A → session-001
任务 B → session-002
```

这次要求：

- 必须是字符串；
- 不能是空字符串；
- 不能只有空格。

以下都会失败：

```python
session_id=""
session_id="   "
session_id=None
```

---

## 九、检查研究阶段

```python
if not isinstance(self.phase, str) or self.phase not in RESEARCH_PHASES:
    raise ValueError(
        f"不支持的研究阶段: {self.phase!r}"
    )
```

这和事件类型检查类似。

必须满足：

```text
phase 是字符串
并且属于 RESEARCH_PHASES
```

这样可以防止工作流出现拼写错误，例如：

```python
phase="reseaching"
```

少写了一个 `r`，会被立刻发现。

---

## 十、检查 `iteration`

代码：

```python
if isinstance(self.iteration, bool) or not isinstance(self.iteration, int):
    raise ValueError("研究事件 iteration 必须是整数")

if self.iteration < 0:
    raise ValueError("研究事件 iteration 不能小于 0")
```

`iteration` 表示审核和修订进行了第几轮。

例如：

```text
0：第一次研究
1：第一次修订
2：第二次修订
```

它必须是：

```python
0
1
2
```

不能是：

```python
-1
1.5
"1"
```

这里有一个 Python 初学者可能不知道的细节：

```python
isinstance(True, int)
```

结果其实是 `True`。

因为 Python 中：

```python
bool 是 int 的特殊子类
```

如果只写：

```python
isinstance(self.iteration, int)
```

那么：

```python
iteration=True
```

会被错误地当成整数。

所以代码先专门排除：

```python
isinstance(self.iteration, bool)
```

这是一种比较严谨的写法。

---

## 十一、检查 `data`

代码：

```python
if not isinstance(self.data, dict):
    raise ValueError("研究事件 data 必须是字典")
```

事件中的额外信息放在 `data` 中：

```python
data={
    "outline": [...],
    "facts": [...]
}
```

它必须是字典。

合法：

```python
data={"outline": []}
```

不合法：

```python
data=[]
data="文本"
data=None
```

不过要注意：

> 当前只检查 `data` 是不是字典，还没有检查不同事件必须包含哪些字段。

例如：

```python
ResearchEvent(
    type="outline_ready",
    session_id="session-001",
    phase="planning",
    data={}
)
```

目前仍然可能通过。

因为它只检查外层格式，不检查每种事件的具体内容。

---

## 十二、`@dataclass(frozen=True)` 现在有什么意义

当前定义是：

```python
@dataclass(frozen=True)
class ResearchEvent:
```

`frozen=True` 表示事件对象创建以后，不能重新给字段赋值：

```python
event.type = "another_type"
```

会报错。

为什么事件需要不可修改？

因为事件代表：

> 某个时间点已经发生的事情。

例如：

```text
22:00:00 研究开始
22:00:01 大纲完成
22:00:02 搜索完成
```

如果事件创建以后还可以随意修改，就可能出现：

```text
原本记录的是“大纲完成”
后来被改成“研究完成”
```

这会让事件记录不可靠。

### 一个重要细节

`frozen=True` 只保护对象字段本身，不能完全冻结内部字典：

```python
event.data["new_key"] = "value"
```

这类嵌套修改仍可能发生。

不过当前 `to_dict()` 使用了：

```python
deepcopy(self.data)
```

所以输出结果会复制一份独立数据，避免调用者直接修改事件内部数据。

---

## 十三、`to_dict()` 现在没有改变核心职责

代码：

```python
def to_dict(self) -> dict[str, Any]:
    event = {
        "type": self.type,
        "session_id": self.session_id,
        "phase": self.phase,
        "iteration": self.iteration,
    }
    event.update(deepcopy(self.data))
    return event
```

它把事件对象转换成普通字典。

例如：

```python
ResearchEvent(
    type="outline_ready",
    session_id="session-001",
    phase="planning",
    iteration=0,
    data={"outline": [{"id": "sec-1"}]},
).to_dict()
```

结果是：

```python
{
    "type": "outline_ready",
    "session_id": "session-001",
    "phase": "planning",
    "iteration": 0,
    "outline": [
        {"id": "sec-1"}
    ]
}
```

这里：

```python
event.update(deepcopy(self.data))
```

表示把 `data` 中的字段展开到事件最外层。

所以不是：

```python
{
    "type": "outline_ready",
    "data": {
        "outline": [...]
    }
}
```

而是：

```python
{
    "type": "outline_ready",
    "outline": [...]
}
```

这样调用方可以直接写：

```python
event["outline"]
event["report"]
event["references"]
```

---

## 十四、工作流现在如何使用这个验证

工作流中的 `_event()`：

```python
return ResearchEvent(
    type=event_type,
    session_id=state.session_id,
    phase=phase or state.phase,
    iteration=state.iteration,
    data=data,
).to_dict()
```

完整过程是：

```text
_workflow._event(...)
        ↓
创建 ResearchEvent
        ↓
自动执行 __post_init__()
        ↓
验证 type、session_id、phase、iteration、data
        ↓
调用 to_dict()
        ↓
发布普通字典事件
```

因此，工作流原来的代码基本不用改：

```python
yield self._event(
    state,
    "outline_ready",
    outline=state.outline,
)
```

但现在这条事件会自动经过统一验证。

这就是一个很好的设计：

> 工作流负责“什么时候发布事件”；ResearchEvent 负责“事件格式是否合法”。

两个职责分开了。

---

## 十五、这次新增了哪些测试

新增了 [test_events.py](D:/课/s4-6/information_deepresearch/backend/tests/test_events.py:11)，主要测试七件事：

1. 合法事件类型已经注册；
2. `to_dict()` 可以正确展开数据；
3. 非法事件类型会报错；
4. 空 `session_id` 会报错；
5. 非法阶段会报错；
6. 负数迭代次数会报错；
7. `data` 不是字典会报错。

例如：

```python
with self.assertRaisesRegex(ValueError, "事件类型"):
    ResearchEvent("unknown", "session-001", "planning")
```

意思是：

> 运行代码时应该抛出 `ValueError`，并且错误信息中应该包含“事件类型”。

---

## 十六、当前测试结果

我重新运行了整个测试套件：

```text
Ran 52 tests
OK
```

说明这次事件格式校验和之前的所有功能都能一起通过。

## 十七、这次更新实际完成了什么

当前事件链路变成：

```text
工作流准备发布事件
        ↓
ResearchEvent 统一检查格式
        ↓
格式正确 → 转成字典并发布
格式错误 → 立即抛出 ValueError
```

这次更新解决的是：

- 事件名称写错；
- 研究阶段写错；
- 会话 ID 为空；
- 迭代次数为负数；
- 事件数据不是字典；
- 事件外层结构不统一。

但它还没有实现：

- 真正的 FastAPI；
- 真正的 SSE；
- 事件持久化到数据库；
- 对每种事件的数据内容做严格检查；
- 前端接收和展示事件。

所以现在最准确的说法是：

> 项目还没有接入真正的 SSE，但已经把未来 SSE 要发送的事件格式先固定并验证好了。
<!-- ORIGINAL_ASSISTANT_27_3_END -->



<a id="qa-28"></a>
### 记录 28：必需字段和公共字段保护

开始时间（北京时间）：2026-10-06 22:41:01。结束时间：2026-10-06 22:49:29。原始记录 ID：`01a111a9-294f-78b2-89c1-efe71a280b9b`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_28_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_28_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_28_2_START -->
我先重新读取当前项目，确认上一次事件格式校验之后又有哪些最新提交和文件变化，再只解释这次新增加的内容。
<!-- ORIGINAL_ASSISTANT_28_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_28_3_START -->
这次是在上一版的基础上继续加检查：以前只检查事件的“外壳”是否合法，现在还检查每种事件有没有带齐必需的数据字段。不过它目前只检查字段是否存在，不检查报告是不是空的、评分是不是数字；我会把这个区别讲清楚。
<!-- ORIGINAL_ASSISTANT_28_3_END -->

#### 原文 4：助手过程说明

<!-- ORIGINAL_ASSISTANT_28_4_START -->
目录在我读取期间又有了更新：除了“必需字段不能遗漏”，现在还增加了“业务数据不能覆盖任务编号、事件类型等公共字段”的保护，文档也同步调整了迭代进度。我会把这两项新检查一起解释，测试也按刚读到的版本重新运行。
<!-- ORIGINAL_ASSISTANT_28_4_END -->

#### 原文 5：助手最终回答

<!-- ORIGINAL_ASSISTANT_28_5_START -->
我重新读取了当前最新版本。和上一次相比，这次更新主要增加了两层保护：

1. 每种事件必须带有自己规定的业务字段；
2. 业务字段不能覆盖事件公共字段。

当前测试为：

```text
Ran 55 tests
OK
```

## 一、上一次只检查“事件外壳”

之前已经有这些公共字段：

```python
{
    "type": "outline_ready",
    "session_id": "session-001",
    "phase": "planning",
    "iteration": 0
}
```

它们可以理解为每张事件通知单都必须有的固定信息：

- `type`：这是什么事件；
- `session_id`：属于哪次研究任务；
- `phase`：当前处于哪个阶段；
- `iteration`：第几次研究或修订。

上一次的代码只检查：

```text
type 是否合法
session_id 是否为空
phase 是否合法
iteration 是否为非负整数
data 是否为字典
```

但它不知道不同事件里面还应该有什么具体内容。

例如：

```python
ResearchEvent(
    type="outline_ready",
    session_id="session-001",
    phase="planning",
    data={}
)
```

以前可能可以通过，但实际上 `outline_ready` 没有提供大纲，信息是不完整的。

---

## 二、新增 `EVENT_REQUIRED_FIELDS`

最新代码增加了：

```python
EVENT_REQUIRED_FIELDS = {
    ResearchEventType.RESEARCH_STARTED:
        frozenset({"query", "max_iterations"}),

    ResearchEventType.PHASE_STARTED:
        frozenset({"agent"}),

    ResearchEventType.OUTLINE_READY:
        frozenset({
            "outline",
            "research_questions",
            "hypotheses",
            "key_entities",
            "mind_map",
        }),

    ResearchEventType.RESEARCH_EVIDENCE_READY:
        frozenset({
            "supplementary",
            "source_count",
            "fact_count",
            "sources",
            "facts",
            "references",
        }),

    ResearchEventType.DRAFT_READY:
        frozenset({
            "report",
            "outline",
            "draft_sections",
            "revision",
        }),

    ResearchEventType.REVIEW_COMPLETED:
        frozenset({
            "review_result",
            "critic_feedback",
            "quality_score",
        }),

    ResearchEventType.RESEARCH_COMPLETED:
        frozenset({
            "report",
            "quality_score",
            "references",
            "review_result",
            "critic_feedback",
        }),
}
```

位置：

[events.py](D:/课/s4-6/information_deepresearch/backend/app/domain/events.py:52)

这相当于给每种事件制定了“必填表格”。

---

## 三、每种事件现在必须带什么

### 1. `research_started`

```python
{
    "query": "...",
    "max_iterations": 1
}
```

表示研究刚开始，所以至少要知道：

- 用户研究什么；
- 最多允许几次审核修订。

工作流中的代码：

```python
yield self._event(
    state,
    "research_started",
    query=state.query,
    max_iterations=state.max_iterations,
)
```

---

### 2. `phase_started`

```python
{
    "agent": "planner"
}
```

表示某个阶段开始了，需要知道由哪个 Agent 执行。

例如：

```python
{
    "type": "phase_started",
    "phase": "planning",
    "agent": "planner"
}
```

---

### 3. `outline_ready`

```python
{
    "outline": [...],
    "research_questions": [...],
    "hypotheses": [...],
    "key_entities": [...],
    "mind_map": {}
}
```

表示 Planner 已经完成研究规划。

这些字段分别表示：

- 报告章节；
- 研究子问题；
- 待验证假设；
- 关键实体；
- 思维导图数据。

即使某些内容为空，也必须把字段放进去：

```python
"hypotheses": []
```

不能直接省略。

---

### 4. `research_evidence_ready`

```python
{
    "supplementary": False,
    "source_count": 3,
    "fact_count": 3,
    "sources": [...],
    "facts": [...],
    "references": [...]
}
```

表示搜索和事实提取完成。

它必须告诉外部调用者：

- 这是不是补充搜索；
- 找到了多少来源；
- 提取了多少事实；
- 来源列表；
- 事实列表；
- 引用列表。

---

### 5. `draft_ready`

```python
{
    "report": "...",
    "outline": [...],
    "draft_sections": {...},
    "revision": False
}
```

表示 Writer 已经完成报告草稿。

这里对应上一次新增的章节写作功能：

```python
state.draft_sections = {
    "sec_1": "第一章草稿",
    "sec_2": "第二章草稿",
    "sec_3": "第三章草稿",
}
```

---

### 6. `review_completed`

```python
{
    "review_result": {...},
    "critic_feedback": [...],
    "quality_score": 8.0
}
```

表示 Critic 审核完成。

必须带：

- 审核结论；
- 具体审核意见；
- 质量评分。

---

### 7. `research_completed`

```python
{
    "report": "...",
    "quality_score": 8.0,
    "references": [...],
    "review_result": {...},
    "critic_feedback": [...]
}
```

表示整条研究流程结束。

最终事件必须包含：

- 最终报告；
- 质量评分；
- 参考文献；
- 最终审核结果；
- 审核反馈。

---

## 四、代码如何检查字段是否缺失

新增代码：

```python
missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()
```

这句对初学者来说可以拆成三步。

假设当前事件是 `outline_ready`：

```python
EVENT_REQUIRED_FIELDS[self.type]
```

得到：

```python
{
    "outline",
    "research_questions",
    "hypotheses",
    "key_entities",
    "mind_map"
}
```

如果实际传入：

```python
self.data = {
    "outline": []
}
```

那么：

```python
self.data.keys()
```

得到：

```python
{"outline"}
```

两者做集合差集：

```text
规定必须有的字段 - 实际已有的字段
```

结果就是：

```python
{
    "research_questions",
    "hypotheses",
    "key_entities",
    "mind_map"
}
```

然后：

```python
if missing_fields:
```

只要缺少字段，就抛出错误：

```python
raise ValueError(
    f"{self.type} 缺少必需字段: {missing}"
)
```

例如：

```text
outline_ready 缺少必需字段:
hypotheses, key_entities, mind_map, research_questions
```

这就是这次更新的核心逻辑。

---

## 五、最新又增加了什么：防止覆盖公共字段

当前文件中还增加了：

```python
EVENT_ENVELOPE_FIELDS = frozenset({
    "type",
    "session_id",
    "phase",
    "iteration",
})
```

位置：

[events.py](D:/课/s4-6/information_deepresearch/backend/app/domain/events.py:75)

这些是事件的公共字段。

然后在 `__post_init__()` 中检查：

```python
reserved_fields = EVENT_ENVELOPE_FIELDS & self.data.keys()
```

这里的 `&` 是集合交集。

意思是：

```text
公共字段集合
和
业务 data 字段集合
有没有重复字段
```

如果重复：

```python
if reserved_fields:
```

就报错：

```python
raise ValueError(
    f"研究事件 data 不能覆盖公共字段: {reserved}"
)
```

---

## 六、为什么必须防止覆盖公共字段

看一下 `to_dict()`：

```python
event = {
    "type": self.type,
    "session_id": self.session_id,
    "phase": self.phase,
    "iteration": self.iteration,
}

event.update(deepcopy(self.data))
```

`update()` 的意思是把 `data` 加入 `event`。

但是如果 `data` 里也有同名字段：

```python
data={
    "agent": "planner",
    "session_id": "other-session"
}
```

执行后：

```python
event = {
    "type": "phase_started",
    "session_id": "session-001",
    "phase": "planning",
    "iteration": 0,
    "agent": "planner",
    "session_id": "other-session"
}
```

字典不能有两个相同的 `session_id`，后面的值会覆盖前面的值。

最终结果变成：

```python
"session_id": "other-session"
```

这就很危险，因为这个事件明明属于：

```text
session-001
```

却被业务数据改成了：

```text
other-session
```

所以现在提前禁止：

```python
data={
    "session_id": "other-session"
}
```

测试代码：

```python
def test_event_data_cannot_replace_common_fields(self):
    with self.assertRaisesRegex(ValueError, "session_id"):
        ResearchEvent(
            ResearchEventType.PHASE_STARTED,
            "session-001",
            "planning",
            data={
                "agent": "planner",
                "session_id": "other-session",
            },
        )
```

这可以理解为：

> 事件公共字段归系统管理，业务数据不能抢占这些字段的名字。

---

## 七、现在事件的完整检查顺序

当前 `ResearchEvent` 创建时，大致按这个顺序检查：

```text
1. type 是否是字符串
2. type 是否属于合法事件类型
3. session_id 是否为空
4. phase 是否属于合法研究阶段
5. iteration 是否为整数
6. iteration 是否小于 0
7. data 是否为字典
8. data 是否覆盖公共字段
9. data 是否缺少当前事件的必需字段
10. 检查通过后才能转换成普通字典
```

流程可以表示为：

```text
工作流调用 _event()
        ↓
创建 ResearchEvent
        ↓
检查公共字段
        ↓
检查字段覆盖
        ↓
检查事件专属字段
        ↓
to_dict()
        ↓
发布事件
```

---

## 八、这次检查仍然没有检查字段类型

当前代码只检查：

```text
字段有没有出现
```

不检查：

```text
字段里面的值是否正确
```

例如下面这个事件目前可能通过：

```python
ResearchEvent(
    type="draft_ready",
    session_id="session-001",
    phase="writing",
    data={
        "report": None,
        "outline": 123,
        "draft_sections": None,
        "revision": "错误类型",
    },
)
```

因为这些字段都存在。

但从业务角度，它们明显不合理：

```text
report 应该是字符串
outline 应该是列表
draft_sections 应该是字典
revision 应该是布尔值
```

所以当前实现属于：

```text
第一层：检查字段是否存在
```

还没有实现：

```text
第二层：检查每个字段的具体类型
```

这通常会在后续使用 Pydantic、TypedDict 或专门的数据模型时继续加强。

---

## 九、文档也同步变化了

[README.md](D:/课/s4-6/information_deepresearch/README.md) 现在把 iteration-02 写成：

```text
iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
```

以前是：

```text
iteration-02（进行中）
```

现在去掉“进行中”，说明作者认为这一阶段的主要目标已经完成。

文档还补充说明：

```text
所有事件都有 type、session_id、phase 和 iteration；
每种事件的必需业务字段见 events.py 中的 EVENT_REQUIRED_FIELDS。
```

这相当于把事件协议正式写进项目说明。

---

## 十、路线图也调整了

`docs/v2-core-contract.md` 中：

以前：

```text
iteration-03：增加章节大纲、假设驱动研究、数据点和知识图谱基础
```

现在：

```text
iteration-03：增加假设驱动研究、数据点和知识图谱基础
```

因为章节大纲已经在 iteration-02 中完成，不再属于未来任务。

以前：

```text
iteration-06：对齐章节写作、引用和结构化审核反馈
```

现在：

```text
iteration-06：完善章节写作、引用和结构化审核反馈
```

因为章节写作的基础版本已经实现，后面是继续完善，而不是从零开始。

---

## 十一、当前这次更新的真正意义

到目前为止，事件协议已经从：

```text
只规定事件外壳
```

变成：

```text
规定事件外壳
+ 规定每种事件必须有什么字段
+ 防止业务数据覆盖公共字段
```

可以类比成填写表格：

```text
第一版：
只检查表格格式像不像表格

第二版：
还规定每种表格必须填哪些栏目

最新版本：
还禁止普通栏目覆盖表格编号和日期等系统字段
```

最终的事件流现在更稳定：

```text
research_started
    必须有 query、max_iterations

phase_started
    必须有 agent

outline_ready
    必须有 outline、research_questions、hypotheses、key_entities、mind_map

research_evidence_ready
    必须有 sources、facts、references 等

draft_ready
    必须有 report、outline、draft_sections、revision

review_completed
    必须有 review_result、critic_feedback、quality_score

research_completed
    必须有最终报告、引用和审核结果
```

这仍然不是实际的 SSE，也没有前端和数据库，但它已经为未来的 API/SSE 接口建立了稳定的事件契约。
<!-- ORIGINAL_ASSISTANT_28_5_END -->



<a id="qa-29"></a>
### 记录 29：iteration-02 正式收尾

开始时间（北京时间）：2026-10-06 22:50:29。结束时间：2026-10-06 22:54:15。原始记录 ID：`01a111b1-d432-7d63-8175-2e282e2b87c2`。

#### 原文 1：用户消息

<!-- ORIGINAL_USER_29_1_START -->
```text
详细解释最新更新的那些内容

```
<!-- ORIGINAL_USER_29_1_END -->

#### 原文 2：助手过程说明

<!-- ORIGINAL_ASSISTANT_29_2_START -->
我先重新读取当前项目，确认上一次事件协议更新之后是否又有新的提交、文件或未提交修改，然后只解释最新增加的部分。
<!-- ORIGINAL_ASSISTANT_29_2_END -->

#### 原文 3：助手过程说明

<!-- ORIGINAL_ASSISTANT_29_3_START -->
我确认了：当前最新提交是 `79db291`，它主要不是新增 Agent，而是把上一轮已经实现的事件协议保护正式收尾，并把 iteration-02 标记为完成。我会重点解释“这次为什么叫完成契约、代码层和文档层分别完成了什么”，避免把上一轮已经讲过的逻辑当成新功能。
<!-- ORIGINAL_ASSISTANT_29_3_END -->

#### 原文 4：助手最终回答

<!-- ORIGINAL_ASSISTANT_29_4_START -->
我重新读取了当前最新版本。严格来说，这次最新更新不是新增一个 Agent 或研究阶段，而是：

> 正式完成 `iteration-02`，把事件协议保护和相关文档收尾。

当前最新提交：

```text
79db291 chore: complete iteration 02 contract
```

所有测试：

```text
Ran 55 tests
OK
```

## 一、这次更新和上一次的关系

上一轮已经实现了：

- 每种事件必须有规定的业务字段；
- 事件数据不能覆盖 `session_id` 等公共字段；
- 事件协议有统一格式。

这次提交主要把这些内容正式整理、提交，并标记：

```text
iteration-02 已完成
```

所以这次没有新增 Planner、Researcher、Writer 等业务流程。

---

## 二、`chore: complete iteration 02 contract` 是什么意思

提交信息里的：

```text
chore
```

通常表示：

> 工程整理、配置、文档或收尾工作。

它和：

```text
feat
```

不同。

`feat` 通常表示新增功能，例如：

```text
新增按章节写作
新增事件校验
```

而这次的 `chore` 说明：

```text
前面的功能已经基本完成，现在整理版本边界和文档
```

---

## 三、`iteration-02` 被正式标记为完成

README 现在写的是：

```text
iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
```

位置：

[README.md](D:/课/s4-6/information_deepresearch/README.md:18)

之前是：

```text
iteration-02（进行中）
```

现在去掉了“进行中”，表示项目作者认为这一阶段已经达到验收标准。

这一阶段实际完成了这些事情：

```text
研究状态字段对齐 V2
        ↓
章节大纲结构化
        ↓
来源关联章节
        ↓
事实关联章节
        ↓
按章节生成草稿
        ↓
固定事件格式
        ↓
验证事件字段
```

---

## 四、这次代码层面最重要的保护

当前事件文件中有：

```python
EVENT_ENVELOPE_FIELDS = frozenset({
    "type",
    "session_id",
    "phase",
    "iteration",
})
```

位置：

[events.py](D:/课/s4-6/information_deepresearch/backend/app/domain/events.py:72)

这些字段属于事件公共外壳。

然后在 `ResearchEvent.__post_init__()` 中检查：

```python
reserved_fields = EVENT_ENVELOPE_FIELDS & self.data.keys()
```

这里的 `&` 是集合交集，意思是：

```text
公共字段
和
业务 data 字段
有没有重名
```

例如：

```python
ResearchEvent(
    type="phase_started",
    session_id="session-001",
    phase="planning",
    data={
        "agent": "planner",
        "session_id": "other-session",
    },
)
```

`data` 中出现了：

```python
"session_id"
```

它和事件外层的 `session_id` 重复了。

如果不拦截，`to_dict()` 中的：

```python
event.update(deepcopy(self.data))
```

可能让业务数据覆盖公共字段。

最终可能变成：

```python
{
    "type": "phase_started",
    "session_id": "other-session",
    "phase": "planning",
    "iteration": 0,
    "agent": "planner",
}
```

这会导致事件原本属于：

```text
session-001
```

却被错误改成：

```text
other-session
```

现在会直接报错：

```text
研究事件 data 不能覆盖公共字段: session_id
```

这是一种数据保护。

---

## 五、事件字段现在有两层规则

当前事件检查分为两层。

### 第一层：公共字段

所有事件都必须有：

```text
type
session_id
phase
iteration
```

这些字段描述：

```text
这是什么事件
属于哪个任务
任务处于什么阶段
第几轮研究
```

### 第二层：事件专属字段

不同事件还必须有不同的数据。

例如 `draft_ready`：

```python
{
    "report",
    "outline",
    "draft_sections",
    "revision",
}
```

例如 `research_completed`：

```python
{
    "report",
    "quality_score",
    "references",
    "review_result",
    "critic_feedback",
}
```

所以现在不是“所有事件都只要有同样几个字段”，而是：

```text
公共字段统一
+
每种事件有自己的必需字段
```

---

## 六、事件协议在 README 中被正式记录

README 新增说明：

```text
所有事件都有 type、session_id、phase 和 iteration；
每种事件的必需业务字段见 events.py 中的 EVENT_REQUIRED_FIELDS。
```

位置：

[README.md](D:/课/s4-6/information_deepresearch/README.md:49)

这意味着以后开发者不需要猜：

```text
draft_ready 应该返回什么？
review_completed 应该返回什么？
```

可以直接查看：

```python
EVENT_REQUIRED_FIELDS
```

这就是“固定进度事件协议”。

---

## 七、路线图发生了调整

在 [v2-core-contract.md](D:/课/s4-6/information_deepresearch/docs/v2-core-contract.md:83) 中，后续迭代任务被重新整理。

### iteration-03

以前：

```text
增加章节大纲、假设驱动研究、数据点和知识图谱基础
```

现在：

```text
增加假设驱动研究、数据点和知识图谱基础
```

为什么删除“章节大纲”？

因为章节大纲已经完成了：

- Planner 已经生成 `outline`；
- Section 已经定义；
- Researcher 已经按章节搜索；
- Writer 已经按章节写草稿。

因此章节大纲不再是未来任务。

### iteration-06

以前：

```text
对齐章节写作、引用和结构化审核反馈
```

现在：

```text
完善章节写作、引用和结构化审核反馈
```

这里从“对齐”改成“完善”，说明章节写作的基础版本已经有了，后面只是继续增强。

---

## 八、Git 标签是什么意思

当前日志显示：

```text
79db291 (HEAD -> iteration-02, tag: iteration-02)
```

这表示：

- `HEAD`：当前代码就在这个提交；
- `iteration-02`：当前本地分支名称；
- `tag: iteration-02`：这个提交还被打了一个版本标签。

可以把 tag 理解成书签：

```text
项目代码不断变化
        ↓
给某个稳定节点贴标签
        ↓
以后可以快速找到 iteration-02 完成时的代码
```

所以现在可以把这个版本理解为：

```text
iteration-02 完成版
```

这不是 Python 代码执行出来的东西，而是 Git 对项目版本的管理。

---

## 九、这次更新没有改变什么

这次没有新增：

- 新 Agent；
- 新搜索逻辑；
- 新写作逻辑；
- 真实 LLM；
- 真实搜索；
- FastAPI；
- SSE；
- 数据库；
- 前端。

当前仍然是：

```text
MockLLMClient
MockSearchClient
Python 内部事件流
```

真正的 FastAPI SSE 仍然属于后面的：

```text
iteration-07
```

---

## 十、当前项目阶段的准确理解

现在项目已经完成了 iteration-02 的基础契约：

```text
状态结构统一
    ↓
章节结构统一
    ↓
来源和事实可以追踪到章节
    ↓
章节草稿可以单独保存
    ↓
工作流事件格式固定
    ↓
事件缺字段会报错
    ↓
业务数据不能覆盖公共字段
```

所以这次更新的重点不是“研究能力变强了”，而是：

> 项目的数据结构和对外事件接口变得稳定，可以开始进入下一阶段的假设、数据点、知识图谱和分析功能。
<!-- ORIGINAL_ASSISTANT_29_4_END -->



<a id="archive-corrections"></a>
## 五、版本区别与校订注释

本节不是对旧回答的替换，而是把读完固定源码后确认的边界单独列出。旧回答仍在上一节原样保留。

### 1. Python 类型写法不是运行时万能验证

`@dataclass` 主要自动生成构造方法和表示方法；`Literal`、类型注解和 `ABC` 帮助表达设计意图，但不会自动保证所有传入值都正确。当前项目中真正的运行时拒绝来自显式 `if`、`raise ValueError`、事件契约校验和测试。`default_factory` 能让默认列表/字典各自独立，但不会深拷贝调用者显式传入的对象。

### 2. 状态共享来自编排器反复传同一对象

Planner、Researcher、FactExtractor、Writer、Critic 修改的是 Workflow 传下去的同一个 `ResearchState` 实例；这不是因为 dataclass 自动提供了“共享状态”能力。`frozen`（项目领域模型没有普遍使用）也不等于深度冻结，嵌套列表仍可能变化；`asdict` 也不保证任意 `Any` 值一定能 JSON 序列化。

### 3. 接口与异步行为的实际边界

`BaseAgent` 的抽象成员要求具体类提供成员，但不会严格检查参数签名是否完全一致，也不会因为写了 `async` 注解就替调用者并行执行。当前 Agent 和 SearchClient 是顺序 `await`；没有自动并行搜索。`run` 与 `stream` 每次调用都会创建自己的任务；内部异步生成器是事件生成器，不是逐 token 的 SSE 实现。`stream` 不被消费时，生成器内部工作也不会完成。

### 4. Planner 与领域对象的校验边界

Planner 的结构化结果经过手写验证后才转换为 Section / 字典；并未自动验证所有业务规则，例如 ID 唯一、priority 非负或 priority 的排序方向。当前 priority 也不参与排序，不能把它解释成已经实现的“越大越重要”。

### 5. 来源、事实与 Mock 的边界

URL 在来源列表中，只说明事实引用了一个已收集的 URL，不等于联网确认了事实真实。`confidence=0.7` 是 Mock 的固定值。FactExtractor 是“把模型返回的候选事实按允许来源和字段规则整理入状态”，不是凭字符串自动证明客观真相。i2 之后的假设证据功能里，Mock 会把事实统一标成支持第一个假设；正反证据同时存在时没有综合权衡逻辑，状态结果可能受处理顺序影响。

### 6. Critic、completed 与修订次数

Critic 的 Mock 检查很有限：事实/来源非空、报告含 `http`，并给固定的 8/4 分数。`completed` 表示 Workflow 结束，不等于 Critic 一定通过；达到最大迭代次数也可能在最后一次仍是 `needs_revision`。`max_iterations=1` 通常表示初稿审核后最多再修订一次，不是只审核一次。异常传播也不保证自动写入 `state.errors`。

### 7. 章节和事件的实际行为

章节来源筛选有“找不到归属时回退全部 facts”的限制；重复 URL 去重保留第一次的章节标签。章节正文存于 `draft_sections`，`outline.content` 不会同步更新；完成时章节通常仍保留 `drafted` 阶段。`critic_feedback` 记录的是描述和 resolved 状态，不是完整的 CriticFeedback 对象；审核时通常重建列表。事件不是每写完一章就发一个，当前主要在阶段完成及整合后发事件；公共字段校验不代表 SSE 网络协议已经实现。

### 8. 版本计数与正式边界

`fad4cdb` 的静态测试数是 54，`79db291` 是 55；此前回答若因实时未提交内容而说“55”，应以本档案第八节固定提交结果为准。i2 后的 `fccf339` 只作为第九节补充，不能倒灌进 i2。

<a id="archive-diffs"></a>
## 六、全部 Git 文件差异

以下 26 个节点按时间顺序提供完整 patch。合并节点按第一父提交比较；`0a892dc` 因此明确显示无工作树差异。没有用省略号替代任何 patch 内容。

<a id="diff-2b63f68"></a>
### 提交 2b63f68：chore: initialize learning project

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..88b348e
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1,7 @@
+__pycache__/
+*.py[cod]
+.venv/
+.env
+node_modules/
+dist/
+*.log
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..23b7f87
--- /dev/null
+++ b/README.md
@@ -0,0 +1,22 @@
+# Industry DeepResearch 学习项目
+
+这是从原行业信息助手项目重新搭建的学习版。
+
+## 学习目标
+
+逐步实现一个完整的 DeepResearch 后端链路：
+
+```text
+用户问题 -> 研究规划 -> 信息搜索 -> 证据整理 -> 报告撰写 -> 质量审核
+```
+
+第一阶段只关注代码结构和数据流，不加入数据库、Docker、登录和复杂前端。
+
+## 当前迭代
+
+- iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
+- 后续迭代：加入结构化数据分析、图表、检查点、本地知识库和简化前端。
+
+## 学习方式
+
+每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。
````

<a id="diff-5c13222"></a>
### 提交 5c13222：feat: add shared research state

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/__init__.py b/backend/app/__init__.py
new file mode 100644
index 0000000..7ba15f5
--- /dev/null
+++ b/backend/app/__init__.py
@@ -0,0 +1 @@
+"""Information DeepResearch backend package."""
diff --git a/backend/app/domain/__init__.py b/backend/app/domain/__init__.py
new file mode 100644
index 0000000..63657ea
--- /dev/null
+++ b/backend/app/domain/__init__.py
@@ -0,0 +1 @@
+"""Domain models used by the research workflow."""
diff --git a/backend/app/domain/state.py b/backend/app/domain/state.py
new file mode 100644
index 0000000..8b9d21c
--- /dev/null
+++ b/backend/app/domain/state.py
@@ -0,0 +1,45 @@
+"""DeepResearch 的共享工作状态。
+
+第一轮先用一个普通 dataclass 表达状态。
+后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象，
+这样可以清楚看到信息如何在研究流程中流动。
+"""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+from typing import Any
+from uuid import uuid4
+
+
+@dataclass
+class ResearchState:
+    """一次研究任务从开始到结束所需要的全部核心数据。"""
+
+    # 用户输入和任务身份
+    query: str
+    session_id: str = field(default_factory=lambda: str(uuid4()))
+
+    # 当前阶段：init / planning / researching / writing / reviewing / completed
+    phase: str = "init"
+
+    # 审核循环次数
+    iteration: int = 0
+    max_iterations: int = 1
+
+    # 规划结果
+    plan: list[dict[str, Any]] = field(default_factory=list)
+    research_questions: list[str] = field(default_factory=list)
+
+    # 研究证据
+    sources: list[dict[str, Any]] = field(default_factory=list)
+    facts: list[dict[str, Any]] = field(default_factory=list)
+    references: list[dict[str, Any]] = field(default_factory=list)
+
+    # 写作和审核结果
+    final_report: str = ""
+    review: dict[str, Any] = field(default_factory=dict)
+    quality_score: float = 0.0
+
+    # 错误记录
+    errors: list[str] = field(default_factory=list)
diff --git a/backend/tests/__init__.py b/backend/tests/__init__.py
new file mode 100644
index 0000000..e9af0eb
--- /dev/null
+++ b/backend/tests/__init__.py
@@ -0,0 +1 @@
+"""Tests for the learning backend."""
diff --git a/backend/tests/test_state.py b/backend/tests/test_state.py
new file mode 100644
index 0000000..14c6b3b
--- /dev/null
+++ b/backend/tests/test_state.py
@@ -0,0 +1,27 @@
+import unittest
+
+from app.domain.state import ResearchState
+
+
+class ResearchStateTests(unittest.TestCase):
+    def test_state_starts_empty(self):
+        state = ResearchState("测试问题")
+
+        self.assertEqual(state.query, "测试问题")
+        self.assertEqual(state.phase, "init")
+        self.assertEqual(state.plan, [])
+        self.assertEqual(state.sources, [])
+        self.assertEqual(state.facts, [])
+
+    def test_mutable_fields_are_not_shared(self):
+        first = ResearchState("第一个问题")
+        second = ResearchState("第二个问题")
+
+        first.plan.append({"title": "只属于第一个任务"})
+
+        self.assertEqual(len(first.plan), 1)
+        self.assertEqual(second.plan, [])
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-3c5fca4"></a>
### 提交 3c5fca4：feat: add base research agent

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/__init__.py b/backend/app/agents/__init__.py
new file mode 100644
index 0000000..feb1554
--- /dev/null
+++ b/backend/app/agents/__init__.py
@@ -0,0 +1 @@
+"""Research agents used by the workflow."""
diff --git a/backend/app/agents/base.py b/backend/app/agents/base.py
new file mode 100644
index 0000000..cee4c66
--- /dev/null
+++ b/backend/app/agents/base.py
@@ -0,0 +1,22 @@
+"""所有研究 Agent 共享的最小接口。"""
+
+from __future__ import annotations
+
+from abc import ABC, abstractmethod
+
+from app.domain.state import ResearchState
+
+
+class BaseAgent(ABC):
+    """Agent 的基础约定。
+
+    每个具体 Agent 只需要实现 ``run``：读取当前状态，完成自己的工作，
+    再返回更新后的状态。这样工作流不需要知道每个 Agent 的内部细节。
+    """
+
+    name: str = "base"
+
+    @abstractmethod
+    async def run(self, state: ResearchState) -> ResearchState:
+        """处理一次研究状态。"""
+        raise NotImplementedError
diff --git a/backend/tests/test_base_agent.py b/backend/tests/test_base_agent.py
new file mode 100644
index 0000000..6be16e3
--- /dev/null
+++ b/backend/tests/test_base_agent.py
@@ -0,0 +1,33 @@
+import asyncio
+import unittest
+
+from app.agents.base import BaseAgent
+from app.domain.state import ResearchState
+
+
+class DemoAgent(BaseAgent):
+    name = "demo"
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        state.phase = "demo_completed"
+        return state
+
+
+class BaseAgentTests(unittest.TestCase):
+    def test_concrete_agent_updates_and_returns_state(self):
+        state = ResearchState("测试问题")
+        agent = DemoAgent()
+
+        result = asyncio.run(agent.run(state))
+
+        self.assertIs(result, state)
+        self.assertEqual(result.phase, "demo_completed")
+        self.assertEqual(agent.name, "demo")
+
+    def test_base_agent_cannot_be_instantiated_directly(self):
+        with self.assertRaises(TypeError):
+            BaseAgent()
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-72a6f09"></a>
### 提交 72a6f09：feat: add llm client abstraction

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/core/__init__.py b/backend/app/core/__init__.py
new file mode 100644
index 0000000..964ac6c
--- /dev/null
+++ b/backend/app/core/__init__.py
@@ -0,0 +1 @@
+"""外部服务和基础设施适配器。"""
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
new file mode 100644
index 0000000..f6c7263
--- /dev/null
+++ b/backend/app/core/llm_client.py
@@ -0,0 +1,85 @@
+"""统一的大模型客户端接口。
+
+Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
+当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
+"""
+
+from __future__ import annotations
+
+from abc import ABC, abstractmethod
+from typing import Any
+
+
+class LLMClient(ABC):
+    """所有 LLM 客户端都必须提供的能力。"""
+
+    @abstractmethod
+    async def complete_json(
+        self,
+        role: str,
+        payload: dict[str, Any],
+    ) -> dict[str, Any]:
+        """让模型返回结构化 JSON 数据。"""
+        raise NotImplementedError
+
+    @abstractmethod
+    async def complete_text(
+        self,
+        role: str,
+        payload: dict[str, Any],
+    ) -> str:
+        """让模型返回普通文本。"""
+        raise NotImplementedError
+
+
+class MockLLMClient(LLMClient):
+    """不联网的确定性客户端。
+
+    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
+    同样的输入会得到同样的输出，测试因此稳定且容易理解。
+    """
+
+    async def complete_json(
+        self,
+        role: str,
+        payload: dict[str, Any],
+    ) -> dict[str, Any]:
+        if role != "planner":
+            raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
+
+        query = str(payload.get("query", "")).strip()
+        if not query:
+            raise ValueError("planner 请求缺少 query")
+
+        return {
+            "plan": [
+                {
+                    "title": "现状与定义",
+                    "description": f"明确“{query}”的研究范围和当前现状。",
+                },
+                {
+                    "title": "问题与证据",
+                    "description": "整理公开来源中的事实、数据和主要争议。",
+                },
+                {
+                    "title": "趋势与建议",
+                    "description": "根据已有证据判断未来趋势并提出建议。",
+                },
+            ],
+            "research_questions": [
+                f"{query} 的当前现状和关键定义是什么？",
+                f"{query} 面临哪些主要问题，有哪些公开证据？",
+                f"{query} 的未来趋势和改进建议是什么？",
+            ],
+        }
+
+    async def complete_text(
+        self,
+        role: str,
+        payload: dict[str, Any],
+    ) -> str:
+        if role != "writer":
+            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")
+
+        query = str(payload.get("query", "")).strip()
+        return f"关于“{query}”的研究报告草稿。"
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
new file mode 100644
index 0000000..ce19c68
--- /dev/null
+++ b/backend/tests/test_llm_client.py
@@ -0,0 +1,42 @@
+import asyncio
+import unittest
+
+from app.core.llm_client import LLMClient, MockLLMClient
+
+
+class LLMClientTests(unittest.TestCase):
+    def test_mock_client_implements_llm_interface(self):
+        self.assertIsInstance(MockLLMClient(), LLMClient)
+
+    def test_mock_planner_returns_structured_result(self):
+        client = MockLLMClient()
+
+        result = asyncio.run(
+            client.complete_json(
+                "planner",
+                {"query": "新能源汽车行业的发展趋势是什么？"},
+            )
+        )
+
+        self.assertEqual(len(result["plan"]), 3)
+        self.assertEqual(len(result["research_questions"]), 3)
+        self.assertIn("新能源汽车", result["research_questions"][0])
+
+    def test_mock_client_rejects_unknown_role(self):
+        client = MockLLMClient()
+
+        with self.assertRaises(ValueError):
+            asyncio.run(client.complete_json("unknown", {"query": "测试"}))
+
+    def test_mock_writer_returns_text(self):
+        client = MockLLMClient()
+
+        result = asyncio.run(
+            client.complete_text("writer", {"query": "测试行业"})
+        )
+
+        self.assertIn("测试行业", result)
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-45049a2"></a>
### 提交 45049a2：feat: add planner agent

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/planner.py b/backend/app/agents/planner.py
new file mode 100644
index 0000000..b5673f3
--- /dev/null
+++ b/backend/app/agents/planner.py
@@ -0,0 +1,68 @@
+"""研究规划 Agent。"""
+
+from __future__ import annotations
+
+from typing import Any
+
+from app.core.llm_client import LLMClient
+from app.domain.state import ResearchState
+
+from .base import BaseAgent
+
+
+class PlannerAgent(BaseAgent):
+    """把一个用户问题拆成可执行的研究计划。"""
+
+    name = "planner"
+
+    def __init__(self, llm: LLMClient):
+        self.llm = llm
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        """调用 LLM，校验结果，然后写回共享状态。"""
+        query = state.query.strip()
+        if not query:
+            raise ValueError("研究问题不能为空")
+
+        result = await self.llm.complete_json(
+            role=self.name,
+            payload={
+                "query": query,
+                "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
+            },
+        )
+        plan = self._validate_plan(result.get("plan"))
+        research_questions = self._validate_questions(result.get("research_questions"))
+
+        state.plan = plan
+        state.research_questions = research_questions
+        state.phase = "planning"
+        return state
+
+    @staticmethod
+    def _validate_plan(value: Any) -> list[dict[str, str]]:
+        """确保计划是由标题和描述组成的字典列表。"""
+        if not isinstance(value, list) or not value:
+            raise ValueError("Planner 返回的 plan 必须是非空列表")
+
+        validated: list[dict[str, str]] = []
+        for index, item in enumerate(value, start=1):
+            if not isinstance(item, dict):
+                raise ValueError(f"Planner 的第 {index} 个计划不是对象")
+            title = str(item.get("title", "")).strip()
+            description = str(item.get("description", "")).strip()
+            if not title or not description:
+                raise ValueError(f"Planner 的第 {index} 个计划缺少 title 或 description")
+            validated.append({"title": title, "description": description})
+        return validated
+
+    @staticmethod
+    def _validate_questions(value: Any) -> list[str]:
+        """确保子问题是非空字符串列表。"""
+        if not isinstance(value, list) or not value:
+            raise ValueError("Planner 返回的 research_questions 必须是非空列表")
+
+        questions = [str(item).strip() for item in value]
+        if any(not question for question in questions):
+            raise ValueError("Planner 返回了空的研究子问题")
+        return questions
diff --git a/backend/tests/test_planner.py b/backend/tests/test_planner.py
new file mode 100644
index 0000000..ecae6f1
--- /dev/null
+++ b/backend/tests/test_planner.py
@@ -0,0 +1,40 @@
+import asyncio
+import unittest
+
+from app.agents.planner import PlannerAgent
+from app.core.llm_client import LLMClient, MockLLMClient
+from app.domain.state import ResearchState
+
+
+class BrokenPlannerClient(LLMClient):
+    async def complete_json(self, role, payload):
+        return {"plan": [], "research_questions": []}
+
+    async def complete_text(self, role, payload):
+        return ""
+
+
+class PlannerAgentTests(unittest.TestCase):
+    def test_planner_writes_plan_into_state(self):
+        state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
+        agent = PlannerAgent(MockLLMClient())
+
+        result = asyncio.run(agent.run(state))
+
+        self.assertIs(result, state)
+        self.assertEqual(result.phase, "planning")
+        self.assertEqual(len(result.plan), 3)
+        self.assertEqual(len(result.research_questions), 3)
+        self.assertIn("新能源汽车", result.plan[0]["description"])
+
+    def test_planner_rejects_empty_query(self):
+        with self.assertRaises(ValueError):
+            asyncio.run(PlannerAgent(MockLLMClient()).run(ResearchState("   ")))
+
+    def test_planner_rejects_invalid_llm_result(self):
+        with self.assertRaisesRegex(ValueError, "非空列表"):
+            asyncio.run(PlannerAgent(BrokenPlannerClient()).run(ResearchState("测试问题")))
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-7a483d7"></a>
### 提交 7a483d7：feat: add search client abstraction

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/core/search_client.py b/backend/app/core/search_client.py
new file mode 100644
index 0000000..d5b0430
--- /dev/null
+++ b/backend/app/core/search_client.py
@@ -0,0 +1,62 @@
+"""统一的搜索客户端接口。
+
+搜索客户端只负责获取候选来源。
+它不负责判断来源是否可信，也不负责把来源写成研究报告。
+这些职责会交给后面的 Researcher 和 Writer。
+"""
+
+from __future__ import annotations
+
+import hashlib
+from abc import ABC, abstractmethod
+from dataclasses import asdict, dataclass
+from typing import Any
+
+
+@dataclass
+class SearchResult:
+    """一条搜索结果的统一格式。"""
+
+    title: str
+    url: str
+    snippet: str
+    query: str
+    content: str = ""
+
+    def to_dict(self) -> dict[str, Any]:
+        """转换成适合放进 ResearchState 的字典。"""
+        return asdict(self)
+
+
+class SearchClient(ABC):
+    """所有搜索服务都要遵守的接口。"""
+
+    @abstractmethod
+    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
+        """根据一个研究子问题返回候选来源。"""
+        raise NotImplementedError
+
+
+class MockSearchClient(SearchClient):
+    """本地模拟搜索服务。
+
+    URL 使用查询内容的摘要生成，因此同一个查询每次都会得到同一个来源。
+    这样测试不会依赖网络，也方便观察数据流。
+    """
+
+    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
+        query = query.strip()
+        if not query:
+            raise ValueError("搜索问题不能为空")
+        if limit < 1:
+            raise ValueError("limit 必须大于 0")
+
+        digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
+        result = SearchResult(
+            title=f"公开资料：{query}",
+            url=f"https://example.com/research/{digest}",
+            snippet=f"这是针对“{query}”的模拟公开资料摘要，用于验证研究流程。",
+            query=query,
+            content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。",
+        )
+        return [result]
diff --git a/backend/tests/test_search_client.py b/backend/tests/test_search_client.py
new file mode 100644
index 0000000..168fd2a
--- /dev/null
+++ b/backend/tests/test_search_client.py
@@ -0,0 +1,41 @@
+import asyncio
+import unittest
+
+from app.core.search_client import MockSearchClient, SearchClient, SearchResult
+
+
+class SearchClientTests(unittest.TestCase):
+    def test_mock_client_implements_search_interface(self):
+        self.assertIsInstance(MockSearchClient(), SearchClient)
+
+    def test_search_returns_normalized_result(self):
+        client = MockSearchClient()
+
+        results = asyncio.run(client.search("新能源汽车行业的市场规模是什么？"))
+
+        self.assertEqual(len(results), 1)
+        self.assertIsInstance(results[0], SearchResult)
+        self.assertTrue(results[0].title)
+        self.assertTrue(results[0].url.startswith("https://"))
+        self.assertTrue(results[0].snippet)
+        self.assertEqual(results[0].query, "新能源汽车行业的市场规模是什么？")
+
+    def test_same_query_has_stable_url(self):
+        client = MockSearchClient()
+
+        first = asyncio.run(client.search("稳定查询"))[0]
+        second = asyncio.run(client.search("稳定查询"))[0]
+
+        self.assertEqual(first.url, second.url)
+
+    def test_search_rejects_invalid_input(self):
+        client = MockSearchClient()
+
+        with self.assertRaises(ValueError):
+            asyncio.run(client.search("   "))
+        with self.assertRaises(ValueError):
+            asyncio.run(client.search("测试", limit=0))
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-b352eb6"></a>
### 提交 b352eb6：feat: add researcher agent

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/researcher.py b/backend/app/agents/researcher.py
new file mode 100644
index 0000000..d469434
--- /dev/null
+++ b/backend/app/agents/researcher.py
@@ -0,0 +1,61 @@
+"""研究信息收集 Agent。"""
+
+from __future__ import annotations
+
+from app.core.search_client import SearchClient
+from app.domain.state import ResearchState
+
+from .base import BaseAgent
+
+
+class ResearcherAgent(BaseAgent):
+    """根据研究子问题收集候选来源。
+
+    这一版只负责搜索和去重。事实提取会在后续步骤使用 LLM 单独完成，
+    这样每个 Agent 的输入和输出都更容易观察。
+    """
+
+    name = "researcher"
+
+    def __init__(self, search: SearchClient, results_per_question: int = 3):
+        if results_per_question < 1:
+            raise ValueError("results_per_question 必须大于 0")
+        self.search = search
+        self.results_per_question = results_per_question
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        """搜索所有子问题，并把来源写入共享状态。"""
+        questions = [question.strip() for question in state.research_questions]
+        questions = [question for question in questions if question]
+        if not questions:
+            raise ValueError("没有可执行的研究子问题")
+
+        collected_sources = list(state.sources)
+        for question in questions:
+            results = await self.search.search(
+                query=question,
+                limit=self.results_per_question,
+            )
+            collected_sources.extend(result.to_dict() for result in results)
+
+        state.sources = self._deduplicate_sources(collected_sources)
+        state.references = [
+            {
+                "title": source["title"],
+                "url": source["url"],
+            }
+            for source in state.sources
+            if source.get("url")
+        ]
+        state.phase = "researching"
+        return state
+
+    @staticmethod
+    def _deduplicate_sources(sources: list[dict]) -> list[dict]:
+        """按 URL 去重，同时保留第一次出现的顺序。"""
+        unique: dict[str, dict] = {}
+        for source in sources:
+            url = str(source.get("url", "")).strip()
+            if url and url not in unique:
+                unique[url] = source
+        return list(unique.values())
diff --git a/backend/tests/test_researcher.py b/backend/tests/test_researcher.py
new file mode 100644
index 0000000..c21e2a0
--- /dev/null
+++ b/backend/tests/test_researcher.py
@@ -0,0 +1,46 @@
+import asyncio
+import unittest
+
+from app.agents.planner import PlannerAgent
+from app.agents.researcher import ResearcherAgent
+from app.core.llm_client import MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.domain.state import ResearchState
+
+
+class ResearcherAgentTests(unittest.TestCase):
+    def test_researcher_collects_sources_after_planning(self):
+        async def run_chain():
+            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
+            await PlannerAgent(MockLLMClient()).run(state)
+            await ResearcherAgent(MockSearchClient()).run(state)
+            return state
+
+        state = asyncio.run(run_chain())
+
+        self.assertEqual(state.phase, "researching")
+        self.assertEqual(len(state.research_questions), 3)
+        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(len(state.references), 3)
+        self.assertTrue(all(source["url"].startswith("https://") for source in state.sources))
+
+    def test_researcher_deduplicates_existing_source_urls(self):
+        async def run():
+            state = ResearchState("测试问题")
+            state.research_questions = ["相同问题", "相同问题"]
+            return await ResearcherAgent(MockSearchClient()).run(state)
+
+        state = asyncio.run(run())
+
+        self.assertEqual(len(state.sources), 1)
+        self.assertEqual(len(state.references), 1)
+
+    def test_researcher_rejects_missing_questions(self):
+        state = ResearchState("还没有规划的问题")
+
+        with self.assertRaisesRegex(ValueError, "研究子问题"):
+            asyncio.run(ResearcherAgent(MockSearchClient()).run(state))
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-13b6ffe"></a>
### 提交 13b6ffe：feat: add source grounded fact extraction

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/fact_extractor.py b/backend/app/agents/fact_extractor.py
new file mode 100644
index 0000000..c33a634
--- /dev/null
+++ b/backend/app/agents/fact_extractor.py
@@ -0,0 +1,88 @@
+"""从候选来源中提取带来源的结构化事实。"""
+
+from __future__ import annotations
+
+from typing import Any
+
+from app.core.llm_client import LLMClient
+from app.domain.state import ResearchState
+
+from .base import BaseAgent
+
+
+class FactExtractorAgent(BaseAgent):
+    """把网页来源转换成报告可以引用的事实。"""
+
+    name = "fact_extractor"
+
+    def __init__(self, llm: LLMClient):
+        self.llm = llm
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        if not state.sources:
+            raise ValueError("没有可供事实提取的来源")
+
+        result = await self.llm.complete_json(
+            role=self.name,
+            payload={
+                "query": state.query,
+                "sources": state.sources,
+                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
+            },
+        )
+        facts = self._validate_facts(result.get("facts"), state.sources)
+        state.facts = self._deduplicate_facts(state.facts + facts)
+        state.phase = "researching"
+        return state
+
+    @staticmethod
+    def _validate_facts(value: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
+        if not isinstance(value, list):
+            raise ValueError("FactExtractor 返回的 facts 必须是列表")
+
+        allowed_urls = {
+            str(source.get("url", "")).strip()
+            for source in sources
+            if source.get("url")
+        }
+        validated: list[dict[str, Any]] = []
+        for index, item in enumerate(value, start=1):
+            if not isinstance(item, dict):
+                raise ValueError(f"FactExtractor 的第 {index} 个事实不是对象")
+
+            content = str(item.get("content", "")).strip()
+            source_url = str(item.get("source_url", "")).strip()
+            if not content or not source_url:
+                raise ValueError(f"FactExtractor 的第 {index} 个事实缺少 content 或 source_url")
+            if source_url not in allowed_urls:
+                raise ValueError(f"FactExtractor 的第 {index} 个事实引用了未知来源")
+
+            try:
+                confidence = float(item.get("confidence", 0.0))
+            except (TypeError, ValueError) as exc:
+                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 无效") from exc
+            if not 0 <= confidence <= 1:
+                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间")
+
+            validated.append(
+                {
+                    "content": content,
+                    "source_title": str(item.get("source_title", "")).strip(),
+                    "source_url": source_url,
+                    "source_type": str(item.get("source_type", "web")).strip() or "web",
+                    "confidence": confidence,
+                }
+            )
+        return validated
+
+    @staticmethod
+    def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
+        unique: dict[tuple[str, str], dict[str, Any]] = {}
+        for fact in facts:
+            key = (
+                str(fact.get("source_url", "")).strip(),
+                str(fact.get("content", "")).strip(),
+            )
+            if key != ("", ""):
+                unique.setdefault(key, fact)
+        return list(unique.values())
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index f6c7263..0840a13 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -44,34 +44,52 @@ class MockLLMClient(LLMClient):
         role: str,
         payload: dict[str, Any],
     ) -> dict[str, Any]:
-        if role != "planner":
-            raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
+        if role == "planner":
+            query = str(payload.get("query", "")).strip()
+            if not query:
+                raise ValueError("planner 请求缺少 query")
 
-        query = str(payload.get("query", "")).strip()
-        if not query:
-            raise ValueError("planner 请求缺少 query")
-
-        return {
-            "plan": [
-                {
-                    "title": "现状与定义",
-                    "description": f"明确“{query}”的研究范围和当前现状。",
-                },
-                {
-                    "title": "问题与证据",
-                    "description": "整理公开来源中的事实、数据和主要争议。",
-                },
-                {
-                    "title": "趋势与建议",
-                    "description": "根据已有证据判断未来趋势并提出建议。",
-                },
-            ],
-            "research_questions": [
-                f"{query} 的当前现状和关键定义是什么？",
-                f"{query} 面临哪些主要问题，有哪些公开证据？",
-                f"{query} 的未来趋势和改进建议是什么？",
-            ],
-        }
+            return {
+                "plan": [
+                    {
+                        "title": "现状与定义",
+                        "description": f"明确“{query}”的研究范围和当前现状。",
+                    },
+                    {
+                        "title": "问题与证据",
+                        "description": "整理公开来源中的事实、数据和主要争议。",
+                    },
+                    {
+                        "title": "趋势与建议",
+                        "description": "根据已有证据判断未来趋势并提出建议。",
+                    },
+                ],
+                "research_questions": [
+                    f"{query} 的当前现状和关键定义是什么？",
+                    f"{query} 面临哪些主要问题，有哪些公开证据？",
+                    f"{query} 的未来趋势和改进建议是什么？",
+                ],
+            }
+
+        if role == "fact_extractor":
+            facts = []
+            for source in payload.get("sources", []):
+                content = str(source.get("content") or source.get("snippet") or "").strip()
+                url = str(source.get("url", "")).strip()
+                if not content or not url:
+                    continue
+                facts.append(
+                    {
+                        "content": content,
+                        "source_title": str(source.get("title", "")).strip(),
+                        "source_url": url,
+                        "source_type": "web",
+                        "confidence": 0.7,
+                    }
+                )
+            return {"facts": facts}
+
+        raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
 
     async def complete_text(
         self,
diff --git a/backend/tests/test_fact_extractor.py b/backend/tests/test_fact_extractor.py
new file mode 100644
index 0000000..3468327
--- /dev/null
+++ b/backend/tests/test_fact_extractor.py
@@ -0,0 +1,64 @@
+import asyncio
+import unittest
+
+from app.agents.fact_extractor import FactExtractorAgent
+from app.agents.planner import PlannerAgent
+from app.agents.researcher import ResearcherAgent
+from app.core.llm_client import LLMClient, MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.domain.state import ResearchState
+
+
+class BrokenFactClient(LLMClient):
+    async def complete_json(self, role, payload):
+        return {
+            "facts": [
+                {
+                    "content": "这条事实引用了不存在的来源。",
+                    "source_url": "https://unknown.example.com",
+                    "confidence": 0.8,
+                }
+            ]
+        }
+
+    async def complete_text(self, role, payload):
+        return ""
+
+
+class FactExtractorAgentTests(unittest.TestCase):
+    def test_fact_extractor_turns_sources_into_facts(self):
+        async def run_chain():
+            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
+            await PlannerAgent(MockLLMClient()).run(state)
+            await ResearcherAgent(MockSearchClient()).run(state)
+            await FactExtractorAgent(MockLLMClient()).run(state)
+            return state
+
+        state = asyncio.run(run_chain())
+
+        self.assertEqual(state.phase, "researching")
+        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(len(state.facts), 3)
+        self.assertTrue(all(fact["source_url"] for fact in state.facts))
+        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
+
+    def test_fact_extractor_rejects_unknown_source_url(self):
+        state = ResearchState("测试问题")
+        state.sources = [
+            {
+                "title": "已知来源",
+                "url": "https://known.example.com",
+                "snippet": "摘要",
+            }
+        ]
+
+        with self.assertRaisesRegex(ValueError, "未知来源"):
+            asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))
+
+    def test_fact_extractor_requires_sources(self):
+        with self.assertRaisesRegex(ValueError, "来源"):
+            asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
index ce19c68..108a42f 100644
--- a/backend/tests/test_llm_client.py
+++ b/backend/tests/test_llm_client.py
@@ -22,6 +22,28 @@ class LLMClientTests(unittest.TestCase):
         self.assertEqual(len(result["research_questions"]), 3)
         self.assertIn("新能源汽车", result["research_questions"][0])
 
+    def test_mock_fact_extractor_returns_source_grounded_facts(self):
+        client = MockLLMClient()
+
+        result = asyncio.run(
+            client.complete_json(
+                "fact_extractor",
+                {
+                    "query": "测试行业",
+                    "sources": [
+                        {
+                            "title": "测试来源",
+                            "url": "https://example.com/source",
+                            "content": "测试来源中的明确事实。",
+                        }
+                    ],
+                },
+            )
+        )
+
+        self.assertEqual(len(result["facts"]), 1)
+        self.assertEqual(result["facts"][0]["source_url"], "https://example.com/source")
+
     def test_mock_client_rejects_unknown_role(self):
         client = MockLLMClient()
 
```

<a id="diff-63e065b"></a>
### 提交 63e065b：feat: add cited report writer

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/writer.py b/backend/app/agents/writer.py
new file mode 100644
index 0000000..09c8a70
--- /dev/null
+++ b/backend/app/agents/writer.py
@@ -0,0 +1,41 @@
+"""研究报告写作 Agent。"""
+
+from __future__ import annotations
+
+from app.core.llm_client import LLMClient
+from app.domain.state import ResearchState
+
+from .base import BaseAgent
+
+
+class WriterAgent(BaseAgent):
+    """根据研究计划和带来源事实生成 Markdown 报告。"""
+
+    name = "writer"
+
+    def __init__(self, llm: LLMClient):
+        self.llm = llm
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        if not state.plan:
+            raise ValueError("没有可用于写作的研究计划")
+        if not state.facts:
+            raise ValueError("没有可用于写作的事实")
+
+        report = await self.llm.complete_text(
+            role=self.name,
+            payload={
+                "query": state.query,
+                "plan": state.plan,
+                "facts": state.facts,
+                "references": state.references,
+                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告。",
+            },
+        )
+        report = report.strip()
+        if not report:
+            raise ValueError("Writer 没有生成报告内容")
+
+        state.final_report = report
+        state.phase = "writing"
+        return state
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index 0840a13..cfb3c76 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -100,4 +100,33 @@ class MockLLMClient(LLMClient):
             raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")
 
         query = str(payload.get("query", "")).strip()
-        return f"关于“{query}”的研究报告草稿。"
+        if not query:
+            raise ValueError("writer 请求缺少 query")
+
+        facts = payload.get("facts", [])
+        lines = [
+            "## 执行摘要",
+            "",
+            f"本报告围绕“{query}”整理公开资料，并只使用已收集的来源作为证据。",
+            "",
+            "## 研究发现",
+            "",
+        ]
+        if facts:
+            for index, fact in enumerate(facts, start=1):
+                content = str(fact.get("content", "")).strip()
+                title = str(fact.get("source_title", "来源")).strip() or "来源"
+                url = str(fact.get("source_url", "")).strip()
+                lines.append(f"{index}. {content} ([{title}]({url}))")
+        else:
+            lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")
+
+        lines.extend(
+            [
+                "",
+                "## 结论",
+                "",
+                "以上结论需要结合更多官方统计和行业报告继续验证。",
+            ]
+        )
+        return "\n".join(lines)
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
index 108a42f..8aba9b5 100644
--- a/backend/tests/test_llm_client.py
+++ b/backend/tests/test_llm_client.py
@@ -54,10 +54,24 @@ class LLMClientTests(unittest.TestCase):
         client = MockLLMClient()
 
         result = asyncio.run(
-            client.complete_text("writer", {"query": "测试行业"})
+            client.complete_text(
+                "writer",
+                {
+                    "query": "测试行业",
+                    "facts": [
+                        {
+                            "content": "测试事实。",
+                            "source_title": "测试来源",
+                            "source_url": "https://example.com/source",
+                        }
+                    ],
+                },
+            )
         )
 
         self.assertIn("测试行业", result)
+        self.assertIn("测试事实", result)
+        self.assertIn("https://example.com/source", result)
 
 
 if __name__ == "__main__":
diff --git a/backend/tests/test_writer.py b/backend/tests/test_writer.py
new file mode 100644
index 0000000..26775a8
--- /dev/null
+++ b/backend/tests/test_writer.py
@@ -0,0 +1,47 @@
+import asyncio
+import unittest
+
+from app.agents.fact_extractor import FactExtractorAgent
+from app.agents.planner import PlannerAgent
+from app.agents.researcher import ResearcherAgent
+from app.agents.writer import WriterAgent
+from app.core.llm_client import MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.domain.state import ResearchState
+
+
+class WriterAgentTests(unittest.TestCase):
+    def test_writer_generates_cited_report(self):
+        async def run_chain():
+            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
+            llm = MockLLMClient()
+            await PlannerAgent(llm).run(state)
+            await ResearcherAgent(MockSearchClient()).run(state)
+            await FactExtractorAgent(llm).run(state)
+            await WriterAgent(llm).run(state)
+            return state
+
+        state = asyncio.run(run_chain())
+
+        self.assertEqual(state.phase, "writing")
+        self.assertTrue(state.final_report.startswith("## 执行摘要"))
+        self.assertIn("研究发现", state.final_report)
+        self.assertIn("https://example.com/research/", state.final_report)
+
+    def test_writer_requires_plan(self):
+        state = ResearchState("测试问题")
+        state.facts = [{"content": "事实", "source_url": "https://example.com"}]
+
+        with self.assertRaisesRegex(ValueError, "研究计划"):
+            asyncio.run(WriterAgent(MockLLMClient()).run(state))
+
+    def test_writer_requires_facts(self):
+        state = ResearchState("测试问题")
+        state.plan = [{"title": "章节", "description": "描述"}]
+
+        with self.assertRaisesRegex(ValueError, "事实"):
+            asyncio.run(WriterAgent(MockLLMClient()).run(state))
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-87f7acf"></a>
### 提交 87f7acf：feat: add research report critic

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/critic.py b/backend/app/agents/critic.py
new file mode 100644
index 0000000..0879a57
--- /dev/null
+++ b/backend/app/agents/critic.py
@@ -0,0 +1,67 @@
+"""研究报告质量审核 Agent。"""
+
+from __future__ import annotations
+
+from typing import Any
+
+from app.core.llm_client import LLMClient
+from app.domain.state import ResearchState
+
+from .base import BaseAgent
+
+
+class CriticAgent(BaseAgent):
+    """检查报告是否有事实、来源和基本的可发布条件。"""
+
+    name = "critic"
+
+    def __init__(self, llm: LLMClient):
+        self.llm = llm
+
+    async def run(self, state: ResearchState) -> ResearchState:
+        if not state.final_report.strip():
+            raise ValueError("没有可供审核的报告")
+
+        result = await self.llm.complete_json(
+            role=self.name,
+            payload={
+                "query": state.query,
+                "report": state.final_report,
+                "facts": state.facts,
+                "sources": state.sources,
+                "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
+            },
+        )
+        review = self._validate_review(result)
+        state.review = review
+        state.quality_score = review["quality_score"]
+        state.phase = "reviewing"
+        return state
+
+    @staticmethod
+    def _validate_review(value: Any) -> dict[str, Any]:
+        if not isinstance(value, dict):
+            raise ValueError("Critic 返回结果必须是对象")
+
+        verdict = str(value.get("verdict", "")).strip()
+        if verdict not in {"pass", "needs_revision"}:
+            raise ValueError("Critic verdict 必须是 pass 或 needs_revision")
+
+        try:
+            quality_score = float(value.get("quality_score"))
+        except (TypeError, ValueError) as exc:
+            raise ValueError("Critic quality_score 必须是数字") from exc
+        if not 0 <= quality_score <= 10:
+            raise ValueError("Critic quality_score 必须在 0 到 10 之间")
+
+        issues = value.get("issues", [])
+        if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
+            raise ValueError("Critic issues 必须是字符串列表")
+
+        return {
+            "verdict": verdict,
+            "quality_score": quality_score,
+            "summary": str(value.get("summary", "")).strip(),
+            "needs_more_research": bool(value.get("needs_more_research", False)),
+            "issues": issues,
+        }
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index cfb3c76..16a2b97 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -89,6 +89,22 @@ class MockLLMClient(LLMClient):
                 )
             return {"facts": facts}
 
+        if role == "critic":
+            report = str(payload.get("report", "")).strip()
+            facts = payload.get("facts", [])
+            sources = payload.get("sources", [])
+            if not report:
+                raise ValueError("critic 请求缺少 report")
+
+            passed = bool(facts and sources and "http" in report)
+            return {
+                "verdict": "pass" if passed else "needs_revision",
+                "quality_score": 8.0 if passed else 4.0,
+                "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
+                "needs_more_research": not passed,
+                "issues": [] if passed else ["需要补充带来源的事实"],
+            }
+
         raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
 
     async def complete_text(
diff --git a/backend/tests/test_critic.py b/backend/tests/test_critic.py
new file mode 100644
index 0000000..e46fd9c
--- /dev/null
+++ b/backend/tests/test_critic.py
@@ -0,0 +1,54 @@
+import asyncio
+import unittest
+
+from app.agents.critic import CriticAgent
+from app.agents.fact_extractor import FactExtractorAgent
+from app.agents.planner import PlannerAgent
+from app.agents.researcher import ResearcherAgent
+from app.agents.writer import WriterAgent
+from app.core.llm_client import LLMClient, MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.domain.state import ResearchState
+
+
+class BrokenCriticClient(LLMClient):
+    async def complete_json(self, role, payload):
+        return {"verdict": "unknown", "quality_score": 20, "issues": "错误格式"}
+
+    async def complete_text(self, role, payload):
+        return ""
+
+
+class CriticAgentTests(unittest.TestCase):
+    def test_critic_approves_source_grounded_report(self):
+        async def run_chain():
+            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
+            llm = MockLLMClient()
+            await PlannerAgent(llm).run(state)
+            await ResearcherAgent(MockSearchClient()).run(state)
+            await FactExtractorAgent(llm).run(state)
+            await WriterAgent(llm).run(state)
+            await CriticAgent(llm).run(state)
+            return state
+
+        state = asyncio.run(run_chain())
+
+        self.assertEqual(state.phase, "reviewing")
+        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.quality_score, 8.0)
+        self.assertEqual(state.review["issues"], [])
+
+    def test_critic_rejects_invalid_result(self):
+        state = ResearchState("测试问题")
+        state.final_report = "## 报告\n内容"
+
+        with self.assertRaisesRegex(ValueError, "verdict"):
+            asyncio.run(CriticAgent(BrokenCriticClient()).run(state))
+
+    def test_critic_requires_report(self):
+        with self.assertRaisesRegex(ValueError, "审核的报告"):
+            asyncio.run(CriticAgent(MockLLMClient()).run(ResearchState("测试问题")))
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
index 8aba9b5..7386590 100644
--- a/backend/tests/test_llm_client.py
+++ b/backend/tests/test_llm_client.py
@@ -44,6 +44,24 @@ class LLMClientTests(unittest.TestCase):
         self.assertEqual(len(result["facts"]), 1)
         self.assertEqual(result["facts"][0]["source_url"], "https://example.com/source")
 
+    def test_mock_critic_approves_cited_report(self):
+        client = MockLLMClient()
+
+        result = asyncio.run(
+            client.complete_json(
+                "critic",
+                {
+                    "query": "测试行业",
+                    "report": "报告内容 https://example.com/source",
+                    "facts": [{"content": "事实"}],
+                    "sources": [{"url": "https://example.com/source"}],
+                },
+            )
+        )
+
+        self.assertEqual(result["verdict"], "pass")
+        self.assertEqual(result["quality_score"], 8.0)
+
     def test_mock_client_rejects_unknown_role(self):
         client = MockLLMClient()
 
```

<a id="diff-861a4fa"></a>
### 提交 861a4fa：feat: orchestrate complete research workflow

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/workflow/__init__.py b/backend/app/workflow/__init__.py
new file mode 100644
index 0000000..5c2e01a
--- /dev/null
+++ b/backend/app/workflow/__init__.py
@@ -0,0 +1 @@
+"""Research workflow orchestration."""
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
new file mode 100644
index 0000000..e956752
--- /dev/null
+++ b/backend/app/workflow/research_workflow.py
@@ -0,0 +1,54 @@
+"""把多个 Agent 编排成一次完整研究任务。"""
+
+from __future__ import annotations
+
+from uuid import uuid4
+
+from app.agents.critic import CriticAgent
+from app.agents.fact_extractor import FactExtractorAgent
+from app.agents.planner import PlannerAgent
+from app.agents.researcher import ResearcherAgent
+from app.agents.writer import WriterAgent
+from app.core.llm_client import LLMClient
+from app.core.search_client import SearchClient
+from app.domain.state import ResearchState
+
+
+class ResearchWorkflow:
+    """Iteration 01 的最小同步编排器。
+
+    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
+    后续再在这个类上增加流式事件和审核修订循环。
+    """
+
+    def __init__(
+        self,
+        llm: LLMClient,
+        search: SearchClient,
+        results_per_question: int = 3,
+    ):
+        self.planner = PlannerAgent(llm)
+        self.researcher = ResearcherAgent(search, results_per_question)
+        self.fact_extractor = FactExtractorAgent(llm)
+        self.writer = WriterAgent(llm)
+        self.critic = CriticAgent(llm)
+
+    async def run(
+        self,
+        query: str,
+        session_id: str | None = None,
+    ) -> ResearchState:
+        """执行一次完整研究并返回最终状态。"""
+        state = ResearchState(
+            query=query,
+            session_id=session_id or str(uuid4()),
+        )
+
+        await self.planner.run(state)
+        await self.researcher.run(state)
+        await self.fact_extractor.run(state)
+        await self.writer.run(state)
+        await self.critic.run(state)
+
+        state.phase = "completed"
+        return state
diff --git a/backend/tests/test_workflow.py b/backend/tests/test_workflow.py
new file mode 100644
index 0000000..e831b4f
--- /dev/null
+++ b/backend/tests/test_workflow.py
@@ -0,0 +1,36 @@
+import asyncio
+import unittest
+
+from app.core.llm_client import MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.workflow.research_workflow import ResearchWorkflow
+
+
+class ResearchWorkflowTests(unittest.TestCase):
+    def test_workflow_runs_full_research_chain(self):
+        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
+
+        state = asyncio.run(
+            workflow.run("中国新能源汽车行业的发展趋势是什么？")
+        )
+
+        self.assertEqual(state.phase, "completed")
+        self.assertEqual(state.plan[0]["title"], "现状与定义")
+        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(len(state.facts), 3)
+        self.assertTrue(state.final_report)
+        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.quality_score, 8.0)
+
+    def test_workflow_preserves_explicit_session_id(self):
+        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
+
+        state = asyncio.run(
+            workflow.run("测试问题", session_id="session-001")
+        )
+
+        self.assertEqual(state.session_id, "session-001")
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-99f39af"></a>
### 提交 99f39af：feat: add command line research runner

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/README.md b/README.md
index 23b7f87..e01320a 100644
--- a/README.md
+++ b/README.md
@@ -20,3 +20,18 @@
 ## 学习方式
 
 每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。
+
+## 命令行运行
+
+在项目根目录执行：
+
+```powershell
+$env:PYTHONPATH = "backend"
+python -m app.scripts.run_research "中国新能源汽车行业的发展趋势是什么？"
+```
+
+不传问题时，会进入交互式输入：
+
+```powershell
+python -m app.scripts.run_research
+```
diff --git a/backend/app/scripts/__init__.py b/backend/app/scripts/__init__.py
new file mode 100644
index 0000000..b22122e
--- /dev/null
+++ b/backend/app/scripts/__init__.py
@@ -0,0 +1 @@
+"""Executable learning scripts."""
diff --git a/backend/app/scripts/run_research.py b/backend/app/scripts/run_research.py
new file mode 100644
index 0000000..bbc5f00
--- /dev/null
+++ b/backend/app/scripts/run_research.py
@@ -0,0 +1,75 @@
+"""从命令行运行一次 Mock DeepResearch。"""
+
+from __future__ import annotations
+
+import argparse
+import asyncio
+
+from app.core.llm_client import MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.domain.state import ResearchState
+from app.workflow.research_workflow import ResearchWorkflow
+
+
+def build_parser() -> argparse.ArgumentParser:
+    parser = argparse.ArgumentParser(description="运行一次 Iteration 01 DeepResearch")
+    parser.add_argument(
+        "query",
+        nargs="?",
+        help="研究问题；不传时会进入交互式输入",
+    )
+    return parser
+
+
+def print_state(state: ResearchState) -> None:
+    print("\n" + "=" * 60)
+    print("研究计划")
+    print("=" * 60)
+    for index, item in enumerate(state.plan, start=1):
+        print(f"{index}. {item['title']}：{item['description']}")
+
+    print("\n" + "=" * 60)
+    print(f"搜索来源（{len(state.sources)} 条）")
+    print("=" * 60)
+    for index, source in enumerate(state.sources, start=1):
+        print(f"{index}. {source['title']}")
+        print(f"   URL: {source['url']}")
+
+    print("\n" + "=" * 60)
+    print(f"结构化事实（{len(state.facts)} 条）")
+    print("=" * 60)
+    for index, fact in enumerate(state.facts, start=1):
+        print(f"{index}. {fact['content']}")
+        print(f"   来源: {fact['source_url']}")
+
+    print("\n" + "=" * 60)
+    print("最终报告")
+    print("=" * 60)
+    print(state.final_report)
+
+    print("\n" + "=" * 60)
+    print("审核结果")
+    print("=" * 60)
+    print(f"结论: {state.review['verdict']}")
+    print(f"评分: {state.quality_score}/10")
+    print(f"摘要: {state.review['summary']}")
+    print(f"任务阶段: {state.phase}")
+    print(f"会话 ID: {state.session_id}")
+
+
+async def run(query: str) -> ResearchState:
+    workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
+    return await workflow.run(query)
+
+
+def main() -> None:
+    args = build_parser().parse_args()
+    query = (args.query or input("请输入研究问题：")).strip()
+    if not query:
+        raise SystemExit("研究问题不能为空")
+    state = asyncio.run(run(query))
+    print_state(state)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/backend/tests/test_run_research.py b/backend/tests/test_run_research.py
new file mode 100644
index 0000000..9ec4232
--- /dev/null
+++ b/backend/tests/test_run_research.py
@@ -0,0 +1,32 @@
+import asyncio
+import unittest
+from contextlib import redirect_stdout
+from io import StringIO
+
+from app.scripts.run_research import print_state, run
+
+
+class RunResearchScriptTests(unittest.TestCase):
+    def test_script_run_returns_completed_state(self):
+        state = asyncio.run(run("测试行业的现状是什么？"))
+
+        self.assertEqual(state.phase, "completed")
+        self.assertTrue(state.final_report)
+
+    def test_print_state_contains_key_sections(self):
+        state = asyncio.run(run("测试行业的现状是什么？"))
+        output = StringIO()
+
+        with redirect_stdout(output):
+            print_state(state)
+
+        text = output.getvalue()
+        self.assertIn("研究计划", text)
+        self.assertIn("搜索来源", text)
+        self.assertIn("结构化事实", text)
+        self.assertIn("最终报告", text)
+        self.assertIn("审核结果", text)
+
+
+if __name__ == "__main__":
+    unittest.main()
````

<a id="diff-64b3d07"></a>
### 提交 64b3d07：feat: add critic routing and revision loop

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/critic.py b/backend/app/agents/critic.py
index 0879a57..bd636e0 100644
--- a/backend/app/agents/critic.py
+++ b/backend/app/agents/critic.py
@@ -29,6 +29,7 @@ class CriticAgent(BaseAgent):
                 "report": state.final_report,
                 "facts": state.facts,
                 "sources": state.sources,
+                "iteration": state.iteration,
                 "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
             },
         )
@@ -58,10 +59,21 @@ class CriticAgent(BaseAgent):
         if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
             raise ValueError("Critic issues 必须是字符串列表")
 
+        needs_more_research = value.get("needs_more_research", False)
+        if not isinstance(needs_more_research, bool):
+            raise ValueError("Critic needs_more_research 必须是布尔值")
+
+        search_queries = value.get("search_queries", [])
+        if not isinstance(search_queries, list) or not all(
+            isinstance(query, str) and query.strip() for query in search_queries
+        ):
+            raise ValueError("Critic search_queries 必须是非空字符串列表")
+
         return {
             "verdict": verdict,
             "quality_score": quality_score,
             "summary": str(value.get("summary", "")).strip(),
-            "needs_more_research": bool(value.get("needs_more_research", False)),
+            "needs_more_research": needs_more_research,
             "issues": issues,
+            "search_queries": [query.strip() for query in search_queries],
         }
diff --git a/backend/app/agents/researcher.py b/backend/app/agents/researcher.py
index d469434..a00631e 100644
--- a/backend/app/agents/researcher.py
+++ b/backend/app/agents/researcher.py
@@ -25,7 +25,10 @@ class ResearcherAgent(BaseAgent):
 
     async def run(self, state: ResearchState) -> ResearchState:
         """搜索所有子问题，并把来源写入共享状态。"""
-        questions = [question.strip() for question in state.research_questions]
+        if state.pending_search_queries:
+            questions = [query.strip() for query in state.pending_search_queries]
+        else:
+            questions = [question.strip() for question in state.research_questions]
         questions = [question for question in questions if question]
         if not questions:
             raise ValueError("没有可执行的研究子问题")
@@ -47,6 +50,7 @@ class ResearcherAgent(BaseAgent):
             for source in state.sources
             if source.get("url")
         ]
+        state.pending_search_queries = []
         state.phase = "researching"
         return state
 
diff --git a/backend/app/agents/writer.py b/backend/app/agents/writer.py
index 09c8a70..ab341b3 100644
--- a/backend/app/agents/writer.py
+++ b/backend/app/agents/writer.py
@@ -29,7 +29,9 @@ class WriterAgent(BaseAgent):
                 "plan": state.plan,
                 "facts": state.facts,
                 "references": state.references,
-                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告。",
+                "review": state.review,
+                "iteration": state.iteration,
+                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
             },
         )
         report = report.strip()
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index 16a2b97..38864a9 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -103,6 +103,7 @@ class MockLLMClient(LLMClient):
                 "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                 "needs_more_research": not passed,
                 "issues": [] if passed else ["需要补充带来源的事实"],
+                "search_queries": [] if passed else ["补充权威来源和数据"],
             }
 
         raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")
@@ -137,6 +138,12 @@ class MockLLMClient(LLMClient):
         else:
             lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")
 
+        review = payload.get("review", {})
+        issues = review.get("issues", []) if isinstance(review, dict) else []
+        if issues:
+            lines.extend(["", "## 根据审核意见修订", ""])
+            lines.extend(f"- 已处理：{issue}" for issue in issues)
+
         lines.extend(
             [
                 "",
diff --git a/backend/app/domain/state.py b/backend/app/domain/state.py
index 8b9d21c..aad55ef 100644
--- a/backend/app/domain/state.py
+++ b/backend/app/domain/state.py
@@ -30,6 +30,7 @@ class ResearchState:
     # 规划结果
     plan: list[dict[str, Any]] = field(default_factory=list)
     research_questions: list[str] = field(default_factory=list)
+    pending_search_queries: list[str] = field(default_factory=list)
 
     # 研究证据
     sources: list[dict[str, Any]] = field(default_factory=list)
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
index e956752..59de0a3 100644
--- a/backend/app/workflow/research_workflow.py
+++ b/backend/app/workflow/research_workflow.py
@@ -18,7 +18,7 @@ class ResearchWorkflow:
     """Iteration 01 的最小同步编排器。
 
     每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
-    后续再在这个类上增加流式事件和审核修订循环。
+    SSE 和数据库等外层能力后续再加入；审核修订循环在本轮实现。
     """
 
     def __init__(
@@ -26,7 +26,11 @@ class ResearchWorkflow:
         llm: LLMClient,
         search: SearchClient,
         results_per_question: int = 3,
+        max_iterations: int = 1,
     ):
+        if max_iterations < 0:
+            raise ValueError("max_iterations 不能小于 0")
+        self.max_iterations = max_iterations
         self.planner = PlannerAgent(llm)
         self.researcher = ResearcherAgent(search, results_per_question)
         self.fact_extractor = FactExtractorAgent(llm)
@@ -42,13 +46,34 @@ class ResearchWorkflow:
         state = ResearchState(
             query=query,
             session_id=session_id or str(uuid4()),
+            max_iterations=self.max_iterations,
         )
 
         await self.planner.run(state)
         await self.researcher.run(state)
         await self.fact_extractor.run(state)
         await self.writer.run(state)
-        await self.critic.run(state)
+
+        while True:
+            await self.critic.run(state)
+            if state.review["verdict"] == "pass":
+                break
+            if state.iteration >= state.max_iterations:
+                break
+
+            state.iteration += 1
+            if state.review["needs_more_research"]:
+                state.pending_search_queries = (
+                    state.review["search_queries"]
+                    or state.review["issues"]
+                    or state.research_questions
+                )
+                await self.researcher.run(state)
+                await self.fact_extractor.run(state)
+
+            # 如果无需新搜索，Writer 根据 state.review 做内容修订；
+            # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
+            await self.writer.run(state)
 
         state.phase = "completed"
         return state
diff --git a/backend/tests/test_workflow.py b/backend/tests/test_workflow.py
index e831b4f..d7d675a 100644
--- a/backend/tests/test_workflow.py
+++ b/backend/tests/test_workflow.py
@@ -6,6 +6,41 @@ from app.core.search_client import MockSearchClient
 from app.workflow.research_workflow import ResearchWorkflow
 
 
+def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
+    return {
+        "verdict": verdict,
+        "quality_score": score,
+        "summary": "测试审核结果",
+        "needs_more_research": more_research,
+        "issues": issues or [],
+        "search_queries": search_queries or [],
+    }
+
+
+class SequencedReviewLLM(MockLLMClient):
+    def __init__(self, reviews):
+        self.reviews = iter(reviews)
+        self.writer_payloads = []
+
+    async def complete_json(self, role, payload):
+        if role == "critic":
+            return next(self.reviews)
+        return await super().complete_json(role, payload)
+
+    async def complete_text(self, role, payload):
+        self.writer_payloads.append(payload)
+        return await super().complete_text(role, payload)
+
+
+class RecordingSearchClient(MockSearchClient):
+    def __init__(self):
+        self.queries = []
+
+    async def search(self, query, limit=3):
+        self.queries.append(query)
+        return await super().search(query, limit)
+
+
 class ResearchWorkflowTests(unittest.TestCase):
     def test_workflow_runs_full_research_chain(self):
         workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
@@ -31,6 +66,78 @@ class ResearchWorkflowTests(unittest.TestCase):
 
         self.assertEqual(state.session_id, "session-001")
 
+    def test_critic_routes_to_supplementary_research_then_passes(self):
+        llm = SequencedReviewLLM(
+            [
+                review(
+                    "needs_revision",
+                    more_research=True,
+                    issues=["补充最新行业数据"],
+                    search_queries=["2025年新能源汽车行业数据"],
+                ),
+                review("pass", score=8.0),
+            ]
+        )
+        search = RecordingSearchClient()
+        workflow = ResearchWorkflow(llm, search, max_iterations=1)
+
+        state = asyncio.run(workflow.run("新能源汽车行业趋势"))
+
+        self.assertEqual(state.phase, "completed")
+        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.iteration, 1)
+        self.assertEqual(len(search.queries), 4)  # 3 个初始问题 + 1 个补充查询
+        self.assertEqual(search.queries[-1], "2025年新能源汽车行业数据")
+        self.assertEqual(len(state.sources), 4)
+        self.assertEqual(len(state.facts), 4)
+        self.assertIn("2025年新能源汽车行业数据", state.final_report)
+
+    def test_critic_routes_to_writer_revision_without_new_search(self):
+        llm = SequencedReviewLLM(
+            [
+                review(
+                    "needs_revision",
+                    issues=["补充结论与证据之间的说明"],
+                ),
+                review("pass", score=8.0),
+            ]
+        )
+        search = RecordingSearchClient()
+        workflow = ResearchWorkflow(llm, search, max_iterations=1)
+
+        state = asyncio.run(workflow.run("新能源汽车行业趋势"))
+
+        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.iteration, 1)
+        self.assertEqual(len(search.queries), 3)
+        self.assertEqual(len(llm.writer_payloads), 2)
+        self.assertIn(
+            "补充结论与证据之间的说明",
+            llm.writer_payloads[1]["review"]["issues"],
+        )
+        self.assertIn("补充结论与证据之间的说明", state.final_report)
+
+    def test_workflow_stops_after_max_iterations(self):
+        llm = SequencedReviewLLM(
+            [
+                review("needs_revision", issues=["第一轮问题"]),
+                review("needs_revision", issues=["仍需改进"], score=5.0),
+            ]
+        )
+        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)
+
+        state = asyncio.run(workflow.run("测试行业", session_id="bounded"))
+
+        self.assertEqual(state.phase, "completed")
+        self.assertEqual(state.iteration, 1)
+        self.assertEqual(state.review["verdict"], "needs_revision")
+        self.assertEqual(state.review["issues"], ["仍需改进"])
+        self.assertEqual(len(llm.writer_payloads), 2)
+
+    def test_workflow_rejects_negative_iteration_limit(self):
+        with self.assertRaisesRegex(ValueError, "max_iterations"):
+            ResearchWorkflow(MockLLMClient(), MockSearchClient(), max_iterations=-1)
+
 
 if __name__ == "__main__":
     unittest.main()
```

<a id="diff-787cd9a"></a>
### 提交 787cd9a：feat: add research workflow event stream

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/README.md b/README.md
index e01320a..6a93739 100644
--- a/README.md
+++ b/README.md
@@ -21,6 +21,37 @@
 
 每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。
 
+## 当前已跑通的后端链路
+
+```text
+用户问题
+  -> Planner 生成研究计划
+  -> Researcher 搜索来源
+  -> FactExtractor 整理带来源的事实
+  -> Writer 撰写报告
+  -> Critic 审核并决定通过、补充搜索或修订
+  -> 返回最终报告、评分和引用
+```
+
+工作流提供两种调用方式：
+
+- `await workflow.run(...)`：等待整条链路结束，返回 `ResearchState`。
+- `async for event in workflow.stream(...)`：按阶段取得进度事件，最后收到完整结果。
+
+事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
+不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。
+
+事件类型包括 `research_started`、`phase_started`、`plan_ready`、
+`research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
+最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。
+
+测试事件流：
+
+```powershell
+$env:PYTHONPATH = "backend"
+python -m unittest discover -s backend/tests -v
+```
+
 ## 命令行运行
 
 在项目根目录执行：
diff --git a/backend/app/domain/events.py b/backend/app/domain/events.py
new file mode 100644
index 0000000..4008527
--- /dev/null
+++ b/backend/app/domain/events.py
@@ -0,0 +1,38 @@
+"""研究工作流对外发布的事件格式。
+
+这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
+字典格式。以后无论接哪种传输方式，都可以把同一类事件发送给调用方。
+"""
+
+from __future__ import annotations
+
+from copy import deepcopy
+from dataclasses import dataclass, field
+from typing import Any
+
+
+@dataclass(frozen=True)
+class ResearchEvent:
+    """一次研究流程进度更新。
+
+    ``data`` 中的字段会在 ``to_dict`` 时展开到事件顶层，调用方因此可以
+    直接读取 ``event["report"]``、``event["references"]`` 等结果字段。
+    """
+
+    type: str
+    session_id: str
+    phase: str
+    iteration: int = 0
+    data: dict[str, Any] = field(default_factory=dict)
+
+    def to_dict(self) -> dict[str, Any]:
+        """转换成可被 API、SSE 或测试直接使用的普通字典。"""
+        event = {
+            "type": self.type,
+            "session_id": self.session_id,
+            "phase": self.phase,
+            "iteration": self.iteration,
+        }
+        event.update(deepcopy(self.data))
+        return event
+
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
index 59de0a3..34ee9c5 100644
--- a/backend/app/workflow/research_workflow.py
+++ b/backend/app/workflow/research_workflow.py
@@ -2,6 +2,8 @@
 
 from __future__ import annotations
 
+from collections.abc import AsyncIterator
+from typing import Any
 from uuid import uuid4
 
 from app.agents.critic import CriticAgent
@@ -11,13 +13,15 @@ from app.agents.researcher import ResearcherAgent
 from app.agents.writer import WriterAgent
 from app.core.llm_client import LLMClient
 from app.core.search_client import SearchClient
+from app.domain.events import ResearchEvent
 from app.domain.state import ResearchState
 
 
 class ResearchWorkflow:
-    """Iteration 01 的最小同步编排器。
+    """Iteration 01 的最小研究编排器。
 
     每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
+    ``run`` 适合一次性拿到结果，``stream`` 适合逐步消费进度事件。
     SSE 和数据库等外层能力后续再加入；审核修订循环在本轮实现。
     """
 
@@ -43,19 +47,96 @@ class ResearchWorkflow:
         session_id: str | None = None,
     ) -> ResearchState:
         """执行一次完整研究并返回最终状态。"""
-        state = ResearchState(
+        state = self._new_state(query, session_id)
+        async for _ in self._stream_state(state):
+            # run 保留一次性调用方式，只忽略中间事件。
+            pass
+        return state
+
+    async def stream(
+        self,
+        query: str,
+        session_id: str | None = None,
+    ) -> AsyncIterator[dict[str, Any]]:
+        """逐步产出研究进度事件，最后一个事件包含完整结果。
+
+        这个方法仍然使用和 ``run`` 相同的 Agent 和状态对象，因此不会
+        产生两套业务逻辑。当前返回普通字典，后续接 FastAPI SSE 时可以
+        直接序列化；暂时不需要启动真实服务就能测试事件顺序。
+        """
+        state = self._new_state(query, session_id)
+        async for event in self._stream_state(state):
+            yield event
+
+    def _new_state(
+        self,
+        query: str,
+        session_id: str | None,
+    ) -> ResearchState:
+        """创建一次研究任务的初始状态。"""
+        return ResearchState(
             query=query,
             session_id=session_id or str(uuid4()),
             max_iterations=self.max_iterations,
         )
 
+    async def _stream_state(
+        self,
+        state: ResearchState,
+    ) -> AsyncIterator[dict[str, Any]]:
+        """执行工作流并发布事件；``run`` 和 ``stream`` 共用此实现。"""
+        yield self._event(
+            state,
+            "research_started",
+            query=state.query,
+            max_iterations=state.max_iterations,
+        )
+
+        yield self._event(
+            state,
+            "phase_started",
+            phase="planning",
+            agent=self.planner.name,
+        )
         await self.planner.run(state)
-        await self.researcher.run(state)
-        await self.fact_extractor.run(state)
+        yield self._event(
+            state,
+            "plan_ready",
+            plan=state.plan,
+            research_questions=state.research_questions,
+        )
+
+        async for event in self._run_research_phase(state, supplementary=False):
+            yield event
+        yield self._event(
+            state,
+            "phase_started",
+            phase="writing",
+            agent=self.writer.name,
+        )
         await self.writer.run(state)
+        yield self._event(
+            state,
+            "draft_ready",
+            report=state.final_report,
+            revision=False,
+        )
 
         while True:
+            yield self._event(
+                state,
+                "phase_started",
+                phase="reviewing",
+                agent=self.critic.name,
+            )
             await self.critic.run(state)
+            yield self._event(
+                state,
+                "review_completed",
+                review=state.review,
+                quality_score=state.quality_score,
+            )
+
             if state.review["verdict"] == "pass":
                 break
             if state.iteration >= state.max_iterations:
@@ -68,12 +149,79 @@ class ResearchWorkflow:
                     or state.review["issues"]
                     or state.research_questions
                 )
-                await self.researcher.run(state)
-                await self.fact_extractor.run(state)
+                async for event in self._run_research_phase(
+                    state,
+                    supplementary=True,
+                ):
+                    yield event
 
             # 如果无需新搜索，Writer 根据 state.review 做内容修订；
             # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
+            yield self._event(
+                state,
+                "phase_started",
+                phase="writing",
+                agent=self.writer.name,
+                revision=True,
+            )
             await self.writer.run(state)
+            yield self._event(
+                state,
+                "draft_ready",
+                report=state.final_report,
+                revision=True,
+            )
 
         state.phase = "completed"
-        return state
+        yield self._event(
+            state,
+            "research_completed",
+            report=state.final_report,
+            quality_score=state.quality_score,
+            references=state.references,
+            review=state.review,
+        )
+
+    async def _run_research_phase(
+        self,
+        state: ResearchState,
+        *,
+        supplementary: bool,
+    ) -> AsyncIterator[dict[str, Any]]:
+        """运行搜索和事实提取，并逐步发布研究阶段事件。"""
+        yield self._event(
+            state,
+            "phase_started",
+            phase="researching",
+            agent=self.researcher.name,
+            supplementary=supplementary,
+        )
+        await self.researcher.run(state)
+        await self.fact_extractor.run(state)
+        yield self._event(
+            state,
+            "research_evidence_ready",
+            supplementary=supplementary,
+            source_count=len(state.sources),
+            fact_count=len(state.facts),
+            sources=state.sources,
+            facts=state.facts,
+            references=state.references,
+        )
+
+    @staticmethod
+    def _event(
+        state: ResearchState,
+        event_type: str,
+        *,
+        phase: str | None = None,
+        **data: Any,
+    ) -> dict[str, Any]:
+        """根据当前状态创建一个普通事件字典。"""
+        return ResearchEvent(
+            type=event_type,
+            session_id=state.session_id,
+            phase=phase or state.phase,
+            iteration=state.iteration,
+            data=data,
+        ).to_dict()
diff --git a/backend/tests/test_stream_workflow.py b/backend/tests/test_stream_workflow.py
new file mode 100644
index 0000000..161a6da
--- /dev/null
+++ b/backend/tests/test_stream_workflow.py
@@ -0,0 +1,102 @@
+import asyncio
+import unittest
+
+from app.core.llm_client import MockLLMClient
+from app.core.search_client import MockSearchClient
+from app.workflow.research_workflow import ResearchWorkflow
+
+
+def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
+    return {
+        "verdict": verdict,
+        "quality_score": score,
+        "summary": "测试审核结果",
+        "needs_more_research": more_research,
+        "issues": issues or [],
+        "search_queries": search_queries or [],
+    }
+
+
+class SequencedReviewLLM(MockLLMClient):
+    def __init__(self, reviews):
+        self.reviews = iter(reviews)
+
+    async def complete_json(self, role, payload):
+        if role == "critic":
+            return next(self.reviews)
+        return await super().complete_json(role, payload)
+
+
+async def collect_events(workflow, query, session_id=None):
+    return [
+        event
+        async for event in workflow.stream(query, session_id=session_id)
+    ]
+
+
+class StreamWorkflowTests(unittest.TestCase):
+    def test_stream_emits_ordered_events_and_final_result(self):
+        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
+
+        events = asyncio.run(
+            collect_events(
+                workflow,
+                "中国新能源汽车行业的发展趋势是什么？",
+                session_id="stream-001",
+            )
+        )
+
+        self.assertEqual(
+            [event["type"] for event in events],
+            [
+                "research_started",
+                "phase_started",
+                "plan_ready",
+                "phase_started",
+                "research_evidence_ready",
+                "phase_started",
+                "draft_ready",
+                "phase_started",
+                "review_completed",
+                "research_completed",
+            ],
+        )
+        self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
+        self.assertEqual(events[1]["phase"], "planning")
+        self.assertEqual(events[3]["phase"], "researching")
+        self.assertEqual(events[4]["source_count"], 3)
+        self.assertEqual(events[4]["fact_count"], 3)
+        self.assertEqual(events[-1]["phase"], "completed")
+        self.assertIn("## 执行摘要", events[-1]["report"])
+        self.assertEqual(events[-1]["quality_score"], 8.0)
+        self.assertEqual(len(events[-1]["references"]), 3)
+
+    def test_stream_marks_supplementary_research_iteration(self):
+        llm = SequencedReviewLLM(
+            [
+                review(
+                    "needs_revision",
+                    more_research=True,
+                    issues=["补充最新行业数据"],
+                    search_queries=["2025年新能源汽车行业数据"],
+                ),
+                review("pass", score=8.0),
+            ]
+        )
+        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)
+
+        events = asyncio.run(collect_events(workflow, "新能源汽车行业趋势"))
+
+        evidence_events = [
+            event for event in events if event["type"] == "research_evidence_ready"
+        ]
+        self.assertEqual(len(evidence_events), 2)
+        self.assertFalse(evidence_events[0]["supplementary"])
+        self.assertTrue(evidence_events[1]["supplementary"])
+        self.assertEqual(evidence_events[1]["iteration"], 1)
+        self.assertEqual(events[-1]["type"], "research_completed")
+        self.assertEqual(events[-1]["review"]["verdict"], "pass")
+
+
+if __name__ == "__main__":
+    unittest.main()
````

<a id="diff-ab7ffa3"></a>
### 提交 ab7ffa3：docs: define v2 core contract

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/docs/v2-core-contract.md b/docs/v2-core-contract.md
new file mode 100644
index 0000000..1c6646b
--- /dev/null
+++ b/docs/v2-core-contract.md
@@ -0,0 +1,95 @@
+# V2 核心功能对照契约
+
+这份文档用来约束学习版的长期方向。
+
+原项目的位置是 `D:\课\s4-6\industry_information_assistant`，学习版的位置是
+`D:\课\s4-6\information_deepresearch`。学习版会重新组织代码，但必须保留原项目
+V2 的核心研究行为。
+
+## 1. 最终核心链路
+
+```text
+用户问题
+  -> ChiefArchitect：规划大纲、研究问题和假设
+  -> DeepScout：搜索来源、深读内容、提取事实和数据
+  -> DataAnalyst：整理数据点、洞察、知识图谱和图表配置
+  -> CodeWizard：执行分析代码并生成图表
+  -> LeadWriter：撰写带引用的研究报告
+  -> CriticMaster：审核报告质量
+  -> 通过 / 补充搜索后重写 / 根据意见修订
+```
+
+学习版当前使用更容易理解的名称：
+
+| 原项目 V2 角色 | 学习版角色 | 当前状态 |
+| --- | --- | --- |
+| ChiefArchitect | `PlannerAgent` | 已有简化版 |
+| DeepScout | `ResearcherAgent` + `FactExtractorAgent` | 已有简化版 |
+| DataAnalyst | 待建立 `DataAnalystAgent` | 未实现 |
+| CodeWizard | 待建立 `CodeWizardAgent` | 未实现 |
+| LeadWriter | `WriterAgent` | 已有简化版 |
+| CriticMaster | `CriticAgent` | 已有简化版 |
+| V2 Graph | `ResearchWorkflow` | 已有简化版 |
+
+## 2. 必须保留的状态数据
+
+最终的 `ResearchState` 至少要能表达这些内容：
+
+- 用户问题、会话 ID、当前阶段和迭代次数
+- 章节大纲、研究子问题、研究假设和关键实体
+- 原始来源、结构化事实和数据点
+- 洞察、知识图谱、图表配置和代码执行记录
+- 草稿、最终报告和参考文献
+- 审核意见、质量评分和待补充搜索查询
+- 事件消息、日志、错误和任务状态
+
+当前 `iteration-01` 只实现了其中的基础字段；后续迭代逐步补齐，避免一次性复制原项目的大状态对象。
+
+## 3. 必须保留的审核路由
+
+审核结束后必须支持三种结果：
+
+1. `pass`：研究完成。
+2. `needs_revision` 且需要新证据：补充搜索，重新写作，再次审核。
+3. `needs_revision` 但不需要新证据：根据审核意见修订报告，再次审核。
+
+达到最大迭代次数时，流程可以结束，但必须保留最后一次审核结果和质量评分。
+
+## 4. 必须保留的对外结果
+
+最终结果必须包含：
+
+- 研究报告
+- 报告引用的来源
+- 结构化事实
+- 数据点和洞察（如果问题产生了数据）
+- 图表结果（如果问题需要图表）
+- 审核结论和质量评分
+- 研究迭代次数
+
+## 5. 版本边界
+
+学习版最终只保留 V2 研究入口：
+
+- 不保留 `version: v1/v2` 切换参数。
+- 不复制 V1 的 ReAct 研究服务和旧路由。
+- 不复制与核心研究无关的新闻、招投标、复杂知识库管理页面。
+- 前端只展示问题输入、研究进度、报告、引用和图表。
+
+## 6. 迭代验收顺序
+
+| 迭代 | 验收重点 |
+| --- | --- |
+| `iteration-01` | Mock 环境下跑通规划、搜索、事实、写作、审核和内部事件流 |
+| `iteration-02` | 对齐状态模型和事件协议，建立本契约对应的领域对象 |
+| `iteration-03` | 增加章节大纲、假设驱动研究、数据点和知识图谱基础 |
+| `iteration-04` | 实现 DataAnalyst，输出洞察和 ECharts 配置 |
+| `iteration-05` | 实现 CodeWizard，完成受限代码执行和图表记录 |
+| `iteration-06` | 对齐章节写作、引用和结构化审核反馈 |
+| `iteration-07` | 增加 FastAPI SSE 单一研究接口 |
+| `iteration-08` | 增加检查点、恢复和取消 |
+| `iteration-09` | 接入真实 LLM、Bocha 搜索和可选本地知识库 |
+| `iteration-10` | 建立简化前端 |
+| `iteration-11` | 完成端到端测试、V1 清理和文档整理 |
+
+每个迭代都必须先通过 Mock 测试，再考虑真实服务或外部基础设施。
````

<a id="diff-3986b40"></a>
### 提交 3986b40：Initial commit

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..2d06edc
--- /dev/null
+++ b/README.md
@@ -0,0 +1 @@
+# Information_deepresearch
\ No newline at end of file
```

<a id="diff-0a892dc"></a>
### 提交 0a892dc：chore: resolve README merge

完整 patch（原始 Git 输出，未省略）：

```diff

```

<a id="diff-39171ba"></a>
### 提交 39171ba：feat: add v2 domain models

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/domain/models.py b/backend/app/domain/models.py
new file mode 100644
index 0000000..c81e579
--- /dev/null
+++ b/backend/app/domain/models.py
@@ -0,0 +1,116 @@
+"""DeepResearch V2 使用的基础领域对象。
+
+这些对象先只描述数据形状，不负责调用 LLM、搜索服务或数据库。
+把数据形状单独放在这里，可以让后续 Agent 共享同一套结构。
+"""
+
+from __future__ import annotations
+
+from dataclasses import asdict, dataclass, field
+from typing import Any, Literal
+
+
+SectionType = Literal["qualitative", "quantitative", "mixed"]
+SectionStatus = Literal["pending", "researching", "drafted", "reviewed", "final"]
+HypothesisStatus = Literal[
+    "unverified",
+    "supported",
+    "refuted",
+    "partially_supported",
+]
+ChartType = Literal["line", "bar", "pie", "scatter", "table", "heatmap"]
+IssueType = Literal[
+    "missing_source",
+    "logic_error",
+    "bias",
+    "hallucination",
+    "outdated",
+    "incomplete",
+]
+IssueSeverity = Literal["critical", "major", "minor"]
+
+
+@dataclass
+class Section:
+    """研究报告中的一个章节。"""
+
+    id: str
+    title: str
+    description: str = ""
+    section_type: SectionType = "mixed"
+    status: SectionStatus = "pending"
+    content: str = ""
+    sources: list[str] = field(default_factory=list)
+    subsections: list[Section] = field(default_factory=list)
+    requires_data: bool = False
+    requires_chart: bool = False
+    priority: int = 0
+    search_queries: list[str] = field(default_factory=list)
+
+    def to_dict(self) -> dict[str, Any]:
+        """转换成可以放入 ResearchState 的普通字典。"""
+        return asdict(self)
+
+
+@dataclass
+class Hypothesis:
+    """研究开始时提出、再由证据验证的假设。"""
+
+    id: str
+    content: str
+    status: HypothesisStatus = "unverified"
+    evidence_for: list[str] = field(default_factory=list)
+    evidence_against: list[str] = field(default_factory=list)
+
+    def to_dict(self) -> dict[str, Any]:
+        return asdict(self)
+
+
+@dataclass
+class DataPoint:
+    """可以被分析或绘图使用的结构化数据点。"""
+
+    id: str
+    name: str
+    value: Any
+    unit: str = ""
+    year: int | None = None
+    source: str = ""
+    confidence: float = 0.0
+
+    def to_dict(self) -> dict[str, Any]:
+        return asdict(self)
+
+
+@dataclass
+class Chart:
+    """DataAnalyst 或 CodeWizard 生成的图表结果。"""
+
+    id: str
+    title: str
+    chart_type: ChartType
+    data: dict[str, Any] = field(default_factory=dict)
+    code: str = ""
+    image_path: str | None = None
+    image_base64: str | None = None
+    section_id: str | None = None
+
+    def to_dict(self) -> dict[str, Any]:
+        return asdict(self)
+
+
+@dataclass
+class CriticFeedback:
+    """审核 Agent 针对报告或章节提出的一条问题。"""
+
+    id: str
+    target_section: str
+    issue_type: IssueType
+    severity: IssueSeverity
+    description: str
+    suggestion: str
+    resolved: bool = False
+
+    def to_dict(self) -> dict[str, Any]:
+        return asdict(self)
+
diff --git a/backend/tests/test_domain_models.py b/backend/tests/test_domain_models.py
new file mode 100644
index 0000000..7093b5a
--- /dev/null
+++ b/backend/tests/test_domain_models.py
@@ -0,0 +1,76 @@
+import unittest
+
+from app.domain.models import (
+    Chart,
+    CriticFeedback,
+    DataPoint,
+    Hypothesis,
+    Section,
+)
+
+
+class DomainModelTests(unittest.TestCase):
+    def test_section_serializes_nested_sections(self):
+        section = Section(
+            id="sec-1",
+            title="行业概况",
+            description="研究行业规模和定义",
+            requires_data=True,
+            search_queries=["行业规模"],
+            subsections=[Section(id="sec-1-1", title="市场定义")],
+        )
+
+        result = section.to_dict()
+
+        self.assertEqual(result["id"], "sec-1")
+        self.assertTrue(result["requires_data"])
+        self.assertEqual(result["subsections"][0]["title"], "市场定义")
+
+    def test_model_collections_are_not_shared(self):
+        first = Hypothesis(id="h-1", content="第一个假设")
+        second = Hypothesis(id="h-2", content="第二个假设")
+
+        first.evidence_for.append("支持证据")
+
+        self.assertEqual(first.evidence_for, ["支持证据"])
+        self.assertEqual(second.evidence_for, [])
+
+    def test_data_point_and_chart_keep_analysis_fields(self):
+        data_point = DataPoint(
+            id="dp-1",
+            name="市场规模",
+            value=120.5,
+            unit="亿元",
+            year=2025,
+            source="https://example.com/source",
+            confidence=0.9,
+        )
+        chart = Chart(
+            id="chart-1",
+            title="市场规模趋势",
+            chart_type="line",
+            data={"x": [2024, 2025], "y": [100, 120.5]},
+            section_id="sec-1",
+        )
+
+        self.assertEqual(data_point.to_dict()["year"], 2025)
+        self.assertEqual(data_point.to_dict()["confidence"], 0.9)
+        self.assertEqual(chart.to_dict()["chart_type"], "line")
+        self.assertEqual(chart.to_dict()["section_id"], "sec-1")
+
+    def test_critic_feedback_starts_unresolved(self):
+        feedback = CriticFeedback(
+            id="issue-1",
+            target_section="sec-1",
+            issue_type="missing_source",
+            severity="major",
+            description="关键数据缺少来源",
+            suggestion="补充官方统计来源",
+        )
+
+        self.assertFalse(feedback.resolved)
+        self.assertEqual(feedback.to_dict()["severity"], "major")
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-a974120"></a>
### 提交 a974120：feat: extend research state for v2 data

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/domain/state.py b/backend/app/domain/state.py
index aad55ef..37ea70b 100644
--- a/backend/app/domain/state.py
+++ b/backend/app/domain/state.py
@@ -20,7 +20,8 @@ class ResearchState:
     query: str
     session_id: str = field(default_factory=lambda: str(uuid4()))
 
-    # 当前阶段：init / planning / researching / writing / reviewing / completed
+    # 当前阶段：init / planning / researching / analyzing / writing /
+    # reviewing / re_researching / revising / completed
     phase: str = "init"
 
     # 审核循环次数
@@ -29,18 +30,37 @@ class ResearchState:
 
     # 规划结果
     plan: list[dict[str, Any]] = field(default_factory=list)
+    # V2 章节大纲。当前仍用字典保存，后续 Planner 会逐步使用 Section。
+    outline: list[dict[str, Any]] = field(default_factory=list)
     research_questions: list[str] = field(default_factory=list)
+    key_entities: list[str] = field(default_factory=list)
+    hypotheses: list[dict[str, Any]] = field(default_factory=list)
+    mind_map: dict[str, Any] = field(default_factory=dict)
+    knowledge_graph: dict[str, Any] = field(
+        default_factory=lambda: {"nodes": [], "edges": []}
+    )
     pending_search_queries: list[str] = field(default_factory=list)
 
     # 研究证据
     sources: list[dict[str, Any]] = field(default_factory=list)
+    # raw_sources 保留原始搜索结果，sources 继续兼容 iteration-01 Agent。
+    raw_sources: list[dict[str, Any]] = field(default_factory=list)
     facts: list[dict[str, Any]] = field(default_factory=list)
+    data_points: list[dict[str, Any]] = field(default_factory=list)
+    insights: list[str] = field(default_factory=list)
     references: list[dict[str, Any]] = field(default_factory=list)
 
     # 写作和审核结果
+    draft_sections: dict[str, str] = field(default_factory=dict)
     final_report: str = ""
+    charts: list[dict[str, Any]] = field(default_factory=list)
+    code_executions: list[dict[str, Any]] = field(default_factory=list)
     review: dict[str, Any] = field(default_factory=dict)
+    critic_feedback: list[dict[str, Any]] = field(default_factory=list)
+    unresolved_issues: int = 0
     quality_score: float = 0.0
 
-    # 错误记录
+    # 运行记录
+    logs: list[dict[str, Any]] = field(default_factory=list)
+    messages: list[dict[str, Any]] = field(default_factory=list)
     errors: list[str] = field(default_factory=list)
diff --git a/backend/tests/test_state.py b/backend/tests/test_state.py
index 14c6b3b..a76b017 100644
--- a/backend/tests/test_state.py
+++ b/backend/tests/test_state.py
@@ -10,17 +10,35 @@ class ResearchStateTests(unittest.TestCase):
         self.assertEqual(state.query, "测试问题")
         self.assertEqual(state.phase, "init")
         self.assertEqual(state.plan, [])
+        self.assertEqual(state.outline, [])
+        self.assertEqual(state.hypotheses, [])
+        self.assertEqual(state.knowledge_graph, {"nodes": [], "edges": []})
         self.assertEqual(state.sources, [])
         self.assertEqual(state.facts, [])
+        self.assertEqual(state.data_points, [])
+        self.assertEqual(state.charts, [])
+        self.assertEqual(state.messages, [])
 
     def test_mutable_fields_are_not_shared(self):
         first = ResearchState("第一个问题")
         second = ResearchState("第二个问题")
 
         first.plan.append({"title": "只属于第一个任务"})
+        first.outline.append({"id": "sec-1"})
+        first.hypotheses.append({"id": "h-1"})
+        first.knowledge_graph["nodes"].append({"id": "node-1"})
+        first.data_points.append({"id": "dp-1"})
+        first.charts.append({"id": "chart-1"})
+        first.messages.append({"type": "progress"})
 
         self.assertEqual(len(first.plan), 1)
         self.assertEqual(second.plan, [])
+        self.assertEqual(second.outline, [])
+        self.assertEqual(second.hypotheses, [])
+        self.assertEqual(second.knowledge_graph, {"nodes": [], "edges": []})
+        self.assertEqual(second.data_points, [])
+        self.assertEqual(second.charts, [])
+        self.assertEqual(second.messages, [])
 
 
 if __name__ == "__main__":
```

<a id="diff-6bf3f4b"></a>
### 提交 6bf3f4b：refactor: align workflow state with v2 terminology

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/README.md b/README.md
index 6a93739..3da33e9 100644
--- a/README.md
+++ b/README.md
@@ -25,7 +25,7 @@
 
 ```text
 用户问题
-  -> Planner 生成研究计划
+  -> Planner 生成章节大纲
   -> Researcher 搜索来源
   -> FactExtractor 整理带来源的事实
   -> Writer 撰写报告
@@ -41,7 +41,7 @@
 事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
 不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。
 
-事件类型包括 `research_started`、`phase_started`、`plan_ready`、
+事件类型包括 `research_started`、`phase_started`、`outline_ready`、
 `research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
 最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。
 
diff --git a/backend/app/agents/critic.py b/backend/app/agents/critic.py
index bd636e0..cd5cbdd 100644
--- a/backend/app/agents/critic.py
+++ b/backend/app/agents/critic.py
@@ -28,13 +28,21 @@ class CriticAgent(BaseAgent):
                 "query": state.query,
                 "report": state.final_report,
                 "facts": state.facts,
-                "sources": state.sources,
+                "sources": state.raw_sources,
                 "iteration": state.iteration,
                 "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
             },
         )
         review = self._validate_review(result)
-        state.review = review
+        state.review_result = review
+        state.critic_feedback = [
+            {
+                "description": issue,
+                "resolved": False,
+            }
+            for issue in review["issues"]
+        ]
+        state.unresolved_issues = len(state.critic_feedback)
         state.quality_score = review["quality_score"]
         state.phase = "reviewing"
         return state
diff --git a/backend/app/agents/fact_extractor.py b/backend/app/agents/fact_extractor.py
index c33a634..b5ef859 100644
--- a/backend/app/agents/fact_extractor.py
+++ b/backend/app/agents/fact_extractor.py
@@ -19,18 +19,18 @@ class FactExtractorAgent(BaseAgent):
         self.llm = llm
 
     async def run(self, state: ResearchState) -> ResearchState:
-        if not state.sources:
+        if not state.raw_sources:
             raise ValueError("没有可供事实提取的来源")
 
         result = await self.llm.complete_json(
             role=self.name,
             payload={
                 "query": state.query,
-                "sources": state.sources,
+                "sources": state.raw_sources,
                 "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
             },
         )
-        facts = self._validate_facts(result.get("facts"), state.sources)
+        facts = self._validate_facts(result.get("facts"), state.raw_sources)
         state.facts = self._deduplicate_facts(state.facts + facts)
         state.phase = "researching"
         return state
diff --git a/backend/app/agents/planner.py b/backend/app/agents/planner.py
index b5673f3..7704071 100644
--- a/backend/app/agents/planner.py
+++ b/backend/app/agents/planner.py
@@ -31,28 +31,28 @@ class PlannerAgent(BaseAgent):
                 "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
             },
         )
-        plan = self._validate_plan(result.get("plan"))
+        outline = self._validate_outline(result.get("outline"))
         research_questions = self._validate_questions(result.get("research_questions"))
 
-        state.plan = plan
+        state.outline = outline
         state.research_questions = research_questions
         state.phase = "planning"
         return state
 
     @staticmethod
-    def _validate_plan(value: Any) -> list[dict[str, str]]:
-        """确保计划是由标题和描述组成的字典列表。"""
+    def _validate_outline(value: Any) -> list[dict[str, str]]:
+        """确保大纲是由标题和描述组成的字典列表。"""
         if not isinstance(value, list) or not value:
-            raise ValueError("Planner 返回的 plan 必须是非空列表")
+            raise ValueError("Planner 返回的 outline 必须是非空列表")
 
         validated: list[dict[str, str]] = []
         for index, item in enumerate(value, start=1):
             if not isinstance(item, dict):
-                raise ValueError(f"Planner 的第 {index} 个计划不是对象")
+                raise ValueError(f"Planner 的第 {index} 个章节不是对象")
             title = str(item.get("title", "")).strip()
             description = str(item.get("description", "")).strip()
             if not title or not description:
-                raise ValueError(f"Planner 的第 {index} 个计划缺少 title 或 description")
+                raise ValueError(f"Planner 的第 {index} 个章节缺少 title 或 description")
             validated.append({"title": title, "description": description})
         return validated
 
diff --git a/backend/app/agents/researcher.py b/backend/app/agents/researcher.py
index a00631e..f28515a 100644
--- a/backend/app/agents/researcher.py
+++ b/backend/app/agents/researcher.py
@@ -33,7 +33,7 @@ class ResearcherAgent(BaseAgent):
         if not questions:
             raise ValueError("没有可执行的研究子问题")
 
-        collected_sources = list(state.sources)
+        collected_sources = list(state.raw_sources)
         for question in questions:
             results = await self.search.search(
                 query=question,
@@ -41,13 +41,13 @@ class ResearcherAgent(BaseAgent):
             )
             collected_sources.extend(result.to_dict() for result in results)
 
-        state.sources = self._deduplicate_sources(collected_sources)
+        state.raw_sources = self._deduplicate_sources(collected_sources)
         state.references = [
             {
                 "title": source["title"],
                 "url": source["url"],
             }
-            for source in state.sources
+            for source in state.raw_sources
             if source.get("url")
         ]
         state.pending_search_queries = []
diff --git a/backend/app/agents/writer.py b/backend/app/agents/writer.py
index ab341b3..9161c4c 100644
--- a/backend/app/agents/writer.py
+++ b/backend/app/agents/writer.py
@@ -17,8 +17,8 @@ class WriterAgent(BaseAgent):
         self.llm = llm
 
     async def run(self, state: ResearchState) -> ResearchState:
-        if not state.plan:
-            raise ValueError("没有可用于写作的研究计划")
+        if not state.outline:
+            raise ValueError("没有可用于写作的研究大纲")
         if not state.facts:
             raise ValueError("没有可用于写作的事实")
 
@@ -26,10 +26,10 @@ class WriterAgent(BaseAgent):
             role=self.name,
             payload={
                 "query": state.query,
-                "plan": state.plan,
+                "outline": state.outline,
                 "facts": state.facts,
                 "references": state.references,
-                "review": state.review,
+                "review_result": state.review_result,
                 "iteration": state.iteration,
                 "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
             },
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index 38864a9..29f9a68 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -50,7 +50,7 @@ class MockLLMClient(LLMClient):
                 raise ValueError("planner 请求缺少 query")
 
             return {
-                "plan": [
+                "outline": [
                     {
                         "title": "现状与定义",
                         "description": f"明确“{query}”的研究范围和当前现状。",
@@ -138,7 +138,7 @@ class MockLLMClient(LLMClient):
         else:
             lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")
 
-        review = payload.get("review", {})
+        review = payload.get("review_result", {})
         issues = review.get("issues", []) if isinstance(review, dict) else []
         if issues:
             lines.extend(["", "## 根据审核意见修订", ""])
diff --git a/backend/app/domain/state.py b/backend/app/domain/state.py
index 37ea70b..928dab9 100644
--- a/backend/app/domain/state.py
+++ b/backend/app/domain/state.py
@@ -1,8 +1,7 @@
-"""DeepResearch 的共享工作状态。
+"""DeepResearch V2 的共享工作状态。
 
-第一轮先用一个普通 dataclass 表达状态。
-后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象，
-这样可以清楚看到信息如何在研究流程中流动。
+所有研究 Agent 读取和更新同一个任务状态。状态只保存数据，流程逻辑
+由 workflow 编排，领域对象由 domain.models 定义。
 """
 
 from __future__ import annotations
@@ -29,8 +28,7 @@ class ResearchState:
     max_iterations: int = 1
 
     # 规划结果
-    plan: list[dict[str, Any]] = field(default_factory=list)
-    # V2 章节大纲。当前仍用字典保存，后续 Planner 会逐步使用 Section。
+    # V2 章节大纲。后续 Planner 会逐步使用 domain.models.Section。
     outline: list[dict[str, Any]] = field(default_factory=list)
     research_questions: list[str] = field(default_factory=list)
     key_entities: list[str] = field(default_factory=list)
@@ -42,8 +40,7 @@ class ResearchState:
     pending_search_queries: list[str] = field(default_factory=list)
 
     # 研究证据
-    sources: list[dict[str, Any]] = field(default_factory=list)
-    # raw_sources 保留原始搜索结果，sources 继续兼容 iteration-01 Agent。
+    # 原始搜索结果；事实提取和后续分析都从这里读取。
     raw_sources: list[dict[str, Any]] = field(default_factory=list)
     facts: list[dict[str, Any]] = field(default_factory=list)
     data_points: list[dict[str, Any]] = field(default_factory=list)
@@ -55,7 +52,7 @@ class ResearchState:
     final_report: str = ""
     charts: list[dict[str, Any]] = field(default_factory=list)
     code_executions: list[dict[str, Any]] = field(default_factory=list)
-    review: dict[str, Any] = field(default_factory=dict)
+    review_result: dict[str, Any] = field(default_factory=dict)
     critic_feedback: list[dict[str, Any]] = field(default_factory=list)
     unresolved_issues: int = 0
     quality_score: float = 0.0
diff --git a/backend/app/scripts/run_research.py b/backend/app/scripts/run_research.py
index bbc5f00..c850bb5 100644
--- a/backend/app/scripts/run_research.py
+++ b/backend/app/scripts/run_research.py
@@ -12,7 +12,7 @@ from app.workflow.research_workflow import ResearchWorkflow
 
 
 def build_parser() -> argparse.ArgumentParser:
-    parser = argparse.ArgumentParser(description="运行一次 Iteration 01 DeepResearch")
+    parser = argparse.ArgumentParser(description="运行一次学习版 DeepResearch")
     parser.add_argument(
         "query",
         nargs="?",
@@ -25,13 +25,13 @@ def print_state(state: ResearchState) -> None:
     print("\n" + "=" * 60)
     print("研究计划")
     print("=" * 60)
-    for index, item in enumerate(state.plan, start=1):
+    for index, item in enumerate(state.outline, start=1):
         print(f"{index}. {item['title']}：{item['description']}")
 
     print("\n" + "=" * 60)
-    print(f"搜索来源（{len(state.sources)} 条）")
+    print(f"搜索来源（{len(state.raw_sources)} 条）")
     print("=" * 60)
-    for index, source in enumerate(state.sources, start=1):
+    for index, source in enumerate(state.raw_sources, start=1):
         print(f"{index}. {source['title']}")
         print(f"   URL: {source['url']}")
 
@@ -50,9 +50,9 @@ def print_state(state: ResearchState) -> None:
     print("\n" + "=" * 60)
     print("审核结果")
     print("=" * 60)
-    print(f"结论: {state.review['verdict']}")
+    print(f"结论: {state.review_result['verdict']}")
     print(f"评分: {state.quality_score}/10")
-    print(f"摘要: {state.review['summary']}")
+    print(f"摘要: {state.review_result['summary']}")
     print(f"任务阶段: {state.phase}")
     print(f"会话 ID: {state.session_id}")
 
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
index 34ee9c5..de559e5 100644
--- a/backend/app/workflow/research_workflow.py
+++ b/backend/app/workflow/research_workflow.py
@@ -101,8 +101,8 @@ class ResearchWorkflow:
         await self.planner.run(state)
         yield self._event(
             state,
-            "plan_ready",
-            plan=state.plan,
+            "outline_ready",
+            outline=state.outline,
             research_questions=state.research_questions,
         )
 
@@ -133,20 +133,21 @@ class ResearchWorkflow:
             yield self._event(
                 state,
                 "review_completed",
-                review=state.review,
+                review_result=state.review_result,
+                critic_feedback=state.critic_feedback,
                 quality_score=state.quality_score,
             )
 
-            if state.review["verdict"] == "pass":
+            if state.review_result["verdict"] == "pass":
                 break
             if state.iteration >= state.max_iterations:
                 break
 
             state.iteration += 1
-            if state.review["needs_more_research"]:
+            if state.review_result["needs_more_research"]:
                 state.pending_search_queries = (
-                    state.review["search_queries"]
-                    or state.review["issues"]
+                    state.review_result["search_queries"]
+                    or state.review_result["issues"]
                     or state.research_questions
                 )
                 async for event in self._run_research_phase(
@@ -155,7 +156,7 @@ class ResearchWorkflow:
                 ):
                     yield event
 
-            # 如果无需新搜索，Writer 根据 state.review 做内容修订；
+            # 如果无需新搜索，Writer 根据 review_result 做内容修订；
             # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
             yield self._event(
                 state,
@@ -179,7 +180,8 @@ class ResearchWorkflow:
             report=state.final_report,
             quality_score=state.quality_score,
             references=state.references,
-            review=state.review,
+            review_result=state.review_result,
+            critic_feedback=state.critic_feedback,
         )
 
     async def _run_research_phase(
@@ -202,9 +204,9 @@ class ResearchWorkflow:
             state,
             "research_evidence_ready",
             supplementary=supplementary,
-            source_count=len(state.sources),
+            source_count=len(state.raw_sources),
             fact_count=len(state.facts),
-            sources=state.sources,
+            sources=state.raw_sources,
             facts=state.facts,
             references=state.references,
         )
diff --git a/backend/tests/test_critic.py b/backend/tests/test_critic.py
index e46fd9c..0c31349 100644
--- a/backend/tests/test_critic.py
+++ b/backend/tests/test_critic.py
@@ -34,9 +34,9 @@ class CriticAgentTests(unittest.TestCase):
         state = asyncio.run(run_chain())
 
         self.assertEqual(state.phase, "reviewing")
-        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.review_result["verdict"], "pass")
         self.assertEqual(state.quality_score, 8.0)
-        self.assertEqual(state.review["issues"], [])
+        self.assertEqual(state.review_result["issues"], [])
 
     def test_critic_rejects_invalid_result(self):
         state = ResearchState("测试问题")
diff --git a/backend/tests/test_fact_extractor.py b/backend/tests/test_fact_extractor.py
index 3468327..f619157 100644
--- a/backend/tests/test_fact_extractor.py
+++ b/backend/tests/test_fact_extractor.py
@@ -26,7 +26,7 @@ class BrokenFactClient(LLMClient):
 
 
 class FactExtractorAgentTests(unittest.TestCase):
-    def test_fact_extractor_turns_sources_into_facts(self):
+    def test_fact_extractor_turns_raw_sources_into_facts(self):
         async def run_chain():
             state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
             await PlannerAgent(MockLLMClient()).run(state)
@@ -37,14 +37,14 @@ class FactExtractorAgentTests(unittest.TestCase):
         state = asyncio.run(run_chain())
 
         self.assertEqual(state.phase, "researching")
-        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(len(state.raw_sources), 3)
         self.assertEqual(len(state.facts), 3)
         self.assertTrue(all(fact["source_url"] for fact in state.facts))
         self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
 
     def test_fact_extractor_rejects_unknown_source_url(self):
         state = ResearchState("测试问题")
-        state.sources = [
+        state.raw_sources = [
             {
                 "title": "已知来源",
                 "url": "https://known.example.com",
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
index 7386590..5fa64e7 100644
--- a/backend/tests/test_llm_client.py
+++ b/backend/tests/test_llm_client.py
@@ -18,7 +18,7 @@ class LLMClientTests(unittest.TestCase):
             )
         )
 
-        self.assertEqual(len(result["plan"]), 3)
+        self.assertEqual(len(result["outline"]), 3)
         self.assertEqual(len(result["research_questions"]), 3)
         self.assertIn("新能源汽车", result["research_questions"][0])
 
diff --git a/backend/tests/test_planner.py b/backend/tests/test_planner.py
index ecae6f1..b9b97e3 100644
--- a/backend/tests/test_planner.py
+++ b/backend/tests/test_planner.py
@@ -8,14 +8,14 @@ from app.domain.state import ResearchState
 
 class BrokenPlannerClient(LLMClient):
     async def complete_json(self, role, payload):
-        return {"plan": [], "research_questions": []}
+        return {"outline": [], "research_questions": []}
 
     async def complete_text(self, role, payload):
         return ""
 
 
 class PlannerAgentTests(unittest.TestCase):
-    def test_planner_writes_plan_into_state(self):
+    def test_planner_writes_outline_into_state(self):
         state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
         agent = PlannerAgent(MockLLMClient())
 
@@ -23,9 +23,9 @@ class PlannerAgentTests(unittest.TestCase):
 
         self.assertIs(result, state)
         self.assertEqual(result.phase, "planning")
-        self.assertEqual(len(result.plan), 3)
+        self.assertEqual(len(result.outline), 3)
         self.assertEqual(len(result.research_questions), 3)
-        self.assertIn("新能源汽车", result.plan[0]["description"])
+        self.assertIn("新能源汽车", result.outline[0]["description"])
 
     def test_planner_rejects_empty_query(self):
         with self.assertRaises(ValueError):
diff --git a/backend/tests/test_researcher.py b/backend/tests/test_researcher.py
index c21e2a0..c82c549 100644
--- a/backend/tests/test_researcher.py
+++ b/backend/tests/test_researcher.py
@@ -20,9 +20,9 @@ class ResearcherAgentTests(unittest.TestCase):
 
         self.assertEqual(state.phase, "researching")
         self.assertEqual(len(state.research_questions), 3)
-        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(len(state.raw_sources), 3)
         self.assertEqual(len(state.references), 3)
-        self.assertTrue(all(source["url"].startswith("https://") for source in state.sources))
+        self.assertTrue(all(source["url"].startswith("https://") for source in state.raw_sources))
 
     def test_researcher_deduplicates_existing_source_urls(self):
         async def run():
@@ -32,7 +32,7 @@ class ResearcherAgentTests(unittest.TestCase):
 
         state = asyncio.run(run())
 
-        self.assertEqual(len(state.sources), 1)
+        self.assertEqual(len(state.raw_sources), 1)
         self.assertEqual(len(state.references), 1)
 
     def test_researcher_rejects_missing_questions(self):
diff --git a/backend/tests/test_state.py b/backend/tests/test_state.py
index a76b017..60cccfd 100644
--- a/backend/tests/test_state.py
+++ b/backend/tests/test_state.py
@@ -9,30 +9,30 @@ class ResearchStateTests(unittest.TestCase):
 
         self.assertEqual(state.query, "测试问题")
         self.assertEqual(state.phase, "init")
-        self.assertEqual(state.plan, [])
         self.assertEqual(state.outline, [])
         self.assertEqual(state.hypotheses, [])
         self.assertEqual(state.knowledge_graph, {"nodes": [], "edges": []})
-        self.assertEqual(state.sources, [])
+        self.assertEqual(state.raw_sources, [])
         self.assertEqual(state.facts, [])
         self.assertEqual(state.data_points, [])
         self.assertEqual(state.charts, [])
         self.assertEqual(state.messages, [])
+        self.assertFalse(hasattr(state, "plan"))
+        self.assertFalse(hasattr(state, "sources"))
+        self.assertFalse(hasattr(state, "review"))
 
     def test_mutable_fields_are_not_shared(self):
         first = ResearchState("第一个问题")
         second = ResearchState("第二个问题")
 
-        first.plan.append({"title": "只属于第一个任务"})
-        first.outline.append({"id": "sec-1"})
+        first.outline.append({"title": "只属于第一个任务"})
         first.hypotheses.append({"id": "h-1"})
         first.knowledge_graph["nodes"].append({"id": "node-1"})
         first.data_points.append({"id": "dp-1"})
         first.charts.append({"id": "chart-1"})
         first.messages.append({"type": "progress"})
 
-        self.assertEqual(len(first.plan), 1)
-        self.assertEqual(second.plan, [])
+        self.assertEqual(len(first.outline), 1)
         self.assertEqual(second.outline, [])
         self.assertEqual(second.hypotheses, [])
         self.assertEqual(second.knowledge_graph, {"nodes": [], "edges": []})
diff --git a/backend/tests/test_stream_workflow.py b/backend/tests/test_stream_workflow.py
index 161a6da..0705796 100644
--- a/backend/tests/test_stream_workflow.py
+++ b/backend/tests/test_stream_workflow.py
@@ -51,7 +51,7 @@ class StreamWorkflowTests(unittest.TestCase):
             [
                 "research_started",
                 "phase_started",
-                "plan_ready",
+                "outline_ready",
                 "phase_started",
                 "research_evidence_ready",
                 "phase_started",
@@ -95,7 +95,7 @@ class StreamWorkflowTests(unittest.TestCase):
         self.assertTrue(evidence_events[1]["supplementary"])
         self.assertEqual(evidence_events[1]["iteration"], 1)
         self.assertEqual(events[-1]["type"], "research_completed")
-        self.assertEqual(events[-1]["review"]["verdict"], "pass")
+        self.assertEqual(events[-1]["review_result"]["verdict"], "pass")
 
 
 if __name__ == "__main__":
diff --git a/backend/tests/test_workflow.py b/backend/tests/test_workflow.py
index d7d675a..300c44f 100644
--- a/backend/tests/test_workflow.py
+++ b/backend/tests/test_workflow.py
@@ -50,11 +50,11 @@ class ResearchWorkflowTests(unittest.TestCase):
         )
 
         self.assertEqual(state.phase, "completed")
-        self.assertEqual(state.plan[0]["title"], "现状与定义")
-        self.assertEqual(len(state.sources), 3)
+        self.assertEqual(state.outline[0]["title"], "现状与定义")
+        self.assertEqual(len(state.raw_sources), 3)
         self.assertEqual(len(state.facts), 3)
         self.assertTrue(state.final_report)
-        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.review_result["verdict"], "pass")
         self.assertEqual(state.quality_score, 8.0)
 
     def test_workflow_preserves_explicit_session_id(self):
@@ -84,11 +84,11 @@ class ResearchWorkflowTests(unittest.TestCase):
         state = asyncio.run(workflow.run("新能源汽车行业趋势"))
 
         self.assertEqual(state.phase, "completed")
-        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.review_result["verdict"], "pass")
         self.assertEqual(state.iteration, 1)
         self.assertEqual(len(search.queries), 4)  # 3 个初始问题 + 1 个补充查询
         self.assertEqual(search.queries[-1], "2025年新能源汽车行业数据")
-        self.assertEqual(len(state.sources), 4)
+        self.assertEqual(len(state.raw_sources), 4)
         self.assertEqual(len(state.facts), 4)
         self.assertIn("2025年新能源汽车行业数据", state.final_report)
 
@@ -107,13 +107,13 @@ class ResearchWorkflowTests(unittest.TestCase):
 
         state = asyncio.run(workflow.run("新能源汽车行业趋势"))
 
-        self.assertEqual(state.review["verdict"], "pass")
+        self.assertEqual(state.review_result["verdict"], "pass")
         self.assertEqual(state.iteration, 1)
         self.assertEqual(len(search.queries), 3)
         self.assertEqual(len(llm.writer_payloads), 2)
         self.assertIn(
             "补充结论与证据之间的说明",
-            llm.writer_payloads[1]["review"]["issues"],
+            llm.writer_payloads[1]["review_result"]["issues"],
         )
         self.assertIn("补充结论与证据之间的说明", state.final_report)
 
@@ -130,8 +130,8 @@ class ResearchWorkflowTests(unittest.TestCase):
 
         self.assertEqual(state.phase, "completed")
         self.assertEqual(state.iteration, 1)
-        self.assertEqual(state.review["verdict"], "needs_revision")
-        self.assertEqual(state.review["issues"], ["仍需改进"])
+        self.assertEqual(state.review_result["verdict"], "needs_revision")
+        self.assertEqual(state.review_result["issues"], ["仍需改进"])
         self.assertEqual(len(llm.writer_payloads), 2)
 
     def test_workflow_rejects_negative_iteration_limit(self):
diff --git a/backend/tests/test_writer.py b/backend/tests/test_writer.py
index 26775a8..6f9c24f 100644
--- a/backend/tests/test_writer.py
+++ b/backend/tests/test_writer.py
@@ -28,16 +28,16 @@ class WriterAgentTests(unittest.TestCase):
         self.assertIn("研究发现", state.final_report)
         self.assertIn("https://example.com/research/", state.final_report)
 
-    def test_writer_requires_plan(self):
+    def test_writer_requires_outline(self):
         state = ResearchState("测试问题")
         state.facts = [{"content": "事实", "source_url": "https://example.com"}]
 
-        with self.assertRaisesRegex(ValueError, "研究计划"):
+        with self.assertRaisesRegex(ValueError, "研究大纲"):
             asyncio.run(WriterAgent(MockLLMClient()).run(state))
 
     def test_writer_requires_facts(self):
         state = ResearchState("测试问题")
-        state.plan = [{"title": "章节", "description": "描述"}]
+        state.outline = [{"title": "章节", "description": "描述"}]
 
         with self.assertRaisesRegex(ValueError, "事实"):
             asyncio.run(WriterAgent(MockLLMClient()).run(state))
````

<a id="diff-b582dec"></a>
### 提交 b582dec：feat: normalize planner output into v2 models

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/planner.py b/backend/app/agents/planner.py
index 7704071..5c5a2f8 100644
--- a/backend/app/agents/planner.py
+++ b/backend/app/agents/planner.py
@@ -5,13 +5,14 @@ from __future__ import annotations
 from typing import Any
 
 from app.core.llm_client import LLMClient
+from app.domain.models import Hypothesis, Section
 from app.domain.state import ResearchState
 
 from .base import BaseAgent
 
 
 class PlannerAgent(BaseAgent):
-    """把一个用户问题拆成可执行的研究计划。"""
+    """把一个用户问题转换成 V2 研究大纲和可验证假设。"""
 
     name = "planner"
 
@@ -32,20 +33,25 @@ class PlannerAgent(BaseAgent):
             },
         )
         outline = self._validate_outline(result.get("outline"))
+        hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
         research_questions = self._validate_questions(result.get("research_questions"))
+        key_entities = self._validate_key_entities(result.get("key_entities", []))
 
         state.outline = outline
+        state.hypotheses = hypotheses
         state.research_questions = research_questions
+        state.key_entities = key_entities
+        state.mind_map = result.get("mind_map", {})
         state.phase = "planning"
         return state
 
     @staticmethod
-    def _validate_outline(value: Any) -> list[dict[str, str]]:
-        """确保大纲是由标题和描述组成的字典列表。"""
+    def _validate_outline(value: Any) -> list[dict[str, Any]]:
+        """用 Section 校验并序列化 LLM 返回的章节大纲。"""
         if not isinstance(value, list) or not value:
             raise ValueError("Planner 返回的 outline 必须是非空列表")
 
-        validated: list[dict[str, str]] = []
+        validated: list[dict[str, Any]] = []
         for index, item in enumerate(value, start=1):
             if not isinstance(item, dict):
                 raise ValueError(f"Planner 的第 {index} 个章节不是对象")
@@ -53,9 +59,90 @@ class PlannerAgent(BaseAgent):
             description = str(item.get("description", "")).strip()
             if not title or not description:
                 raise ValueError(f"Planner 的第 {index} 个章节缺少 title 或 description")
-            validated.append({"title": title, "description": description})
+
+            section_type = str(item.get("section_type", "mixed")).strip() or "mixed"
+            if section_type not in {"qualitative", "quantitative", "mixed"}:
+                raise ValueError(f"Planner 的第 {index} 个章节 section_type 无效")
+
+            status = str(item.get("status", "pending")).strip() or "pending"
+            if status not in {"pending", "researching", "drafted", "reviewed", "final"}:
+                raise ValueError(f"Planner 的第 {index} 个章节 status 无效")
+
+            search_queries = item.get("search_queries", [title])
+            if not isinstance(search_queries, list):
+                raise ValueError(f"Planner 的第 {index} 个章节 search_queries 必须是列表")
+            search_queries = [str(query).strip() for query in search_queries if str(query).strip()]
+            if not search_queries:
+                search_queries = [title]
+
+            section = Section(
+                id=str(item.get("id", f"sec_{index}")).strip() or f"sec_{index}",
+                title=title,
+                description=description,
+                section_type=section_type,
+                status=status,
+                requires_data=bool(item.get("requires_data", False)),
+                requires_chart=bool(item.get("requires_chart", False)),
+                priority=int(item.get("priority", index)),
+                search_queries=search_queries,
+            )
+            validated.append(section.to_dict())
+        return validated
+
+    @staticmethod
+    def _validate_hypotheses(value: Any) -> list[dict[str, Any]]:
+        """用 Hypothesis 校验研究假设，并初始化证据列表。"""
+        if value is None:
+            return []
+        if not isinstance(value, list):
+            raise ValueError("Planner 返回的 hypotheses 必须是列表")
+
+        validated: list[dict[str, Any]] = []
+        allowed_statuses = {
+            "unverified",
+            "supported",
+            "refuted",
+            "partially_supported",
+        }
+        for index, item in enumerate(value, start=1):
+            if not isinstance(item, dict):
+                raise ValueError(f"Planner 的第 {index} 个假设不是对象")
+            content = str(item.get("content", "")).strip()
+            if not content:
+                raise ValueError(f"Planner 的第 {index} 个假设缺少 content")
+            status = str(item.get("status", "unverified")).strip() or "unverified"
+            if status not in allowed_statuses:
+                raise ValueError(f"Planner 的第 {index} 个假设 status 无效")
+
+            hypothesis = Hypothesis(
+                id=str(item.get("id", f"h_{index}")).strip() or f"h_{index}",
+                content=content,
+                status=status,
+                evidence_for=[str(evidence).strip() for evidence in item.get("evidence_for", [])],
+                evidence_against=[
+                    str(evidence).strip() for evidence in item.get("evidence_against", [])
+                ],
+            )
+            validated.append(hypothesis.to_dict())
         return validated
 
+    @staticmethod
+    def _validate_key_entities(value: Any) -> list[str]:
+        """兼容字符串或带 name 的实体对象，并统一成名称列表。"""
+        if value is None:
+            return []
+        if not isinstance(value, list):
+            raise ValueError("Planner 返回的 key_entities 必须是列表")
+
+        entities: list[str] = []
+        for item in value:
+            if isinstance(item, dict):
+                item = item.get("name", "")
+            name = str(item).strip()
+            if name:
+                entities.append(name)
+        return entities
+
     @staticmethod
     def _validate_questions(value: Any) -> list[str]:
         """确保子问题是非空字符串列表。"""
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index 29f9a68..e4fd5ef 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -69,6 +69,14 @@ class MockLLMClient(LLMClient):
                     f"{query} 面临哪些主要问题，有哪些公开证据？",
                     f"{query} 的未来趋势和改进建议是什么？",
                 ],
+                "hypotheses": [
+                    {
+                        "id": "h_1",
+                        "content": f"{query} 的发展趋势会受到政策和市场需求共同影响。",
+                        "status": "unverified",
+                    }
+                ],
+                "key_entities": [],
             }
 
         if role == "fact_extractor":
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
index de559e5..621059a 100644
--- a/backend/app/workflow/research_workflow.py
+++ b/backend/app/workflow/research_workflow.py
@@ -104,6 +104,9 @@ class ResearchWorkflow:
             "outline_ready",
             outline=state.outline,
             research_questions=state.research_questions,
+            hypotheses=state.hypotheses,
+            key_entities=state.key_entities,
+            mind_map=state.mind_map,
         )
 
         async for event in self._run_research_phase(state, supplementary=False):
diff --git a/backend/tests/test_llm_client.py b/backend/tests/test_llm_client.py
index 5fa64e7..a17b618 100644
--- a/backend/tests/test_llm_client.py
+++ b/backend/tests/test_llm_client.py
@@ -20,6 +20,7 @@ class LLMClientTests(unittest.TestCase):
 
         self.assertEqual(len(result["outline"]), 3)
         self.assertEqual(len(result["research_questions"]), 3)
+        self.assertEqual(result["hypotheses"][0]["status"], "unverified")
         self.assertIn("新能源汽车", result["research_questions"][0])
 
     def test_mock_fact_extractor_returns_source_grounded_facts(self):
diff --git a/backend/tests/test_planner.py b/backend/tests/test_planner.py
index b9b97e3..e1ff9f7 100644
--- a/backend/tests/test_planner.py
+++ b/backend/tests/test_planner.py
@@ -25,6 +25,10 @@ class PlannerAgentTests(unittest.TestCase):
         self.assertEqual(result.phase, "planning")
         self.assertEqual(len(result.outline), 3)
         self.assertEqual(len(result.research_questions), 3)
+        self.assertEqual(result.outline[0]["id"], "sec_1")
+        self.assertEqual(result.outline[0]["status"], "pending")
+        self.assertEqual(len(result.hypotheses), 1)
+        self.assertEqual(result.hypotheses[0]["status"], "unverified")
         self.assertIn("新能源汽车", result.outline[0]["description"])
 
     def test_planner_rejects_empty_query(self):
diff --git a/backend/tests/test_stream_workflow.py b/backend/tests/test_stream_workflow.py
index 0705796..3b1a1eb 100644
--- a/backend/tests/test_stream_workflow.py
+++ b/backend/tests/test_stream_workflow.py
@@ -63,6 +63,8 @@ class StreamWorkflowTests(unittest.TestCase):
         )
         self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
         self.assertEqual(events[1]["phase"], "planning")
+        self.assertEqual(len(events[2]["outline"]), 3)
+        self.assertEqual(events[2]["hypotheses"][0]["status"], "unverified")
         self.assertEqual(events[3]["phase"], "researching")
         self.assertEqual(events[4]["source_count"], 3)
         self.assertEqual(events[4]["fact_count"], 3)
```

<a id="diff-0c0ecb5"></a>
### 提交 0c0ecb5：feat: associate research sources with outline sections

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/agents/fact_extractor.py b/backend/app/agents/fact_extractor.py
index b5ef859..55b1912 100644
--- a/backend/app/agents/fact_extractor.py
+++ b/backend/app/agents/fact_extractor.py
@@ -45,6 +45,11 @@ class FactExtractorAgent(BaseAgent):
             for source in sources
             if source.get("url")
         }
+        source_by_url = {
+            str(source.get("url", "")).strip(): source
+            for source in sources
+            if source.get("url")
+        }
         validated: list[dict[str, Any]] = []
         for index, item in enumerate(value, start=1):
             if not isinstance(item, dict):
@@ -64,15 +69,18 @@ class FactExtractorAgent(BaseAgent):
             if not 0 <= confidence <= 1:
                 raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间")
 
-            validated.append(
-                {
-                    "content": content,
-                    "source_title": str(item.get("source_title", "")).strip(),
-                    "source_url": source_url,
-                    "source_type": str(item.get("source_type", "web")).strip() or "web",
-                    "confidence": confidence,
-                }
-            )
+            fact = {
+                "content": content,
+                "source_title": str(item.get("source_title", "")).strip(),
+                "source_url": source_url,
+                "source_type": str(item.get("source_type", "web")).strip() or "web",
+                "confidence": confidence,
+            }
+            source_context = source_by_url[source_url]
+            for field_name in ("section_id", "section_title"):
+                if source_context.get(field_name):
+                    fact[field_name] = source_context[field_name]
+            validated.append(fact)
         return validated
 
     @staticmethod
diff --git a/backend/app/agents/researcher.py b/backend/app/agents/researcher.py
index f28515a..e3e33b7 100644
--- a/backend/app/agents/researcher.py
+++ b/backend/app/agents/researcher.py
@@ -9,7 +9,7 @@ from .base import BaseAgent
 
 
 class ResearcherAgent(BaseAgent):
-    """根据研究子问题收集候选来源。
+    """根据章节大纲中的搜索查询收集候选来源。
 
     这一版只负责搜索和去重。事实提取会在后续步骤使用 LLM 单独完成，
     这样每个 Agent 的输入和输出都更容易观察。
@@ -24,22 +24,30 @@ class ResearcherAgent(BaseAgent):
         self.results_per_question = results_per_question
 
     async def run(self, state: ResearchState) -> ResearchState:
-        """搜索所有子问题，并把来源写入共享状态。"""
+        """搜索章节查询，并把来源与章节关联后写入共享状态。"""
         if state.pending_search_queries:
-            questions = [query.strip() for query in state.pending_search_queries]
+            tasks = [
+                {"query": query.strip(), "section_id": "", "section_title": ""}
+                for query in state.pending_search_queries
+            ]
         else:
-            questions = [question.strip() for question in state.research_questions]
-        questions = [question for question in questions if question]
-        if not questions:
+            tasks = self._build_search_tasks(state)
+        tasks = [task for task in tasks if task["query"]]
+        if not tasks:
             raise ValueError("没有可执行的研究子问题")
 
         collected_sources = list(state.raw_sources)
-        for question in questions:
+        for task in tasks:
             results = await self.search.search(
-                query=question,
+                query=task["query"],
                 limit=self.results_per_question,
             )
-            collected_sources.extend(result.to_dict() for result in results)
+            for result in results:
+                source = result.to_dict()
+                if task["section_id"]:
+                    source["section_id"] = task["section_id"]
+                    source["section_title"] = task["section_title"]
+                collected_sources.append(source)
 
         state.raw_sources = self._deduplicate_sources(collected_sources)
         state.references = [
@@ -54,6 +62,35 @@ class ResearcherAgent(BaseAgent):
         state.phase = "researching"
         return state
 
+    @staticmethod
+    def _build_search_tasks(state: ResearchState) -> list[dict[str, str]]:
+        """把章节大纲转换成搜索任务；没有大纲时回退到研究问题。"""
+        tasks: list[dict[str, str]] = []
+        for section in state.outline:
+            section_id = str(section.get("id", "")).strip()
+            section_title = str(section.get("title", "")).strip()
+            queries = section.get("search_queries") or [section_title]
+            if not isinstance(queries, list):
+                raise ValueError("章节 search_queries 必须是列表")
+            for query in queries:
+                query = str(query).strip()
+                if query:
+                    tasks.append(
+                        {
+                            "query": query,
+                            "section_id": section_id,
+                            "section_title": section_title,
+                        }
+                    )
+
+        if tasks:
+            return tasks
+
+        return [
+            {"query": str(question).strip(), "section_id": "", "section_title": ""}
+            for question in state.research_questions
+        ]
+
     @staticmethod
     def _deduplicate_sources(sources: list[dict]) -> list[dict]:
         """按 URL 去重，同时保留第一次出现的顺序。"""
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index e4fd5ef..c7f9a07 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -54,14 +54,17 @@ class MockLLMClient(LLMClient):
                     {
                         "title": "现状与定义",
                         "description": f"明确“{query}”的研究范围和当前现状。",
+                        "search_queries": [f"{query} 的当前现状和关键定义"],
                     },
                     {
                         "title": "问题与证据",
                         "description": "整理公开来源中的事实、数据和主要争议。",
+                        "search_queries": [f"{query} 的主要问题和公开证据"],
                     },
                     {
                         "title": "趋势与建议",
                         "description": "根据已有证据判断未来趋势并提出建议。",
+                        "search_queries": [f"{query} 的未来趋势和改进建议"],
                     },
                 ],
                 "research_questions": [
diff --git a/backend/tests/test_fact_extractor.py b/backend/tests/test_fact_extractor.py
index f619157..71b6d97 100644
--- a/backend/tests/test_fact_extractor.py
+++ b/backend/tests/test_fact_extractor.py
@@ -41,6 +41,11 @@ class FactExtractorAgentTests(unittest.TestCase):
         self.assertEqual(len(state.facts), 3)
         self.assertTrue(all(fact["source_url"] for fact in state.facts))
         self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
+        self.assertEqual(
+            {fact["section_id"] for fact in state.facts},
+            {"sec_1", "sec_2", "sec_3"},
+        )
+        self.assertTrue(all(fact["section_title"] for fact in state.facts))
 
     def test_fact_extractor_rejects_unknown_source_url(self):
         state = ResearchState("测试问题")
diff --git a/backend/tests/test_researcher.py b/backend/tests/test_researcher.py
index c82c549..54a3da9 100644
--- a/backend/tests/test_researcher.py
+++ b/backend/tests/test_researcher.py
@@ -23,6 +23,33 @@ class ResearcherAgentTests(unittest.TestCase):
         self.assertEqual(len(state.raw_sources), 3)
         self.assertEqual(len(state.references), 3)
         self.assertTrue(all(source["url"].startswith("https://") for source in state.raw_sources))
+        self.assertEqual(
+            {source["section_id"] for source in state.raw_sources},
+            {"sec_1", "sec_2", "sec_3"},
+        )
+
+    def test_researcher_uses_all_queries_from_a_section(self):
+        async def run():
+            state = ResearchState("测试问题")
+            state.outline = [
+                {
+                    "id": "sec-market",
+                    "title": "市场规模",
+                    "search_queries": ["市场规模 2024", "市场规模 2025"],
+                }
+            ]
+            return await ResearcherAgent(MockSearchClient()).run(state)
+
+        state = asyncio.run(run())
+
+        self.assertEqual(len(state.raw_sources), 2)
+        self.assertEqual(
+            {source["query"] for source in state.raw_sources},
+            {"市场规模 2024", "市场规模 2025"},
+        )
+        self.assertTrue(
+            all(source["section_id"] == "sec-market" for source in state.raw_sources)
+        )
 
     def test_researcher_deduplicates_existing_source_urls(self):
         async def run():
```

<a id="diff-0387dc8"></a>
### 提交 0387dc8：feat: add section level drafting

完整 patch（原始 Git 输出，未省略）：

````diff
diff --git a/README.md b/README.md
index 3da33e9..e378ca7 100644
--- a/README.md
+++ b/README.md
@@ -15,6 +15,7 @@
 ## 当前迭代
 
 - iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
+- iteration-02（进行中）：对齐 V2 领域字段；来源、事实、章节草稿和进度事件可以按章节追踪。
 - 后续迭代：加入结构化数据分析、图表、检查点、本地知识库和简化前端。
 
 ## 学习方式
@@ -26,9 +27,9 @@
 ```text
 用户问题
   -> Planner 生成章节大纲
-  -> Researcher 搜索来源
-  -> FactExtractor 整理带来源的事实
-  -> Writer 撰写报告
+  -> Researcher 按章节查询搜索来源
+  -> FactExtractor 整理带章节关联的事实
+  -> Writer 逐章生成草稿，再整合报告
   -> Critic 审核并决定通过、补充搜索或修订
   -> 返回最终报告、评分和引用
 ```
@@ -43,6 +44,7 @@
 
 事件类型包括 `research_started`、`phase_started`、`outline_ready`、
 `research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
+`draft_ready` 事件还包含 `outline` 和 `draft_sections`，可以按章节读取中间结果。
 最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。
 
 测试事件流：
diff --git a/backend/app/agents/writer.py b/backend/app/agents/writer.py
index 9161c4c..d1dd4be 100644
--- a/backend/app/agents/writer.py
+++ b/backend/app/agents/writer.py
@@ -9,7 +9,7 @@ from .base import BaseAgent
 
 
 class WriterAgent(BaseAgent):
-    """根据研究计划和带来源事实生成 Markdown 报告。"""
+    """按章节整理事实，并生成带来源的 Markdown 报告。"""
 
     name = "writer"
 
@@ -22,22 +22,103 @@ class WriterAgent(BaseAgent):
         if not state.facts:
             raise ValueError("没有可用于写作的事实")
 
+        draft_sections: dict[str, str] = {}
+        normalized_outline: list[dict] = []
+        outline_ids = {
+            str(section.get("id", "")).strip()
+            for section in state.outline
+            if str(section.get("id", "")).strip()
+        }
+        unassigned_facts = [
+            fact
+            for fact in state.facts
+            if str(fact.get("section_id", "")).strip() not in outline_ids
+        ]
+        for index, raw_section in enumerate(state.outline, start=1):
+            section = dict(raw_section)
+            section_id = str(section.get("id", f"sec_{index}")).strip() or f"sec_{index}"
+            section["id"] = section_id
+            section_title = str(section.get("title", "")).strip() or f"第 {index} 节"
+            section["title"] = section_title
+
+            related_facts = self._facts_for_section(state.facts, section_id)
+            if index == 1 and unassigned_facts:
+                related_facts = self._merge_facts(related_facts, unassigned_facts)
+            section_content = await self.llm.complete_text(
+                role=self.name,
+                payload={
+                    "mode": "section",
+                    "query": state.query,
+                    "section": section,
+                    "facts": related_facts,
+                    "data_points": state.data_points,
+                    "insights": state.insights,
+                    "charts": state.charts,
+                    "review_result": state.review_result,
+                    "iteration": state.iteration,
+                    "instruction": "只生成本章节正文，不要重复章节标题；每个事实都保留可点击来源链接。",
+                },
+            )
+            section_content = section_content.strip()
+            if not section_content:
+                raise ValueError(f"Writer 没有生成章节内容: {section_title}")
+
+            section["status"] = "drafted"
+            draft_sections[section_id] = section_content
+            normalized_outline.append(section)
+
         report = await self.llm.complete_text(
             role=self.name,
             payload={
+                "mode": "report",
                 "query": state.query,
-                "outline": state.outline,
+                "outline": normalized_outline,
                 "facts": state.facts,
+                "draft_sections": draft_sections,
+                "data_points": state.data_points,
+                "insights": state.insights,
+                "charts": state.charts,
                 "references": state.references,
                 "review_result": state.review_result,
                 "iteration": state.iteration,
-                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
+                "instruction": "整合各章节草稿，生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
             },
         )
         report = report.strip()
         if not report:
             raise ValueError("Writer 没有生成报告内容")
 
+        state.outline = normalized_outline
+        state.draft_sections = draft_sections
         state.final_report = report
         state.phase = "writing"
         return state
+
+    @staticmethod
+    def _facts_for_section(
+        facts: list[dict],
+        section_id: str,
+    ) -> list[dict]:
+        """优先选择当前章节的事实；没有关联时回退到全部事实。"""
+        related = [
+            fact
+            for fact in facts
+            if str(fact.get("section_id", "")).strip() == section_id
+        ]
+        return related or facts
+
+    @staticmethod
+    def _merge_facts(*groups: list[dict]) -> list[dict]:
+        """合并事实并按来源和内容去重。"""
+        merged: list[dict] = []
+        seen: set[tuple[str, str]] = set()
+        for group in groups:
+            for fact in group:
+                key = (
+                    str(fact.get("source_url", "")).strip(),
+                    str(fact.get("content", "")).strip(),
+                )
+                if key not in seen:
+                    seen.add(key)
+                    merged.append(fact)
+        return merged
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index c7f9a07..51807d0 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -131,6 +131,57 @@ class MockLLMClient(LLMClient):
         if not query:
             raise ValueError("writer 请求缺少 query")
 
+        if payload.get("mode") == "section":
+            section = payload.get("section", {})
+            title = str(section.get("title", "本章节")).strip() or "本章节"
+            facts = payload.get("facts", [])
+            lines = [f"本章节围绕“{title}”整理研究证据。"]
+            for fact in facts:
+                content = str(fact.get("content", "")).strip()
+                if not content:
+                    continue
+                source_title = str(fact.get("source_title", "来源")).strip() or "来源"
+                source_url = str(fact.get("source_url", "")).strip()
+                citation = f" ([{source_title}]({source_url}))" if source_url else ""
+                lines.append(f"- {content}{citation}")
+            if len(lines) == 1:
+                lines.append("当前章节还没有可引用的事实。")
+            return "\n".join(lines)
+
+        if payload.get("mode") == "report":
+            outline = payload.get("outline", [])
+            draft_sections = payload.get("draft_sections", {})
+            lines = [
+                "## 执行摘要",
+                "",
+                f"本报告围绕“{query}”整理公开资料，并按研究大纲组织可验证证据。",
+                "",
+                "## 研究发现",
+                "",
+            ]
+            for index, section in enumerate(outline, start=1):
+                section_id = str(section.get("id", f"sec_{index}")).strip()
+                title = str(section.get("title", f"第 {index} 节")).strip()
+                content = str(draft_sections.get(section_id, "")).strip()
+                if content:
+                    lines.extend([f"### {index}. {title}", "", content, ""])
+
+            review = payload.get("review_result", {})
+            issues = review.get("issues", []) if isinstance(review, dict) else []
+            if issues:
+                lines.extend(["## 根据审核意见修订", ""])
+                lines.extend(f"- 已处理：{issue}" for issue in issues)
+                lines.append("")
+
+            lines.extend(
+                [
+                    "## 结论",
+                    "",
+                    "以上结论需要结合更多官方统计和行业报告继续验证。",
+                ]
+            )
+            return "\n".join(lines)
+
         facts = payload.get("facts", [])
         lines = [
             "## 执行摘要",
diff --git a/backend/app/workflow/research_workflow.py b/backend/app/workflow/research_workflow.py
index 621059a..da367ff 100644
--- a/backend/app/workflow/research_workflow.py
+++ b/backend/app/workflow/research_workflow.py
@@ -18,7 +18,7 @@ from app.domain.state import ResearchState
 
 
 class ResearchWorkflow:
-    """Iteration 01 的最小研究编排器。
+    """学习版 DeepResearch 的研究编排器。
 
     每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
     ``run`` 适合一次性拿到结果，``stream`` 适合逐步消费进度事件。
@@ -122,6 +122,8 @@ class ResearchWorkflow:
             state,
             "draft_ready",
             report=state.final_report,
+            outline=state.outline,
+            draft_sections=state.draft_sections,
             revision=False,
         )
 
@@ -173,6 +175,8 @@ class ResearchWorkflow:
                 state,
                 "draft_ready",
                 report=state.final_report,
+                outline=state.outline,
+                draft_sections=state.draft_sections,
                 revision=True,
             )
 
diff --git a/backend/tests/test_stream_workflow.py b/backend/tests/test_stream_workflow.py
index 3b1a1eb..ac0fbf0 100644
--- a/backend/tests/test_stream_workflow.py
+++ b/backend/tests/test_stream_workflow.py
@@ -68,6 +68,10 @@ class StreamWorkflowTests(unittest.TestCase):
         self.assertEqual(events[3]["phase"], "researching")
         self.assertEqual(events[4]["source_count"], 3)
         self.assertEqual(events[4]["fact_count"], 3)
+        self.assertEqual(
+            set(events[6]["draft_sections"]),
+            {"sec_1", "sec_2", "sec_3"},
+        )
         self.assertEqual(events[-1]["phase"], "completed")
         self.assertIn("## 执行摘要", events[-1]["report"])
         self.assertEqual(events[-1]["quality_score"], 8.0)
diff --git a/backend/tests/test_workflow.py b/backend/tests/test_workflow.py
index 300c44f..6bdffcf 100644
--- a/backend/tests/test_workflow.py
+++ b/backend/tests/test_workflow.py
@@ -110,10 +110,13 @@ class ResearchWorkflowTests(unittest.TestCase):
         self.assertEqual(state.review_result["verdict"], "pass")
         self.assertEqual(state.iteration, 1)
         self.assertEqual(len(search.queries), 3)
-        self.assertEqual(len(llm.writer_payloads), 2)
+        report_payloads = [
+            payload for payload in llm.writer_payloads if payload.get("mode") == "report"
+        ]
+        self.assertEqual(len(report_payloads), 2)
         self.assertIn(
             "补充结论与证据之间的说明",
-            llm.writer_payloads[1]["review_result"]["issues"],
+            report_payloads[1]["review_result"]["issues"],
         )
         self.assertIn("补充结论与证据之间的说明", state.final_report)
 
@@ -132,7 +135,10 @@ class ResearchWorkflowTests(unittest.TestCase):
         self.assertEqual(state.iteration, 1)
         self.assertEqual(state.review_result["verdict"], "needs_revision")
         self.assertEqual(state.review_result["issues"], ["仍需改进"])
-        self.assertEqual(len(llm.writer_payloads), 2)
+        self.assertEqual(
+            len([payload for payload in llm.writer_payloads if payload.get("mode") == "report"]),
+            2,
+        )
 
     def test_workflow_rejects_negative_iteration_limit(self):
         with self.assertRaisesRegex(ValueError, "max_iterations"):
diff --git a/backend/tests/test_writer.py b/backend/tests/test_writer.py
index 6f9c24f..b077a2a 100644
--- a/backend/tests/test_writer.py
+++ b/backend/tests/test_writer.py
@@ -27,6 +27,13 @@ class WriterAgentTests(unittest.TestCase):
         self.assertTrue(state.final_report.startswith("## 执行摘要"))
         self.assertIn("研究发现", state.final_report)
         self.assertIn("https://example.com/research/", state.final_report)
+        self.assertEqual(
+            set(state.draft_sections),
+            {"sec_1", "sec_2", "sec_3"},
+        )
+        self.assertTrue(all(section["status"] == "drafted" for section in state.outline))
+        for section in state.outline:
+            self.assertIn(section["title"], state.final_report)
 
     def test_writer_requires_outline(self):
         state = ResearchState("测试问题")
@@ -42,6 +49,36 @@ class WriterAgentTests(unittest.TestCase):
         with self.assertRaisesRegex(ValueError, "事实"):
             asyncio.run(WriterAgent(MockLLMClient()).run(state))
 
+    def test_writer_prefers_facts_from_the_matching_section(self):
+        async def run():
+            state = ResearchState("测试问题")
+            state.outline = [
+                {"id": "sec-a", "title": "A 章节", "description": "A 描述"},
+                {"id": "sec-b", "title": "B 章节", "description": "B 描述"},
+            ]
+            state.facts = [
+                {
+                    "content": "A 事实",
+                    "source_title": "A 来源",
+                    "source_url": "https://example.com/a",
+                    "section_id": "sec-a",
+                },
+                {
+                    "content": "B 事实",
+                    "source_title": "B 来源",
+                    "source_url": "https://example.com/b",
+                    "section_id": "sec-b",
+                },
+            ]
+            return await WriterAgent(MockLLMClient()).run(state)
+
+        state = asyncio.run(run())
+
+        self.assertIn("A 事实", state.draft_sections["sec-a"])
+        self.assertNotIn("B 事实", state.draft_sections["sec-a"])
+        self.assertIn("B 事实", state.draft_sections["sec-b"])
+        self.assertNotIn("A 事实", state.draft_sections["sec-b"])
+
 
 if __name__ == "__main__":
     unittest.main()
diff --git a/docs/v2-core-contract.md b/docs/v2-core-contract.md
index 1c6646b..aea8bde 100644
--- a/docs/v2-core-contract.md
+++ b/docs/v2-core-contract.md
@@ -43,7 +43,8 @@ V2 的核心研究行为。
 - 审核意见、质量评分和待补充搜索查询
 - 事件消息、日志、错误和任务状态
 
-当前 `iteration-01` 只实现了其中的基础字段；后续迭代逐步补齐，避免一次性复制原项目的大状态对象。
+当前 `iteration-02` 已经把章节大纲、章节查询、来源和事实的关联字段接入工作流；
+数据分析、图表和检查点仍在后续迭代逐步补齐，避免一次性复制原项目的大状态对象。
 
 ## 3. 必须保留的审核路由
 
````

<a id="diff-99fe715"></a>
### 提交 99fe715：feat: validate research event envelope

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/domain/events.py b/backend/app/domain/events.py
index 4008527..91b0e67 100644
--- a/backend/app/domain/events.py
+++ b/backend/app/domain/events.py
@@ -11,6 +11,45 @@ from dataclasses import dataclass, field
 from typing import Any
 
 
+class ResearchEventType:
+    """工作流允许对外发布的事件类型。"""
+
+    RESEARCH_STARTED = "research_started"
+    PHASE_STARTED = "phase_started"
+    OUTLINE_READY = "outline_ready"
+    RESEARCH_EVIDENCE_READY = "research_evidence_ready"
+    DRAFT_READY = "draft_ready"
+    REVIEW_COMPLETED = "review_completed"
+    RESEARCH_COMPLETED = "research_completed"
+
+
+EVENT_TYPES = frozenset(
+    {
+        ResearchEventType.RESEARCH_STARTED,
+        ResearchEventType.PHASE_STARTED,
+        ResearchEventType.OUTLINE_READY,
+        ResearchEventType.RESEARCH_EVIDENCE_READY,
+        ResearchEventType.DRAFT_READY,
+        ResearchEventType.REVIEW_COMPLETED,
+        ResearchEventType.RESEARCH_COMPLETED,
+    }
+)
+
+RESEARCH_PHASES = frozenset(
+    {
+        "init",
+        "planning",
+        "researching",
+        "analyzing",
+        "writing",
+        "reviewing",
+        "re_researching",
+        "revising",
+        "completed",
+    }
+)
+
+
 @dataclass(frozen=True)
 class ResearchEvent:
     """一次研究流程进度更新。
@@ -25,6 +64,21 @@ class ResearchEvent:
     iteration: int = 0
     data: dict[str, Any] = field(default_factory=dict)
 
+    def __post_init__(self) -> None:
+        """校验所有事件共有的外层字段。"""
+        if not isinstance(self.type, str) or self.type not in EVENT_TYPES:
+            raise ValueError(f"不支持的研究事件类型: {self.type!r}")
+        if not isinstance(self.session_id, str) or not self.session_id.strip():
+            raise ValueError("研究事件 session_id 不能为空")
+        if not isinstance(self.phase, str) or self.phase not in RESEARCH_PHASES:
+            raise ValueError(f"不支持的研究阶段: {self.phase!r}")
+        if isinstance(self.iteration, bool) or not isinstance(self.iteration, int):
+            raise ValueError("研究事件 iteration 必须是整数")
+        if self.iteration < 0:
+            raise ValueError("研究事件 iteration 不能小于 0")
+        if not isinstance(self.data, dict):
+            raise ValueError("研究事件 data 必须是字典")
+
     def to_dict(self) -> dict[str, Any]:
         """转换成可被 API、SSE 或测试直接使用的普通字典。"""
         event = {
diff --git a/backend/tests/test_events.py b/backend/tests/test_events.py
new file mode 100644
index 0000000..132d592
--- /dev/null
+++ b/backend/tests/test_events.py
@@ -0,0 +1,63 @@
+import unittest
+
+from app.domain.events import (
+    EVENT_TYPES,
+    RESEARCH_PHASES,
+    ResearchEvent,
+    ResearchEventType,
+)
+
+
+class ResearchEventTests(unittest.TestCase):
+    def test_event_type_constants_are_registered(self):
+        self.assertIn(ResearchEventType.OUTLINE_READY, EVENT_TYPES)
+        self.assertIn("planning", RESEARCH_PHASES)
+
+    def test_event_to_dict_keeps_common_fields_and_data(self):
+        event = ResearchEvent(
+            type=ResearchEventType.OUTLINE_READY,
+            session_id="session-001",
+            phase="planning",
+            iteration=0,
+            data={"outline": [{"id": "sec-1"}]},
+        )
+
+        self.assertEqual(
+            event.to_dict(),
+            {
+                "type": "outline_ready",
+                "session_id": "session-001",
+                "phase": "planning",
+                "iteration": 0,
+                "outline": [{"id": "sec-1"}],
+            },
+        )
+
+    def test_event_rejects_unknown_type(self):
+        with self.assertRaisesRegex(ValueError, "事件类型"):
+            ResearchEvent("unknown", "session-001", "planning")
+
+    def test_event_rejects_empty_session_id(self):
+        with self.assertRaisesRegex(ValueError, "session_id"):
+            ResearchEvent(ResearchEventType.PHASE_STARTED, "  ", "planning")
+
+    def test_event_rejects_unknown_phase(self):
+        with self.assertRaisesRegex(ValueError, "研究阶段"):
+            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "unknown")
+
+    def test_event_rejects_invalid_iteration(self):
+        with self.assertRaisesRegex(ValueError, "iteration"):
+            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "planning", -1)
+
+    def test_event_rejects_non_dict_data(self):
+        with self.assertRaisesRegex(ValueError, "data"):
+            ResearchEvent(
+                ResearchEventType.PHASE_STARTED,
+                "session-001",
+                "planning",
+                data=[],
+            )
+
+
+if __name__ == "__main__":
+    unittest.main()
```

<a id="diff-fad4cdb"></a>
### 提交 fad4cdb：feat: define required research event fields

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/backend/app/domain/events.py b/backend/app/domain/events.py
index 91b0e67..533ad8f 100644
--- a/backend/app/domain/events.py
+++ b/backend/app/domain/events.py
@@ -49,6 +49,26 @@ RESEARCH_PHASES = frozenset(
     }
 )
 
+EVENT_REQUIRED_FIELDS = {
+    ResearchEventType.RESEARCH_STARTED: frozenset({"query", "max_iterations"}),
+    ResearchEventType.PHASE_STARTED: frozenset({"agent"}),
+    ResearchEventType.OUTLINE_READY: frozenset(
+        {"outline", "research_questions", "hypotheses", "key_entities", "mind_map"}
+    ),
+    ResearchEventType.RESEARCH_EVIDENCE_READY: frozenset(
+        {"supplementary", "source_count", "fact_count", "sources", "facts", "references"}
+    ),
+    ResearchEventType.DRAFT_READY: frozenset(
+        {"report", "outline", "draft_sections", "revision"}
+    ),
+    ResearchEventType.REVIEW_COMPLETED: frozenset(
+        {"review_result", "critic_feedback", "quality_score"}
+    ),
+    ResearchEventType.RESEARCH_COMPLETED: frozenset(
+        {"report", "quality_score", "references", "review_result", "critic_feedback"}
+    ),
+}
+
 
 @dataclass(frozen=True)
 class ResearchEvent:
@@ -78,6 +98,10 @@ class ResearchEvent:
             raise ValueError("研究事件 iteration 不能小于 0")
         if not isinstance(self.data, dict):
             raise ValueError("研究事件 data 必须是字典")
+        missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()
+        if missing_fields:
+            missing = ", ".join(sorted(missing_fields))
+            raise ValueError(f"{self.type} 缺少必需字段: {missing}")
 
     def to_dict(self) -> dict[str, Any]:
         """转换成可被 API、SSE 或测试直接使用的普通字典。"""
diff --git a/backend/tests/test_events.py b/backend/tests/test_events.py
index 132d592..398b2d2 100644
--- a/backend/tests/test_events.py
+++ b/backend/tests/test_events.py
@@ -2,6 +2,7 @@ import unittest
 
 from app.domain.events import (
     EVENT_TYPES,
+    EVENT_REQUIRED_FIELDS,
     RESEARCH_PHASES,
     ResearchEvent,
     ResearchEventType,
@@ -18,8 +19,13 @@ class ResearchEventTests(unittest.TestCase):
             type=ResearchEventType.OUTLINE_READY,
             session_id="session-001",
             phase="planning",
-            iteration=0,
-            data={"outline": [{"id": "sec-1"}]},
+            data={
+                "outline": [{"id": "sec-1"}],
+                "research_questions": [],
+                "hypotheses": [],
+                "key_entities": [],
+                "mind_map": {},
+            },
         )
 
         self.assertEqual(
@@ -30,9 +36,28 @@ class ResearchEventTests(unittest.TestCase):
                 "phase": "planning",
                 "iteration": 0,
                 "outline": [{"id": "sec-1"}],
+                "research_questions": [],
+                "hypotheses": [],
+                "key_entities": [],
+                "mind_map": {},
             },
         )
 
+    def test_each_event_type_declares_required_fields(self):
+        self.assertEqual(set(EVENT_TYPES), set(EVENT_REQUIRED_FIELDS))
+        self.assertTrue(
+            all(fields for fields in EVENT_REQUIRED_FIELDS.values()),
+        )
+
+    def test_event_rejects_missing_business_fields(self):
+        with self.assertRaisesRegex(ValueError, "outline_ready.*必需字段"):
+            ResearchEvent(
+                ResearchEventType.OUTLINE_READY,
+                "session-001",
+                "planning",
+                data={"outline": []},
+            )
+
     def test_event_rejects_unknown_type(self):
         with self.assertRaisesRegex(ValueError, "事件类型"):
             ResearchEvent("unknown", "session-001", "planning")
```

<a id="diff-79db291"></a>
### 提交 79db291：chore: complete iteration 02 contract

完整 patch（原始 Git 输出，未省略）：

```diff
diff --git a/README.md b/README.md
index e378ca7..b944887 100644
--- a/README.md
+++ b/README.md
@@ -15,7 +15,7 @@
 ## 当前迭代
 
 - iteration-01：建立研究状态、规划、搜索、写作和审核的最小链路。
-- iteration-02（进行中）：对齐 V2 领域字段；来源、事实、章节草稿和进度事件可以按章节追踪。
+- iteration-02：对齐 V2 领域字段；来源、事实和章节草稿可以按章节追踪，并固定进度事件协议。
 - 后续迭代：加入结构化数据分析、图表、检查点、本地知识库和简化前端。
 
 ## 学习方式
@@ -46,6 +46,8 @@
 `research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
 `draft_ready` 事件还包含 `outline` 和 `draft_sections`，可以按章节读取中间结果。
 最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。
+所有事件都有 `type`、`session_id`、`phase` 和 `iteration`；每种事件的必需业务字段
+见 `backend/app/domain/events.py` 中的 `EVENT_REQUIRED_FIELDS`。
 
 测试事件流：
 
diff --git a/backend/app/domain/events.py b/backend/app/domain/events.py
index 533ad8f..6fbca23 100644
--- a/backend/app/domain/events.py
+++ b/backend/app/domain/events.py
@@ -69,6 +69,8 @@ EVENT_REQUIRED_FIELDS = {
     ),
 }
 
+EVENT_ENVELOPE_FIELDS = frozenset({"type", "session_id", "phase", "iteration"})
+
 
 @dataclass(frozen=True)
 class ResearchEvent:
@@ -98,6 +100,10 @@ class ResearchEvent:
             raise ValueError("研究事件 iteration 不能小于 0")
         if not isinstance(self.data, dict):
             raise ValueError("研究事件 data 必须是字典")
+        reserved_fields = EVENT_ENVELOPE_FIELDS & self.data.keys()
+        if reserved_fields:
+            reserved = ", ".join(sorted(reserved_fields))
+            raise ValueError(f"研究事件 data 不能覆盖公共字段: {reserved}")
         missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()
         if missing_fields:
             missing = ", ".join(sorted(missing_fields))
diff --git a/backend/tests/test_events.py b/backend/tests/test_events.py
index 398b2d2..5377d57 100644
--- a/backend/tests/test_events.py
+++ b/backend/tests/test_events.py
@@ -83,6 +83,15 @@ class ResearchEventTests(unittest.TestCase):
                 data=[],
             )
 
+    def test_event_data_cannot_replace_common_fields(self):
+        with self.assertRaisesRegex(ValueError, "session_id"):
+            ResearchEvent(
+                ResearchEventType.PHASE_STARTED,
+                "session-001",
+                "planning",
+                data={"agent": "planner", "session_id": "other-session"},
+            )
+
 
 if __name__ == "__main__":
     unittest.main()
diff --git a/docs/v2-core-contract.md b/docs/v2-core-contract.md
index aea8bde..0bf1448 100644
--- a/docs/v2-core-contract.md
+++ b/docs/v2-core-contract.md
@@ -83,10 +83,10 @@ V2 的核心研究行为。
 | --- | --- |
 | `iteration-01` | Mock 环境下跑通规划、搜索、事实、写作、审核和内部事件流 |
 | `iteration-02` | 对齐状态模型和事件协议，建立本契约对应的领域对象 |
-| `iteration-03` | 增加章节大纲、假设驱动研究、数据点和知识图谱基础 |
+| `iteration-03` | 增加假设驱动研究、数据点和知识图谱基础 |
 | `iteration-04` | 实现 DataAnalyst，输出洞察和 ECharts 配置 |
 | `iteration-05` | 实现 CodeWizard，完成受限代码执行和图表记录 |
-| `iteration-06` | 对齐章节写作、引用和结构化审核反馈 |
+| `iteration-06` | 完善章节写作、引用和结构化审核反馈 |
 | `iteration-07` | 增加 FastAPI SSE 单一研究接口 |
 | `iteration-08` | 增加检查点、恢复和取消 |
 | `iteration-09` | 接入真实 LLM、Bocha 搜索和可选本地知识库 |
```

<a id="archive-snapshots"></a>
## 七、i1 与 i2 全部跟踪文件完整快照

这些内容来自固定标签，而不是当前 iteration-03 工作树：

- i1：`787cd9a4ecfd496e17efbf522f765d013607e0db`，33 个跟踪文本文件；
- i2：`79db291dc0a1a7825b846d05516bce556f8976dc`，37 个跟踪文本文件；
- 共 70 份快照。README、.gitignore、契约文档、初始化文件、源码和测试都包含在内。

每个代码块内的内容是 Git 版本中的完整文件正文。快照中的空文件会明确标出“（空文件）”。
### 787cd9a 文件：.gitignore

```text
__pycache__/
*.py[cod]
.venv/
.env
node_modules/
dist/
*.log
```

### 787cd9a 文件：README.md

````text
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
- 后续迭代：加入结构化数据分析、图表、检查点、本地知识库和简化前端。

## 学习方式

每建立一个文件，先理解它的职责，再连接到下一个文件。不要一开始复制原项目的全部代码。

## 当前已跑通的后端链路

```text
用户问题
  -> Planner 生成研究计划
  -> Researcher 搜索来源
  -> FactExtractor 整理带来源的事实
  -> Writer 撰写报告
  -> Critic 审核并决定通过、补充搜索或修订
  -> 返回最终报告、评分和引用
```

工作流提供两种调用方式：

- `await workflow.run(...)`：等待整条链路结束，返回 `ResearchState`。
- `async for event in workflow.stream(...)`：按阶段取得进度事件，最后收到完整结果。

事件由 `backend/app/domain/events.py` 中的 `ResearchEvent` 统一转成普通字典，
不依赖 Web 框架。当前可以在 Python 内部验证事件顺序；FastAPI 和 SSE 会在之后的步骤加入。

事件类型包括 `research_started`、`phase_started`、`plan_ready`、
`research_evidence_ready`、`draft_ready`、`review_completed` 和 `research_completed`。
最终的 `research_completed` 事件包含报告、审核结果、质量评分和引用。

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
````

### 787cd9a 文件：backend/app/__init__.py

```text
"""Information DeepResearch backend package."""
```

### 787cd9a 文件：backend/app/agents/__init__.py

```text
"""Research agents used by the workflow."""
```

### 787cd9a 文件：backend/app/agents/base.py

```text
"""所有研究 Agent 共享的最小接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.state import ResearchState


class BaseAgent(ABC):
    """Agent 的基础约定。

    每个具体 Agent 只需要实现 ``run``：读取当前状态，完成自己的工作，
    再返回更新后的状态。这样工作流不需要知道每个 Agent 的内部细节。
    """

    name: str = "base"

    @abstractmethod
    async def run(self, state: ResearchState) -> ResearchState:
        """处理一次研究状态。"""
        raise NotImplementedError
```

### 787cd9a 文件：backend/app/agents/critic.py

```text
"""研究报告质量审核 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class CriticAgent(BaseAgent):
    """检查报告是否有事实、来源和基本的可发布条件。"""

    name = "critic"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.final_report.strip():
            raise ValueError("没有可供审核的报告")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "report": state.final_report,
                "facts": state.facts,
                "sources": state.sources,
                "iteration": state.iteration,
                "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
            },
        )
        review = self._validate_review(result)
        state.review = review
        state.quality_score = review["quality_score"]
        state.phase = "reviewing"
        return state

    @staticmethod
    def _validate_review(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Critic 返回结果必须是对象")

        verdict = str(value.get("verdict", "")).strip()
        if verdict not in {"pass", "needs_revision"}:
            raise ValueError("Critic verdict 必须是 pass 或 needs_revision")

        try:
            quality_score = float(value.get("quality_score"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Critic quality_score 必须是数字") from exc
        if not 0 <= quality_score <= 10:
            raise ValueError("Critic quality_score 必须在 0 到 10 之间")

        issues = value.get("issues", [])
        if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
            raise ValueError("Critic issues 必须是字符串列表")

        needs_more_research = value.get("needs_more_research", False)
        if not isinstance(needs_more_research, bool):
            raise ValueError("Critic needs_more_research 必须是布尔值")

        search_queries = value.get("search_queries", [])
        if not isinstance(search_queries, list) or not all(
            isinstance(query, str) and query.strip() for query in search_queries
        ):
            raise ValueError("Critic search_queries 必须是非空字符串列表")

        return {
            "verdict": verdict,
            "quality_score": quality_score,
            "summary": str(value.get("summary", "")).strip(),
            "needs_more_research": needs_more_research,
            "issues": issues,
            "search_queries": [query.strip() for query in search_queries],
        }
```

### 787cd9a 文件：backend/app/agents/fact_extractor.py

```text
"""从候选来源中提取带来源的结构化事实。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class FactExtractorAgent(BaseAgent):
    """把网页来源转换成报告可以引用的事实。"""

    name = "fact_extractor"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.sources:
            raise ValueError("没有可供事实提取的来源")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "sources": state.sources,
                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
            },
        )
        facts = self._validate_facts(result.get("facts"), state.sources)
        state.facts = self._deduplicate_facts(state.facts + facts)
        state.phase = "researching"
        return state

    @staticmethod
    def _validate_facts(value: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError("FactExtractor 返回的 facts 必须是列表")

        allowed_urls = {
            str(source.get("url", "")).strip()
            for source in sources
            if source.get("url")
        }
        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"FactExtractor 的第 {index} 个事实不是对象")

            content = str(item.get("content", "")).strip()
            source_url = str(item.get("source_url", "")).strip()
            if not content or not source_url:
                raise ValueError(f"FactExtractor 的第 {index} 个事实缺少 content 或 source_url")
            if source_url not in allowed_urls:
                raise ValueError(f"FactExtractor 的第 {index} 个事实引用了未知来源")

            try:
                confidence = float(item.get("confidence", 0.0))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 无效") from exc
            if not 0 <= confidence <= 1:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间")

            validated.append(
                {
                    "content": content,
                    "source_title": str(item.get("source_title", "")).strip(),
                    "source_url": source_url,
                    "source_type": str(item.get("source_type", "web")).strip() or "web",
                    "confidence": confidence,
                }
            )
        return validated

    @staticmethod
    def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[str, str], dict[str, Any]] = {}
        for fact in facts:
            key = (
                str(fact.get("source_url", "")).strip(),
                str(fact.get("content", "")).strip(),
            )
            if key != ("", ""):
                unique.setdefault(key, fact)
        return list(unique.values())
```

### 787cd9a 文件：backend/app/agents/planner.py

```text
"""研究规划 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """把一个用户问题拆成可执行的研究计划。"""

    name = "planner"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        """调用 LLM，校验结果，然后写回共享状态。"""
        query = state.query.strip()
        if not query:
            raise ValueError("研究问题不能为空")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": query,
                "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
            },
        )
        plan = self._validate_plan(result.get("plan"))
        research_questions = self._validate_questions(result.get("research_questions"))

        state.plan = plan
        state.research_questions = research_questions
        state.phase = "planning"
        return state

    @staticmethod
    def _validate_plan(value: Any) -> list[dict[str, str]]:
        """确保计划是由标题和描述组成的字典列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 plan 必须是非空列表")

        validated: list[dict[str, str]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个计划不是对象")
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise ValueError(f"Planner 的第 {index} 个计划缺少 title 或 description")
            validated.append({"title": title, "description": description})
        return validated

    @staticmethod
    def _validate_questions(value: Any) -> list[str]:
        """确保子问题是非空字符串列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 research_questions 必须是非空列表")

        questions = [str(item).strip() for item in value]
        if any(not question for question in questions):
            raise ValueError("Planner 返回了空的研究子问题")
        return questions
```

### 787cd9a 文件：backend/app/agents/researcher.py

```text
"""研究信息收集 Agent。"""

from __future__ import annotations

from app.core.search_client import SearchClient
from app.domain.state import ResearchState

from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    """根据研究子问题收集候选来源。

    这一版只负责搜索和去重。事实提取会在后续步骤使用 LLM 单独完成，
    这样每个 Agent 的输入和输出都更容易观察。
    """

    name = "researcher"

    def __init__(self, search: SearchClient, results_per_question: int = 3):
        if results_per_question < 1:
            raise ValueError("results_per_question 必须大于 0")
        self.search = search
        self.results_per_question = results_per_question

    async def run(self, state: ResearchState) -> ResearchState:
        """搜索所有子问题，并把来源写入共享状态。"""
        if state.pending_search_queries:
            questions = [query.strip() for query in state.pending_search_queries]
        else:
            questions = [question.strip() for question in state.research_questions]
        questions = [question for question in questions if question]
        if not questions:
            raise ValueError("没有可执行的研究子问题")

        collected_sources = list(state.sources)
        for question in questions:
            results = await self.search.search(
                query=question,
                limit=self.results_per_question,
            )
            collected_sources.extend(result.to_dict() for result in results)

        state.sources = self._deduplicate_sources(collected_sources)
        state.references = [
            {
                "title": source["title"],
                "url": source["url"],
            }
            for source in state.sources
            if source.get("url")
        ]
        state.pending_search_queries = []
        state.phase = "researching"
        return state

    @staticmethod
    def _deduplicate_sources(sources: list[dict]) -> list[dict]:
        """按 URL 去重，同时保留第一次出现的顺序。"""
        unique: dict[str, dict] = {}
        for source in sources:
            url = str(source.get("url", "")).strip()
            if url and url not in unique:
                unique[url] = source
        return list(unique.values())
```

### 787cd9a 文件：backend/app/agents/writer.py

```text
"""研究报告写作 Agent。"""

from __future__ import annotations

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """根据研究计划和带来源事实生成 Markdown 报告。"""

    name = "writer"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.plan:
            raise ValueError("没有可用于写作的研究计划")
        if not state.facts:
            raise ValueError("没有可用于写作的事实")

        report = await self.llm.complete_text(
            role=self.name,
            payload={
                "query": state.query,
                "plan": state.plan,
                "facts": state.facts,
                "references": state.references,
                "review": state.review,
                "iteration": state.iteration,
                "instruction": "生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
            },
        )
        report = report.strip()
        if not report:
            raise ValueError("Writer 没有生成报告内容")

        state.final_report = report
        state.phase = "writing"
        return state
```

### 787cd9a 文件：backend/app/core/__init__.py

```text
"""外部服务和基础设施适配器。"""
```

### 787cd9a 文件：backend/app/core/llm_client.py

```text
"""统一的大模型客户端接口。

Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """所有 LLM 客户端都必须提供的能力。"""

    @abstractmethod
    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """让模型返回结构化 JSON 数据。"""
        raise NotImplementedError

    @abstractmethod
    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        """让模型返回普通文本。"""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """不联网的确定性客户端。

    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
    同样的输入会得到同样的输出，测试因此稳定且容易理解。
    """

    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if role == "planner":
            query = str(payload.get("query", "")).strip()
            if not query:
                raise ValueError("planner 请求缺少 query")

            return {
                "plan": [
                    {
                        "title": "现状与定义",
                        "description": f"明确“{query}”的研究范围和当前现状。",
                    },
                    {
                        "title": "问题与证据",
                        "description": "整理公开来源中的事实、数据和主要争议。",
                    },
                    {
                        "title": "趋势与建议",
                        "description": "根据已有证据判断未来趋势并提出建议。",
                    },
                ],
                "research_questions": [
                    f"{query} 的当前现状和关键定义是什么？",
                    f"{query} 面临哪些主要问题，有哪些公开证据？",
                    f"{query} 的未来趋势和改进建议是什么？",
                ],
            }

        if role == "fact_extractor":
            facts = []
            for source in payload.get("sources", []):
                content = str(source.get("content") or source.get("snippet") or "").strip()
                url = str(source.get("url", "")).strip()
                if not content or not url:
                    continue
                facts.append(
                    {
                        "content": content,
                        "source_title": str(source.get("title", "")).strip(),
                        "source_url": url,
                        "source_type": "web",
                        "confidence": 0.7,
                    }
                )
            return {"facts": facts}

        if role == "critic":
            report = str(payload.get("report", "")).strip()
            facts = payload.get("facts", [])
            sources = payload.get("sources", [])
            if not report:
                raise ValueError("critic 请求缺少 report")

            passed = bool(facts and sources and "http" in report)
            return {
                "verdict": "pass" if passed else "needs_revision",
                "quality_score": 8.0 if passed else 4.0,
                "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                "needs_more_research": not passed,
                "issues": [] if passed else ["需要补充带来源的事实"],
                "search_queries": [] if passed else ["补充权威来源和数据"],
            }

        raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        if role != "writer":
            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")

        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("writer 请求缺少 query")

        facts = payload.get("facts", [])
        lines = [
            "## 执行摘要",
            "",
            f"本报告围绕“{query}”整理公开资料，并只使用已收集的来源作为证据。",
            "",
            "## 研究发现",
            "",
        ]
        if facts:
            for index, fact in enumerate(facts, start=1):
                content = str(fact.get("content", "")).strip()
                title = str(fact.get("source_title", "来源")).strip() or "来源"
                url = str(fact.get("source_url", "")).strip()
                lines.append(f"{index}. {content} ([{title}]({url}))")
        else:
            lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")

        review = payload.get("review", {})
        issues = review.get("issues", []) if isinstance(review, dict) else []
        if issues:
            lines.extend(["", "## 根据审核意见修订", ""])
            lines.extend(f"- 已处理：{issue}" for issue in issues)

        lines.extend(
            [
                "",
                "## 结论",
                "",
                "以上结论需要结合更多官方统计和行业报告继续验证。",
            ]
        )
        return "\n".join(lines)
```

### 787cd9a 文件：backend/app/core/search_client.py

```text
"""统一的搜索客户端接口。

搜索客户端只负责获取候选来源。
它不负责判断来源是否可信，也不负责把来源写成研究报告。
这些职责会交给后面的 Researcher 和 Writer。
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SearchResult:
    """一条搜索结果的统一格式。"""

    title: str
    url: str
    snippet: str
    query: str
    content: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换成适合放进 ResearchState 的字典。"""
        return asdict(self)


class SearchClient(ABC):
    """所有搜索服务都要遵守的接口。"""

    @abstractmethod
    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """根据一个研究子问题返回候选来源。"""
        raise NotImplementedError


class MockSearchClient(SearchClient):
    """本地模拟搜索服务。

    URL 使用查询内容的摘要生成，因此同一个查询每次都会得到同一个来源。
    这样测试不会依赖网络，也方便观察数据流。
    """

    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("搜索问题不能为空")
        if limit < 1:
            raise ValueError("limit 必须大于 0")

        digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
        result = SearchResult(
            title=f"公开资料：{query}",
            url=f"https://example.com/research/{digest}",
            snippet=f"这是针对“{query}”的模拟公开资料摘要，用于验证研究流程。",
            query=query,
            content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。",
        )
        return [result]
```

### 787cd9a 文件：backend/app/domain/__init__.py

```text
"""Domain models used by the research workflow."""
```

### 787cd9a 文件：backend/app/domain/events.py

```text
"""研究工作流对外发布的事件格式。

这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
字典格式。以后无论接哪种传输方式，都可以把同一类事件发送给调用方。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResearchEvent:
    """一次研究流程进度更新。

    ``data`` 中的字段会在 ``to_dict`` 时展开到事件顶层，调用方因此可以
    直接读取 ``event["report"]``、``event["references"]`` 等结果字段。
    """

    type: str
    session_id: str
    phase: str
    iteration: int = 0
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换成可被 API、SSE 或测试直接使用的普通字典。"""
        event = {
            "type": self.type,
            "session_id": self.session_id,
            "phase": self.phase,
            "iteration": self.iteration,
        }
        event.update(deepcopy(self.data))
        return event

```

### 787cd9a 文件：backend/app/domain/state.py

```text
"""DeepResearch 的共享工作状态。

第一轮先用一个普通 dataclass 表达状态。
后面的 Planner、Researcher、Writer 和 Critic 都读写同一个对象，
这样可以清楚看到信息如何在研究流程中流动。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class ResearchState:
    """一次研究任务从开始到结束所需要的全部核心数据。"""

    # 用户输入和任务身份
    query: str
    session_id: str = field(default_factory=lambda: str(uuid4()))

    # 当前阶段：init / planning / researching / writing / reviewing / completed
    phase: str = "init"

    # 审核循环次数
    iteration: int = 0
    max_iterations: int = 1

    # 规划结果
    plan: list[dict[str, Any]] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    pending_search_queries: list[str] = field(default_factory=list)

    # 研究证据
    sources: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)

    # 写作和审核结果
    final_report: str = ""
    review: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0

    # 错误记录
    errors: list[str] = field(default_factory=list)
```

### 787cd9a 文件：backend/app/scripts/__init__.py

```text
"""Executable learning scripts."""
```

### 787cd9a 文件：backend/app/scripts/run_research.py

```text
"""从命令行运行一次 Mock DeepResearch。"""

from __future__ import annotations

import argparse
import asyncio

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.workflow.research_workflow import ResearchWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行一次 Iteration 01 DeepResearch")
    parser.add_argument(
        "query",
        nargs="?",
        help="研究问题；不传时会进入交互式输入",
    )
    return parser


def print_state(state: ResearchState) -> None:
    print("\n" + "=" * 60)
    print("研究计划")
    print("=" * 60)
    for index, item in enumerate(state.plan, start=1):
        print(f"{index}. {item['title']}：{item['description']}")

    print("\n" + "=" * 60)
    print(f"搜索来源（{len(state.sources)} 条）")
    print("=" * 60)
    for index, source in enumerate(state.sources, start=1):
        print(f"{index}. {source['title']}")
        print(f"   URL: {source['url']}")

    print("\n" + "=" * 60)
    print(f"结构化事实（{len(state.facts)} 条）")
    print("=" * 60)
    for index, fact in enumerate(state.facts, start=1):
        print(f"{index}. {fact['content']}")
        print(f"   来源: {fact['source_url']}")

    print("\n" + "=" * 60)
    print("最终报告")
    print("=" * 60)
    print(state.final_report)

    print("\n" + "=" * 60)
    print("审核结果")
    print("=" * 60)
    print(f"结论: {state.review['verdict']}")
    print(f"评分: {state.quality_score}/10")
    print(f"摘要: {state.review['summary']}")
    print(f"任务阶段: {state.phase}")
    print(f"会话 ID: {state.session_id}")


async def run(query: str) -> ResearchState:
    workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
    return await workflow.run(query)


def main() -> None:
    args = build_parser().parse_args()
    query = (args.query or input("请输入研究问题：")).strip()
    if not query:
        raise SystemExit("研究问题不能为空")
    state = asyncio.run(run(query))
    print_state(state)


if __name__ == "__main__":
    main()
```

### 787cd9a 文件：backend/app/workflow/__init__.py

```text
"""Research workflow orchestration."""
```

### 787cd9a 文件：backend/app/workflow/research_workflow.py

```text
"""把多个 Agent 编排成一次完整研究任务。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.events import ResearchEvent
from app.domain.state import ResearchState


class ResearchWorkflow:
    """Iteration 01 的最小研究编排器。

    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
    ``run`` 适合一次性拿到结果，``stream`` 适合逐步消费进度事件。
    SSE 和数据库等外层能力后续再加入；审核修订循环在本轮实现。
    """

    def __init__(
        self,
        llm: LLMClient,
        search: SearchClient,
        results_per_question: int = 3,
        max_iterations: int = 1,
    ):
        if max_iterations < 0:
            raise ValueError("max_iterations 不能小于 0")
        self.max_iterations = max_iterations
        self.planner = PlannerAgent(llm)
        self.researcher = ResearcherAgent(search, results_per_question)
        self.fact_extractor = FactExtractorAgent(llm)
        self.writer = WriterAgent(llm)
        self.critic = CriticAgent(llm)

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        """执行一次完整研究并返回最终状态。"""
        state = self._new_state(query, session_id)
        async for _ in self._stream_state(state):
            # run 保留一次性调用方式，只忽略中间事件。
            pass
        return state

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """逐步产出研究进度事件，最后一个事件包含完整结果。

        这个方法仍然使用和 ``run`` 相同的 Agent 和状态对象，因此不会
        产生两套业务逻辑。当前返回普通字典，后续接 FastAPI SSE 时可以
        直接序列化；暂时不需要启动真实服务就能测试事件顺序。
        """
        state = self._new_state(query, session_id)
        async for event in self._stream_state(state):
            yield event

    def _new_state(
        self,
        query: str,
        session_id: str | None,
    ) -> ResearchState:
        """创建一次研究任务的初始状态。"""
        return ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

    async def _stream_state(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        """执行工作流并发布事件；``run`` 和 ``stream`` 共用此实现。"""
        yield self._event(
            state,
            "research_started",
            query=state.query,
            max_iterations=state.max_iterations,
        )

        yield self._event(
            state,
            "phase_started",
            phase="planning",
            agent=self.planner.name,
        )
        await self.planner.run(state)
        yield self._event(
            state,
            "plan_ready",
            plan=state.plan,
            research_questions=state.research_questions,
        )

        async for event in self._run_research_phase(state, supplementary=False):
            yield event
        yield self._event(
            state,
            "phase_started",
            phase="writing",
            agent=self.writer.name,
        )
        await self.writer.run(state)
        yield self._event(
            state,
            "draft_ready",
            report=state.final_report,
            revision=False,
        )

        while True:
            yield self._event(
                state,
                "phase_started",
                phase="reviewing",
                agent=self.critic.name,
            )
            await self.critic.run(state)
            yield self._event(
                state,
                "review_completed",
                review=state.review,
                quality_score=state.quality_score,
            )

            if state.review["verdict"] == "pass":
                break
            if state.iteration >= state.max_iterations:
                break

            state.iteration += 1
            if state.review["needs_more_research"]:
                state.pending_search_queries = (
                    state.review["search_queries"]
                    or state.review["issues"]
                    or state.research_questions
                )
                async for event in self._run_research_phase(
                    state,
                    supplementary=True,
                ):
                    yield event

            # 如果无需新搜索，Writer 根据 state.review 做内容修订；
            # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
            yield self._event(
                state,
                "phase_started",
                phase="writing",
                agent=self.writer.name,
                revision=True,
            )
            await self.writer.run(state)
            yield self._event(
                state,
                "draft_ready",
                report=state.final_report,
                revision=True,
            )

        state.phase = "completed"
        yield self._event(
            state,
            "research_completed",
            report=state.final_report,
            quality_score=state.quality_score,
            references=state.references,
            review=state.review,
        )

    async def _run_research_phase(
        self,
        state: ResearchState,
        *,
        supplementary: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """运行搜索和事实提取，并逐步发布研究阶段事件。"""
        yield self._event(
            state,
            "phase_started",
            phase="researching",
            agent=self.researcher.name,
            supplementary=supplementary,
        )
        await self.researcher.run(state)
        await self.fact_extractor.run(state)
        yield self._event(
            state,
            "research_evidence_ready",
            supplementary=supplementary,
            source_count=len(state.sources),
            fact_count=len(state.facts),
            sources=state.sources,
            facts=state.facts,
            references=state.references,
        )

    @staticmethod
    def _event(
        state: ResearchState,
        event_type: str,
        *,
        phase: str | None = None,
        **data: Any,
    ) -> dict[str, Any]:
        """根据当前状态创建一个普通事件字典。"""
        return ResearchEvent(
            type=event_type,
            session_id=state.session_id,
            phase=phase or state.phase,
            iteration=state.iteration,
            data=data,
        ).to_dict()
```

### 787cd9a 文件：backend/tests/__init__.py

```text
"""Tests for the learning backend."""
```

### 787cd9a 文件：backend/tests/test_base_agent.py

```text
import asyncio
import unittest

from app.agents.base import BaseAgent
from app.domain.state import ResearchState


class DemoAgent(BaseAgent):
    name = "demo"

    async def run(self, state: ResearchState) -> ResearchState:
        state.phase = "demo_completed"
        return state


class BaseAgentTests(unittest.TestCase):
    def test_concrete_agent_updates_and_returns_state(self):
        state = ResearchState("测试问题")
        agent = DemoAgent()

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "demo_completed")
        self.assertEqual(agent.name, "demo")

    def test_base_agent_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            BaseAgent()


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_critic.py

```text
import asyncio
import unittest

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenCriticClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"verdict": "unknown", "quality_score": 20, "issues": "错误格式"}

    async def complete_text(self, role, payload):
        return ""


class CriticAgentTests(unittest.TestCase):
    def test_critic_approves_source_grounded_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            await CriticAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "reviewing")
        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)
        self.assertEqual(state.review["issues"], [])

    def test_critic_rejects_invalid_result(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容"

        with self.assertRaisesRegex(ValueError, "verdict"):
            asyncio.run(CriticAgent(BrokenCriticClient()).run(state))

    def test_critic_requires_report(self):
        with self.assertRaisesRegex(ValueError, "审核的报告"):
            asyncio.run(CriticAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_fact_extractor.py

```text
import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "facts": [
                {
                    "content": "这条事实引用了不存在的来源。",
                    "source_url": "https://unknown.example.com",
                    "confidence": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class FactExtractorAgentTests(unittest.TestCase):
    def test_fact_extractor_turns_sources_into_facts(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(all(fact["source_url"] for fact in state.facts))
        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))

    def test_fact_extractor_rejects_unknown_source_url(self):
        state = ResearchState("测试问题")
        state.sources = [
            {
                "title": "已知来源",
                "url": "https://known.example.com",
                "snippet": "摘要",
            }
        ]

        with self.assertRaisesRegex(ValueError, "未知来源"):
            asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))

    def test_fact_extractor_requires_sources(self):
        with self.assertRaisesRegex(ValueError, "来源"):
            asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_llm_client.py

```text
import asyncio
import unittest

from app.core.llm_client import LLMClient, MockLLMClient


class LLMClientTests(unittest.TestCase):
    def test_mock_client_implements_llm_interface(self):
        self.assertIsInstance(MockLLMClient(), LLMClient)

    def test_mock_planner_returns_structured_result(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "planner",
                {"query": "新能源汽车行业的发展趋势是什么？"},
            )
        )

        self.assertEqual(len(result["plan"]), 3)
        self.assertEqual(len(result["research_questions"]), 3)
        self.assertIn("新能源汽车", result["research_questions"][0])

    def test_mock_fact_extractor_returns_source_grounded_facts(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "fact_extractor",
                {
                    "query": "测试行业",
                    "sources": [
                        {
                            "title": "测试来源",
                            "url": "https://example.com/source",
                            "content": "测试来源中的明确事实。",
                        }
                    ],
                },
            )
        )

        self.assertEqual(len(result["facts"]), 1)
        self.assertEqual(result["facts"][0]["source_url"], "https://example.com/source")

    def test_mock_critic_approves_cited_report(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "critic",
                {
                    "query": "测试行业",
                    "report": "报告内容 https://example.com/source",
                    "facts": [{"content": "事实"}],
                    "sources": [{"url": "https://example.com/source"}],
                },
            )
        )

        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["quality_score"], 8.0)

    def test_mock_client_rejects_unknown_role(self):
        client = MockLLMClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.complete_json("unknown", {"query": "测试"}))

    def test_mock_writer_returns_text(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_text(
                "writer",
                {
                    "query": "测试行业",
                    "facts": [
                        {
                            "content": "测试事实。",
                            "source_title": "测试来源",
                            "source_url": "https://example.com/source",
                        }
                    ],
                },
            )
        )

        self.assertIn("测试行业", result)
        self.assertIn("测试事实", result)
        self.assertIn("https://example.com/source", result)


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_planner.py

```text
import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.domain.state import ResearchState


class BrokenPlannerClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"plan": [], "research_questions": []}

    async def complete_text(self, role, payload):
        return ""


class PlannerAgentTests(unittest.TestCase):
    def test_planner_writes_plan_into_state(self):
        state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
        agent = PlannerAgent(MockLLMClient())

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "planning")
        self.assertEqual(len(result.plan), 3)
        self.assertEqual(len(result.research_questions), 3)
        self.assertIn("新能源汽车", result.plan[0]["description"])

    def test_planner_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            asyncio.run(PlannerAgent(MockLLMClient()).run(ResearchState("   ")))

    def test_planner_rejects_invalid_llm_result(self):
        with self.assertRaisesRegex(ValueError, "非空列表"):
            asyncio.run(PlannerAgent(BrokenPlannerClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_researcher.py

```text
import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class ResearcherAgentTests(unittest.TestCase):
    def test_researcher_collects_sources_after_planning(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.research_questions), 3)
        self.assertEqual(len(state.sources), 3)
        self.assertEqual(len(state.references), 3)
        self.assertTrue(all(source["url"].startswith("https://") for source in state.sources))

    def test_researcher_deduplicates_existing_source_urls(self):
        async def run():
            state = ResearchState("测试问题")
            state.research_questions = ["相同问题", "相同问题"]
            return await ResearcherAgent(MockSearchClient()).run(state)

        state = asyncio.run(run())

        self.assertEqual(len(state.sources), 1)
        self.assertEqual(len(state.references), 1)

    def test_researcher_rejects_missing_questions(self):
        state = ResearchState("还没有规划的问题")

        with self.assertRaisesRegex(ValueError, "研究子问题"):
            asyncio.run(ResearcherAgent(MockSearchClient()).run(state))


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_run_research.py

```text
import asyncio
import unittest
from contextlib import redirect_stdout
from io import StringIO

from app.scripts.run_research import print_state, run


class RunResearchScriptTests(unittest.TestCase):
    def test_script_run_returns_completed_state(self):
        state = asyncio.run(run("测试行业的现状是什么？"))

        self.assertEqual(state.phase, "completed")
        self.assertTrue(state.final_report)

    def test_print_state_contains_key_sections(self):
        state = asyncio.run(run("测试行业的现状是什么？"))
        output = StringIO()

        with redirect_stdout(output):
            print_state(state)

        text = output.getvalue()
        self.assertIn("研究计划", text)
        self.assertIn("搜索来源", text)
        self.assertIn("结构化事实", text)
        self.assertIn("最终报告", text)
        self.assertIn("审核结果", text)


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_search_client.py

```text
import asyncio
import unittest

from app.core.search_client import MockSearchClient, SearchClient, SearchResult


class SearchClientTests(unittest.TestCase):
    def test_mock_client_implements_search_interface(self):
        self.assertIsInstance(MockSearchClient(), SearchClient)

    def test_search_returns_normalized_result(self):
        client = MockSearchClient()

        results = asyncio.run(client.search("新能源汽车行业的市场规模是什么？"))

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SearchResult)
        self.assertTrue(results[0].title)
        self.assertTrue(results[0].url.startswith("https://"))
        self.assertTrue(results[0].snippet)
        self.assertEqual(results[0].query, "新能源汽车行业的市场规模是什么？")

    def test_same_query_has_stable_url(self):
        client = MockSearchClient()

        first = asyncio.run(client.search("稳定查询"))[0]
        second = asyncio.run(client.search("稳定查询"))[0]

        self.assertEqual(first.url, second.url)

    def test_search_rejects_invalid_input(self):
        client = MockSearchClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.search("   "))
        with self.assertRaises(ValueError):
            asyncio.run(client.search("测试", limit=0))


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_state.py

```text
import unittest

from app.domain.state import ResearchState


class ResearchStateTests(unittest.TestCase):
    def test_state_starts_empty(self):
        state = ResearchState("测试问题")

        self.assertEqual(state.query, "测试问题")
        self.assertEqual(state.phase, "init")
        self.assertEqual(state.plan, [])
        self.assertEqual(state.sources, [])
        self.assertEqual(state.facts, [])

    def test_mutable_fields_are_not_shared(self):
        first = ResearchState("第一个问题")
        second = ResearchState("第二个问题")

        first.plan.append({"title": "只属于第一个任务"})

        self.assertEqual(len(first.plan), 1)
        self.assertEqual(second.plan, [])


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_stream_workflow.py

```text
import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)


async def collect_events(workflow, query, session_id=None):
    return [
        event
        async for event in workflow.stream(query, session_id=session_id)
    ]


class StreamWorkflowTests(unittest.TestCase):
    def test_stream_emits_ordered_events_and_final_result(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        events = asyncio.run(
            collect_events(
                workflow,
                "中国新能源汽车行业的发展趋势是什么？",
                session_id="stream-001",
            )
        )

        self.assertEqual(
            [event["type"] for event in events],
            [
                "research_started",
                "phase_started",
                "plan_ready",
                "phase_started",
                "research_evidence_ready",
                "phase_started",
                "draft_ready",
                "phase_started",
                "review_completed",
                "research_completed",
            ],
        )
        self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
        self.assertEqual(events[1]["phase"], "planning")
        self.assertEqual(events[3]["phase"], "researching")
        self.assertEqual(events[4]["source_count"], 3)
        self.assertEqual(events[4]["fact_count"], 3)
        self.assertEqual(events[-1]["phase"], "completed")
        self.assertIn("## 执行摘要", events[-1]["report"])
        self.assertEqual(events[-1]["quality_score"], 8.0)
        self.assertEqual(len(events[-1]["references"]), 3)

    def test_stream_marks_supplementary_research_iteration(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=["补充最新行业数据"],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)

        events = asyncio.run(collect_events(workflow, "新能源汽车行业趋势"))

        evidence_events = [
            event for event in events if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertFalse(evidence_events[0]["supplementary"])
        self.assertTrue(evidence_events[1]["supplementary"])
        self.assertEqual(evidence_events[1]["iteration"], 1)
        self.assertEqual(events[-1]["type"], "research_completed")
        self.assertEqual(events[-1]["review"]["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_workflow.py

```text
import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)
        self.writer_payloads = []

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)

    async def complete_text(self, role, payload):
        self.writer_payloads.append(payload)
        return await super().complete_text(role, payload)


class RecordingSearchClient(MockSearchClient):
    def __init__(self):
        self.queries = []

    async def search(self, query, limit=3):
        self.queries.append(query)
        return await super().search(query, limit)


class ResearchWorkflowTests(unittest.TestCase):
    def test_workflow_runs_full_research_chain(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("中国新能源汽车行业的发展趋势是什么？")
        )

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.plan[0]["title"], "现状与定义")
        self.assertEqual(len(state.sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(state.final_report)
        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)

    def test_workflow_preserves_explicit_session_id(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("测试问题", session_id="session-001")
        )

        self.assertEqual(state.session_id, "session-001")

    def test_critic_routes_to_supplementary_research_then_passes(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=["补充最新行业数据"],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = ResearchWorkflow(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 4)  # 3 个初始问题 + 1 个补充查询
        self.assertEqual(search.queries[-1], "2025年新能源汽车行业数据")
        self.assertEqual(len(state.sources), 4)
        self.assertEqual(len(state.facts), 4)
        self.assertIn("2025年新能源汽车行业数据", state.final_report)

    def test_critic_routes_to_writer_revision_without_new_search(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    issues=["补充结论与证据之间的说明"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = ResearchWorkflow(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.review["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 3)
        self.assertEqual(len(llm.writer_payloads), 2)
        self.assertIn(
            "补充结论与证据之间的说明",
            llm.writer_payloads[1]["review"]["issues"],
        )
        self.assertIn("补充结论与证据之间的说明", state.final_report)

    def test_workflow_stops_after_max_iterations(self):
        llm = SequencedReviewLLM(
            [
                review("needs_revision", issues=["第一轮问题"]),
                review("needs_revision", issues=["仍需改进"], score=5.0),
            ]
        )
        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)

        state = asyncio.run(workflow.run("测试行业", session_id="bounded"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(state.review["verdict"], "needs_revision")
        self.assertEqual(state.review["issues"], ["仍需改进"])
        self.assertEqual(len(llm.writer_payloads), 2)

    def test_workflow_rejects_negative_iteration_limit(self):
        with self.assertRaisesRegex(ValueError, "max_iterations"):
            ResearchWorkflow(MockLLMClient(), MockSearchClient(), max_iterations=-1)


if __name__ == "__main__":
    unittest.main()
```

### 787cd9a 文件：backend/tests/test_writer.py

```text
import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class WriterAgentTests(unittest.TestCase):
    def test_writer_generates_cited_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "writing")
        self.assertTrue(state.final_report.startswith("## 执行摘要"))
        self.assertIn("研究发现", state.final_report)
        self.assertIn("https://example.com/research/", state.final_report)

    def test_writer_requires_plan(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "研究计划"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))

    def test_writer_requires_facts(self):
        state = ResearchState("测试问题")
        state.plan = [{"title": "章节", "description": "描述"}]

        with self.assertRaisesRegex(ValueError, "事实"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：.gitignore

```text
__pycache__/
*.py[cod]
.venv/
.env
node_modules/
dist/
*.log
```

### 79db291 文件：README.md

````text
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
````

### 79db291 文件：backend/app/__init__.py

```text
"""Information DeepResearch backend package."""
```

### 79db291 文件：backend/app/agents/__init__.py

```text
"""Research agents used by the workflow."""
```

### 79db291 文件：backend/app/agents/base.py

```text
"""所有研究 Agent 共享的最小接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.state import ResearchState


class BaseAgent(ABC):
    """Agent 的基础约定。

    每个具体 Agent 只需要实现 ``run``：读取当前状态，完成自己的工作，
    再返回更新后的状态。这样工作流不需要知道每个 Agent 的内部细节。
    """

    name: str = "base"

    @abstractmethod
    async def run(self, state: ResearchState) -> ResearchState:
        """处理一次研究状态。"""
        raise NotImplementedError
```

### 79db291 文件：backend/app/agents/critic.py

```text
"""研究报告质量审核 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class CriticAgent(BaseAgent):
    """检查报告是否有事实、来源和基本的可发布条件。"""

    name = "critic"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.final_report.strip():
            raise ValueError("没有可供审核的报告")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "report": state.final_report,
                "facts": state.facts,
                "sources": state.raw_sources,
                "iteration": state.iteration,
                "instruction": "检查事实是否有来源支撑，并判断报告是否需要补充研究。",
            },
        )
        review = self._validate_review(result)
        state.review_result = review
        state.critic_feedback = [
            {
                "description": issue,
                "resolved": False,
            }
            for issue in review["issues"]
        ]
        state.unresolved_issues = len(state.critic_feedback)
        state.quality_score = review["quality_score"]
        state.phase = "reviewing"
        return state

    @staticmethod
    def _validate_review(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Critic 返回结果必须是对象")

        verdict = str(value.get("verdict", "")).strip()
        if verdict not in {"pass", "needs_revision"}:
            raise ValueError("Critic verdict 必须是 pass 或 needs_revision")

        try:
            quality_score = float(value.get("quality_score"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Critic quality_score 必须是数字") from exc
        if not 0 <= quality_score <= 10:
            raise ValueError("Critic quality_score 必须在 0 到 10 之间")

        issues = value.get("issues", [])
        if not isinstance(issues, list) or not all(isinstance(issue, str) for issue in issues):
            raise ValueError("Critic issues 必须是字符串列表")

        needs_more_research = value.get("needs_more_research", False)
        if not isinstance(needs_more_research, bool):
            raise ValueError("Critic needs_more_research 必须是布尔值")

        search_queries = value.get("search_queries", [])
        if not isinstance(search_queries, list) or not all(
            isinstance(query, str) and query.strip() for query in search_queries
        ):
            raise ValueError("Critic search_queries 必须是非空字符串列表")

        return {
            "verdict": verdict,
            "quality_score": quality_score,
            "summary": str(value.get("summary", "")).strip(),
            "needs_more_research": needs_more_research,
            "issues": issues,
            "search_queries": [query.strip() for query in search_queries],
        }
```

### 79db291 文件：backend/app/agents/fact_extractor.py

```text
"""从候选来源中提取带来源的结构化事实。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class FactExtractorAgent(BaseAgent):
    """把网页来源转换成报告可以引用的事实。"""

    name = "fact_extractor"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.raw_sources:
            raise ValueError("没有可供事实提取的来源")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": state.query,
                "sources": state.raw_sources,
                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
            },
        )
        facts = self._validate_facts(result.get("facts"), state.raw_sources)
        state.facts = self._deduplicate_facts(state.facts + facts)
        state.phase = "researching"
        return state

    @staticmethod
    def _validate_facts(value: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError("FactExtractor 返回的 facts 必须是列表")

        allowed_urls = {
            str(source.get("url", "")).strip()
            for source in sources
            if source.get("url")
        }
        source_by_url = {
            str(source.get("url", "")).strip(): source
            for source in sources
            if source.get("url")
        }
        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"FactExtractor 的第 {index} 个事实不是对象")

            content = str(item.get("content", "")).strip()
            source_url = str(item.get("source_url", "")).strip()
            if not content or not source_url:
                raise ValueError(f"FactExtractor 的第 {index} 个事实缺少 content 或 source_url")
            if source_url not in allowed_urls:
                raise ValueError(f"FactExtractor 的第 {index} 个事实引用了未知来源")

            try:
                confidence = float(item.get("confidence", 0.0))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 无效") from exc
            if not 0 <= confidence <= 1:
                raise ValueError(f"FactExtractor 的第 {index} 个事实 confidence 必须在 0 到 1 之间")

            fact = {
                "content": content,
                "source_title": str(item.get("source_title", "")).strip(),
                "source_url": source_url,
                "source_type": str(item.get("source_type", "web")).strip() or "web",
                "confidence": confidence,
            }
            source_context = source_by_url[source_url]
            for field_name in ("section_id", "section_title"):
                if source_context.get(field_name):
                    fact[field_name] = source_context[field_name]
            validated.append(fact)
        return validated

    @staticmethod
    def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[str, str], dict[str, Any]] = {}
        for fact in facts:
            key = (
                str(fact.get("source_url", "")).strip(),
                str(fact.get("content", "")).strip(),
            )
            if key != ("", ""):
                unique.setdefault(key, fact)
        return list(unique.values())
```

### 79db291 文件：backend/app/agents/planner.py

```text
"""研究规划 Agent。"""

from __future__ import annotations

from typing import Any

from app.core.llm_client import LLMClient
from app.domain.models import Hypothesis, Section
from app.domain.state import ResearchState

from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """把一个用户问题转换成 V2 研究大纲和可验证假设。"""

    name = "planner"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        """调用 LLM，校验结果，然后写回共享状态。"""
        query = state.query.strip()
        if not query:
            raise ValueError("研究问题不能为空")

        result = await self.llm.complete_json(
            role=self.name,
            payload={
                "query": query,
                "instruction": "请拆分成 2 到 4 个互不重复、可以搜索验证的研究子问题。",
            },
        )
        outline = self._validate_outline(result.get("outline"))
        hypotheses = self._validate_hypotheses(result.get("hypotheses", []))
        research_questions = self._validate_questions(result.get("research_questions"))
        key_entities = self._validate_key_entities(result.get("key_entities", []))

        state.outline = outline
        state.hypotheses = hypotheses
        state.research_questions = research_questions
        state.key_entities = key_entities
        state.mind_map = result.get("mind_map", {})
        state.phase = "planning"
        return state

    @staticmethod
    def _validate_outline(value: Any) -> list[dict[str, Any]]:
        """用 Section 校验并序列化 LLM 返回的章节大纲。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 outline 必须是非空列表")

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个章节不是对象")
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not title or not description:
                raise ValueError(f"Planner 的第 {index} 个章节缺少 title 或 description")

            section_type = str(item.get("section_type", "mixed")).strip() or "mixed"
            if section_type not in {"qualitative", "quantitative", "mixed"}:
                raise ValueError(f"Planner 的第 {index} 个章节 section_type 无效")

            status = str(item.get("status", "pending")).strip() or "pending"
            if status not in {"pending", "researching", "drafted", "reviewed", "final"}:
                raise ValueError(f"Planner 的第 {index} 个章节 status 无效")

            search_queries = item.get("search_queries", [title])
            if not isinstance(search_queries, list):
                raise ValueError(f"Planner 的第 {index} 个章节 search_queries 必须是列表")
            search_queries = [str(query).strip() for query in search_queries if str(query).strip()]
            if not search_queries:
                search_queries = [title]

            section = Section(
                id=str(item.get("id", f"sec_{index}")).strip() or f"sec_{index}",
                title=title,
                description=description,
                section_type=section_type,
                status=status,
                requires_data=bool(item.get("requires_data", False)),
                requires_chart=bool(item.get("requires_chart", False)),
                priority=int(item.get("priority", index)),
                search_queries=search_queries,
            )
            validated.append(section.to_dict())
        return validated

    @staticmethod
    def _validate_hypotheses(value: Any) -> list[dict[str, Any]]:
        """用 Hypothesis 校验研究假设，并初始化证据列表。"""
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Planner 返回的 hypotheses 必须是列表")

        validated: list[dict[str, Any]] = []
        allowed_statuses = {
            "unverified",
            "supported",
            "refuted",
            "partially_supported",
        }
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Planner 的第 {index} 个假设不是对象")
            content = str(item.get("content", "")).strip()
            if not content:
                raise ValueError(f"Planner 的第 {index} 个假设缺少 content")
            status = str(item.get("status", "unverified")).strip() or "unverified"
            if status not in allowed_statuses:
                raise ValueError(f"Planner 的第 {index} 个假设 status 无效")

            hypothesis = Hypothesis(
                id=str(item.get("id", f"h_{index}")).strip() or f"h_{index}",
                content=content,
                status=status,
                evidence_for=[str(evidence).strip() for evidence in item.get("evidence_for", [])],
                evidence_against=[
                    str(evidence).strip() for evidence in item.get("evidence_against", [])
                ],
            )
            validated.append(hypothesis.to_dict())
        return validated

    @staticmethod
    def _validate_key_entities(value: Any) -> list[str]:
        """兼容字符串或带 name 的实体对象，并统一成名称列表。"""
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Planner 返回的 key_entities 必须是列表")

        entities: list[str] = []
        for item in value:
            if isinstance(item, dict):
                item = item.get("name", "")
            name = str(item).strip()
            if name:
                entities.append(name)
        return entities

    @staticmethod
    def _validate_questions(value: Any) -> list[str]:
        """确保子问题是非空字符串列表。"""
        if not isinstance(value, list) or not value:
            raise ValueError("Planner 返回的 research_questions 必须是非空列表")

        questions = [str(item).strip() for item in value]
        if any(not question for question in questions):
            raise ValueError("Planner 返回了空的研究子问题")
        return questions
```

### 79db291 文件：backend/app/agents/researcher.py

```text
"""研究信息收集 Agent。"""

from __future__ import annotations

from app.core.search_client import SearchClient
from app.domain.state import ResearchState

from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    """根据章节大纲中的搜索查询收集候选来源。

    这一版只负责搜索和去重。事实提取会在后续步骤使用 LLM 单独完成，
    这样每个 Agent 的输入和输出都更容易观察。
    """

    name = "researcher"

    def __init__(self, search: SearchClient, results_per_question: int = 3):
        if results_per_question < 1:
            raise ValueError("results_per_question 必须大于 0")
        self.search = search
        self.results_per_question = results_per_question

    async def run(self, state: ResearchState) -> ResearchState:
        """搜索章节查询，并把来源与章节关联后写入共享状态。"""
        if state.pending_search_queries:
            tasks = [
                {"query": query.strip(), "section_id": "", "section_title": ""}
                for query in state.pending_search_queries
            ]
        else:
            tasks = self._build_search_tasks(state)
        tasks = [task for task in tasks if task["query"]]
        if not tasks:
            raise ValueError("没有可执行的研究子问题")

        collected_sources = list(state.raw_sources)
        for task in tasks:
            results = await self.search.search(
                query=task["query"],
                limit=self.results_per_question,
            )
            for result in results:
                source = result.to_dict()
                if task["section_id"]:
                    source["section_id"] = task["section_id"]
                    source["section_title"] = task["section_title"]
                collected_sources.append(source)

        state.raw_sources = self._deduplicate_sources(collected_sources)
        state.references = [
            {
                "title": source["title"],
                "url": source["url"],
            }
            for source in state.raw_sources
            if source.get("url")
        ]
        state.pending_search_queries = []
        state.phase = "researching"
        return state

    @staticmethod
    def _build_search_tasks(state: ResearchState) -> list[dict[str, str]]:
        """把章节大纲转换成搜索任务；没有大纲时回退到研究问题。"""
        tasks: list[dict[str, str]] = []
        for section in state.outline:
            section_id = str(section.get("id", "")).strip()
            section_title = str(section.get("title", "")).strip()
            queries = section.get("search_queries") or [section_title]
            if not isinstance(queries, list):
                raise ValueError("章节 search_queries 必须是列表")
            for query in queries:
                query = str(query).strip()
                if query:
                    tasks.append(
                        {
                            "query": query,
                            "section_id": section_id,
                            "section_title": section_title,
                        }
                    )

        if tasks:
            return tasks

        return [
            {"query": str(question).strip(), "section_id": "", "section_title": ""}
            for question in state.research_questions
        ]

    @staticmethod
    def _deduplicate_sources(sources: list[dict]) -> list[dict]:
        """按 URL 去重，同时保留第一次出现的顺序。"""
        unique: dict[str, dict] = {}
        for source in sources:
            url = str(source.get("url", "")).strip()
            if url and url not in unique:
                unique[url] = source
        return list(unique.values())
```

### 79db291 文件：backend/app/agents/writer.py

```text
"""研究报告写作 Agent。"""

from __future__ import annotations

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState

from .base import BaseAgent


class WriterAgent(BaseAgent):
    """按章节整理事实，并生成带来源的 Markdown 报告。"""

    name = "writer"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.outline:
            raise ValueError("没有可用于写作的研究大纲")
        if not state.facts:
            raise ValueError("没有可用于写作的事实")

        draft_sections: dict[str, str] = {}
        normalized_outline: list[dict] = []
        outline_ids = {
            str(section.get("id", "")).strip()
            for section in state.outline
            if str(section.get("id", "")).strip()
        }
        unassigned_facts = [
            fact
            for fact in state.facts
            if str(fact.get("section_id", "")).strip() not in outline_ids
        ]
        for index, raw_section in enumerate(state.outline, start=1):
            section = dict(raw_section)
            section_id = str(section.get("id", f"sec_{index}")).strip() or f"sec_{index}"
            section["id"] = section_id
            section_title = str(section.get("title", "")).strip() or f"第 {index} 节"
            section["title"] = section_title

            related_facts = self._facts_for_section(state.facts, section_id)
            if index == 1 and unassigned_facts:
                related_facts = self._merge_facts(related_facts, unassigned_facts)
            section_content = await self.llm.complete_text(
                role=self.name,
                payload={
                    "mode": "section",
                    "query": state.query,
                    "section": section,
                    "facts": related_facts,
                    "data_points": state.data_points,
                    "insights": state.insights,
                    "charts": state.charts,
                    "review_result": state.review_result,
                    "iteration": state.iteration,
                    "instruction": "只生成本章节正文，不要重复章节标题；每个事实都保留可点击来源链接。",
                },
            )
            section_content = section_content.strip()
            if not section_content:
                raise ValueError(f"Writer 没有生成章节内容: {section_title}")

            section["status"] = "drafted"
            draft_sections[section_id] = section_content
            normalized_outline.append(section)

        report = await self.llm.complete_text(
            role=self.name,
            payload={
                "mode": "report",
                "query": state.query,
                "outline": normalized_outline,
                "facts": state.facts,
                "draft_sections": draft_sections,
                "data_points": state.data_points,
                "insights": state.insights,
                "charts": state.charts,
                "references": state.references,
                "review_result": state.review_result,
                "iteration": state.iteration,
                "instruction": "整合各章节草稿，生成带 Markdown 标题和可点击来源链接的研究报告；若有审核意见，逐条处理。",
            },
        )
        report = report.strip()
        if not report:
            raise ValueError("Writer 没有生成报告内容")

        state.outline = normalized_outline
        state.draft_sections = draft_sections
        state.final_report = report
        state.phase = "writing"
        return state

    @staticmethod
    def _facts_for_section(
        facts: list[dict],
        section_id: str,
    ) -> list[dict]:
        """优先选择当前章节的事实；没有关联时回退到全部事实。"""
        related = [
            fact
            for fact in facts
            if str(fact.get("section_id", "")).strip() == section_id
        ]
        return related or facts

    @staticmethod
    def _merge_facts(*groups: list[dict]) -> list[dict]:
        """合并事实并按来源和内容去重。"""
        merged: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for group in groups:
            for fact in group:
                key = (
                    str(fact.get("source_url", "")).strip(),
                    str(fact.get("content", "")).strip(),
                )
                if key not in seen:
                    seen.add(key)
                    merged.append(fact)
        return merged
```

### 79db291 文件：backend/app/core/__init__.py

```text
"""外部服务和基础设施适配器。"""
```

### 79db291 文件：backend/app/core/llm_client.py

```text
"""统一的大模型客户端接口。

Agent 只依赖这里定义的接口，不直接依赖某一家模型服务的 SDK。
当前先实现 MockLLMClient，后续再实现真实的 OpenAI 兼容客户端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """所有 LLM 客户端都必须提供的能力。"""

    @abstractmethod
    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """让模型返回结构化 JSON 数据。"""
        raise NotImplementedError

    @abstractmethod
    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        """让模型返回普通文本。"""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """不联网的确定性客户端。

    Mock 的作用是先验证业务流程和状态流转，而不是模拟真正的智能程度。
    同样的输入会得到同样的输出，测试因此稳定且容易理解。
    """

    async def complete_json(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if role == "planner":
            query = str(payload.get("query", "")).strip()
            if not query:
                raise ValueError("planner 请求缺少 query")

            return {
                "outline": [
                    {
                        "title": "现状与定义",
                        "description": f"明确“{query}”的研究范围和当前现状。",
                        "search_queries": [f"{query} 的当前现状和关键定义"],
                    },
                    {
                        "title": "问题与证据",
                        "description": "整理公开来源中的事实、数据和主要争议。",
                        "search_queries": [f"{query} 的主要问题和公开证据"],
                    },
                    {
                        "title": "趋势与建议",
                        "description": "根据已有证据判断未来趋势并提出建议。",
                        "search_queries": [f"{query} 的未来趋势和改进建议"],
                    },
                ],
                "research_questions": [
                    f"{query} 的当前现状和关键定义是什么？",
                    f"{query} 面临哪些主要问题，有哪些公开证据？",
                    f"{query} 的未来趋势和改进建议是什么？",
                ],
                "hypotheses": [
                    {
                        "id": "h_1",
                        "content": f"{query} 的发展趋势会受到政策和市场需求共同影响。",
                        "status": "unverified",
                    }
                ],
                "key_entities": [],
            }

        if role == "fact_extractor":
            facts = []
            for source in payload.get("sources", []):
                content = str(source.get("content") or source.get("snippet") or "").strip()
                url = str(source.get("url", "")).strip()
                if not content or not url:
                    continue
                facts.append(
                    {
                        "content": content,
                        "source_title": str(source.get("title", "")).strip(),
                        "source_url": url,
                        "source_type": "web",
                        "confidence": 0.7,
                    }
                )
            return {"facts": facts}

        if role == "critic":
            report = str(payload.get("report", "")).strip()
            facts = payload.get("facts", [])
            sources = payload.get("sources", [])
            if not report:
                raise ValueError("critic 请求缺少 report")

            passed = bool(facts and sources and "http" in report)
            return {
                "verdict": "pass" if passed else "needs_revision",
                "quality_score": 8.0 if passed else 4.0,
                "summary": "报告中的事实都关联了来源。" if passed else "报告缺少足够的可验证证据。",
                "needs_more_research": not passed,
                "issues": [] if passed else ["需要补充带来源的事实"],
                "search_queries": [] if passed else ["补充权威来源和数据"],
            }

        raise ValueError(f"MockLLMClient 暂时不支持角色: {role}")

    async def complete_text(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> str:
        if role != "writer":
            raise ValueError(f"MockLLMClient 暂时不支持文本角色: {role}")

        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("writer 请求缺少 query")

        if payload.get("mode") == "section":
            section = payload.get("section", {})
            title = str(section.get("title", "本章节")).strip() or "本章节"
            facts = payload.get("facts", [])
            lines = [f"本章节围绕“{title}”整理研究证据。"]
            for fact in facts:
                content = str(fact.get("content", "")).strip()
                if not content:
                    continue
                source_title = str(fact.get("source_title", "来源")).strip() or "来源"
                source_url = str(fact.get("source_url", "")).strip()
                citation = f" ([{source_title}]({source_url}))" if source_url else ""
                lines.append(f"- {content}{citation}")
            if len(lines) == 1:
                lines.append("当前章节还没有可引用的事实。")
            return "\n".join(lines)

        if payload.get("mode") == "report":
            outline = payload.get("outline", [])
            draft_sections = payload.get("draft_sections", {})
            lines = [
                "## 执行摘要",
                "",
                f"本报告围绕“{query}”整理公开资料，并按研究大纲组织可验证证据。",
                "",
                "## 研究发现",
                "",
            ]
            for index, section in enumerate(outline, start=1):
                section_id = str(section.get("id", f"sec_{index}")).strip()
                title = str(section.get("title", f"第 {index} 节")).strip()
                content = str(draft_sections.get(section_id, "")).strip()
                if content:
                    lines.extend([f"### {index}. {title}", "", content, ""])

            review = payload.get("review_result", {})
            issues = review.get("issues", []) if isinstance(review, dict) else []
            if issues:
                lines.extend(["## 根据审核意见修订", ""])
                lines.extend(f"- 已处理：{issue}" for issue in issues)
                lines.append("")

            lines.extend(
                [
                    "## 结论",
                    "",
                    "以上结论需要结合更多官方统计和行业报告继续验证。",
                ]
            )
            return "\n".join(lines)

        facts = payload.get("facts", [])
        lines = [
            "## 执行摘要",
            "",
            f"本报告围绕“{query}”整理公开资料，并只使用已收集的来源作为证据。",
            "",
            "## 研究发现",
            "",
        ]
        if facts:
            for index, fact in enumerate(facts, start=1):
                content = str(fact.get("content", "")).strip()
                title = str(fact.get("source_title", "来源")).strip() or "来源"
                url = str(fact.get("source_url", "")).strip()
                lines.append(f"{index}. {content} ([{title}]({url}))")
        else:
            lines.append("当前没有收集到可引用的事实，无法形成可靠结论。")

        review = payload.get("review_result", {})
        issues = review.get("issues", []) if isinstance(review, dict) else []
        if issues:
            lines.extend(["", "## 根据审核意见修订", ""])
            lines.extend(f"- 已处理：{issue}" for issue in issues)

        lines.extend(
            [
                "",
                "## 结论",
                "",
                "以上结论需要结合更多官方统计和行业报告继续验证。",
            ]
        )
        return "\n".join(lines)
```

### 79db291 文件：backend/app/core/search_client.py

```text
"""统一的搜索客户端接口。

搜索客户端只负责获取候选来源。
它不负责判断来源是否可信，也不负责把来源写成研究报告。
这些职责会交给后面的 Researcher 和 Writer。
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SearchResult:
    """一条搜索结果的统一格式。"""

    title: str
    url: str
    snippet: str
    query: str
    content: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换成适合放进 ResearchState 的字典。"""
        return asdict(self)


class SearchClient(ABC):
    """所有搜索服务都要遵守的接口。"""

    @abstractmethod
    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """根据一个研究子问题返回候选来源。"""
        raise NotImplementedError


class MockSearchClient(SearchClient):
    """本地模拟搜索服务。

    URL 使用查询内容的摘要生成，因此同一个查询每次都会得到同一个来源。
    这样测试不会依赖网络，也方便观察数据流。
    """

    async def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("搜索问题不能为空")
        if limit < 1:
            raise ValueError("limit 必须大于 0")

        digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
        result = SearchResult(
            title=f"公开资料：{query}",
            url=f"https://example.com/research/{digest}",
            snippet=f"这是针对“{query}”的模拟公开资料摘要，用于验证研究流程。",
            query=query,
            content=f"模拟资料正文：{query}需要结合公开数据、行业实践和政策环境综合判断。",
        )
        return [result]
```

### 79db291 文件：backend/app/domain/__init__.py

```text
"""Domain models used by the research workflow."""
```

### 79db291 文件：backend/app/domain/events.py

```text
"""研究工作流对外发布的事件格式。

这一层先不绑定 SSE、WebSocket 或具体前端，只定义一个稳定的 Python
字典格式。以后无论接哪种传输方式，都可以把同一类事件发送给调用方。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


class ResearchEventType:
    """工作流允许对外发布的事件类型。"""

    RESEARCH_STARTED = "research_started"
    PHASE_STARTED = "phase_started"
    OUTLINE_READY = "outline_ready"
    RESEARCH_EVIDENCE_READY = "research_evidence_ready"
    DRAFT_READY = "draft_ready"
    REVIEW_COMPLETED = "review_completed"
    RESEARCH_COMPLETED = "research_completed"


EVENT_TYPES = frozenset(
    {
        ResearchEventType.RESEARCH_STARTED,
        ResearchEventType.PHASE_STARTED,
        ResearchEventType.OUTLINE_READY,
        ResearchEventType.RESEARCH_EVIDENCE_READY,
        ResearchEventType.DRAFT_READY,
        ResearchEventType.REVIEW_COMPLETED,
        ResearchEventType.RESEARCH_COMPLETED,
    }
)

RESEARCH_PHASES = frozenset(
    {
        "init",
        "planning",
        "researching",
        "analyzing",
        "writing",
        "reviewing",
        "re_researching",
        "revising",
        "completed",
    }
)

EVENT_REQUIRED_FIELDS = {
    ResearchEventType.RESEARCH_STARTED: frozenset({"query", "max_iterations"}),
    ResearchEventType.PHASE_STARTED: frozenset({"agent"}),
    ResearchEventType.OUTLINE_READY: frozenset(
        {"outline", "research_questions", "hypotheses", "key_entities", "mind_map"}
    ),
    ResearchEventType.RESEARCH_EVIDENCE_READY: frozenset(
        {"supplementary", "source_count", "fact_count", "sources", "facts", "references"}
    ),
    ResearchEventType.DRAFT_READY: frozenset(
        {"report", "outline", "draft_sections", "revision"}
    ),
    ResearchEventType.REVIEW_COMPLETED: frozenset(
        {"review_result", "critic_feedback", "quality_score"}
    ),
    ResearchEventType.RESEARCH_COMPLETED: frozenset(
        {"report", "quality_score", "references", "review_result", "critic_feedback"}
    ),
}

EVENT_ENVELOPE_FIELDS = frozenset({"type", "session_id", "phase", "iteration"})


@dataclass(frozen=True)
class ResearchEvent:
    """一次研究流程进度更新。

    ``data`` 中的字段会在 ``to_dict`` 时展开到事件顶层，调用方因此可以
    直接读取 ``event["report"]``、``event["references"]`` 等结果字段。
    """

    type: str
    session_id: str
    phase: str
    iteration: int = 0
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """校验所有事件共有的外层字段。"""
        if not isinstance(self.type, str) or self.type not in EVENT_TYPES:
            raise ValueError(f"不支持的研究事件类型: {self.type!r}")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("研究事件 session_id 不能为空")
        if not isinstance(self.phase, str) or self.phase not in RESEARCH_PHASES:
            raise ValueError(f"不支持的研究阶段: {self.phase!r}")
        if isinstance(self.iteration, bool) or not isinstance(self.iteration, int):
            raise ValueError("研究事件 iteration 必须是整数")
        if self.iteration < 0:
            raise ValueError("研究事件 iteration 不能小于 0")
        if not isinstance(self.data, dict):
            raise ValueError("研究事件 data 必须是字典")
        reserved_fields = EVENT_ENVELOPE_FIELDS & self.data.keys()
        if reserved_fields:
            reserved = ", ".join(sorted(reserved_fields))
            raise ValueError(f"研究事件 data 不能覆盖公共字段: {reserved}")
        missing_fields = EVENT_REQUIRED_FIELDS[self.type] - self.data.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"{self.type} 缺少必需字段: {missing}")

    def to_dict(self) -> dict[str, Any]:
        """转换成可被 API、SSE 或测试直接使用的普通字典。"""
        event = {
            "type": self.type,
            "session_id": self.session_id,
            "phase": self.phase,
            "iteration": self.iteration,
        }
        event.update(deepcopy(self.data))
        return event

```

### 79db291 文件：backend/app/domain/models.py

```text
"""DeepResearch V2 使用的基础领域对象。

这些对象先只描述数据形状，不负责调用 LLM、搜索服务或数据库。
把数据形状单独放在这里，可以让后续 Agent 共享同一套结构。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SectionType = Literal["qualitative", "quantitative", "mixed"]
SectionStatus = Literal["pending", "researching", "drafted", "reviewed", "final"]
HypothesisStatus = Literal[
    "unverified",
    "supported",
    "refuted",
    "partially_supported",
]
ChartType = Literal["line", "bar", "pie", "scatter", "table", "heatmap"]
IssueType = Literal[
    "missing_source",
    "logic_error",
    "bias",
    "hallucination",
    "outdated",
    "incomplete",
]
IssueSeverity = Literal["critical", "major", "minor"]


@dataclass
class Section:
    """研究报告中的一个章节。"""

    id: str
    title: str
    description: str = ""
    section_type: SectionType = "mixed"
    status: SectionStatus = "pending"
    content: str = ""
    sources: list[str] = field(default_factory=list)
    subsections: list[Section] = field(default_factory=list)
    requires_data: bool = False
    requires_chart: bool = False
    priority: int = 0
    search_queries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换成可以放入 ResearchState 的普通字典。"""
        return asdict(self)


@dataclass
class Hypothesis:
    """研究开始时提出、再由证据验证的假设。"""

    id: str
    content: str
    status: HypothesisStatus = "unverified"
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataPoint:
    """可以被分析或绘图使用的结构化数据点。"""

    id: str
    name: str
    value: Any
    unit: str = ""
    year: int | None = None
    source: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Chart:
    """DataAnalyst 或 CodeWizard 生成的图表结果。"""

    id: str
    title: str
    chart_type: ChartType
    data: dict[str, Any] = field(default_factory=dict)
    code: str = ""
    image_path: str | None = None
    image_base64: str | None = None
    section_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CriticFeedback:
    """审核 Agent 针对报告或章节提出的一条问题。"""

    id: str
    target_section: str
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    suggestion: str
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

```

### 79db291 文件：backend/app/domain/state.py

```text
"""DeepResearch V2 的共享工作状态。

所有研究 Agent 读取和更新同一个任务状态。状态只保存数据，流程逻辑
由 workflow 编排，领域对象由 domain.models 定义。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class ResearchState:
    """一次研究任务从开始到结束所需要的全部核心数据。"""

    # 用户输入和任务身份
    query: str
    session_id: str = field(default_factory=lambda: str(uuid4()))

    # 当前阶段：init / planning / researching / analyzing / writing /
    # reviewing / re_researching / revising / completed
    phase: str = "init"

    # 审核循环次数
    iteration: int = 0
    max_iterations: int = 1

    # 规划结果
    # V2 章节大纲。后续 Planner 会逐步使用 domain.models.Section。
    outline: list[dict[str, Any]] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    mind_map: dict[str, Any] = field(default_factory=dict)
    knowledge_graph: dict[str, Any] = field(
        default_factory=lambda: {"nodes": [], "edges": []}
    )
    pending_search_queries: list[str] = field(default_factory=list)

    # 研究证据
    # 原始搜索结果；事实提取和后续分析都从这里读取。
    raw_sources: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    data_points: list[dict[str, Any]] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)

    # 写作和审核结果
    draft_sections: dict[str, str] = field(default_factory=dict)
    final_report: str = ""
    charts: list[dict[str, Any]] = field(default_factory=list)
    code_executions: list[dict[str, Any]] = field(default_factory=list)
    review_result: dict[str, Any] = field(default_factory=dict)
    critic_feedback: list[dict[str, Any]] = field(default_factory=list)
    unresolved_issues: int = 0
    quality_score: float = 0.0

    # 运行记录
    logs: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

### 79db291 文件：backend/app/scripts/__init__.py

```text
"""Executable learning scripts."""
```

### 79db291 文件：backend/app/scripts/run_research.py

```text
"""从命令行运行一次 Mock DeepResearch。"""

from __future__ import annotations

import argparse
import asyncio

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState
from app.workflow.research_workflow import ResearchWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行一次学习版 DeepResearch")
    parser.add_argument(
        "query",
        nargs="?",
        help="研究问题；不传时会进入交互式输入",
    )
    return parser


def print_state(state: ResearchState) -> None:
    print("\n" + "=" * 60)
    print("研究计划")
    print("=" * 60)
    for index, item in enumerate(state.outline, start=1):
        print(f"{index}. {item['title']}：{item['description']}")

    print("\n" + "=" * 60)
    print(f"搜索来源（{len(state.raw_sources)} 条）")
    print("=" * 60)
    for index, source in enumerate(state.raw_sources, start=1):
        print(f"{index}. {source['title']}")
        print(f"   URL: {source['url']}")

    print("\n" + "=" * 60)
    print(f"结构化事实（{len(state.facts)} 条）")
    print("=" * 60)
    for index, fact in enumerate(state.facts, start=1):
        print(f"{index}. {fact['content']}")
        print(f"   来源: {fact['source_url']}")

    print("\n" + "=" * 60)
    print("最终报告")
    print("=" * 60)
    print(state.final_report)

    print("\n" + "=" * 60)
    print("审核结果")
    print("=" * 60)
    print(f"结论: {state.review_result['verdict']}")
    print(f"评分: {state.quality_score}/10")
    print(f"摘要: {state.review_result['summary']}")
    print(f"任务阶段: {state.phase}")
    print(f"会话 ID: {state.session_id}")


async def run(query: str) -> ResearchState:
    workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())
    return await workflow.run(query)


def main() -> None:
    args = build_parser().parse_args()
    query = (args.query or input("请输入研究问题：")).strip()
    if not query:
        raise SystemExit("研究问题不能为空")
    state = asyncio.run(run(query))
    print_state(state)


if __name__ == "__main__":
    main()
```

### 79db291 文件：backend/app/workflow/__init__.py

```text
"""Research workflow orchestration."""
```

### 79db291 文件：backend/app/workflow/research_workflow.py

```text
"""把多个 Agent 编排成一次完整研究任务。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient
from app.core.search_client import SearchClient
from app.domain.events import ResearchEvent
from app.domain.state import ResearchState


class ResearchWorkflow:
    """学习版 DeepResearch 的研究编排器。

    每一步都显式写出来，便于学习状态如何在 Agent 之间流动。
    ``run`` 适合一次性拿到结果，``stream`` 适合逐步消费进度事件。
    SSE 和数据库等外层能力后续再加入；审核修订循环在本轮实现。
    """

    def __init__(
        self,
        llm: LLMClient,
        search: SearchClient,
        results_per_question: int = 3,
        max_iterations: int = 1,
    ):
        if max_iterations < 0:
            raise ValueError("max_iterations 不能小于 0")
        self.max_iterations = max_iterations
        self.planner = PlannerAgent(llm)
        self.researcher = ResearcherAgent(search, results_per_question)
        self.fact_extractor = FactExtractorAgent(llm)
        self.writer = WriterAgent(llm)
        self.critic = CriticAgent(llm)

    async def run(
        self,
        query: str,
        session_id: str | None = None,
    ) -> ResearchState:
        """执行一次完整研究并返回最终状态。"""
        state = self._new_state(query, session_id)
        async for _ in self._stream_state(state):
            # run 保留一次性调用方式，只忽略中间事件。
            pass
        return state

    async def stream(
        self,
        query: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """逐步产出研究进度事件，最后一个事件包含完整结果。

        这个方法仍然使用和 ``run`` 相同的 Agent 和状态对象，因此不会
        产生两套业务逻辑。当前返回普通字典，后续接 FastAPI SSE 时可以
        直接序列化；暂时不需要启动真实服务就能测试事件顺序。
        """
        state = self._new_state(query, session_id)
        async for event in self._stream_state(state):
            yield event

    def _new_state(
        self,
        query: str,
        session_id: str | None,
    ) -> ResearchState:
        """创建一次研究任务的初始状态。"""
        return ResearchState(
            query=query,
            session_id=session_id or str(uuid4()),
            max_iterations=self.max_iterations,
        )

    async def _stream_state(
        self,
        state: ResearchState,
    ) -> AsyncIterator[dict[str, Any]]:
        """执行工作流并发布事件；``run`` 和 ``stream`` 共用此实现。"""
        yield self._event(
            state,
            "research_started",
            query=state.query,
            max_iterations=state.max_iterations,
        )

        yield self._event(
            state,
            "phase_started",
            phase="planning",
            agent=self.planner.name,
        )
        await self.planner.run(state)
        yield self._event(
            state,
            "outline_ready",
            outline=state.outline,
            research_questions=state.research_questions,
            hypotheses=state.hypotheses,
            key_entities=state.key_entities,
            mind_map=state.mind_map,
        )

        async for event in self._run_research_phase(state, supplementary=False):
            yield event
        yield self._event(
            state,
            "phase_started",
            phase="writing",
            agent=self.writer.name,
        )
        await self.writer.run(state)
        yield self._event(
            state,
            "draft_ready",
            report=state.final_report,
            outline=state.outline,
            draft_sections=state.draft_sections,
            revision=False,
        )

        while True:
            yield self._event(
                state,
                "phase_started",
                phase="reviewing",
                agent=self.critic.name,
            )
            await self.critic.run(state)
            yield self._event(
                state,
                "review_completed",
                review_result=state.review_result,
                critic_feedback=state.critic_feedback,
                quality_score=state.quality_score,
            )

            if state.review_result["verdict"] == "pass":
                break
            if state.iteration >= state.max_iterations:
                break

            state.iteration += 1
            if state.review_result["needs_more_research"]:
                state.pending_search_queries = (
                    state.review_result["search_queries"]
                    or state.review_result["issues"]
                    or state.research_questions
                )
                async for event in self._run_research_phase(
                    state,
                    supplementary=True,
                ):
                    yield event

            # 如果无需新搜索，Writer 根据 review_result 做内容修订；
            # 如果补充了证据，则 Writer 同时整合新事实和审核意见。
            yield self._event(
                state,
                "phase_started",
                phase="writing",
                agent=self.writer.name,
                revision=True,
            )
            await self.writer.run(state)
            yield self._event(
                state,
                "draft_ready",
                report=state.final_report,
                outline=state.outline,
                draft_sections=state.draft_sections,
                revision=True,
            )

        state.phase = "completed"
        yield self._event(
            state,
            "research_completed",
            report=state.final_report,
            quality_score=state.quality_score,
            references=state.references,
            review_result=state.review_result,
            critic_feedback=state.critic_feedback,
        )

    async def _run_research_phase(
        self,
        state: ResearchState,
        *,
        supplementary: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """运行搜索和事实提取，并逐步发布研究阶段事件。"""
        yield self._event(
            state,
            "phase_started",
            phase="researching",
            agent=self.researcher.name,
            supplementary=supplementary,
        )
        await self.researcher.run(state)
        await self.fact_extractor.run(state)
        yield self._event(
            state,
            "research_evidence_ready",
            supplementary=supplementary,
            source_count=len(state.raw_sources),
            fact_count=len(state.facts),
            sources=state.raw_sources,
            facts=state.facts,
            references=state.references,
        )

    @staticmethod
    def _event(
        state: ResearchState,
        event_type: str,
        *,
        phase: str | None = None,
        **data: Any,
    ) -> dict[str, Any]:
        """根据当前状态创建一个普通事件字典。"""
        return ResearchEvent(
            type=event_type,
            session_id=state.session_id,
            phase=phase or state.phase,
            iteration=state.iteration,
            data=data,
        ).to_dict()
```

### 79db291 文件：backend/tests/__init__.py

```text
"""Tests for the learning backend."""
```

### 79db291 文件：backend/tests/test_base_agent.py

```text
import asyncio
import unittest

from app.agents.base import BaseAgent
from app.domain.state import ResearchState


class DemoAgent(BaseAgent):
    name = "demo"

    async def run(self, state: ResearchState) -> ResearchState:
        state.phase = "demo_completed"
        return state


class BaseAgentTests(unittest.TestCase):
    def test_concrete_agent_updates_and_returns_state(self):
        state = ResearchState("测试问题")
        agent = DemoAgent()

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "demo_completed")
        self.assertEqual(agent.name, "demo")

    def test_base_agent_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            BaseAgent()


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_critic.py

```text
import asyncio
import unittest

from app.agents.critic import CriticAgent
from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenCriticClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"verdict": "unknown", "quality_score": 20, "issues": "错误格式"}

    async def complete_text(self, role, payload):
        return ""


class CriticAgentTests(unittest.TestCase):
    def test_critic_approves_source_grounded_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            await CriticAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "reviewing")
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)
        self.assertEqual(state.review_result["issues"], [])

    def test_critic_rejects_invalid_result(self):
        state = ResearchState("测试问题")
        state.final_report = "## 报告\n内容"

        with self.assertRaisesRegex(ValueError, "verdict"):
            asyncio.run(CriticAgent(BrokenCriticClient()).run(state))

    def test_critic_requires_report(self):
        with self.assertRaisesRegex(ValueError, "审核的报告"):
            asyncio.run(CriticAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_domain_models.py

```text
import unittest

from app.domain.models import (
    Chart,
    CriticFeedback,
    DataPoint,
    Hypothesis,
    Section,
)


class DomainModelTests(unittest.TestCase):
    def test_section_serializes_nested_sections(self):
        section = Section(
            id="sec-1",
            title="行业概况",
            description="研究行业规模和定义",
            requires_data=True,
            search_queries=["行业规模"],
            subsections=[Section(id="sec-1-1", title="市场定义")],
        )

        result = section.to_dict()

        self.assertEqual(result["id"], "sec-1")
        self.assertTrue(result["requires_data"])
        self.assertEqual(result["subsections"][0]["title"], "市场定义")

    def test_model_collections_are_not_shared(self):
        first = Hypothesis(id="h-1", content="第一个假设")
        second = Hypothesis(id="h-2", content="第二个假设")

        first.evidence_for.append("支持证据")

        self.assertEqual(first.evidence_for, ["支持证据"])
        self.assertEqual(second.evidence_for, [])

    def test_data_point_and_chart_keep_analysis_fields(self):
        data_point = DataPoint(
            id="dp-1",
            name="市场规模",
            value=120.5,
            unit="亿元",
            year=2025,
            source="https://example.com/source",
            confidence=0.9,
        )
        chart = Chart(
            id="chart-1",
            title="市场规模趋势",
            chart_type="line",
            data={"x": [2024, 2025], "y": [100, 120.5]},
            section_id="sec-1",
        )

        self.assertEqual(data_point.to_dict()["year"], 2025)
        self.assertEqual(data_point.to_dict()["confidence"], 0.9)
        self.assertEqual(chart.to_dict()["chart_type"], "line")
        self.assertEqual(chart.to_dict()["section_id"], "sec-1")

    def test_critic_feedback_starts_unresolved(self):
        feedback = CriticFeedback(
            id="issue-1",
            target_section="sec-1",
            issue_type="missing_source",
            severity="major",
            description="关键数据缺少来源",
            suggestion="补充官方统计来源",
        )

        self.assertFalse(feedback.resolved)
        self.assertEqual(feedback.to_dict()["severity"], "major")


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_events.py

```text
import unittest

from app.domain.events import (
    EVENT_TYPES,
    EVENT_REQUIRED_FIELDS,
    RESEARCH_PHASES,
    ResearchEvent,
    ResearchEventType,
)


class ResearchEventTests(unittest.TestCase):
    def test_event_type_constants_are_registered(self):
        self.assertIn(ResearchEventType.OUTLINE_READY, EVENT_TYPES)
        self.assertIn("planning", RESEARCH_PHASES)

    def test_event_to_dict_keeps_common_fields_and_data(self):
        event = ResearchEvent(
            type=ResearchEventType.OUTLINE_READY,
            session_id="session-001",
            phase="planning",
            data={
                "outline": [{"id": "sec-1"}],
                "research_questions": [],
                "hypotheses": [],
                "key_entities": [],
                "mind_map": {},
            },
        )

        self.assertEqual(
            event.to_dict(),
            {
                "type": "outline_ready",
                "session_id": "session-001",
                "phase": "planning",
                "iteration": 0,
                "outline": [{"id": "sec-1"}],
                "research_questions": [],
                "hypotheses": [],
                "key_entities": [],
                "mind_map": {},
            },
        )

    def test_each_event_type_declares_required_fields(self):
        self.assertEqual(set(EVENT_TYPES), set(EVENT_REQUIRED_FIELDS))
        self.assertTrue(
            all(fields for fields in EVENT_REQUIRED_FIELDS.values()),
        )

    def test_event_rejects_missing_business_fields(self):
        with self.assertRaisesRegex(ValueError, "outline_ready.*必需字段"):
            ResearchEvent(
                ResearchEventType.OUTLINE_READY,
                "session-001",
                "planning",
                data={"outline": []},
            )

    def test_event_rejects_unknown_type(self):
        with self.assertRaisesRegex(ValueError, "事件类型"):
            ResearchEvent("unknown", "session-001", "planning")

    def test_event_rejects_empty_session_id(self):
        with self.assertRaisesRegex(ValueError, "session_id"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "  ", "planning")

    def test_event_rejects_unknown_phase(self):
        with self.assertRaisesRegex(ValueError, "研究阶段"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "unknown")

    def test_event_rejects_invalid_iteration(self):
        with self.assertRaisesRegex(ValueError, "iteration"):
            ResearchEvent(ResearchEventType.PHASE_STARTED, "session-001", "planning", -1)

    def test_event_rejects_non_dict_data(self):
        with self.assertRaisesRegex(ValueError, "data"):
            ResearchEvent(
                ResearchEventType.PHASE_STARTED,
                "session-001",
                "planning",
                data=[],
            )

    def test_event_data_cannot_replace_common_fields(self):
        with self.assertRaisesRegex(ValueError, "session_id"):
            ResearchEvent(
                ResearchEventType.PHASE_STARTED,
                "session-001",
                "planning",
                data={"agent": "planner", "session_id": "other-session"},
            )


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_fact_extractor.py

```text
import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class BrokenFactClient(LLMClient):
    async def complete_json(self, role, payload):
        return {
            "facts": [
                {
                    "content": "这条事实引用了不存在的来源。",
                    "source_url": "https://unknown.example.com",
                    "confidence": 0.8,
                }
            ]
        }

    async def complete_text(self, role, payload):
        return ""


class FactExtractorAgentTests(unittest.TestCase):
    def test_fact_extractor_turns_raw_sources_into_facts(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(MockLLMClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(all(fact["source_url"] for fact in state.facts))
        self.assertTrue(all(0 <= fact["confidence"] <= 1 for fact in state.facts))
        self.assertEqual(
            {fact["section_id"] for fact in state.facts},
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertTrue(all(fact["section_title"] for fact in state.facts))

    def test_fact_extractor_rejects_unknown_source_url(self):
        state = ResearchState("测试问题")
        state.raw_sources = [
            {
                "title": "已知来源",
                "url": "https://known.example.com",
                "snippet": "摘要",
            }
        ]

        with self.assertRaisesRegex(ValueError, "未知来源"):
            asyncio.run(FactExtractorAgent(BrokenFactClient()).run(state))

    def test_fact_extractor_requires_sources(self):
        with self.assertRaisesRegex(ValueError, "来源"):
            asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_llm_client.py

```text
import asyncio
import unittest

from app.core.llm_client import LLMClient, MockLLMClient


class LLMClientTests(unittest.TestCase):
    def test_mock_client_implements_llm_interface(self):
        self.assertIsInstance(MockLLMClient(), LLMClient)

    def test_mock_planner_returns_structured_result(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "planner",
                {"query": "新能源汽车行业的发展趋势是什么？"},
            )
        )

        self.assertEqual(len(result["outline"]), 3)
        self.assertEqual(len(result["research_questions"]), 3)
        self.assertEqual(result["hypotheses"][0]["status"], "unverified")
        self.assertIn("新能源汽车", result["research_questions"][0])

    def test_mock_fact_extractor_returns_source_grounded_facts(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "fact_extractor",
                {
                    "query": "测试行业",
                    "sources": [
                        {
                            "title": "测试来源",
                            "url": "https://example.com/source",
                            "content": "测试来源中的明确事实。",
                        }
                    ],
                },
            )
        )

        self.assertEqual(len(result["facts"]), 1)
        self.assertEqual(result["facts"][0]["source_url"], "https://example.com/source")

    def test_mock_critic_approves_cited_report(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_json(
                "critic",
                {
                    "query": "测试行业",
                    "report": "报告内容 https://example.com/source",
                    "facts": [{"content": "事实"}],
                    "sources": [{"url": "https://example.com/source"}],
                },
            )
        )

        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["quality_score"], 8.0)

    def test_mock_client_rejects_unknown_role(self):
        client = MockLLMClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.complete_json("unknown", {"query": "测试"}))

    def test_mock_writer_returns_text(self):
        client = MockLLMClient()

        result = asyncio.run(
            client.complete_text(
                "writer",
                {
                    "query": "测试行业",
                    "facts": [
                        {
                            "content": "测试事实。",
                            "source_title": "测试来源",
                            "source_url": "https://example.com/source",
                        }
                    ],
                },
            )
        )

        self.assertIn("测试行业", result)
        self.assertIn("测试事实", result)
        self.assertIn("https://example.com/source", result)


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_planner.py

```text
import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.core.llm_client import LLMClient, MockLLMClient
from app.domain.state import ResearchState


class BrokenPlannerClient(LLMClient):
    async def complete_json(self, role, payload):
        return {"outline": [], "research_questions": []}

    async def complete_text(self, role, payload):
        return ""


class PlannerAgentTests(unittest.TestCase):
    def test_planner_writes_outline_into_state(self):
        state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
        agent = PlannerAgent(MockLLMClient())

        result = asyncio.run(agent.run(state))

        self.assertIs(result, state)
        self.assertEqual(result.phase, "planning")
        self.assertEqual(len(result.outline), 3)
        self.assertEqual(len(result.research_questions), 3)
        self.assertEqual(result.outline[0]["id"], "sec_1")
        self.assertEqual(result.outline[0]["status"], "pending")
        self.assertEqual(len(result.hypotheses), 1)
        self.assertEqual(result.hypotheses[0]["status"], "unverified")
        self.assertIn("新能源汽车", result.outline[0]["description"])

    def test_planner_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            asyncio.run(PlannerAgent(MockLLMClient()).run(ResearchState("   ")))

    def test_planner_rejects_invalid_llm_result(self):
        with self.assertRaisesRegex(ValueError, "非空列表"):
            asyncio.run(PlannerAgent(BrokenPlannerClient()).run(ResearchState("测试问题")))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_researcher.py

```text
import asyncio
import unittest

from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class ResearcherAgentTests(unittest.TestCase):
    def test_researcher_collects_sources_after_planning(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            await PlannerAgent(MockLLMClient()).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "researching")
        self.assertEqual(len(state.research_questions), 3)
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.references), 3)
        self.assertTrue(all(source["url"].startswith("https://") for source in state.raw_sources))
        self.assertEqual(
            {source["section_id"] for source in state.raw_sources},
            {"sec_1", "sec_2", "sec_3"},
        )

    def test_researcher_uses_all_queries_from_a_section(self):
        async def run():
            state = ResearchState("测试问题")
            state.outline = [
                {
                    "id": "sec-market",
                    "title": "市场规模",
                    "search_queries": ["市场规模 2024", "市场规模 2025"],
                }
            ]
            return await ResearcherAgent(MockSearchClient()).run(state)

        state = asyncio.run(run())

        self.assertEqual(len(state.raw_sources), 2)
        self.assertEqual(
            {source["query"] for source in state.raw_sources},
            {"市场规模 2024", "市场规模 2025"},
        )
        self.assertTrue(
            all(source["section_id"] == "sec-market" for source in state.raw_sources)
        )

    def test_researcher_deduplicates_existing_source_urls(self):
        async def run():
            state = ResearchState("测试问题")
            state.research_questions = ["相同问题", "相同问题"]
            return await ResearcherAgent(MockSearchClient()).run(state)

        state = asyncio.run(run())

        self.assertEqual(len(state.raw_sources), 1)
        self.assertEqual(len(state.references), 1)

    def test_researcher_rejects_missing_questions(self):
        state = ResearchState("还没有规划的问题")

        with self.assertRaisesRegex(ValueError, "研究子问题"):
            asyncio.run(ResearcherAgent(MockSearchClient()).run(state))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_run_research.py

```text
import asyncio
import unittest
from contextlib import redirect_stdout
from io import StringIO

from app.scripts.run_research import print_state, run


class RunResearchScriptTests(unittest.TestCase):
    def test_script_run_returns_completed_state(self):
        state = asyncio.run(run("测试行业的现状是什么？"))

        self.assertEqual(state.phase, "completed")
        self.assertTrue(state.final_report)

    def test_print_state_contains_key_sections(self):
        state = asyncio.run(run("测试行业的现状是什么？"))
        output = StringIO()

        with redirect_stdout(output):
            print_state(state)

        text = output.getvalue()
        self.assertIn("研究计划", text)
        self.assertIn("搜索来源", text)
        self.assertIn("结构化事实", text)
        self.assertIn("最终报告", text)
        self.assertIn("审核结果", text)


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_search_client.py

```text
import asyncio
import unittest

from app.core.search_client import MockSearchClient, SearchClient, SearchResult


class SearchClientTests(unittest.TestCase):
    def test_mock_client_implements_search_interface(self):
        self.assertIsInstance(MockSearchClient(), SearchClient)

    def test_search_returns_normalized_result(self):
        client = MockSearchClient()

        results = asyncio.run(client.search("新能源汽车行业的市场规模是什么？"))

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SearchResult)
        self.assertTrue(results[0].title)
        self.assertTrue(results[0].url.startswith("https://"))
        self.assertTrue(results[0].snippet)
        self.assertEqual(results[0].query, "新能源汽车行业的市场规模是什么？")

    def test_same_query_has_stable_url(self):
        client = MockSearchClient()

        first = asyncio.run(client.search("稳定查询"))[0]
        second = asyncio.run(client.search("稳定查询"))[0]

        self.assertEqual(first.url, second.url)

    def test_search_rejects_invalid_input(self):
        client = MockSearchClient()

        with self.assertRaises(ValueError):
            asyncio.run(client.search("   "))
        with self.assertRaises(ValueError):
            asyncio.run(client.search("测试", limit=0))


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_state.py

```text
import unittest

from app.domain.state import ResearchState


class ResearchStateTests(unittest.TestCase):
    def test_state_starts_empty(self):
        state = ResearchState("测试问题")

        self.assertEqual(state.query, "测试问题")
        self.assertEqual(state.phase, "init")
        self.assertEqual(state.outline, [])
        self.assertEqual(state.hypotheses, [])
        self.assertEqual(state.knowledge_graph, {"nodes": [], "edges": []})
        self.assertEqual(state.raw_sources, [])
        self.assertEqual(state.facts, [])
        self.assertEqual(state.data_points, [])
        self.assertEqual(state.charts, [])
        self.assertEqual(state.messages, [])
        self.assertFalse(hasattr(state, "plan"))
        self.assertFalse(hasattr(state, "sources"))
        self.assertFalse(hasattr(state, "review"))

    def test_mutable_fields_are_not_shared(self):
        first = ResearchState("第一个问题")
        second = ResearchState("第二个问题")

        first.outline.append({"title": "只属于第一个任务"})
        first.hypotheses.append({"id": "h-1"})
        first.knowledge_graph["nodes"].append({"id": "node-1"})
        first.data_points.append({"id": "dp-1"})
        first.charts.append({"id": "chart-1"})
        first.messages.append({"type": "progress"})

        self.assertEqual(len(first.outline), 1)
        self.assertEqual(second.outline, [])
        self.assertEqual(second.hypotheses, [])
        self.assertEqual(second.knowledge_graph, {"nodes": [], "edges": []})
        self.assertEqual(second.data_points, [])
        self.assertEqual(second.charts, [])
        self.assertEqual(second.messages, [])


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_stream_workflow.py

```text
import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)


async def collect_events(workflow, query, session_id=None):
    return [
        event
        async for event in workflow.stream(query, session_id=session_id)
    ]


class StreamWorkflowTests(unittest.TestCase):
    def test_stream_emits_ordered_events_and_final_result(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        events = asyncio.run(
            collect_events(
                workflow,
                "中国新能源汽车行业的发展趋势是什么？",
                session_id="stream-001",
            )
        )

        self.assertEqual(
            [event["type"] for event in events],
            [
                "research_started",
                "phase_started",
                "outline_ready",
                "phase_started",
                "research_evidence_ready",
                "phase_started",
                "draft_ready",
                "phase_started",
                "review_completed",
                "research_completed",
            ],
        )
        self.assertTrue(all(event["session_id"] == "stream-001" for event in events))
        self.assertEqual(events[1]["phase"], "planning")
        self.assertEqual(len(events[2]["outline"]), 3)
        self.assertEqual(events[2]["hypotheses"][0]["status"], "unverified")
        self.assertEqual(events[3]["phase"], "researching")
        self.assertEqual(events[4]["source_count"], 3)
        self.assertEqual(events[4]["fact_count"], 3)
        self.assertEqual(
            set(events[6]["draft_sections"]),
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertEqual(events[-1]["phase"], "completed")
        self.assertIn("## 执行摘要", events[-1]["report"])
        self.assertEqual(events[-1]["quality_score"], 8.0)
        self.assertEqual(len(events[-1]["references"]), 3)

    def test_stream_marks_supplementary_research_iteration(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=["补充最新行业数据"],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)

        events = asyncio.run(collect_events(workflow, "新能源汽车行业趋势"))

        evidence_events = [
            event for event in events if event["type"] == "research_evidence_ready"
        ]
        self.assertEqual(len(evidence_events), 2)
        self.assertFalse(evidence_events[0]["supplementary"])
        self.assertTrue(evidence_events[1]["supplementary"])
        self.assertEqual(evidence_events[1]["iteration"], 1)
        self.assertEqual(events[-1]["type"], "research_completed")
        self.assertEqual(events[-1]["review_result"]["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_workflow.py

```text
import asyncio
import unittest

from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.workflow.research_workflow import ResearchWorkflow


def review(verdict, *, more_research=False, issues=None, search_queries=None, score=5.0):
    return {
        "verdict": verdict,
        "quality_score": score,
        "summary": "测试审核结果",
        "needs_more_research": more_research,
        "issues": issues or [],
        "search_queries": search_queries or [],
    }


class SequencedReviewLLM(MockLLMClient):
    def __init__(self, reviews):
        self.reviews = iter(reviews)
        self.writer_payloads = []

    async def complete_json(self, role, payload):
        if role == "critic":
            return next(self.reviews)
        return await super().complete_json(role, payload)

    async def complete_text(self, role, payload):
        self.writer_payloads.append(payload)
        return await super().complete_text(role, payload)


class RecordingSearchClient(MockSearchClient):
    def __init__(self):
        self.queries = []

    async def search(self, query, limit=3):
        self.queries.append(query)
        return await super().search(query, limit)


class ResearchWorkflowTests(unittest.TestCase):
    def test_workflow_runs_full_research_chain(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("中国新能源汽车行业的发展趋势是什么？")
        )

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.outline[0]["title"], "现状与定义")
        self.assertEqual(len(state.raw_sources), 3)
        self.assertEqual(len(state.facts), 3)
        self.assertTrue(state.final_report)
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.quality_score, 8.0)

    def test_workflow_preserves_explicit_session_id(self):
        workflow = ResearchWorkflow(MockLLMClient(), MockSearchClient())

        state = asyncio.run(
            workflow.run("测试问题", session_id="session-001")
        )

        self.assertEqual(state.session_id, "session-001")

    def test_critic_routes_to_supplementary_research_then_passes(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    more_research=True,
                    issues=["补充最新行业数据"],
                    search_queries=["2025年新能源汽车行业数据"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = ResearchWorkflow(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 4)  # 3 个初始问题 + 1 个补充查询
        self.assertEqual(search.queries[-1], "2025年新能源汽车行业数据")
        self.assertEqual(len(state.raw_sources), 4)
        self.assertEqual(len(state.facts), 4)
        self.assertIn("2025年新能源汽车行业数据", state.final_report)

    def test_critic_routes_to_writer_revision_without_new_search(self):
        llm = SequencedReviewLLM(
            [
                review(
                    "needs_revision",
                    issues=["补充结论与证据之间的说明"],
                ),
                review("pass", score=8.0),
            ]
        )
        search = RecordingSearchClient()
        workflow = ResearchWorkflow(llm, search, max_iterations=1)

        state = asyncio.run(workflow.run("新能源汽车行业趋势"))

        self.assertEqual(state.review_result["verdict"], "pass")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(len(search.queries), 3)
        report_payloads = [
            payload for payload in llm.writer_payloads if payload.get("mode") == "report"
        ]
        self.assertEqual(len(report_payloads), 2)
        self.assertIn(
            "补充结论与证据之间的说明",
            report_payloads[1]["review_result"]["issues"],
        )
        self.assertIn("补充结论与证据之间的说明", state.final_report)

    def test_workflow_stops_after_max_iterations(self):
        llm = SequencedReviewLLM(
            [
                review("needs_revision", issues=["第一轮问题"]),
                review("needs_revision", issues=["仍需改进"], score=5.0),
            ]
        )
        workflow = ResearchWorkflow(llm, MockSearchClient(), max_iterations=1)

        state = asyncio.run(workflow.run("测试行业", session_id="bounded"))

        self.assertEqual(state.phase, "completed")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(state.review_result["verdict"], "needs_revision")
        self.assertEqual(state.review_result["issues"], ["仍需改进"])
        self.assertEqual(
            len([payload for payload in llm.writer_payloads if payload.get("mode") == "report"]),
            2,
        )

    def test_workflow_rejects_negative_iteration_limit(self):
        with self.assertRaisesRegex(ValueError, "max_iterations"):
            ResearchWorkflow(MockLLMClient(), MockSearchClient(), max_iterations=-1)


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：backend/tests/test_writer.py

```text
import asyncio
import unittest

from app.agents.fact_extractor import FactExtractorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.core.llm_client import MockLLMClient
from app.core.search_client import MockSearchClient
from app.domain.state import ResearchState


class WriterAgentTests(unittest.TestCase):
    def test_writer_generates_cited_report(self):
        async def run_chain():
            state = ResearchState("中国新能源汽车行业的发展趋势是什么？")
            llm = MockLLMClient()
            await PlannerAgent(llm).run(state)
            await ResearcherAgent(MockSearchClient()).run(state)
            await FactExtractorAgent(llm).run(state)
            await WriterAgent(llm).run(state)
            return state

        state = asyncio.run(run_chain())

        self.assertEqual(state.phase, "writing")
        self.assertTrue(state.final_report.startswith("## 执行摘要"))
        self.assertIn("研究发现", state.final_report)
        self.assertIn("https://example.com/research/", state.final_report)
        self.assertEqual(
            set(state.draft_sections),
            {"sec_1", "sec_2", "sec_3"},
        )
        self.assertTrue(all(section["status"] == "drafted" for section in state.outline))
        for section in state.outline:
            self.assertIn(section["title"], state.final_report)

    def test_writer_requires_outline(self):
        state = ResearchState("测试问题")
        state.facts = [{"content": "事实", "source_url": "https://example.com"}]

        with self.assertRaisesRegex(ValueError, "研究大纲"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))

    def test_writer_requires_facts(self):
        state = ResearchState("测试问题")
        state.outline = [{"title": "章节", "description": "描述"}]

        with self.assertRaisesRegex(ValueError, "事实"):
            asyncio.run(WriterAgent(MockLLMClient()).run(state))

    def test_writer_prefers_facts_from_the_matching_section(self):
        async def run():
            state = ResearchState("测试问题")
            state.outline = [
                {"id": "sec-a", "title": "A 章节", "description": "A 描述"},
                {"id": "sec-b", "title": "B 章节", "description": "B 描述"},
            ]
            state.facts = [
                {
                    "content": "A 事实",
                    "source_title": "A 来源",
                    "source_url": "https://example.com/a",
                    "section_id": "sec-a",
                },
                {
                    "content": "B 事实",
                    "source_title": "B 来源",
                    "source_url": "https://example.com/b",
                    "section_id": "sec-b",
                },
            ]
            return await WriterAgent(MockLLMClient()).run(state)

        state = asyncio.run(run())

        self.assertIn("A 事实", state.draft_sections["sec-a"])
        self.assertNotIn("B 事实", state.draft_sections["sec-a"])
        self.assertIn("B 事实", state.draft_sections["sec-b"])
        self.assertNotIn("A 事实", state.draft_sections["sec-b"])


if __name__ == "__main__":
    unittest.main()
```

### 79db291 文件：docs/v2-core-contract.md

````text
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

当前 `iteration-02` 已经把章节大纲、章节查询、来源和事实的关联字段接入工作流；
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
````

<a id="archive-tests"></a>
## 八、两个正式完成版的测试证据

### 1. 测试口径

以下结果是在从固定 Git 标签导出的独立副本中运行的，不是对当前 iteration-03 工作树的结果：

```powershell
$env:PYTHONPATH='backend'
python -B -m unittest discover -s backend/tests -v
```

- i1 固定提交 `787cd9a4`：39 项全部通过；
- i2 固定提交 `79db291d`：55 项全部通过；
- 时间线里的中间“静态测试数”只是读取每个提交中测试方法的数量，没有逐提交重新执行；这里的 i1/i2 才是实际运行证据。

### 2. i1 完整运行输出

```text
test_base_agent_cannot_be_instantiated_directly (test_base_agent.BaseAgentTests.test_base_agent_cannot_be_instantiated_directly) ... ok
test_concrete_agent_updates_and_returns_state (test_base_agent.BaseAgentTests.test_concrete_agent_updates_and_returns_state) ... ok
test_critic_approves_source_grounded_report (test_critic.CriticAgentTests.test_critic_approves_source_grounded_report) ... ok
test_critic_rejects_invalid_result (test_critic.CriticAgentTests.test_critic_rejects_invalid_result) ... ok
test_critic_requires_report (test_critic.CriticAgentTests.test_critic_requires_report) ... ok
test_fact_extractor_rejects_unknown_source_url (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_rejects_unknown_source_url) ... ok
test_fact_extractor_requires_sources (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_requires_sources) ... ok
test_fact_extractor_turns_sources_into_facts (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_turns_sources_into_facts) ... ok
test_mock_client_implements_llm_interface (test_llm_client.LLMClientTests.test_mock_client_implements_llm_interface) ... ok
test_mock_client_rejects_unknown_role (test_llm_client.LLMClientTests.test_mock_client_rejects_unknown_role) ... ok
test_mock_critic_approves_cited_report (test_llm_client.LLMClientTests.test_mock_critic_approves_cited_report) ... ok
test_mock_fact_extractor_returns_source_grounded_facts (test_llm_client.LLMClientTests.test_mock_fact_extractor_returns_source_grounded_facts) ... ok
test_mock_planner_returns_structured_result (test_llm_client.LLMClientTests.test_mock_planner_returns_structured_result) ... ok
test_mock_writer_returns_text (test_llm_client.LLMClientTests.test_mock_writer_returns_text) ... ok
test_planner_rejects_empty_query (test_planner.PlannerAgentTests.test_planner_rejects_empty_query) ... ok
test_planner_rejects_invalid_llm_result (test_planner.PlannerAgentTests.test_planner_rejects_invalid_llm_result) ... ok
test_planner_writes_plan_into_state (test_planner.PlannerAgentTests.test_planner_writes_plan_into_state) ... ok
test_researcher_collects_sources_after_planning (test_researcher.ResearcherAgentTests.test_researcher_collects_sources_after_planning) ... ok
test_researcher_deduplicates_existing_source_urls (test_researcher.ResearcherAgentTests.test_researcher_deduplicates_existing_source_urls) ... ok
test_researcher_rejects_missing_questions (test_researcher.ResearcherAgentTests.test_researcher_rejects_missing_questions) ... ok
test_print_state_contains_key_sections (test_run_research.RunResearchScriptTests.test_print_state_contains_key_sections) ... ok
test_script_run_returns_completed_state (test_run_research.RunResearchScriptTests.test_script_run_returns_completed_state) ... ok
test_mock_client_implements_search_interface (test_search_client.SearchClientTests.test_mock_client_implements_search_interface) ... ok
test_same_query_has_stable_url (test_search_client.SearchClientTests.test_same_query_has_stable_url) ... ok
test_search_rejects_invalid_input (test_search_client.SearchClientTests.test_search_rejects_invalid_input) ... ok
test_search_returns_normalized_result (test_search_client.SearchClientTests.test_search_returns_normalized_result) ... ok
test_mutable_fields_are_not_shared (test_state.ResearchStateTests.test_mutable_fields_are_not_shared) ... ok
test_state_starts_empty (test_state.ResearchStateTests.test_state_starts_empty) ... ok
test_stream_emits_ordered_events_and_final_result (test_stream_workflow.StreamWorkflowTests.test_stream_emits_ordered_events_and_final_result) ... ok
test_stream_marks_supplementary_research_iteration (test_stream_workflow.StreamWorkflowTests.test_stream_marks_supplementary_research_iteration) ... ok
test_critic_routes_to_supplementary_research_then_passes (test_workflow.ResearchWorkflowTests.test_critic_routes_to_supplementary_research_then_passes) ... ok
test_critic_routes_to_writer_revision_without_new_search (test_workflow.ResearchWorkflowTests.test_critic_routes_to_writer_revision_without_new_search) ... ok
test_workflow_preserves_explicit_session_id (test_workflow.ResearchWorkflowTests.test_workflow_preserves_explicit_session_id) ... ok
test_workflow_rejects_negative_iteration_limit (test_workflow.ResearchWorkflowTests.test_workflow_rejects_negative_iteration_limit) ... ok
test_workflow_runs_full_research_chain (test_workflow.ResearchWorkflowTests.test_workflow_runs_full_research_chain) ... ok
test_workflow_stops_after_max_iterations (test_workflow.ResearchWorkflowTests.test_workflow_stops_after_max_iterations) ... ok
test_writer_generates_cited_report (test_writer.WriterAgentTests.test_writer_generates_cited_report) ... ok
test_writer_requires_facts (test_writer.WriterAgentTests.test_writer_requires_facts) ... ok
test_writer_requires_plan (test_writer.WriterAgentTests.test_writer_requires_plan) ... ok

----------------------------------------------------------------------
Ran 39 tests in 0.026s

OK

```

### 3. i2 完整运行输出

```text
test_base_agent_cannot_be_instantiated_directly (test_base_agent.BaseAgentTests.test_base_agent_cannot_be_instantiated_directly) ... ok
test_concrete_agent_updates_and_returns_state (test_base_agent.BaseAgentTests.test_concrete_agent_updates_and_returns_state) ... ok
test_critic_approves_source_grounded_report (test_critic.CriticAgentTests.test_critic_approves_source_grounded_report) ... ok
test_critic_rejects_invalid_result (test_critic.CriticAgentTests.test_critic_rejects_invalid_result) ... ok
test_critic_requires_report (test_critic.CriticAgentTests.test_critic_requires_report) ... ok
test_critic_feedback_starts_unresolved (test_domain_models.DomainModelTests.test_critic_feedback_starts_unresolved) ... ok
test_data_point_and_chart_keep_analysis_fields (test_domain_models.DomainModelTests.test_data_point_and_chart_keep_analysis_fields) ... ok
test_model_collections_are_not_shared (test_domain_models.DomainModelTests.test_model_collections_are_not_shared) ... ok
test_section_serializes_nested_sections (test_domain_models.DomainModelTests.test_section_serializes_nested_sections) ... ok
test_each_event_type_declares_required_fields (test_events.ResearchEventTests.test_each_event_type_declares_required_fields) ... ok
test_event_data_cannot_replace_common_fields (test_events.ResearchEventTests.test_event_data_cannot_replace_common_fields) ... ok
test_event_rejects_empty_session_id (test_events.ResearchEventTests.test_event_rejects_empty_session_id) ... ok
test_event_rejects_invalid_iteration (test_events.ResearchEventTests.test_event_rejects_invalid_iteration) ... ok
test_event_rejects_missing_business_fields (test_events.ResearchEventTests.test_event_rejects_missing_business_fields) ... ok
test_event_rejects_non_dict_data (test_events.ResearchEventTests.test_event_rejects_non_dict_data) ... ok
test_event_rejects_unknown_phase (test_events.ResearchEventTests.test_event_rejects_unknown_phase) ... ok
test_event_rejects_unknown_type (test_events.ResearchEventTests.test_event_rejects_unknown_type) ... ok
test_event_to_dict_keeps_common_fields_and_data (test_events.ResearchEventTests.test_event_to_dict_keeps_common_fields_and_data) ... ok
test_event_type_constants_are_registered (test_events.ResearchEventTests.test_event_type_constants_are_registered) ... ok
test_fact_extractor_rejects_unknown_source_url (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_rejects_unknown_source_url) ... ok
test_fact_extractor_requires_sources (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_requires_sources) ... ok
test_fact_extractor_turns_raw_sources_into_facts (test_fact_extractor.FactExtractorAgentTests.test_fact_extractor_turns_raw_sources_into_facts) ... ok
test_mock_client_implements_llm_interface (test_llm_client.LLMClientTests.test_mock_client_implements_llm_interface) ... ok
test_mock_client_rejects_unknown_role (test_llm_client.LLMClientTests.test_mock_client_rejects_unknown_role) ... ok
test_mock_critic_approves_cited_report (test_llm_client.LLMClientTests.test_mock_critic_approves_cited_report) ... ok
test_mock_fact_extractor_returns_source_grounded_facts (test_llm_client.LLMClientTests.test_mock_fact_extractor_returns_source_grounded_facts) ... ok
test_mock_planner_returns_structured_result (test_llm_client.LLMClientTests.test_mock_planner_returns_structured_result) ... ok
test_mock_writer_returns_text (test_llm_client.LLMClientTests.test_mock_writer_returns_text) ... ok
test_planner_rejects_empty_query (test_planner.PlannerAgentTests.test_planner_rejects_empty_query) ... ok
test_planner_rejects_invalid_llm_result (test_planner.PlannerAgentTests.test_planner_rejects_invalid_llm_result) ... ok
test_planner_writes_outline_into_state (test_planner.PlannerAgentTests.test_planner_writes_outline_into_state) ... ok
test_researcher_collects_sources_after_planning (test_researcher.ResearcherAgentTests.test_researcher_collects_sources_after_planning) ... ok
test_researcher_deduplicates_existing_source_urls (test_researcher.ResearcherAgentTests.test_researcher_deduplicates_existing_source_urls) ... ok
test_researcher_rejects_missing_questions (test_researcher.ResearcherAgentTests.test_researcher_rejects_missing_questions) ... ok
test_researcher_uses_all_queries_from_a_section (test_researcher.ResearcherAgentTests.test_researcher_uses_all_queries_from_a_section) ... ok
test_print_state_contains_key_sections (test_run_research.RunResearchScriptTests.test_print_state_contains_key_sections) ... ok
test_script_run_returns_completed_state (test_run_research.RunResearchScriptTests.test_script_run_returns_completed_state) ... ok
test_mock_client_implements_search_interface (test_search_client.SearchClientTests.test_mock_client_implements_search_interface) ... ok
test_same_query_has_stable_url (test_search_client.SearchClientTests.test_same_query_has_stable_url) ... ok
test_search_rejects_invalid_input (test_search_client.SearchClientTests.test_search_rejects_invalid_input) ... ok
test_search_returns_normalized_result (test_search_client.SearchClientTests.test_search_returns_normalized_result) ... ok
test_mutable_fields_are_not_shared (test_state.ResearchStateTests.test_mutable_fields_are_not_shared) ... ok
test_state_starts_empty (test_state.ResearchStateTests.test_state_starts_empty) ... ok
test_stream_emits_ordered_events_and_final_result (test_stream_workflow.StreamWorkflowTests.test_stream_emits_ordered_events_and_final_result) ... ok
test_stream_marks_supplementary_research_iteration (test_stream_workflow.StreamWorkflowTests.test_stream_marks_supplementary_research_iteration) ... ok
test_critic_routes_to_supplementary_research_then_passes (test_workflow.ResearchWorkflowTests.test_critic_routes_to_supplementary_research_then_passes) ... ok
test_critic_routes_to_writer_revision_without_new_search (test_workflow.ResearchWorkflowTests.test_critic_routes_to_writer_revision_without_new_search) ... ok
test_workflow_preserves_explicit_session_id (test_workflow.ResearchWorkflowTests.test_workflow_preserves_explicit_session_id) ... ok
test_workflow_rejects_negative_iteration_limit (test_workflow.ResearchWorkflowTests.test_workflow_rejects_negative_iteration_limit) ... ok
test_workflow_runs_full_research_chain (test_workflow.ResearchWorkflowTests.test_workflow_runs_full_research_chain) ... ok
test_workflow_stops_after_max_iterations (test_workflow.ResearchWorkflowTests.test_workflow_stops_after_max_iterations) ... ok
test_writer_generates_cited_report (test_writer.WriterAgentTests.test_writer_generates_cited_report) ... ok
test_writer_prefers_facts_from_the_matching_section (test_writer.WriterAgentTests.test_writer_prefers_facts_from_the_matching_section) ... ok
test_writer_requires_facts (test_writer.WriterAgentTests.test_writer_requires_facts) ... ok
test_writer_requires_outline (test_writer.WriterAgentTests.test_writer_requires_outline) ... ok

----------------------------------------------------------------------
Ran 55 tests in 0.030s

OK

```

<a id="archive-after-i2"></a>
## 九、i2 之后的单独补充

### fccf339：为事实关联假设证据

提交：`fccf33983342fd6e30248746c816b2111368c76d`，时间：2026-10-06 23:08:26（北京时间）。它是 `79db291` 的直接子提交，不属于 iteration-02 正式标签。

修改文件：

- `backend/app/agents/fact_extractor.py`
- `backend/app/core/llm_client.py`
- `backend/tests/test_fact_extractor.py`

功能变化：

- FactExtractor 请求中加入 `hypotheses`；事实可带 `related_hypothesis` 和 `hypothesis_support`，两字段必须同时出现；
- 假设 ID 必须已知，支持方向限定为 `supports`、`refutes`、`neutral`；
- 支持证据达到 2 条时把假设设为 `supported`，反驳证据达到 2 条时设为 `refuted`；neutral 对尚未验证假设设为 `partially_supported`；
- Mock 会把所有事实标为支持第一个假设，这是测试替身的固定行为，不是真实语义判断；
- 正反证据并存时没有综合权衡，结果受处理顺序影响；
- 这次提交增加了 3 个测试，之后静态测试数为 57。

### fccf339 完整 Git patch

```diff
commit fccf33983342fd6e30248746c816b2111368c76d
Author:     JDliu217 <1185310350@qq.com>
AuthorDate: Tue Oct 6 23:08:26 2026 +0800
Commit:     JDliu217 <1185310350@qq.com>
CommitDate: Tue Oct 6 23:08:26 2026 +0800

    feat: track hypothesis evidence in extracted facts
---
 backend/app/agents/fact_extractor.py | 73 +++++++++++++++++++++++++++++++--
 backend/app/core/llm_client.py       | 22 ++++++----
 backend/tests/test_fact_extractor.py | 79 ++++++++++++++++++++++++++++++++++++
 3 files changed, 162 insertions(+), 12 deletions(-)

diff --git a/backend/app/agents/fact_extractor.py b/backend/app/agents/fact_extractor.py
index 55b1912..1b38d65 100644
--- a/backend/app/agents/fact_extractor.py
+++ b/backend/app/agents/fact_extractor.py
@@ -27,16 +27,26 @@ class FactExtractorAgent(BaseAgent):
             payload={
                 "query": state.query,
                 "sources": state.raw_sources,
-                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实。",
+                "hypotheses": state.hypotheses,
+                "instruction": "只提取来源正文中明确表达、且可以由同一 URL 支撑的事实；如果事实与某个研究假设相关，请标记关联假设和支持方向。",
             },
         )
-        facts = self._validate_facts(result.get("facts"), state.raw_sources)
+        facts = self._validate_facts(
+            result.get("facts"),
+            state.raw_sources,
+            state.hypotheses,
+        )
         state.facts = self._deduplicate_facts(state.facts + facts)
+        self._apply_hypothesis_evidence(state.hypotheses, facts)
         state.phase = "researching"
         return state
 
     @staticmethod
-    def _validate_facts(value: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
+    def _validate_facts(
+        value: Any,
+        sources: list[dict[str, Any]],
+        hypotheses: list[dict[str, Any]],
+    ) -> list[dict[str, Any]]:
         if not isinstance(value, list):
             raise ValueError("FactExtractor 返回的 facts 必须是列表")
 
@@ -50,6 +60,11 @@ class FactExtractorAgent(BaseAgent):
             for source in sources
             if source.get("url")
         }
+        hypothesis_ids = {
+            str(hypothesis.get("id", "")).strip()
+            for hypothesis in hypotheses
+            if hypothesis.get("id")
+        }
         validated: list[dict[str, Any]] = []
         for index, item in enumerate(value, start=1):
             if not isinstance(item, dict):
@@ -76,6 +91,24 @@ class FactExtractorAgent(BaseAgent):
                 "source_type": str(item.get("source_type", "web")).strip() or "web",
                 "confidence": confidence,
             }
+            related_hypothesis = str(item.get("related_hypothesis") or "").strip()
+            hypothesis_support = str(item.get("hypothesis_support") or "").strip()
+            if related_hypothesis or hypothesis_support:
+                if not related_hypothesis or not hypothesis_support:
+                    raise ValueError(
+                        f"FactExtractor 的第 {index} 个事实假设关联字段必须同时提供"
+                    )
+                if related_hypothesis not in hypothesis_ids:
+                    raise ValueError(
+                        f"FactExtractor 的第 {index} 个事实引用了未知假设"
+                    )
+                if hypothesis_support not in {"supports", "refutes", "neutral"}:
+                    raise ValueError(
+                        f"FactExtractor 的第 {index} 个事实 hypothesis_support 无效"
+                    )
+                fact["related_hypothesis"] = related_hypothesis
+                fact["hypothesis_support"] = hypothesis_support
+
             source_context = source_by_url[source_url]
             for field_name in ("section_id", "section_title"):
                 if source_context.get(field_name):
@@ -83,6 +116,40 @@ class FactExtractorAgent(BaseAgent):
             validated.append(fact)
         return validated
 
+    @staticmethod
+    def _apply_hypothesis_evidence(
+        hypotheses: list[dict[str, Any]],
+        facts: list[dict[str, Any]],
+    ) -> None:
+        """将事实中的支持方向累积到对应假设。"""
+        hypotheses_by_id = {
+            str(hypothesis.get("id", "")).strip(): hypothesis
+            for hypothesis in hypotheses
+            if hypothesis.get("id")
+        }
+        for fact in facts:
+            hypothesis_id = fact.get("related_hypothesis")
+            if not hypothesis_id or hypothesis_id not in hypotheses_by_id:
+                continue
+
+            hypothesis = hypotheses_by_id[hypothesis_id]
+            support = fact["hypothesis_support"]
+            summary = str(fact.get("content", "")).strip()[:100]
+            if support == "supports":
+                evidence = hypothesis.setdefault("evidence_for", [])
+                if summary not in evidence:
+                    evidence.append(summary)
+                if len(evidence) >= 2:
+                    hypothesis["status"] = "supported"
+            elif support == "refutes":
+                evidence = hypothesis.setdefault("evidence_against", [])
+                if summary not in evidence:
+                    evidence.append(summary)
+                if len(evidence) >= 2:
+                    hypothesis["status"] = "refuted"
+            elif hypothesis.get("status") == "unverified":
+                hypothesis["status"] = "partially_supported"
+
     @staticmethod
     def _deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
         unique: dict[tuple[str, str], dict[str, Any]] = {}
diff --git a/backend/app/core/llm_client.py b/backend/app/core/llm_client.py
index 51807d0..417f372 100644
--- a/backend/app/core/llm_client.py
+++ b/backend/app/core/llm_client.py
@@ -84,20 +84,24 @@ class MockLLMClient(LLMClient):
 
         if role == "fact_extractor":
             facts = []
+            hypotheses = payload.get("hypotheses", [])
+            hypothesis = hypotheses[0] if hypotheses else None
             for source in payload.get("sources", []):
                 content = str(source.get("content") or source.get("snippet") or "").strip()
                 url = str(source.get("url", "")).strip()
                 if not content or not url:
                     continue
-                facts.append(
-                    {
-                        "content": content,
-                        "source_title": str(source.get("title", "")).strip(),
-                        "source_url": url,
-                        "source_type": "web",
-                        "confidence": 0.7,
-                    }
-                )
+                fact = {
+                    "content": content,
+                    "source_title": str(source.get("title", "")).strip(),
+                    "source_url": url,
+                    "source_type": "web",
+                    "confidence": 0.7,
+                }
+                if hypothesis and hypothesis.get("id"):
+                    fact["related_hypothesis"] = str(hypothesis["id"])
+                    fact["hypothesis_support"] = "supports"
+                facts.append(fact)
             return {"facts": facts}
 
         if role == "critic":
diff --git a/backend/tests/test_fact_extractor.py b/backend/tests/test_fact_extractor.py
index 71b6d97..4453d0f 100644
--- a/backend/tests/test_fact_extractor.py
+++ b/backend/tests/test_fact_extractor.py
@@ -25,6 +25,30 @@ class BrokenFactClient(LLMClient):
         return ""
 
 
+class HypothesisFactClient(LLMClient):
+    def __init__(self, support, hypothesis_id="h-1"):
+        self.support = support
+        self.hypothesis_id = hypothesis_id
+
+    async def complete_json(self, role, payload):
+        facts = []
+        for source in payload["sources"]:
+            facts.append(
+                {
+                    "content": f"关于假设的证据：{source['title']}",
+                    "source_title": source["title"],
+                    "source_url": source["url"],
+                    "confidence": 0.9,
+                    "related_hypothesis": self.hypothesis_id,
+                    "hypothesis_support": self.support,
+                }
+            )
+        return {"facts": facts}
+
+    async def complete_text(self, role, payload):
+        return ""
+
+
 class FactExtractorAgentTests(unittest.TestCase):
     def test_fact_extractor_turns_raw_sources_into_facts(self):
         async def run_chain():
@@ -46,6 +70,14 @@ class FactExtractorAgentTests(unittest.TestCase):
             {"sec_1", "sec_2", "sec_3"},
         )
         self.assertTrue(all(fact["section_title"] for fact in state.facts))
+        self.assertTrue(
+            all(fact["related_hypothesis"] == "h_1" for fact in state.facts)
+        )
+        self.assertTrue(
+            all(fact["hypothesis_support"] == "supports" for fact in state.facts)
+        )
+        self.assertEqual(state.hypotheses[0]["status"], "supported")
+        self.assertEqual(len(state.hypotheses[0]["evidence_for"]), 3)
 
     def test_fact_extractor_rejects_unknown_source_url(self):
         state = ResearchState("测试问题")
@@ -64,6 +96,53 @@ class FactExtractorAgentTests(unittest.TestCase):
         with self.assertRaisesRegex(ValueError, "来源"):
             asyncio.run(FactExtractorAgent(MockLLMClient()).run(ResearchState("测试问题")))
 
+    def test_fact_extractor_marks_hypothesis_as_refuted(self):
+        async def run():
+            state = ResearchState("测试问题")
+            state.raw_sources = [
+                {"title": "来源一", "url": "https://example.com/1", "snippet": "证据一"},
+                {"title": "来源二", "url": "https://example.com/2", "snippet": "证据二"},
+            ]
+            state.hypotheses = [
+                {
+                    "id": "h-1",
+                    "content": "待验证假设",
+                    "status": "unverified",
+                    "evidence_for": [],
+                    "evidence_against": [],
+                }
+            ]
+            return await FactExtractorAgent(
+                HypothesisFactClient("refutes")
+            ).run(state)
+
+        state = asyncio.run(run())
+
+        self.assertEqual(state.hypotheses[0]["status"], "refuted")
+        self.assertEqual(len(state.hypotheses[0]["evidence_against"]), 2)
+
+    def test_fact_extractor_rejects_unknown_hypothesis(self):
+        state = ResearchState("测试问题")
+        state.raw_sources = [
+            {"title": "来源", "url": "https://example.com/1", "snippet": "证据"}
+        ]
+        state.hypotheses = [
+            {
+                "id": "h-1",
+                "content": "待验证假设",
+                "status": "unverified",
+                "evidence_for": [],
+                "evidence_against": [],
+            }
+        ]
+
+        with self.assertRaisesRegex(ValueError, "未知假设"):
+            asyncio.run(
+                FactExtractorAgent(
+                    HypothesisFactClient("supports", hypothesis_id="missing")
+                ).run(state)
+            )
+
 
 if __name__ == "__main__":
     unittest.main()

```

<a id="archive-integrity"></a>
## 十、完整性检查与归档说明

本文件生成后核对了以下项目：

- 历史聊天：29 个 turn、28 条用户消息、27 条最终回答、36 段助手过程说明；每条可见原文均有记录编号和原始记录 ID；
- Git 修改：26 个历史节点，逐节点保存提交元数据、文件列表、统计和完整 patch；
- 版本快照：i1 的 33 个、i2 的 37 个跟踪文本文件，共 70 份；
- 测试：固定 i1 运行 39/39，固定 i2 运行 55/55；
- 后续提交：`fccf339` 单独保存，未混入 i2；
- 工作区项目本身没有被 checkout、修改或提交；归档文件只写入本输出目录。

如果以后项目继续更新，请先重新读取项目，再把新提交作为新章节追加；不要修改本文件中标为“原文”的历史回答。
