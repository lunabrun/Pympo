"""
Post

Module to post-process and plot results for pympo program.
"""
import os
from ansys.mapdl import core as pymapdl

# Define common theme for all plots
my_theme = pymapdl.MapdlTheme()
my_theme.background = "white"
my_theme.cmap = "jet"  # colormap
my_theme.axes.show = False
my_theme.show_scalar_bar = False
my_theme.cpos = "xy"


def plot_results(mapdl, rho, young, stimulus, i, inp):
    """Drive plotting of results

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    rho: float vector
        Vector of element-wise density

    young: float vector
        Vector of element-wise young modulus
    """

    grid = mapdl.mesh.grid
    grid.cell_data["Density"] = rho
    grid.cell_data["Young Modulus"] = young
    grid.cell_data["Stimulus"] = stimulus
    grid.save(os.getcwd() + inp.out_dir + "/pympo_res00" + str(i) + ".vtk")

    plot_scalar(grid, rho, "rho00" + str(i), inp)
    plot_scalar(grid, young, "young00" + str(i), inp)


def plot_scalar(grid, scalar, scalar_name, inp):
    """Plot generic scalar field over mesh

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    scalar: vector
        Vector of scalars to be plotted
    """

    # Parameters for scalar bar
    sbar_kwargs = {"color": "black", "title": scalar_name}

    grid.plot(
        off_screen=True,
        screenshot=os.getcwd() + inp.out_dir + "/" + scalar_name + ".png",
        scalars=scalar,
        show_scalar_bar=True,
        scalar_bar_args=sbar_kwargs,
        show_edges=True,
        theme=my_theme,
        cpos="xy",  # for 2D meshes
    )
