# Astro Bill

Local 24/7 scanner for **every Kalshi 15-minute crypto up/down market**.

Astro Bill reads public Kalshi books + public spot, computes a short-horizon fair value, subtracts the Kalshi taker fee, and prints **BUY YES / BUY NO / SIT**. It does **not** log into Kalshi. It does **not** place orders. ChatGPT Astra is optional commentary on a snapshot — not the live loop.

Repo: https://github.com/labstek9-glitch/astro-bill

## What it watches

Auto-discovers `*15M` series tagged Crypto, plus this seed list:

| Asset | Series |
| --- | --- |
| BTC | KXBTC15M |
| ETH | KXETH15M |
| SOL | KXSOL15M |
| XRP | KXXRP15M |
| DOGE | KXDOGE15M |
| BNB | KXBNB15M |
| HYPE | KXHYPE15M |
| ADA | KXADA15M |
| BCH | KXBCH15M |
| NEAR | KXNEAR15M |
| TON | KXTON15M |
| ZEC | KXZEC15M |

Comparison/race series (`KXCRYPTOCOMP15M`, `KXCRYPTOLEAD15M`) are skipped — different contract structure.

## Settlement (do not ignore this)

Kalshi crypto 15m markets settle on a **60-second CF Benchmarks Real-Time Index average**, not the last Coinbase print. Spot here is a proxy. Fair value is a floor model. Near-flat windows after fees are coin flips. **SIT is the correct default.**

## Install

```bash
git clone https://github.com/labstek9-glitch/astro-bill.git
cd astro-bill
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally 24/7

```bash
python -m astrobill --poll 2
```

Single pass:

```bash
python -m astrobill --once
```

Open `web/index.html` in a browser after the first scan. It reads `web/latest.json`.

Stop with Ctrl+C.

## What you do with a BUY

1. Read ticker, side, limit, size.
2. Place it yourself on kalshi.com **or** a signed API bot you control.
3. Never paste RSA keys or passwords into ChatGPT.

Default size is capped at `$25` notional in `config.yaml`.

## Architecture

```
Kalshi public REST  ─┐
Coinbase / Binance  ─┼─► engine ─► terminal table + logs/scans.jsonl + web/latest.json
config.yaml         ─┘
```

- Poll interval: 2s (public REST). True tick-level books need a Kalshi API key + WebSocket on *your* machine only.
- Fees: `ceil(0.07 × C × P × (1−P))` dollars.
- Fair: lognormal P(spot ≥ strike) over remaining seconds with per-asset vol priors.

## Tests

```bash
pip install pytest
python -m pytest -q
```

## Law

Analysis tool. Not a broker. Not financial advice. You are responsible for every order that hits Kalshi.
