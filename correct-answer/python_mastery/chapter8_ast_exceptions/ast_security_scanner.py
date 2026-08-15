import ast
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SecurityReport:
    forbidden_calls: list[str] = field(default_factory=list)
    forbidden_attributes: list[str] = field(default_factory=list)
    has_global_statement: bool = False

    @property
    def is_safe(self) -> bool:
        return (
            not self.forbidden_calls
            and not self.forbidden_attributes
            and not self.has_global_statement
        )


class SecurityASTVisitor(ast.NodeVisitor):
    FORBIDDEN_CALLS = {"eval", "exec", "__import__", "open"}
    FORBIDDEN_ATTRS = {"__subclasses__", "__globals__", "__code__"}

    def __init__(self) -> None:
        self.report = SecurityReport()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_CALLS:
                self.report.forbidden_calls.append(node.func.id)
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in self.FORBIDDEN_CALLS
        ):
            self.report.forbidden_calls.append(node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in self.FORBIDDEN_ATTRS:
            self.report.forbidden_attributes.append(node.attr)
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self.report.has_global_statement = True
        self.generic_visit(node)


class SecurityScanner:
    @staticmethod
    def scan_source(source_code: str) -> SecurityReport:
        tree = ast.parse(source_code)
        visitor = SecurityASTVisitor()
        visitor.visit(tree)
        return visitor.report


def validate_callable_signature(
    func: Callable[..., Any],
    required_params: list[str],
    require_type_annotations: bool = True,
) -> bool:
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return False

    for param_name in required_params:
        if param_name not in sig.parameters:
            return False
        if require_type_annotations:
            param = sig.parameters[param_name]
            if param.annotation is inspect.Parameter.empty:
                return False

    return not (
        require_type_annotations and sig.return_annotation is inspect.Signature.empty
    )
