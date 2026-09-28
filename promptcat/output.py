"""Semantic terminal output using Rich (no emojis, strictly semantic tags)."""

from __future__ import annotations

import sys
from rich.console import Console
from rich.syntax import Syntax


class OutputFormatter:
    """Semantic terminal formatting without emoji clutter."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console if console is not None else Console(highlight=False)

    def ok(self, message: str) -> None:
        """Display success semantic tag."""
        self.console.print(f"[bold green][OK][/bold green] {message}")

    def info(self, message: str) -> None:
        """Display info semantic tag."""
        self.console.print(f"[bold cyan][INFO][/bold cyan] {message}")

    def warn(self, message: str) -> None:
        """Display warning semantic tag."""
        self.console.print(f"[bold yellow][WARN][/bold yellow] {message}")

    def error(self, message: str) -> None:
        """Display error semantic tag."""
        self.console.print(f"[bold red][ERROR][/bold red] {message}", file=sys.stderr)

    def print_prompt(self, text: str, is_xml: bool = True) -> None:
        """Render prompt text cleanly to the console."""
        if is_xml and text.startswith("<role>"):
            syntax = Syntax(text, "xml", theme="ansi_dark", word_wrap=True)
            self.console.print(syntax)
        else:
            self.console.print(text)

    def raw(self, text: str) -> None:
        """Print raw text directly to stdout without formatting or tags."""
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()


# Global default instance
formatter = OutputFormatter()
