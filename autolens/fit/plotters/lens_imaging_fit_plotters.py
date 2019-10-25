import autofit as af
import matplotlib

backend = af.conf.instance.visualize.get("figures", "backend", str)
matplotlib.use(backend)
from matplotlib import pyplot as plt

import autoarray as aa
from autolens.plotters import plane_plotters, fit_plotters
from autoarray.plotters import inversion_plotters


def plot_fit_subplot(
    fit,
    should_plot_mask=True,
    positions=None,
    should_plot_image_plane_pix=False,
    plot_mass_profile_centres=True,
    units="arcsec",
    figsize=None,
    aspect="square",
    cmap="jet",
    norm="linear",
    norm_min=None,
    norm_max=None,
    linthresh=0.05,
    linscale=0.01,
    cb_ticksize=10,
    cb_fraction=0.047,
    cb_pad=0.01,
    cb_tick_values=None,
    cb_tick_labels=None,
    titlesize=10,
    xlabelsize=10,
    ylabelsize=10,
    xyticksize=10,
    mask_pointsize=10,
    position_pointsize=10,
    grid_pointsize=1,
    output_path=None,
    output_filename="fit",
    output_format="show",
):

    rows, columns, figsize_tool = aa.plotter_util.get_subplot_rows_columns_figsize(
        number_subplots=6
    )

    mask = fit_plotters.get_mask(fit=fit, should_plot_mask=should_plot_mask)

    if figsize is None:
        figsize = figsize_tool

    plt.figure(figsize=figsize)
    plt.subplot(rows, columns, 1)

    kpc_per_arcsec = fit.tracer.image_plane.kpc_per_arcsec

    image_plane_pix_grid = fit_plotters.get_image_plane_pix_grid(
        should_plot_image_plane_pix, fit
    )

    fit_plotters.plot_image(
        fit=fit,
        grid=image_plane_pix_grid,
        mask=mask,
        positions=positions,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        grid_pointsize=grid_pointsize,
        position_pointsize=position_pointsize,
        mask_pointsize=mask_pointsize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 2)

    fit_plotters.plot_signal_to_noise_map(
        fit=fit,
        mask=mask,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        position_pointsize=position_pointsize,
        mask_pointsize=mask_pointsize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 3)

    fit_plotters.plot_model_data(
        fit=fit,
        mask=mask,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 4)

    fit_plotters.plot_residual_map(
        fit=fit,
        mask=mask,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 5)

    fit_plotters.plot_normalized_residual_map(
        fit=fit,
        mask=mask,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 6)

    fit_plotters.plot_chi_squared_map(
        fit=fit,
        mask=mask,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    aa.plotter_util.output_subplot_array(
        output_path=output_path,
        output_filename=output_filename,
        output_format=output_format,
    )

    plt.close()


def plot_fit_subplot_of_planes(
    fit,
    should_plot_mask=True,
    positions=None,
    should_plot_image_plane_pix=False,
    plot_mass_profile_centres=True,
    units="arcsec",
    figsize=None,
    aspect="square",
    cmap="jet",
    norm="linear",
    norm_min=None,
    norm_max=None,
    linthresh=0.05,
    linscale=0.01,
    cb_ticksize=10,
    cb_fraction=0.047,
    cb_pad=0.01,
    cb_tick_values=None,
    cb_tick_labels=None,
    titlesize=10,
    xlabelsize=10,
    ylabelsize=10,
    xyticksize=10,
    mask_pointsize=10,
    position_pointsize=10,
    grid_pointsize=1,
    output_path=None,
    output_filename="lens_fit_plane",
    output_format="show",
):

    for plane_index in range(fit.tracer.total_planes):

        if (
            fit.tracer.planes[plane_index].has_light_profile
            or fit.tracer.planes[plane_index].has_pixelization
        ):

            plot_fit_subplot_for_plane(
                fit=fit,
                plane_index=plane_index,
                should_plot_mask=should_plot_mask,
                should_plot_image_plane_pix=should_plot_image_plane_pix,
                positions=positions,
                units=units,
                figsize=figsize,
                aspect=aspect,
                cmap=cmap,
                norm=norm,
                norm_min=norm_min,
                norm_max=norm_max,
                linthresh=linthresh,
                linscale=linscale,
                cb_ticksize=cb_ticksize,
                cb_fraction=cb_fraction,
                cb_pad=cb_pad,
                cb_tick_values=cb_tick_values,
                cb_tick_labels=cb_tick_labels,
                titlesize=titlesize,
                xlabelsize=xlabelsize,
                ylabelsize=ylabelsize,
                xyticksize=xyticksize,
                grid_pointsize=grid_pointsize,
                position_pointsize=position_pointsize,
                mask_pointsize=mask_pointsize,
                output_path=output_path,
                output_filename=output_filename,
                output_format=output_format,
            )


def plot_fit_subplot_for_plane(
    fit,
    plane_index,
    should_plot_mask=True,
    should_plot_source_grid=False,
    positions=None,
    should_plot_image_plane_pix=False,
    plot_mass_profile_centres=True,
    units="arcsec",
    figsize=None,
    aspect="square",
    cmap="jet",
    norm="linear",
    norm_min=None,
    norm_max=None,
    linthresh=0.05,
    linscale=0.01,
    cb_ticksize=10,
    cb_fraction=0.047,
    cb_pad=0.01,
    cb_tick_values=None,
    cb_tick_labels=None,
    titlesize=10,
    xlabelsize=10,
    ylabelsize=10,
    xyticksize=10,
    mask_pointsize=10,
    position_pointsize=10,
    grid_pointsize=1,
    output_path=None,
    output_filename="lens_fit_plane",
    output_format="show",
):
    """Plot the model datas_ of an analysis, using the *Fitter* class object.

    The visualization and output type can be fully customized.

    Parameters
    -----------
    fit : autolens.lens.fitting.Fitter
        Class containing fit between the model datas_ and observed lens datas_ (including residual_map, chi_squared_map etc.)
    output_path : str
        The path where the datas_ is output if the output_type is a file format (e.g. png, fits)
    output_filename : str
        The name of the file that is output, if the output_type is a file format (e.g. png, fits)
    output_format : str
        How the datas_ is output. File formats (e.g. png, fits) output the datas_ to harddisk. 'show' displays the datas_ \
        in the python interpreter window.
    """

    output_filename += "_" + str(plane_index)

    rows, columns, figsize_tool = aa.plotter_util.get_subplot_rows_columns_figsize(
        number_subplots=4
    )

    mask = fit_plotters.get_mask(fit=fit, should_plot_mask=should_plot_mask)

    if figsize is None:
        figsize = figsize_tool

    plt.figure(figsize=figsize)

    kpc_per_arcsec = fit.tracer.image_plane.kpc_per_arcsec

    image_plane_pix_grid = fit_plotters.get_image_plane_pix_grid(
        should_plot_image_plane_pix, fit
    )

    plt.subplot(rows, columns, 1)

    fit_plotters.plot_image(
        fit=fit,
        mask=mask,
        grid=image_plane_pix_grid,
        positions=positions,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        grid_pointsize=grid_pointsize,
        position_pointsize=position_pointsize,
        mask_pointsize=mask_pointsize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 2)

    fit_plotters.plot_subtracted_image_of_plane(
        fit=fit,
        plane_index=plane_index,
        mask=mask,
        image_plane_pix_grid=image_plane_pix_grid,
        positions=positions,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        mask_pointsize=mask_pointsize,
        position_pointsize=position_pointsize,
        xyticksize=xyticksize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    plt.subplot(rows, columns, 3)

    fit_plotters.plot_model_image_of_plane(
        fit=fit,
        plane_index=plane_index,
        mask=mask,
        plot_mass_profile_centres=plot_mass_profile_centres,
        as_subplot=True,
        units=units,
        kpc_per_arcsec=kpc_per_arcsec,
        figsize=figsize,
        aspect=aspect,
        cmap=cmap,
        norm=norm,
        norm_min=norm_min,
        norm_max=norm_max,
        linthresh=linthresh,
        linscale=linscale,
        cb_ticksize=cb_ticksize,
        cb_fraction=cb_fraction,
        cb_pad=cb_pad,
        cb_tick_values=cb_tick_values,
        cb_tick_labels=cb_tick_labels,
        titlesize=titlesize,
        xlabelsize=xlabelsize,
        ylabelsize=ylabelsize,
        xyticksize=xyticksize,
        mask_pointsize=mask_pointsize,
        output_path=output_path,
        output_filename="",
        output_format=output_format,
    )

    if not fit.tracer.planes[plane_index].has_pixelization:

        plt.subplot(rows, columns, 4)

        traced_grids = fit.tracer.traced_grids_of_planes_from_grid(grid=fit.grid)

        plane_plotters.plane_image(
            plane=fit.tracer.planes[plane_index],
            grid=traced_grids[plane_index],
            positions=None,
            plot_grid=should_plot_source_grid,
            as_subplot=True,
            units=units,
            figsize=figsize,
            aspect=aspect,
            cmap=cmap,
            norm=norm,
            norm_min=norm_min,
            norm_max=norm_max,
            linthresh=linthresh,
            linscale=linscale,
            cb_ticksize=cb_ticksize,
            cb_fraction=cb_fraction,
            cb_pad=cb_pad,
            cb_tick_values=cb_tick_values,
            cb_tick_labels=cb_tick_labels,
            titlesize=titlesize,
            xlabelsize=xlabelsize,
            ylabelsize=ylabelsize,
            xyticksize=xyticksize,
            grid_pointsize=grid_pointsize,
            position_pointsize=position_pointsize,
            output_path=output_path,
            output_filename="",
            output_format=output_format,
        )

    elif fit.tracer.planes[plane_index].has_pixelization:

        ratio = float(
            (
                fit.inversion.mapper.arc_second_maxima[1]
                - fit.inversion.mapper.arc_second_minima[1]
            )
            / (
                fit.inversion.mapper.arc_second_maxima[0]
                - fit.inversion.mapper.arc_second_minima[0]
            )
        )

        if aspect is "square":
            aspect_inv = ratio
        elif aspect is "auto":
            aspect_inv = 1.0 / ratio
        elif aspect is "equal":
            aspect_inv = 1.0

        plt.subplot(rows, columns, 4, aspect=float(aspect_inv))

        inversion_plotters.plot_pixelization_values(
            inversion=fit.inversion,
            positions=None,
            should_plot_grid=False,
            should_plot_centres=False,
            as_subplot=True,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            figsize=figsize,
            aspect=None,
            cmap=cmap,
            norm=norm,
            norm_min=norm_min,
            norm_max=norm_max,
            linthresh=linthresh,
            linscale=linscale,
            cb_ticksize=cb_ticksize,
            cb_fraction=cb_fraction,
            cb_pad=cb_pad,
            cb_tick_values=cb_tick_values,
            cb_tick_labels=cb_tick_labels,
            titlesize=titlesize,
            xlabelsize=xlabelsize,
            ylabelsize=ylabelsize,
            xyticksize=xyticksize,
            output_path=output_path,
            output_filename=None,
            output_format=output_format,
        )

    aa.plotter_util.output_subplot_array(
        output_path=output_path,
        output_filename=output_filename,
        output_format=output_format,
    )

    plt.close()


def plot_fit_individuals(
    fit,
    should_plot_mask=True,
    positions=None,
    should_plot_image_plane_pix=False,
    should_plot_image=False,
    should_plot_noise_map=False,
    should_plot_signal_to_noise_map=False,
    should_plot_model_image=False,
    should_plot_residual_map=False,
    should_plot_normalized_residual_map=False,
    should_plot_chi_squared_map=False,
    should_plot_pixelization_residual_map=False,
    should_plot_pixelization_normalized_residual_map=False,
    should_plot_pixelization_chi_squared_map=False,
    should_plot_pixelization_regularization_weight_map=False,
    should_plot_subtracted_images_of_planes=False,
    should_plot_model_images_of_planes=False,
    should_plot_plane_images_of_planes=False,
    units="arcsec",
    output_path=None,
    output_format="show",
):
    """Plot the model datas_ of an analysis, using the *Fitter* class object.

    The visualization and output type can be fully customized.

    Parameters
    -----------
    fit : autolens.lens.fitting.Fitter
        Class containing fit between the model datas_ and observed lens datas_ (including residual_map, chi_squared_map etc.)
    output_path : str
        The path where the datas_ is output if the output_type is a file format (e.g. png, fits)
    output_format : str
        How the datas_ is output. File formats (e.g. png, fits) output the datas_ to harddisk. 'show' displays the datas_ \
        in the python interpreter window.
    """

    mask = fit_plotters.get_mask(fit=fit, should_plot_mask=should_plot_mask)
    image_plane_pix_grid = fit_plotters.get_image_plane_pix_grid(
        should_plot_image_plane_pix, fit
    )

    traced_grids = fit.tracer.traced_grids_of_planes_from_grid(grid=fit.grid)

    kpc_per_arcsec = fit.tracer.image_plane.kpc_per_arcsec

    if should_plot_image:

        fit_plotters.plot_image(
            fit=fit,
            mask=mask,
            positions=positions,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_noise_map:

        fit_plotters.plot_noise_map(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_signal_to_noise_map:

        fit_plotters.plot_signal_to_noise_map(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_model_image:

        fit_plotters.plot_model_data(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_residual_map:

        fit_plotters.plot_residual_map(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_normalized_residual_map:

        fit_plotters.plot_normalized_residual_map(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_chi_squared_map:

        fit_plotters.plot_chi_squared_map(
            fit=fit,
            mask=mask,
            units=units,
            kpc_per_arcsec=kpc_per_arcsec,
            output_path=output_path,
            output_format=output_format,
        )

    if should_plot_pixelization_residual_map:

        if fit.total_inversions == 1:

            inversion_plotters.plot_pixelization_residual_map(
                inversion=fit.inversion,
                should_plot_grid=True,
                units=units,
                figsize=(20, 20),
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_pixelization_normalized_residual_map:

        if fit.total_inversions == 1:

            inversion_plotters.plot_pixelization_normalized_residual_map(
                inversion=fit.inversion,
                should_plot_grid=True,
                units=units,
                figsize=(20, 20),
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_pixelization_chi_squared_map:

        if fit.total_inversions == 1:

            inversion_plotters.plot_pixelization_chi_squared_map(
                inversion=fit.inversion,
                should_plot_grid=True,
                units=units,
                figsize=(20, 20),
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_pixelization_regularization_weight_map:

        if fit.total_inversions == 1:

            inversion_plotters.plot_pixelization_regularization_weights(
                inversion=fit.inversion,
                should_plot_grid=True,
                units=units,
                figsize=(20, 20),
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_subtracted_images_of_planes:

        for plane_index in range(fit.tracer.total_planes):

            fit_plotters.plot_subtracted_image_of_plane(
                fit=fit,
                plane_index=plane_index,
                mask=mask,
                units=units,
                kpc_per_arcsec=kpc_per_arcsec,
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_model_images_of_planes:

        for plane_index in range(fit.tracer.total_planes):

            fit_plotters.plot_model_image_of_plane(
                fit=fit,
                plane_index=plane_index,
                mask=mask,
                units=units,
                kpc_per_arcsec=kpc_per_arcsec,
                output_path=output_path,
                output_format=output_format,
            )

    if should_plot_plane_images_of_planes:

        for plane_index in range(fit.tracer.total_planes):

            if fit.tracer.planes[plane_index].has_light_profile:

                output_filename = "fit_plane_image_of_plane_" + str(plane_index)

                plane_plotters.plane_image(
                    plane=fit.tracer.planes[plane_index],
                    grid=traced_grids[plane_index],
                    plot_grid=True,
                    units=units,
                    output_path=output_path,
                    output_filename=output_filename,
                    output_format=output_format,
                )
