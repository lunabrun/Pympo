"""
Remodel

Module to calculate remodeling of bone
"""

import numpy as np


def remodel_weinans92(mapdl, inp, nelem, rho):
    """Remodel material as per algorithm in Weinans92 paper

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object
    inp: input module file
        Parameter list containing all input variables
    """
    # Vectors creation for element related fields
    delta_rho = np.zeros(nelem)
    sed = np.zeros(nelem)
    young = np.zeros(nelem)

    # Loop over remodeling steps
    for iter in range(1, inp.niter + 1):
        # Print status
        msg = "Remodeling iteration " + str(iter) + " of " + str(inp.niter + 1)
        print(msg)

        # Solution of static analysis
        mapdl.slashsolu()
        mapdl.antype(0)
        mapdl.solve()

        # Postprocessor for last step
        mapdl.post1()
        mapdl.set("LAST")

        # Read Strain Energy Density (SED)
        # Save element-wise SED result in E-Table
        mapdl.etable("et_sed", "SEND", "ELASTIC")
        # Loop over all elements and read element result
        for el in range(nelem):
            el_ansys = el + 1
            sed[el] = mapdl.get("sed", "ELEM", el_ansys, "ETAB", "et_sed")

        # Prepare remodeling (i.e., calculate d_rho/dt)
        for el in range(nelem):
            stimulus = sed[el] / rho[el]
            if stimulus < inp.limit_res:
                delta_rho[el] = inp.resorp_fac * (stimulus - inp.limit_res)
            elif stimulus > inp.limit_for:
                delta_rho[el] = inp.form_fac * (stimulus - inp.limit_for)
            else:
                delta_rho[el] = 0.0
            rho[el] = rho[el] + delta_rho[el]

            # Limit resorption and formation
            if rho[el] <= inp.rho_min:
                rho[el] = inp.rho_min
            elif rho[el] >= inp.rho_max:
                rho[el] = inp.rho_max

        # Remodeling (i.e., actually change material properties)
        # Overwrite young modulus of material number with new value
        mapdl.prep7()
        for el in range(nelem):
            el_ansys = el + 1
            mat_no = mapdl.get(
                "mat_no", "MAT", el
            )  # Get mat number of each elem
            young[el] = mapdl.get("young", "EX", mat_no)
            young[el] = inp.CC * (rho[el] ** inp.GC)
            mapdl.mp("EX", el_ansys, young[el])

        return mapdl, rho, young
