from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "var" / "intake_demo.sqlite3"


def _today_prefix() -> str:
    return datetime.now(timezone.utc).date().isoformat()


class SqliteIntakeStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    patient TEXT NOT NULL,
                    age_or_birth_year TEXT NOT NULL,
                    main_symptom TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    red_flag_status TEXT NOT NULL,
                    red_flags_json TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    suggested_specialty TEXT NOT NULL,
                    preferred_hospital TEXT NOT NULL,
                    preferred_time_detail TEXT NOT NULL,
                    booking_status TEXT NOT NULL,
                    case_status TEXT NOT NULL,
                    doctor_summary TEXT NOT NULL,
                    raw_case_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_case_snapshot(self, case: Any, patient: Any, booking_status: str = "none") -> None:
        case_data = case.model_dump()
        patient_data = patient.model_dump()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cases (
                    case_id, session_id, patient_id, patient, age_or_birth_year,
                    main_symptom, duration, severity, red_flag_status, red_flags_json,
                    priority, suggested_specialty, preferred_hospital, preferred_time_detail,
                    booking_status, case_status, doctor_summary, raw_case_json,
                    updated_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    patient=excluded.patient,
                    age_or_birth_year=excluded.age_or_birth_year,
                    main_symptom=excluded.main_symptom,
                    duration=excluded.duration,
                    severity=excluded.severity,
                    red_flag_status=excluded.red_flag_status,
                    red_flags_json=excluded.red_flags_json,
                    priority=excluded.priority,
                    suggested_specialty=excluded.suggested_specialty,
                    preferred_hospital=excluded.preferred_hospital,
                    preferred_time_detail=excluded.preferred_time_detail,
                    booking_status=excluded.booking_status,
                    case_status=excluded.case_status,
                    doctor_summary=excluded.doctor_summary,
                    raw_case_json=excluded.raw_case_json,
                    updated_at=excluded.updated_at
                """,
                (
                    case.case_id,
                    case.session_id,
                    case.patient_id,
                    patient_data.get("relationship_to_customer", "unknown"),
                    patient_data.get("age_or_birth_year", "unknown"),
                    case_data.get("main_symptom", "unknown"),
                    case_data.get("duration", "unknown"),
                    case_data.get("severity", "unknown"),
                    case_data.get("red_flag_status", "unknown"),
                    json.dumps(case_data.get("red_flags", []), ensure_ascii=False),
                    case_data.get("priority", "medium"),
                    case_data.get("suggested_specialty", "unknown"),
                    case_data.get("preferred_hospital", "unknown"),
                    case_data.get("preferred_time_detail", "unknown"),
                    booking_status,
                    case_data.get("case_status", "new"),
                    case_data.get("doctor_summary", ""),
                    json.dumps(case_data, ensure_ascii=False),
                    case_data.get("updated_at", ""),
                    case_data.get("created_at", ""),
                ),
            )

    def append_log(self, case_id: str, event: str, detail: str, created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs (case_id, event, detail, created_at) VALUES (?, ?, ?, ?)",
                (case_id, event, detail, created_at),
            )
        self._append_log_file(case_id, event, detail, created_at)

    def _append_log_file(self, case_id: str, event: str, detail: str, created_at: str) -> None:
        safe_case_id = "".join(ch for ch in case_id if ch.isalnum() or ch in {"_", "-"})
        log_dir = self.db_path.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{safe_case_id}.log"
        with log_path.open("a", encoding="utf-8") as file:
            file.write(f"[{created_at}] {event}: {detail}\n")

    def list_doctor_case_rows(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT case_id, patient, age_or_birth_year, main_symptom, duration, severity, red_flag_status,
                       priority, suggested_specialty, preferred_hospital, preferred_time_detail,
                       booking_status, created_at, doctor_summary
                FROM cases
                ORDER BY updated_at DESC, created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def list_logs(self, case_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT case_id, event, detail, created_at
                FROM audit_logs
                WHERE case_id = ?
                ORDER BY id ASC
                """,
                (case_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def dashboard_stats(self) -> dict:
        today = _today_prefix()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT priority, red_flag_status, booking_status, suggested_specialty
                FROM cases
                WHERE substr(created_at, 1, 10) = ?
                """,
                (today,),
            ).fetchall()

        total = len(rows)
        red_flags = sum(1 for row in rows if row["red_flag_status"] == "confirmed")
        booking_drafts = sum(1 for row in rows if row["booking_status"] == "draft")
        priority_counts: dict[str, int] = {}
        specialty_counts: dict[str, int] = {}
        for row in rows:
            priority_counts[row["priority"]] = priority_counts.get(row["priority"], 0) + 1
            specialty_counts[row["suggested_specialty"]] = specialty_counts.get(row["suggested_specialty"], 0) + 1

        return {
            "date": today,
            "total_conversations": total,
            "red_flag_cases": red_flags,
            "booking_drafts": booking_drafts,
            "priority_counts": priority_counts,
            "specialty_counts": specialty_counts,
        }
