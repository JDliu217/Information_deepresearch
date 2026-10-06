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
