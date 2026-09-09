from astrobill.fees import taker_fee_dollars


def test_peak_at_fifty():
    assert taker_fee_dollars(0.50, 100) == 1.75


def test_zero_at_extremes():
    assert taker_fee_dollars(0.0, 10) == 0.0
    assert taker_fee_dollars(1.0, 10) == 0.0


def test_single_contract_rounds_up():
    fee = taker_fee_dollars(0.50, 1)
    assert fee == 0.02
