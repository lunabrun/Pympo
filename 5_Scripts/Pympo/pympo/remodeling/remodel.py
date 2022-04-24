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
    """

    stimulus = np.zeros(nelem)

    for el in range(nelem):
        stimulus[el] = calc_stimulus(rho[el], sed[el])
        delta_rho = calc_delta_rho_local(inp, stimulus[el])
        rho[el] = rho[el] + delta_rho[el]

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


def calc_delta_rho_local(inp, stimulus):
    """Calculate delta rho based on local method

    It is equal to d_rho/dt, if time step is included in inp.resorp- or
    inp-form_fac. It considers contribution only from the element/local data.

    See Weinans1992 paper for details.

    Parameters
    ----------
    inp: input module file
        Parameter list containing all input variables

    stimulus: float
        Element stimulus for density change

    Returns
    -------
    delta_rho: float
        Difference in density to be added to current value
    """

    # No variation in "lazy-zone"
    delta_rho = 0.0

    if stimulus < inp.limit_res:
        delta_rho = inp.resorp_fac * (stimulus - inp.limit_res)
    elif stimulus > inp.limit_for:
        delta_rho = inp.form_fac * (stimulus - inp.limit_for)

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

    CC: float
        Linear constant in Currey's function

    GC: float
        Exponential constant in Currey's function

    Returns
    -------
    young: float
        Element young modulus
    """

    young = CC * (rho**GC)

    return young
