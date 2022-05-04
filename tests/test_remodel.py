"""
Test_remodel

Module to test functions related to remodeling algorithms
"""

import pytest
from pympo.remodeling.remodel import calc_new_rho
from pympo.remodeling.remodel import calc_stimulus
from pympo.remodeling.remodel import calc_delta_rho_local
from pympo.remodeling.remodel import calc_young
from pympo.remodeling.remodel import check_if_number


# Constants as reference for tests
RHO = 0.8
SED = 0.25

CC = 100
GC = 2

K_ZERO = 0.25
S = 0.0
F_FAC = 1.0
R_FAC = 1.0


class Inp:
    # Dummy empty class to allow a Matlab-'struct' style variable for testing
    pass


inp = Inp()
inp.K = 1.0
inp.s = 0.0
inp.f_fac = 1.0
inp.r_fac = 1.0
inp.rho_min = 0.01
inp.rho_max = 1.740

RHO_VEC = [1.0, 1.0, 1.0]
SED_VEC = [1.0, 1.0, 1.0]
NELEM = 3


@pytest.mark.parametrize(
    "inp, rho, sed, nelem, rho_new",
    [
        (inp, RHO_VEC, SED_VEC, NELEM, pytest.approx([1, 1, 2])),
    ],
)
def test_calc_new_rho_regular(inp, rho, sed, nelem, rho_new):
    assert calc_new_rho(inp, rho, sed, nelem) == rho_new


@pytest.mark.parametrize(
    "rho, sed, stimulus",
    [
        (RHO, SED, pytest.approx(0.3125)),
        (2, 10, 5),
        (1.2e8, 2.7e8, pytest.approx(2.25)),
    ],
)
def test_calc_stimulus_regular(rho, sed, stimulus):
    assert calc_stimulus(rho, sed) == stimulus


@pytest.mark.parametrize(
    "rho, sed, exception",
    [(1, "a", TypeError), ([2], 1, TypeError), (0, 1, ZeroDivisionError)],
)
def test_stimulus_exception(rho, sed, exception):
    with pytest.raises(exception):
        calc_stimulus(rho, sed)


@pytest.mark.parametrize(
    "stimulus, K, s, f_fac, r_fac, delta_rho",
    [
        (SED, K_ZERO, S, F_FAC, R_FAC, pytest.approx(0.0)),
        (2, 2, 0, 1, 1, 0),
        (3, 2, 0, 1, 1, 1),
        (1, 2, 0, 1, 1, -1),
        (0.3, 0.2, 0.5, 1, 1, pytest.approx(0.0)),
        (0.35, 0.2, 0.5, 1, 1, pytest.approx(0.05)),
        (0.15, 0.2, 0.5, 1, 1, pytest.approx(0.0)),
        (0.07, 0.2, 0.5, 1, 1, pytest.approx(-0.03)),
        (0.07, 0.2, 0.5, 1.5, 1.2, pytest.approx(-0.036)),
        (0.35, 0.2, 0.5, 1.5, 1.2, pytest.approx(0.075)),
    ],
)
def test_calc_delta_rho_local_regular(stimulus, K, s, f_fac, r_fac, delta_rho):
    assert calc_delta_rho_local(stimulus, K, s, f_fac, r_fac) == delta_rho


@pytest.mark.parametrize(
    "stimulus, K, s, f_fac, r_fac, exception",
    [
        (2, "a", 0, 1, 1, TypeError),
        ([2], 1, 0, 1, 1, TypeError),
        (2, 1, 0, [1], 1, TypeError),
        (1, 2, 0, 1, [1], TypeError),
    ],
)
def test_calc_delta_rho_local_exception(
    stimulus, K, s, f_fac, r_fac, exception
):
    with pytest.raises(exception):
        calc_delta_rho_local(stimulus, K, s, f_fac, r_fac)


@pytest.mark.parametrize(
    "rho, cc, gc, young",
    [
        (RHO, CC, GC, pytest.approx(64.0)),
        (10, 15, 0, 15),
        (1.2e8, 2.0e8, 2.0, pytest.approx(2.88e24)),
    ],
)
def test_calc_young_regular(rho, cc, gc, young):
    assert calc_young(rho, cc, gc) == young


@pytest.mark.parametrize(
    "rho, cc, gc, exception",
    [
        (1, "a", 1, TypeError),
        ([2], 1, 1, TypeError),
        (0, 1, [0], TypeError),
    ],
)
def test_calc_young_exception(rho, cc, gc, exception):
    with pytest.raises(exception):
        calc_young(rho, cc, gc)


@pytest.mark.parametrize(
    "var",
    [
        1,
        2.0,
        -3,
        -4.5,
        3.7e18,
    ],
)
def test_check_if_number_regular(var):
    assert check_if_number(var)


@pytest.mark.parametrize(
    "var, exception",
    [
        ("a", TypeError),
        ([2], TypeError),
    ],
)
def test_check_if_number_exception(var, exception):
    with pytest.raises(exception):
        check_if_number(var)
