"""
Post

Module to post-process and plot results for pympo program.
"""
from ansys.mapdl import core as pymapdl


# Define common theme for all plots
my_theme = pymapdl.MapdlTheme()
my_theme.background = "white"
my_theme.cmap = "jet"  # colormap
my_theme.axes.show = False
my_theme.show_scalar_bar = False
my_theme.cpos = "xy"


def plot_results(mapdl, rho, young, stimulus, i, run_dir):
    """Drive plotting of results

    Parameters
    ----------
    mapdl: pyMAPDL object
        Main object containing ansys interface object

    rho: float vector
        Vector of element-wise density

    young: float vector
        Vector of element-wise young modulus

    stimulus: float vector
        Vector of element-wise stimulus

    i: integer
        Step for post-processing

    run_dir: string
        Directory for saving post-processing files
    """

    grid = mapdl.mesh.grid
    list_of_outputs = [
        ("Rho", rho),
        ("Young", young),
        ("Stimulus", stimulus),
    ]

    for index, tuple in enumerate(list_of_outputs):
        grid.cell_data[tuple[0]] = tuple[1]
        plot_scalar(grid, tuple[1], tuple[0] + "00" + str(i), run_dir)

    grid.save(run_dir + "/pympo_res00" + str(i) + ".vtk")


def plot_scalar(grid, scalar, scalar_name, run_dir):
    """Plot generic scalar field over mesh

    Parameters
    ----------
    grid: pyMAPDL grid object
        Grid object containing ansys mesh information

    scalar: vector
        Vector of scalars to be plotted

    scalar_name: scalar_name
        Name of scalar to be plotted

    run_dir: string
        Directory for saving post-processing files
    """

    # Parameters for scalar bar
    sbar_kwargs = {"color": "black", "title": scalar_name}

    grid.plot(
        off_screen=True,
        screenshot=run_dir + "/" + scalar_name + ".png",
        scalars=scalar,
        show_scalar_bar=True,
        scalar_bar_args=sbar_kwargs,
        show_edges=True,
        theme=my_theme,
        cpos="xy",  # for 2D meshes
    )
