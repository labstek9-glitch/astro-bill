# Changelog

## 2.0.0 — 2026-09-09

- Replaced BUY YES / BUY NO / SIT with BET UP / BET DOWN / HOLD; added fill-dependent HOLD POSITION and CASH OUT.
- Added actual REST order-book pricing, fixed-point parsing, complement asks, depth-aware sizing, fee-inclusive budget caps, and explicit stale/missing/confidence/spread guards.
- Added concurrent public Coinbase/Binance/Kraken quotes, venue divergence checks, rolling local volatility, and a guarded trailing-60-second settlement proxy.
- Added seed-plus-periodic-discovery with pagination and mandatory comparison-series exclusions.
- Added locked, append-only local journal events, partial exits, human settlement, net realized P/L, Brier and sample-size reporting.
- Added loopback HTTP service, a responsive dark Decision Desk, expiring signals, copy tickets, local journal controls, position dock, calibration, and read-only snapshot fallback.
- Preserved V1 CLI flags and module entry point; fixed JSON NaN serialization and snapshot partial-write races.
- Kept the fee formula isolated; decimal evaluation prevents floating-point overcharges at cent boundaries.
- Documented strict no-login/no-order boundaries in docs/PROMPT_CONTRACT.md; removed unused credential placeholders.
- Added regression and integration tests. Public live connectivity remains unverified in the build environment (HTTP 403/timeouts); no measured hit-rate claim.
