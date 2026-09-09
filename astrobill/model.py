from __future__ import annotations

import math
from dataclasses import dataclass

from astrobill.fees import taker_fee_dollars

DEFAULT_VOL = {
    "BTC": 0.55, "ETH": 0.70, "SOL": 0.90, "XRP": 0.85, "DOGE": 1.10,
    "BNB": 0.65, "HYPE": 1.40, "ADA": 0.85, "BCH": 0.80, "NEAR": 1.00,
    "TON": 0.90, "ZEC": 1.00,
}


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def fair_yes(spot: float, strike: float, seconds_left: float, vol_ann: float) -> float:
    if spot <= 0 or strike <= 0 or seconds_left <= 0 or vol_ann <= 0:
        return float("nan")
    tau = max(seconds_left, 1.0) / (365.25 * 24 * 3600)
    denom = vol_ann * math.sqrt(tau)
    if denom <= 0:
        return 1.0 if spot >= strike else 0.0
    z = math.log(spot / strike) / denom
    return min(0.999, max(0.001, _norm_cdf(z)))


@dataclass
class Proposal:
    action: str
    side: str
    limit: float
    contracts: float
    notional: float
    fee: float
    edge: float
    rationale: str


def propose(*, fair, yes_bid, yes_ask, no_bid, no_ask, contracts, max_notional, min_edge, seconds_left, sit_below) -> Proposal:
    if seconds_left < sit_below:
        return Proposal("SIT", "", 0.0, 0.0, 0.0, 0.0, 0.0, "window too close to settlement")
    if any(math.isnan(x) for x in (fair, yes_bid, yes_ask, no_bid, no_ask)):
        return Proposal("SIT", "", 0.0, 0.0, 0.0, 0.0, 0.0, "incomplete book or spot")
    px_cap = max(yes_ask, no_ask, 0.01)
    sized = max(1.0, math.floor(min(contracts, max_notional / px_cap)))
    buy_yes_fee = taker_fee_dollars(yes_ask, sized)
    buy_no_fee = taker_fee_dollars(no_ask, sized)
    yes_edge = fair - yes_ask - (buy_yes_fee / sized)
    no_edge = (1.0 - fair) - no_ask - (buy_no_fee / sized)
    if yes_edge >= no_edge and yes_edge >= min_edge:
        return Proposal("BUY YES", "yes", yes_ask, sized, yes_ask * sized, buy_yes_fee, yes_edge,
                        f"fair {fair:.3f} vs yes ask {yes_ask:.3f}; edge {yes_edge:.3f} after fee")
    if no_edge >= min_edge:
        return Proposal("BUY NO", "no", no_ask, sized, no_ask * sized, buy_no_fee, no_edge,
                        f"fair {fair:.3f} vs no ask {no_ask:.3f}; edge {no_edge:.3f} after fee")
    return Proposal("SIT", "", 0.0, 0.0, 0.0, 0.0, max(yes_edge, no_edge), "no edge after taker fee + buffer")
