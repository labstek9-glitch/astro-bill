from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class SpotConfig(BaseModel):
    primary: str = "coinbase"
    fallback: str = "binance"


class Settings(BaseModel):
    poll_seconds: float = 2.0
    request_timeout_seconds: float = 8.0
    max_concurrency: int = 8
    default_contracts: float = 10.0
    max_notional_usd: float = 25.0
    min_edge_after_fee: float = 0.01
    sit_if_seconds_left_below: int = 8
    log_dir: str = "logs"
    write_web_snapshot: bool = True
    web_snapshot_path: str = "web/latest.json"
    series: list[str] = Field(default_factory=list)
    spot: SpotConfig = Field(default_factory=SpotConfig)
    auto_discover: bool = True

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Settings":
        candidates = []
        if path:
            candidates.append(Path(path))
        candidates.extend(
            [
                Path("config.yaml"),
                Path(__file__).resolve().parent.parent / "config.yaml",
            ]
        )
        data: dict[str, Any] = {}
        for p in candidates:
            if p.exists():
                data = yaml.safe_load(p.read_text()) or {}
                break
        return cls.model_validate(data)
