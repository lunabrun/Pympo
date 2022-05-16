"""
Mesh

Module to input or create mesh for pympo program.
"""

import numpy as np


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
    mapdl.eplot()

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

    # Initialization of density for each element
    # Uses one materal type for each element
    for el in range(nelem):
        el_ansys = el + 1  # Ansys numbering convention
        mapdl.mp("EX", el_ansys, inp.young_ini)
        mapdl.mp("PRXY", el_ansys, inp.poisson)
        mapdl.emodif(el_ansys, "MAT", el_ansys)
        rho[el] = inp.rho_ini

    return nelem, rho
