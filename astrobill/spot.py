from __future__ import annotations

import httpx
from astrobill.series import BINANCE_SYMBOL, COINBASE_PRODUCT


class SpotFeed:
    def __init__(self, timeout: float = 8.0) -> None:
        self.client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self.client.aclose()

    async def price(self, asset: str) -> tuple[float, str]:
        for name, fn in (("coinbase", self._coinbase), ("coinbase_v2", self._coinbase_v2), ("binance", self._binance), ("kraken", self._kraken)):
            try:
                px = await fn(asset)
                if px:
                    return px, name
            except Exception:
                continue
        raise RuntimeError(f"no spot for {asset}")

    async def _coinbase(self, asset: str) -> float | None:
        product = COINBASE_PRODUCT.get(asset)
        if not product:
            return None
        r = await self.client.get(f"https://api.exchange.coinbase.com/products/{product}/ticker")
        if r.status_code != 200:
            return None
        return float(r.json()["price"])

    async def _coinbase_v2(self, asset: str) -> float | None:
        r = await self.client.get(f"https://api.coinbase.com/v2/prices/{asset}-USD/spot")
        if r.status_code != 200:
            return None
        amt = (r.json().get("data") or {}).get("amount")
        return float(amt) if amt else None

    async def _kraken(self, asset: str) -> float | None:
        pairs = {"BTC": "XBTUSD", "ETH": "ETHUSD", "SOL": "SOLUSD", "XRP": "XRPUSD", "DOGE": "DOGEUSD", "ADA": "ADAUSD", "BCH": "BCHUSD", "NEAR": "NEARUSD"}
        pair = pairs.get(asset)
        if not pair:
            return None
        r = await self.client.get("https://api.kraken.com/0/public/Ticker", params={"pair": pair})
        if r.status_code != 200:
            return None
        result = r.json().get("result") or {}
        if not result:
            return None
        last = next(iter(result.values())).get("c", [None])[0]
        return float(last) if last else None

    async def _binance(self, asset: str) -> float | None:
        symbol = BINANCE_SYMBOL.get(asset)
        if not symbol:
            return None
        r = await self.client.get("https://api.binance.com/api/v3/ticker/price", params={"symbol": symbol})
        if r.status_code != 200:
            return None
        return float(r.json()["price"])
