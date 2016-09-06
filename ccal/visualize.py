"""
Computational Cancer Analysis Library v0.1

Authors:
Pablo Tamayo
ptamayo@ucsd.edu
Computational Cancer Analysis, UCSD Cancer Center

Huwate (Kwat) Yeerna (Medetgul-Ernar)
kwat.medetgul.ernar@gmail.com
Computational Cancer Analysis, UCSD Cancer Center

James Jensen
jdjensen@eng.ucsd.edu
Laboratory of Jill Mesirov
"""
import math

from numpy import asarray, array, unique, linspace
from pandas import DataFrame, Series, isnull
from scipy.spatial import Delaunay, ConvexHull
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.path import Path
from matplotlib.colors import Normalize
from matplotlib.cm import bwr, Paired
from matplotlib.colorbar import make_axes, ColorbarBase
from seaborn import light_palette, heatmap, pointplot, violinplot, boxplot

from .support import print_log, establish_path, get_unique_in_order, normalize_pandas_object

# ======================================================================================================================
# Parameters
# ======================================================================================================================
# Color maps
BAD_COLOR = 'wheat'
CMAP_CONTINUOUS = bwr
CMAP_CONTINUOUS.set_bad(BAD_COLOR)
CMAP_CATEGORICAL = Paired
CMAP_CATEGORICAL.set_bad(BAD_COLOR)
CMAP_BINARY = light_palette('black', n_colors=2, as_cmap=True)
CMAP_BINARY.set_bad(BAD_COLOR)

FIGURE_SIZE = (16, 10)
DPI = 1000


# ======================================================================================================================
# Functions
# ======================================================================================================================
def plot_nmf_result(nmf_results, k, max_std=3, figure_size=FIGURE_SIZE, title=None, title_fontsize=20,
                    output_filepath=None, dpi=DPI):
    """
    Plot `nmf_results` dictionary (can be generated by `ccal.analyze.nmf` function).
    :param nmf_results: dict; {k: {W:w, H:h, ERROR:error}}
    :param k: int; k for NMF
    :param max_std: number; threshold to clip standardized values
    :param figure_size: tuple;
    :param title: str;
    :param title_fontsize: number;
    :param output_filepath: str;
    :param dpi: int;
    :return: None
    """
    figure = plt.figure(figsize=figure_size)
    gridspec = GridSpec(10, 16)
    ax_w = plt.subplot(gridspec[1:, :5])
    ax_h = plt.subplot(gridspec[3:8, 7:])

    if not title:
        title = 'NMF Result for k={}'.format(k)
    figure.suptitle(title, fontsize=title_fontsize, fontweight='bold')

    axtitle_font_properties = {'fontsize': title_fontsize * 0.9, 'fontweight': 'bold'}
    label_font_properties = {'fontsize': title_fontsize * 0.81, 'fontweight': 'bold'}

    # Plot W
    heatmap(normalize_pandas_object(nmf_results[k]['W'], axis=0).clip(-max_std, max_std), cmap=CMAP_CONTINUOUS,
            yticklabels=False, ax=ax_w)
    ax_w.set_title('W'.format(k), **axtitle_font_properties)
    ax_w.set_xlabel('Component', **label_font_properties)
    ax_w.set_ylabel('Feature', **label_font_properties)

    # Plot H
    heatmap(normalize_pandas_object(nmf_results[k]['H'], axis=1).clip(-max_std, max_std), cmap=CMAP_CONTINUOUS,
            xticklabels=False, cbar_kws={'orientation': 'horizontal'}, ax=ax_h)
    ax_h.set_title('H'.format(k), **axtitle_font_properties)
    ax_h.set_xlabel('Sample', **label_font_properties)
    ax_h.set_ylabel('Component', **label_font_properties)

    if output_filepath:
        establish_path(output_filepath)
        figure.savefig(output_filepath, dpi=dpi, bbox_inches='tight')
    plt.show()


def plot_nmf_scores(scores, figure_size=FIGURE_SIZE, title='NMF Clustering Score vs. k', title_fontsize=20,
                    output_filepath=None, dpi=DPI):
    """
    Plot `scores` dictionary.
    :param scores: dict; {k: score}
    :param figure_size: tuple;
    :param title: str;
    :param title_fontsize: number;
    :param output_filepath: str;
    :param dpi: int;
    :return: None
    """
    figure = plt.figure(figsize=figure_size)

    if title:
        figure.suptitle(title, fontsize=title_fontsize, fontweight='bold')

    label_font_properties = {'fontsize': title_fontsize * 0.81, 'fontweight': 'bold'}

    ax = pointplot(x=[k for k, v in scores.items()], y=[v for k, v in scores.items()])
    ax.set_xlabel('k', **label_font_properties)
    ax.set_ylabel('Score', **label_font_properties)

    if output_filepath:
        establish_path(output_filepath)
        figure.savefig(output_filepath, dpi=dpi, bbox_inches='tight')
    plt.show()


def plot_onco_gps(component_coordinates, samples, grid_probabilities, grid_states,
                  annotations=(), annotation_name='', annotation_type='continuous', std_max=3,
                  title='Onco-GPS Map', title_fontsize=24, title_fontcolor='#3326C0',
                  subtitle_fontsize=16, subtitle_fontcolor='#FF0039',
                  component_markersize=13, component_markerfacecolor='#000726', component_markeredgewidth=1.69,
                  component_markeredgecolor='#FFFFFF', component_text_position='auto', component_fontsize=16,
                  delaunay_linewidth=1, delaunay_linecolor='#000000',
                  n_contours=26, contour_linewidth=0.81, contour_linecolor='#5A5A5A', contour_alpha=0.92,
                  background_markersize=5.55, background_mask_markersize=7, background_max_alpha=0.7,
                  sample_markersize=12, sample_without_annotation_markerfacecolor='#999999',
                  sample_markeredgewidth=0.81, sample_markeredgecolor='#000000',
                  legend_markersize=10, legend_fontsize=11,
                  effectplot_type='violine', effectplot_mean_markerfacecolor='#FFFFFF',
                  effectplot_mean_markeredgecolor='#FF0082', effectplot_median_markeredgecolor='#FF0082',
                  output_filepath=None, figure_size=FIGURE_SIZE, dpi=DPI):
    """
    :param component_coordinates: pandas DataFrame; (n_components, [x, y])
    :param samples: pandas DataFrame; (n_samples, [x, y, state, annotation])
    :param grid_probabilities: numpy 2D array; (n_grids, n_grids)
    :param grid_states: numpy 2D array; (n_grids, n_grids)
    :param annotations: pandas Series; (n_samples); sample annotations; will color samples based on annotations
    :param annotation_name: str;
    :param annotation_type: str; {'continuous', 'categorical', 'binary'}
    :param std_max: number; threshold to clip standardized values
    :param title: str;
    :param title_fontsize: number;
    :param title_fontcolor: matplotlib color;
    :param subtitle_fontsize: number;
    :param subtitle_fontcolor: matplotlib color;
    :param component_markersize: number;
    :param component_markerfacecolor: matplotlib color;
    :param component_markeredgewidth: number;
    :param component_markeredgecolor: matplotlib color;
    :param component_text_position: str; {'auto', 'top', 'bottom'}
    :param component_fontsize: number;
    :param delaunay_linewidth: number;
    :param delaunay_linecolor: matplotlib color;
    :param n_contours: int; set to 0 to disable drawing contours
    :param contour_linewidth: number;
    :param contour_linecolor: matplotlib color;
    :param contour_alpha: float; [0, 1]
    :param background_markersize: number; set to 0 to disable drawing backgrounds
    :param background_mask_markersize: number; set to 0 to disable masking
    :param background_max_alpha: float; [0, 1]; the maximum background alpha (transparency)
    :param sample_markersize: number;
    :param sample_without_annotation_markerfacecolor: matplotlib color;
    :param sample_markeredgewidth: number;
    :param sample_markeredgecolor: matplotlib color;
    :param legend_markersize: number;
    :param legend_fontsize: number;
    :param effectplot_type: str; {'violine', 'box'}
    :param effectplot_mean_markerfacecolor: matplotlib color;
    :param effectplot_mean_markeredgecolor: matplotlib color;
    :param effectplot_median_markeredgecolor: matplotlib color;
    :param output_filepath: str;
    :param figure_size: tuple;
    :param dpi: int;
    :return: None
    """
    states = samples.ix[:, 'state']
    unique_states = sorted(set(states))

    x_grids = linspace(0, 1, grid_probabilities.shape[0])
    y_grids = linspace(0, 1, grid_probabilities.shape[1])

    # Set up figure and axes
    figure = plt.figure(figsize=figure_size)
    gridspec = GridSpec(10, 16)
    ax_title = plt.subplot(gridspec[0, :7])
    ax_title.axis([0, 1, 0, 1])
    ax_title.axis('off')
    ax_colorbar = plt.subplot(gridspec[0, 7:12])
    ax_colorbar.axis([0, 1, 0, 1])
    ax_colorbar.axis('off')
    ax_map = plt.subplot(gridspec[1:, :12])
    ax_map.axis([0, 1, 0, 1])
    ax_map.axis('off')
    ax_legend = plt.subplot(gridspec[1:, 14:])
    ax_legend.axis([0, 1, 0, 1])
    ax_legend.axis('off')

    # Plot title
    ax_title.text(0, 0.9, title, fontsize=title_fontsize, color=title_fontcolor, weight='bold')
    ax_title.text(0, 0.39,
                  '{} samples, {} components, and {} states'.format(samples.shape[0], component_coordinates.shape[0],
                                                                    len(unique_states)),
                  fontsize=subtitle_fontsize, color=subtitle_fontcolor, weight='bold')

    # Plot components and their labels
    ax_map.plot(component_coordinates.ix[:, 'x'], component_coordinates.ix[:, 'y'], marker='D', linestyle='',
                markersize=component_markersize, markerfacecolor=component_markerfacecolor,
                markeredgewidth=component_markeredgewidth, markeredgecolor=component_markeredgecolor, clip_on=False,
                aa=True, zorder=6)
    # Compute convexhull
    convexhull = ConvexHull(component_coordinates)
    convexhull_region = Path(convexhull.points[convexhull.vertices])
    # Put labels on top or bottom of the component markers
    component_text_verticalshift = -0.03
    for i in range(component_coordinates.shape[0]):
        if component_text_position == 'auto':
            if convexhull_region.contains_point((component_coordinates.ix[i, 'x'],
                                                 component_coordinates.ix[i, 'y'] + component_text_verticalshift)):
                component_text_verticalshift *= -1
        elif component_text_position == 'top':
            component_text_verticalshift *= -1
        elif component_text_position == 'bottom':
            pass
        x, y = component_coordinates.ix[i, 'x'], component_coordinates.ix[i, 'y'] + component_text_verticalshift

        ax_map.text(x, y, component_coordinates.index[i],
                    fontsize=component_fontsize, color=component_markerfacecolor, weight='bold',
                    horizontalalignment='center', verticalalignment='center', zorder=6)

    # Plot Delaunay triangulation
    delaunay = Delaunay(component_coordinates)
    ax_map.triplot(delaunay.points[:, 0], delaunay.points[:, 1], delaunay.simplices.copy(),
                   linewidth=delaunay_linewidth, color=delaunay_linecolor, aa=True, zorder=4)

    # Plot contours
    if n_contours > 0:
        ax_map.contour(x_grids, y_grids, grid_probabilities, n_contours, corner_mask=True,
                       linewidths=contour_linewidth, colors=contour_linecolor, alpha=contour_alpha, aa=True, zorder=2)

    # Assign colors to states
    states_color = {}
    for s in unique_states:
        print(s)
        states_color[s] = CMAP_CATEGORICAL(int(s / len(unique_states) * CMAP_CATEGORICAL.N))

    # Plot background
    if background_markersize > 0:
        grid_probabilities_min = grid_probabilities.min()
        grid_probabilities_max = grid_probabilities.max()
        grid_probabilities_range = grid_probabilities_max - grid_probabilities_min
        for i in range(grid_probabilities.shape[0]):
            for j in range(grid_probabilities.shape[1]):
                if convexhull_region.contains_point((x_grids[i], y_grids[j])):
                    c = states_color[grid_states[i, j]]
                    a = min(background_max_alpha,
                            (grid_probabilities[i, j] - grid_probabilities_min) / grid_probabilities_range)
                    ax_map.plot(x_grids[i], y_grids[j], marker='s', markersize=background_markersize, markerfacecolor=c,
                                alpha=a, aa=True, zorder=1)
    # Plot background mask
    if background_mask_markersize > 0:
        for i in range(grid_probabilities.shape[0]):
            for j in range(grid_probabilities.shape[1]):
                if not convexhull_region.contains_point((x_grids[i], y_grids[j])):
                    ax_map.plot(x_grids[i], y_grids[j], marker='s', markersize=background_mask_markersize,
                                markerfacecolor='w', aa=True, zorder=3)

    if any(annotations):  # Plot samples, annotations, sample legends, and annotation legends
        # Set up annotations
        a = Series(annotations)
        a.index = samples.index
        if annotation_type == 'continuous':
            samples.ix[:, 'annotation'] = normalize_pandas_object(a).clip(-std_max, std_max)
            annotation_min = max(-std_max, samples.ix[:, 'annotation'].min())
            annotation_mean = samples.ix[:, 'annotation'].mean()
            annotation_max = min(std_max, samples.ix[:, 'annotation'].max())
            cmap = CMAP_CONTINUOUS
        else:
            samples.ix[:, 'annotation'] = annotations
            annotation_min = 0
            annotation_mean = int(samples.ix[:, 'annotation'].mean())
            annotation_max = int(samples.ix[:, 'annotation'].max())
            if annotation_type == 'categorical':
                cmap = CMAP_CATEGORICAL
            elif annotation_type == 'binary':
                cmap = CMAP_BINARY
            else:
                raise ValueError('Unknown annotation_type {}.'.format(annotation_type))
        annotation_range = annotation_max - annotation_min

        # Plot samples
        for idx, s in samples.iterrows():
            if isnull(s.ix['annotation']):
                c = sample_without_annotation_markerfacecolor
            else:
                if annotation_type == 'continuous':
                    c = cmap(s.ix['annotation'])
                elif annotation_type in ('categorical', 'binary'):
                    c = cmap((s.ix['annotation'] - annotation_min) / annotation_range)
                else:
                    raise ValueError('Unknown annotation_type {}.'.format(annotation_type))
            ax_map.plot(s.ix['x'], s.ix['y'], marker='o', markersize=sample_markersize, markerfacecolor=c,
                        markeredgewidth=sample_markeredgewidth, markeredgecolor=sample_markeredgecolor, aa=True,
                        zorder=5)

        # Plot sample legends
        ax_legend.axis('on')
        ax_legend.patch.set_visible(False)
        # TODO: Compute IC and get p-val
        ax_legend.set_title('{}\nIC={} (p-val={})'.format(annotation_name, 'XXX', 'XXX'),
                            fontsize=legend_fontsize * 1.26, weight='bold')
        if effectplot_type == 'violine':
            violinplot(x=samples.ix[:, 'annotation'], y=states, palette=states_color, scale='count', inner=None,
                       orient='h', ax=ax_legend, clip_on=False)
            boxplot(x=samples.ix[:, 'annotation'], y=states, showbox=False, showmeans=True,
                    medianprops={'marker': 'o',
                                 'markerfacecolor': effectplot_mean_markerfacecolor,
                                 'markeredgewidth': 0.9,
                                 'markeredgecolor': effectplot_mean_markeredgecolor},
                    meanprops={'color': effectplot_median_markeredgecolor}, orient='h', ax=ax_legend)
        elif effectplot_type == 'box':
            boxplot(x=samples.ix[:, 'annotation'], y=states, palette=states_color, showmeans=True,
                    medianpops={'marker': 'o',
                                'markerfacecolor': effectplot_mean_markerfacecolor,
                                'markeredgewidth': 0.9,
                                'markeredgecolor': effectplot_mean_markeredgecolor},
                    meanprops={'color': effectplot_median_markeredgecolor}, orient='h', ax=ax_legend)
        ax_legend.axvline(annotation_min, color='#000000', ls='-', alpha=0.16, aa=True)
        ax_legend.axvline(annotation_mean, color='#000000', ls='-', alpha=0.39, aa=True)
        ax_legend.axvline(annotation_max, color='#000000', ls='-', alpha=0.16, aa=True)
        ax_legend.set_xticks([annotation_min, annotation_mean, annotation_max])
        ax_legend.set_xlabel('')
        for t in ax_legend.get_xticklabels():
            t.set(rotation=90, size=legend_fontsize * 0.9, weight='bold')
        ax_legend.set_yticklabels(['State {} (n={})'.format(s, sum(array(states) == s)) for s in unique_states],
                                  fontsize=legend_fontsize, weight='bold')
        ax_legend.yaxis.tick_right()

        # Plot annotation legends
        if annotation_type == 'continuous':
            cax, kw = make_axes(ax_colorbar, location='top', fraction=0.39, shrink=1, aspect=16,
                                cmap=cmap, norm=Normalize(vmin=annotation_min, vmax=annotation_max),
                                ticks=[annotation_min, annotation_mean, annotation_max])
            ColorbarBase(cax, **kw)

    else:  # Plot samples and sample legends
        # Plot samples
        for idx, s in samples.iterrows():
            c = states_color[s.ix['state']]
            ax_map.plot(s.ix['x'], s.ix['y'], marker='o', markersize=sample_markersize, markerfacecolor=c,
                        markeredgewidth=sample_markeredgewidth, markeredgecolor=sample_markeredgecolor, aa=True,
                        zorder=5)
        # Plot sample legends
        for i, s in enumerate(unique_states):
            y = 1 - float(1 / (len(unique_states) + 1)) * (i + 1)
            c = states_color[s]
            ax_legend.plot(0.16, y, marker='o', markersize=legend_markersize, markerfacecolor=c, aa=True, clip_on=False)
            ax_legend.text(0.26, y, 'State {} (n={})'.format(s, sum(asarray(states) == s)),
                           fontsize=legend_fontsize, weight='bold', verticalalignment='center')

    if output_filepath:
        establish_path(output_filepath)
        figure.savefig(output_filepath, dpi=dpi, bbox_inches='tight')
    plt.show()


def plot_features_against_reference(features, ref, annotations, feature_type='continuous', ref_type='continuous',
                                    std_max=3, figure_size='auto', title=None, title_size=20,
                                    annotation_header=None, annotation_label_size=9,
                                    plot_colname=False, output_filepath=None, dpi=DPI):
    """
    Plot a heatmap panel.
    :param features: pandas DataFrame; (n_features, n_elements); must have indices and columns
    :param ref: pandas Series; (n_elements); must have indices, which must match `features`'s columns
    :param annotations:  pandas DataFrame; (n_features, n_annotations); must have indices, which must match `features`'s
    :param feature_type: str; {'continuous', 'categorical', 'binary'}
    :param ref_type: str; {'continuous', 'categorical', 'binary'}
    :param std_max: number;
    :param figure_size: 'auto' or tuple;
    :param title: str;
    :param title_size: number;
    :param annotation_header: str; annotation header to be plotted
    :param annotation_label_size: number;
    :param plot_colname: bool; plot column names or not
    :param output_filepath: str;
    :param dpi: int;
    :return: None
    """
    if feature_type == 'continuous':
        features_cmap = CMAP_CONTINUOUS
        features_min, features_max = -std_max, std_max
        print_log('Normalizing continuous features ...')
        features = normalize_pandas_object(features, axis=1)
    elif feature_type == 'categorical':
        features_cmap = CMAP_CATEGORICAL
        features_min, features_max = 0, len(unique(features))
    elif feature_type == 'binary':
        features_cmap = CMAP_BINARY
        features_min, features_max = 0, 1
    else:
        raise ValueError('Unknown feature_type {}.'.format(feature_type))
    if ref_type == 'continuous':
        ref_cmap = CMAP_CONTINUOUS
        ref_min, ref_max = -std_max, std_max
        print_log('Normalizing continuous ref ...')
        ref = normalize_pandas_object(ref)
    elif ref_type == 'categorical':
        ref_cmap = CMAP_CATEGORICAL
        ref_min, ref_max = 0, len(unique(ref))
    elif ref_type == 'binary':
        ref_cmap = CMAP_BINARY
        ref_min, ref_max = 0, 1
    else:
        raise ValueError('Unknown ref_type {}.'.format(ref_type))

    if figure_size == 'auto':
        figure_size = (min(math.pow(features.shape[1], 0.7), 7), math.pow(features.shape[0], 0.9))
    figure = plt.figure(figsize=figure_size)
    gridspec = GridSpec(features.shape[0] + 1, features.shape[1] + 1)
    ax_ref = plt.subplot(gridspec[:1, :features.shape[1]])
    ax_features = plt.subplot(gridspec[1:, :features.shape[1]])
    ax_annotation_header = plt.subplot(gridspec[:1, features.shape[1]:])
    ax_annotation_header.axis('off')
    horizontal_text_margin = math.pow(features.shape[1], 0.39)

    # Plot ref, ref label, and title,
    heatmap(DataFrame(ref).T, ax=ax_ref, vmin=ref_min, vmax=ref_max, cmap=ref_cmap, xticklabels=False, cbar=False)
    for t in ax_ref.get_yticklabels():
        t.set(rotation=0, weight='bold')

    if title:
        ax_ref.text(features.shape[1] / 2, 1.9, title, horizontalalignment='center', size=title_size, weight='bold')

    if ref_type in ('binary', 'categorical'):
        # Add binary or categorical ref labels
        boundaries = [0]
        prev_v = ref.iloc[0]
        for i, v in enumerate(ref.iloc[1:]):
            if prev_v != v:
                boundaries.append(i + 1)
            prev_v = v
        boundaries.append(features.shape[1])
        label_horizontal_positions = []
        prev_b = 0
        for b in boundaries[1:]:
            label_horizontal_positions.append(b - (b - prev_b) / 2)
            prev_b = b
        unique_ref_labels = get_unique_in_order(ref.values)

        for i, pos in enumerate(label_horizontal_positions):
            ax_ref.text(pos, 1, unique_ref_labels[i], horizontalalignment='center', weight='bold')

    # Plot features
    heatmap(features, ax=ax_features, vmin=features_min, vmax=features_max, cmap=features_cmap,
            xticklabels=plot_colname, cbar=False)
    for t in ax_features.get_yticklabels():
        t.set(rotation=0, weight='bold')

    # Plot annotations
    if not annotation_header:
        annotation_header = '\t'.join(annotations.columns).expandtabs()
    ax_annotation_header.text(horizontal_text_margin, 0.5, annotation_header, horizontalalignment='left',
                              verticalalignment='center', size=annotation_label_size, weight='bold')
    for i, (idx, s) in enumerate(annotations.iterrows()):
        ax = plt.subplot(gridspec[i + 1:i + 2, features.shape[1]:])
        ax.axis('off')
        a = '\t'.join(s.tolist()).expandtabs()
        ax.text(horizontal_text_margin, 0.5, a, horizontalalignment='left', verticalalignment='center',
                size=annotation_label_size, weight='bold')

    if output_filepath:
        establish_path(output_filepath)
        figure.savefig(output_filepath, dpi=dpi, bbox_inches='tight')
    plt.show(figure)
