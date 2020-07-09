from numpy import (
    apply_along_axis,
    arange,
    asarray,
    concatenate,
    full,
    isnan,
    ix_,
    median,
    nan,
    unique,
)
from numpy.random import choice, seed
from pandas import DataFrame, Series, isna

from .array import map_int, normalize as array_normalize
from .CONSTANT import RANDOM_SEED
from .grid import make_grid_nd
from .plot import plot_heat_map, plot_histogram


def error_axes(dataframe):

    for labels in (dataframe.index.to_numpy(), dataframe.columns.to_numpy()):

        labels, counts = unique(labels, return_counts=True)

        is_na = isna(labels)

        assert not is_na.any()

        assert (counts == 1).all()


def drop_axis_label(dataframe, axis, min_good_value=None, min_good_unique_value=None):

    assert min_good_value is not None or min_good_unique_value is not None

    shape_before = dataframe.shape

    is_kept = full(shape_before[axis], True)

    if axis == 0:

        axis_apply = 1

    elif axis == 1:

        axis_apply = 0

    matrix = dataframe.to_numpy()

    if min_good_value is not None:

        if min_good_value < 1:

            min_good_value = min_good_value * shape_before[axis_apply]

        is_kept &= apply_along_axis(
            lambda vector: min_good_value <= (~isna(vector)).sum(), axis_apply, matrix
        )

    if min_good_unique_value is not None:

        if min_good_unique_value < 1:

            min_good_unique_value = min_good_unique_value * dataframe.shape[axis_apply]

        is_kept &= apply_along_axis(
            lambda vector: min_good_unique_value <= unique(vector[~isna(vector)]).size,
            axis_apply,
            matrix,
        )

    if axis == 0:

        dataframe = dataframe.loc[is_kept, :]

    elif axis == 1:

        dataframe = dataframe.loc[:, is_kept]

    print("{} ==> {}".format(shape_before, dataframe.shape))

    return dataframe


def drop_axes_label(
    dataframe, axis=None, min_good_value=None, min_good_unique_value=None
):

    shape_before = dataframe.shape

    if axis is None:

        axis = int(shape_before[0] < shape_before[1])

    can_return = False

    while True:

        dataframe = drop_axis_label(
            dataframe,
            axis,
            min_good_value=min_good_value,
            min_good_unique_value=min_good_unique_value,
        )

        shape_after = dataframe.shape

        if can_return and shape_before == shape_after:

            return dataframe

        shape_before = shape_after

        if axis == 0:

            axis = 1

        elif axis == 1:

            axis = 0

        can_return = True


def sample(
    dataframe,
    axis_0_n,
    axis_1_n,
    random_seed=RANDOM_SEED,
    axis_0_choice_keyword_arguments=None,
    axis_1_choice_keyword_arguments=None,
):

    matrix = dataframe.to_numpy()

    axis_0_size, axis_1_size = matrix.shape

    seed(seed=random_seed)

    if axis_0_n is not None:

        if axis_0_n < 1:

            axis_0_n = int(axis_0_n * axis_0_size)

        if axis_0_choice_keyword_arguments is None:

            axis_0_choice_keyword_arguments = {}

        axis_0_is = choice(
            arange(axis_0_size), size=axis_0_n, **axis_0_choice_keyword_arguments
        )

    if axis_1_n is not None:

        if axis_1_n < 1:

            axis_1_n = int(axis_1_n * axis_1_size)

        if axis_1_choice_keyword_arguments is None:

            axis_1_choice_keyword_arguments = {}

        axis_1_is = choice(
            arange(axis_1_size), size=axis_1_n, **axis_1_choice_keyword_arguments
        )

    if axis_0_n is not None and axis_1_n is not None:

        return DataFrame(
            matrix[ix_(axis_0_is, axis_1_is)],
            index=dataframe.index[axis_0_is],
            columns=dataframe.columns[axis_1_is],
        )

    elif axis_0_n is not None:

        return DataFrame(
            matrix[axis_0_is, :],
            index=dataframe.index[axis_0_is],
            columns=dataframe.columns,
        )

    elif axis_1_n is not None:

        return DataFrame(
            matrix[:, axis_1_is],
            index=dataframe.index,
            columns=dataframe.columns[axis_1_is],
        )


def sync_axis(dataframes, axis, method):

    if method == "union":

        dataframe_0 = dataframes[0]

        if axis == 0:

            labels = set(dataframe_0.index)

        else:

            labels = set(dataframe_0.columns)

        for dataframe in dataframes[1:]:

            if axis == 0:

                labels = labels.union(set(dataframe.index))

            else:

                labels = labels.union(set(dataframe.columns))

        labels = asarray(sorted(labels))

    elif method == "intersection":

        dataframe_0 = dataframes[0]

        if axis == 0:

            labels = dataframe_0.index.to_list()

        else:

            labels = dataframe_0.columns.to_list()

        for dataframe in dataframes[1:]:

            if axis == 0:

                labels += dataframe.index.to_list()

            else:

                labels += dataframe.columns.to_list()

        labels, counts = unique(labels, return_counts=True)

        labels = labels[counts == len(dataframes)]

    print(labels.size)

    return tuple(dataframe.reindex(labels, axis=axis) for dataframe in dataframes)


def normalize(matrix, axis, method, **normalize_keyword_arguments):

    matrix = matrix.to_numpy()

    if axis is None:

        matrix = array_normalize(matrix, method, **normalize_keyword_arguments)

    else:

        matrix = apply_along_axis(
            array_normalize, axis, matrix, method, **normalize_keyword_arguments
        )

    return DataFrame(matrix, index=matrix.index, columns=matrix.columns)


def summarize(
    matrix,
    plot=True,
    plot_heat_map_max_size=int(1e6),
    plot_histogram_max_size=int(1e3),
):

    if matrix.index.name is None:

        matrix.index.name = "Axis 0"

    if matrix.columns.name is None:

        matrix.columns.name = "Axis 1"

    print(matrix.shape)

    matrix_size = matrix.size

    if plot and matrix_size <= plot_heat_map_max_size:

        plot_heat_map(matrix)

    is_nan = isnan(matrix)

    n_nan = is_nan.sum()

    if 0 < n_nan:

        if plot:

            plot_histogram(
                (
                    Series(is_nan.sum(axis=1), name=matrix.index.name),
                    Series(is_nan.sum(axis=0), name=matrix.columns.name),
                ),
                layout={
                    "title": {
                        "text": "Fraction NaN: {:.2e}".format(n_nan / matrix_size)
                    },
                    "xaxis": {"title": {"text": "N NaN"}},
                },
            )

    is_good = ~is_nan

    # TODO: check speed (flatten vs ravel, etc)
    numbers = matrix.to_numpy()[is_good].flatten()

    labels = asarray(
        tuple(
            "{}_{}".format(axis_0_label, axis_1_label)
            for axis_0_label, axis_1_label in make_grid_nd(
                (matrix.index.to_numpy(), matrix.columns.to_numpy())
            )[is_good.ravel()]
        )
    )

    print("Good min: {:.2e}".format(numbers.min()))

    print("Good median: {:.2e}".format(median(numbers)))

    print("Good mean: {:.2e}".format(numbers.mean()))

    print("Good max: {:.2e}".format(numbers.max()))

    if plot:

        if plot_histogram_max_size < numbers.size:

            print("Choosing {} for histogram...".format(plot_histogram_max_size))

            is_chosen = concatenate(
                (
                    choice(
                        arange(numbers.size),
                        size=plot_histogram_max_size,
                        replace=False,
                    ),
                    (numbers.argmin(), numbers.argmax()),
                )
            )

            numbers = numbers[is_chosen]

            labels = labels[is_chosen]

        plot_histogram(
            (Series(numbers, index=labels),),
            layout={"xaxis": {"title": {"text": "Good Number"}}},
        )


# TODO: take 3 arrays
def pivot(dataframe, axis_0, axis_1, value, function=None):

    # dataframe.columns
    # axis_0_i =
    # axis_1_i =
    # value_i =

    axis_0_labels = unique(dataframe.loc[:, axis_0].to_numpy())

    axis_1_labels = unique(dataframe.loc[:, axis_1].to_numpy())

    axis_0_label_to_i = map_int(axis_0_labels)[0]

    axis_1_label_to_i = map_int(axis_1_labels)[0]

    matrix = full((axis_0_labels.size, axis_1_labels.size), nan)

    for axis_0_label, axis_1_label, value in dataframe.loc[
        :, [axis_0, axis_1, value]
    ].to_numpy():

        axis_0_i = axis_0_label_to_i[axis_0_label]

        axis_1_i = axis_1_label_to_i[axis_1_label]

        value_now = matrix[axis_0_i, axis_1_i]

        if isnan(value_now):

            matrix[axis_0_i, axis_1_i] = value

        else:

            matrix[axis_0_i, axis_1_i] = function(value_now, value)

    return DataFrame(matrix, index=axis_0_labels, columns=axis_1_labels)
