import os

import numpy as np
import pytest
import shutil
from astropy import units
from astropy.coordinates import Angle
from astropy.modeling import functional_models

import autolens as al
from autolens import exc

test_data_dir = "{}/../../test_files/array/".format(
    os.path.dirname(os.path.realpath(__file__))
)


class TestImagingData:
    class TestConstructor:
        def test__setup_image__correct_attributes(self):
            array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

            psf = al.PSF(array=3.0 * np.ones((3, 3)), pixel_scale=1.0)
            noise_map = 5.0 * np.ones((3, 3))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=0.1,
                noise_map=noise_map,
                psf=psf,
                background_noise_map=7.0 * np.ones((3, 3)),
                poisson_noise_map=9.0 * np.ones((3, 3)),
                exposure_time_map=11.0 * np.ones((3, 3)),
            )

            assert imaging_data.image == pytest.approx(
                np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]), 1e-2
            )
            assert (imaging_data.psf == 3.0 * np.ones((3, 3))).all()
            assert (imaging_data.noise_map == 5.0 * np.ones((3, 3))).all()
            assert (imaging_data.background_noise_map == 7.0 * np.ones((3, 3))).all()
            assert (imaging_data.poisson_noise_map == 9.0 * np.ones((3, 3))).all()
            assert (imaging_data.exposure_time_map == 11.0 * np.ones((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

    class TestEstimateNoiseFromImage:
        def test__image_and_exposure_time_all_1s__no_background__noise_is_all_1s(self):
            # Imaging (eps) = 1.0
            # Background (eps) = 0.0
            # Exposure times = 1.0 s
            # Imaging (counts) = 1.0
            # Background (counts) = 0.0

            # Noise (counts) = sqrt(1.0 + 0.0**2) = 1.0
            # Noise (eps) = 1.0 / 1.0

            array = np.ones((3, 3))
            exposure_time = np.ones((3, 3))
            background_noise = np.zeros((3, 3))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert (imaging_data.estimated_noise_map == np.ones((3, 3))).all()

        def test__image_all_4s__exposure_time_all_1s__no_background__noise_is_all_2s(
            self
        ):
            # Imaging (eps) = 4.0
            # Background (eps) = 0.0
            # Exposure times = 1.0 s
            # Imaging (counts) = 4.0
            # Background (counts) = 0.0

            # Noise (counts) = sqrt(4.0 + 0.0**2) = 2.0
            # Noise (eps) = 2.0 / 1.0

            array = 4.0 * np.ones((4, 2))

            exposure_time = np.ones((4, 2))
            background_noise = np.zeros((4, 2))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert (imaging_data.estimated_noise_map == 2.0 * np.ones((4, 2))).all()

        def test__image_all_1s__exposure_time_all_4s__no_background__noise_is_all_2_divided_4_so_halves(
            self
        ):
            # Imaging (eps) = 1.0
            # Background (eps) = 0.0
            # Exposure times = 4.0 s
            # Imaging (counts) = 4.0
            # Background (counts) = 0.0

            # Noise (counts) = sqrt(4.0 + 0.0**2) = 2.0
            # Noise (eps) = 2.0 / 4.0 = 0.5

            array = np.ones((1, 5))

            exposure_time = 4.0 * np.ones((1, 5))

            background_noise = np.zeros((1, 5))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert (imaging_data.estimated_noise_map == 0.5 * np.ones((1, 5))).all()

        def test__image_and_exposure_times_range_of_values__no_background__noises_estimates_correct(
            self
        ):
            array = np.array([[5.0, 3.0], [10.0, 20.0]])

            exposure_time = al.ScaledSquarePixelArray(
                np.array([[1.0, 2.0], [3.0, 4.0]]), pixel_scale=1.0
            )

            background_noise = np.zeros((2, 2))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert (
                imaging_data.estimated_noise_map
                == np.array(
                    [
                        [np.sqrt(5.0), np.sqrt(6.0) / 2.0],
                        [np.sqrt(30.0) / 3.0, np.sqrt(80.0) / 4.0],
                    ]
                )
            ).all()

        def test__image_and_exposure_times_all_1s__background_is_float_sqrt_3__noise_is_all_2s(
            self
        ):
            # Imaging (eps) = 1.0
            # Background (eps) = sqrt(3.0)
            # Exposure times = 1.0 s
            # Imaging (counts) = 1.0
            # Background (counts) = sqrt(3.0)

            # Noise (counts) = sqrt(1.0 + sqrt(3.0)**2) = sqrt(1.0 + 3.0) = 2.0
            # Noise (eps) = 2.0 / 1.0 = 2.0

            array = np.ones((3, 3))

            exposure_time = np.ones((3, 3))

            background_noise = 3.0 ** 0.5 * np.ones((3, 3))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                2.0 * np.ones((3, 3)), 1e-2
            )

        def test__image_and_exposure_times_all_1s__background_is_float_5__noise_all_correct(
            self
        ):
            # Imaging (eps) = 1.0
            # Background (eps) = 5.0
            # Exposure times = 1.0 s
            # Imaging (counts) = 1.0
            # Background (counts) = 5.0

            # Noise (counts) = sqrt(1.0 + 5**2)
            # Noise (eps) = sqrt(1.0 + 5**2) / 1.0

            array = np.ones((2, 3))

            exposure_time = np.ones((2, 3))

            background_noise = 5 * np.ones((2, 3))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                np.array(
                    [
                        [np.sqrt(1.0 + 25.0), np.sqrt(1.0 + 25.0), np.sqrt(1.0 + 25.0)],
                        [np.sqrt(1.0 + 25.0), np.sqrt(1.0 + 25.0), np.sqrt(1.0 + 25.0)],
                    ]
                ),
                1e-2,
            )

        def test__image_all_1s__exposure_times_all_2s__background_is_float_5__noise_all_correct(
            self
        ):
            # Imaging (eps) = 1.0
            # Background (eps) = 5.0
            # Exposure times = 2.0 s
            # Imaging (counts) = 2.0
            # Background (counts) = 10.0

            # Noise (counts) = sqrt(2.0 + 10**2) = sqrt(2.0 + 100.0)
            # Noise (eps) = sqrt(2.0 + 100.0) / 2.0

            array = np.ones((2, 3))

            exposure_time = 2.0 * np.ones((2, 3))
            background_noise = 5.0 * np.ones((2, 3))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                np.array(
                    [
                        [
                            np.sqrt(2.0 + 100.0) / 2.0,
                            np.sqrt(2.0 + 100.0) / 2.0,
                            np.sqrt(2.0 + 100.0) / 2.0,
                        ],
                        [
                            np.sqrt(2.0 + 100.0) / 2.0,
                            np.sqrt(2.0 + 100.0) / 2.0,
                            np.sqrt(2.0 + 100.0) / 2.0,
                        ],
                    ]
                ),
                1e-2,
            )

        def test__same_as_above_but_different_image_values_in_each_pixel_and_new_background_values(
            self
        ):
            # Can use pattern from previous test for values

            array = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

            exposure_time = np.ones((3, 2))
            background_noise = 12.0 * np.ones((3, 2))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                np.array(
                    [
                        [np.sqrt(1.0 + 144.0), np.sqrt(2.0 + 144.0)],
                        [np.sqrt(3.0 + 144.0), np.sqrt(4.0 + 144.0)],
                        [np.sqrt(5.0 + 144.0), np.sqrt(6.0 + 144.0)],
                    ]
                ),
                1e-2,
            )

        def test__image_and_exposure_times_range_of_values__background_has_value_9___noise_estimates_correct(
            self
        ):
            # Use same pattern as above, noting that here our background values are now being converts to counts using
            # different exposure time and then being squared.

            array = np.array([[5.0, 3.0], [10.0, 20.0]])

            exposure_time = np.array([[1.0, 2.0], [3.0, 4.0]])
            background_noise = 9.0 * np.ones((2, 2))

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                np.array(
                    [
                        [np.sqrt(5.0 + 81.0), np.sqrt(6.0 + 18.0 ** 2.0) / 2.0],
                        [
                            np.sqrt(30.0 + 27.0 ** 2.0) / 3.0,
                            np.sqrt(80.0 + 36.0 ** 2.0) / 4.0,
                        ],
                    ]
                ),
                1e-2,
            )

        def test__image_and_exposure_times_and_background_are_all_ranges_of_values__noise_estimates_correct(
            self
        ):
            # Use same pattern as above, noting that we are now also using a variable background signal_to_noise_ratio map.

            array = np.array([[5.0, 3.0], [10.0, 20.0]])

            exposure_time = np.array([[1.0, 2.0], [3.0, 4.0]])

            background_noise = np.array([[5.0, 6.0], [7.0, 8.0]])

            imaging_data = al.ImagingData(
                image=array,
                pixel_scale=1.0,
                psf=al.PSF(array=np.ones((3, 3)), pixel_scale=1.0),
                exposure_time_map=exposure_time,
                background_noise_map=background_noise,
            )

            assert imaging_data.estimated_noise_map == pytest.approx(
                np.array(
                    [
                        [np.sqrt(5.0 + 5.0 ** 2.0), np.sqrt(6.0 + 12.0 ** 2.0) / 2.0],
                        [
                            np.sqrt(30.0 + 21.0 ** 2.0) / 3.0,
                            np.sqrt(80.0 + 32.0 ** 2.0) / 4.0,
                        ],
                    ]
                ),
                1e-2,
            )

    class TestEstimateDataGrid(object):
        def test__via_edges__input_all_ones__sky_bg_level_1(self):
            imaging_data = al.ImagingData(
                image=np.ones((3, 3)),
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )

            sky_noise = imaging_data.background_noise_from_edges(no_edges=1)

            assert sky_noise == 0.0

        def test__via_edges__3x3_image_simple_gaussian__answer_ignores_central_pixel(
            self
        ):
            image_array = np.array([[1, 1, 1], [1, 100, 1], [1, 1, 1]])

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=1)

            assert sky_noise == 0.0

        def test__via_edges__4x3_image_simple_gaussian__ignores_central_pixels(self):
            image_array = np.array([[1, 1, 1], [1, 100, 1], [1, 100, 1], [1, 1, 1]])

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=1)

            assert sky_noise == 0.0

        def test__via_edges__4x4_image_simple_gaussian__ignores_central_pixels(self):
            image_array = np.array(
                [[1, 1, 1, 1], [1, 100, 100, 1], [1, 100, 100, 1], [1, 1, 1, 1]]
            )

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=1)

            assert sky_noise == 0.0

        def test__via_edges__5x5_image_simple_gaussian_two_edges__ignores_central_pixel(
            self
        ):
            image_array = np.array(
                [
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 100, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                ]
            )

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=2)

            assert sky_noise == 0.0

        def test__via_edges__6x5_image_two_edges__values(self):
            image_array = np.array(
                [
                    [0, 1, 2, 3, 4],
                    [5, 6, 7, 8, 9],
                    [10, 11, 100, 12, 13],
                    [14, 15, 100, 16, 17],
                    [18, 19, 20, 21, 22],
                    [23, 24, 25, 26, 27],
                ]
            )

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=2)

            assert sky_noise == np.std(np.arange(28))

        def test__via_edges__7x7_image_three_edges__values(self):
            image_array = np.array(
                [
                    [0, 1, 2, 3, 4, 5, 6],
                    [7, 8, 9, 10, 11, 12, 13],
                    [14, 15, 16, 17, 18, 19, 20],
                    [21, 22, 23, 100, 24, 25, 26],
                    [27, 28, 29, 30, 31, 32, 33],
                    [34, 35, 36, 37, 38, 39, 40],
                    [41, 42, 43, 44, 45, 46, 47],
                ]
            )

            imaging_data = al.ImagingData(
                image=image_array,
                noise_map=np.ones((3, 3)),
                psf=np.ones((3, 3)),
                pixel_scale=0.1,
            )
            sky_noise = imaging_data.background_noise_from_edges(no_edges=3)

            assert sky_noise == np.std(np.arange(48))

    class TestNewImagingDataResized:
        def test__all_components_resized__psf_is_not(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)
            image_array[3, 3] = 2.0

            noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            noise_map_array[3, 3] = 3.0

            background_noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_noise_map_array[3, 3] = 4.0

            exposure_time_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            exposure_time_map_array[3, 3] = 5.0

            background_sky_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_sky_map_array[3, 3] = 6.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_with_resized_arrays(new_shape=(4, 4))

            assert (
                imaging_data.image
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 2.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.noise_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 3.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.background_noise_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 4.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.exposure_time_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 5.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.background_sky_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 6.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()

            assert imaging_data.poisson_noise_map == None

            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

        def test__resize_psf(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
            )

            imaging_data = imaging_data.new_imaging_data_with_resized_psf(new_shape=(1, 1))

            assert (imaging_data.image == np.ones((6, 6))).all()
            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((1, 1))).all()
            assert imaging_data.origin == (0.0, 0.0)

        def test__input_new_centre_pixels__arrays_use_new_centre__psf_does_not(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)
            image_array[3, 3] = 2.0

            noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            noise_map_array[3, 3] = 3.0

            background_noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_noise_map_array[3, 3] = 4.0

            exposure_time_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            exposure_time_map_array[3, 3] = 5.0

            background_sky_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_sky_map_array[3, 3] = 6.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_with_resized_arrays(
                new_shape=(3, 3), new_centre_pixels=(3, 3)
            )

            assert (
                imaging_data.image
                == np.array([[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.noise_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 3.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.background_noise_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 4.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.exposure_time_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 5.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.background_sky_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 6.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()

            assert imaging_data.poisson_noise_map == None

            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

        def test__input_new_centre_arcsec__arrays_use_new_centre__psf_does_not(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)
            image_array[3, 3] = 2.0

            noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            noise_map_array[3, 3] = 3.0

            background_noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_noise_map_array[3, 3] = 4.0

            exposure_time_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            exposure_time_map_array[3, 3] = 5.0

            background_sky_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_sky_map_array[3, 3] = 6.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_with_resized_arrays(
                new_shape=(3, 3), new_centre_arcsec=(-0.5, 0.5)
            )

            assert (
                imaging_data.image
                == np.array([[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.noise_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 3.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.background_noise_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 4.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.exposure_time_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 5.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()
            assert (
                imaging_data.background_sky_map
                == np.array([[1.0, 1.0, 1.0], [1.0, 6.0, 1.0], [1.0, 1.0, 1.0]])
            ).all()

            assert imaging_data.poisson_noise_map == None

            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

        def test__input_both_centres__raises_error(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)
            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
            )

            with pytest.raises(exc.DataException):
                imaging_data.new_imaging_data_with_resized_arrays(
                    new_shape=(3, 3),
                    new_centre_pixels=(3, 3),
                    new_centre_arcsec=(-0.5, 0.5),
                )

    class TestNewImagingModifiedImage:
        def test__imaging_data_returns_with_modified_image(self):
            image_array = al.ScaledSquarePixelArray(np.ones((4, 4)), pixel_scale=1.0)
            image_array[2, 2] = 2.0

            noise_map_array = al.ScaledSquarePixelArray(
                np.ones((4, 4)), pixel_scale=1.0
            )
            noise_map_array[2, 2] = 3.0

            background_noise_map_array = al.ScaledSquarePixelArray(
                np.ones((4, 4)), pixel_scale=1.0
            )
            background_noise_map_array[2, 2] = 4.0

            exposure_time_map_array = al.ScaledSquarePixelArray(
                np.ones((4, 4)), pixel_scale=1.0
            )
            exposure_time_map_array[2, 2] = 5.0

            background_sky_map_array = al.ScaledSquarePixelArray(
                np.ones((4, 4)), pixel_scale=1.0
            )
            background_sky_map_array[2, 2] = 6.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            modified_image = al.ScaledSquarePixelArray(np.ones((4, 4)), pixel_scale=1.0)
            modified_image[2, 2] = 10.0

            imaging_data = imaging_data.new_imaging_data_with_modified_image(
                modified_image=modified_image
            )

            assert (
                imaging_data.image
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 10.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.noise_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 3.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.background_noise_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 4.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.exposure_time_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 5.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()
            assert (
                imaging_data.background_sky_map
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 6.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                )
            ).all()

            assert imaging_data.poisson_noise_map == None

            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

    class TestNewImagingBinnedUp:
        def test__all_components_binned_up_correct(self):
            image_array = al.ScaledSquarePixelArray(np.ones((6, 6)), pixel_scale=1.0)
            image_array[3:5, 3] = 2.0
            binned_image_util = al.binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
                array_2d=image_array, bin_up_factor=2
            )

            noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            noise_map_array[3, 3:5] = 3.0
            binned_noise_map_util = al.binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
                array_2d=noise_map_array, bin_up_factor=2
            )

            background_noise_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_noise_map_array[3:5, 3] = 4.0
            binned_background_noise_map_util = al.binning_util.binned_array_2d_using_quadrature_from_array_2d_and_bin_up_factor(
                array_2d=background_noise_map_array, bin_up_factor=2
            )

            exposure_time_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            exposure_time_map_array[3, 3:5] = 5.0
            binned_exposure_time_map_util = al.binning_util.binned_array_2d_using_sum_from_array_2d_and_bin_up_factor(
                array_2d=exposure_time_map_array, bin_up_factor=2
            )

            background_sky_map_array = al.ScaledSquarePixelArray(
                np.ones((6, 6)), pixel_scale=1.0
            )
            background_sky_map_array[3, 3:5] = 6.0
            binned_background_sky_map_util = al.binning_util.binned_up_array_2d_using_mean_from_array_2d_and_bin_up_factor(
                array_2d=background_sky_map_array, bin_up_factor=2
            )

            psf = al.PSF(array=np.ones((3, 5)), pixel_scale=1.0)
            psf_util = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5
            )

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=psf,
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_with_binned_up_arrays(bin_up_factor=2)

            assert (imaging_data.image == binned_image_util).all()
            assert (imaging_data.psf == psf_util).all()
            assert (imaging_data.noise_map == binned_noise_map_util).all()
            assert (
                imaging_data.background_noise_map == binned_background_noise_map_util
            ).all()
            assert (imaging_data.exposure_time_map == binned_exposure_time_map_util).all()
            assert (imaging_data.background_sky_map == binned_background_sky_map_util).all()
            assert imaging_data.poisson_noise_map == None

            assert imaging_data.pixel_scale == 2.0
            assert imaging_data.image.pixel_scale == 2.0
            assert imaging_data.psf.pixel_scale == pytest.approx(1.66666666666, 1.0e-4)
            assert imaging_data.noise_map.pixel_scale == 2.0
            assert imaging_data.background_noise_map.pixel_scale == 2.0
            assert imaging_data.exposure_time_map.pixel_scale == 2.0
            assert imaging_data.background_sky_map.pixel_scale == 2.0

            assert imaging_data.origin == (0.0, 0.0)

    class TestNewSNRLimit:
        def test__signal_to_noise_limit_above_max_signal_to_noise__signal_to_noise_map_unchanged(
            self
        ):
            image_array = al.ScaledSquarePixelArray(
                20.0 * np.ones((2, 2)), pixel_scale=1.0
            )
            image_array[1, 1] = 5.0

            noise_map_array = al.ScaledSquarePixelArray(
                5.0 * np.ones((2, 2)), pixel_scale=1.0
            )
            noise_map_array[1, 1] = 2.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=1.0 * np.ones((2, 2)),
                exposure_time_map=2.0 * np.ones((2, 2)),
                background_sky_map=3.0 * np.ones((2, 2)),
            )

            imaging_data = imaging_data.new_imaging_data_with_signal_to_noise_limit(
                signal_to_noise_limit=100.0
            )

            assert (imaging_data.image == np.array([[20.0, 20.0], [20.0, 5.0]])).all()

            assert (imaging_data.noise_map == np.array([[5.0, 5.0], [5.0, 2.0]])).all()

            assert (
                imaging_data.signal_to_noise_map == np.array([[4.0, 4.0], [4.0, 2.5]])
            ).all()

            assert imaging_data.pixel_scale == 1.0
            assert (imaging_data.psf == np.zeros((3, 3))).all()
            assert (imaging_data.background_noise_map == np.ones((2, 2))).all()
            assert (imaging_data.exposure_time_map == 2.0 * np.ones((2, 2))).all()
            assert (imaging_data.background_sky_map == 3.0 * np.ones((2, 2))).all()

        def test__signal_to_noise_limit_below_max_signal_to_noise__signal_to_noise_map_capped_to_limit(
            self
        ):
            image_array = al.ScaledSquarePixelArray(
                20.0 * np.ones((2, 2)), pixel_scale=1.0
            )
            image_array[1, 1] = 5.0

            noise_map_array = al.ScaledSquarePixelArray(
                5.0 * np.ones((2, 2)), pixel_scale=1.0
            )
            noise_map_array[1, 1] = 2.0

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=1.0 * np.ones((2, 2)),
                exposure_time_map=2.0 * np.ones((2, 2)),
                background_sky_map=3.0 * np.ones((2, 2)),
            )

            imaging_data_capped = imaging_data.new_imaging_data_with_signal_to_noise_limit(
                signal_to_noise_limit=2.0
            )

            assert (
                imaging_data_capped.image == np.array([[20.0, 20.0], [20.0, 5.0]])
            ).all()

            assert (
                imaging_data_capped.noise_map == np.array([[10.0, 10.0], [10.0, 2.5]])
            ).all()

            assert (
                imaging_data_capped.signal_to_noise_map
                == np.array([[2.0, 2.0], [2.0, 2.0]])
            ).all()

            assert imaging_data_capped.pixel_scale == 1.0
            assert (imaging_data_capped.psf == np.zeros((3, 3))).all()
            assert (imaging_data_capped.background_noise_map == np.ones((2, 2))).all()
            assert (imaging_data_capped.exposure_time_map == 2.0 * np.ones((2, 2))).all()
            assert (imaging_data_capped.background_sky_map == 3.0 * np.ones((2, 2))).all()

            imaging_data_capped = imaging_data.new_imaging_data_with_signal_to_noise_limit(
                signal_to_noise_limit=3.0
            )

            assert (
                imaging_data_capped.image == np.array([[20.0, 20.0], [20.0, 5.0]])
            ).all()

            assert (
                imaging_data_capped.noise_map
                == np.array([[(20.0 / 3.0), (20.0 / 3.0)], [(20.0 / 3.0), 2.0]])
            ).all()

            assert (
                imaging_data_capped.signal_to_noise_map
                == np.array([[3.0, 3.0], [3.0, 2.5]])
            ).all()

            assert imaging_data_capped.pixel_scale == 1.0
            assert (imaging_data_capped.psf == np.zeros((3, 3))).all()
            assert (imaging_data_capped.background_noise_map == np.ones((2, 2))).all()
            assert (imaging_data_capped.exposure_time_map == 2.0 * np.ones((2, 2))).all()
            assert (imaging_data_capped.background_sky_map == 3.0 * np.ones((2, 2))).all()

    class TestNewImageConvertedFrom:
        def test__counts__all_arrays_in_units_of_flux_are_converted(self):
            image_array = al.ScaledSquarePixelArray(np.ones((3, 3)), pixel_scale=1.0)
            noise_map_array = al.ScaledSquarePixelArray(
                2.0 * np.ones((3, 3)), pixel_scale=1.0
            )
            background_noise_map_array = al.ScaledSquarePixelArray(
                3.0 * np.ones((3, 3)), pixel_scale=1.0
            )
            exposure_time_map_array = al.ScaledSquarePixelArray(
                0.5 * np.ones((3, 3)), pixel_scale=1.0
            )
            background_sky_map_array = al.ScaledSquarePixelArray(
                6.0 * np.ones((3, 3)), pixel_scale=1.0
            )

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                poisson_noise_map=None,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_converted_from_electrons()

            assert (imaging_data.image == 2.0 * np.ones((3, 3))).all()
            assert (imaging_data.noise_map == 4.0 * np.ones((3, 3))).all()
            assert (imaging_data.background_noise_map == 6.0 * np.ones((3, 3))).all()
            assert imaging_data.poisson_noise_map == None
            assert (imaging_data.background_sky_map == 12.0 * np.ones((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

        def test__adus__all_arrays_in_units_of_flux_are_converted(self):
            image_array = al.ScaledSquarePixelArray(np.ones((3, 3)), pixel_scale=1.0)
            noise_map_array = al.ScaledSquarePixelArray(
                2.0 * np.ones((3, 3)), pixel_scale=1.0
            )
            background_noise_map_array = al.ScaledSquarePixelArray(
                3.0 * np.ones((3, 3)), pixel_scale=1.0
            )
            exposure_time_map_array = al.ScaledSquarePixelArray(
                0.5 * np.ones((3, 3)), pixel_scale=1.0
            )
            background_sky_map_array = al.ScaledSquarePixelArray(
                6.0 * np.ones((3, 3)), pixel_scale=1.0
            )

            imaging_data = al.ImagingData(
                image=image_array,
                pixel_scale=1.0,
                psf=al.PSF(np.zeros((3, 3)), pixel_scale=1.0),
                noise_map=noise_map_array,
                background_noise_map=background_noise_map_array,
                poisson_noise_map=None,
                exposure_time_map=exposure_time_map_array,
                background_sky_map=background_sky_map_array,
            )

            imaging_data = imaging_data.new_imaging_data_converted_from_adus(gain=2.0)

            assert (imaging_data.image == 2.0 * 2.0 * np.ones((3, 3))).all()
            assert (imaging_data.noise_map == 2.0 * 4.0 * np.ones((3, 3))).all()
            assert (imaging_data.background_noise_map == 2.0 * 6.0 * np.ones((3, 3))).all()
            assert imaging_data.poisson_noise_map == None
            assert (imaging_data.background_sky_map == 2.0 * 12.0 * np.ones((3, 3))).all()
            assert imaging_data.origin == (0.0, 0.0)

    class TestNewImageWithPoissonNoiseAdded:
        def test__mock_image_all_1s__poisson_noise_is_added_correct(self):
            psf = al.PSF(array=np.ones((3, 3)), pixel_scale=3.0, renormalize=False)
            imaging_data = al.ImagingData(
                image=np.ones((4, 4)),
                pixel_scale=3.0,
                psf=psf,
                noise_map=np.ones((4, 4)),
                exposure_time_map=3.0 * np.ones((4, 4)),
                background_sky_map=4.0 * np.ones((4, 4)),
            )

            mock_image = np.ones((4, 4))
            mock_image_with_sky = mock_image + 4.0 * np.ones((4, 4))
            mock_image_with_sky_and_noise = (
                mock_image_with_sky
                + al.generate_poisson_noise(
                    image=mock_image_with_sky,
                    exposure_time_map=3.0 * np.ones((4, 4)),
                    seed=1,
                )
            )

            mock_image_with_noise = mock_image_with_sky_and_noise - 4.0 * np.ones(
                (4, 4)
            )

            imaging_with_noise = imaging_data.new_imaging_data_with_poisson_noise_added(seed=1)

            assert (imaging_with_noise.image == mock_image_with_noise).all()


class TestNoiseMap(object):
    class TestFromImageAndBackgroundNoiseMap:
        def test__image_all_1s__bg_noise_all_1s__exposure_time_all_1s__noise_map_all_sqrt_2s(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(2.0)], [np.sqrt(2.0), np.sqrt(2.0)]]
                )
            ).all()

        def test__image_all_2s__bg_noise_all_1s__exposure_time_all_1s__noise_map_all_sqrt_3s(
            self
        ):
            imaging_data = np.array([[2.0, 2.0], [2.0, 2.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(3.0), np.sqrt(3.0)], [np.sqrt(3.0), np.sqrt(3.0)]]
                )
            ).all()

        def test__image_all_1s__bg_noise_all_2s__exposure_time_all_1s__noise_map_all_sqrt_5s(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            background_noise_map = np.array([[2.0, 2.0], [2.0, 2.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(5.0), np.sqrt(5.0)], [np.sqrt(5.0), np.sqrt(5.0)]]
                )
            ).all()

        def test__image_all_1s__bg_noise_all_1s__exposure_time_all_2s__noise_map_all_sqrt_6s_over_2(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[2.0, 2.0], [2.0, 2.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (
                noise_map
                == np.array(
                    [
                        [np.sqrt(6.0) / 2.0, np.sqrt(6.0) / 2.0],
                        [np.sqrt(6.0) / 2.0, np.sqrt(6.0) / 2.0],
                    ]
                )
            ).all()

        def test__image_all_negative_2s__bg_noise_all_1s__exposure_time_all_1s__noise_map_all_1s(
            self
        ):
            imaging_data = np.array([[-2.0, -2.0], [-2.0, -2.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (noise_map == np.array([[1.0, 1.0], [1.0, 1.0]])).all()

        def test__same_as_above__use_different_values_in_different_array_elemets(self):
            imaging_data = np.array([[1.0, 2.0], [2.0, 3.0]])
            background_noise_map = np.array([[1.0, 1.0], [2.0, 3.0]])
            exposure_time_map = np.array([[4.0, 3.0], [2.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                gain=1.0,
                exposure_time_map=exposure_time_map,
            )

            assert (
                noise_map
                == np.array(
                    [
                        [np.sqrt(20.0) / 4.0, np.sqrt(15.0) / 3.0],
                        [np.sqrt(20.0) / 2.0, np.sqrt(12.0)],
                    ]
                )
            ).all()

        def test__convert_from_electrons__image_all_1s__bg_noise_all_1s__exposure_time_all_1s__noise_map_all_sqrt_2s(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                exposure_time_map=exposure_time_map,
                gain=2.0,
                convert_from_electrons=True,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(2.0)], [np.sqrt(2.0), np.sqrt(2.0)]]
                )
            ).all()

        def test__convert_from_electrons__image_all_negative_2s__bg_noise_all_1s__exposure_time_all_10s__noise_map_all_1s(
            self
        ):
            imaging_data = np.array([[-2.0, -2.0], [-2.0, -2.0]])
            background_noise_map = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[10.0, 10.0], [10.0, 10.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                exposure_time_map=exposure_time_map,
                gain=1.0,
                convert_from_electrons=True,
            )

            assert (noise_map == np.array([[1.0, 1.0], [1.0, 1.0]])).all()

        def test__convert_from_electrons__same_as_above__use_different_values_in_different_array_elemets(
            self
        ):
            imaging_data = np.array([[1.0, 2.0], [2.0, 3.0]])
            background_noise_map = np.array([[1.0, 1.0], [2.0, 3.0]])
            exposure_time_map = np.array([[10.0, 11.0], [12.0, 13.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                exposure_time_map=exposure_time_map,
                gain=4.0,
                convert_from_electrons=True,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(3.0)], [np.sqrt(6.0), np.sqrt(12.0)]]
                )
            ).all()

        def test__convert_from_adus__same_as_above__gain_is_1__same_values(self):
            imaging_data = np.array([[1.0, 2.0], [2.0, 3.0]])
            background_noise_map = np.array([[1.0, 1.0], [2.0, 3.0]])
            exposure_time_map = np.array([[10.0, 11.0], [12.0, 13.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                exposure_time_map=exposure_time_map,
                gain=1.0,
                convert_from_adus=True,
            )

            assert (
                noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(3.0)], [np.sqrt(6.0), np.sqrt(12.0)]]
                )
            ).all()

        def test__convert_from_adus__same_as_above__gain_is_2__values_change(self):
            imaging_data = np.array([[1.0, 2.0], [2.0, 3.0]])
            background_noise_map = np.array([[1.0, 1.0], [2.0, 3.0]])
            exposure_time_map = np.array([[10.0, 11.0], [12.0, 13.0]])

            noise_map = al.NoiseMap.from_image_and_background_noise_map(
                pixel_scale=0.1,
                image=imaging_data,
                background_noise_map=background_noise_map,
                exposure_time_map=exposure_time_map,
                gain=2.0,
                convert_from_adus=True,
            )

            assert (
                noise_map
                == np.array(
                    [
                        [np.sqrt(6.0) / 2.0, np.sqrt(8.0) / 2.0],
                        [np.sqrt(20.0) / 2.0, np.sqrt(42.0) / 2.0],
                    ]
                )
            ).all()


class TestPoissonNoiseMap(object):
    class TestFromImageAndExposureTimeMap:
        def test__image_all_1s__exposure_time_all_1s__noise_map_all_1s(self):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=1.0,
            )

            assert (poisson_noise_map == np.array([[1.0, 1.0], [1.0, 1.0]])).all()

        def test__image_all_2s_and_3s__exposure_time_all_1s__noise_map_all_sqrt_2s_and_3s(
            self
        ):
            imaging_data = np.array([[2.0, 2.0], [3.0, 3.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=1.0,
            )

            assert (
                poisson_noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(2.0)], [np.sqrt(3.0), np.sqrt(3.0)]]
                )
            ).all()

        def test__image_all_1s__exposure_time_all__2s_and_3s__noise_map_all_sqrt_2s_and_3s(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[2.0, 2.0], [3.0, 3.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=1.0,
            )

            assert (
                poisson_noise_map
                == np.array(
                    [
                        [np.sqrt(2.0) / 2.0, np.sqrt(2.0) / 2.0],
                        [np.sqrt(3.0) / 3.0, np.sqrt(3.0) / 3.0],
                    ]
                )
            ).all()

        def test__image_all_1s__exposure_time_all_1s__noise_map_all_1s__gain_is_2__ignores_gain(
            self
        ):
            imaging_data = np.array([[1.0, 1.0], [1.0, 1.0]])
            exposure_time_map = np.array([[1.0, 1.0], [1.0, 1.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=2.0,
            )

            assert (
                poisson_noise_map
                == np.array(
                    [[np.sqrt(1.0), np.sqrt(1.0)], [np.sqrt(1.0), np.sqrt(1.0)]]
                )
            ).all()

        def test__convert_from_electrons_is_true__image_already_in_counts_so_exposure_time_ignored(
            self
        ):
            imaging_data = np.array([[2.0, 2.0], [3.0, 3.0]])
            exposure_time_map = np.array([[10.0, 10.0], [10.0, 10.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=4.0,
                convert_from_electrons=True,
            )

            assert (
                poisson_noise_map
                == np.array(
                    [[np.sqrt(2.0), np.sqrt(2.0)], [np.sqrt(3.0), np.sqrt(3.0)]]
                )
            ).all()

        def test__same_as_above__convert_from_adus__includes_gain_multiplication(self):
            imaging_data = np.array([[2.0, 2.0], [3.0, 3.0]])
            exposure_time_map = np.array([[10.0, 10.0], [10.0, 10.0]])

            poisson_noise_map = al.PoissonNoiseMap.from_image_and_exposure_time_map(
                pixel_scale=0.1,
                image=imaging_data,
                exposure_time_map=exposure_time_map,
                gain=2.0,
                convert_from_adus=True,
            )

            assert (
                poisson_noise_map
                == np.array(
                    [
                        [np.sqrt(2.0 * 2.0) / 2.0, np.sqrt(2.0 * 2.0) / 2.0],
                        [np.sqrt(2.0 * 3.0) / 2.0, np.sqrt(2.0 * 3.0) / 2.0],
                    ]
                )
            ).all()


class TestPSF(object):
    class TestConstructors(object):
        def test__init__input_psf__all_attributes_correct_including_data_inheritance(
            self
        ):
            psf = al.PSF(array=np.ones((3, 3)), pixel_scale=1.0, renormalize=False)

            assert psf.shape == (3, 3)
            assert psf.pixel_scale == 1.0
            assert (psf == np.ones((3, 3))).all()
            assert psf.origin == (0.0, 0.0)

            psf = al.PSF(array=np.ones((4, 3)), pixel_scale=1.0, renormalize=False)

            assert (psf == np.ones((4, 3))).all()
            assert psf.pixel_scale == 1.0
            assert psf.shape == (4, 3)
            assert psf.origin == (0.0, 0.0)

        def test__from_fits__input_psf_3x3__all_attributes_correct_including_data_inheritance(
            self
        ):
            psf = al.PSF.from_fits_with_scale(
                file_path=test_data_dir + "3x3_ones.fits", hdu=0, pixel_scale=1.0
            )

            assert (psf == np.ones((3, 3))).all()
            assert psf.pixel_scale == 1.0
            assert psf.origin == (0.0, 0.0)

            psf = al.PSF.from_fits_with_scale(
                file_path=test_data_dir + "4x3_ones.fits", hdu=0, pixel_scale=1.0
            )

            assert (psf == np.ones((4, 3))).all()
            assert psf.pixel_scale == 1.0
            assert psf.origin == (0.0, 0.0)

    class TestRenormalize(object):
        def test__input_is_already_normalized__no_change(self):
            psf_data = np.ones((3, 3)) / 9.0

            psf = al.PSF(array=psf_data, pixel_scale=1.0, renormalize=True)

            assert psf == pytest.approx(psf_data, 1e-3)

        def test__input_is_above_normalization_so_is_normalized(self):
            psf_data = np.ones((3, 3))

            psf = al.PSF(array=psf_data, pixel_scale=1.0, renormalize=True)

            assert psf == pytest.approx(np.ones((3, 3)) / 9.0, 1e-3)

        def test__same_as_above__renomalized_false_does_not_renormalize(self):
            psf_data = np.ones((3, 3))

            psf = al.PSF(array=psf_data, pixel_scale=1.0, renormalize=False)

            assert psf == pytest.approx(np.ones((3, 3)), 1e-3)

    class TestBinnedUp(object):
        def test__psf_is_even_x_even__rescaled_to_odd_x_odd__no_use_of_dimension_trimming(
            self
        ):
            array_2d = np.ones((6, 6))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5, renormalize=True
            )
            assert psf.pixel_scale == 2.0
            assert psf == (1.0 / 9.0) * np.ones((3, 3))

            array_2d = np.ones((9, 9))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.333333333333333, renormalize=True
            )
            assert psf.pixel_scale == 3.0
            assert psf == (1.0 / 9.0) * np.ones((3, 3))

            array_2d = np.ones((18, 6))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5, renormalize=True
            )
            assert psf.pixel_scale == 2.0
            assert psf == (1.0 / 27.0) * np.ones((9, 3))

            array_2d = np.ones((6, 18))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5, renormalize=True
            )
            assert psf.pixel_scale == 2.0
            assert psf == (1.0 / 27.0) * np.ones((3, 9))

        def test__psf_is_even_x_even_after_binning_up__resized_to_odd_x_odd_with_shape_plus_one(
            self
        ):
            array_2d = np.ones((2, 2))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=2.0, renormalize=True
            )
            assert psf.pixel_scale == 0.4
            assert psf == (1.0 / 25.0) * np.ones((5, 5))

            array_2d = np.ones((40, 40))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.1, renormalize=True
            )
            assert psf.pixel_scale == 8.0
            assert psf == (1.0 / 25.0) * np.ones((5, 5))

            array_2d = np.ones((2, 4))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=2.0, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(0.4444444, 1.0e-4)
            assert psf == (1.0 / 45.0) * np.ones((5, 9))

            array_2d = np.ones((4, 2))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=2.0, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(0.4444444, 1.0e-4)
            assert psf == (1.0 / 45.0) * np.ones((9, 5))

        def test__psf_is_odd_and_even_after_binning_up__resized_to_odd_and_odd_with_shape_plus_one(
            self
        ):
            array_2d = np.ones((6, 4))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(2.0, 1.0e-4)
            assert psf == (1.0 / 9.0) * np.ones((3, 3))

            array_2d = np.ones((9, 12))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.33333333333, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(3.0, 1.0e-4)
            assert psf == (1.0 / 15.0) * np.ones((3, 5))

            array_2d = np.ones((4, 6))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.5, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(2.0, 1.0e-4)
            assert psf == (1.0 / 9.0) * np.ones((3, 3))

            array_2d = np.ones((12, 9))
            psf = al.PSF(array=array_2d, pixel_scale=1.0, renormalize=False)
            psf = psf.new_psf_with_rescaled_odd_dimensioned_array(
                rescale_factor=0.33333333333, renormalize=True
            )
            assert psf.pixel_scale == pytest.approx(3.0, 1.0e-4)
            assert psf == (1.0 / 15.0) * np.ones((5, 3))

    class TestNewRenormalizedPsf(object):
        def test__input_is_already_normalized__no_change(self):
            psf_data = np.ones((3, 3)) / 9.0

            psf = al.PSF(array=psf_data, pixel_scale=1.0, renormalize=False)

            psf_new = psf.new_psf_with_renormalized_array()

            assert psf_new == pytest.approx(psf_data, 1e-3)

        def test__input_is_above_normalization_so_is_normalized(self):
            psf_data = np.ones((3, 3))

            psf = al.PSF(array=psf_data, pixel_scale=1.0, renormalize=False)

            psf_new = psf.new_psf_with_renormalized_array()

            assert psf_new == pytest.approx(np.ones((3, 3)) / 9.0, 1e-3)

    class TestConvolve(object):
        def test__kernel_is_not_odd_x_odd__raises_error(self):
            kernel = np.array([[0.0, 1.0], [1.0, 2.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            with pytest.raises(exc.ConvolutionException):
                psf.convolve(np.ones((5, 5)))

        def test__image_is_3x3_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
            self
        ):
            image = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

            kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (blurred_image == kernel).all()

        def test__image_is_4x4_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
            self
        ):
            image = np.array(
                [
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                ]
            )

            kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [
                        [0.0, 1.0, 0.0, 0.0],
                        [1.0, 2.0, 1.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0],
                    ]
                )
            ).all()

        def test__image_is_4x3_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
            self
        ):
            image = np.array(
                [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
            )

            kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
                )
            ).all()

        def test__image_is_3x4_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
            self
        ):
            image = np.array(
                [[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
            )

            kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [[0.0, 1.0, 0.0, 0.0], [1.0, 2.0, 1.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
                )
            ).all()

        def test__image_is_4x4_has_two_central_values__kernel_is_asymmetric__blurred_image_follows_convolution(
            self
        ):
            image = np.array(
                [
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                ]
            )

            kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [
                        [1.0, 1.0, 1.0, 0.0],
                        [2.0, 3.0, 2.0, 1.0],
                        [1.0, 5.0, 5.0, 1.0],
                        [0.0, 1.0, 3.0, 3.0],
                    ]
                )
            ).all()

        def test__image_is_4x4_values_are_on_edge__kernel_is_asymmetric__blurring_does_not_account_for_edge_effects(
            self
        ):
            image = np.array(
                [
                    [0.0, 0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                    [0.0, 0.0, 0.0, 0.0],
                ]
            )

            kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [
                        [1.0, 1.0, 0.0, 0.0],
                        [2.0, 1.0, 1.0, 1.0],
                        [3.0, 3.0, 2.0, 2.0],
                        [0.0, 0.0, 1.0, 3.0],
                    ]
                )
            ).all()

        def test__image_is_4x4_values_are_on_corner__kernel_is_asymmetric__blurring_does_not_account_for_edge_effects(
            self
        ):
            image = np.array(
                [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )

            kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

            psf = al.PSF(array=kernel, pixel_scale=1.0)

            blurred_image = psf.convolve(image)

            assert (
                blurred_image
                == np.array(
                    [
                        [2.0, 1.0, 0.0, 0.0],
                        [3.0, 3.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 1.0],
                        [0.0, 0.0, 2.0, 2.0],
                    ]
                )
            ).all()

    class TestFromKernelNoBlurring(object):
        def test__correct_kernel(self):
            psf = al.PSF.from_no_blurring_kernel(pixel_scale=1.0)

            assert (
                psf == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
            ).all()
            assert psf.pixel_scale == 1.0

            psf = al.PSF.from_no_blurring_kernel(pixel_scale=2.0)

            assert (
                psf == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
            ).all()
            assert psf.pixel_scale == 2.0

    class TestFromGaussian(object):
        def test__identical_to_gaussian_light_profile(self):
            grid = al.Grid.from_shape_pixel_scale_and_sub_size(
                shape=(3, 3), pixel_scale=1.0, sub_size=1
            )

            gaussian = al.light_profiles.EllipticalGaussian(
                centre=(0.1, 0.1), axis_ratio=0.9, phi=45.0, intensity=1.0, sigma=1.0
            )
            profile_gaussian = gaussian.profile_image_from_grid(
                grid=grid, return_in_2d=True, return_binned=True, bypass_decorator=False
            )

            profile_psf = al.PSF(
                array=profile_gaussian, pixel_scale=1.0, renormalize=True
            )

            imaging_psf = al.PSF.from_gaussian(
                shape=(3, 3),
                pixel_scale=1.0,
                centre=(0.1, 0.1),
                axis_ratio=0.9,
                phi=45.0,
                sigma=1.0,
            )

            assert profile_psf == pytest.approx(imaging_psf, 1e-4)

    class TestFromAlmaGaussian(object):
        def test__identical_to_astropy_gaussian_model__circular_no_rotation(self):
            pixel_scale = 0.1

            x_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=2.0,
                y_mean=2.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=0.0,
            )

            shape = (5, 5)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=2.0e-5,
                theta=0.0,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)

        def test__identical_to_astropy_gaussian_model__circular_no_rotation_different_pixel_scale(
            self
        ):
            pixel_scale = 0.02

            x_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=2.0,
                y_mean=2.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=0.0,
            )

            shape = (5, 5)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=2.0e-5,
                theta=0.0,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)

        def test__identical_to_astropy_gaussian_model__include_ellipticity_from_x_and_y_stddev(
            self
        ):
            pixel_scale = 0.1

            x_stddev = (
                1.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            theta_deg = 0.0
            theta = Angle(theta_deg, "deg").radian

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=2.0,
                y_mean=2.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=theta,
            )

            shape = (5, 5)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=1.0e-5,
                theta=theta_deg,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)

        def test__identical_to_astropy_gaussian_model__include_different_ellipticity_from_x_and_y_stddev(
            self
        ):
            pixel_scale = 0.1

            x_stddev = (
                3.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            theta_deg = 0.0
            theta = Angle(theta_deg, "deg").radian

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=2.0,
                y_mean=2.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=theta,
            )

            shape = (5, 5)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=3.0e-5,
                theta=theta_deg,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)

        def test__identical_to_astropy_gaussian_model__include_rotation_angle_30(self):
            pixel_scale = 0.1

            x_stddev = (
                1.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            theta_deg = 30.0
            theta = Angle(theta_deg, "deg").radian

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=1.0,
                y_mean=1.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=theta,
            )

            shape = (3, 3)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=1.0e-5,
                theta=theta_deg,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)

        def test__identical_to_astropy_gaussian_model__include_rotation_angle_230(self):
            pixel_scale = 0.1

            x_stddev = (
                1.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )
            y_stddev = (
                2.0e-5
                * (units.deg).to(units.arcsec)
                / pixel_scale
                / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            )

            theta_deg = 230.0
            theta = Angle(theta_deg, "deg").radian

            gaussian_astropy = functional_models.Gaussian2D(
                amplitude=1.0,
                x_mean=1.0,
                y_mean=1.0,
                x_stddev=x_stddev,
                y_stddev=y_stddev,
                theta=theta,
            )

            shape = (3, 3)
            y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
            psf_astropy = gaussian_astropy(x, y)
            psf_astropy /= np.sum(psf_astropy)

            psf = al.PSF.from_as_gaussian_via_alma_fits_header_parameters(
                shape=shape,
                pixel_scale=pixel_scale,
                y_stddev=2.0e-5,
                x_stddev=1.0e-5,
                theta=theta_deg,
            )

            assert psf_astropy == pytest.approx(psf, 1e-4)


class TestSimulateImaging(object):
    def test__setup_image__correct_attributes(self):
        array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

        psf = al.PSF(array=3.0 * np.ones((3, 3)), pixel_scale=1.0)
        noise_map = 5.0 * np.ones((3, 3))

        imaging_data = al.SimulatedImagingData(
            image=array,
            pixel_scale=0.1,
            noise_map=noise_map,
            psf=psf,
            background_noise_map=7.0 * np.ones((3, 3)),
            poisson_noise_map=9.0 * np.ones((3, 3)),
            exposure_time_map=11.0 * np.ones((3, 3)),
        )

        assert imaging_data.image == pytest.approx(
            np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]), 1e-2
        )
        assert (imaging_data.psf == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 7.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 9.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 11.0 * np.ones((3, 3))).all()
        assert imaging_data.origin == (0.0, 0.0)

    def test__setup_with_all_features_off(self):
        image = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            pixel_scale=0.1,
            add_noise=False,
        )

        assert (imaging_data_simulated.exposure_time_map == np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1
        assert (
            imaging_data_simulated.image
            == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        ).all()
        assert imaging_data_simulated.origin == (0.0, 0.0)

    def test__setup_with_background_sky_on__noise_off__no_noise_in_image__noise_map_is_noise_value(
        self
    ):
        image = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        background_sky_map = al.ScaledSquarePixelArray.single_value(
            value=16.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            background_sky_map=background_sky_map,
            add_noise=False,
            noise_if_add_noise_false=0.2,
            noise_seed=1,
        )

        assert (imaging_data_simulated.exposure_time_map == 1.0 * np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1

        assert (
            imaging_data_simulated.image
            == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        ).all()
        assert imaging_data_simulated.noise_map == 0.2 * np.ones((3, 3))

        assert (imaging_data_simulated.background_noise_map == 4.0 * np.ones((3, 3))).all()

    def test__setup_with_background_sky_on__noise_on_so_background_adds_noise_to_image(
        self
    ):
        image = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        background_sky_map = al.ScaledSquarePixelArray.single_value(
            value=16.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            background_sky_map=background_sky_map,
            add_noise=True,
            noise_seed=1,
        )

        assert (imaging_data_simulated.exposure_time_map == 1.0 * np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1

        assert (
            imaging_data_simulated.image
            == np.array([[1.0, 5.0, 4.0], [1.0, 2.0, 1.0], [5.0, 2.0, 7.0]])
        ).all()

        assert (
            imaging_data_simulated.poisson_noise_map
            == np.array(
                [
                    [np.sqrt(1.0), np.sqrt(5.0), np.sqrt(4.0)],
                    [np.sqrt(1.0), np.sqrt(2.0), np.sqrt(1.0)],
                    [np.sqrt(5.0), np.sqrt(2.0), np.sqrt(7.0)],
                ]
            )
        ).all()

        assert (imaging_data_simulated.background_noise_map == 4.0 * np.ones((3, 3))).all()

    def test__setup_with_psf_blurring_on__blurs_image_and_trims_psf_edge_off(self):
        image = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        psf = al.PSF(
            array=np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]]),
            pixel_scale=1.0,
        )

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            psf=psf,
            add_noise=False,
        )

        assert (
            imaging_data_simulated.image
            == np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])
        ).all()
        assert (imaging_data_simulated.exposure_time_map == np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1

    def test__setup_with_background_sky_and_psf_on__psf_does_no_blurring__image_and_sky_both_trimmed(
        self
    ):
        image = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        psf = al.PSF(
            array=np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]),
            pixel_scale=1.0,
        )

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        background_sky_map = al.ScaledSquarePixelArray.single_value(
            value=16.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            psf=psf,
            background_sky_map=background_sky_map,
            add_noise=False,
            noise_seed=1,
        )

        assert (imaging_data_simulated.exposure_time_map == 1.0 * np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1

        assert (
            imaging_data_simulated.image
            == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        ).all()

        assert (imaging_data_simulated.background_noise_map == 4.0 * np.ones((3, 3))).all()

    def test__setup_with_noise(self):
        image = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=20.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=20.0,
            exposure_time_map=exposure_time_map,
            add_noise=True,
            noise_seed=1,
        )

        assert (imaging_data_simulated.exposure_time_map == 20.0 * np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1

        assert imaging_data_simulated.image == pytest.approx(
            np.array([[0.0, 0.0, 0.0], [0.0, 1.05, 0.0], [0.0, 0.0, 0.0]]), 1e-2
        )

        # Because of the value is 1.05, the estimated Poisson noise_map_1d is:
        # sqrt((1.05 * 20))/20 = 0.2291

        assert imaging_data_simulated.poisson_noise_map == pytest.approx(
            np.array([[0.0, 0.0, 0.0], [0.0, 0.2291, 0.0], [0.0, 0.0, 0.0]]), 1e-2
        )

        assert imaging_data_simulated.noise_map == pytest.approx(
            np.array([[0.0, 0.0, 0.0], [0.0, 0.2291, 0.0], [0.0, 0.0, 0.0]]), 1e-2
        )

    def test__setup_with__psf_blurring_and_poisson_noise_on__poisson_noise_added_to_blurred_image(
        self
    ):
        image = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        psf = al.PSF(
            array=np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]]),
            pixel_scale=1.0,
        )

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=20.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=20.0,
            exposure_time_map=exposure_time_map,
            psf=psf,
            add_noise=True,
            noise_seed=1,
        )

        assert (imaging_data_simulated.exposure_time_map == 20.0 * np.ones((3, 3))).all()
        assert imaging_data_simulated.pixel_scale == 0.1
        assert imaging_data_simulated.image == pytest.approx(
            np.array([[0.0, 1.05, 0.0], [1.3, 2.35, 1.05], [0.0, 1.05, 0.0]]), 1e-2
        )

        # The estimated Poisson noises are:
        # sqrt((2.35 * 20))/20 = 0.3427
        # sqrt((1.3 * 20))/20 = 0.2549
        # sqrt((1.05 * 20))/20 = 0.2291

        assert imaging_data_simulated.poisson_noise_map == pytest.approx(
            np.array(
                [[0.0, 0.2291, 0.0], [0.2549, 0.3427, 0.2291], [0.0, 0.2291, 0.0]]
            ),
            1e-2,
        )

    def test__simulate_function__turns_exposure_time_and_sky_level_to_arrays(self):
        image = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        psf = al.PSF(
            array=np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]),
            pixel_scale=1.0,
        )

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        background_sky_map = al.ScaledSquarePixelArray.single_value(
            value=16.0, pixel_scale=0.1, shape=image.shape
        )

        imaging_variable = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            exposure_time=1.0,
            exposure_time_map=exposure_time_map,
            psf=psf,
            background_sky_map=background_sky_map,
            pixel_scale=0.1,
            add_noise=False,
            noise_seed=1,
        )

        image = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=image,
            pixel_scale=0.1,
            exposure_time=1.0,
            background_sky_level=16.0,
            psf=psf,
            add_noise=False,
            noise_seed=1,
        )

        assert (
            imaging_variable.exposure_time_map == imaging_data_simulated.exposure_time_map
        ).all()
        assert imaging_variable.pixel_scale == imaging_data_simulated.pixel_scale
        assert imaging_variable.image == pytest.approx(imaging_data_simulated.image, 1e-4)
        assert (
            imaging_variable.background_noise_map == imaging_data_simulated.background_noise_map
        ).all()

    def test__noise_map_creates_nans_due_to_low_exposure_time__raises_error(self):
        image = np.ones((9, 9))

        psf = al.PSF.from_gaussian(shape=(3, 3), sigma=0.1, pixel_scale=0.2)

        exposure_time_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        background_sky_map = al.ScaledSquarePixelArray.single_value(
            value=1.0, pixel_scale=0.1, shape=image.shape
        )

        with pytest.raises(exc.DataException):
            al.SimulatedImagingData.from_image_and_exposure_arrays(
                image=image,
                psf=psf,
                pixel_scale=0.1,
                exposure_time=1.0,
                exposure_time_map=exposure_time_map,
                background_sky_map=background_sky_map,
                add_noise=True,
                noise_seed=1,
            )

    def test__from_deflections_and_galaxies__same_as_manual_calculation_using_tracer(
        self
    ):
        psf = al.PSF(
            array=np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]]),
            pixel_scale=1.0,
        )

        grid = al.Grid.from_shape_pixel_scale_and_sub_size(
            shape=(10, 10), pixel_scale=1.0, sub_size=1
        )

        g0 = al.Galaxy(
            redshift=0.5,
            mass_profile=al.mass_profiles.SphericalIsothermal(einstein_radius=1.0),
        )

        g1 = al.Galaxy(
            redshift=1.0, light=al.light_profiles.SphericalSersic(intensity=1.0)
        )

        tracer = al.Tracer.from_galaxies(galaxies=[g0, g1])

        deflections = tracer.deflections_from_grid(
            grid=grid, return_in_2d=True, return_binned=True,
        )

        imaging_data_simulated_via_deflections = al.SimulatedImagingData.from_deflections_galaxies_and_exposure_arrays(
            deflections=deflections,
            pixel_scale=1.0,
            galaxies=[g1],
            exposure_time=10000.0,
            background_sky_level=100.0,
            add_noise=True,
            noise_seed=1,
        )

        tracer_profile_image_plane_image = tracer.profile_image_from_grid(
            grid=grid, return_in_2d=True, return_binned=True,
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=tracer_profile_image_plane_image,
            pixel_scale=1.0,
            exposure_time=10000.0,
            background_sky_level=100.0,
            add_noise=True,
            noise_seed=1,
        )

        assert (
            imaging_data_simulated_via_deflections.image == imaging_data_simulated.image
        ).all()
        assert (imaging_data_simulated_via_deflections.psf == imaging_data_simulated.psf).all()
        assert (
            imaging_data_simulated_via_deflections.noise_map == imaging_data_simulated.noise_map
        ).all()
        assert (
            imaging_data_simulated_via_deflections.background_sky_map
            == imaging_data_simulated.background_sky_map
        ).all()
        assert (
            imaging_data_simulated_via_deflections.exposure_time_map
            == imaging_data_simulated.exposure_time_map
        ).all()

    def test__from_tracer__same_as_manual_tracer_input(self):
        psf = al.PSF(
            array=np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]]),
            pixel_scale=1.0,
        )

        grid = al.Grid.from_shape_pixel_scale_and_sub_size(
            shape=(20, 20), pixel_scale=0.05, sub_size=1
        )

        lens_galaxy = al.Galaxy(
            redshift=0.5,
            light=al.light_profiles.EllipticalSersic(intensity=1.0),
            mass=al.mass_profiles.EllipticalIsothermal(einstein_radius=1.6),
        )

        source_galaxy = al.Galaxy(
            redshift=1.0, light=al.light_profiles.EllipticalSersic(intensity=0.3)
        )

        tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

        imaging_data_simulated_via_tracer = al.SimulatedImagingData.from_tracer_grid_and_exposure_arrays(
            tracer=tracer,
            grid=grid,
            pixel_scale=0.1,
            exposure_time=10000.0,
            psf=psf,
            background_sky_level=100.0,
            add_noise=True,
            noise_seed=1,
        )

        imaging_data_simulated = al.SimulatedImagingData.from_image_and_exposure_arrays(
            image=tracer.padded_profile_image_2d_from_grid_and_psf_shape(
                grid=grid, psf_shape=(3, 3)
            ),
            pixel_scale=0.1,
            exposure_time=10000.0,
            psf=psf,
            background_sky_level=100.0,
            add_noise=True,
            noise_seed=1,
        )

        assert (imaging_data_simulated_via_tracer.image == imaging_data_simulated.image).all()
        assert (imaging_data_simulated_via_tracer.psf == imaging_data_simulated.psf).all()
        assert (
            imaging_data_simulated_via_tracer.noise_map == imaging_data_simulated.noise_map
        ).all()
        assert (
            imaging_data_simulated_via_tracer.background_sky_map
            == imaging_data_simulated.background_sky_map
        ).all()
        assert (
            imaging_data_simulated_via_tracer.exposure_time_map
            == imaging_data_simulated.exposure_time_map
        ).all()


class TestSimulatePoissonNoise(object):
    def test__input_image_all_0s__exposure_time_all_1s__all_noise_values_are_0s(self):
        image = np.zeros((2, 2))

        exposure_time = al.ScaledSquarePixelArray.single_value(
            1.0, image.shape, pixel_scale=0.1
        )
        simulated_poisson_image = image + al.generate_poisson_noise(
            image, exposure_time, seed=1
        )

        assert simulated_poisson_image.shape == (2, 2)
        assert (simulated_poisson_image == np.zeros((2, 2))).all()

    def test__input_image_includes_10s__exposure_time_is_1s__gives_noise_values_near_1_to_5(
        self
    ):
        image = np.array([[10.0, 0.0], [0.0, 10.0]])

        exposure_time = al.ScaledSquarePixelArray.single_value(
            1.0, image.shape, pixel_scale=0.1
        )
        poisson_noise_map = al.generate_poisson_noise(image, exposure_time, seed=1)
        simulated_poisson_image = image + poisson_noise_map

        assert simulated_poisson_image.shape == (2, 2)

        # Use known noise_map_1d map for given seed.
        assert (
            poisson_noise_map == np.array([[(10.0 - 9.0), 0], [0, (10.0 - 6.0)]])
        ).all()
        assert (simulated_poisson_image == np.array([[11, 0], [0, 14]])).all()

        assert (simulated_poisson_image - poisson_noise_map == image).all()

    def test__input_image_is_all_10s__exposure_time_is_1s__gives_noise_values_near_1_to_5(
        self
    ):
        image = np.array([[10.0, 10.0], [10.0, 10.0]])

        exposure_time = al.ScaledSquarePixelArray.single_value(
            1.0, image.shape, pixel_scale=0.1
        )
        poisson_noise_map = al.generate_poisson_noise(image, exposure_time, seed=1)
        simulated_poisson_image = image + poisson_noise_map

        assert simulated_poisson_image.shape == (2, 2)

        # Use known noise_map_1d map for given seed.
        assert (poisson_noise_map == np.array([[1, 4], [3, 1]])).all()

        assert (simulated_poisson_image == np.array([[11, 14], [13, 11]])).all()

        assert (simulated_poisson_image - poisson_noise_map == image).all()

    def test__input_image_has_1000000s__exposure_times_is_1s__these_give_positive_noise_values_near_1000(
        self
    ):
        image = np.array([[10000000.0, 0.0], [0.0, 10000000.0]])

        exposure_time = al.ScaledSquarePixelArray(
            array=np.ones((2, 2)), pixel_scale=0.1
        )

        poisson_noise_map = al.generate_poisson_noise(image, exposure_time, seed=2)

        simulated_poisson_image = image + poisson_noise_map

        assert simulated_poisson_image.shape == (2, 2)

        # Use known noise_map_1d map for given seed.
        assert (poisson_noise_map == np.array([[571, 0], [0, -441]])).all()

        assert (
            simulated_poisson_image
            == np.array([[10000000.0 + 571, 0.0], [0.0, 10000000.0 - 441]])
        ).all()

        assert (simulated_poisson_image - poisson_noise_map == image).all()

    def test__two_images_same_in_counts_but_different_in_electrons_per_sec__noise_related_by_exposure_times(
        self
    ):
        image_0 = np.array([[10.0, 0.0], [0.0, 10.0]])

        exposure_time_0 = al.ScaledSquarePixelArray(
            array=np.ones((2, 2)), pixel_scale=0.1
        )

        image_1 = np.array([[5.0, 0.0], [0.0, 5.0]])

        exposure_time_1 = al.ScaledSquarePixelArray(
            array=2.0 * np.ones((2, 2)), pixel_scale=0.1
        )

        simulated_poisson_image_0 = image_0 + al.generate_poisson_noise(
            image_0, exposure_time_0, seed=1
        )
        simulated_poisson_image_1 = image_1 + al.generate_poisson_noise(
            image_1, exposure_time_1, seed=1
        )

        assert (simulated_poisson_image_0 / 2.0 == simulated_poisson_image_1).all()

    def test__same_as_above_but_range_of_image_values_and_exposure_times(self):
        image_0 = np.array([[10.0, 20.0], [30.0, 40.0]])

        exposure_time_0 = al.ScaledSquarePixelArray(
            array=np.array([[2.0, 2.0], [3.0, 4.0]]), pixel_scale=0.1
        )

        image_1 = np.array([[20.0, 20.0], [45.0, 20.0]])

        exposure_time_1 = al.ScaledSquarePixelArray(
            array=np.array([[1.0, 2.0], [2.0, 8.0]]), pixel_scale=0.1
        )

        simulated_poisson_image_0 = image_0 + al.generate_poisson_noise(
            image_0, exposure_time_0, seed=1
        )
        simulated_poisson_image_1 = image_1 + al.generate_poisson_noise(
            image_1, exposure_time_1, seed=1
        )

        assert (
            simulated_poisson_image_0[0, 0] == simulated_poisson_image_1[0, 0] / 2.0
        ).all()
        assert simulated_poisson_image_0[0, 1] == simulated_poisson_image_1[0, 1]
        assert (
            simulated_poisson_image_0[1, 0] * 1.5
            == pytest.approx(simulated_poisson_image_1[1, 0], 1e-2)
        ).all()
        assert (
            simulated_poisson_image_0[1, 1] / 2.0 == simulated_poisson_image_1[1, 1]
        ).all()


class TestImagingFromFits(object):
    def test__no_settings_just_pass_fits(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            renormalize_psf=False,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert imaging_data.background_noise_map == None
        assert imaging_data.poisson_noise_map == None
        assert imaging_data.exposure_time_map == None
        assert imaging_data.background_sky_map == None

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1

    def test__optional_array_paths_included__loads_optional_array(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__all_files_in_one_fits__load_using_different_hdus(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_multiple_hdu.fits",
            image_hdu=0,
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_multiple_hdu.fits",
            psf_hdu=1,
            noise_map_path=test_data_dir + "3x3_multiple_hdu.fits",
            noise_map_hdu=2,
            background_noise_map_path=test_data_dir + "3x3_multiple_hdu.fits",
            background_noise_map_hdu=3,
            poisson_noise_map_path=test_data_dir + "3x3_multiple_hdu.fits",
            poisson_noise_map_hdu=4,
            exposure_time_map_path=test_data_dir + "3x3_multiple_hdu.fits",
            exposure_time_map_hdu=5,
            background_sky_map_path=test_data_dir + "3x3_multiple_hdu.fits",
            background_sky_map_hdu=6,
            renormalize_psf=False,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__exposure_time_included__creates_exposure_time_map_using_exposure_time(
        self
    ):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            noise_map_path=test_data_dir + "3x3_ones.fits",
            psf_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            exposure_time_map_from_single_value=3.0,
            renormalize_psf=False,
        )

        assert (imaging_data.exposure_time_map == 3.0 * np.ones((3, 3))).all()

    def test__exposure_time_map_from_inverse_noise_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            exposure_time_map_from_single_value=3.0,
            exposure_time_map_from_inverse_noise_map=True,
            renormalize_psf=False,
        )

        assert (imaging_data.exposure_time_map == 3.0 * np.ones((3, 3))).all()

        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            exposure_time_map_from_single_value=6.0,
            exposure_time_map_from_inverse_noise_map=True,
            renormalize_psf=False,
        )

        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()

    def test__exposure_time_map_from_inverse_noise_map__background_noise_is_converted_from_inverse_noise_map(
        self
    ):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_ones_central_two.fits",
            convert_background_noise_map_from_inverse_noise_map=True,
            exposure_time_map_from_single_value=3.0,
            exposure_time_map_from_inverse_noise_map=True,
            renormalize_psf=False,
        )

        inverse_noise_map = np.array(
            [[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]]
        )

        background_noise_map_converted = al.NoiseMap.from_inverse_noise_map(
            inverse_noise_map=inverse_noise_map, pixel_scale=0.1
        )

        assert (
            imaging_data.background_noise_map
            == np.array([[1.0, 1.0, 1.0], [1.0, 0.5, 1.0], [1.0, 1.0, 1.0]])
        ).all()
        assert (imaging_data.background_noise_map == background_noise_map_converted).all()

        assert (
            imaging_data.exposure_time_map
            == np.array([[1.5, 1.5, 1.5], [1.5, 3.0, 1.5], [1.5, 1.5, 1.5]])
        ).all()

    def test__pad_shape_of_image_arrays_and_psf(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            resized_imaging_shape=(5, 5),
            resized_psf_shape=(7, 7),
            renormalize_psf=False,
        )

        padded_array = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        psf_padded_array = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                [0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                [0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        assert (imaging_data.image == padded_array).all()
        assert (imaging_data.psf == psf_padded_array).all()
        assert (imaging_data.noise_map == 3.0 * padded_array).all()
        assert (imaging_data.background_noise_map == 4.0 * padded_array).all()
        assert (imaging_data.poisson_noise_map == 5.0 * padded_array).all()
        assert (imaging_data.exposure_time_map == 6.0 * padded_array).all()
        assert (imaging_data.background_sky_map == 7.0 * padded_array).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            exposure_time_map_from_single_value=3.0,
            pixel_scale=0.1,
            resized_imaging_shape=(5, 5),
            resized_psf_shape=(7, 7),
            renormalize_psf=False,
        )

        exposure_padded_array = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 3.0, 3.0, 3.0, 0.0],
                [0.0, 3.0, 3.0, 3.0, 0.0],
                [0.0, 3.0, 3.0, 3.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        assert (imaging_data.image == padded_array).all()
        assert (imaging_data.exposure_time_map == exposure_padded_array).all()

    def test__trim_shape_of_image_arrays_and_psf(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            resized_imaging_shape=(1, 1),
            resized_psf_shape=(1, 1),
            renormalize_psf=False,
        )

        trimmed_array = np.array([[1.0]])

        assert (imaging_data.image == trimmed_array).all()
        assert (imaging_data.psf == 2.0 * trimmed_array).all()
        assert (imaging_data.noise_map == 3.0 * trimmed_array).all()
        assert (imaging_data.background_noise_map == 4.0 * trimmed_array).all()
        assert (imaging_data.poisson_noise_map == 5.0 * trimmed_array).all()
        assert (imaging_data.exposure_time_map == 6.0 * trimmed_array).all()
        assert (imaging_data.background_sky_map == 7.0 * trimmed_array).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_noise_map_from_weight_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            convert_noise_map_from_weight_map=True,
            renormalize_psf=False,
        )

        noise_map_converted = al.NoiseMap.from_weight_map(
            weight_map=3.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == noise_map_converted).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_noise_map_from_inverse_noise_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            convert_noise_map_from_inverse_noise_map=True,
            renormalize_psf=False,
        )

        noise_map_converted = al.NoiseMap.from_inverse_noise_map(
            inverse_noise_map=3.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == noise_map_converted).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__noise_map_from_image_and_background_noise_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_from_image_and_background_noise_map=True,
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
        )

        noise_map_converted = al.NoiseMap.from_image_and_background_noise_map(
            pixel_scale=0.1,
            image=imaging_data.image,
            background_noise_map=imaging_data.background_noise_map,
            gain=2.0,
            exposure_time_map=imaging_data.exposure_time_map,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == noise_map_converted).all()
        assert imaging_data.noise_map == (np.sqrt((24.0) ** 2.0 + (6.0)) / (6.0)) * np.ones(
            (3, 3)
        )
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__noise_map_from_image_and_background_noise_map__include_convert_from_electrons(
        self
    ):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_from_image_and_background_noise_map=True,
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            convert_from_electrons=True,
            renormalize_psf=False,
        )

        noise_map_converted = al.NoiseMap.from_image_and_background_noise_map(
            pixel_scale=0.1,
            image=1.0 * np.ones((3, 3)),
            background_noise_map=4.0 * np.ones((3, 3)),
            gain=None,
            exposure_time_map=imaging_data.exposure_time_map,
            convert_from_electrons=True,
        )

        noise_map_converted = noise_map_converted / 6.0

        assert (imaging_data.image == np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == noise_map_converted).all()
        assert (imaging_data.noise_map == np.sqrt(17.0) * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__noise_map_from_image_and_background_noise_map__include_convert_from_adus(
        self
    ):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_from_image_and_background_noise_map=True,
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            gain=2.0,
            convert_from_adus=True,
            renormalize_psf=False,
        )

        noise_map_converted = al.NoiseMap.from_image_and_background_noise_map(
            pixel_scale=0.1,
            image=1.0 * np.ones((3, 3)),
            background_noise_map=4.0 * np.ones((3, 3)),
            gain=2.0,
            exposure_time_map=imaging_data.exposure_time_map,
            convert_from_adus=True,
        )

        noise_map_converted = 2.0 * noise_map_converted / 6.0

        assert (imaging_data.image == 2.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == noise_map_converted).all()
        assert (imaging_data.noise_map == np.sqrt(66.0) * np.ones((3, 3)) / 6.0).all()
        assert (
            imaging_data.background_noise_map == 2.0 * 4.0 * np.ones((3, 3)) / 6.0
        ).all()
        assert (imaging_data.poisson_noise_map == 2.0 * 5.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 2.0 * 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_background_noise_map_from_weight_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            convert_background_noise_map_from_weight_map=True,
        )

        background_noise_map_converted = al.NoiseMap.from_weight_map(
            weight_map=4.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == background_noise_map_converted).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_background_noise_map_from_inverse_noise_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            convert_background_noise_map_from_inverse_noise_map=True,
        )

        background_noise_map_converted = al.NoiseMap.from_inverse_noise_map(
            inverse_noise_map=4.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == background_noise_map_converted).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__poisson_noise_map_from_image(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            poisson_noise_map_from_image=True,
        )

        poisson_noise_map_converted = al.PoissonNoiseMap.from_image_and_exposure_time_map(
            pixel_scale=0.1,
            image=np.ones((3, 3)),
            exposure_time_map=imaging_data.exposure_time_map,
            gain=None,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert imaging_data.poisson_noise_map == (np.sqrt(6.0) / (6.0)) * np.ones((3, 3))
        assert (imaging_data.poisson_noise_map == poisson_noise_map_converted).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__poisson_noise_map_from_image__include_convert_from_electrons(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            poisson_noise_map_from_image=True,
            convert_from_electrons=True,
        )

        poisson_noise_map_counts = al.PoissonNoiseMap.from_image_and_exposure_time_map(
            pixel_scale=0.1,
            image=np.ones((3, 3)),
            exposure_time_map=imaging_data.exposure_time_map,
            gain=None,
            convert_from_electrons=True,
        )

        poisson_noise_map_converted = poisson_noise_map_counts / 6.0

        assert (imaging_data.image == np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3)) / 6.0).all()
        assert imaging_data.poisson_noise_map == np.ones((3, 3)) / 6.0
        assert (imaging_data.poisson_noise_map == poisson_noise_map_converted).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__poisson_noise_map_from_image__include_convert_from_adus(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            poisson_noise_map_from_image=True,
            gain=2.0,
            convert_from_adus=True,
        )

        poisson_noise_map_counts = al.PoissonNoiseMap.from_image_and_exposure_time_map(
            pixel_scale=0.1,
            image=np.ones((3, 3)),
            exposure_time_map=imaging_data.exposure_time_map,
            gain=2.0,
            convert_from_adus=True,
        )

        poisson_noise_map_converted = 2.0 * poisson_noise_map_counts / 6.0

        assert (imaging_data.image == 2.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 2.0 * 3.0 * np.ones((3, 3)) / 6.0).all()
        assert (
            imaging_data.background_noise_map == 2.0 * 4.0 * np.ones((3, 3)) / 6.0
        ).all()
        assert imaging_data.poisson_noise_map == np.sqrt(2.0 * np.ones((3, 3))) / 6.0
        assert (imaging_data.poisson_noise_map == poisson_noise_map_converted).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 2.0 * 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_poisson_noise_map_from_weight_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            convert_poisson_noise_map_from_weight_map=True,
        )

        poisson_noise_map_converted = al.NoiseMap.from_weight_map(
            weight_map=5.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == poisson_noise_map_converted).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_poisson_noise_map_from_inverse_noise_map(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            convert_poisson_noise_map_from_inverse_noise_map=True,
        )

        poisson_noise_map_converted = al.NoiseMap.from_inverse_noise_map(
            inverse_noise_map=5.0 * np.ones((3, 3)), pixel_scale=0.1
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == poisson_noise_map_converted).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__psf_renormalized_true__renormalized_psf(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=True,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert imaging_data.psf == pytest.approx((1.0 / 9.0) * np.ones((3, 3)), 1e-2)
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_image_from_electrons_using_exposure_time(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            convert_from_electrons=True,
        )

        assert (imaging_data.image == np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__convert_image_from_adus_using_exposure_time_and_gain(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
            gain=2.0,
            convert_from_adus=True,
        )

        assert (imaging_data.image == 2.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 2.0 * 3.0 * np.ones((3, 3)) / 6.0).all()
        assert (
            imaging_data.background_noise_map == 2.0 * 4.0 * np.ones((3, 3)) / 6.0
        ).all()
        assert (imaging_data.poisson_noise_map == 2.0 * 5.0 * np.ones((3, 3)) / 6.0).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 2.0 * 7.0 * np.ones((3, 3)) / 6.0).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1

    def test__no_noise_map_input__raises_imaging_exception(self):
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                psf_path=test_data_dir + "3x3_twos.fits",
            )

    def test__multiple_noise_map_options__raises_imaging_exception(self):
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                psf_path=test_data_dir + "3x3_twos.fits",
                noise_map_path=test_data_dir + "3x3_threes.fits",
                convert_noise_map_from_inverse_noise_map=True,
                convert_noise_map_from_weight_map=True,
            )

        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                psf_path=test_data_dir + "3x3_twos.fits",
                noise_map_path=test_data_dir + "3x3_threes.fits",
                convert_noise_map_from_inverse_noise_map=True,
                noise_map_from_image_and_background_noise_map=True,
            )

        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                psf_path=test_data_dir + "3x3_twos.fits",
                noise_map_path=test_data_dir + "3x3_threes.fits",
                noise_map_from_image_and_background_noise_map=True,
                convert_noise_map_from_weight_map=True,
            )

    def test__exposure_time_and_exposure_time_map_included__raies_imaging_error(self):
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                psf_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                noise_map_path=test_data_dir + "3x3_threes.fits",
                exposure_time_map_path=test_data_dir + "3x3_ones.fits",
                exposure_time_map_from_single_value=1.0,
            )

    def test__noise_map_from_image_and_background_noise_map_exceptions(self):
        # need background noise_map map - raise error if not present
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                psf_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                noise_map_path=test_data_dir + "3x3_threes.fits",
                exposure_time_map_from_single_value=1.0,
                noise_map_from_image_and_background_noise_map=True,
            )

        # Dont need gain if datas is in electrons
        al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            psf_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            exposure_time_map_from_single_value=1.0,
            noise_map_from_image_and_background_noise_map=True,
            convert_from_electrons=True,
        )

        # Need gain if datas is in adus
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                psf_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                noise_map_path=test_data_dir + "3x3_threes.fits",
                background_noise_map_path=test_data_dir + "3x3_fours.fits",
                noise_map_from_image_and_background_noise_map=True,
                convert_from_adus=True,
            )

        # No error if datas already in adus
        al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            psf_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            exposure_time_map_from_single_value=1.0,
            noise_map_from_image_and_background_noise_map=True,
            gain=1.0,
            convert_from_adus=True,
        )

    def test__poisson_noise_map_from_image_exceptions(self):
        # Dont need gain if datas is in e/s
        al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            psf_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            noise_map_path=test_data_dir + "3x3_threes.fits",
            exposure_time_map_from_single_value=1.0,
            poisson_noise_map_from_image=True,
        )

        # No exposure time - not load
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                psf_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                poisson_noise_map_from_image=True,
                convert_from_electrons=True,
            )

        # Need gain if datas in adus
        with pytest.raises(exc.DataException):
            al.load_imaging_data_from_fits(
                image_path=test_data_dir + "3x3_ones.fits",
                psf_path=test_data_dir + "3x3_ones.fits",
                pixel_scale=0.1,
                noise_map_path=test_data_dir + "3x3_threes.fits",
                background_noise_map_path=test_data_dir + "3x3_fours.fits",
                exposure_time_map_from_single_value=1.0,
                poisson_noise_map_from_image=True,
                convert_from_adus=True,
            )

    def test__output_all_arrays(self):
        imaging_data = al.load_imaging_data_from_fits(
            image_path=test_data_dir + "3x3_ones.fits",
            pixel_scale=0.1,
            psf_path=test_data_dir + "3x3_twos.fits",
            noise_map_path=test_data_dir + "3x3_threes.fits",
            background_noise_map_path=test_data_dir + "3x3_fours.fits",
            poisson_noise_map_path=test_data_dir + "3x3_fives.fits",
            exposure_time_map_path=test_data_dir + "3x3_sixes.fits",
            background_sky_map_path=test_data_dir + "3x3_sevens.fits",
            renormalize_psf=False,
        )

        output_data_dir = "{}/../test_files/array/output_test/".format(
            os.path.dirname(os.path.realpath(__file__))
        )
        if os.path.exists(output_data_dir):
            shutil.rmtree(output_data_dir)

        os.makedirs(output_data_dir)

        al.output_imaging_data_to_fits(
            imaging_data=imaging_data,
            image_path=output_data_dir + "image.fits",
            psf_path=output_data_dir + "psf.fits",
            noise_map_path=output_data_dir + "noise_map.fits",
            background_noise_map_path=output_data_dir + "background_noise_map.fits",
            poisson_noise_map_path=output_data_dir + "poisson_noise_map.fits",
            exposure_time_map_path=output_data_dir + "exposure_time_map.fits",
            background_sky_map_path=output_data_dir + "background_sky_map.fits",
        )

        imaging_data = al.load_imaging_data_from_fits(
            image_path=output_data_dir + "image.fits",
            pixel_scale=0.1,
            psf_path=output_data_dir + "psf.fits",
            noise_map_path=output_data_dir + "noise_map.fits",
            background_noise_map_path=output_data_dir + "background_noise_map.fits",
            poisson_noise_map_path=output_data_dir + "poisson_noise_map.fits",
            exposure_time_map_path=output_data_dir + "exposure_time_map.fits",
            background_sky_map_path=output_data_dir + "background_sky_map.fits",
            renormalize_psf=False,
        )

        assert (imaging_data.image == np.ones((3, 3))).all()
        assert (imaging_data.psf == 2.0 * np.ones((3, 3))).all()
        assert (imaging_data.noise_map == 3.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_noise_map == 4.0 * np.ones((3, 3))).all()
        assert (imaging_data.poisson_noise_map == 5.0 * np.ones((3, 3))).all()
        assert (imaging_data.exposure_time_map == 6.0 * np.ones((3, 3))).all()
        assert (imaging_data.background_sky_map == 7.0 * np.ones((3, 3))).all()

        assert imaging_data.pixel_scale == 0.1
        assert imaging_data.psf.pixel_scale == 0.1
        assert imaging_data.noise_map.pixel_scale == 0.1
        assert imaging_data.background_noise_map.pixel_scale == 0.1
        assert imaging_data.poisson_noise_map.pixel_scale == 0.1
        assert imaging_data.exposure_time_map.pixel_scale == 0.1
        assert imaging_data.background_sky_map.pixel_scale == 0.1