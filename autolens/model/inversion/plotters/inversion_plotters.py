from autolens.plotters import plotter_util, array_plotters
from autolens.model.inversion.plotters import mapper_plotters
from autolens.model.inversion import mappers

def plot_reconstructed_image(
        inversion, mask=None, positions=None, grid=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05, linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed CCD', titlesize=16, xlabelsize=16, ylabelsize=16, xyticksize=16,
        output_path=None, output_format='show', output_filename='reconstructed_inversion_image'):

    array_plotters.plot_array(
        array=inversion.reconstructed_data_2d, mask=mask, positions=positions, grid=grid, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max,
        linthresh=linthresh, linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

def plot_pixelization_values(
        inversion, plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='reconstructed_inversion_image'):

    if output_format is 'fits':
        return

    plotter_util.setup_figure(figsize=figsize, as_subplot=as_subplot)

    plot_inversion_with_source_values(
        inversion=inversion, source_pixel_values=inversion.pixelization_values,
        plot_origin=plot_origin, positions=positions, should_plot_centres=should_plot_centres,
        should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
        image_pixels=image_pixels, source_pixels=source_pixels, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max, linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize, xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

    plotter_util.close_figure(as_subplot=as_subplot)

def plot_pixelization_residuals(
        inversion, plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='reconstructed_inversion_image'):

    if output_format is 'fits':
        return

    plotter_util.setup_figure(figsize=figsize, as_subplot=as_subplot)

    plot_inversion_with_source_values(
        inversion=inversion, source_pixel_values=inversion.pixelization_residuals,
        plot_origin=plot_origin, positions=positions, should_plot_centres=should_plot_centres,
        should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
        image_pixels=image_pixels, source_pixels=source_pixels, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max, linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize, xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

    plotter_util.close_figure(as_subplot=as_subplot)

def plot_pixelization_normalized_residuals(
        inversion, plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='reconstructed_inversion_image'):

    if output_format is 'fits':
        return

    plotter_util.setup_figure(figsize=figsize, as_subplot=as_subplot)

    plot_inversion_with_source_values(
        inversion=inversion, source_pixel_values=inversion.pixelization_normalized_residuals,
        plot_origin=plot_origin, positions=positions, should_plot_centres=should_plot_centres,
        should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
        image_pixels=image_pixels, source_pixels=source_pixels, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max, linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize, xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

    plotter_util.close_figure(as_subplot=as_subplot)

def plot_pixelization_chi_squareds(
        inversion, plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='reconstructed_inversion_image'):

    if output_format is 'fits':
        return

    plotter_util.setup_figure(figsize=figsize, as_subplot=as_subplot)

    plot_inversion_with_source_values(
        inversion=inversion, source_pixel_values=inversion.pixelization_chi_squareds,
        plot_origin=plot_origin, positions=positions, should_plot_centres=should_plot_centres,
        should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
        image_pixels=image_pixels, source_pixels=source_pixels, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max, linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize, xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

    plotter_util.close_figure(as_subplot=as_subplot)


def plot_pixelization_regularization_weights(
        inversion, plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='regularization_weights'):

    if output_format is 'fits':
        return

    plotter_util.setup_figure(
        figsize=figsize, as_subplot=as_subplot)

    regularization_weights = inversion.regularization.regularization_weights_from_mapper(
        mapper=inversion.mapper)

    plot_inversion_with_source_values(
        inversion=inversion, source_pixel_values=regularization_weights,
        plot_origin=plot_origin, positions=positions, should_plot_centres=should_plot_centres,
        should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
        image_pixels=image_pixels, source_pixels=source_pixels, as_subplot=as_subplot,
        units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
        cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max, linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
        cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
        title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize, xyticksize=xyticksize,
        output_path=output_path, output_format=output_format, output_filename=output_filename)

    plotter_util.close_figure(as_subplot=as_subplot)

def plot_inversion_with_source_values(
        inversion, source_pixel_values,
        plot_origin=True, positions=None, should_plot_centres=False,
        should_plot_grid=False, should_plot_border=False, image_pixels=None,
        source_pixels=None, as_subplot=False,
        units='arcsec', kpc_per_arcsec=None, figsize=(7, 7), aspect='square',
        cmap='jet', norm='linear', norm_min=None, norm_max=None, linthresh=0.05,
        linscale=0.01,
        cb_ticksize=10, cb_fraction=0.047, cb_pad=0.01, cb_tick_values=None, cb_tick_labels=None,
        title='Reconstructed Pixelization', titlesize=16, xlabelsize=16, ylabelsize=16,
        xyticksize=16,
        output_path=None, output_format='show', output_filename='regularization_weights'):

    if isinstance(inversion.mapper, mappers.RectangularMapper):

        reconstructed_pixelization = \
            inversion.mapper.reconstructed_pixelization_from_solution_vector(solution_vector=source_pixel_values)

        origin = get_origin(image=reconstructed_pixelization, plot_origin=plot_origin)

        array_plotters.plot_array(
            array=reconstructed_pixelization, origin=origin, positions=positions, as_subplot=True,
            units=units, kpc_per_arcsec=kpc_per_arcsec, figsize=figsize, aspect=aspect,
            cmap=cmap, norm=norm, norm_min=norm_min, norm_max=norm_max,
            linthresh=linthresh, linscale=linscale,
            cb_ticksize=cb_ticksize, cb_fraction=cb_fraction, cb_pad=cb_pad,
            cb_tick_values=cb_tick_values, cb_tick_labels=cb_tick_labels,
            title=title, titlesize=titlesize, xlabelsize=xlabelsize, ylabelsize=ylabelsize,
            xyticksize=xyticksize,
            output_filename=output_filename)

        mapper_plotters.plot_rectangular_mapper(
            mapper=inversion.mapper,
            should_plot_centres=should_plot_centres, should_plot_grid=should_plot_grid,
            should_plot_border=should_plot_border,
            image_pixels=image_pixels, source_pixels=source_pixels,
            as_subplot=True,
            units=units, kpc_per_arcsec=kpc_per_arcsec,
            title=title, titlesize=titlesize, xlabelsize=xlabelsize,
            ylabelsize=ylabelsize, xyticksize=xyticksize)

        plotter_util.output_figure(
            array=reconstructed_pixelization, as_subplot=as_subplot,
            output_path=output_path, output_filename=output_filename, output_format=output_format)

    elif isinstance(inversion.mapper, mappers.VoronoiMapper):

        mapper_plotters.plot_voronoi_mapper(
            mapper=inversion.mapper, source_pixel_values=source_pixel_values,
            should_plot_centres=should_plot_centres,
            should_plot_grid=should_plot_grid, should_plot_border=should_plot_border,
            image_pixels=image_pixels, source_pixels=source_pixels,
            as_subplot=True,
            units=units, kpc_per_arcsec=kpc_per_arcsec,
            title=title, titlesize=titlesize, xlabelsize=xlabelsize,
            ylabelsize=ylabelsize, xyticksize=xyticksize)

        plotter_util.output_figure(
            array=None, as_subplot=as_subplot,
            output_path=output_path, output_filename=output_filename, output_format=output_format)

def get_origin(image, plot_origin):

    if plot_origin:
        return image.origin
    else:
        return None