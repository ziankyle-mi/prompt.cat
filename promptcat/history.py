"""Offline local prompt history storage using SQLite."""

from __future__ import annotations

import datetime
import json
import sqlite3
from pathlib import Path
from typing import Any


def _get_db_path() -> Path:
    """Return local promptcat history database path."""
    app_dir = Path.home() / ".promptcat"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / "history.db"


def _init_db(conn: sqlite3.Connection) -> None:
    """Initialize history schema if it doesn't already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            mode TEXT NOT NULL,
            format TEXT NOT NULL,
            raw_input TEXT NOT NULL,
            cleaned_text TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            tokens INTEGER NOT NULL,
            stack TEXT NOT NULL
        )
        """
    )
    conn.commit()


def save_history(
    mode: str,
    format_type: str,
    raw_input: str,
    cleaned_text: str,
    prompt_text: str,
    tokens: int,
    stack: list[str],
) -> int:
    """Save a compiled prompt to local SQLite history, returning entry ID."""
    db_path = _get_db_path()
    with sqlite3.connect(db_path) as conn:
        _init_db(conn)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO prompt_history (
                created_at, mode, format, raw_input, cleaned_text, prompt_text, tokens, stack
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                mode,
                format_type,
                raw_input,
                cleaned_text,
                prompt_text,
                tokens,
                json.dumps(stack),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid or 0)


def list_history(limit: int = 10) -> list[dict[str, Any]]:
    """Retrieve recent prompt history entries ordered newest first."""
    db_path = _get_db_path()
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as conn:
        _init_db(conn)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, created_at, mode, format, raw_input, cleaned_text, prompt_text, tokens, stack
            FROM prompt_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append(
                {
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "mode": r["mode"],
                    "format": r["format"],
                    "raw_input": r["raw_input"],
                    "cleaned_text": r["cleaned_text"],
                    "prompt_text": r["prompt_text"],
                    "tokens": r["tokens"],
                    "stack": json.loads(r["stack"]) if r["stack"] else [],
                }
            )
        return result


def get_history(entry_id: int) -> dict[str, Any] | None:
    """Fetch a specific prompt history entry by ID."""
    db_path = _get_db_path()
    if not db_path.exists():
        return None

    with sqlite3.connect(db_path) as conn:
        _init_db(conn)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, created_at, mode, format, raw_input, cleaned_text, prompt_text, tokens, stack
            FROM prompt_history
            WHERE id = ?
            """,
            (entry_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "mode": row["mode"],
            "format": row["format"],
            "raw_input": row["raw_input"],
            "cleaned_text": row["cleaned_text"],
            "prompt_text": row["prompt_text"],
            "tokens": row["tokens"],
            "stack": json.loads(row["stack"]) if row["stack"] else [],
        }


def get_last_history() -> dict[str, Any] | None:
    """Fetch the most recently compiled prompt from history."""
    entries = list_history(limit=1)
    return entries[0] if entries else None


def clear_history() -> int:
    """Clear all records from local history and return count of deleted items."""
    db_path = _get_db_path()
    if not db_path.exists():
        return 0

    with sqlite3.connect(db_path) as conn:
        _init_db(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prompt_history")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM prompt_history")
        conn.commit()
        return int(count)
