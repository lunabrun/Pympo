"""
Remodel

Module to calculate remodeling of bone
"""

import numpy as np


def huiskes_methods(mapdl, inp, nelem, rho):
    """Remodel material as per algorithm from Huiskes "family"

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables
    """

    # Loop over remodeling steps
    for i in range(1, inp.niter + 1):
        status = "Remodeling iteration " + str(i) + " of " + str(inp.niter + 1)
        print(status)

        mapdl = solve_ansys(mapdl)
        mapdl, sed = get_sed(mapdl, nelem)
        rho = calc_new_rho(inp, rho, sed, nelem)
        young = update_material(mapdl, inp, rho, nelem)

    return mapdl, rho, young


def solve_ansys(mapdl):
    """Solve static analysis with Ansys and set solution to last step

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object
    """

    mapdl.slashsolu()
    mapdl.antype(0)
    mapdl.solve()
    mapdl.post1()
    mapdl.set("LAST")

    return mapdl


def get_sed(mapdl, nelem):
    """Get strain energy density for each element from last solved solution

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    nelem: integer
        Number of elements in finite element mesh
    """

    sed = np.zeros(nelem)

    # Save element-wise SED result in E-Table
    mapdl.etable("et_sed", "SEND", "ELASTIC")

    # Read element-wise SED from etable and save to numpy vector
    for el in range(nelem):
        el_ansys = el + 1
        sed[el] = mapdl.get("sed", "ELEM", el_ansys, "ETAB", "et_sed")

    return mapdl, sed


def calc_new_rho(inp, rho, sed, nelem):
    """Calculate density based on stimulus and update function (d_rho/dt)

    Parameters
    ----------
    inp: input module file
        Parameter list containing all input variables

    rho: float vector
        Vector of element-wise density

    sed: float vector
        Vector of element-wise strain-energy-density

    nelem: integer
        Number of elements in finite element mesh

    Returns
    -------
    rho: float vector
        Vector of element-wise updated density
    """

    stimulus = np.zeros(nelem)
    K = inp.K
    s = inp.s
    f_fac = inp.f_fac
    r_fac = inp.r_fac

    for el in range(nelem):
        stimulus[el] = calc_stimulus(rho[el], sed[el])
        delta_rho = calc_delta_rho_local(
            stimulus[el],
            K,
            s,
            f_fac,
            r_fac,
        )
        rho[el] = rho[el] + delta_rho

        # Limit resorption and formation
        if rho[el] <= inp.rho_min:
            rho[el] = inp.rho_min
        elif rho[el] >= inp.rho_max:
            rho[el] = inp.rho_max

    return rho


def calc_stimulus(rho, sed):
    """Calculate stimulus

    Parameters
    ----------
    rho: float
        Element density

    sed: float
        Element strain-energy-density

    Returns
    -------
    stimulus: float
        Element stimulus for comparison with reference value
    """

    stimulus = sed / rho

    return stimulus


def calc_delta_rho_local(stimulus, K, s, f_fac, r_fac):
    """Calculate delta rho based on local method

    It is equal to d_rho/dt, if time step is included in inp.r_ or
    inp.f_fac.
    It considers contribution only from the element/local data.

    See Weinans1992 paper for details.

    Parameters
    ----------
    K: float
        Setpoint for Strain Energy Density (SED)

    s: float
        "Lazy-zone" breadth (i.e., threshold)

    f_fac, r_fac: float
        Factors (slope) for resorption/formation function

    stimulus: float
        Element stimulus for density change

    Returns
    -------
    delta_rho: float
        Difference in density to be added to current value
        No variation in "lazy-zone" implies delta_rho = 0.0
    """

    # Define limits to trigger formation/resportion remodeling
    f_lim = (1 + s) * K
    r_lim = (1 - s) * K

    if stimulus > f_lim:
        delta_rho = f_fac * (stimulus - f_lim)
    elif stimulus < r_lim:
        delta_rho = r_fac * (stimulus - r_lim)
    else:
        delta_rho = 0.0

    check_if_number(delta_rho)

    return delta_rho


def update_material(mapdl, inp, rho, nelem):
    """Change young modulus for each element based on new density

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables

    rho: float vector
        Vector of element-wise density

    nelem: integer
        Number of elements in finite element mesh
    """

    young = np.zeros(nelem)
    CC = inp.CC
    GC = inp.GC

    mapdl.prep7()

    for el in range(nelem):
        el_ansys = el + 1

        # Get mat number and young modulus of each elem
        mat_no = mapdl.get("mat_no", "MAT", el)
        young[el] = mapdl.get("young", "EX", mat_no)

        # Update based on density
        young[el] = calc_young(rho[el], CC, GC)
        mapdl.mp("EX", el_ansys, young[el])

    return young


def calc_young(rho, CC, GC):
    """Calculate young modulus for based on density acc. to Currey1998

    Parameters
    ----------
    rho: float
        Element density

    CC: float or int
        Linear constant in Currey's function

    GC: float or int
        Exponential constant in Currey's function

    Returns
    -------
    young: float
        Element young modulus
    """

    young = CC * (rho**GC)

    check_if_number(young)

    return young


def check_if_number(var):
    """Function to check if a variable is a number (float or int)

    Useful to avoid errors due to following behaviours:
    2*"a" = "aa"
    3*[1] = [1 1 1]

    Parameters
    ----------
    var: any
        Variable to be checked

    Returns
    -------
    True: true
        True if ok, otherwise TypeError exception is raised.
        Function does NOT change the value or type of var
    """

    if not (isinstance(var, float) or isinstance(var, int)):
        raise TypeError("Result has wrong type, check input variables.")
    return True
