"""
Mesh

Module to input or create mesh for pympo program.
"""

import numpy as np
import time


def create_2d_mesh(mapdl, inp):
    """Create a 2D mesh using APDL commands

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables
    """
    # Definition of element and its keyoptions
    # Element type (et) 1: PLANE182, 4-node 2D plane element
    # Key option 1 (element technology)
    # Key option 3 (element behavior)
    mapdl.et(1, "PLANE182")
    mapdl.keyopt(1, 1, 2)
    mapdl.keyopt(1, 3, 0)

    # Define global mesh ref. level (1(fine) to 10(rough)) and plot
    mapdl.smrtsize(inp.mesh_refine)
    mapdl.amesh("ALL")

    return mapdl


def ini_rho(mapdl, inp):
    """Initialize element-wise vector rho

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables
    """
    # Vectors creation for element related fields
    nelem = mapdl.mesh.n_elem
    rho = np.zeros(nelem)

    # Start time measure of ini_rho
    tic_ini_rho = time.time()

    # Initialization (via implied do-loop) of density for each element
    # Uses one materal type for each element
    mapdl.mp("EX", "1:" + str(nelem), inp.young_ini)
    mapdl.mp("PRXY", "1:" + str(nelem), inp.poisson)
    mapdl.emodif("1:" + str(nelem), "MAT", "1:" + str(nelem))
    rho = np.full(nelem, inp.rho_ini)

    # Finish time measure of ini_rho
    tac_ini_rho = time.time()
    print(
        "--- Function ini_rho elapsed time: %s seconds ---"
        % (tac_ini_rho - tic_ini_rho)
    )

    return nelem, rho
