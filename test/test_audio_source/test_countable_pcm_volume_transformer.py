import unittest
from unittest.mock import patch, call

from audio_source.countable_pcm_volume_transformer import CountablePCMVolumeTransformer


class CountablePCMVolumeTransformerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        patch('audio_source.countable_pcm_volume_transformer.PCMVolumeTransformer.__init__').start()
        
        self.read_mock = patch('audio_source.countable_pcm_volume_transformer.PCMVolumeTransformer.read').start()

        self.obj = CountablePCMVolumeTransformer(None)

    def tearDown(self) -> None:
        patch.stopall()

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


class CountablePCMVolumeTransformerCtorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        patch('audio_source.countable_pcm_volume_transformer.PCMVolumeTransformer.read').start()

        self.init_mock = patch('audio_source.countable_pcm_volume_transformer.PCMVolumeTransformer.__init__').start()

    def tearDown(self) -> None:
        patch.stopall()

    def test_ctor_calls_super_ctor(self) -> None:
        CountablePCMVolumeTransformer('original', 2)

        self.init_mock.assert_called_once_with('original', 2)

    def test_ctor_calls_super_ctor_with_correct_default_volume(self) -> None:
        CountablePCMVolumeTransformer('original')

        self.init_mock.assert_called_once_with('original', 1)
