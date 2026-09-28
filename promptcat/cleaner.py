"""Deterministic text cleaning engine for promptcat."""

from __future__ import annotations

import re
from typing import Callable
from promptcat.models import CleanedText

# Common typos lookup table (unambiguous corrections)
COMMON_TYPOS: dict[str, str] = {
    "teh": "the",
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "occured": "occurred",
    "untill": "until",
    "alot": "a lot",
    "truely": "truly",
    "wierd": "weird",
    "accomodate": "accommodate",
    "enviornment": "environment",
    "dependancy": "dependency",
    "impliment": "implement",
    "implimentation": "implementation",
    "necessery": "necessary",
    "maintainance": "maintenance",
    "existense": "existence",
}

# Unambiguous contractions without apostrophes
COMMON_CONTRACTIONS: dict[str, str] = {
    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "isnt": "isn't",
    "arent": "aren't",
    "didnt": "didn't",
    "doesnt": "doesn't",
    "couldnt": "couldn't",
    "shouldnt": "shouldn't",
    "wouldnt": "wouldn't",
    "thats": "that's",
    "whats": "what's",
    "theres": "there's",
    "youre": "you're",
    "theyre": "they're",
    "weve": "we've",
    "im": "I'm",
    "ive": "I've",
}

# Technical acronyms and brand names casing
TECH_CASING: dict[str, str] = {
    "ui": "UI",
    "api": "API",
    "jwt": "JWT",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "db": "DB",
    "rest": "REST",
    "cli": "CLI",
    "url": "URL",
    "http": "HTTP",
    "https": "HTTPS",
    "json": "JSON",
    "xml": "XML",
    "sdk": "SDK",
    "orm": "ORM",
    "crud": "CRUD",
    "oauth": "OAuth",
    "react": "React",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "mysql": "MySQL",
    "vue": "Vue",
    "angular": "Angular",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "docker": "Docker",
}


def _match_case(original: str, replacement: str) -> str:
    """Preserve case style of original word if possible."""
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    if original.istitle():
        return replacement.capitalize()
    return replacement


class TextCleaner:
    """Cleans raw text through deterministic transformations."""

    def __init__(
        self,
        typos: dict[str, str] | None = None,
        contractions: dict[str, str] | None = None,
        tech_casing: dict[str, str] | None = None,
    ) -> None:
        self.typos = typos if typos is not None else dict(COMMON_TYPOS)
        self.contractions = contractions if contractions is not None else dict(COMMON_CONTRACTIONS)
        self.tech_casing = tech_casing if tech_casing is not None else dict(TECH_CASING)

    def clean(self, text: str) -> CleanedText:
        """Execute deterministic cleaning pipeline and return CleanedText with audit log."""
        if not text:
            return CleanedText(original="", cleaned="", corrections=[])

        original = text
        corrections: list[str] = []

        # 1. Protect code blocks and inline code from cleaning
        code_blocks: list[str] = []

        def _save_code(match: re.Match[str]) -> str:
            code_blocks.append(match.group(0))
            return f"__PROMPTCAT_CODE_{len(code_blocks) - 1}__"

        # Match markdown fenced code blocks or inline code
        protected = re.sub(r"```[\s\S]*?```|`[^`\n]+`", _save_code, text)

        # 2. Normalize line endings and whitespace
        step_text, wh_changes = self._normalize_whitespace(protected)
        corrections.extend(wh_changes)

        # 3. Punctuation cleanup (spacing before/after, duplicated exclamation/question marks)
        step_text, punc_changes = self._normalize_punctuation(step_text)
        corrections.extend(punc_changes)

        # 4. Contractions
        step_text, cont_changes = self._fix_contractions(step_text)
        corrections.extend(cont_changes)

        # 5. Common typos
        step_text, typo_changes = self._fix_typos(step_text)
        corrections.extend(typo_changes)

        # 6. Tech casing and acronyms
        step_text, tech_changes = self._fix_tech_casing(step_text)
        corrections.extend(tech_changes)

        # 7. Pronoun 'I' and sentence capitalization
        step_text, cap_changes = self._fix_capitalization(step_text)
        corrections.extend(cap_changes)

        # 8. Terminal punctuation
        step_text, term_changes = self._ensure_terminal_punctuation(step_text)
        corrections.extend(term_changes)

        # 9. Restore code blocks
        for i, code in enumerate(code_blocks):
            step_text = step_text.replace(f"__PROMPTCAT_CODE_{i}__", code)

        return CleanedText(original=original, cleaned=step_text, corrections=corrections)

    def _normalize_whitespace(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        # Convert CRLF to LF
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        # Strip trailing/leading spaces on each line
        lines = [line.strip() for line in normalized.split("\n")]
        line_stripped = "\n".join(lines)

        # Collapse multiple horizontal spaces within lines
        collapsed = re.sub(r"[^\S\n]+", " ", line_stripped)

        # Normalize 3+ newlines to 2 newlines (one empty line between paragraphs)
        collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)

        # Strip leading and trailing whitespace overall
        result = collapsed.strip()

        if result != text:
            changes.append("Normalized whitespace and line breaks")
        return result, changes

    def _normalize_punctuation(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        result = text

        # Remove spaces before commas, periods, colons, semicolons, exclamation/question marks
        # e.g., "hello ,world" -> "hello, world"
        new_result = re.sub(r"\s+([,.:;!?])", r"\1", result)
        if new_result != result:
            changes.append("Removed misplaced whitespace before punctuation")
            result = new_result

        # Collapse multiple exclamation marks to single: "hello!!" -> "hello!"
        new_result = re.sub(r"!{2,}", "!", result)
        if new_result != result:
            changes.append("Normalized repeated exclamation marks")
            result = new_result

        # Collapse multiple question marks: "really???" -> "really?"
        new_result = re.sub(r"\?{2,}", "?", result)
        if new_result != result:
            changes.append("Normalized repeated question marks")
            result = new_result

        # Space after comma if immediately followed by letter: "apple,banana" -> "apple, banana"
        new_result = re.sub(r"([a-zA-Z]),([a-zA-Z])", r"\1, \2", result)
        if new_result != result:
            changes.append("Added spacing after commas")
            result = new_result

        return result, changes

    def _fix_contractions(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        result = text

        # Standard unambiguous contractions
        for word, expansion in self.contractions.items():
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)

            def _repl(match: re.Match[str], exp: str = expansion) -> str:
                matched = match.group(0)
                if matched.istitle():
                    return exp.capitalize()
                if matched.isupper():
                    return exp.upper()
                return exp

            new_result, count = pattern.subn(_repl, result)
            if count > 0:
                changes.append(f"Corrected contraction: '{word}' -> '{expansion}' ({count}x)")
                result = new_result

        # Unambiguous "id" -> "I'd" when followed by verbs/modals
        # Avoids converting "user id" or "id column"
        id_pattern = re.compile(
            r"\b[iI]d\b(?=\s+(?:like|love|prefer|rather|want|need|suggest|recommend|say|think|appreciate|be|have)\b)",
            re.IGNORECASE,
        )
        new_result, id_count = id_pattern.subn("I'd", result)
        if id_count > 0:
            changes.append(f"Corrected 'id' -> 'I'd' ({id_count}x)")
            result = new_result

        # Expand "idk" -> "I don't know"
        idk_pattern = re.compile(r"\b[iI]dk\b")
        new_result, idk_count = idk_pattern.subn("I don't know", result)
        if idk_count > 0:
            changes.append(f"Expanded 'idk' -> 'I don't know' ({idk_count}x)")
            result = new_result

        return result, changes

    def _fix_typos(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        result = text

        for typo, fix in self.typos.items():
            pattern = re.compile(rf"\b{re.escape(typo)}\b", re.IGNORECASE)

            def _repl(match: re.Match[str], f: str = fix) -> str:
                orig = match.group(0)
                return _match_case(orig, f)

            new_result, count = pattern.subn(_repl, result)
            if count > 0:
                changes.append(f"Corrected typo: '{typo}' -> '{fix}' ({count}x)")
                result = new_result

        return result, changes

    def _fix_tech_casing(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        result = text

        for lower_term, proper_casing in self.tech_casing.items():
            # Match only whole words matching lower_term (case-insensitive)
            # but only replace if it's currently lowercase or wrongly cased
            pattern = re.compile(rf"\b{re.escape(lower_term)}\b", re.IGNORECASE)

            def _repl(match: re.Match[str], target: str = proper_casing) -> str:
                return target

            matches = list(pattern.finditer(result))
            needs_update = any(m.group(0) != proper_casing for m in matches)
            if needs_update:
                result = pattern.sub(_repl, result)
                changes.append(f"Standardized casing: '{lower_term}' -> '{proper_casing}'")

        return result, changes

    def _fix_capitalization(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        result = text

        # Standalone lowercase 'i' -> 'I'
        new_result, count_i = re.subn(r"\bi\b", "I", result)
        if count_i > 0:
            changes.append(f"Capitalized standalone 'i' -> 'I' ({count_i}x)")
            result = new_result

        # Standalone 'i'll' -> 'I'll'
        new_result, count_ill = re.subn(r"\bi'll\b", "I'll", result)
        if count_ill > 0:
            changes.append(f"Capitalized 'i'll' -> 'I'll' ({count_ill}x)")
            result = new_result

        # Capitalize first character of text or line
        def _cap_start(match: re.Match[str]) -> str:
            prefix = match.group(1)
            char = match.group(2)
            return f"{prefix}{char.upper()}"

        new_result = re.sub(r"(^|[\r\n]+)([a-z])", _cap_start, result)
        if new_result != result:
            changes.append("Capitalized start of lines")
            result = new_result

        # Capitalize first character after sentence ending punctuation (.!?)
        def _cap_sentence(match: re.Match[str]) -> str:
            punc = match.group(1)
            char = match.group(2)
            return f"{punc}{char.upper()}"

        new_result = re.sub(r"([.!?]\s+)([a-z])", _cap_sentence, result)
        if new_result != result:
            changes.append("Capitalized start of sentences")
            result = new_result

        return result, changes

    def _ensure_terminal_punctuation(self, text: str) -> tuple[str, list[str]]:
        changes: list[str] = []
        lines = text.split("\n")
        updated_lines: list[str] = []

        for line in lines:
            trimmed = line.rstrip()
            # If line is non-empty, doesn't end with punctuation or code markup, and looks like a sentence
            if trimmed and not trimmed.endswith((".", "!", "?", ":", ";", "`", "-", "*", ">", "{", "}", "[", "]")):
                # Check if it ends in word character
                if re.search(r"\w$", trimmed):
                    trimmed += "."
                    changes.append("Added terminal punctuation")
            updated_lines.append(trimmed)

        result = "\n".join(updated_lines)
        return result, changes


def clean_text(text: str) -> CleanedText:
    """Convenience helper to clean text with default cleaner settings."""
    return TextCleaner().clean(text)
