"""Parse real REST bid ladders; never replace an empty ladder with market metadata."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class Book:
    yes_bid: float = math.nan
    yes_ask: float = math.nan
    no_bid: float = math.nan
    no_ask: float = math.nan
    yes_bid_depth: float = 0
    no_bid_depth: float = 0
    yes_depth: float = 0
    no_depth: float = 0


def parse_book(data: dict[str, Any]) -> Book:
    body = data.get("orderbook_fp") or data.get("orderbook") or {}

    def best(side: str) -> tuple[float, float]:
        dollar_key = f"{side}_dollars"
        dollars = dollar_key in body
        levels = body.get(dollar_key if dollars else side) or []
        parsed = []
        for level in levels:
            try:
                price, quantity = float(level[0]), float(level[1])
                price /= 1 if dollars else 100
                if math.isfinite(price) and 0 < price < 1 and math.isfinite(quantity) and quantity > 0:
                    parsed.append((price, quantity))
            except (IndexError, TypeError, ValueError):
                continue
        if not parsed:
            return math.nan, 0
        bid = max(p for p, _ in parsed)
        return bid, sum(q for p, q in parsed if p == bid)

    y, yq = best("yes")
    n, nq = best("no")
    return Book(y, 1-n, n, 1-y, yq, nq, nq, yq)
