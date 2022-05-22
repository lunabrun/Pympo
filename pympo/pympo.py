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
import time
from ansys.mapdl.core import launch_mapdl

from remodeling import remodel, post
from utils import inp, geo, mesh, bc

# Start time measure
tic = time.time()

# Initialization - Stops, clear and delete any running module/analysis
mapdl = launch_mapdl(run_location=os.getcwd() + inp.out_dir, override=True)
mapdl.finish()
mapdl.mute = True
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
mapdl, rho, young, stimulus = remodel.huiskes_methods(mapdl, inp, nelem, rho)

# Postprocess results
post.plot_results(mapdl, rho, young, stimulus, "last", inp)

# Finish mapdl
mapdl.run(":ENDSCRIPT")
mapdl.exit()

# Finish time measure
tac = time.time()
print("--- Total elapsed time: %s seconds ---" % (tac - tic))
