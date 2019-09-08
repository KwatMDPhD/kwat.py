from KDEpy import FFTKDE

from .ALMOST_ZERO import ALMOST_ZERO
from .compute_vector_bandwidth import compute_vector_bandwidth
from .FRACTION_GRID_EXTENSION_FOR_ESTIMATING_KERNEL_DENSITY import (
    FRACTION_GRID_EXTENSION_FOR_ESTIMATING_KERNEL_DENSITY,
)
from .make_mesh_grid_point_x_dimension import make_mesh_grid_point_x_dimension
from .make_vector_grid import make_vector_grid
from .N_GRID_FOR_ESTIMATING_KERNEL_DENSITY import N_GRID_FOR_ESTIMATING_KERNEL_DENSITY
from .plot_mesh_grid import plot_mesh_grid


def estimate_element_x_dimension_kernel_density(
    element_x_dimension,
    dimension_bandwidths=None,
    dimension_bandwidth_factors=None,
    dimension_grid_mins=None,
    dimension_grid_maxs=None,
    dimension_fraction_grid_extensions=None,
    dimension_n_grids=None,
    plot=True,
    dimension_names=None,
):

    n_dimension = element_x_dimension.shape[1]

    if dimension_bandwidths is None:

        dimension_bandwidths = tuple(
            compute_vector_bandwidth(element_x_dimension[:, i])
            for i in range(n_dimension)
        )

    if dimension_bandwidth_factors is not None:

        dimension_bandwidths = tuple(
            dimension_bandwidths[i] * dimension_bandwidth_factors[i]
            for i in range(n_dimension)
        )

    if dimension_grid_mins is None:

        dimension_grid_mins = (None,) * n_dimension

    if dimension_grid_maxs is None:

        dimension_grid_maxs = (None,) * n_dimension

    if dimension_fraction_grid_extensions is None:

        dimension_fraction_grid_extensions = (
            FRACTION_GRID_EXTENSION_FOR_ESTIMATING_KERNEL_DENSITY,
        ) * n_dimension

    if dimension_n_grids is None:

        dimension_n_grids = (N_GRID_FOR_ESTIMATING_KERNEL_DENSITY,) * n_dimension

    mesh_grid_point_x_dimension = make_mesh_grid_point_x_dimension(
        (
            make_vector_grid(
                element_x_dimension[:, i],
                dimension_grid_mins[i],
                dimension_grid_maxs[i],
                dimension_fraction_grid_extensions[i],
                dimension_n_grids[i],
            )
            for i in range(n_dimension)
        )
    )

    mesh_grid_point_kernel_density = (
        (
            FFTKDE(bw=dimension_bandwidths)
            .fit(element_x_dimension)
            .evaluate(mesh_grid_point_x_dimension)
        )
    ).clip(min=ALMOST_ZERO)

    if plot:

        plot_mesh_grid(
            mesh_grid_point_x_dimension,
            mesh_grid_point_kernel_density,
            title_text="Kernel Density",
            dimension_names=dimension_names,
        )

    return mesh_grid_point_x_dimension, mesh_grid_point_kernel_density
