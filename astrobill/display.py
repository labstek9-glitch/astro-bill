from __future__ import annotations

import math
from rich.console import Console
from rich.table import Table
from astrobill.engine import Row

console = Console()


def _fmt(v: float, nd: int = 3) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    return f"{v:.{nd}f}"


def render(rows: list[Row], cycle: int) -> None:
    table = Table(title=f"ASTRO BILL  ·  Kalshi 15m crypto  ·  cycle {cycle}  ·  analysis only", show_lines=False, expand=True)
    for col in ["AST", "TICKER", "SEC", "SPOT", "STRIKE", "FAIR", "YES", "NO", "EDGE", "ACTION", "NOTE"]:
        table.add_column(col, overflow="fold")
    for r in rows:
        style = "green" if r.action.startswith("BUY") else ("red" if r.error else "dim")
        table.add_row(
            r.asset, (r.ticker or r.series)[:28], str(r.secs_left),
            _fmt(r.spot, 2), _fmt(r.strike, 2), _fmt(r.fair, 3),
            f"{_fmt(r.yes_bid, 2)}/{_fmt(r.yes_ask, 2)}",
            f"{_fmt(r.no_bid, 2)}/{_fmt(r.no_ask, 2)}",
            _fmt(r.edge, 3), r.action, (r.error or r.rationale)[:48], style=style,
        )
    console.clear()
    console.print(table)
    console.print("[dim]SIT is the default. Confirm any BUY yourself on Kalshi. No keys. No orders.[/dim]")
