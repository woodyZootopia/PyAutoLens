from matplotlib import pyplot as plt

from autolens import conf
from autolens.plotting import plotters

def plot_intensities(galaxy, grid,
                     units='arcsec', kpc_per_arcsec=None,
                     xyticksize=40, norm='linear', norm_min=None, norm_max=None, linthresh=0.05, linscale=0.01,
                     figsize=(20, 15), aspect='auto', cmap='jet', cb_ticksize=20,
                     title='Galaxy Intensities', titlesize=46, xlabelsize=36, ylabelsize=36,
                     output_path=None, output_format='show', output_filename='galaxy_intensities', as_subplot=False):

    intensities = galaxy.intensities_from_grid(grid=grid)
    intensities = grid.scaled_array_from_array_1d(intensities)

    plotters.plot_array(intensities, as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh, linscale)
    plotters.set_title(title, titlesize)
    plotters.set_xy_labels_and_ticks(intensities.shape, units, kpc_per_arcsec, intensities.xticks, intensities.yticks,
                                     xlabelsize, ylabelsize, xyticksize)
    plotters.set_colorbar(cb_ticksize)
    plotters.plot_grid(grid)
    plotters.output_array(intensities, output_path, output_filename, output_format)
    plt.close()

def plot_intensities_individual(galaxy, grid,
                                units='arcsec', kpc_per_arcsec=None,
                                xyticksize=40, norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
                                linscale=0.01,
                                figsize=(20, 15), aspect='auto', cmap='jet', cb_ticksize=20,
                                title='Galaxy Intensities', titlesize=46, xlabelsize=36, ylabelsize=36,
                                output_path=None, output_format='show', output_filename='galaxy_individual_intensities'):

    intensities_1d = galaxy.intensities_from_grid_individual(grid=grid)
    intensities = list(map(lambda intensities : grid.scaled_array_from_array_1d(intensities), intensities_1d))

    plt.figure(figsize=(13, 4))
    as_subplot = True

    for i in range(len(intensities)):

        plt.subplot(1, len(intensities), i+1)

        plotters.plot_array(intensities[i], as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh,
                            linscale)
        plotters.set_title(title, titlesize)
        plotters.set_xy_labels_and_ticks(intensities[i].shape, units, kpc_per_arcsec,
                                         intensities[i].xticks, intensities[i].yticks,
                                         xlabelsize, ylabelsize, xyticksize)
        plotters.set_colorbar(cb_ticksize)
        plotters.plot_grid(grid)
        plotters.output_array(intensities[i], output_path, output_filename, output_format)

    plotters.output_subplot_array(output_path=output_path, output_filename=output_filename,
                                  output_format=output_format)
    plt.close()

def plot_surface_density(galaxy, grid,
                         units='arcsec', kpc_per_arcsec=None,
                         xyticksize=40, norm='linear', norm_min=None, norm_max=None, linthresh=0.05, linscale=0.01,
                         figsize=(20, 15), aspect='auto', cmap='jet', cb_ticksize=20,
                         title='Galaxy Surface Density', titlesize=46, xlabelsize=36, ylabelsize=36,
                         output_path=None, output_format='show', output_filename='galaxy_surface_density',
                         as_subplot=False):

    surface_density = galaxy.surface_density_from_grid(grid=grid)
    surface_density = grid.scaled_array_from_array_1d(surface_density)

    plotters.plot_array(surface_density, as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh,
                        linscale)
    plotters.set_title(title, titlesize)
    plotters.set_xy_labels_and_ticks(surface_density.shape, units, kpc_per_arcsec, surface_density.xticks,
                                     surface_density.yticks, xlabelsize, ylabelsize, xyticksize)
    plotters.set_colorbar(cb_ticksize)
    plotters.plot_grid(grid)
    plotters.output_array(surface_density, output_path, output_filename, output_format)
    plt.close()
    
def plot_potential(galaxy, grid,
                   units='arcsec', kpc_per_arcsec=None,
                   xyticksize=40, norm='linear', norm_min=None, norm_max=None, linthresh=0.05, linscale=0.01,
                   figsize=(20, 15), aspect='auto', cmap='jet', cb_ticksize=20,
                   title='Galaxy Potential', titlesize=46, xlabelsize=36, ylabelsize=36,
                   output_path=None, output_format='show', output_filename='galaxy_potential', as_subplot=False):

    potential = galaxy.potential_from_grid(grid=grid)
    potential = grid.scaled_array_from_array_1d(potential)

    plotters.plot_array(potential, as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh, linscale)
    plotters.set_title(title, titlesize)
    plotters.set_xy_labels_and_ticks(potential.shape, units, kpc_per_arcsec, potential.xticks, potential.yticks,
                                     xlabelsize, ylabelsize, xyticksize)
    plotters.set_colorbar(cb_ticksize)
    plotters.plot_grid(grid)
    plotters.output_array(potential, output_path, output_filename, output_format)
    plt.close()

def plot_deflections(galaxy, grid,
                     units='arcsec', kpc_per_arcsec=None,
                     xyticksize=40, norm='linear', norm_min=None, norm_max=None, linthresh=0.05, linscale=0.01,
                     figsize=(20, 15), aspect='auto', cmap='jet', cb_ticksize=20,
                     titlesize=46, xlabelsize=36, ylabelsize=36,
                     output_path=None, output_format='show', output_filename='galaxy_deflections'):

    deflections = galaxy.deflections_from_grid(grid)

    deflections_y = grid.scaled_array_from_array_1d(deflections[:,0])
    deflections_x = grid.scaled_array_from_array_1d(deflections[:,1])

    plt.figure(figsize=figsize)
    plt.subplot(1, 2, 1)
    as_subplot = True

    plotters.plot_array(deflections_y, as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh, linscale)
    plotters.set_title(title='Galaxy Deflections (y)', titlesize=titlesize)
    plotters.set_xy_labels_and_ticks(deflections_y.shape, units, kpc_per_arcsec, deflections_y.xticks, deflections_y.yticks,
                                     xlabelsize, ylabelsize, xyticksize)
    plotters.set_colorbar(cb_ticksize)
    plotters.plot_grid(grid)
    plotters.output_array(deflections_y, output_path, output_filename, output_format)

    plt.subplot(1, 2, 2)

    plotters.plot_array(deflections_x, as_subplot, figsize, aspect, cmap, norm, norm_max, norm_min, linthresh, linscale)
    plotters.set_title(title='Galaxy Deflections (x)', titlesize=titlesize)
    plotters.set_xy_labels_and_ticks(deflections_x.shape, units, kpc_per_arcsec, deflections_x.xticks, deflections_x.yticks,
                                     xlabelsize, ylabelsize, xyticksize)
    plotters.set_colorbar(cb_ticksize)
    plotters.plot_grid(grid)
    plotters.output_array(deflections_x, output_path, output_filename, output_format)

    plotters.output_subplot_array(output_path=output_path, output_filename=output_filename,
                                  output_format=output_format)

    plt.close()