"""Tests for promptcat local history."""

from unittest.mock import patch
from pathlib import Path
import pytest
from promptcat.history import clear_history, get_history, get_last_history, list_history, save_history


@pytest.fixture(autouse=True)
def mock_db_path(tmp_path: Path):
    test_db = tmp_path / "test_history.db"
    with patch("promptcat.history._get_db_path", return_value=test_db):
        yield test_db


def test_history_lifecycle():
    assert list_history() == []

    # Save prompt
    entry_id = save_history(
        mode="feature",
        format_type="xml",
        raw_input="build a login page",
        cleaned_text="Build a login page.",
        prompt_text="<role>Senior</role>",
        tokens=120,
        stack=["React", "PostgreSQL"],
    )
    assert entry_id == 1

    # List entries
    entries = list_history()
    assert len(entries) == 1
    assert entries[0]["mode"] == "feature"
    assert entries[0]["tokens"] == 120
    assert "React" in entries[0]["stack"]

    # Get single entry
    item = get_history(1)
    assert item is not None
    assert item["raw_input"] == "build a login page"

    # Get last entry
    last = get_last_history()
    assert last is not None
    assert last["id"] == 1

    # Clear history
    deleted = clear_history()
    assert deleted == 1
    assert list_history() == []
