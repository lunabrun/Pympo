"""
Test_remodel_mapdl

Module to test functions related to remodeling algorithms.
Only functions that need a mapdl instance are tested here.
"""

import os
import sys
import pytest
import numpy as np

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.errors import LockFileException

from pympo.remodeling.remodel import huiskes_methods
from pympo.remodeling.remodel import solve_ansys
from pympo.remodeling.remodel import get_sed
from pympo.remodeling.remodel import update_material

# Constants as reference for tests
N_ELEM = 130
EL_TYP_NUMBER = 1
RHO = 5.0 * np.ones(N_ELEM)


class Inp:
    # Dummy empty class to allow a Matlab-'struct' style variable for testing
    pass


# Input structures for tests
inp1 = Inp()
inp1.niter = 1
inp1.el_typ_number = EL_TYP_NUMBER
inp1.CC = 100.0
inp1.GC = 2.0
inp1.K = 1.0
inp1.s = 0.0
inp1.f_fac = 1.0
inp1.r_fac = 1.0
inp1.rho_min = 0.01
inp1.rho_max = 2.0

# Common variable for test support functions
out_dir = "/tests/sandbox"
run_dir = os.getcwd() + out_dir


@pytest.fixture(scope="module")
def load_mapdl():
    # Initialization - Stops, clear and delete any running module/analysis
    try:  # Initiate grpc server
        mapdl = launch_mapdl(
            run_location=run_dir,
            override=True,
            start_instance=True,
        )
    except (
        IOError,
        LockFileException,
    ):  # If unable to initiate, try to connect to existing server
        mapdl = launch_mapdl(
            run_location=run_dir,
            override=True,
            start_instance=False,
        )
    except:
        print("Ansys Grpc server failed to start. Pympo will be closed.")
        sys.exit()

    mapdl.mute = True

    yield mapdl

    # Finish mapdl
    mapdl.run(":ENDSCRIPT")
    mapdl.exit()


def run_sed_benchmark(mapdl):
    # Read all necessary APDL commands for benchmark
    with open(run_dir + "/SED_Benchmark.inp", "r") as f:
        cmd = f.read()

    # Run script under "cmd"
    mapdl.input_strings(cmd)

    return mapdl


def solve_sed_benchmark(mapdl):
    # Solve static analysis with ansys
    mapdl.slashsolu()
    mapdl.antype(0)
    mapdl.solve()
    mapdl.post1()
    mapdl.set("LAST")
    mapdl.esel("S", "TYPE", "", EL_TYP_NUMBER)

    return mapdl


@pytest.mark.slow
def test_huiskes_methods_regular(load_mapdl):
    mapdl_sed_benchmark = run_sed_benchmark(load_mapdl)
    mapdl_sed_benchmark, rho_new, young_new, stimulus = huiskes_methods(
        mapdl_sed_benchmark, inp1, N_ELEM, RHO
    )

    assert (
        np.allclose(
            rho_new,
            2.0,
            rtol=1e-05,
            atol=1e-08,
        )
        and np.allclose(
            young_new,
            400.0,
            rtol=1e-05,
            atol=1e-08,
        )
        and np.allclose(
            stimulus,
            0.0542,
            rtol=0.0,
            atol=1e-04,
        )
    )


@pytest.mark.slow
def test_solve_ansys_regular(load_mapdl):
    mapdl_sed_benchmark = run_sed_benchmark(load_mapdl)
    mapdl_sed_benchmark = solve_ansys(mapdl_sed_benchmark, inp1)

    # Normal stress in transverse direction
    s_z = mapdl_sed_benchmark.post_processing.element_values("S", "Z")
    assert np.allclose(
        s_z,
        163.7,
        rtol=0.0,
        atol=0.1,
    )


@pytest.mark.slow
def test_get_sed_regular(load_mapdl):
    mapdl_sed_benchmark = run_sed_benchmark(load_mapdl)
    mapdl_sed_benchmark = solve_sed_benchmark(mapdl_sed_benchmark)
    assert np.allclose(
        get_sed(mapdl_sed_benchmark, N_ELEM),
        0.271,
        rtol=0.0,
        atol=1e-04,
    )


@pytest.mark.slow
def test_update_material_regular(load_mapdl):
    mapdl_sed_benchmark = run_sed_benchmark(load_mapdl)
    mapdl_sed_benchmark = solve_sed_benchmark(mapdl_sed_benchmark)
    assert np.allclose(
        update_material(mapdl_sed_benchmark, inp1, RHO, N_ELEM),
        2500.0,
        rtol=1e-05,
        atol=1e-08,
    )
