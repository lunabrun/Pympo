"""
Inp

Module to supply input variables to pympo program.
"""

# Parameters unit system: SI (m, N, kg, etc.). Always check and confirm this!

# Program control
niter = 50  # Number of iterations for material remodeling

# Geometry parameters
length = 1.0  # Length (x) of plate (m)
height = 1.0  # Height (y) of plate (m)
thickness = 1.0  # Thickness of plate (m)
mesh_refine = 2  # Global mesh refinement level (1(fine) ... 10(rough))

# Load paramters
dist_force = 10 / thickness  # Load (Force, vertical) (N/m)

# Initial material parameters
rho_ini = 0.8  # Initial density of the plate material (bone) (kg*m^-3)
poisson = 0.3  # Initial Poisson's ratio of the plates material (bone)

# Parameters for Currey1988 Young's modulus to density function
CC = 100.0  # Constant in Currey's function (Pa/((kg*m^-3)^2))
GC = 2.0  # Constant in Currey's function (adim)
young_ini = CC * (rho_ini**GC)  # Initial Young's modulus of the bone

# Remodeling function parameters
K = 0.25  # Setpoint for Strain Energy Density (SED) (J/kg)
s = 0.0  # 'Lazy Zone' breadth (threshold)
f_fac = 1.0  # Slope of the bone formation function
r_fac = 1.0  # Slope of the bone resorption function
rho_min = 0.01  # Minimal allowed density
rho_max = 1.740  # Maximum allowed density

# Output parameters
out_dir = "/pympo/ansys_tmp"
