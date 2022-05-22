"""
Remodel

Module to calculate remodeling of bone
"""

import numpy as np

import post


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
    for i in range(inp.niter):
        status = "Remodeling iteration " + str(i + 1) + " of " + str(inp.niter)
        print(status)

        mapdl = solve_ansys(mapdl)
        sed = get_sed(mapdl, nelem)
        rho, stimulus = calc_new_rho(inp, rho, sed, nelem)
        young = update_material(mapdl, inp, rho, nelem)

    post.plot_results(mapdl, rho, young, stimulus, i, inp)

    return mapdl, rho, young, stimulus


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

    # Plot SED solution
    # mapdl.plesol("SEND", "ELASTIC")

    return mapdl


def get_sed(mapdl, nelem):
    """Get strain energy density for each element from last solved solution

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    nelem: integer
        Number of elements in finite element mesh

    Returns
    -------
    sed: float vector
        Vector of element-wise strain energy density
    """

    sed = np.zeros(nelem)
    sed = mapdl.post_processing.element_values("SEND", "ELASTIC")

    return sed


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

    stimulus = calc_stimulus(sed, rho)
    for el in range(nelem):
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

    return rho, stimulus


def calc_stimulus(sed, rho):
    """Calculate stimulus

    Parameters
    ----------
    rho: float vector
        Vector of element-wise density

    sed: float vector
        Vector of element-wise strain-energy-density

    Returns
    -------
    stimulus: float vector
        Vector of element-wise stimulus for comparison with reference value
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

    check_if_numeric(delta_rho)

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

    Returns
    -------
    young: float vector
        vector of element-wise young modulus
    """

    young = np.zeros(nelem)
    CC = inp.CC
    GC = inp.GC

    mapdl.prep7()

    # Update based on density
    young = calc_young(rho, CC, GC)
    for el in range(nelem):
        elansys = el + 1
        mapdl.mp("EX", elansys, young[el])  # THIS STILL NOT WORKING AS VECTOR!

    return young


def calc_young(rho, CC, GC):
    """Calculate young modulus for based on density acc. to Currey1998

    Parameters
    ----------
    rho: float vector
        Vector of element-wise density

    CC: float or int
        Linear constant in Currey's function

    GC: float or int
        Exponential constant in Currey's function

    Returns
    -------
    young: float vectpr
        vector of element-wise young modulus
    """

    young = CC * (rho**GC)

    # check_if_number(young)

    return young


def check_if_numeric(array):
    """Determine whether the argument has a numeric datatype, when
    converted to a NumPy array.

    Signed integers ("i"), floats numbers ("f") are the kinds of numeric
    datatype accepted.

    Parameters
    ----------
    array : array-like
        The array to check.

    Returns
    -------
    is_numeric : `bool`
        True if the array has a numeric datatype,
        otherwise TypeError exception is raised.
        Function does NOT change the value or type of var

    """

    # Boolean, unsigned integer, signed integer, float, complex.
    _NUMERIC_KINDS = set("if")

    if not (np.asarray(array).dtype.kind in _NUMERIC_KINDS):
        raise TypeError("Result has wrong type, check input variables.")
    return True
