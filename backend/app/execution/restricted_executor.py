"""用于学习版 CodeWizard 的受限代码执行器。

该执行器只提供最小的本地保护和可测试行为，不能替代进程或容器隔离。
生产环境需要在 Docker 等独立沙箱中执行不可信代码。
"""

from __future__ import annotations

import ast
import io
import time
from contextlib import redirect_stdout
from copy import deepcopy
from typing import Any

from app.domain.models import CodeExecution


class _CodePolicy(ast.NodeVisitor):
    """拒绝导入、属性访问和动态执行，只允许简单统计表达式。"""

    allowed_calls = {"len", "max", "min", "print", "round", "sorted", "sum"}
    allowed_binops = (ast.Add, ast.Div, ast.FloorDiv, ast.Mult, ast.Pow, ast.Sub)
    allowed_unaryops = (ast.UAdd, ast.USub, ast.Not)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id.startswith("__"):
            raise ValueError("代码不能使用双下划线名称")

    def visit_Call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Name) or node.func.id not in self.allowed_calls:
            raise ValueError("代码只能调用允许的统计函数")
        if node.keywords and any(keyword.arg is None for keyword in node.keywords):
            raise ValueError("代码不能使用动态参数展开")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        raise ValueError("代码不能访问对象属性")

    def visit_Import(self, node: ast.Import) -> None:
        raise ValueError("代码不能导入模块")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        raise ValueError("代码不能导入模块")

    def visit_Lambda(self, node: ast.Lambda) -> None:
        raise ValueError("代码不能定义 Lambda")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        raise ValueError("代码不能定义函数")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        raise ValueError("代码不能定义类")

    def visit_While(self, node: ast.While) -> None:
        raise ValueError("代码不能使用 while 循环")

    def visit_For(self, node: ast.For) -> None:
        raise ValueError("代码不能使用 for 循环")

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, self.allowed_binops):
            raise ValueError("代码使用了不允许的运算")
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, self.allowed_unaryops):
            raise ValueError("代码使用了不允许的一元运算")
        self.generic_visit(node)


class RestrictedCodeExecutor:
    """在有限的命名空间中执行统计代码并返回统一记录。"""

    allowed_builtins = {
        "len": len,
        "max": max,
        "min": min,
        "print": print,
        "round": round,
        "sorted": sorted,
        "sum": sum,
    }
    allowed_context_names = {"charts", "data_points", "facts", "insights"}

    def execute(
        self,
        code: str,
        context: dict[str, Any],
        execution_id: str = "exec_1",
    ) -> CodeExecution:
        started_at = time.perf_counter()
        try:
            tree = ast.parse(code, mode="exec")
            _CodePolicy().visit(tree)
            self._validate_context(context)
        except (SyntaxError, TypeError, ValueError) as exc:
            return self._record(
                execution_id,
                code,
                "rejected",
                error=str(exc),
                started_at=started_at,
            )

        namespace: dict[str, Any] = {
            "__builtins__": self.allowed_builtins,
            **{name: deepcopy(context.get(name, [])) for name in self.allowed_context_names},
        }
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                exec(compile(tree, "<code-wizard>", "exec"), namespace, namespace)
        except Exception as exc:  # 执行错误要作为研究结果返回，而不是中断服务。
            return self._record(
                execution_id,
                code,
                "failed",
                stdout=output.getvalue(),
                error=str(exc),
                started_at=started_at,
            )

        result = namespace.get("result", {})
        if result is None:
            result = {}
        if not isinstance(result, dict):
            return self._record(
                execution_id,
                code,
                "failed",
                stdout=output.getvalue(),
                error="代码变量 result 必须是对象",
                started_at=started_at,
            )

        return self._record(
            execution_id,
            code,
            "succeeded",
            stdout=output.getvalue(),
            result=result,
            started_at=started_at,
        )

    @classmethod
    def _validate_context(cls, context: dict[str, Any]) -> None:
        if not isinstance(context, dict):
            raise ValueError("执行上下文必须是对象")
        unknown_names = set(context) - cls.allowed_context_names
        if unknown_names:
            names = ", ".join(sorted(unknown_names))
            raise ValueError(f"执行上下文包含不允许的字段: {names}")

    @staticmethod
    def _record(
        execution_id: str,
        code: str,
        status: str,
        *,
        stdout: str = "",
        error: str = "",
        result: dict[str, Any] | None = None,
        started_at: float,
    ) -> CodeExecution:
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        return CodeExecution(
            id=execution_id,
            code=code,
            status=status,
            stdout=stdout,
            error=error,
            duration_ms=duration_ms,
            result=result or {},
        )
