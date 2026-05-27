import pytest
from tools.calculator import CalculatorTool


class TestCalculatorTool:
    def setup_method(self):
        self.calc = CalculatorTool()

    def test_addition(self):
        assert self.calc.evaluate("2 + 3") == 5

    def test_subtraction(self):
        assert self.calc.evaluate("10 - 4") == 6

    def test_multiplication(self):
        assert self.calc.evaluate("6 * 7") == 42

    def test_division(self):
        assert self.calc.evaluate("15 / 3") == 5.0

    def test_complex_expression(self):
        assert self.calc.evaluate("(2 + 3) * 4") == 20

    def test_power(self):
        assert self.calc.evaluate("2 ** 10") == 1024

    def test_invalid_expression(self):
        result = self.calc.evaluate("import os")
        assert "error" in result.lower()
