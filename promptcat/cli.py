"""Typer-based command line interface for promptcat."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
import typer
import questionary
from rich.table import Table
from promptcat import __version__
from promptcat.cleaner import TextCleaner
from promptcat.clipboard import copy_to_clipboard
from promptcat.compiler import PromptCompiler
from promptcat.history import clear_history, get_history, get_last_history, list_history
from promptcat.models import PromptFormat, PromptMode, PromptRequest
from promptcat.output import OutputFormatter, formatter
from promptcat.rules import RuleRegistry

app = typer.Typer(
    name="promptcat",
    help="Offline, deterministic prompt compiler and text improver.",
    add_completion=False,
    no_args_is_help=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"promptcat v{__version__}")
        raise typer.Exit()


def _handle_history_operation(
    out: OutputFormatter,
    show_id: Optional[int] = None,
    last: bool = False,
    clear: bool = False,
    limit: int = 10,
    copy: bool = True,
) -> None:
    """Handle all history viewing, retrieval, and clearing operations."""
    if clear:
        deleted = clear_history()
        out.ok(f"Cleared {deleted} history records.")
        return

    # Show single entry
    entry = None
    if last:
        entry = get_last_history()
        if not entry:
            out.warn("No prompt history found.")
            return
    elif show_id is not None:
        entry = get_history(show_id)
        if not entry:
            out.error(f"History entry #{show_id} not found.")
            raise typer.Exit(code=1)

    if entry is not None:
        out.ok(f"Prompt #{entry['id']} ({entry['created_at']} | Mode: {entry['mode']} | ~{entry['tokens']} tokens)")
        if copy:
            success, msg = copy_to_clipboard(entry["prompt_text"])
            if success:
                out.ok("Copied to clipboard")
            else:
                out.warn(f"Clipboard unavailable: {msg}")

        out.console.print()
        out.print_prompt(
            entry["prompt_text"],
            is_xml=(entry["format"] == "xml" and entry["mode"] != "grammar"),
        )
        return

    # List recent entries in a clean table
    entries = list_history(limit=limit)
    if not entries:
        out.info("No prompt history yet. Generate prompts with 'promptcat' to see them here!")
        return

    table = Table(title="Recent Prompt History", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="bold green", justify="right", width=5)
    table.add_column("Date", style="dim", width=19)
    table.add_column("Mode", style="yellow", width=10)
    table.add_column("Fmt", style="magenta", width=8)
    table.add_column("Tokens", justify="right", width=8)
    table.add_column("Input Preview", style="white")

    for e in entries:
        preview = e["raw_input"].replace("\n", " ").strip()
        if len(preview) > 50:
            preview = preview[:47] + "..."
        table.add_row(
            str(e["id"]),
            e["created_at"],
            e["mode"],
            e["format"],
            f"~{e['tokens']}",
            preview,
        )

    out.console.print(table)
    out.console.print("[dim]Use 'promptcat --history-show <ID>' or '--last' to view and re-copy.[/dim]")


def _run_interactive() -> tuple[str, PromptMode, PromptFormat, list[str]]:
    """Prompt the user interactively with intuitive choices."""
    text = questionary.text("What do you want to build or improve? (Press Enter):").ask()
    if not text or not text.strip():
        typer.echo("Error: Input text cannot be empty.", err=True)
        raise typer.Exit(code=1)

    # 1. Mode Selection with clear guidance
    mode_choice = questionary.select(
        "Select mode:",
        choices=[
            questionary.Choice("Improve  (Senior architecture & plan - Recommended)", value="improve"),
            questionary.Choice("Feature  (Complete implementation, edge cases & tests)", value="feature"),
            questionary.Choice("Debug    (Root-cause diagnosis & surgical fix)", value="debug"),
            questionary.Choice("Refactor (Code cleanup & zero regressions)", value="refactor"),
            questionary.Choice("Grammar  (Fix typos, punctuation & formatting only)", value="grammar"),
        ],
        default="improve",
    ).ask()
    mode = PromptMode.from_str(mode_choice or "improve")

    # 2. Format Selection (XML vs Markdown)
    format_choice = questionary.select(
        "Select prompt format:",
        choices=[
            questionary.Choice("XML tags  (<role>, <task> - Best for Claude / Anthropic)", value="xml"),
            questionary.Choice("Markdown  (# Role, ## Task - Best for ChatGPT, Cursor)", value="markdown"),
        ],
        default="xml",
    ).ask()
    prompt_format = PromptFormat.from_str(format_choice or "xml")

    # 3. Easy Stack Selection via Checkboxes
    stack_choices = [
        questionary.Choice("None (Auto-detect from my idea)", value="__NONE__", checked=True),
        questionary.Choice("React", value="React"),
        questionary.Choice("Next.js", value="Next.js"),
        questionary.Choice("Vue.js", value="Vue.js"),
        questionary.Choice("Tailwind CSS", value="Tailwind CSS"),
        questionary.Choice("TypeScript", value="TypeScript"),
        questionary.Choice("Python / FastAPI", value="FastAPI"),
        questionary.Choice("Node.js / Express", value="Express.js"),
        questionary.Choice("PostgreSQL", value="PostgreSQL"),
        questionary.Choice("MongoDB", value="MongoDB"),
        questionary.Choice("SQLite", value="SQLite"),
        questionary.Choice("Docker", value="Docker"),
        questionary.Choice("Type custom stack...", value="__CUSTOM__"),
    ]

    selected_stacks = questionary.checkbox(
        "Select tech stack (Spacebar to toggle, Enter to confirm):",
        choices=stack_choices,
    ).ask() or []

    stack: list[str] = []
    if "__CUSTOM__" in selected_stacks:
        custom_input = questionary.text("Enter custom tech stack (comma-separated):").ask()
        if custom_input:
            stack.extend([s.strip() for s in custom_input.split(",") if s.strip()])

    for item in selected_stacks:
        if item not in ("__NONE__", "__CUSTOM__") and item not in stack:
            stack.append(item)

    return text.strip(), mode, prompt_format, stack


@app.command()
def main(
    text: Optional[str] = typer.Argument(
        None,
        help="Raw text or idea to compile into a prompt. Can also be piped via stdin.",
    ),
    mode: str = typer.Option(
        "improve",
        "--mode",
        "-m",
        help="Compilation mode: improve, grammar, feature, debug, refactor.",
    ),
    format_type: str = typer.Option(
        "xml",
        "--format",
        "-F",
        help="Template format: xml (best for Claude) or markdown (best for ChatGPT/Cursor).",
    ),
    stack: Optional[str] = typer.Option(
        None,
        "--stack",
        "-s",
        help="Comma-separated tech stack (e.g. 'react,postgresql,fastapi').",
    ),
    copy: bool = typer.Option(
        True,
        "--copy/--no-copy",
        "-c",
        help="Copy compiled prompt to system clipboard (default: enabled).",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Read input text from a file instead of arguments.",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save compiled prompt to a file.",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print only the final output text without status tags or decorations.",
    ),
    clean_only: bool = typer.Option(
        False,
        "--clean-only",
        help="Execute only the text cleaner and output the cleaned text.",
    ),
    detect_only: bool = typer.Option(
        False,
        "--detect-only",
        help="Execute only domain detection rules and output detected domains.",
    ),
    history: bool = typer.Option(
        False,
        "--history",
        "-H",
        help="View recent prompt history.",
    ),
    history_show: Optional[int] = typer.Option(
        None,
        "--history-show",
        help="View and copy prompt by history ID.",
    ),
    last: bool = typer.Option(
        False,
        "--last",
        "-l",
        help="View and re-copy the most recent prompt from history.",
    ),
    clear_history_flag: bool = typer.Option(
        False,
        "--clear-history",
        help="Clear all stored prompt history.",
    ),
    no_history: bool = typer.Option(
        False,
        "--no-history",
        help="Do not save this prompt to local history.",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Launch interactive prompt questionary.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show promptcat version.",
    ),
) -> None:
    """Compile messy ideas and pasted text into clean, structured prompts offline."""
    out: OutputFormatter = formatter

    # Check for history action
    if text == "history" or history or last or history_show is not None or clear_history_flag:
        _handle_history_operation(
            out=out,
            show_id=history_show,
            last=last,
            clear=clear_history_flag,
            copy=copy,
        )
        return

    # 1. Resolve prompt mode and format
    try:
        prompt_mode = PromptMode.from_str(mode)
    except ValueError as e:
        out.error(str(e))
        raise typer.Exit(code=1)

    try:
        parsed_format = PromptFormat.from_str(format_type)
    except ValueError as e:
        out.error(str(e))
        raise typer.Exit(code=1)

    # 2. Parse tech stack argument
    stack_list: list[str] = [s.strip() for s in (stack or "").split(",") if s.strip()]

    # 3. Resolve input text source
    input_text: str = ""

    # Priority A: --file
    if file is not None:
        if not file.exists():
            out.error(f"File not found: {file}")
            raise typer.Exit(code=1)
        input_text = file.read_text(encoding="utf-8")

    # Priority B: positional argument
    elif text is not None and text.strip():
        input_text = text

    # Priority C: standard input if piped
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()

    # Priority D: interactive mode or fallback
    elif interactive or (text is None and sys.stdin.isatty()):
        try:
            input_text, prompt_mode, parsed_format, interactive_stack = _run_interactive()
            if interactive_stack and not stack_list:
                stack_list = interactive_stack
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nOperation cancelled.", err=True)
            raise typer.Exit(code=1)

    if not input_text or not input_text.strip():
        out.error("No input text provided. Provide text as argument, --file, or pipe via stdin.")
        raise typer.Exit(code=1)

    # Initialize components
    cleaner = TextCleaner()
    registry = RuleRegistry()
    compiler = PromptCompiler(cleaner=cleaner, registry=registry)

    # Branch 1: --clean-only
    if clean_only:
        cleaned_result = cleaner.clean(input_text)
        if raw:
            out.raw(cleaned_result.cleaned)
        else:
            out.ok("Text cleaned")
            for correction in cleaned_result.corrections:
                out.info(f"Correction: {correction}")
            out.console.print()
            out.console.print(cleaned_result.cleaned)
        return

    # Branch 2: --detect-only
    if detect_only:
        cleaned_result = cleaner.clean(input_text)
        detected_rules = registry.analyze(cleaned_result.cleaned)
        detected_tech = registry.detect_technologies(cleaned_result.cleaned)
        if raw:
            for rule in detected_rules:
                out.raw(rule.domain)
        else:
            if detected_rules:
                for rule in detected_rules:
                    out.ok(f"{rule.domain} detected ({', '.join(rule.matched_keywords)})")
            else:
                out.info("No specific domains detected")
            if detected_tech:
                out.info(f"Detected technologies: {', '.join(detected_tech)}")
        return

    # Branch 3: Standard prompt compilation pipeline
    request = PromptRequest(
        text=input_text,
        mode=prompt_mode,
        format=parsed_format,
        stack=stack_list,
        options={"no_history": no_history},
    )

    compiled = compiler.compile(request)

    # Handle output file if requested
    if output_file is not None:
        try:
            output_file.write_text(compiled.prompt_text, encoding="utf-8")
        except Exception as exc:
            out.error(f"Failed to write to {output_file}: {exc}")
            raise typer.Exit(code=1)

    # Handle clipboard copy
    clipboard_msg = ""
    if copy:
        success, msg = copy_to_clipboard(compiled.prompt_text)
        if success:
            clipboard_msg = "Copied to clipboard"
        else:
            clipboard_msg = f"Clipboard unavailable: {msg}"

    # Render output
    if raw:
        out.raw(compiled.prompt_text)
    else:
        out.ok("Text cleaned")
        for domain in compiled.detected_domains:
            out.ok(f"{domain} detected")
        if compiled.stack:
            out.ok(f"Technologies: {', '.join(compiled.stack)}")

        stats_str = f"~{compiled.estimated_tokens} tokens, {compiled.char_count} chars"
        out.ok(f"Prompt compiled (Mode: {prompt_mode.value}, Format: {parsed_format.value} | {stats_str})")

        if compiled.history_id:
            out.ok(f"Saved to local history (#{compiled.history_id})")

        if copy:
            if "Copied" in clipboard_msg:
                out.ok(clipboard_msg)
            else:
                out.warn(clipboard_msg)
        if output_file is not None:
            out.ok(f"Saved to {output_file}")

        out.console.print()
        out.print_prompt(
            compiled.prompt_text,
            is_xml=(parsed_format == PromptFormat.XML and prompt_mode != PromptMode.GRAMMAR),
        )


if __name__ == "__main__":
    app()
