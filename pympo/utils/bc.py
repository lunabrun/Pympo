"""
BC

Module to define boundary conditions (bc) for pympo program.
"""


def create_bc_weinans92(mapdl, inp):
    """Create the boundary conditions for the example shown in Weinans92 paper

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables
    """
    # Apply Load and Boundary Conditions
    # Displacement boundary conditions
    # Bottom side (y=0)
    mapdl.nsel("S", "LOC", "Y", 0.0)
    mapdl.d("ALL", "UY", 0.0)
    mapdl.allsel()
    # Bottom left corner (x=0,y=0)
    mapdl.nsel("S", "LOC", "Y", 0.0)
    mapdl.nsel("R", "LOC", "X", 0.0)
    mapdl.d("ALL", "UY", 0.0)
    mapdl.d("ALL", "UX", 0.0)
    mapdl.allsel()

    # Applying the load
    # Distributed force definition (linear gradient)
    mapdl.sfgrad("PRES", 0, "X", 0.0, -inp.dist_force / inp.length)
    # Top side (y=height)
    mapdl.nsel("S", "LOC", "Y", inp.height)
    mapdl.sf("ALL", "PRES", inp.dist_force)
    mapdl.sfgrad()  # 'Turn off' SFGRAD
    mapdl.allsel()

    return mapdl
