import autofit as af
import autolens as al
from test_autolens.simulate import simulate_util

import os


def simulate_image_from_galaxies_and_output_to_fits(
    data_resolution,
    data_type,
    sub_size,
    galaxies,
    psf_shape_2d=(51, 51),
    exposure_time=300.0,
    background_sky_level=1.0,
):

    pixel_scales = simulate_util.pixel_scale_from_data_resolution(
        data_resolution=data_resolution
    )
    shape_2d = simulate_util.shape_from_data_resolution(data_resolution=data_resolution)

    # Simulate a simple Gaussian PSF for the image.
    psf = al.kernel.from_gaussian(
        shape_2d=psf_shape_2d, sigma=pixel_scales[0], pixel_scales=pixel_scales
    )

    # Use the input galaxies to setup a tracer, which will generate the image for the simulated Imaging data_type.
    tracer = al.tracer.from_galaxies(galaxies=galaxies)

    # Simulate the Imaging data_type, remembering that we use a special image which ensures edge-effects don't
    # degrade our modeling of the telescope optics (e.al. the PSF convolution).

    simulator = al.simulator.imaging(
        shape_2d=shape_2d,
        pixel_scales=pixel_scales,
        sub_size=sub_size,
        exposure_time=exposure_time,
        psf=psf,
        background_sky_level=background_sky_level,
        add_noise=True,
    )

    imaging = simulator.from_tracer(tracer=tracer)

    # Now, lets output this simulated imaging-simulator to the test_autoarray/simulator folder.
    test_path = "{}/../".format(os.path.dirname(os.path.realpath(__file__)))

    dataset_path = af.path_util.make_and_return_path_from_path_and_folder_names(
        path=test_path, folder_names=["dataset", data_type, data_resolution]
    )

    imaging.output_to_fits(
        image_path=dataset_path + "image.fits",
        psf_path=dataset_path + "psf.fits",
        noise_map_path=dataset_path + "noise_map.fits",
        overwrite=True,
    )

    al.plot.imaging.subplot(
        imaging=imaging,
        output_filename="imaging",
        output_path=dataset_path,
        output_format="png",
    )

    al.plot.imaging.individual(
        imaging=imaging,
        plot_image=True,
        plot_noise_map=True,
        plot_psf=True,
        plot_signal_to_noise_map=True,
        output_path=dataset_path,
        output_format="png",
    )

    al.plot.tracer.subplot(
        tracer=tracer,
        grid=simulator.grid,
        output_filename="tracer",
        output_path=dataset_path,
        output_format="png",
    )

    al.plot.tracer.individual(
        tracer=tracer,
        grid=simulator.grid,
        plot_profile_image=True,
        plot_source_plane=True,
        plot_convergence=True,
        plot_potential=True,
        plot_deflections=True,
        output_path=dataset_path,
        output_format="png",
    )


def make_lens_light_dev_vaucouleurs(data_resolutions, sub_size):

    data_type = "lens_light_dev_vaucouleurs"

    # This lens-only system has a Dev Vaucouleurs spheroid / bulge.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        bulge=al.lp.EllipticalDevVaucouleurs(
            centre=(0.0, 0.0),
            axis_ratio=0.9,
            phi=45.0,
            intensity=0.1,
            effective_radius=1.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, al.galaxy(redshift=1.0)],
        )


def make_lens_bulge_disk(data_resolutions, sub_size):

    data_type = "lens_bulge_disk"

    # This source-only system has a Dev Vaucouleurs spheroid / bulge and surrounding Exponential envelope

    lens_galaxy = al.galaxy(
        redshift=0.5,
        bulge=al.lp.EllipticalDevVaucouleurs(
            centre=(0.0, 0.0),
            axis_ratio=0.9,
            phi=45.0,
            intensity=0.1,
            effective_radius=1.0,
        ),
        envelope=al.lp.EllipticalExponential(
            centre=(0.0, 0.0),
            axis_ratio=0.7,
            phi=60.0,
            intensity=1.0,
            effective_radius=2.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, al.galaxy(redshift=1.0)],
        )


def make_lens_x2_light(data_resolutions, sub_size):

    data_type = "lens_x2_light"

    # This source-only system has two Sersic bulges separated by 2.0"

    lens_galaxy_0 = al.galaxy(
        redshift=0.5,
        bulge=al.lp.EllipticalSersic(
            centre=(-1.0, -1.0),
            axis_ratio=0.8,
            phi=0.0,
            intensity=1.0,
            effective_radius=1.0,
            sersic_index=3.0,
        ),
    )

    lens_galaxy_1 = al.galaxy(
        redshift=0.5,
        bulge=al.lp.EllipticalSersic(
            centre=(1.0, 1.0),
            axis_ratio=0.8,
            phi=0.0,
            intensity=1.0,
            effective_radius=1.0,
            sersic_index=3.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy_0, lens_galaxy_1, al.galaxy(redshift=1.0)],
        )


def make_lens_mass__source_smooth(data_resolutions, sub_size):

    data_type = "lens_mass__source_smooth"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        mass=al.mp.EllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
        ),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.4,
            effective_radius=0.5,
            sersic_index=1.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )


def make_lens_mass__source_cuspy(data_resolutions, sub_size):

    data_type = "lens_mass__source_cuspy"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        mass=al.mp.EllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
        ),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.1,
            effective_radius=0.5,
            sersic_index=3.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )


def make_lens_sis__source_smooth(data_resolutions, sub_size):

    data_type = "lens_sis__source_smooth"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.6),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.4,
            effective_radius=0.5,
            sersic_index=1.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )


def make_lens_mass__source_smooth__offset_centre(data_resolutions, sub_size):

    data_type = "lens_mass__source_smooth__offset_centre"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        mass=al.mp.SphericalIsothermal(centre=(2.0, 2.0), einstein_radius=1.2),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(2.0, 2.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.4,
            effective_radius=0.5,
            sersic_index=1.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )


def make_lens_light__source_smooth(data_resolutions, sub_size):

    data_type = "lens_light__source_smooth"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.9,
            phi=45.0,
            intensity=0.5,
            effective_radius=0.8,
            sersic_index=4.0,
        ),
        mass=al.mp.EllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
        ),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.4,
            effective_radius=0.5,
            sersic_index=1.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )


def make_lens_light__source_cuspy(data_resolutions, sub_size):

    data_type = "lens_light__source_cuspy"

    # This source-only system has a smooth source (low Sersic Index) and simple SIE mass profile.

    lens_galaxy = al.galaxy(
        redshift=0.5,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.9,
            phi=45.0,
            intensity=0.5,
            effective_radius=0.8,
            sersic_index=4.0,
        ),
        mass=al.mp.EllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
        ),
    )

    source_galaxy = al.galaxy(
        redshift=1.0,
        light=al.lp.EllipticalSersic(
            centre=(0.0, 0.0),
            axis_ratio=0.8,
            phi=60.0,
            intensity=0.1,
            effective_radius=0.5,
            sersic_index=3.0,
        ),
    )

    for data_resolution in data_resolutions:

        simulate_image_from_galaxies_and_output_to_fits(
            data_type=data_type,
            data_resolution=data_resolution,
            sub_size=sub_size,
            galaxies=[lens_galaxy, source_galaxy],
        )