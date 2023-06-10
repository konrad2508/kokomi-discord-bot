import yt_dlp

from audio_source.ytdlp_pcm_source import YtdlpPCMSource
from model.exception.unsupported_source import UnsupportedSource
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'audio_source.ytdlp_pcm_source'


@tested_module(TEST_MODULE)
class YtdlpPCMSourceCtorUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.init_mock = self.patch('IPCMSource.__init__')

    def test_ctor_calls_super_ctor(self) -> None:
        YtdlpPCMSource('audio_source', {}, '', volume=2.)

        self.init_mock.assert_called_once_with('audio_source', volume=2.)

    def test_ctor_calls_super_ctor_with_correct_default(self) -> None:
        YtdlpPCMSource('audio_source', {}, '')

        self.init_mock.assert_called_once_with('audio_source', volume=.5)

    def test_ctor_parses_data_correctly(self) -> None:
        obj = YtdlpPCMSource('', { 'title': 'title129', 'webpage_url': 'url452', 'duration': 87 }, '')

        self.assertEqual(obj.title, 'title129')
        self.assertEqual(obj.url, 'url452')
        self.assertEqual(obj.duration, 87)

    def test_ctor_parses_empty_data_correctly(self) -> None:
        obj = YtdlpPCMSource('', {}, '')

        self.assertEqual(obj.title, '')
        self.assertEqual(obj.url, '')
        self.assertEqual(obj.duration, 0)

    def test_ctor_parses_data_with_floored_duration(self) -> None:
        obj = YtdlpPCMSource('', { 'title': '', 'webpage_url': '', 'duration': 98.9 }, '')

        self.assertEqual(obj.duration, 98)

    def test_ctor_parses_data_with_duration_as_int_string(self) -> None:
        obj = YtdlpPCMSource('', { 'title': '', 'webpage_url': '', 'duration': '100' }, '')

        self.assertEqual(obj.duration, 100)

    def test_ctor_parses_data_with_duration_as_float_string(self) -> None:
        obj = YtdlpPCMSource('', { 'title': '', 'webpage_url': '', 'duration': '120.24' }, '')

        self.assertEqual(obj.duration, 120)


@tested_module(TEST_MODULE)
class YtdlpPCMSourceUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.super_init_mock = self.patch('IPCMSource.__init__')
        self.logging_mock = self.patch('logging')
        self.ytdlp_mock = self.patch('yt_dlp.YoutubeDL')
        self.ytdlp_mock_obj = self.ytdlp_mock.return_value
        self.ffmpeg_pcm_audio_mock = self.patch('FFmpegPCMAudio')

    async def test_from_search_uses_ytdlp(self) -> None:
        await YtdlpPCMSource.from_search('url')

        self.ytdlp_mock.assert_called_once()

    async def test_from_search_extracts_info_from_url_using_ytdlp(self) -> None:
        await YtdlpPCMSource.from_search('url')

        self.ytdlp_mock_obj.extract_info.assert_called_once_with('url', download=False)

    async def test_from_search_throws_unsupported_source_on_download_error_when_extract_info(self) -> None:
        self.ytdlp_mock_obj.extract_info.side_effect = yt_dlp.utils.DownloadError('error_msg')

        with self.assertRaises(UnsupportedSource):
            await YtdlpPCMSource.from_search('url')

    async def test_from_search_uses_ffmpeg_pcm_audio_as_source(self) -> None:
        await YtdlpPCMSource.from_search('url')

        self.ffmpeg_pcm_audio_mock.assert_called_once()
        self.super_init_mock.assert_called_once_with(self.ffmpeg_pcm_audio_mock.return_value, volume=.5)

    async def test_from_search_uses_url_in_entries_first_record_in_data_from_extract_info(self) -> None:
        self.ytdlp_mock_obj.extract_info.return_value = {
            'entries': [
                { 'url': 'deeply_nested_song_url' }
            ]
        }

        await YtdlpPCMSource.from_search('url')

        args, _ = self.ffmpeg_pcm_audio_mock.call_args
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0], 'deeply_nested_song_url')

    async def test_from_search_uses_url_in_flat_data_from_extract_info(self) -> None:
        self.ytdlp_mock_obj.extract_info.return_value = { 'url': 'song_url' }

        await YtdlpPCMSource.from_search('url')

        args, _ = self.ffmpeg_pcm_audio_mock.call_args
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0], 'song_url')

    async def test_from_search_uses_logging(self) -> None:
        await YtdlpPCMSource.from_search('url')

        self.logging_mock.info.assert_called()


@tested_module(TEST_MODULE)
class YtdlpPCMSourceIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.patch('IPCMSource.__init__')
        self.patch('logging')
        self.patch('FFmpegPCMAudio')

    async def test_from_search_correctly_gets_normal_song_from_youtube(self) -> None:
        obj = await YtdlpPCMSource.from_search('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

        self.assertEqual(obj.title, 'Rick Astley - Never Gonna Give You Up (Official Music Video)')
        self.assertEqual(obj.url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.assertEqual(obj.duration, 212)

    async def test_from_search_correctly_gets_playlist_song_from_youtube(self) -> None:
        obj = await YtdlpPCMSource.from_search('https://www.youtube.com/watch?v=q6EoRBvdVPQ&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo&index=1')

        self.assertEqual(obj.title, 'Yee')
        self.assertEqual(obj.url, 'https://www.youtube.com/watch?v=q6EoRBvdVPQ')
        self.assertEqual(obj.duration, 9)

    async def test_from_search_correctly_gets_shortened_url_song_from_youtube(self) -> None:
        obj = await YtdlpPCMSource.from_search('https://youtu.be/dQw4w9WgXcQ')

        self.assertEqual(obj.title, 'Rick Astley - Never Gonna Give You Up (Official Music Video)')
        self.assertEqual(obj.url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.assertEqual(obj.duration, 212)

    async def test_from_search_correctly_gets_song_from_soundcloud(self) -> None:
        obj = await YtdlpPCMSource.from_search('https://soundcloud.com/deathgrips/death-grips-exmilitary-2')

        self.assertEqual(obj.title, 'Death Grips - Exmilitary - 2 - Guillotine')
        self.assertEqual(obj.url, 'https://soundcloud.com/deathgrips/death-grips-exmilitary-2')
        self.assertEqual(obj.duration, 223)

    async def test_from_search_correctly_finds_song_from_youtube_based_on_query(self) -> None:
        obj = await YtdlpPCMSource.from_search('never gonna give you up')

        self.assertEqual(obj.title, 'Rick Astley - Never Gonna Give You Up (Official Music Video)')
        self.assertEqual(obj.url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.assertEqual(obj.duration, 212)
