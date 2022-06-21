"""
Remodel

Module to calculate remodeling of bone
"""

import numpy as np
from scipy.spatial import distance

# import remodeling.post


def huiskes_methods(mapdl, inp, nelem, rho):
    """Remodel material as per algorithm from Huiskes "family"
    Implemented algorithms:
    1 - Weinans1992, J. Biomechanics, Vol.25, No.12
    2 - Mullender1994, J. Biomechanics, Vol. 27, No.11 (Work-in-progress)

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables

    nelem: integer
        Number of elements in finite element mesh

    rho: float numpy array
        Numpy array of element-wise density

    Returns
    -------
    mapdl: pyMAPDL object
        Updated main object containing ansys interface object

    rho: float numpy array
        Numpy array of element-wise updated density

    young: float numpy array
        Numpy array of element-wise updated young modulus

    stimulus: float numpy array
        Numpy array of element-wise remodeling stimulus
    """

    # Loop over remodeling steps
    for i in range(inp.niter):
        status = "Remodeling iteration " + str(i + 1) + " of " + str(inp.niter)
        print(status)

        mapdl = solve_ansys(mapdl, inp)
        sed = get_sed(mapdl, nelem)
        rho, stimulus = calc_new_rho(inp, rho, sed, nelem)
        young = update_material(mapdl, inp, rho, nelem)

        # remodeling.post.plot_results(mapdl, rho, young, stimulus, i, inp)

    # Check type of results
    for array in [rho, young, stimulus]:
        check_if_num_numpy(array)

    return mapdl, rho, young, stimulus


def solve_ansys(mapdl, inp):
    """Solve static analysis with Ansys and set solution to last step
    Important: this function assumes that the elements to be remodeled
    are all assigned to element type number '1'.

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    Returns
    -------
    mapdl: pyMAPDL object
        Updated main object containing ansys interface object
    """

    mapdl.allsel()
    mapdl.slashsolu()
    mapdl.antype(0)
    mapdl.solve()
    mapdl.post1()
    mapdl.set("LAST")
    mapdl.esel("S", "TYPE", "", inp.el_typ_number)

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
    sed: float numpy array
        Numpy array of element-wise strain energy density
    """

    sed = np.zeros(nelem)
    sed = mapdl.post_processing.element_values("SEND", "ELASTIC")

    check_if_num_numpy(sed)

    return sed


def calc_new_rho(inp, rho, sed, nelem):
    """Calculate density based on stimulus and update function (d_rho/dt)

    Parameters
    ----------
    inp: input module file
        Parameter list containing all input variables

    rho: float numpy array
        Numpy array of element-wise density

    sed: float numpy array
        Numpy array of element-wise strain-energy-density

    nelem: integer
        Number of elements in finite element mesh

    Returns
    -------
    rho: float numpy array
        Numpy array of element-wise updated density
    """

    stimulus = np.zeros(nelem)
    K = inp.K
    s = inp.s
    f_fac = inp.f_fac
    r_fac = inp.r_fac

    # Check type of input
    for var in [K, s, f_fac, r_fac]:
        check_if_float(var)

    stimulus = calc_stimulus(sed, rho)
    delta_rho = calc_delta_rho_local(
        stimulus,
        K,
        s,
        f_fac,
        r_fac,
    )
    rho = rho + delta_rho

    # Limit resorption and formation
    rho[rho < inp.rho_min] = inp.rho_min
    rho[rho > inp.rho_max] = inp.rho_max

    # Check type of results
    for array in [rho, stimulus]:
        check_if_num_numpy(array)

    return rho, stimulus


def calc_stimulus(sed, rho):
    """Calculate stimulus

    Parameters
    ----------
    rho: float numpy array
        Numpy array of element-wise density

    sed: float numpy array
        Numpy array of element-wise strain-energy-density

    Returns
    -------
    stimulus: float numpy array
        Numpy array of element-wise stimulus for comparison with reference
    """

    stimulus = sed / rho

    # Check type of result
    check_if_num_numpy(stimulus)

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

    stimulus: float numpy array
        Numpy array of element-wise stimulus for density change

    Returns
    -------
    delta_rho: float numpy array
        Difference in density to be added to current value
        No variation in "lazy-zone" implies delta_rho = 0.0
    """

    delta_rho = np.zeros(len(stimulus))

    # Define limits to trigger formation/resportion remodeling
    f_lim = (1 + s) * K
    r_lim = (1 - s) * K

    # Check type of input
    for var in [K, s, f_lim, r_lim, f_fac, r_fac]:
        check_if_float(var)

    delta_rho[stimulus >= f_lim] = f_fac * (
        stimulus[stimulus >= f_lim] - f_lim
    )
    delta_rho[stimulus <= r_lim] = r_fac * (
        stimulus[stimulus <= r_lim] - r_lim
    )

    # Check type of result
    check_if_num_numpy(delta_rho)

    return delta_rho


def update_material(mapdl, inp, rho, nelem):
    """Change young modulus for each element based on new density

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    inp: input module file
        Parameter list containing all input variables

    rho: float numpy array
        Numpy array of element-wise density

    nelem: integer
        Number of elements in finite element mesh

    Returns
    -------
    young: float numpy array
        numpy array of element-wise young modulus
    """

    young = np.zeros(nelem)
    CC = inp.CC
    GC = inp.GC

    # Check type of input
    for var in [CC, GC]:
        check_if_float(var)

    mapdl.prep7()

    # Update based on density
    young = calc_young(rho, CC, GC)
    for el in range(nelem):
        elansys = el + 1
        mapdl.mp(
            "EX", elansys, young[el]
        )  # Note: mp with multiple inputs does not accept APDL implied do

    return young


def calc_young(rho, CC, GC):
    """Calculate young modulus for based on density acc. to Currey1998

    Parameters
    ----------
    rho: float numpy array
        Numpy array of element-wise density

    CC: float or int
        Linear constant in Currey's function

    GC: float or int
        Exponential constant in Currey's function

    Returns
    -------
    young: float numpy array
        Numpy array of element-wise young modulus
    """

    # Check type of input
    for var in [CC, GC]:
        check_if_float(var)

    young = CC * (rho**GC)

    # Check type of result
    check_if_num_numpy(young)

    return young


def calc_distance(v1, M1):
    """Calculate distance between reference vectors v1
    and a group of vectors presented as lines in a matrix M1
    using the cdist function from the scipy package

    Parameters
    ----------
    v1: float numpy array (defined as matrix with single line)
        Numpy array of coordinates [x, y, z] of reference vector

    M1: float numpy array/matrix (>=1)
        Numpy array(s) of coordinates [x, y, z] of group of vectors

    Returns
    -------
    dist: float numpy matrix
        Numpy array(s) of distances between vector in v1 and vector(s) in M1
    """

    dist = distance.cdist(v1, M1, "euclidean")

    # Check type of result
    check_if_num_numpy(dist)

    return dist


def check_if_num_numpy(array):
    """Determine whether the argument is a numpy array and if it has
    a numeric datatype.

    Signed integers ("i"), floats numbers ("f") are the kinds of numeric
    datatype accepted.

    Parameters
    ----------
    array : Numpy array
        The array to be checked.

    Returns
    -------
    : `bool`
        True if it is a numpy array with a numeric datatype,
        otherwise TypeError exception is raised.
        Function does NOT change the value or type of array

    """

    # Boolean, unsigned integer, signed integer, float, complex.
    _NUMERIC_KINDS = set("if")

    if not (isinstance(array, np.ndarray)):
        raise TypeError("Variable not a Numpy array, check input variables.")

    if not (array.dtype.kind in _NUMERIC_KINDS):
        raise TypeError(
            "Variable numpy array is not numeric, check input variables."
        )

    return True


def check_if_float(var):
    """Determine whether the argument is a float.

    Parameters
    ----------
    var : any
        The variable to be checked.

    Returns
    -------
    : `bool`
        True if it is a float, otherwise TypeError exception is raised.
        Function does NOT change the value or type of var

    """

    if not (isinstance(var, float)):
        raise TypeError(
            "Variable not a float. Float expected. Check input variables."
        )

    return True
