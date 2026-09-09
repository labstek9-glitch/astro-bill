# Repository guidance — ASTRO BILL V2

V2: obey docs/PROMPT_CONTRACT.md. Public, unauthenticated analysis only. Do not implement login, place_order, private endpoints, or browser trading. Keep tests green. V2 delivery was reviewed with deterministic tests and local HTTP/DOM checks; no multi-agent or visual-browser review is claimed.

## Historical V1 notes

Four passes after the first build. All four are locked.

## Architect
- Public REST only on the hot path. No credentials in repo.
- Series list is seed + discover, with comparison markets excluded.
- Persist JSONL + web snapshot so Astra can comment on a file, not drive Chrome.

## Quant
- Fair value is a short-horizon lognormal, not a news scraper.
- Fee is subtracted before GREEN. Peak taker 1.75¢ at 50¢.
- Late-window kill: default sit under 8 seconds.

## Auditor
- Unit tests cover fee peak, extreme prices, sit-on-no-edge, sit-on-late-window.
- Live `--once` must return rows or a clean error, never a hang.
- README states settlement is CF Benchmarks 60s average.

## Operator
- `python -m astrobill` is the only command that needs to exist.
- Ctrl+C exits. Logs append. No order endpoint is imported.
- V2 supersedes the old authenticated-feed suggestion. Any settlement-data improvement must preserve the no-login/no-private-endpoint contract.
