import ast
import operator
from typing import Union


SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


class CalculatorTool:
    def evaluate(self, expression: str) -> Union[float, str]:
        """Safely evaluate a math expression."""
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            return self._eval(tree.body)
        except Exception as e:
            return f"Calculation error: {e}"

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(self._eval(node.operand))
        raise ValueError(f"Unsupported expression: {node}")
