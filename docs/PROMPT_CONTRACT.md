# ASTRO BILL V2 prompt contract

This repository is an analysis-only, local decision desk. The human remains the operator of Kalshi.

## Non-negotiable boundary

- Never implement, import, invoke, or expose `place_order` or any equivalent exchange execution action.
- Never log into Kalshi, control a browser to trade, request passwords, 2FA, API keys, private keys, or account access.
- Never add Kalshi private, account, portfolio, or order endpoints, or signed/authenticated connections. Kalshi network traffic is restricted to unauthenticated, allowlisted public market/series GET routes.
- A public API refusing access must produce a visible HOLD/error. Do not bypass access controls or silently substitute invented market data.
- `POST /api/journal` writes local JSON only. It is not an exchange endpoint. It may never send a network order or confirmation.
- Do not commit credentials, logs, fills, position records, or generated snapshots. Preserve .gitignore protections.

## Decision truth

- Proposals, copied tickets, and UI views do not establish fills. CASH OUT and HOLD POSITION require an open human-logged FILL.
- CASH OUT compares a bid sale of the existing Kalshi position with holding it to expiry. No automatic sale occurs.
- Only human FILL followed by human SETTLE contributes to settled directional results. An unlogged proposal cannot become a win.
- Distinguish modeled fair probability, data-quality confidence, required break-even rate, and observed journal hit rate.
- Settlement is a 60-second CF Benchmarks average. Public venue spot and trailing spot means are proxies. Near-flat after fees means HOLD.
- Missing/stale data, unsupported strike direction, insufficient history near expiry, or uncertainty are not permission to fabricate a price, position, or result.
- New model changes require deterministic regression checks and honest live-validation status. Never promise a hit-rate improvement from internal scores alone.

## Compatibility and operation

Keep the package `astrobill`, V1 CLI flags, seed-plus-discovery, required exclusions, isolated rounded fee function, and local-first outputs. The local server binds to loopback and serves only desk assets and local analysis/journal routes. No cloud deployment or account integration is part of this contract.
