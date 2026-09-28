"""Prompt compiler for promptcat."""

from __future__ import annotations

from typing import Any
from promptcat.cleaner import TextCleaner
from promptcat.history import save_history
from promptcat.models import (
    CleanedText,
    CompiledPrompt,
    DetectedRule,
    PromptFormat,
    PromptMode,
    PromptRequest,
)
from promptcat.rules import RuleRegistry
from promptcat.templates import MODE_DEFAULTS, render_template
from promptcat.tokens import estimate_tokens


class PromptCompiler:
    """Orchestrates text cleaning, domain analysis, token estimation, and template compilation."""

    def __init__(
        self,
        cleaner: TextCleaner | None = None,
        registry: RuleRegistry | None = None,
    ) -> None:
        self.cleaner = cleaner if cleaner is not None else TextCleaner()
        self.registry = registry if registry is not None else RuleRegistry()

    def compile(self, request: PromptRequest) -> CompiledPrompt:
        """Compile a PromptRequest into a deterministic CompiledPrompt with token stats and history."""
        # 1. Clean input text
        cleaned: CleanedText = self.cleaner.clean(request.text)

        # Handle pure Grammar mode
        if request.mode == PromptMode.GRAMMAR:
            tokens, chars, words = estimate_tokens(cleaned.cleaned)
            hist_id = None
            if not request.options.get("no_history", False):
                hist_id = save_history(
                    mode=request.mode.value,
                    format_type=request.format.value,
                    raw_input=request.text,
                    cleaned_text=cleaned.cleaned,
                    prompt_text=cleaned.cleaned,
                    tokens=tokens,
                    stack=[],
                )

            return CompiledPrompt(
                raw_input=request.text,
                cleaned_text=cleaned.cleaned,
                mode=PromptMode.GRAMMAR,
                format=request.format,
                detected_domains=[],
                stack=[],
                prompt_text=cleaned.cleaned,
                estimated_tokens=tokens,
                char_count=chars,
                word_count=words,
                history_id=hist_id,
                metadata={
                    "corrections": cleaned.corrections,
                    "corrections_count": len(cleaned.corrections),
                },
            )

        # 2. Analyze domain rules
        detected_rules: list[DetectedRule] = self.registry.analyze(cleaned.cleaned)
        detected_domains: list[str] = [rule.domain for rule in detected_rules]

        # 3. Aggregate technologies (explicit user stack + detected keywords)
        detected_tech = self.registry.detect_technologies(cleaned.cleaned)
        combined_stack: list[str] = []
        seen_stack: set[str] = set()

        # Add explicit stack first
        for tech in request.stack:
            item = tech.strip()
            if item and item.lower() not in seen_stack:
                seen_stack.add(item.lower())
                combined_stack.append(item)

        # Add auto-detected stack
        for tech in detected_tech:
            if tech.lower() not in seen_stack:
                seen_stack.add(tech.lower())
                combined_stack.append(tech)

        # 4. Mode defaults configuration
        mode_conf = MODE_DEFAULTS.get(request.mode, MODE_DEFAULTS[PromptMode.IMPROVE])

        # 5. Role
        role = request.role if request.role else mode_conf["role"]

        # 6. Task
        task_prefix = mode_conf.get("task_prefix", "Execute the following task:")
        if request.task:
            task = f"{task_prefix}\n{request.task.strip()}"
        else:
            task = f"{task_prefix}\n{cleaned.cleaned.strip()}"

        # 7. Context
        context_intro = mode_conf.get("context_intro", "Context:")
        if request.context:
            context = f"{context_intro}\n{request.context.strip()}\n\nDetailed Request:\n{cleaned.cleaned.strip()}"
        else:
            context = f"{context_intro}\n{cleaned.cleaned.strip()}"

        # 8. Technology section
        if combined_stack:
            tech_bullets = "\n".join(f"- {tech}" for tech in combined_stack)
            technology = f"Primary Technology Stack:\n{tech_bullets}"
        else:
            technology = "Standard modern frameworks, idioms, and standard library tools appropriate for the problem."

        # 9. Aggregate constraints (deterministic deduplication)
        constraints_list: list[str] = []
        seen_constraints: set[str] = set()

        def _add_constraint(c: str) -> None:
            stripped = c.strip()
            if stripped and stripped not in seen_constraints:
                seen_constraints.add(stripped)
                constraints_list.append(stripped)

        # User-specified custom constraints
        for c in request.constraints:
            _add_constraint(c)

        # Mode default constraints
        for c in mode_conf.get("default_constraints", []):
            _add_constraint(c)

        # Domain rule constraints
        for rule in detected_rules:
            for c in rule.constraints:
                _add_constraint(f"[{rule.domain}] {c}")

        constraints_formatted = "\n".join(f"- {c}" for c in constraints_list)

        # 10. Requirements
        req_list: list[str] = list(mode_conf.get("default_requirements", []))
        requirements_formatted = "\n".join(f"- {req}" for req in req_list)

        # 11. Expected Output
        output_text = mode_conf.get("default_output", "")

        # 12. Render XML or Markdown template
        prompt_text = render_template(
            role=role,
            task=task,
            context=context,
            technology=technology,
            constraints=constraints_formatted,
            requirements=requirements_formatted,
            output=output_text,
            format_type=request.format,
        )

        # 13. Estimate tokens
        tokens, chars, words = estimate_tokens(prompt_text)

        # 14. Save to local history
        hist_id = None
        if not request.options.get("no_history", False):
            hist_id = save_history(
                mode=request.mode.value,
                format_type=request.format.value,
                raw_input=request.text,
                cleaned_text=cleaned.cleaned,
                prompt_text=prompt_text,
                tokens=tokens,
                stack=combined_stack,
            )

        metadata: dict[str, Any] = {
            "corrections": cleaned.corrections,
            "corrections_count": len(cleaned.corrections),
            "detected_domains": detected_domains,
            "detected_rules_count": len(detected_rules),
            "stack": combined_stack,
            "tokens": tokens,
            "chars": chars,
            "words": words,
        }

        return CompiledPrompt(
            raw_input=request.text,
            cleaned_text=cleaned.cleaned,
            mode=request.mode,
            format=request.format,
            detected_domains=detected_domains,
            stack=combined_stack,
            prompt_text=prompt_text,
            estimated_tokens=tokens,
            char_count=chars,
            word_count=words,
            history_id=hist_id,
            metadata=metadata,
        )


def compile_prompt(
    text: str,
    mode: PromptMode = PromptMode.IMPROVE,
    format_type: PromptFormat = PromptFormat.XML,
    stack: list[str] | None = None,
    constraints: list[str] | None = None,
    options: dict[str, Any] | None = None,
) -> CompiledPrompt:
    """Convenience helper to compile prompt from text and parameters."""
    req = PromptRequest(
        text=text,
        mode=mode,
        format=format_type,
        stack=stack if stack is not None else [],
        constraints=constraints if constraints is not None else [],
        options=options if options is not None else {},
    )
    return PromptCompiler().compile(req)
