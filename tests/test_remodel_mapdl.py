import os
import sys
import pytest
import numpy as np

from ansys.mapdl.core import launch_mapdl

from pympo.remodeling.remodel import get_sed


@pytest.fixture
def mapdl_sed_benchmark():
    # Initialization - Stops, clear and delete any running module/analysis
    out_dir = "/tests/sandbox"
    run_dir = os.getcwd() + out_dir
    try:  # Initiate grpc server
        mapdl = launch_mapdl(
            run_location=run_dir,
            override=True,
            start_instance=True,
        )
    except OSError:  # If unable to initiate, try to connect to existing server
        mapdl = launch_mapdl(
            run_location=run_dir,
            override=True,
            start_instance=False,
        )
    except:
        print("Ansys Grpc server failed to start. Pympo will be closed.")
        sys.exit()

    mapdl.mute = True

    # Read all necessary APDL commands for benchmark
    with open(run_dir + "/SED_Benchmark.inp", "r") as f:
        cmd = f.read()

    # Run script under "cmd"
    mapdl.input_strings(cmd)
    mapdl.post1()
    mapdl.set("LAST")
    mapdl.esel("S", "MAT", "", 1)

    yield mapdl

    # Finish mapdl
    mapdl.run(":ENDSCRIPT")
    mapdl.exit()


@pytest.mark.slow
def test_get_sed(mapdl_sed_benchmark):
    assert np.allclose(get_sed(mapdl_sed_benchmark, 130), 0.271, 10e-04)
