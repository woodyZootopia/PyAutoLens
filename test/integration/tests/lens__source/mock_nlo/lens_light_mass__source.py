from test.integration.tests.lens__source import lens_light_mass__source
from test.integration.tests.runner import run_a_mock


class TestCase:
    def _test_lens_light_mass__source(self):
        run_a_mock(lens_light_mass__source)
