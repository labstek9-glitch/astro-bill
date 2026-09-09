from __future__ import annotations

from typing import Any
import httpx

BASE = "https://external-api.kalshi.com/trade-api/v2"


class KalshiPublic:
    def __init__(self, timeout: float = 8.0) -> None:
        self.client = httpx.AsyncClient(base_url=BASE, timeout=timeout, headers={"User-Agent": "astro-bill/0.1"})

    async def aclose(self) -> None:
        await self.client.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        r = await self.client.get(path, params=params)
        r.raise_for_status()
        return r.json()

    async def discover_crypto_15m(self) -> list[str]:
        found: list[str] = []
        cursor = None
        for _ in range(20):
            params: dict[str, Any] = {"limit": 200}
            if cursor:
                params["cursor"] = cursor
            data = await self.get("/series", params=params)
            rows = data.get("series") or data.get("series_list") or []
            for s in rows:
                ticker = s.get("ticker") or s.get("series_ticker") or ""
                cat = str(s.get("category") or "").lower()
                if ticker.endswith("15M") and ticker.startswith("KX") and "crypto" in cat:
                    found.append(ticker)
            cursor = data.get("cursor")
            if not cursor or not rows:
                break
        return sorted(set(found))

    async def open_markets(self, series_ticker: str) -> list[dict[str, Any]]:
        data = await self.get("/markets", params={"series_ticker": series_ticker, "status": "open", "limit": 20})
        return data.get("markets") or []

    async def orderbook(self, market_ticker: str) -> dict[str, Any]:
        return await self.get(f"/markets/{market_ticker}/orderbook")
