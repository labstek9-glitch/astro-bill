from __future__ import annotations

import asyncio
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from astrobill.config import Settings
from astrobill.kalshi import KalshiPublic
from astrobill.model import DEFAULT_VOL, Proposal, fair_yes, propose
from astrobill.series import asset_from_series
from astrobill.spot import SpotFeed


def _f(v: Any, default: float = float("nan")) -> float:
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _secs_left(close_time: str | None) -> int:
    if not close_time:
        return 0
    try:
        close = datetime.fromisoformat(close_time.replace("Z", "+00:00"))
        return int((close - datetime.now(timezone.utc)).total_seconds())
    except ValueError:
        return 0


@dataclass
class Row:
    asset: str
    series: str
    ticker: str
    strike: float
    secs_left: int
    spot: float
    spot_src: str
    vol: float
    fair: float
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    mid: float
    edge: float
    action: str
    limit: float
    contracts: float
    fee: float
    rationale: str
    volume: float
    error: str = ""


class Engine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.kalshi = KalshiPublic(timeout=settings.request_timeout_seconds)
        self.spot = SpotFeed(timeout=settings.request_timeout_seconds)
        self.series: list[str] = list(settings.series)
        self.spot_cache: dict[str, tuple[float, str]] = {}

    async def close(self) -> None:
        await self.kalshi.aclose()
        await self.spot.aclose()

    async def resolve_series(self) -> list[str]:
        seed = set(self.settings.series)
        if self.settings.auto_discover:
            try:
                seed |= set(await self.kalshi.discover_crypto_15m())
            except Exception:
                pass
        skip = {"KXCRYPTOCOMP15M", "KXCRYPTOLEAD15M"}
        self.series = sorted(s for s in seed if s not in skip)
        return self.series

    async def scan_once(self) -> list[Row]:
        if not self.series:
            await self.resolve_series()
        sem = asyncio.Semaphore(self.settings.max_concurrency)

        async def one(series: str) -> list[Row]:
            async with sem:
                return await self._scan_series(series)

        batches = await asyncio.gather(*[one(s) for s in self.series], return_exceptions=True)
        rows: list[Row] = []
        for series, batch in zip(self.series, batches):
            if isinstance(batch, Exception):
                rows.append(Row(asset_from_series(series), series, "", float("nan"), 0, float("nan"), "", 0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), 0, "SIT", 0, 0, 0, "", 0, str(batch)[:160]))
            else:
                rows.extend(batch)
        rows.sort(key=lambda r: (0 if r.action != "SIT" else 1, -abs(r.edge or 0), r.asset))
        return rows

    async def _scan_series(self, series: str) -> list[Row]:
        asset = asset_from_series(series)
        markets = await self.kalshi.open_markets(series)
        if not markets:
            return []
        try:
            spot, src = await self.spot.price(asset)
            self.spot_cache[asset] = (spot, src)
        except Exception as exc:
            cached = self.spot_cache.get(asset)
            if cached:
                spot, src = cached
            else:
                spot, src = float("nan"), f"spot-miss:{exc}"[:40]
        vol = DEFAULT_VOL.get(asset, 0.90)
        out: list[Row] = []
        for m in markets:
            ticker = m.get("ticker") or ""
            strike = _f(m.get("floor_strike"))
            secs = _secs_left(m.get("close_time"))
            yes_bid = _f(m.get("yes_bid_dollars"))
            yes_ask = _f(m.get("yes_ask_dollars"))
            no_bid = _f(m.get("no_bid_dollars"))
            no_ask = _f(m.get("no_ask_dollars"))
            if math.isnan(yes_ask) and not math.isnan(no_bid):
                yes_ask = 1.0 - no_bid
            if math.isnan(no_ask) and not math.isnan(yes_bid):
                no_ask = 1.0 - yes_bid
            mid = (yes_bid + yes_ask) / 2.0 if not math.isnan(yes_bid) and not math.isnan(yes_ask) else float("nan")
            fair = fair_yes(spot, strike, float(max(secs, 0)), vol)
            prop: Proposal = propose(
                fair=fair, yes_bid=yes_bid, yes_ask=yes_ask, no_bid=no_bid, no_ask=no_ask,
                contracts=self.settings.default_contracts, max_notional=self.settings.max_notional_usd,
                min_edge=self.settings.min_edge_after_fee, seconds_left=secs,
                sit_below=self.settings.sit_if_seconds_left_below,
            )
            out.append(Row(asset, series, ticker, strike, secs, spot, src, vol, fair, yes_bid, yes_ask, no_bid, no_ask, mid, prop.edge, prop.action, prop.limit, prop.contracts, prop.fee, prop.rationale, _f(m.get("volume_fp"), 0.0)))
        return out


def persist(rows: list[Row], settings: Settings) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    payload = {"ts": stamp, "disclaimer": "Analysis only. No orders are placed. Not financial advice.", "rows": [asdict(r) for r in rows]}
    if settings.write_web_snapshot:
        path = Path(settings.web_snapshot_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "scans.jsonl").open("a") as f:
        f.write(json.dumps(payload) + "\n")
