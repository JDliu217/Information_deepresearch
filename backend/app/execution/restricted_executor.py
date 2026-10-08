"""CodeWizard 的小型统计表达式解释器。

仅支持受限的赋值、数据读取和统计函数。复杂 Python 分析留给后续
Docker 执行器；这里没有运行动态 Python 字节码。
"""

from __future__ import annotations

import ast
import json
import math
import time
from copy import deepcopy
from typing import Any

from app.domain.models import CodeExecution


class _RejectedCode(ValueError):
    pass


class RestrictedCodeExecutor:
    """解释有界统计表达式，返回统一的 CodeExecution 记录。"""

    supports_reference_python = False
    allowed_context_names = {"charts", "data_points", "facts", "insights"}
    max_code_chars = 4_000
    max_context_chars = 100_000
    max_nodes = 120
    max_output_chars = 4_000
    max_result_chars = 100_000

    def execute(
        self,
        code: str,
        context: dict[str, Any],
        execution_id: str = "exec_1",
    ) -> CodeExecution:
        started_at = time.perf_counter()
        try:
            if not isinstance(code, str) or not code.strip() or len(code) > self.max_code_chars:
                raise _RejectedCode("代码不能为空，且不能超过长度限制")
            if not isinstance(context, dict):
                raise _RejectedCode("执行上下文必须是对象")
            unknown_names = set(context) - self.allowed_context_names
            if unknown_names:
                names = ", ".join(sorted(unknown_names))
                raise _RejectedCode(f"执行上下文包含不允许的字段: {names}")
            try:
                encoded = json.dumps(context, ensure_ascii=False, allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise _RejectedCode("执行上下文必须包含可序列化的有限数据") from exc
            if len(encoded) > self.max_context_chars:
                raise _RejectedCode("执行上下文超过长度限制")
            try:
                tree = ast.parse(code, mode="exec")
            except SyntaxError as exc:
                raise _RejectedCode(f"代码语法错误: {exc.msg}") from exc
            if sum(1 for _ in ast.walk(tree)) > self.max_nodes:
                raise _RejectedCode("代码超过复杂度限制")
            namespace = {
                name: deepcopy(context.get(name, []))
                for name in self.allowed_context_names
            }
            stdout: list[str] = []
            for statement in tree.body:
                self._execute_statement(statement, namespace, stdout)
            result = namespace.get("result", {})
            if result is None:
                result = {}
            if not isinstance(result, dict):
                raise ValueError("代码变量 result 必须是对象")
            encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
            if len(encoded_result) > self.max_result_chars:
                raise _RejectedCode("分析结果超过长度限制")
            return self._record(
                execution_id, code, "succeeded", started_at,
                stdout="\n".join(stdout) + ("\n" if stdout else ""),
                result=result,
            )
        except _RejectedCode as exc:
            return self._record(
                execution_id, code, "rejected", started_at, error=str(exc)
            )
        except (ArithmeticError, KeyError, IndexError, TypeError, ValueError) as exc:
            return self._record(
                execution_id, code, "failed", started_at, error=str(exc)
            )

    def _execute_statement(
        self,
        node: ast.stmt,
        namespace: dict[str, Any],
        stdout: list[str],
    ) -> None:
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                raise _RejectedCode("代码只允许对普通变量赋值")
            name = node.targets[0].id
            if name.startswith("__") or name in self.allowed_context_names:
                raise _RejectedCode("代码不能覆盖输入数据或系统名称")
            namespace[name] = self._evaluate(node.value, namespace, stdout)
        elif isinstance(node, ast.Expr):
            self._evaluate(node.value, namespace, stdout)
        else:
            raise _RejectedCode("代码只允许赋值和统计表达式")

    def _evaluate(
        self,
        node: ast.expr,
        namespace: dict[str, Any],
        stdout: list[str],
    ) -> Any:
        if isinstance(node, ast.Constant):
            value = node.value
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise _RejectedCode("代码包含不支持的常量")
            if isinstance(value, int) and abs(value) > 1_000_000_000:
                raise _RejectedCode("整数超过范围")
            return value
        if isinstance(node, ast.Name):
            if node.id not in namespace:
                raise _RejectedCode(f"未知变量: {node.id}")
            return namespace[node.id]
        if isinstance(node, (ast.List, ast.Tuple)):
            return [self._evaluate(item, namespace, stdout) for item in node.elts]
        if isinstance(node, ast.Dict):
            if any(key is None for key in node.keys):
                raise _RejectedCode("代码不能展开字典")
            keys = [self._evaluate(key, namespace, stdout) for key in node.keys]
            values = [self._evaluate(value, namespace, stdout) for value in node.values]
            return dict(zip(keys, values))
        if isinstance(node, ast.Subscript):
            target = self._evaluate(node.value, namespace, stdout)
            index = self._evaluate(node.slice, namespace, stdout)
            if isinstance(target, (list, dict, str)) and isinstance(index, (int, str)):
                return target[index]
            raise _RejectedCode("代码只能读取列表、字典或字符串元素")
        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left, namespace, stdout)
            right = self._evaluate(node.right, namespace, stdout)
            if type(left) not in (int, float) or type(right) not in (int, float):
                raise _RejectedCode("算术运算只允许数字")
            if abs(left) > 1_000_000_000 or abs(right) > 1_000_000_000:
                raise _RejectedCode("数字超过范围")
            if isinstance(node.op, ast.Add):
                value = left + right
            elif isinstance(node.op, ast.Sub):
                value = left - right
            elif isinstance(node.op, ast.Mult):
                value = left * right
            elif isinstance(node.op, ast.Div):
                value = left / right
            else:
                raise _RejectedCode("不支持的算术运算")
            if abs(value) > 1_000_000_000:
                raise _RejectedCode("计算结果超过范围")
            return value
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise _RejectedCode("代码只能调用允许的统计函数")
            name = node.func.id
            args = [self._evaluate(arg, namespace, stdout) for arg in node.args]
            if name == "print" and len(args) == 1:
                output = str(args[0])
                if sum(map(len, stdout)) + len(output) > self.max_output_chars:
                    raise _RejectedCode("标准输出超过长度限制")
                stdout.append(output)
                return None
            functions = {
                "len": len,
                "max": max,
                "min": min,
                "round": round,
                "sum": sum,
                "numeric_values": self._numeric_values,
            }
            if name not in functions:
                raise _RejectedCode("代码只能调用允许的统计函数")
            return functions[name](*args)
        raise _RejectedCode("代码包含不支持的语法")

    @staticmethod
    def _numeric_values(data_points: Any) -> list[int | float]:
        """Return bounded numeric values from the input metric records."""

        if not isinstance(data_points, list):
            raise _RejectedCode("numeric_values 只接受数据点列表")
        values: list[int | float] = []
        for point in data_points[:1_000]:
            if not isinstance(point, dict):
                continue
            value = point.get("value")
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                numeric = value
            elif isinstance(value, str):
                try:
                    numeric = float(value.replace(",", "").strip())
                except ValueError:
                    continue
            else:
                continue
            if math.isfinite(numeric) and abs(numeric) <= 1_000_000_000:
                values.append(numeric)
        return values

    @staticmethod
    def _record(
        execution_id: str,
        code: str,
        status: str,
        started_at: float,
        *,
        stdout: str = "",
        error: str = "",
        result: dict[str, Any] | None = None,
    ) -> CodeExecution:
        return CodeExecution(
            id=execution_id,
            code=code,
            status=status,
            stdout=stdout,
            error=error,
            duration_ms=int((time.perf_counter() - started_at) * 1000),
            result=result or {},
        )
