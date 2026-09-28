"""Tests for promptcat domain detection and rules engine."""

import pytest
from promptcat.rules import DomainRule, RuleRegistry, analyze_rules


class TestRules:
    @pytest.fixture
    def registry(self):
        return RuleRegistry()

    def test_authentication_detection(self, registry):
        text = "Implement user login with session token and password reset."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "Authentication" in domains

        auth_rule = next(r for r in rules if r.domain == "Authentication")
        assert "login" in auth_rule.matched_keywords
        assert any("Protect credentials" in c for c in auth_rule.constraints)

    def test_database_detection(self, registry):
        text = "Create a database schema for Postgres with migration scripts."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "Database" in domains

        db_rule = next(r for r in rules if r.domain == "Database")
        assert any("Define the data schema explicitly" in c for c in db_rule.constraints)

    def test_api_detection(self, registry):
        text = "Create a REST API endpoint that returns JSON response."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "API" in domains

    def test_frontend_detection(self, registry):
        text = "Design a responsive UI component using React and CSS."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "Frontend" in domains

    def test_testing_detection(self, registry):
        text = "Write unit tests using pytest to verify the calculator."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "Testing" in domains

    def test_multi_domain_detection(self, registry):
        text = "Build a JWT login API using PostgreSQL and React."
        rules = registry.analyze(text)
        domains = {r.domain for r in rules}
        assert "Authentication" in domains
        assert "API" in domains
        assert "Database" in domains
        assert "Frontend" in domains

    def test_technology_extraction(self, registry):
        text = "Build a FastAPI backend with PostgreSQL and React frontend."
        techs = registry.detect_technologies(text)
        assert "FastAPI" in techs
        assert "PostgreSQL" in techs
        assert "React" in techs

    def test_extensibility_custom_rule(self, registry):
        custom_rule = DomainRule(
            name="Blockchain",
            keywords=["solidity", "smart contract", "ethereum", "web3"],
            constraints=["Audit smart contract for reentrancy bugs.", "Minimize gas consumption."],
        )
        registry.register(custom_rule)

        text = "Write a Solidity smart contract for token staking."
        rules = registry.analyze(text)
        domains = [r.domain for r in rules]
        assert "Blockchain" in domains

        matched = next(r for r in rules if r.domain == "Blockchain")
        assert "solidity" in matched.matched_keywords
        assert any("reentrancy" in c for c in matched.constraints)
