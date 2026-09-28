"""Tests for promptcat text cleaner."""

import pytest
from promptcat.cleaner import TextCleaner, clean_text


class TestCleaner:
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()

    def test_whitespace_normalization(self, cleaner):
        raw = "make the ui nice   and responsive"
        result = cleaner.clean(raw)
        assert "nice and responsive" in result.cleaned

    def test_multiline_whitespace_and_blank_lines(self, cleaner):
        raw = "line 1   \n\n\n\n   line 2   "
        result = cleaner.clean(raw)
        assert result.cleaned == "Line 1.\n\nLine 2."

    def test_capitalization_standalone_i(self, cleaner):
        raw = "i want this to work"
        result = cleaner.clean(raw)
        assert result.cleaned == "I want this to work."

    def test_contractions(self, cleaner):
        assert cleaner.clean("dont use a database").cleaned == "Don't use a database."
        assert cleaner.clean("cant do this").cleaned == "Can't do this."
        assert cleaner.clean("wont fail").cleaned == "Won't fail."
        assert cleaner.clean("im building an app").cleaned == "I'm building an app."
        assert cleaner.clean("ive seen this").cleaned == "I've seen this."

    def test_conditional_id_contraction(self, cleaner):
        # "id like" -> "I'd like"
        assert cleaner.clean("id like to create a feature").cleaned == "I'd like to create a feature."
        # "user id" should NOT become "user I'd"
        assert "user id" in cleaner.clean("pass the user id to the endpoint").cleaned

    def test_common_typos(self, cleaner):
        raw = "teh system will recieve seperate requests"
        result = cleaner.clean(raw)
        assert "the system will receive separate requests" in result.cleaned.lower()

    def test_tech_casing(self, cleaner):
        raw = "build a ui with react and an api with postgres and jwt"
        result = cleaner.clean(raw)
        assert "UI" in result.cleaned
        assert "React" in result.cleaned
        assert "API" in result.cleaned
        assert "PostgreSQL" in result.cleaned
        assert "JWT" in result.cleaned

    def test_punctuation_cleanup(self, cleaner):
        raw = "hello ,world !! is this working ???"
        result = cleaner.clean(raw)
        assert "Hello, world!" in result.cleaned
        assert "Is this working?" in result.cleaned

    def test_code_block_preservation(self, cleaner):
        code_snippet = "def dont_change_teh_code():\n    return 42"
        raw = f"Fix this code:\n```{code_snippet}```"
        result = cleaner.clean(raw)
        assert code_snippet in result.cleaned

    def test_determinism(self, cleaner):
        raw = "i want to make a login page using react but idk how to make teh backend and make it secure"
        results = [cleaner.clean(raw).cleaned for _ in range(50)]
        assert len(set(results)) == 1

    def test_empty_string(self, cleaner):
        result = cleaner.clean("")
        assert result.cleaned == ""
        assert result.corrections == []
