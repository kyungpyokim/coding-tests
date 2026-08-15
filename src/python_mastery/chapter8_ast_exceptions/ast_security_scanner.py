import ast
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
    """AST Visitor scanning for dangerous constructs in Python source code.

    Forbidden Calls: 'eval', 'exec', '__import__', 'open'
    Forbidden Attributes: '__subclasses__', '__globals__', '__code__'
    Forbidden Statements: `global`
    """

    FORBIDDEN_CALLS = {"eval", "exec", "__import__", "open"}
    FORBIDDEN_ATTRS = {"__subclasses__", "__globals__", "__code__"}

    def __init__(self) -> None:
        self.report = SecurityReport()

    def visit_Call(self, node: ast.Call) -> None:
        # TODO: node.func가 ast.Name(예: eval()) 또는 ast.Attribute(예: os.system())인 경우를 검사하여
        # FORBIDDEN_CALLS에 포함되면 self.report.forbidden_calls에 추가하세요.
        # generic_visit(node)를 호출하여 자식 노드 순회를 유지하세요.
        raise NotImplementedError

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # TODO: node.attr이 FORBIDDEN_ATTRS에 포함되면 self.report.forbidden_attributes에 추가하세요.
        # generic_visit(node)를 호출하세요.
        raise NotImplementedError

    def visit_Global(self, node: ast.Global) -> None:
        # TODO: self.report.has_global_statement = True 로 설정하세요.
        # generic_visit(node)를 호출하세요.
        raise NotImplementedError


class SecurityScanner:
    @staticmethod
    def scan_source(source_code: str) -> SecurityReport:
        """Parse source into AST and run SecurityASTVisitor."""
        # TODO: ast.parse(source_code)를 수행하고 SecurityASTVisitor를 실행한 후 report를 반환하세요.
        raise NotImplementedError


def validate_callable_signature(
    func: Callable[..., Any],
    required_params: list[str],
    require_type_annotations: bool = True,
) -> bool:
    """Validate function signature using Python's `inspect.signature`.

    - Verifies all `required_params` are present in the signature.
    - If `require_type_annotations` is True, verifies that each required param
      has an annotation (not inspect.Parameter.empty) and return annotation exists.
    """
    # TODO: inspect.signature(func)를 검사하여 조건을 만족하면 True, 아니면 False를 반환하세요.
    raise NotImplementedError
