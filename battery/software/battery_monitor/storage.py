"""Persistent state and history.

The coulomb-counter state is a small JSON file rewritten on a timer, not on
every sample. The write is atomic (temp file, fsync, rename) so a power cut
leaves either the previous state or the new one.

History is append-only SQLite. The chip registers are not the long-term
record: they reset when the INA228 supply drops.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from .accounting import fresh_state


def atomic_write_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with open(temporary, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


class StateStore:
    def __init__(self, path: str | Path, initial_soc_percent: float | None):
        self.path = Path(path)
        self.initial_soc_percent = initial_soc_percent
        self.state = fresh_state(initial_soc_percent)
        self.loaded_from_disk = False

    def load(self) -> dict:
        if self.path.is_file():
            self.state = load_json(self.path)
            self.state.setdefault("ampere_hours_out", 0.0)
            self.state.setdefault("watt_hours_out", 0.0)
            self.state.setdefault("soc_anchor_percent", None)
            self.state.setdefault("ah_at_anchor", 0.0)
            # Wall-clock downtime is not integrated. The flag tells the UI.
            self.state["power_loss_gap"] = True
            self.loaded_from_disk = True
        else:
            self.state = fresh_state(self.initial_soc_percent)
            self.state["power_loss_gap"] = False
            self.loaded_from_disk = False
        return self.state

    def save(self) -> None:
        atomic_write_json(self.path, self.state)


class HistoryDB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY,
                unix_time REAL NOT NULL,
                voltage_v REAL,
                current_a REAL,
                power_w REAL,
                soc_percent REAL,
                capacity_ah REAL,
                energy_wh REAL,
                ampere_hours_out REAL,
                status TEXT,
                temperature_c REAL,
                faults TEXT
            )
            """
        )
        self._db.commit()

    def insert(self, row: dict) -> None:
        self._db.execute(
            """
            INSERT INTO samples (
                unix_time, voltage_v, current_a, power_w, soc_percent,
                capacity_ah, energy_wh, ampere_hours_out, status,
                temperature_c, faults
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("updated_unix"),
                row.get("voltage_v"),
                row.get("current_a"),
                row.get("power_w"),
                row.get("soc_percent"),
                row.get("nominal_capacity_ah"),
                row.get("energy_wh"),
                row.get("ampere_hours_out"),
                row.get("status"),
                row.get("temperature_c"),
                ",".join(row.get("faults") or []),
            ),
        )
        self._db.commit()

    def count(self) -> int:
        cursor = self._db.execute("SELECT COUNT(*) FROM samples")
        return int(cursor.fetchone()[0])

    def close(self) -> None:
        self._db.close()
