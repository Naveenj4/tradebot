"""
tests/unit/test_bias.py
Unit tests for BiasEvaluator (Spot vs Index Open).
"""
from decimal import Decimal
from src.core.bias import BiasEvaluator, BiasDirection

def test_bullish_bias():
    res = BiasEvaluator.evaluate(index_open=Decimal("25450.00"), reference_spot=Decimal("25400.00"))
    assert res.direction == BiasDirection.BULLISH
    assert res.diff == Decimal("50.00")

def test_bearish_bias():
    res = BiasEvaluator.evaluate(index_open=Decimal("25380.50"), reference_spot=Decimal("25400.00"))
    assert res.direction == BiasDirection.BEARISH
    assert res.diff == Decimal("-19.50")

def test_neutral_bias():
    res = BiasEvaluator.evaluate(index_open=Decimal("25400.00"), reference_spot=Decimal("25400.00"))
    assert res.direction == BiasDirection.NEUTRAL
    assert res.diff == Decimal("0.00")

