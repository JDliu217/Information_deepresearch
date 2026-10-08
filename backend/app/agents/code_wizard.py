"""CodeWizard 的代码分析阶段。"""

from __future__ import annotations

import json
from typing import Any

from app.core.llm_client import LLMClient
from app.domain.state import ResearchState
from app.execution.restricted_executor import RestrictedCodeExecutor

from .base import BaseAgent


class CodeWizardAgent(BaseAgent):
    """分析已有数据点，并把代码执行记录保存在研究状态中。

    当前的受限解释器有意不提供 pandas、matplotlib 或文件输出能力。图表
    仍由 DataAnalyst 生成 ECharts 配置；CodeWizard 的图片绘制工作会被
    记录为跳过，直到后续沙箱支持绘图库和图片产物。
    """

    name = "code_wizard"

    REFERENCE_ANALYSIS_SYSTEM = "你是专业的数据分析师，擅长Python数据处理和可视化。"
    ANALYSIS_SYSTEM = """你是研究数据分析助手。只分析输入中已有的数据，不得补造或外推数据。
代码由受限统计解释器执行，只能使用普通赋值、容器、下标、数字运算和明确列出的统计函数。
不得 import、访问属性、使用循环、访问文件或网络、调用进程或执行动态代码。返回严格 JSON。"""

    ANALYSIS_PROMPT = r"""你是一位资深的数据分析师，擅长用Python进行数据处理和可视化。

## 研究问题
{query}

## 可用数据
{data_points}

## 任务
根据上述数据，生成Python代码完成以下任务：
1. 数据清洗和标准化
2. 计算关键统计指标
3. 生成专业的可视化图表

## 代码要求（必须严格遵守）

### 0. 禁止使用反斜杠续行（最重要！）
**严禁使用反斜杠 `\` 进行代码续行**。Python 的字典、列表、函数参数天然支持跨行书写，不需要反斜杠。

✅ 正确示例：
```python
data = {{
    "Year": [2020, 2021, 2022],
    "Value": [100, 200, 300]
}}
df = pd.DataFrame(data)
```

❌ 错误示例（绝对禁止）：
```python
data = {{ \
    "Year": ...
}}
```

### 1. 数据精简
- **只选取最关键的5-10个数据点**，不要把所有数据都写入代码
- **相同指标去重**：如果同一指标有多个时期或类别，只保留有代表性的几个
- **代码总长度不超过40行**
- **禁止生成重复数据**：如 [2020, 2020, 2020...] 这种重复是错误的

### 2. 数据定义方式
必须使用"列字典"格式定义数据：
```python
data = {{
    "Year": [2018, 2020, 2022, 2024],
    "Value": [100, 200, 300, 400]
}}
df = pd.DataFrame(data)
```

示例中的名称和数值仅用于说明数据格式；实际代码只能使用提供的数据点。
**禁止**使用复杂的嵌套列表 `[[...], [...]]`。

### 3. 数据清洗
创建 DataFrame 后，**必须**执行类型转换：
```python
for col in df.columns:
    if col != 'Year':
        df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()
```

### 4. 环境限制
- **禁止import语句**，已预定义: pd, np, plt, sns
- **禁止plt.rcParams**，中文字体已预设

### 5. 高级图表样式（必须遵守）
生成清晰、专业且符合当前研究主题的图表，要求：
- **图表尺寸**: `plt.figure(figsize=(12, 7), dpi=200)`
- **seaborn主题**: `sns.set_theme(style='whitegrid', palette='husl')`
- **标题**: `plt.title('标题', fontsize=18, fontweight='bold', pad=20)`
- **轴标签**: `fontsize=14`
- **刻度**: `fontsize=12`
- **配色**: 使用专业配色如 `#6366f1`（靛蓝）、`#06b6d4`（青色）、`#10b981`（翡翠绿）
- **网格线**: `plt.grid(True, linestyle='--', alpha=0.3)`
- **去除边框**: `sns.despine()`
- **折线图**: `linewidth=2.5, marker='o', markersize=8`，可加面积填充 `plt.fill_between()`
- **柱状图**: 添加数值标签
- **保存**: `plt.savefig('chart.png', dpi=200, bbox_inches='tight', facecolor='white')`

## 输出格式（严格JSON，code字段用\n表示换行）
```json
{{
    "analysis_plan": "简要分析计划",
    "code": "sns.set_theme(style='whitegrid')\ndata = {{'Year': [2020, 2022, 2024], 'Value': [100, 150, 200]}}\ndf = pd.DataFrame(data)\ndf['Value'] = pd.to_numeric(df['Value'], errors='coerce')\nplt.figure(figsize=(12, 7), dpi=200)\nplt.plot(df['Year'], df['Value'], linewidth=2.5, marker='o', markersize=8, color='#6366f1')\nplt.fill_between(df['Year'], df['Value'], alpha=0.15, color='#6366f1')\nplt.title('指标变化趋势', fontsize=18, fontweight='bold')\nplt.xlabel('年份', fontsize=14)\nplt.ylabel('指标值', fontsize=14)\nplt.xticks(fontsize=12)\nplt.yticks(fontsize=12)\nsns.despine()\nplt.savefig('chart.png', dpi=200, bbox_inches='tight', facecolor='white')",
    "expected_outputs": ["图表描述"]
}}
```

注意：code 字段中的换行请使用 `\n` 字符表示，不要使用物理换行符，也**绝对不要使用续行符 `\`**。"""

    # ANALYSIS_PROMPT below remains the reference prompt. This smaller prompt
    # keeps real LLM output executable while the default interpreter is the
    # restricted AST implementation.
    RESTRICTED_ANALYSIS_PROMPT = r"""只使用下面提供的数据点进行统计，不得补造、外推或查询新数据。

## 研究问题
{query}

## 可用数据点
{data_points}

## 解释器支持的语法
- 只允许普通变量赋值、字典/列表/元组、下标读取、数字四则运算和函数调用。
- 只允许调用 len、max、min、round、sum、numeric_values。
- 禁止 import、属性访问、循环、条件语句、文件、网络和绘图库。
- data_points 是字典列表；numeric_values(data_points) 提取其中可解析的数值，忽略布尔值、空值和非数值。
- 必须把分析结论放进字典变量 result，并用 print(result) 输出。
- 无数值时，总和为 0、平均值为 0；必须如实报告可用数值数量。

## 输出格式
返回严格 JSON，包含 analysis_plan、code、expected_outputs。code 不要使用 Markdown 围栏。
code 的逻辑应等价于：
numeric_list = numeric_values(data_points)
numeric_count = len(numeric_list)
numeric_total = sum(numeric_list)
numeric_average = round(numeric_total / max(numeric_count, 1), 2)
result = {{"data_point_count": len(data_points), "numeric_value_count": numeric_count, "numeric_total": numeric_total, "numeric_average": numeric_average}}
print(result)"""

    CODE_FIX_PROMPT = r"""你是一位Python专家，需要修复执行失败的代码。

## 错误类型诊断

请根据错误信息判断错误类型并采取对应修复方法：

1. **如果错误是 `could not convert string to float`**：
   说明你试图将包含中文或特殊字符的列作为数值列处理。
   **修复方法**：在绘图或计算前，使用 `pd.to_numeric(df['col'], errors='coerce')` 清洗该列，并删除 NaN 值。
   不要试图直接画包含中文内容的列（除非是作为标签）。

2. **如果错误是 `SyntaxError`**：
   检查是否有多余的反斜杠或未闭合的括号。

3. **如果错误是 `KeyError`**：
   检查 DataFrame 列名是否正确，确保使用的列名与数据定义一致。

4. **如果错误是类型相关 (`TypeError`)**：
   检查数据类型是否匹配，必要时使用 `.astype()` 或 `pd.to_numeric()` 转换。

## 原始代码
{code}

## 错误信息
{error}

## 输出
{stdout}

## 要求
1. **不要写import语句**，已预导入: pd, np, plt, sns
2. 中文字体已预设
3. 使用"列字典"格式定义数据: `data = {{"col1": [...], "col2": [...]}}`
4. 创建 DataFrame 后立即转换数值列

## 输出格式
```json
{{
    "error_analysis": "错误原因分析",
    "fix_description": "具体修复说明",
    "fixed_code": "data = {{'Year': [2020, 2021], 'Value': [100, 200]}}\ndf = pd.DataFrame(data)\ndf['Value'] = pd.to_numeric(df['Value'], errors='coerce')\nprint('done')"
}}
```"""

    RESTRICTED_CODE_FIX_PROMPT = r"""修复受限统计解释器执行失败的代码。只能使用普通变量赋值、字典/列表、下标、数字四则运算，以及 len、max、min、round、sum、numeric_values。禁止 import、属性访问、循环、条件语句、文件、网络或绘图调用。

## 原始代码
{code}

## 错误
{error}

## 输出
{stdout}

请返回严格 JSON，包含 error_analysis、fix_description、fixed_code。fixed_code 必须把结果存入 result 字典并调用 print(result)。"""

    CHART_SYSTEM = """你是研究数据可视化助手，只能使用输入中提供的数据。
当前运行环境不会执行或渲染 matplotlib 等绘图代码。请按要求生成图表代码并返回 JSON，
代码只会保存供后续受限沙箱评估，不要在输出中声称图表已经生成。"""

    CHART_PROMPT = r"""你是专业的数据可视化专家，擅长制作高端商业图表。

## 主题: {topic}
## 图表类型: {chart_type}
## 标题: {title}

## 数据
{data}

## 代码要求（重要）

### 基础要求
1. **严禁使用反斜杠 `\` 进行代码续行**
2. **不要写import语句**，已预导入: pd, np, plt, sns
3. 数据定义使用标准字典格式: `data = {{"col1": [...], "col2": [...]}}`

### 高级样式要求（必须遵守）
1. **图表尺寸**: `plt.figure(figsize=(12, 7), dpi=200)`
2. **使用 seaborn 主题**: `sns.set_theme(style='whitegrid', palette='husl')`
3. **标题字体**: `plt.title('标题', fontsize=18, fontweight='bold', pad=20)`
4. **坐标轴标签**: `plt.xlabel('X轴', fontsize=14)` 和 `plt.ylabel('Y轴', fontsize=14)`
5. **刻度字体**: `plt.xticks(fontsize=12)` 和 `plt.yticks(fontsize=12)`
6. **添加数据标签**: 在柱状图或折线图的数据点上显示数值
7. **配色方案**: 使用渐变色或专业配色，如 `color='#6366f1'` 或 `palette='Blues_d'`
8. **网格线**: 使用浅色虚线网格 `plt.grid(True, linestyle='--', alpha=0.3)`
9. **边框优化**: `sns.despine()` 去除上右边框
10. **保存**: `plt.savefig('chart.png', dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')`

### 折线图额外要求
- 线宽 2.5: `linewidth=2.5`
- 添加数据点标记: `marker='o', markersize=8`
- 添加面积填充: `plt.fill_between(x, y, alpha=0.15)`

### 柱状图额外要求
- 圆角效果（如支持）
- 添加数值标签: `for i, v in enumerate(values): plt.text(i, v + offset, str(v), ha='center', fontsize=11)`

## 输出格式（严格JSON）
```json
{{
    "code": "sns.set_theme(style='whitegrid')\ndata = {{'Year': [2020, 2022], 'Value': [100, 200]}}\ndf = pd.DataFrame(data)\nplt.figure(figsize=(12,7), dpi=200)\nplt.bar(df['Year'], df['Value'], color='#6366f1')\nplt.title('标题', fontsize=18, fontweight='bold')\nplt.xlabel('年份', fontsize=14)\nplt.ylabel('数值', fontsize=14)\nplt.xticks(fontsize=12)\nplt.yticks(fontsize=12)\nsns.despine()\nplt.savefig('chart.png', dpi=200, bbox_inches='tight', facecolor='white')",
    "chart_description": "图表说明"
}}
```

注意：code字段用 `\n` 表示换行，**绝对不要使用续行符 `\`**。"""

    max_repair_attempts = 3
    max_chart_sections = 2
    max_repair_stdout_chars = 1000

    def __init__(
        self,
        llm: LLMClient,
        executor: RestrictedCodeExecutor | None = None,
    ):
        self.llm = llm
        self.executor = executor or RestrictedCodeExecutor()

    async def run(self, state: ResearchState) -> ResearchState:
        # Match the reference CodeWizard gate. Checking it unconditionally is
        # important here because the preceding LangGraph node may already have
        # set phase="analyzing" before CodeWizard runs.
        if len(state.data_points) < 3:
            return state

        use_reference_python = bool(
            getattr(self.executor, "supports_reference_python", False)
        )
        analysis_system = (
            self.REFERENCE_ANALYSIS_SYSTEM
            if use_reference_python
            else self.ANALYSIS_SYSTEM
        )
        analysis_prompt = (
            self.ANALYSIS_PROMPT
            if use_reference_python
            else self.RESTRICTED_ANALYSIS_PROMPT
        )
        data_summary = self._format_data_points(state.data_points)
        payload = {
            "query": state.query,
            "data_summary": data_summary,
            "instruction": (
                "数据点按名称、数值、单位和年份整理；只能使用这些数据进行简单统计分析。"
            ),
        }
        response = await self._complete_json(
            payload,
            system_prompt=analysis_system,
            user_prompt=analysis_prompt.format(
                query=state.query,
                data_points=data_summary,
            ),
            temperature=0.3,
            max_tokens=16000,
        )
        plan = self._validate_plan(response)

        # chart_ids is accepted only as a compatibility field for older
        # clients. The reference analysis contract does not ask the model for
        # chart IDs, and repeated IDs should not fail an entire research run.
        known_chart_ids = {
            str(chart.get("id", "")).strip()
            for chart in state.charts
            if isinstance(chart, dict) and str(chart.get("id", "")).strip()
        }
        plan["chart_ids"] = [
            chart_id for chart_id in plan["chart_ids"] if chart_id in known_chart_ids
        ]

        for attempt in range(self.max_repair_attempts + 1):
            execution = self.executor.execute(
                plan["code"],
                {
                    "data_points": state.data_points,
                    "facts": state.facts,
                    "insights": state.insights,
                    "charts": state.charts,
                },
                execution_id=f"exec_{len(state.code_executions) + 1}",
            )
            execution.result = {
                "analysis_plan": plan["analysis_plan"],
                "expected_outputs": plan["expected_outputs"],
                "output": execution.result,
            }
            execution.chart_ids = plan["chart_ids"]
            state.code_executions.append(execution.to_dict())

            if execution.status == "succeeded":
                for chart in state.charts:
                    if (
                        isinstance(chart, dict)
                        and str(chart.get("id", "")).strip() in execution.chart_ids
                    ):
                        chart["code"] = execution.code
                        chart["execution_id"] = execution.id

            # A safety rejection is terminal: never ask a model to rewrite
            # code that attempted to leave the restricted execution surface.
            if execution.status != "failed" or attempt >= self.max_repair_attempts:
                break

            repair_payload = {
                "mode": "repair",
                "query": state.query,
                "data_summary": data_summary,
                "analysis_plan": plan["analysis_plan"],
                "code": plan["code"],
                "error": str(execution.error).strip()[:2000],
                "stdout": str(execution.stdout).strip()[: self.max_repair_stdout_chars],
            }
            try:
                repair_result = await self._complete_json(
                    repair_payload,
                    system_prompt=analysis_system,
                    user_prompt=(
                        self.CODE_FIX_PROMPT
                        if use_reference_python
                        else self.RESTRICTED_CODE_FIX_PROMPT
                    ).format(
                        code=repair_payload["code"],
                        error=repair_payload["error"],
                        stdout=repair_payload["stdout"],
                    ),
                    temperature=0.2,
                    max_tokens=16000,
                )
                fixed = self._validate_fix(repair_result)
            except Exception as exc:
                state.logs.append(
                    {
                        "agent": self.name,
                        "event": "code_repair_skipped",
                        "reason": str(exc),
                    }
                )
                break
            plan["code"] = fixed["fixed_code"]
            if fixed["error_analysis"] or fixed["fix_description"]:
                state.logs.append(
                    {
                        "agent": self.name,
                        "event": "code_repaired",
                        "error_analysis": fixed["error_analysis"],
                        "fix_description": fixed["fix_description"],
                        "attempt": attempt + 1,
                    }
                )

        state.phase = "analyzing"
        await self._generate_charts(state)
        return state

    @staticmethod
    def _format_data_points(data_points: list[dict[str, Any]]) -> str:
        """Format data as readable metric/value/unit/year lines."""

        lines: list[str] = []
        for point in data_points:
            if not isinstance(point, dict):
                continue
            name = str(point.get("name", "未知指标"))
            value = point.get("value", "未知")
            unit = str(point.get("unit", "") or "")
            year = point.get("year", "N/A")
            suffix = f" {unit}" if unit else ""
            lines.append(f"- {name}: {value}{suffix} ({year})")
        return "\n".join(lines)

    @staticmethod
    def _validate_plan(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("CodeWizard 返回结果必须是对象")

        raw_code = value.get("code", "")
        if isinstance(raw_code, list):
            raw_code = "\n".join(str(line) for line in raw_code)
        code = str(raw_code).strip()
        if not code:
            raise ValueError("CodeWizard 返回结果缺少 code")

        # analysis_plan is the reference field; purpose remains accepted for
        # compatibility with earlier local fixtures.
        analysis_plan = str(
            value.get("analysis_plan", value.get("purpose", ""))
        ).strip()
        if not analysis_plan:
            raise ValueError("CodeWizard 返回结果缺少 analysis_plan")

        # The reference CodeWizard does not consume expected_outputs when it
        # executes a plan.  Compatible models sometimes return a single
        # string, an object, or omit this optional metadata entirely.  Keep
        # the execution contract strict for code and analysis_plan, while
        # normalizing this non-functional field instead of failing a run.
        raw_expected_outputs = value.get("expected_outputs", [])
        if isinstance(raw_expected_outputs, str):
            expected_outputs = [raw_expected_outputs]
        elif isinstance(raw_expected_outputs, list):
            expected_outputs = [
                item for item in raw_expected_outputs if isinstance(item, str)
            ]
        elif isinstance(raw_expected_outputs, dict):
            expected_outputs = [
                str(raw_expected_outputs[key]).strip()
                for key in ("name", "description", "output")
                if isinstance(raw_expected_outputs.get(key), str)
                and raw_expected_outputs[key].strip()
            ]
        else:
            expected_outputs = []

        chart_ids = value.get("chart_ids", [])
        if not isinstance(chart_ids, list):
            chart_ids = []
        # Preserve order while dropping malformed and duplicate legacy values.
        normalized_chart_ids = list(
            dict.fromkeys(
                item.strip()
                for item in chart_ids
                if isinstance(item, str) and item.strip()
            )
        )
        return {
            "analysis_plan": analysis_plan,
            "code": code,
            "expected_outputs": [item.strip() for item in expected_outputs if item.strip()],
            "chart_ids": normalized_chart_ids,
        }

    @staticmethod
    def _validate_fix(value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            raise ValueError("CodeWizard 修复结果必须是对象")
        raw_code = value.get("fixed_code", "")
        if isinstance(raw_code, list):
            raw_code = "\n".join(str(line) for line in raw_code)
        fixed_code = str(raw_code).strip()
        if not fixed_code:
            raise ValueError("CodeWizard 修复结果缺少 fixed_code")
        return {
            "fixed_code": fixed_code,
            "error_analysis": str(value.get("error_analysis", "")).strip(),
            "fix_description": str(value.get("fix_description", "")).strip(),
        }

    @classmethod
    def _select_chart_sections(
        cls, outline: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        marked = [
            section
            for section in outline
            if isinstance(section, dict) and section.get("requires_chart")
        ]
        candidates = marked if marked else [
            section for section in outline if isinstance(section, dict)
        ][: cls.max_chart_sections]
        return candidates[: cls.max_chart_sections]

    @staticmethod
    def _section_data(
        state: ResearchState, section_id: str
    ) -> list[dict[str, Any]]:
        related: list[dict[str, Any]] = []
        for fact in state.facts:
            if not isinstance(fact, dict):
                continue
            related_sections = fact.get("related_sections", [])
            if not isinstance(related_sections, list):
                related_sections = [related_sections] if related_sections else []
            if section_id not in related_sections:
                continue
            data_points = fact.get("data_points", [])
            if isinstance(data_points, list):
                related.extend(point for point in data_points if isinstance(point, dict))

        # Preserve the reference flow: section-linked fact data comes first,
        # followed by the first ten globally extracted data points.
        related.extend(
            point for point in state.data_points[:10] if isinstance(point, dict)
        )
        return related

    async def _generate_charts(self, state: ResearchState) -> None:
        """Generate chart code for reference section scopes without executing it."""
        sections = self._select_chart_sections(state.outline)
        for section in sections:
            section_id = str(section.get("id", "")).strip()
            data = self._section_data(state, section_id)
            if not data:
                continue

            title = str(section.get("title", "研究章节"))
            chart_type = (
                "bar" if section.get("section_type") == "quantitative" else "line"
            )
            payload = {
                "mode": "chart_generation",
                "query": title,
                "section_id": section_id,
                "chart_type": chart_type,
                "title": f"{title}分析",
                "data": data,
            }
            try:
                result = await self._complete_json(
                    payload,
                    system_prompt=self.CHART_SYSTEM,
                    user_prompt=self.CHART_PROMPT.format(
                        topic=title,
                        chart_type=chart_type,
                        title=payload["title"],
                        data=json.dumps(data, ensure_ascii=False, indent=2),
                    ),
                    temperature=0.3,
                    max_tokens=16000,
                )
                code = self._validate_chart_code(result)
            except Exception as exc:
                state.logs.append(
                    {
                        "agent": self.name,
                        "event": "chart_generation_skipped",
                        "section_id": section_id,
                        "section_title": title,
                        "data_point_count": len(data),
                        "reason": f"图表代码生成失败：{exc}",
                    }
                )
                continue

            limitation = (
                "当前 RestrictedCodeExecutor 不支持 pandas/matplotlib、图片文件输出或图片产物；"
                "绘图代码仅记录，未执行。DataAnalyst 的 ECharts 配置仍可用。"
            )
            state.logs.append(
                {
                    "agent": self.name,
                    "event": "chart_generation_skipped",
                    "section_id": section_id,
                    "section_title": title,
                    "data_point_count": len(data),
                    "code": code,
                    "chart_description": str(result.get("chart_description", "")).strip(),
                    "reason": limitation,
                }
            )

    @staticmethod
    def _validate_chart_code(value: Any) -> str:
        if not isinstance(value, dict):
            raise ValueError("CodeWizard 图表结果必须是对象")
        raw_code = value.get("code", "")
        if isinstance(raw_code, list):
            raw_code = "\n".join(str(line) for line in raw_code)
        code = str(raw_code).strip()
        if not code:
            raise ValueError("CodeWizard 图表结果缺少 code")
        return code
