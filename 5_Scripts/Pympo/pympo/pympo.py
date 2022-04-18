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
import numpy as np
from ansys.mapdl.core import launch_mapdl
from utils import inp, geo, mesh

# Initialization - Stops, clear and delete any running module/analysis
mapdl = launch_mapdl(
    run_location=os.getcwd() + "/ansys_tmp", loglevel="WARNING", print_com=True
)
mapdl.finish()
mapdl.run("/CLEAR")

# Preprocessor (Setting up the model)
mapdl.prep7()

# Create/import geometry
mapdl = geo.create_2d_plate(mapdl, inp)

# Create/import mesh
mapdl = mesh.create_2d_mesh(mapdl, inp)

# Vectors creation for element related fields
nelem = int(mapdl.get("nElem", "ELEM", 0, "COUNT"))
rho = np.zeros(nelem)
delta_rho = np.zeros(nelem)
sed = np.zeros(nelem)
young = np.zeros(nelem)

# Initialization of density for each element
# Uses one materal type for each element
for el in range(nelem):
    el_ansys = el + 1  # Account for ansys numbering convention
    mapdl.mp("EX", el_ansys, inp.young_ini)
    mapdl.mp("PRXY", el_ansys, inp.poisson)
    mapdl.emodif(el_ansys, "MAT", el_ansys)
    rho[el] = inp.rho_ini

# === Apply Load and Boundary Conditions
# --- Displacement boundary conditions
mapdl.nsel("S", "LOC", "Y", 0.0)  # Select all nodes at y = 0 (bottom side)
mapdl.d("ALL", "UY", 0.0)  # Set displacement uy to zero for selected nodes
mapdl.allsel()  # Select all entities
mapdl.nsel("S", "LOC", "Y", 0.0)  # Select all nodes at y = 0 (bottom side)
mapdl.nsel(
    "R", "LOC", "X", 0.0
)  # From previous selected nodes, get bottom left corner (x=0,y=0)
mapdl.d("ALL", "UY", 0.0)  # Set displacement uy to zero for selected nodes
mapdl.d("ALL", "UX", 0.0)  # Set displacement ux to zero for selected node
mapdl.allsel()  # Select all entities

# --- Applying the load
mapdl.sfgrad(
    "PRES", 0, "X", 0.0, -inp.dist_force / inp.length
)  # Distributed force definition (linear gradient)
mapdl.nsel(
    "S", "LOC", "Y", inp.height
)  # Select location for application of linear varying force
mapdl.sf("ALL", "PRES", inp.dist_force)  # Application of force
mapdl.sfgrad()  # 'Turn off' SFGRAD
mapdl.allsel()  # Select all entries

# ===============================================================================
# B. START REMODELING LOOP
# ===============================================================================

for iter in range(1, inp.niter + 1):  # Loop over remodeling steps
    # ============================================================================
    # ====== Solution
    mapdl.slashsolu()  # Switch to the solution module
    mapdl.antype(0)  # Select the static analysis type
    mapdl.solve()  # Solve current load step
    # ============================================================================
    # ====== Postprocessor
    mapdl.run("/POST1")  # Switch to the postprocessor module
    mapdl.post1()
    mapdl.set("LAST")  # Read results from last step
    # ============================================================================
    # === Read Strain Energy Density (SED)
    # Save element-wise SED result in E-Table
    mapdl.etable("et_SED", "SEND", "ELASTIC")
    for el in range(nelem):  # Loop over all elements
        el_ansys = el + 1
        sed[el] = mapdl.get(
            "sed", "ELEM", el_ansys, "ETAB", "et_SED"
        )  # ... and read element result
    # ============================================================================

    # === Prepare remodeling (i.e., calculate dp/dt)
    for el in range(nelem):  # Loop over all elements
        stimulus = sed[el] / rho[el]
        if stimulus < inp.limit_res:
            delta_rho[el] = inp.resorp_fac * (stimulus - inp.limit_res)
        elif stimulus > inp.limit_for:
            delta_rho[el] = inp.form_fac * (stimulus - inp.limit_for)
        else:
            delta_rho[el] = 0.0
        rho[el] = rho[el] + delta_rho[el]

        if rho[el] <= inp.rho_min:  # Limit resorption
            rho[el] = inp.rho_min
        elif rho[el] >= inp.rho_max:  # Limit formation
            rho[el] = inp.rho_max

    # ============================================================================
    # === Remodeling, actually change material

    mapdl.prep7()  # Switch to Preprocessor
    for el in range(nelem):  # Loop over all elements
        el_ansys = el + 1
        mat_no = mapdl.get("Mat_no", "MAT", el)  # Get mat number of each elem
        young[el] = mapdl.get(
            "young", "EX", mat_no
        )  # Get Young's modulus of that material number
        young[el] = inp.CC * (rho[el] ** inp.GC)  # Change Young modulus
        mapdl.mp("EX", el_ansys, young[el])  # Set Young modulus to element
# ===============================================================================
# END OF LOOP
# ===============================================================================

# ===============================================================================
# END LABEL
# ===============================================================================
mapdl.run(":ENDSCRIPT")
mapdl.exit()
