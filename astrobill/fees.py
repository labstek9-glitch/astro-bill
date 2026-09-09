from __future__ import annotations

import math


TAKER_RATE = 0.07


def taker_fee_dollars(price: float, contracts: float) -> float:
    """Kalshi event-contract taker fee.

    fee = ceil_to_cent(0.07 * C * P * (1 - P))
    P in dollars [0, 1]. Peaks at 1.75¢/contract when P = 0.50.
    """
    if contracts <= 0 or price <= 0.0 or price >= 1.0:
        return 0.0
    raw = TAKER_RATE * contracts * price * (1.0 - price)
    return math.ceil(raw * 100.0 - 1e-12) / 100.0


def fee_per_contract(price: float) -> float:
    return taker_fee_dollars(price, 1.0)
