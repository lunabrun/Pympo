import pytest
from pympo.remodeling.remodel import calc_stimulus
from pympo.remodeling.remodel import calc_young

RHO = 0.8
SED = 0.25

CC = 100
GC = 2


def test_stimulus():
    stimulus = calc_stimulus(RHO, SED)
    assert stimulus == pytest.approx(0.3125)


def test_young():
    young = calc_young(RHO, CC, GC)
    assert young == pytest.approx(64.0)
