"""
Test_remodel

Module to test functions related to remodeling algorithms.
Only functions that do NOT need a mapdl instance are tested here.
"""

import pytest
import numpy as np

from pympo.remodeling.remodel import calc_new_rho
from pympo.remodeling.remodel import calc_stimulus
from pympo.remodeling.remodel import calc_delta_rho_local
from pympo.remodeling.remodel import calc_young
from pympo.remodeling.remodel import calc_distance
from pympo.remodeling.remodel import spatial_influence
from pympo.remodeling.remodel import calc_spatial_stimulus
from pympo.remodeling.remodel import check_if_num_numpy
from pympo.remodeling.remodel import check_if_float


# Constants as reference for tests
RHO = np.asarray([0.8])
SED = np.asarray([0.25])

CC = 100.0
GC = 2.0

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
inp1.D = 0.025

inp2 = Inp()
inp2.K = inp1.K
inp2.s = 0.5
inp2.f_fac = inp1.f_fac
inp2.r_fac = inp1.r_fac
inp2.rho_min = inp1.rho_min
inp2.rho_max = inp1.rho_max
inp2.D = -0.025


@pytest.mark.parametrize(
    "inp, rho, sed, nelem, rho_new, stimulus",
    [
        (
            inp1,
            np.asarray([1.0]),
            np.asarray([1.0]),
            1,
            pytest.approx(np.asarray([1.0])),
            pytest.approx(np.asarray([1.0])),
        ),
        (
            inp1,
            np.asarray([2.0]),
            np.asarray([0.5]),
            1,
            pytest.approx(np.asarray([1.25])),
            pytest.approx(np.asarray([0.25])),
        ),
        (
            inp1,
            np.asarray([1.0, 2.0, 1.3]),
            np.asarray([1.0, 0.5, 1.0]),
            3,
            pytest.approx(np.asarray([1.0, 1.25, 1.06923])),
            pytest.approx(np.asarray([1.0, 0.25, 0.7692307])),
        ),
        (
            inp1,
            np.asarray([100.0, 0.005]),
            np.asarray([5.0, 0.005]),
            2,
            pytest.approx(np.asarray([inp1.rho_max, inp1.rho_min])),
            pytest.approx(np.asarray([0.05, 1])),
        ),
        (
            inp2,
            np.asarray([2.0, 2.0, 1.0]),
            np.asarray([0.5, 4.0, 1.75]),
            3,
            pytest.approx(np.asarray([1.75, 2.0, 1.25])),
            pytest.approx(np.asarray([0.25, 2.0, 1.75])),
        ),
    ],
)
def test_calc_new_rho_regular(inp, rho, sed, nelem, rho_new, stimulus):
    assert calc_new_rho(inp, rho, sed, nelem) == (rho_new, stimulus)


@pytest.mark.parametrize(
    "inp, rho, sed, nelem, exception",
    [
        (inp1, ["a"], [1.0], 1, TypeError),
        (inp1, [1.0], ["a"], 1, TypeError),
        (inp2, [1.0], [1.0], "a", TypeError),
    ],
)
def test_calc_new_rho_exception(inp, rho, sed, nelem, exception):
    with pytest.raises(exception):
        calc_new_rho(inp, rho, sed, nelem)


@pytest.mark.parametrize(
    "sed, rho, stimulus",
    [
        (SED, RHO, pytest.approx(np.asarray([0.3125]))),
        (
            np.asarray([2.7e8]),
            np.asarray([1.2e8]),
            pytest.approx(np.asarray([2.25])),
        ),
        (
            np.asarray([1.0, 2.0, 3.0]),
            np.asarray([3.0, 2.0, 1.0]),
            pytest.approx(np.asarray([1 / 3, 1.0, 3.0])),
        ),
    ],
)
def test_calc_stimulus_regular(sed, rho, stimulus):
    assert calc_stimulus(sed, rho) == stimulus


@pytest.mark.parametrize(
    "sed, rho, exception",
    [
        (1, "a", TypeError),
        ([2], 1, TypeError),
        (1, 0, ZeroDivisionError),
        (
            np.asarray([1.0, 2.0, 3.0]),
            np.asarray([3.0, 2.0]),
            ValueError,
        ),
    ],
)
def test_stimulus_exception(sed, rho, exception):
    with pytest.raises(exception):
        calc_stimulus(sed, rho)


@pytest.mark.parametrize(
    "stimulus, K, s, f_fac, r_fac, delta_rho",
    [
        (SED, K_ZERO, S, F_FAC, R_FAC, pytest.approx(np.asarray([0.0]))),
        (
            np.asarray([0.3, 0.35, 0.15]),
            0.2,
            0.5,
            1.0,
            1.0,
            pytest.approx(np.asarray([0.00, 0.05, 0.0])),
        ),
        (
            np.asarray([0.07, 0.35]),
            0.2,
            0.5,
            1.5,
            1.2,
            pytest.approx(np.asarray([-0.036, 0.075])),
        ),
    ],
)
def test_calc_delta_rho_local_regular(stimulus, K, s, f_fac, r_fac, delta_rho):
    assert calc_delta_rho_local(stimulus, K, s, f_fac, r_fac) == delta_rho


@pytest.mark.parametrize(
    "stimulus, K, s, f_fac, r_fac, exception",
    [
        (np.asarray([2.0]), "a", 0, 1, 1, TypeError),
        ([2], 1, 0, 1, 1, TypeError),
        (np.asarray([2.0, 2.0]), 1, 0, [1, 2], 1, TypeError),
        (np.asarray([2.0]), 2, 0, 1, [2, 1], TypeError),
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
        (RHO, CC, GC, pytest.approx(np.asarray([64.0]))),
        (
            np.asarray([1.2e8]),
            2.0e8,
            2.0,
            pytest.approx(np.asarray([2.88e24])),
        ),
        (
            np.asarray([1.0, 2.0, 3.0]),
            3.0,
            2.0,
            pytest.approx(np.asarray([3.0, 12.0, 27.0])),
        ),
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
        (-2.0, 1.0, -0.5, TypeError),
        (
            np.asarray(["NaN", 2.0, 3.0]),
            3.0,
            2.0,
            TypeError,
        ),
        (
            np.asarray([10.0, 1.2e8]),
            np.asarray([15.0, 2.0e8]),
            np.asarray([0.0, 2.0]),
            TypeError,
        ),
    ],
)
def test_calc_young_exception(rho, cc, gc, exception):
    with pytest.raises(exception):
        calc_young(rho, cc, gc)


@pytest.mark.parametrize(
    "v1, M1, dist",
    [
        (
            np.asarray([[2.0, 3.0, 4.0]]),
            np.asarray([[5.0, 6.0, 7.0]]),
            np.asarray([[5.19615]]),
        ),
        (
            np.asarray([[1.86e-02, 9.00e-02, -8.35e-03]]),
            np.asarray([[1.86e-02, 7.00e-02, -8.35e-03]]),
            np.asarray([[0.020]]),
        ),
        (
            np.asarray([[1.0, 0.0, 0.0]]),
            np.asarray([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 1.0]]),
            np.asarray([[1.0, 0.0, 1.41421]]),
        ),
    ],
)
def test_calc_distance_regular(v1, M1, dist):
    assert np.allclose(calc_distance(v1, M1), dist)


@pytest.mark.parametrize(
    "v1, M1, exception",
    [
        (
            np.asarray([[2.0, 3.0, 4.0]]),
            np.asarray([[5.0, 6.0, "NaN"]]),
            ValueError,
        ),
        (
            np.asarray([[2.0, 3.0, 4.0]]),
            np.asarray([[5.0, 6.0]]),
            ValueError,
        ),
        (
            np.asarray([[2.0]]),
            np.asarray([[5.0, 6.0]]),
            ValueError,
        ),
        (
            np.asarray([2.0, 3.0, 4.0]),
            np.asarray([[5.0, 6.0, 7.0]]),
            ValueError,
        ),
        (
            np.asarray([[2.0, 3.0, 4.0]]),
            np.asarray("NaN"),
            ValueError,
        ),
    ],
)
def test_calc_distance_exception(v1, M1, exception):
    with pytest.raises(exception):
        calc_distance(v1, M1)


@pytest.mark.parametrize(
    "inp, dist, f",
    [
        (
            inp1,
            np.asarray([[1.0, 0.0, 1.41421]]),
            np.asarray([[4.24835426e-18, 1.0e00, 2.70804595e-25]]),
        ),
    ],
)
def test_spatial_influence_regular(inp, dist, f):
    assert np.allclose(spatial_influence(inp, dist), f)


@pytest.mark.parametrize(
    "inp, dist, exception",
    [
        (
            inp1,
            np.asarray([["NaN", 0.0, 1.41421]]),
            TypeError,
        ),
        (
            inp2,
            np.asarray([[1.0, 0.0, 1.41421]]),
            ValueError,
        ),
    ],
)
def test_spatial_influence_exception(inp, dist, exception):
    with pytest.raises(exception):
        spatial_influence(inp, dist)


@pytest.mark.parametrize(
    "f, stimulus, K, phi",
    [
        (np.asarray([[2, 3, 0]]), np.asarray([[5, 2, 4]]), inp1.K, 11.0),
    ],
)
def test_calc_spatial_stimulus_regular(f, stimulus, K, phi):
    assert np.allclose(calc_spatial_stimulus(f, stimulus, K), phi)


@pytest.mark.parametrize(
    "f, stimulus, K, exception",
    [
        (np.asarray([[2, 3, 0]]), np.asarray([[5, 2]]), inp1.K, ValueError),
        (np.asarray([[2, 3]]), np.asarray([[5, 2, 4]]), inp1.K, ValueError),
        (
            np.asarray([[2, 3, 0]]),
            np.asarray([[5, 2, "NaN"]]),
            inp1.K,
            np.core._exceptions.UFuncTypeError,
        ),
    ],
)
def test_calc_spatial_stimulus_exception(f, stimulus, K, exception):
    with pytest.raises(exception):
        calc_spatial_stimulus(f, stimulus, K)


@pytest.mark.parametrize(
    "array",
    [
        np.asarray([1]),
        np.asarray([2.0]),
        np.asarray([-3]),
        np.asarray([3.7e18]),
        np.asarray([1.0, 2.0, 3.0]),
    ],
)
def test_check_if_num_numpy_regular(array):
    assert check_if_num_numpy(array)


@pytest.mark.parametrize(
    "array, exception",
    [
        (1.0, TypeError),
        ([1, 2], TypeError),
        ("a", TypeError),
        ([2, "a"], TypeError),
        (np.asarray([1.0, 2.0, "NaN"]), TypeError),
    ],
)
def test_check_if_num_numpy_exception(array, exception):
    with pytest.raises(exception):
        check_if_num_numpy(array)


@pytest.mark.parametrize(
    "var",
    [
        0.0,
        -1.0,
        1e20,
        1 / 3,
    ],
)
def test_check_if_float_regular(var):
    assert check_if_float(var)


@pytest.mark.parametrize(
    "var, exception",
    [
        (np.asarray([1]), TypeError),
        ([1, 2], TypeError),
        ("a", TypeError),
        ([2, "a"], TypeError),
        (np.asarray([1.0, 2.0, "NaN"]), TypeError),
        (-2, TypeError),
        (0, TypeError),
    ],
)
def test_check_if_float_exception(var, exception):
    with pytest.raises(exception):
        check_if_float(var)
