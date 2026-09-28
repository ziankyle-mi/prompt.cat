"""Data models for promptcat."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PromptMode(str, Enum):
    """Available prompt compilation modes."""

    IMPROVE = "improve"
    GRAMMAR = "grammar"
    FEATURE = "feature"
    DEBUG = "debug"
    REFACTOR = "refactor"

    @classmethod
    def from_str(cls, value: str) -> PromptMode:
        """Parse string to PromptMode case-insensitively."""
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Unknown prompt mode: '{value}'. Valid modes: {[m.value for m in cls]}")


class PromptFormat(str, Enum):
    """Template output format (XML or Markdown)."""

    XML = "xml"
    MARKDOWN = "markdown"

    @classmethod
    def from_str(cls, value: str) -> PromptFormat:
        """Parse string to PromptFormat case-insensitively."""
        normalized = value.strip().lower()
        for fmt in cls:
            if fmt.value == normalized:
                return fmt
        raise ValueError(f"Unknown prompt format: '{value}'. Valid formats: {[f.value for f in cls]}")


@dataclass
class DetectedRule:
    """Represents a domain rule matched against user text."""

    domain: str
    matched_keywords: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass
class CleanedText:
    """Result of deterministic text cleaning."""

    original: str
    cleaned: str
    corrections: list[str] = field(default_factory=list)


@dataclass
class PromptRequest:
    """User input and options requested for compilation."""

    text: str
    mode: PromptMode = PromptMode.IMPROVE
    format: PromptFormat = PromptFormat.XML
    stack: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    role: str | None = None
    task: str | None = None
    context: str | None = None
    constraints: list[str] = field(default_factory=list)


@dataclass
class CompiledPrompt:
    """Final compiled prompt output and metadata."""

    raw_input: str
    cleaned_text: str
    mode: PromptMode
    format: PromptFormat = PromptFormat.XML
    detected_domains: list[str] = field(default_factory=list)
    stack: list[str] = field(default_factory=list)
    prompt_text: str = ""
    estimated_tokens: int = 0
    char_count: int = 0
    word_count: int = 0
    history_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
