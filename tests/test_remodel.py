"""
Test_remodel

Module to test functions related to remodeling algorithms
"""

import pytest
from pympo.remodeling.remodel import calc_new_rho
from pympo.remodeling.remodel import calc_stimulus
from pympo.remodeling.remodel import calc_delta_rho_local
from pympo.remodeling.remodel import update_material
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


# Different input structures for tests
inp1 = Inp()
inp1.K = 1.0
inp1.s = 0.0
inp1.f_fac = 1.0
inp1.r_fac = 1.0
inp1.rho_min = 0.01
inp1.rho_max = 2.0

inp2 = Inp()
inp2.K = inp1.K
inp2.s = 0.5
inp2.f_fac = inp1.f_fac
inp2.r_fac = inp1.r_fac
inp2.rho_min = inp1.rho_min
inp2.rho_max = inp1.rho_max

inp3 = Inp()
inp3.K = inp1.K
inp3.s = "1"
inp3.f_fac = inp1.f_fac
inp3.r_fac = inp1.r_fac
inp3.rho_min = inp1.rho_min
inp3.rho_max = inp1.rho_max


@pytest.mark.parametrize(
    "inp, rho, sed, nelem, rho_new",
    [
        (inp1, [1.0], [1.0], 1, pytest.approx([1.0])),
        (inp1, [2.0], [0.5], 1, pytest.approx([1.25])),
        (inp1, [-2.0], [0.5], 1, pytest.approx([0.01])),
        (inp1, [2.0], [-0.5], 1, pytest.approx([0.75])),
        (
            inp1,
            [-2.0, 2.0, 1.3],
            [0.5, -0.5, 1.0],
            3,
            pytest.approx([0.01, 0.75, 1.06923]),
        ),
        (inp1, [100.0], [5], 1, pytest.approx([inp1.rho_max])),
        (inp1, [0.005], [0.005], 1, pytest.approx([inp1.rho_min])),
        (inp2, [2.0], [0.5], 1, pytest.approx([1.75])),
        (inp2, [2.0], [4.0], 1, pytest.approx([2.0])),
        (inp2, [1.0], [1.75], 1, pytest.approx([1.25])),
    ],
)
def test_calc_new_rho_regular(inp, rho, sed, nelem, rho_new):
    assert calc_new_rho(inp, rho, sed, nelem) == rho_new


@pytest.mark.parametrize(
    "inp, rho, sed, nelem, exception",
    [
        (inp1, ["a"], [1.0], 1, TypeError),
        (inp1, [1.0], ["a"], 1, TypeError),
        (inp1, [1.0], [1.0], "a", TypeError),
        (inp3, [1.0], [1.0], 1, TypeError),
    ],
)
def test_calc_new_rho_exception(inp, rho, sed, nelem, exception):
    with pytest.raises(exception):
        calc_new_rho(inp, rho, sed, nelem)


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
    "mapdl, inp, rho, nelem, young",
    [
        (mapdl, inp1, [1.0], 1, pytest.approx([1.0])),
    ],
)
def test_update_material_regular(mapdl, inp, rho, nelem, young):
    assert update_material(mapdl, inp, rho, nelem) == young


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
