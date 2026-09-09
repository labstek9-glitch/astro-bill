from __future__ import annotations

import math
from decimal import Decimal


TAKER_RATE = 0.07


def taker_fee_dollars(price: float, contracts: float) -> float:
    """Kalshi event-contract taker fee.

    fee = ceil_to_cent(0.07 * C * P * (1 - P))
    P in dollars [0, 1]. Peaks at 1.75¢/contract when P = 0.50.
    """
    if contracts <= 0 or price <= 0.0 or price >= 1.0:
        return 0.0
    # Decimal prevents binary 1.7500000000000002 rounding up to $1.76.
    p = Decimal(str(price))
    raw = Decimal("0.07") * Decimal(str(contracts)) * p * (1-p)
    return math.ceil(raw * 100) / 100


def fee_per_contract(price: float) -> float:
    return taker_fee_dollars(price, 1.0)
