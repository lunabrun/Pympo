"""
Geo

Module to input or create geometry for pympo program.
"""


def create_2d_plate(mapdl, inp):
    """Create a 2D rectangular/square plate using APDL commands

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables
    """
    # Build the geometry - Create plate
    # Define keypoint via their coordinates x, y, z
    mapdl.k(1, 0.0, 0.0, 0.0)
    mapdl.k(2, inp.length, 0.0, 0.0)
    mapdl.k(3, inp.length, inp.height, 0.0)
    mapdl.k(4, 0.0, inp.height, 0.0)

    # Connect keypoints and create lines
    mapdl.lstr(1, 2)
    mapdl.lstr(2, 3)
    mapdl.lstr(3, 4)
    mapdl.lstr(4, 1)

    # Create and plot area by all selected lines (1, 2, 3, 4)
    mapdl.al("ALL")
    mapdl.allsel()

    return mapdl
