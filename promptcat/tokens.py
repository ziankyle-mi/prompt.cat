"""Offline, deterministic token and text statistic estimation."""

from __future__ import annotations

import re


def estimate_tokens(text: str) -> tuple[int, int, int]:
    """Estimate token count, character count, and word count offline.

    Uses a deterministic heuristic aligned with modern Byte-Pair Encoding (BPE)
    tokenizers (e.g. cl100k_base / LLaMA / Claude), where:
    - Normal words average ~1.3 tokens
    - Punctuation, symbols, XML/Markdown tags, and numbers form discrete tokens
    - Whitespace and line breaks consume tokens

    Returns:
        (estimated_tokens: int, char_count: int, word_count: int)
    """
    if not text:
        return 0, 0, 0

    char_count = len(text)
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    # Regex tokenization pattern approximating BPE
    # 1. Words of varying lengths (long words get broken into ~4-char fragments)
    # 2. Number sequences
    # 3. Punctuation and XML/HTML tag boundaries
    # 4. Newlines and indentations
    tokens = 0

    # Break words into approximate BPE subwords
    for word in words:
        length = len(word)
        if length <= 4:
            tokens += 1
        elif length <= 8:
            tokens += 2
        elif length <= 12:
            tokens += 3
        else:
            tokens += (length + 3) // 4

    # Add tokens for special symbols and punctuation (< > / = " - : ; , . etc.)
    symbols = re.findall(r"[^\w\s]", text)
    tokens += len(symbols)

    # Add tokens for newlines and tabs
    newlines = len(re.findall(r"\n+", text))
    tokens += newlines

    return max(1, tokens), char_count, word_count
