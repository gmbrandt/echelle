import numpy as np
from astropy.table import Table

from echelle.tests.utils import FakeContext, FakeImage
from echelle import basic


def test_gain_normalizer():
    image = FakeImage()
    context = FakeContext()
    image.data = np.ones((10, 10))
    image.set_header_val('gain', 2)
    image = basic.GainNormalizer(context).do_stage(image)
    assert image.get_header_val('gain') == 1
    assert np.allclose(image.data, 2)


def test_overscan_subtractor():
    image = FakeImage()
    context = FakeContext()
    image.data = np.ones((10, 12)).astype(float)
    image.data[:, 10:] = .5
    image.set_header_val('data_section', '[1:10,1:10]')
    image.set_header_val('overscan_section', '[1:10, 11:12]')
    image = basic.OverscanSubtractor(context).do_stage(image)
    assert np.allclose(image.data[:10, :10], 0.5)


def test_overscan_trimmer():
    image = FakeImage()
    context = FakeContext()
    image.data = np.ones((10, 12)).astype(float)
    image.data[:, 10:] = .5
    image.set_header_val('data_section', '[1:10,1:10]')
    image = basic.Trimmer(context).do_stage(image)
    assert np.allclose(image.data.shape, (10, 10))


class TestBackgroundSubtract1dSpectrum:
    def test_do_stage(self):
        stage = basic.BackgroundSubtractSpectrum(FakeContext())
        image = FakeImage()
        image.data_tables = {'SPECBOX': Table({'fiber': [1, 1], 'flux': np.ones((2, 10)),
                                               'stderr': np.ones((2, 10))})}
        image = stage.do_stage(image)
        assert np.allclose(image.data_tables['SPECBOX']['flux'].data, np.zeros((2, 10)))