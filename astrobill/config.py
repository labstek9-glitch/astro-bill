from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from astrobill.series import ASSET_TO_SERIES


class SpotConfig(BaseModel):
    primary: str = "coinbase"
    fallback: str = "binance"


class Settings(BaseModel):
    poll_seconds: float = Field(default=2.0, ge=1)
    request_timeout_seconds: float = Field(default=1.5, gt=0, le=30)
    max_concurrency: int = Field(default=16, ge=1, le=64)
    default_contracts: float = Field(default=10, ge=1, le=100000)
    max_notional_usd: float = Field(default=25, ge=0, le=100000)
    min_edge_after_fee: float = Field(default=0.01, ge=0, le=1)
    sit_if_seconds_left_below: int = 8
    log_dir: str = "logs"
    write_web_snapshot: bool = True
    web_snapshot_path: str = "web/latest.json"
    series: list[str] = Field(default_factory=lambda: list(ASSET_TO_SERIES.values()))
    spot: SpotConfig = Field(default_factory=SpotConfig)
    auto_discover: bool = True

    max_spread: float = Field(default=0.06, ge=0, le=1)
    max_data_age_seconds: float = Field(default=3, gt=0, le=10)
    market_refresh_seconds: float = Field(default=15, ge=1)
    discovery_refresh_seconds: float = Field(default=300, ge=10)
    realized_vol: bool = True
    cf_average_proxy: bool = True
    cross_venue_check: bool = True
    vol_clamps: dict[str, tuple[float, float]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_clamps(self) -> "Settings":
        if any(not (0 < lo <= hi < 100) for lo, hi in self.vol_clamps.values()):
            raise ValueError("vol_clamps require 0 < lower <= upper < 100")
        return self

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
