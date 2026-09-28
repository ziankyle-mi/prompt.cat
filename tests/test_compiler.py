"""Tests for promptcat prompt compiler."""

import pytest
from promptcat.compiler import PromptCompiler, compile_prompt
from promptcat.models import PromptFormat, PromptMode, PromptRequest


class TestCompiler:
    @pytest.fixture
    def compiler(self):
        return PromptCompiler()

    def test_improve_mode_structure(self, compiler):
        req = PromptRequest(
            text="i want to make a login page using react but idk how to make the backend and make it secure",
            mode=PromptMode.IMPROVE,
        )
        compiled = compiler.compile(req)

        assert "<role>" in compiled.prompt_text
        assert "<task>" in compiled.prompt_text
        assert "<context>" in compiled.prompt_text
        assert "<technology>" in compiled.prompt_text
        assert "<constraints>" in compiled.prompt_text
        assert "<requirements>" in compiled.prompt_text
        assert "<output>" in compiled.prompt_text

        assert "Senior Software Engineer" in compiled.prompt_text
        assert "Authentication" in compiled.detected_domains
        assert "React" in compiled.stack
        assert compiled.estimated_tokens > 50

    def test_markdown_format(self, compiler):
        req = PromptRequest(
            text="Add OAuth2 Google login button to user settings",
            mode=PromptMode.FEATURE,
            format=PromptFormat.MARKDOWN,
            stack=["TypeScript", "Next.js"],
        )
        compiled = compiler.compile(req)

        assert "# Role" in compiled.prompt_text
        assert "## Task" in compiled.prompt_text
        assert "## Context" in compiled.prompt_text
        assert "## Technology Stack" in compiled.prompt_text
        assert "<role>" not in compiled.prompt_text
        assert compiled.estimated_tokens > 50

    def test_feature_mode(self, compiler):
        req = PromptRequest(
            text="Add OAuth2 Google login button to user settings",
            mode=PromptMode.FEATURE,
            stack=["TypeScript", "Next.js"],
        )
        compiled = compiler.compile(req)

        assert "Principal Software Engineer" in compiled.prompt_text
        assert "Edge Cases" in compiled.prompt_text
        assert "TypeScript" in compiled.prompt_text
        assert "Next.js" in compiled.prompt_text

    def test_debug_mode(self, compiler):
        req = PromptRequest(
            text="User token expires immediately after login in Safari browser",
            mode=PromptMode.DEBUG,
        )
        compiled = compiler.compile(req)

        assert "Staff Diagnostic Engineer" in compiled.prompt_text
        assert "Root-Cause Analysis" in compiled.prompt_text
        assert "Minimal Atomic Fix" in compiled.prompt_text
        assert "Regression Prevention" in compiled.prompt_text

    def test_refactor_mode(self, compiler):
        req = PromptRequest(
            text="Refactor the authentication middleware to use dependency injection",
            mode=PromptMode.REFACTOR,
        )
        compiled = compiler.compile(req)

        assert "Refactoring Specialist" in compiled.prompt_text
        assert "Behavior Preservation" in compiled.prompt_text
        assert "zero regressions" in compiled.prompt_text.lower()

    def test_grammar_mode(self, compiler):
        req = PromptRequest(
            text="teh api dont work with mysql",
            mode=PromptMode.GRAMMAR,
        )
        compiled = compiler.compile(req)

        assert compiled.prompt_text == "The API don't work with MySQL."
        assert "<role>" not in compiled.prompt_text

    def test_explicit_constraints_merged(self, compiler):
        req = PromptRequest(
            text="Build a REST API endpoint",
            mode=PromptMode.IMPROVE,
            constraints=["Do not use ORM.", "Respond within 50ms."],
        )
        compiled = compiler.compile(req)

        assert "Do not use ORM." in compiled.prompt_text
        assert "Respond within 50ms." in compiled.prompt_text
        assert "[API]" in compiled.prompt_text

    def test_determinism_50_iterations(self, compiler):
        req = PromptRequest(
            text="build a JWT login API using postgresql and react",
            mode=PromptMode.FEATURE,
            stack=["Docker"],
        )
        results = [compiler.compile(req).prompt_text for _ in range(50)]
        assert len(set(results)) == 1
