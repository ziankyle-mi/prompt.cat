"""Typer-based command line interface for promptcat."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
import typer
import questionary
from promptcat import __version__
from promptcat.cleaner import TextCleaner
from promptcat.clipboard import copy_to_clipboard
from promptcat.compiler import PromptCompiler
from promptcat.models import PromptMode, PromptRequest
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


def _run_interactive() -> tuple[str, PromptMode, list[str]]:
    """Prompt the user interactively using questionary."""
    text = questionary.text("What do you want to build or improve? (Press Enter):").ask()
    if not text or not text.strip():
        typer.echo("Error: Input text cannot be empty.", err=True)
        raise typer.Exit(code=1)

    mode_choice = questionary.select(
        "Select mode:",
        choices=[
            "Improve",
            "Grammar",
            "Feature",
            "Debug",
            "Refactor",
        ],
        default="Improve",
    ).ask()

    mode = PromptMode.from_str(mode_choice or "improve")

    stack_str = questionary.text("Tech stack (optional, comma-separated e.g. React, PostgreSQL):").ask()
    stack = [s.strip() for s in (stack_str or "").split(",") if s.strip()]

    return text.strip(), mode, stack


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

    # 1. Resolve prompt mode
    try:
        prompt_mode = PromptMode.from_str(mode)
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
            input_text, prompt_mode, interactive_stack = _run_interactive()
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
        stack=stack_list,
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
        out.ok(f"Prompt compiled (Mode: {prompt_mode.value})")
        if copy:
            if "Copied" in clipboard_msg:
                out.ok(clipboard_msg)
            else:
                out.warn(clipboard_msg)
        if output_file is not None:
            out.ok(f"Saved to {output_file}")

        out.console.print()
        out.print_prompt(compiled.prompt_text, is_xml=(prompt_mode != PromptMode.GRAMMAR))


if __name__ == "__main__":
    app()
