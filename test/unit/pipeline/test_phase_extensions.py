import numpy as np
import pytest
from astropy import cosmology as cosmo

import autofit as af
from autolens.lens import lens_fit
from autolens.lens import ray_tracing as rt
from autolens.model.galaxy import galaxy as g
from autolens.model.galaxy import galaxy_model as gm
from autolens.model.hyper import hyper_data as hd
from autolens.model.inversion import pixelizations as px
from autolens.model.inversion import regularization as rg
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.pipeline.phase import phase_extensions
from autolens.pipeline.phase import phase_imaging
from test.unit.mock.pipeline import mock_pipeline


@pytest.fixture(name="lens_galaxy")
def make_lens_galaxy():
    return g.Galaxy(redshift=1.0, light=lp.SphericalSersic(),
                    mass=mp.SphericalIsothermal())


@pytest.fixture(name="source_galaxy")
def make_source_galaxy():
    return g.Galaxy(redshift=2.0, light=lp.SphericalSersic())


@pytest.fixture(name="lens_galaxies")
def make_lens_galaxies(lens_galaxy):
    lens_galaxies = af.ModelInstance()
    lens_galaxies.lens = lens_galaxy
    return lens_galaxies


@pytest.fixture(name="all_galaxies")
def make_all_galaxies(lens_galaxy, source_galaxy):
    galaxies = af.ModelInstance()
    galaxies.lens = lens_galaxy
    galaxies.source = source_galaxy
    return galaxies


@pytest.fixture(name="lens_instance")
def make_lens_instance(lens_galaxies):
    instance = af.ModelInstance()
    instance.lens_galaxies = lens_galaxies
    return instance


@pytest.fixture(name="lens_result")
def make_lens_result(lens_data_7x7, lens_instance):
    return phase_imaging.LensPlanePhase.Result(
        constant=lens_instance, figure_of_merit=1.0, previous_variable=af.ModelMapper(),
        gaussian_tuples=None,
        analysis=phase_imaging.LensPlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=cosmo.Planck15, positions_threshold=1.0),
        optimizer=None)


@pytest.fixture(name="lens_source_instance")
def make_lens_source_instance(lens_galaxy, source_galaxy):
    source_galaxies = af.ModelInstance()
    lens_galaxies = af.ModelInstance()
    source_galaxies.source = source_galaxy
    lens_galaxies.lens = lens_galaxy

    instance = af.ModelInstance()
    instance.source_galaxies = source_galaxies
    instance.lens_galaxies = lens_galaxies
    return instance


@pytest.fixture(name="lens_source_result")
def make_lens_source_result(lens_data_7x7, lens_source_instance):
    return phase_imaging.LensSourcePlanePhase.Result(
        constant=lens_source_instance, figure_of_merit=1.0,
        previous_variable=af.ModelMapper(), gaussian_tuples=None,
        analysis=phase_imaging.LensSourcePlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=cosmo.Planck15, positions_threshold=1.0),
        optimizer=None)


@pytest.fixture(name="multi_plane_instance")
def make_multi_plane_instance(all_galaxies):
    instance = af.ModelInstance()
    instance.galaxies = all_galaxies
    return instance


@pytest.fixture(name="multi_plane_result")
def make_multi_plane_result(lens_data_7x7, multi_plane_instance):
    return phase_imaging.MultiPlanePhase.Result(
        constant=multi_plane_instance, figure_of_merit=1.0,
        previous_variable=af.ModelMapper(), gaussian_tuples=None,
        analysis=phase_imaging.MultiPlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=cosmo.Planck15, positions_threshold=1.0),
        optimizer=None)


class MostLikelyFit(object):
    def __init__(self, model_image_2d):
        self.model_image_2d = model_image_2d


class MockResult(object):
    def __init__(self, most_likely_fit=None):
        self.most_likely_fit = most_likely_fit
        self.analysis = MockAnalysis()
        self.path_galaxy_tuples = []
        self.variable = af.ModelMapper()


class MockAnalysis(object):
    pass


class MockOptimizer(af.NonLinearOptimizer):
    def __init__(self, phase_name="mock_optimizer", phase_tag="tag", phase_folders=tuple(),
                 model_mapper=None):
        super().__init__(phase_folders=phase_folders, phase_tag=phase_tag,
                         phase_name=phase_name,
                         model_mapper=model_mapper)

    def fit(self, analysis):
        # noinspection PyTypeChecker
        return af.Result(
            None,
            analysis.fit(None),
            None
        )


class MockPhase(object):

    def __init__(self):
        self.phase_name = "phase name"
        self.phase_path = "phase_path"
        self.optimizer = MockOptimizer()
        self.phase_folders = ['']

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def run(self, *args, **kwargs):
        return MockResult()


class TestVariableFixing(object):
    def test_defaults_both(self):
        # noinspection PyTypeChecker
        phase = phase_extensions.InversionBackgroundBothPhase(
            MockPhase()
        )
        mapper = af.ModelMapper()
        mapper.hyper_image_sky = hd.HyperImageSky

        prior_model = mapper.hyper_image_sky

        phase.add_defaults(mapper)

        assert isinstance(mapper.hyper_image_sky, af.PriorModel)
        assert isinstance(mapper.hyper_noise_background, af.PriorModel)

        assert mapper.hyper_image_sky.cls == hd.HyperImageSky
        assert mapper.hyper_noise_background.cls == hd.HyperNoiseBackground

        assert mapper.hyper_image_sky is prior_model

    def test_defaults_hyper_image_sky(self):
        # noinspection PyTypeChecker
        phase = phase_extensions.InversionBackgroundSkyPhase(
            MockPhase()
        )

        mapper = af.ModelMapper()
        phase.add_defaults(mapper)

        assert isinstance(mapper.hyper_image_sky, af.PriorModel)
        assert mapper.hyper_image_sky.cls == hd.HyperImageSky

    def test_defaults_background_noise(self):
        # noinspection PyTypeChecker
        phase = phase_extensions.InversionBackgroundNoisePhase(
            MockPhase()
        )

        mapper = af.ModelMapper()
        phase.add_defaults(mapper)

        assert isinstance(mapper.hyper_noise_background, af.PriorModel)
        assert mapper.hyper_noise_background.cls == hd.HyperNoiseBackground

    def test_make_pixelization_variable(self):
        instance = af.ModelInstance()
        mapper = af.ModelMapper()

        mapper.lens_galaxy = gm.GalaxyModel(
            redshift=g.Redshift,
            pixelization=px.Rectangular,
            regularization=rg.Constant
        )
        mapper.source_galaxy = gm.GalaxyModel(
            redshift=g.Redshift,
            light=lp.EllipticalLightProfile
        )

        assert mapper.prior_count == 9

        instance.lens_galaxy = g.Galaxy(
            pixelization=px.Rectangular(),
            regularization=rg.Constant(),
            redshift=1.0
        )
        instance.source_galaxy = g.Galaxy(
            redshift=1.0,
            light=lp.EllipticalLightProfile()
        )

        # noinspection PyTypeChecker
        phase = phase_extensions.VariableFixingHyperPhase(
            MockPhase(),
            "mock_phase",
            variable_classes=(
                px.Pixelization,
                rg.Regularization
            )
        )

        phase.transfer_classes(
            instance,
            mapper
        )

        assert mapper.prior_count == 3
        assert mapper.lens_galaxy.redshift == 1.0
        assert mapper.source_galaxy.light.axis_ratio == 1.0


class TestImagePassing(object):

    def test_path_galaxy_tuples(
            self, lens_result, lens_galaxy):
        assert lens_result.path_galaxy_tuples == [
            (("lens_galaxies", "lens"), lens_galaxy)]

    def test_lens_source_galaxy_dict(
            self, lens_source_result, lens_galaxy, source_galaxy):
        assert lens_source_result.path_galaxy_tuples == [
            (("source_galaxies", "source"), source_galaxy),
            (("lens_galaxies", "lens"), lens_galaxy)
        ]

    def test_multi_plane_galaxy_dict(
            self, multi_plane_result, lens_galaxy, source_galaxy):
        assert multi_plane_result.path_galaxy_tuples == [
            (("galaxies", "lens"), lens_galaxy),
            (("galaxies", "source"), source_galaxy)
        ]

    def test_lens_image_dict_2d_and_1d(
            self, lens_result, mask_7x7):
        image_2d_dict = lens_result.image_2d_dict

        assert isinstance(image_2d_dict[("lens_galaxies", "lens")], np.ndarray)
        assert image_2d_dict[("lens_galaxies", "lens")].shape == (7, 7)

        image_1d_dict = lens_result.image_1d_dict_from_mask(mask=mask_7x7)
        assert image_1d_dict[("lens_galaxies", "lens")].shape == (9,)

    def test_lens_source_image_dict(
            self, lens_source_result, mask_7x7):
        image_2d_dict = lens_source_result.image_2d_dict

        assert isinstance(image_2d_dict[("lens_galaxies", "lens")], np.ndarray)
        assert isinstance(image_2d_dict[("source_galaxies", "source")], np.ndarray)

        assert image_2d_dict[("lens_galaxies", "lens")].shape == (7, 7)
        assert image_2d_dict[("source_galaxies", "source")].shape == (7, 7)

        image_1d_dict = lens_source_result.image_1d_dict_from_mask(mask=mask_7x7)

        assert image_1d_dict[("lens_galaxies", "lens")].shape == (9,)
        assert image_1d_dict[("source_galaxies", "source")].shape == (9,)

        lens_source_result.constant.lens_galaxies.lens = g.Galaxy(redshift=0.5)
        lens_source_result.constant.source_galaxies.source = g.Galaxy(redshift=1.0)

    def test_multi_plane_image_dict(
            self, multi_plane_result):
        image_dict = multi_plane_result.image_2d_dict
        assert isinstance(image_dict[("galaxies", "lens")], np.ndarray)
        assert isinstance(image_dict[("galaxies", "source")], np.ndarray)

        multi_plane_result.constant.galaxies.lens = g.Galaxy(redshift=0.5)

        image_dict = multi_plane_result.image_2d_dict
        assert (image_dict[("galaxies", "lens")] == np.zeros((7, 7))).all()
        assert isinstance(image_dict[("galaxies", "source")], np.ndarray)

    def test_galaxy_image_dict(
            self, lens_galaxy, source_galaxy, grid_stack_7x7, convolver_image_7x7):
        tracer = rt.TracerImageSourcePlanes([lens_galaxy], [source_galaxy],
                                            grid_stack_7x7)

        assert len(tracer.galaxy_image_dict_from_convolver_image(
            convolver_image=convolver_image_7x7)) == 2
        assert lens_galaxy in tracer.galaxy_image_dict_from_convolver_image(
            convolver_image=convolver_image_7x7)
        assert source_galaxy in tracer.galaxy_image_dict_from_convolver_image(
            convolver_image=convolver_image_7x7)

    def test__results_are_passed_to_new_analysis__sets_up_hyper_images(
            self, mask_function_7x7, results_collection_7x7, ccd_data_7x7):
        results_collection_7x7[0].galaxy_images = [2.0 * np.ones((7, 7)),
                                                   2.0 * np.ones((7, 7))]
        results_collection_7x7[0].galaxy_images[0][3, 2] = -1.0
        results_collection_7x7[0].galaxy_images[1][3, 4] = -1.0

        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy)),
            optimizer_class=mock_pipeline.MockNLO,
            mask_function=mask_function_7x7,
            phase_name='test_phase')

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_galaxy_image_1d_path_dict[('g0',)] == np.array(
            [2.0, 2.0, 2.0, 0.02, 2.0, 2.0, 2.0, 2.0, 2.0])).all()

        assert (analysis.hyper_galaxy_image_1d_path_dict[('g1',)] == np.array(
            [2.0, 2.0, 2.0, 2.0, 2.0, 0.02, 2.0, 2.0, 2.0])).all()

        assert (analysis.hyper_model_image_1d == np.array(
            [4.0, 4.0, 4.0, 2.02, 4.0, 2.02, 4.0, 4.0, 4.0])).all()

    def test__results_are_passed_to_new_analysis__hyper_images_values_below_minimum_are_scaled_up_using_config(
            self, mask_function_7x7, results_collection_7x7, ccd_data_7x7):
        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy)),
            optimizer_class=mock_pipeline.MockNLO,
            mask_function=mask_function_7x7,
            phase_name='test_phase')

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_model_image_1d == 5.0 * np.ones(9)).all()

        assert (analysis.hyper_galaxy_image_1d_path_dict[('g0',)] == 2.0 * np.ones(
            9)).all()
        assert (analysis.hyper_galaxy_image_1d_path_dict[('g1',)] == 3.0 * np.ones(
            9)).all()

    def test__results_are_passed_to_new_analysis__sets_up_hyper_cluster_images__includes_hyper_minimum(
            self, mask_function_7x7, results_collection_7x7, ccd_data_7x7):
        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            phase_name='test_phase',
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy,
                    pixelization=px.VoronoiBrightnessImage,
                    regularization=rg.Constant)),
            mask_function=mask_function_7x7,
            inversion_pixel_limit=5,
            cluster_pixel_scale=None,
            optimizer_class=mock_pipeline.MockNLO)

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[
                    ('g0',)] == 2.0 * np.ones(9)).all()
        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[
                    ('g1',)] == 3.0 * np.ones(9)).all()

        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy,
                    pixelization=px.VoronoiBrightnessImage,
                    regularization=rg.Constant)),
            inversion_pixel_limit=1,
            optimizer_class=mock_pipeline.MockNLO, mask_function=mask_function_7x7,
            cluster_pixel_scale=ccd_data_7x7.pixel_scale, phase_name='test_phase')

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[
                    ('g0',)] == 2.0 * np.ones(9)).all()
        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[
                    ('g1',)] == 3.0 * np.ones(9)).all()
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g0',)]) ==
                analysis.lens_data.cluster.shape[0])
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g1',)]) ==
                analysis.lens_data.cluster.shape[0])

        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy,
                    pixelization=px.VoronoiBrightnessImage,
                    regularization=rg.Constant)),
            inversion_pixel_limit=1,
            optimizer_class=mock_pipeline.MockNLO, mask_function=mask_function_7x7,
            cluster_pixel_scale=ccd_data_7x7.pixel_scale * 2.0, phase_name='test_phase')

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[('g0',)] == np.array(
            [0.5, 1.0, 1.0, 2.0])).all()
        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[('g1',)] == np.array(
            [0.75, 1.5, 1.5, 3.0])).all()
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g0',)]) ==
                analysis.lens_data.cluster.shape[0])
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g1',)]) ==
                analysis.lens_data.cluster.shape[0])

        results_collection_7x7[0].galaxy_images = [2.0 * np.ones((7, 7)),
                                                   2.0 * np.ones((7, 7))]
        results_collection_7x7[0].galaxy_images[0][3, 2] = -1.0
        results_collection_7x7[0].galaxy_images[1][3, 4] = -1.0

        phase_7x7 = phase_imaging.LensSourcePlanePhase(
            lens_galaxies=dict(
                lens=gm.GalaxyModel(
                    redshift=0.5,
                    hyper_galaxy=g.HyperGalaxy,
                    pixelization=px.VoronoiBrightnessImage,
                    regularization=rg.Constant)),
            inversion_pixel_limit=1,
            optimizer_class=mock_pipeline.MockNLO, mask_function=mask_function_7x7,
            cluster_pixel_scale=ccd_data_7x7.pixel_scale * 2.0, phase_name='test_phase')

        analysis = phase_7x7.make_analysis(data=ccd_data_7x7,
                                           results=results_collection_7x7)

        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[('g0',)] == np.array(
            [2.0, 2.0, 1.25, 2.0])).all()
        assert (analysis.hyper_galaxy_cluster_image_1d_path_dict[('g1',)] == np.array(
            [2.0, 2.0, 2.0, 1.25])).all()
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g0',)]) ==
                analysis.lens_data.cluster.shape[0])
        assert (len(analysis.hyper_galaxy_cluster_image_1d_path_dict[('g1',)]) ==
                analysis.lens_data.cluster.shape[0])

    def test_associate_images_lens(
            self, lens_instance, lens_result, lens_data_7x7):
        results_collection = af.ResultsCollection()
        results_collection.add("phase", lens_result)

        analysis = phase_imaging.LensPlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=None, positions_threshold=None,
            results=results_collection)

        instance = analysis.associate_images(instance=lens_instance)

        hyper_model_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=lens_result.image_2d_dict[("lens_galaxies", "lens")])

        assert instance.lens_galaxies.lens.hyper_model_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)
        assert instance.lens_galaxies.lens.hyper_galaxy_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)

    def test_associate_images_lens_source(
            self, lens_source_instance, lens_source_result, lens_data_7x7):
        results_collection = af.ResultsCollection()
        results_collection.add("phase", lens_source_result)
        analysis = phase_imaging.LensSourcePlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=None, positions_threshold=None,
            results=results_collection)

        instance = analysis.associate_images(lens_source_instance)

        hyper_lens_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=lens_source_result.image_2d_dict[("lens_galaxies", "lens")])
        hyper_source_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=lens_source_result.image_2d_dict[("source_galaxies", "source")])

        hyper_model_image_1d = hyper_lens_image_1d + hyper_source_image_1d

        assert instance.lens_galaxies.lens.hyper_model_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)
        assert instance.source_galaxies.source.hyper_model_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)

        assert instance.lens_galaxies.lens.hyper_galaxy_image_1d == pytest.approx(
            hyper_lens_image_1d, 1.0e-4)
        assert instance.source_galaxies.source.hyper_galaxy_image_1d == pytest.approx(
            hyper_source_image_1d, 1.04e-4)

    def test_associate_images_multi_plane(
            self, multi_plane_instance, multi_plane_result, lens_data_7x7):
        results_collection = af.ResultsCollection()
        results_collection.add("phase", multi_plane_result)
        analysis = phase_imaging.MultiPlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=None, positions_threshold=None,
            results=results_collection)

        instance = analysis.associate_images(instance=multi_plane_instance)

        hyper_lens_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=multi_plane_result.image_2d_dict[("galaxies", "lens")])
        hyper_source_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=multi_plane_result.image_2d_dict[("galaxies", "source")])

        hyper_model_image_1d = hyper_lens_image_1d + hyper_source_image_1d

        assert instance.galaxies.lens.hyper_galaxy_image_1d == pytest.approx(
            hyper_lens_image_1d, 1.0e-4)
        assert instance.galaxies.source.hyper_galaxy_image_1d == pytest.approx(
            hyper_source_image_1d, 1.0e-4)

        assert instance.galaxies.lens.hyper_model_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)
        assert instance.galaxies.source.hyper_model_image_1d == pytest.approx(
            hyper_model_image_1d, 1.0e-4)

    def test_fit_uses_hyper_fit_correctly_multi_plane(
            self, multi_plane_instance, multi_plane_result, lens_data_7x7):
        results_collection = af.ResultsCollection()
        results_collection.add("phase", multi_plane_result)
        analysis = phase_imaging.MultiPlanePhase.Analysis(
            lens_data=lens_data_7x7, cosmology=cosmo.Planck15, positions_threshold=None,
            results=results_collection)

        hyper_galaxy = g.HyperGalaxy(contribution_factor=1.0, noise_factor=1.0,
                                     noise_power=1.0)

        multi_plane_instance.galaxies.lens.hyper_galaxy = hyper_galaxy

        fit_figure_of_merit = analysis.fit(instance=multi_plane_instance)

        hyper_lens_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=multi_plane_result.image_2d_dict[("galaxies", "lens")])
        hyper_source_image_1d = lens_data_7x7.array_1d_from_array_2d(
            array_2d=multi_plane_result.image_2d_dict[("galaxies", "source")])

        hyper_model_image_1d = hyper_lens_image_1d + hyper_source_image_1d

        g0 = g.Galaxy(redshift=0.5,
                      light_profile=multi_plane_instance.galaxies.lens.light,
                      mass_profile=multi_plane_instance.galaxies.lens.mass,
                      hyper_galaxy=hyper_galaxy,
                      hyper_model_image_1d=hyper_model_image_1d,
                      hyper_galaxy_image_1d=hyper_lens_image_1d,
                      hyper_minimum_value=0.0)
        g1 = g.Galaxy(redshift=1.0,
                      light_profile=multi_plane_instance.galaxies.source.light)

        tracer = rt.TracerImageSourcePlanes(
            lens_galaxies=[g0],
            source_galaxies=[g1],
            image_plane_grid_stack=lens_data_7x7.grid_stack
        )

        fit = lens_fit.LensDataFit.for_data_and_tracer(lens_data=lens_data_7x7,
                                                       tracer=tracer,
                                                       padded_tracer=None)

        assert (fit_figure_of_merit == fit.figure_of_merit).all()


@pytest.fixture(name="combined")
def make_combined():
    normal_phase = MockPhase()

    # noinspection PyUnusedLocal
    def run_hyper(*args, **kwargs):
        return MockResult()

    # noinspection PyTypeChecker
    combined = phase_extensions.CombinedHyperPhase(
        normal_phase,
        hyper_phase_classes=(
            phase_extensions.HyperGalaxyPhase,
            phase_extensions.InversionPhase
        )
    )

    for phase in combined.hyper_phases:
        phase.run_hyper = run_hyper

    return combined


class TestHyperAPI(object):

    def test_combined_result(self, combined):
        result = combined.run(None)

        assert hasattr(result, "hyper_galaxy")
        assert isinstance(result.hyper_galaxy, MockResult)

        assert hasattr(result, "inversion")
        assert isinstance(result.inversion, MockResult)

        assert hasattr(result, "combined")
        assert isinstance(result.combined, MockResult)

    def test_combine_variables(self, combined):
        result = MockResult()
        hyper_galaxy_result = MockResult()
        inversion_result = MockResult()

        hyper_galaxy_result.variable = af.ModelMapper()
        inversion_result.variable = af.ModelMapper()

        hyper_galaxy_result.variable.hyper_galaxy = g.HyperGalaxy
        hyper_galaxy_result.variable.pixelization = px.Pixelization()
        inversion_result.variable.pixelization = px.Pixelization
        inversion_result.variable.hyper_galaxy = g.HyperGalaxy()

        result.hyper_galaxy = hyper_galaxy_result
        result.inversion = inversion_result

        variable = combined.combine_variables(result)

        assert isinstance(variable.hyper_galaxy, af.PriorModel)
        assert isinstance(variable.pixelization, af.PriorModel)

        assert variable.hyper_galaxy.cls == g.HyperGalaxy
        assert variable.pixelization.cls == px.Pixelization

    def test_instantiation(self, combined):
        assert len(combined.hyper_phases) == 2

        galaxy_phase = combined.hyper_phases[0]
        pixelization_phase = combined.hyper_phases[1]

        assert galaxy_phase.hyper_name == "hyper_galaxy"
        assert isinstance(
            galaxy_phase,
            phase_extensions.HyperGalaxyPhase
        )

        assert pixelization_phase.hyper_name == "inversion"
        assert isinstance(
            pixelization_phase,
            phase_extensions.InversionPhase
        )

    def test_hyper_result(self, ccd_data_7x7):
        normal_phase = MockPhase()

        # noinspection PyTypeChecker
        phase = phase_extensions.HyperGalaxyPhase(
            normal_phase
        )

        # noinspection PyUnusedLocal
        def run_hyper(*args, **kwargs):
            return MockResult()

        phase.run_hyper = run_hyper

        result = phase.run(ccd_data_7x7)

        assert hasattr(result, "hyper_galaxy")
        assert isinstance(result.hyper_galaxy, MockResult)