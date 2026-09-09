from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from astrobill.config import Settings
from astrobill.journal import Journal
from astrobill.storage import atomic_json, clean

if TYPE_CHECKING:
    from astrobill.engine import Row


def persist(rows: list[Row], settings: Settings, *, session_start: float | None = None,
            discovery_error: str = "") -> dict[str, Any]:
    stamp = time.time()
    stats = Journal(settings.log_dir).stats(session_start, settings.min_edge_after_fee)
    calibration = stats["assets"]
    for row in rows:
        if row.asset and row.asset not in calibration:
            calibration[row.asset] = {"proposed": 0, "taken": 0, "wins": 0, "losses": 0,
                                     "n": 0, "hit_rate": None, "brier": None, "brier_n": 0,
                                     "last50": [], "last50_hit_rate": None,
                                     "suggested_min_edge": settings.min_edge_after_fee,
                                     "warning": "SAMPLE TOO SMALL"}
    atomic_json(Path(settings.log_dir)/"calibrations.json", calibration)
    payload = clean({"ts": datetime.fromtimestamp(stamp, timezone.utc).isoformat(), "scan_ts": stamp,
                     "disclaimer": "ANALYSIS ONLY — YOU CLICK KALSHI", "rows": [asdict(r) for r in rows],
                     "stats": stats, "discovery_error": discovery_error})
    if settings.write_web_snapshot:
        atomic_json(Path(settings.web_snapshot_path), payload)
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir/"scans.jsonl").open("a") as f:
        f.write(json.dumps(payload, allow_nan=False)+"\n")
    return payload
