from pympo.remodeling.remodel import calc_stimulus

RHO = 5.0
SED = 10.0


def test_stimulus():
    stimulus = calc_stimulus(RHO, SED)
    assert stimulus == 2.0
