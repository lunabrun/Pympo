"""Script generated by ansys-mapdl-core version 0.61.2"""
import os
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(
    run_location=os.getcwd(), loglevel="WARNING", print_com=True
)

# ===============================================================================
# PROGRAM:          2DPlate_Lian2010
#
# PROJEKT:          REMODELING: Iterative adaptation of local material
# properties to local mechanical environment.
# TASK:             2D model of a plate with a linear varying force on top
# with initially constant material properties undergoes an
# iterative change of element material properties similar
# to bone remodeling.  The changing rate is modeled dependent
# on the local strain energy density as per Lian2010
# 3 showed algorithms.
# Remodeling script based on Simon, Wieland (Uni Ulm, 2011)
# Paramters taken from papers Lian2010, Weinans1992, Mullender1993
# AUTHOR:           Bruno Luna
# LAST CHANGES:     23.03.2022
#
# COMPUTER:         MHH PC
# OPERATING SYSTEM: Windows
# ANSYS Version:    License: Mechanical Enterprise 2022 R1
#
# CALL:             /INPUT,2DPlate_Lian2010.inp
#
# ===============================================================================

# === Initialization
mapdl.finish()  # Stops all modules (preprocessor, solution, postprocessor)
mapdl.run(
    "/CLEAR              "
)  # Start a new analysis, delete the old database (file.db)
mapdl.run("/PLOPTS,INFO,AUTO ")  # Good old contour labeling style

# ===============================================================================
# Parameters (in SI: m, N, kg, etc.)
# ===============================================================================

# --- Program control
mapdl.run(
    "nIter    =     50        	"
)  # Number of iterations for material remodeling

# --- Geometry parameters
mapdl.run("Length   =     1        	")  # Length (x) of plate (m)
mapdl.run("Height   =     1        	")  # Height (y) of plate (m)
mapdl.run("Thickn   =     1  		      	")  # Thickness of plate (m)
mapdl.run(
    "Meshrefine =     2	    	"
)  # Global mesh refinement level (1(fine) ... 10(rough))

# --- Load paramters
mapdl.run("DistForce    =  10/Thickn   ")  # Load (Force, vertical) (N/m)

# --- Initial material parameters
mapdl.run(
    "Density_ini = 0.8			"
)  # Initial density of the plate material (bone) (kg*m^-3)
mapdl.run(
    "Poiss_ini	= 0.3       	"
)  # Initial Poisson's ratio of the plates material (bone)

# --- Parameters for Currey1988 Young's modulus to density function
mapdl.run("cC	= 100	")  # Constant in Currey's function (Pa/((kg*m^-3)^2))
mapdl.run("gC = 2		")  # Constant in Currey's function (adim)
mapdl.run(
    "Young_ini = cC*(Density_ini**gC) "
)  # Initial Young's modulus of the plate material (bone)

# --- Remodeling function parameters
mapdl.run(
    "Setpoint	= 0.25			"
)  # Setpoint for Strain Energy Density (SED) (J/kg)
mapdl.run("Epsilon		= 0*Setpoint/10	")  # 'Lazy Zone' breadth (threshold)
mapdl.run("ResorpFac	= 1				")  # Slope of the bone resorption function
mapdl.run("FormFac		= ResorpFac		")  # Slope of the bone formation function
mapdl.run(
    "Limit_Res	= Setpoint - Epsilon "
)  # Bottom limit to start remodeling
mapdl.run("Limit_For	= Setpoint + Epsilon ")  # Top limit to start remodeling
mapdl.run("Rho_min		= .010	")  # Minimal allowed density
mapdl.run("Rho_max		= 1.740	")  # Maximum allowed density

# ===============================================================================
# A. Preprocessor (Setting up the model)
# ===============================================================================
mapdl.prep7()  # Switch to the preprocessor modul

# === Build the geometry by means of bottom-up method
# --- Create plate
mapdl.k(1, 0.0, 0.0, 0.0)  # Define keypoint via its coordinates x, y, z
mapdl.k(2, "Length", 0.0, 0.0)  # Define keypoint via its coordinates x, y, z
mapdl.k(
    3, "Length", "Height", 0.0
)  # Define keypoint via its coordinates x, y, z
mapdl.k(4, 0.0, "Height", 0.0)  # Define keypoint via its coordinates x, y, z
mapdl.lstr(1, 2)  # Connect keypoints 1 and 2 to create line 1
mapdl.lstr(2, 3)  # Connect keypoints to create a line
mapdl.lstr(3, 4)  # Connect keypoints to create a line
mapdl.lstr(4, 1)  # Connect keypoints to create a line
mapdl.al("ALL")  # Create area by all selected lines (1, 2, 3, 4)
mapdl.allsel()  # Select everything
mapdl.aplot()  # Plot areas

# === Meshing
mapdl.et(
    1, "PLANE182"
)  # Define the local element type 1 as a PLANE182 element
mapdl.keyopt(
    1, 1, 2
)  # Sets key option 1 (of elem type 1) to 2 (enhanc. strain formul.)
mapdl.keyopt(
    1, 3, 0
)  # Sets key option 3 (of elem type 1) to 3 (plane stress w/ thickn)

# --- Define real constants
# R,1,Thickn              	  Set thicknessess of the plate in 'real set' no. 1
mapdl.smrtsize(
    "Meshrefine"
)  # Global mesh refinement level (1(fine) ... 10(rough))
mapdl.amesh("ALL")  # Meshing areas with this number
mapdl.eplot()  # Plot elements
mapdl.get("nElem", "ELEM", 0, "COUNT")  # Get number of elements

# ===============================================================================

# === Initial definition of material properties, one for each of the FE
mapdl.run("*DIM,AR_Rho,ARRAY,nElem    ")  # Create a field (vector)
mapdl.allsel()

with mapdl.non_interactive:
    mapdl.run("*DO,el,1,nElem               ")  # Loop over all elements
    mapdl.mp("EX", "el", "Young_ini")  # Assign Young modulus
    mapdl.mp("PRXY", "el", "Poiss_ini")  # Assign Poisson number
    mapdl.emodif("el", "MAT", "el")  # Assign material type el to element el
    mapdl.run("AR_Rho(el) = Density_ini	 ")  # Initial density for all elements
    mapdl.run("*ENDDO")

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
    "PRES", 0, "X", 0.0, "-DistForce/Length"
)  # Distributed force definition (linear gradient)
mapdl.nsel(
    "S", "LOC", "Y", "Height"
)  # Select location for application of linear varying force
mapdl.sf("ALL", "PRES", "DistForce")  # Application of force
mapdl.sfgrad()  # 'Turn off' SFGRAD
mapdl.allsel()  # Select all entries

# ===============================================================================
# === Arrays creation for element related fields
mapdl.run("*DIM,AR_ActVal,ARRAY,nElem		")  # Create a field (vector)
mapdl.run("*DIM,AR_EMod,ARRAY,nElem        ")  # Create a field (vector)
mapdl.run("*DIM,AR_DeltaRho,ARRAY,nElem    ")  # Create a field (vector)
# ===============================================================================

# B. START REMODELING LOOP

# ===============================================================================

with mapdl.non_interactive:
    mapdl.run("*DO,iter,1,nIter				")  # Loop over remodeling steps
    # ============================================================================
    # ====== Solution
    mapdl.run("/SOLU                        ")  # Switch to the solution module
    mapdl.antype(0)  # Select the static analysis type
    # NLGEOM,on					 Allow large deformation/rotation
    mapdl.solve()  # Solve current load step
    # ============================================================================
    # ====== Postprocessor
    mapdl.run(
        "/POST1                       "
    )  # Switch to the postprocessor module
    mapdl.set("LAST")  # Read results from last step
    # ============================================================================
    # === Read Strain Energy Density (SED)
    mapdl.etable(
        "et_SED", "SEND", "ELASTIC"
    )  # Save element-wise SED result in E-Table
    mapdl.run(
        "*DO,el,1,nElem                     		"
    )  # Loop over all elements
    mapdl.run(
        "*GET,AR_ActVal(el),ELEM,el,ETAB,et_SED   "
    )  # ... and read element result
    mapdl.run("*ENDDO")
    # ============================================================================

    # === Output intermediate result
    mapdl.title("Strain-Energy-Density (SED) Schritt = %iter%")
    # /DSCALE,1,1.0
    # /CONTOUR,,,0,,2*Limit_For
    mapdl.plesol("SEND", "ELASTIC")
    # === Prepare remodeling (i.e., calculate dp/dt)
    mapdl.run("*DO,el,1,nElem            ")  # Loop over all elements
    mapdl.run("Stimulus = AR_ActVal(el)/AR_Rho(el)")
    mapdl.run("*IF,Stimulus,LT,Limit_Res,THEN")
    mapdl.run("AR_DeltaRho(el) = ResorpFac*(Stimulus - Limit_Res)")
    mapdl.run("*ELSEIF,Stimulus,GT,Limit_For,THEN")
    mapdl.run("AR_DeltaRho(el) = FormFac*(Stimulus - Limit_For)")
    mapdl.run("*ELSE")
    mapdl.run("AR_DeltaRho(el) = 0.0")
    mapdl.run("*ENDIF")
    mapdl.run("AR_Rho(el) = AR_Rho(el) + AR_DeltaRho(el)")
    mapdl.run("*IF,AR_Rho(el),LE,Rho_min,THEN    	")  # Limit resorption
    mapdl.run("AR_Rho(el) = Rho_min")
    mapdl.run("*ELSEIF,AR_Rho(el),GE,Rho_max,THEN ")  # Limit formation
    mapdl.run("AR_Rho(el) = Rho_max")
    mapdl.run("*ENDIF")
    mapdl.run("*ENDDO")

    # ============================================================================
    # === Remodeling, actually change material

    mapdl.prep7()  # Switch to Preprocor
    mapdl.run("*DO,el,1,nElem            			")  # Loop over all elements
    mapdl.run(
        "*GET,Mat_no,MAT,el        		"
    )  # Get material number of each elem
    mapdl.run(
        "*GET,AR_EMod(el),EX,Mat_no        "
    )  # Get Young's modulus of that material number
    mapdl.run("AR_EMod(el) = cC*(AR_Rho(el)**gC) ")  # Change Young's modulus
    mapdl.mp("EX", "el", "AR_EMod(el)")  # Set new Young's modulus to element
    mapdl.run("*ENDDO")
    mapdl.run("*ENDDO")

# ===============================================================================
# END OF LOOP
# ===============================================================================

# ===============================================================================
# C. POSTPROCESSOR
# ===============================================================================
mapdl.run("/POST1							")  # Switch to Postprocesser
# ===============================================================================
# === Plot of Young's modulus
# --- Create element table; initially with EPTOX, to be overwritten later
mapdl.etable("et_Emod", "EPTO", "X")  # for visualization of Young's modulus
# --- Fill element table with Young modulus (including loop over all elements)
# *vput,AR_EMod(1),ELEM,1,ETAB,et_Emod,0
# --- Fill element table with density (including loop over all elements)
mapdl.run("*vput,AR_Rho(1),ELEM,1,ETAB,et_Emod,0")
# --- Plot
# /CONTOUR,,,Young_min,,Young_max
# /TITLE,'Young modulus distribution after iteration = %iter%'
mapdl.run("/CONTOUR,,,Rho_min,,Rho_max")
mapdl.title("Density")
mapdl.pletab("et_Emod", "NOAVG")

# === Plot of SED
# /TITLE,'Strain Energy Density (SED) iteration = %iter%'
# /DSCALE,1,1.0
# /CONTOUR,,,0,,2*Limit_For
# PLESOL,SEND,ELASTIC

# ===============================================================================
# END LABEL
# ===============================================================================

mapdl.run(":ENDSCRIPT")
mapdl.exit()
