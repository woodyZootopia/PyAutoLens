import autofit as af
import autolens as al
from test_autolens.integration.tests.imaging import runner

test_type = "features"
test_name = "assertion"
data_type = "lens_light_dev_vaucouleurs"
data_resolution = "lsst"


def make_pipeline(name, phase_folders, optimizer_class=af.MultiNest):

    sersic = af.PriorModel(al.lp.EllipticalSersic)

    # This will lead to pretty weird results

    sersic.add_assertion(sersic.axis_ratio > sersic.intensity)

    phase1 = al.PhaseImaging(
        phase_name="phase_1",
        phase_folders=phase_folders,
        galaxies=dict(lens=al.GalaxyModel(redshift=0.5, sersic=sersic)),
        optimizer_class=optimizer_class,
    )

    phase1.optimizer.const_efficiency_mode = True
    phase1.optimizer.n_live_points = 40
    phase1.optimizer.sampling_efficiency = 0.8

    # TODO : And even with them not causing errors above, the promise doesnt work.

    phase2 = al.PhaseImaging(
        phase_name="phase_2",
        phase_folders=phase_folders,
        galaxies=dict(lens=phase1.result.model.galaxies.lens),
        optimizer_class=optimizer_class,
    )

    phase2.optimizer.const_efficiency_mode = True
    phase2.optimizer.n_live_points = 40
    phase2.optimizer.sampling_efficiency = 0.8

    return al.PipelineDataset(name, phase1, phase2)


if __name__ == "__main__":
    import sys

    runner.run(sys.modules[__name__])
