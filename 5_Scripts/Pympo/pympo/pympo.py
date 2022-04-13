import os
import numpy as np
from ansys.mapdl.core import launch_mapdl

# ===============================================================================
# PROGRAM: pympo
# 
# OBJECTIVE: Iterative adaptation of local material
# properties to local mechanical environment.
#
# EXAMPLE: 2D model of a plate with a linear varying force on top
# with initially constant material properties undergoes an
# iterative change of element material properties similar
# to bone remodeling.  
#
# The changing rate is modeled dependent on the local strain energy density as 
# per Lian2010 3 showed algorithms.
#
# Remodeling workflow based on Simon, Wieland (Uni Ulm, 2011)
# Algorithm and parameters taken from papers Lian2010, Weinans1992, Mullender1993
# 
# AUTHOR:           Bruno Luna
# 
# COMPUTER:         MHH PC
# OPERATING SYSTEM: Windows
# ANSYS Version:    License: Mechanical Enterprise 2022 R1
# 
# ===============================================================================

# === Initialization
mapdl = launch_mapdl(run_location=os.getcwd() + "/ansys_tmp",loglevel="WARNING", print_com=True)
mapdl.finish()                      # Stops all modules (preprocessor, solution, postprocessor)
mapdl.run("/CLEAR              ")   # Start a new analysis, delete the old database (file.db)
mapdl.run("/PLOPTS,INFO,AUTO ")     # Good old contour labeling style

# ===============================================================================
# Parameters (in SI: m, N, kg, etc.)
# ===============================================================================

# --- Program control
niter = 2  # Number of iterations for material remodeling

# --- Geometry parameters
Length = 1  # Length (x) of plate (m)
Height = 1  # Height (y) of plate (m)
Thickn = 1  # Thickness of plate (m)
mesh_refine = 2  # Global mesh refinement level (1(fine) ... 10(rough))

# --- Load paramters
DistForce = 10/Thickn   # Load (Force, vertical) (N/m)

# --- Initial material parameters
Density_ini = 0.8   # Initial density of the plate material (bone) (kg*m^-3)
Poiss_ini = 0.3     # Initial Poisson's ratio of the plates material (bone)

# --- Parameters for Currey1988 Young's modulus to density function
cC = 100    # Constant in Currey's function (Pa/((kg*m^-3)^2))
gC = 2      # Constant in Currey's function (adim)
Young_ini = cC*(Density_ini**gC)    # Initial Young's modulus of the plate material (bone)

# --- Remodeling function parameters
Setpoint = 0.25     # Setpoint for Strain Energy Density (SED) (J/kg)
Epsilon = 0*Setpoint/10 # 'Lazy Zone' breadth (threshold)
ResorpFac = 1       # Slope of the bone resorption function
FormFac = ResorpFac # Slope of the bone formation function
Limit_Res = Setpoint - Epsilon  # Bottom limit to start remodeling
Limit_For = Setpoint + Epsilon  # Top limit to start remodeling
Rho_min = 0.01      # Minimal allowed density
Rho_max = 1.740     # Maximum allowed density

# ===============================================================================
# A. Preprocessor (Setting up the model)
# ===============================================================================
mapdl.prep7()  # Switch to the preprocessor modul

# === Build the geometry
# --- Create plate
mapdl.k(1, 0.0, 0.0, 0.0)       # Define keypoint via its coordinates x, y, z
mapdl.k(2, Length, 0.0, 0.0)    # Define keypoint via its coordinates x, y, z
mapdl.k(3, Length, Height, 0.0) # Define keypoint via its coordinates x, y, z
mapdl.k(4, 0.0, Height, 0.0)    # Define keypoint via its coordinates x, y, z
mapdl.lstr(1, 2)    # Connect keypoints 1 and 2 to create line 1
mapdl.lstr(2, 3)    # Connect keypoints to create a line
mapdl.lstr(3, 4)    # Connect keypoints to create a line
mapdl.lstr(4, 1)    # Connect keypoints to create a line
mapdl.al("ALL")     # Create area by all selected lines (1, 2, 3, 4)
mapdl.allsel()      # Select everything
mapdl.aplot()       # Plot areas

# === Meshing
mapdl.et(1, "PLANE182") # Define the local element type 1 as a PLANE182 element
mapdl.keyopt(1, 1, 2)   # Sets key option 1 (of elem type 1) to 2 (enhanc. strain formul.)
mapdl.keyopt(1, 3, 0)   # Sets key option 3 (of elem type 1) to 3 (plane stress w/ thickn)

# --- Define real constants
mapdl.smrtsize(mesh_refine)    # Global mesh refinement level (1(fine) ... 10(rough))
mapdl.amesh("ALL")  # Meshing areas with this number
mapdl.eplot()       # Plot elements
nelem = int(mapdl.get("nElem", "ELEM", 0, "COUNT"))  # Get number of elements

# ===============================================================================

# === Initial definition of material properties, one for each of the FE
AR_Rho = np.zeros(nelem)  # Create a field (vector)
mapdl.allsel()

for el in range(nelem):
    el_ansys = el + 1
    mapdl.mp("EX", el_ansys, Young_ini)  # Assign Young modulus
    mapdl.mp("PRXY", el_ansys, Poiss_ini)# Assign Poisson number
    mapdl.emodif(el_ansys, "MAT", el_ansys)  # Assign material type el to element el
    AR_Rho[el] = Density_ini

# === Apply Load and Boundary Conditions
# --- Displacement boundary conditions
mapdl.nsel("S", "LOC", "Y", 0.0)  # Select all nodes at y = 0 (bottom side)
mapdl.d("ALL", "UY", 0.0)  # Set displacement uy to zero for selected nodes
mapdl.allsel()  # Select all entities
mapdl.nsel("S", "LOC", "Y", 0.0)  # Select all nodes at y = 0 (bottom side)
mapdl.nsel("R", "LOC", "X", 0.0)  # From previous selected nodes, get bottom left corner (x=0,y=0)
mapdl.d("ALL", "UY", 0.0)  # Set displacement uy to zero for selected nodes
mapdl.d("ALL", "UX", 0.0)  # Set displacement ux to zero for selected node
mapdl.allsel()  # Select all entities

# --- Applying the load
mapdl.sfgrad("PRES", 0, "X", 0.0, -DistForce/Length)  # Distributed force definition (linear gradient)
mapdl.nsel("S", "LOC", "Y", Height)  # Select location for application of linear varying force
mapdl.sf("ALL", "PRES", DistForce)  # Application of force
mapdl.sfgrad()  # 'Turn off' SFGRAD
mapdl.allsel()  # Select all entries

# ===============================================================================
# === Arrays creation for element related fields
AR_ActVal = np.zeros(nelem)  # Create a field (vector)
AR_EMod = np.zeros(nelem)  # Create a field (vector)
AR_DeltaRho = np.zeros(nelem)  # Create a field (vector)

# ===============================================================================
# B. START REMODELING LOOP
# ===============================================================================

for iter in range(1,niter+1): # Loop over remodeling steps
    # ============================================================================
    # ====== Solution
    mapdl.slashsolu()  # Switch to the solution module
    mapdl.antype(0)  # Select the static analysis type
    mapdl.solve()  # Solve current load step
    # ============================================================================
    # ====== Postprocessor
    mapdl.run("/POST1                       ")  # Switch to the postprocessor module
    mapdl.post1()
    mapdl.set("LAST")  # Read results from last step
    # ============================================================================
    # === Read Strain Energy Density (SED)
    mapdl.etable("et_SED", "SEND", "ELASTIC")  # Save element-wise SED result in E-Table
    for el in range(nelem): # Loop over all elements
        el_ansys = el + 1
        AR_ActVal[el] = mapdl.get("AR_ActVal", "ELEM", el_ansys, "ETAB","et_SED") # ... and read element result
    # ============================================================================

    # === Prepare remodeling (i.e., calculate dp/dt)
    for el in range(nelem): # Loop over all elements
        stimulus = AR_ActVal[el]/AR_Rho[el]
        if (stimulus < Limit_Res):
            AR_DeltaRho[el] = ResorpFac*(stimulus - Limit_Res)
        elif (stimulus > Limit_For):
            AR_DeltaRho[el] = FormFac*(stimulus - Limit_For)
        else:
            AR_DeltaRho[el] = 0.0
        AR_Rho[el] = AR_Rho[el] + AR_DeltaRho[el]
        
        if (AR_Rho[el] <= Rho_min): # Limit resorption
            AR_Rho[el] = Rho_min
        elif (AR_Rho[el] >= Rho_max): # Limit formation
            AR_Rho[el] = Rho_min

    # ============================================================================
    # === Remodeling, actually change material

    mapdl.prep7()  # Switch to Preprocessor
    for el in range(nelem): # Loop over all elements
        el_ansys = el + 1
        mat_no = mapdl.get("Mat_no", "MAT", el) # Get material number of each elem
        AR_EMod[el] = mapdl.get("AR_EMod", "EX", mat_no)    # Get Young's modulus of that material number
        AR_EMod[el] = cC*(AR_Rho[el]**gC)       # Change Young's modulus
        mapdl.mp("EX", el_ansys, AR_EMod[el])  # Set new Young's modulus to element
# ===============================================================================
# END OF LOOP
# ===============================================================================

# ===============================================================================
# END LABEL
# ===============================================================================
mapdl.run(":ENDSCRIPT")
mapdl.exit()
