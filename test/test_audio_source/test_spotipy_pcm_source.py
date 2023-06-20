import os

from dotenv import dotenv_values, find_dotenv

from audio_source.spotipy_pcm_source import SpotipyPCMSource
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'audio_source.spotipy_pcm_source'


@tested_module(TEST_MODULE)
class SpotipyPCMSourceUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.super_from_search_mock = self.patch('YtdlpPCMSource.from_search')
        self.logging_mock = self.patch('logging')
        self.spotipy_mock = self.patch('spotipy')

    async def test_from_search_creates_logs(self) -> None:
        await SpotipyPCMSource.from_search('open.spotify.com')

        self.logging_mock.info.assert_called()

    async def test_from_search_passes_bad_url_to_super(self) -> None:
        await SpotipyPCMSource.from_search('bad url')

        self.super_from_search_mock.assert_called_once_with('bad url')

    async def test_from_search_authorizes_with_spotipy(self) -> None:
        await SpotipyPCMSource.from_search('open.spotify.com')

        self.spotipy_mock.SpotifyClientCredentials.assert_called_once()
        self.spotipy_mock.Spotify.assert_called_once_with(
            client_credentials_manager=self.spotipy_mock.SpotifyClientCredentials.return_value
        )

    async def test_from_search_gets_song_data_from_spotipy(self) -> None:
        await SpotipyPCMSource.from_search('open.spotify.com')

        self.spotipy_mock.Spotify.return_value.track.assert_called_once_with('open.spotify.com')

    async def test_from_search_passes_correct_song_query_to_super(self) -> None:
        song = {
            'name': 'name of the song',
            'artists': [
                { 'name': 'artist name' }
            ]
        }
        self.spotipy_mock.Spotify.return_value.track.return_value = song
        self.super_from_search_mock.side_effect = lambda x: x

        ret = await SpotipyPCMSource.from_search('open.spotify.com')

        self.assertEqual(ret, 'artist name - name of the song')


@tested_module(TEST_MODULE)
class SpotipyPCMSourceIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.super_from_search_mock = self.patch('YtdlpPCMSource.from_search')
        self.patch('logging')
        self.patch_dict(os.environ, dotenv_values(find_dotenv()))

    def tearDown(self) -> None:
        super().tearDown()

        if os.path.exists('.cache'):
            os.remove('.cache')

    async def test_from_search_correctly_gets_song_from_spotify(self) -> None:
        self.super_from_search_mock.side_effect = lambda x: x

        ret = await SpotipyPCMSource.from_search('https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT')

        self.assertEqual(ret, 'Rick Astley - Never Gonna Give You Up')
