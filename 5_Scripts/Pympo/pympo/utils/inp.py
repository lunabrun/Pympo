"""
Inp

Module to supply input variables to pympo program.
"""

# Parameters unit system: SI (m, N, kg, etc.). Always check and confirm this!

# Program control
niter = 2  # Number of iterations for material remodeling

# Geometry parameters
length = 1  # Length (x) of plate (m)
height = 1  # Height (y) of plate (m)
thickness = 1  # Thickness of plate (m)
mesh_refine = 2  # Global mesh refinement level (1(fine) ... 10(rough))

# Load paramters
dist_force = 10 / thickness  # Load (Force, vertical) (N/m)

# Initial material parameters
rho_ini = 0.8  # Initial density of the plate material (bone) (kg*m^-3)
poisson = 0.3  # Initial Poisson's ratio of the plates material (bone)

# Parameters for Currey1988 Young's modulus to density function
CC = 100  # Constant in Currey's function (Pa/((kg*m^-3)^2))
GC = 2  # Constant in Currey's function (adim)
young_ini = CC * (
    rho_ini**GC
)  # Initial Young's modulus of the plate material (bone)

# Remodeling function parameters
setpoint = 0.25  # Setpoint for Strain Energy Density (SED) (J/kg)
epsilon = 0 * setpoint / 10  # 'Lazy Zone' breadth (threshold)
resorp_fac = 1  # Slope of the bone resorption function
form_fac = resorp_fac  # Slope of the bone formation function
limit_res = setpoint - epsilon  # Bottom limit to start remodeling
limit_for = setpoint + epsilon  # Top limit to start remodeling
rho_min = 0.01  # Minimal allowed density
rho_max = 1.740  # Maximum allowed density
