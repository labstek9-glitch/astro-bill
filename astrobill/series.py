from __future__ import annotations

ASSET_TO_SERIES = {
    "BTC": "KXBTC15M",
    "ETH": "KXETH15M",
    "SOL": "KXSOL15M",
    "XRP": "KXXRP15M",
    "DOGE": "KXDOGE15M",
    "BNB": "KXBNB15M",
    "HYPE": "KXHYPE15M",
    "ADA": "KXADA15M",
    "BCH": "KXBCH15M",
    "NEAR": "KXNEAR15M",
    "TON": "KXTON15M",
    "ZEC": "KXZEC15M",
}

SERIES_TO_ASSET = {v: k for k, v in ASSET_TO_SERIES.items()}

COINBASE_PRODUCT = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "XRP": "XRP-USD",
    "DOGE": "DOGE-USD",
    "ADA": "ADA-USD",
    "BCH": "BCH-USD",
    "NEAR": "NEAR-USD",
    "ZEC": "ZEC-USD",
}

BINANCE_SYMBOL = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT",
    "DOGE": "DOGEUSDT",
    "BNB": "BNBUSDT",
    "ADA": "ADAUSDT",
    "BCH": "BCHUSDT",
    "NEAR": "NEARUSDT",
    "TON": "TONUSDT",
    "ZEC": "ZECUSDT",
    "HYPE": "HYPEUSDT",
}


def asset_from_series(ticker: str) -> str:
    if ticker in SERIES_TO_ASSET:
        return SERIES_TO_ASSET[ticker]
    if ticker.startswith("KX") and ticker.endswith("15M"):
        return ticker[2:-3]
    return ticker
