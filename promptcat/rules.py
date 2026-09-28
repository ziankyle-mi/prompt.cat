"""Deterministic domain and technology detection rules for promptcat."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from promptcat.models import DetectedRule


@dataclass
class DomainRule:
    """Configurable domain rule definition."""

    name: str
    keywords: list[str]
    constraints: list[str]
    patterns: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)

    def match(self, text: str) -> tuple[bool, list[str]]:
        """Check if rule matches the text, returning (is_match, matched_terms)."""
        matched_terms: list[str] = []
        lower_text = text.lower()

        # Check keyword matches using word boundaries
        for kw in self.keywords:
            pattern = rf"\b{re.escape(kw.lower())}\b"
            if re.search(pattern, lower_text):
                matched_terms.append(kw)

        # Check regex patterns if specified
        for pat in self.patterns:
            if re.search(pat, text, re.IGNORECASE):
                matched_terms.append(f"pattern({pat})")

        return (len(matched_terms) > 0, matched_terms)


# Built-in Domain Rules as defined in the Promptcat specification
DEFAULT_RULES: list[DomainRule] = [
    DomainRule(
        name="Authentication",
        keywords=[
            "auth",
            "authentication",
            "login",
            "logout",
            "jwt",
            "session",
            "password",
            "credential",
            "oauth",
            "security",
            "sso",
            "2fa",
            "mfa",
            "token",
        ],
        constraints=[
            "Protect credentials and secrets.",
            "Define authentication flow.",
            "Clarify session/token lifecycle.",
            "Handle unauthorized and forbidden requests.",
            "Do not expose sensitive information.",
        ],
    ),
    DomainRule(
        name="Database",
        keywords=[
            "database",
            "db",
            "sql",
            "sqlite",
            "postgres",
            "postgresql",
            "mysql",
            "mongodb",
            "schema",
            "migration",
            "orm",
            "prisma",
            "sqlalchemy",
            "redis",
        ],
        constraints=[
            "Define the data schema explicitly.",
            "Identify keys and relationships.",
            "Clarify persistence behavior.",
            "Explain migrations where applicable.",
        ],
        technologies=["PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Prisma", "SQLAlchemy"],
    ),
    DomainRule(
        name="API",
        keywords=[
            "api",
            "rest",
            "endpoint",
            "http",
            "request",
            "response",
            "backend",
            "server",
            "graphql",
            "grpc",
            "webhook",
        ],
        constraints=[
            "Define API contracts.",
            "Use appropriate HTTP methods and status codes.",
            "Use structured error responses.",
            "Clarify request and response formats.",
        ],
    ),
    DomainRule(
        name="Frontend",
        keywords=[
            "ui",
            "frontend",
            "component",
            "css",
            "html",
            "react",
            "vue",
            "angular",
            "interface",
            "responsive",
            "tailwind",
            "svelte",
            "nextjs",
            "client",
        ],
        constraints=[
            "Separate UI concerns appropriately.",
            "Handle loading and error states.",
            "Consider responsive behavior.",
            "Maintain clear component boundaries.",
        ],
        technologies=["React", "Vue", "Angular", "Svelte", "Next.js", "Tailwind CSS"],
    ),
    DomainRule(
        name="Testing",
        keywords=[
            "test",
            "testing",
            "unit test",
            "integration",
            "pytest",
            "jest",
            "mocha",
            "cypress",
            "playwright",
            "tdd",
        ],
        constraints=[
            "Include relevant test cases.",
            "Cover important edge cases.",
            "Explain how the implementation can be verified.",
        ],
        technologies=["Pytest", "Jest", "Playwright", "Cypress"],
    ),
    DomainRule(
        name="Performance",
        keywords=[
            "performance",
            "optimize",
            "optimization",
            "latency",
            "cache",
            "caching",
            "throughput",
            "concurrency",
            "scalable",
            "profiling",
        ],
        constraints=[
            "Profile and benchmark before optimizing.",
            "Minimize memory and CPU overhead.",
            "Ensure algorithms and queries scale cleanly with dataset size.",
        ],
    ),
]

# Known technology keywords to auto-detect technology stack
TECH_SIGNATURES: dict[str, str] = {
    "react": "React",
    "vue": "Vue.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "tailwind": "Tailwind CSS",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "express": "Express.js",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "node": "Node.js",
    "nodejs": "Node.js",
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "rust": "Rust",
    "go": "Go",
    "golang": "Go",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "jwt": "JWT",
    "pytest": "Pytest",
    "jest": "Jest",
}


class RuleRegistry:
    """Registry of rules for domain detection and constraint aggregation."""

    def __init__(self, rules: list[DomainRule] | None = None) -> None:
        self.rules: list[DomainRule] = []
        initial_rules = rules if rules is not None else DEFAULT_RULES
        for r in initial_rules:
            self.register(r)

    def register(self, rule: DomainRule) -> None:
        """Register a new domain rule or replace an existing one by name."""
        self.rules = [r for r in self.rules if r.name.lower() != rule.name.lower()]
        self.rules.append(rule)

    def analyze(self, text: str) -> list[DetectedRule]:
        """Analyze text and return all matching DetectedRule instances."""
        detected: list[DetectedRule] = []
        for rule in self.rules:
            is_match, terms = rule.match(text)
            if is_match:
                detected.append(
                    DetectedRule(
                        domain=rule.name,
                        matched_keywords=terms,
                        constraints=list(rule.constraints),
                    )
                )
        return detected

    def detect_technologies(self, text: str) -> list[str]:
        """Extract mentioned technologies deterministically from text."""
        detected: list[str] = []
        lower_text = text.lower()
        seen = set()

        for kw, canonical in TECH_SIGNATURES.items():
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, lower_text):
                if canonical not in seen:
                    seen.add(canonical)
                    detected.append(canonical)

        return detected


def analyze_rules(text: str) -> list[DetectedRule]:
    """Convenience helper to analyze text with default rule registry."""
    return RuleRegistry().analyze(text)
