from astrobill.model import fair_yes, propose


def test_far_above_strike_high_fair():
    p = fair_yes(spot=100, strike=90, seconds_left=60, vol_ann=0.5)
    assert p > 0.8


def test_far_below_strike_low_fair():
    p = fair_yes(spot=90, strike=100, seconds_left=60, vol_ann=0.5)
    assert p < 0.2


def test_propose_sits_when_no_edge():
    prop = propose(
        fair=0.50,
        yes_bid=0.49,
        yes_ask=0.51,
        no_bid=0.49,
        no_ask=0.51,
        contracts=10,
        max_notional=25,
        min_edge=0.01,
        seconds_left=400,
        sit_below=8,
    )
    assert prop.action == "SIT"


def test_propose_sits_late_window():
    prop = propose(
        fair=0.90,
        yes_bid=0.40,
        yes_ask=0.41,
        no_bid=0.59,
        no_ask=0.60,
        contracts=10,
        max_notional=25,
        min_edge=0.01,
        seconds_left=3,
        sit_below=8,
    )
    assert prop.action == "SIT"
