"""Tests for promptcat offline token estimation."""

from promptcat.tokens import estimate_tokens


def test_token_estimation_basic():
    tokens, chars, words = estimate_tokens("Hello world")
    assert tokens >= 2
    assert chars == 11
    assert words == 2


def test_token_estimation_empty():
    tokens, chars, words = estimate_tokens("")
    assert tokens == 0
    assert chars == 0
    assert words == 0


def test_token_estimation_code_and_tags():
    text = "<role>Senior Engineer</role>\n```python\ndef add(a, b):\n    return a + b\n```"
    tokens, chars, words = estimate_tokens(text)
    assert tokens > 15
    assert chars > len(text) - 5
