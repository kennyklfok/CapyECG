import json
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "capyecg.sqlite3"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ecg_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rhythm_label TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                source_type TEXT NOT NULL,
                explanation TEXT NOT NULL,
                key_features_json TEXT NOT NULL,
                waveform_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def row_to_case(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "rhythm_label": row["rhythm_label"],
        "difficulty": row["difficulty"],
        "source_type": row["source_type"],
        "explanation": row["explanation"],
        "key_features": json.loads(row["key_features_json"]),
        "waveform": json.loads(row["waveform_json"]),
    }


def insert_case(case: dict[str, Any]) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO ecg_cases (
                rhythm_label,
                difficulty,
                source_type,
                explanation,
                key_features_json,
                waveform_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                case["rhythm_label"],
                case["difficulty"],
                case["source_type"],
                case["explanation"],
                json.dumps(case["key_features"]),
                json.dumps(case["waveform"]),
            ),
        )
        return int(cursor.lastrowid)


def recent_rhythm_labels(difficulty: str, limit: int = 4) -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT rhythm_label
            FROM ecg_cases
            WHERE difficulty = ?
                AND source_type IN ('groq-generated', 'groq-cache', 'groq-fallback', 'local-fallback')
            ORDER BY id DESC
            LIMIT ?
            """,
            (difficulty, limit),
        ).fetchall()
    return [row["rhythm_label"] for row in rows]
