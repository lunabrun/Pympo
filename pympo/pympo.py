"""
Pympo

Program for the fatigue calculation of dental implants considering the effect
of bone remodeling.

Stimulus for remodeling calculated via Finite Element Method.
Interface with Ansys via pyAnsys/pyMAPDL.

Input to the program via the utils.input module.
Output from the program to the "ansys_tmp" folder.
"""

import os
from ansys.mapdl.core import launch_mapdl

from remodeling import remodel
from utils import inp, geo, mesh, bc

# Initialization - Stops, clear and delete any running module/analysis
mapdl = launch_mapdl(
    run_location=os.getcwd() + "/pympo/ansys_tmp",
    loglevel="WARNING",
    print_com=True,
)
mapdl.finish()
mapdl.clear()

# Preprocessor (Setting up the model)
mapdl.prep7()

# Create/import geometry
mapdl = geo.create_2d_plate(mapdl, inp)

# Create/import mesh
mapdl = mesh.create_2d_mesh(mapdl, inp)

# Initialization of element-wise data and vector rho
nelem, rho = mesh.ini_rho(mapdl, inp)

# Apply boundary conditions
mapdl = bc.create_bc_weinans92(mapdl, inp)

# Remodel material
mapdl, rho, young = remodel.huiskes_methods(mapdl, inp, nelem, rho)

# Finish mapdl
mapdl.run(":ENDSCRIPT")
mapdl.exit()
