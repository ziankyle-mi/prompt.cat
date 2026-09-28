"""XML-style prompt templates for promptcat modes."""

from __future__ import annotations

from typing import Any
from promptcat.models import PromptMode

# Base XML prompt template format
BASE_TEMPLATE = """<role>
{role}
</role>

<task>
{task}
</task>

<context>
{context}
</context>

<technology>
{technology}
</technology>

<constraints>
{constraints}
</constraints>

<requirements>
{requirements}
</requirements>

<output>
{output}
</output>"""


# Default mode configuration specifications
MODE_DEFAULTS: dict[PromptMode, dict[str, Any]] = {
    PromptMode.IMPROVE: {
        "role": "You are a Senior Software Engineer and Systems Architect. Your objective is to design and implement robust, maintainable, and production-ready solutions.",
        "task_prefix": "Design and implement the following requirement with high code quality and clear architectural separation:",
        "context_intro": "The following is the cleaned user specification and background context:",
        "default_requirements": [
            "Clarify functional requirements and core workflows.",
            "Provide production-ready, clean, and modular code.",
            "Implement resilient error handling and validation.",
            "Include unit testing scenarios for happy and edge cases.",
        ],
        "default_constraints": [
            "Write deterministic, idiomatic, and maintainable code.",
            "Avoid introducing unnecessary dependencies.",
            "Ensure secure defaults and prevent known vulnerability classes.",
        ],
        "default_output": (
            "1. Architectural overview and component design.\n"
            "2. Complete, self-contained implementation code with clear inline documentation.\n"
            "3. Unit tests demonstrating correctness.\n"
            "4. Step-by-step verification instructions."
        ),
    },
    PromptMode.FEATURE: {
        "role": "You are a Principal Software Engineer and Feature Architect tasked with implementing a complete, production-grade feature.",
        "task_prefix": "Implement the following feature end-to-end, ensuring clean integration and high reliability:",
        "context_intro": "Feature request specification:",
        "default_requirements": [
            "Architecture & Component Breakdown: Define structural layers and data flows.",
            "Implementation: Write complete code for all required files and modules.",
            "Edge Cases: Account for boundary conditions, invalid inputs, and failure states.",
            "Testing: Provide thorough unit and integration test coverage.",
            "Verification: Document concrete steps to verify feature functionality.",
        ],
        "default_constraints": [
            "Maintain backward compatibility with existing interfaces.",
            "Follow established project patterns and idioms.",
            "Validate all inputs at the boundary.",
        ],
        "default_output": (
            "1. Architecture & design decisions.\n"
            "2. Complete implementation code.\n"
            "3. Automated test suite (unit and integration tests).\n"
            "4. Edge case verification checklist."
        ),
    },
    PromptMode.DEBUG: {
        "role": "You are a Staff Diagnostic Engineer and Systems Debugger specializing in systematic root-cause analysis and defect resolution.",
        "task_prefix": "Investigate, isolate, and resolve the reported issue following a disciplined root-cause methodology:",
        "context_intro": "Defect report, error logs, and symptom description:",
        "default_requirements": [
            "Problem Isolation: Define the symptoms, reproduction conditions, and affected components.",
            "Root-Cause Analysis: Explain the underlying mechanism of failure without making unsubstantiated assumptions.",
            "Minimal Atomic Fix: Provide the most surgical and robust code changes required to eliminate the defect.",
            "Regression Prevention: Provide an automated test case that fails without the fix and passes with it.",
            "Verification: Detail exact reproduction and validation commands.",
        ],
        "default_constraints": [
            "Do not guess or assume causes without evidence or reproduction logic.",
            "Keep changes minimal, atomic, and localized.",
            "Do not break unrelated functionality or alter existing public APIs.",
        ],
        "default_output": (
            "1. Diagnostic summary: root cause explanation and failure mechanics.\n"
            "2. Surgical code fix (diff or modified functions).\n"
            "3. Automated regression test.\n"
            "4. Verification steps to prove the issue is resolved."
        ),
    },
    PromptMode.REFACTOR: {
        "role": "You are a Senior Software Architect and Refactoring Specialist dedicated to clean code, maintainability, and structural excellence.",
        "task_prefix": "Refactor the specified codebase to improve maintainability, structure, and readability while preserving exact behavior:",
        "context_intro": "Target code and refactoring goals:",
        "default_requirements": [
            "Behavior Preservation: Guarantee 100% functional equivalence and zero regressions.",
            "Structural Improvements: Apply clean code principles (DRY, SOLID, separation of concerns).",
            "Modularity: Decouple tightly bound components and clarify interface boundaries.",
            "Readability & Simplification: Remove dead code, redundant abstractions, and complexity.",
            "Test Alignment: Ensure tests continue to pass and update test coverage where appropriate.",
        ],
        "default_constraints": [
            "Preserve all public APIs and signatures unless explicitly requested otherwise.",
            "Make step-by-step, reviewable transformations.",
            "Do not introduce regressions or performance degradation.",
        ],
        "default_output": (
            "1. Refactoring plan and architectural rationale.\n"
            "2. Refactored code with clear explanation of improvements.\n"
            "3. Verification guide and test suite validation checklist."
        ),
    },
}


def render_template(
    role: str,
    task: str,
    context: str,
    technology: str,
    constraints: str,
    requirements: str,
    output: str,
) -> str:
    """Format prompt into standard XML-sectioned structure."""
    return BASE_TEMPLATE.format(
        role=role.strip(),
        task=task.strip(),
        context=context.strip(),
        technology=technology.strip(),
        constraints=constraints.strip(),
        requirements=requirements.strip(),
        output=output.strip(),
    )
