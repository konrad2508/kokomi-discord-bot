from unittest.mock import call

from audio_source.countable_pcm_volume_transformer import CountablePCMVolumeTransformer
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'audio_source.countable_pcm_volume_transformer'


@tested_module(TEST_MODULE)
class CountablePCMVolumeTransformerCtorUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.init_mock = self.patch('PCMVolumeTransformer.__init__')

    def test_ctor_calls_super_ctor(self) -> None:
        CountablePCMVolumeTransformer('original', 2)

        self.init_mock.assert_called_once_with('original', 2)

    def test_ctor_calls_super_ctor_with_correct_default_volume(self) -> None:
        CountablePCMVolumeTransformer('original')

        self.init_mock.assert_called_once_with('original', 1)


@tested_module(TEST_MODULE)
class CountablePCMVolumeTransformerUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.read_mock = self.patch('PCMVolumeTransformer.read')
        self.patch('PCMVolumeTransformer.__init__')

        self.obj = CountablePCMVolumeTransformer(None)

    def test_read_calls_super_read_with_correct_args(self) -> None:
        for _ in range(50):
            self.obj.read()

        self.read_mock.assert_has_calls([call()] * 50)
        self.assertEqual(self.read_mock.call_count, 50)

    def test_current_time_returns_correct_time(self) -> None:
        for _ in range(50):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 1)

        for _ in range(50):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 2)

        for _ in range(50):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 3)

    def test_current_time_returns_floor_of_time_passed(self) -> None:
        for _ in range(49):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 0)

        for _ in range(50):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 1)

        for _ in range(50):
            self.obj.read()
        
        self.assertEqual(self.obj.current_time(), 2)
