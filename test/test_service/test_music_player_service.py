from unittest.mock import AsyncMock

from model.exception.no_song_playing import NoSongPlaying
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.already_connected import AlreadyConnected
from model.exception.not_yet_connected import NotYetConnected
from service.music_player_service import MusicPlayerService
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'service.music_player_service'


@tested_module(TEST_MODULE)
class MusicPlayerServiceUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.vc_mock = self.patch('VC')
        self.vc_mock_obj = self.vc_mock.return_value
        self.song_service = self.patch('SongService').return_value

        self.obj = MusicPlayerService(self.song_service)

    async def test_check_if_not_connected_throws_exception_if_connected(self) -> None:
        await self.obj.connect(10, AsyncMock())

        self.assertRaises(AlreadyConnected, self.obj.check_if_not_connected, 10)
    
    def test_check_if_not_connected_throws_no_exception_if_not_connected(self) -> None:
        self.assertNotRaises(AlreadyConnected, self.obj.check_if_not_connected, 10)

    def test_check_if_connected_throws_exception_if_not_connected(self) -> None:
        self.assertRaises(NotYetConnected, self.obj.check_if_connected, 10)

    async def test_check_if_connected_throws_no_exception_if_connected(self) -> None:
        await self.obj.connect(10, AsyncMock())

        self.assertNotRaises(NotYetConnected, self.obj.check_if_connected, 10)

    async def test_check_if_queue_not_locked_throws_exception_if_locked(self) -> None:
        self.vc_mock_obj.is_queue_locked = True
        await self.obj.connect(10, AsyncMock())

        self.assertRaises(MusicQueueLocked, self.obj.check_if_queue_not_locked, 10)

    async def test_check_if_queue_not_locked_throws_no_exception_if_not_locked(self) -> None:
        self.vc_mock_obj.is_queue_locked = False
        await self.obj.connect(10, AsyncMock())

        self.assertNotRaises(MusicQueueLocked, self.obj.check_if_queue_not_locked, 10)

    def test_check_if_queue_not_locked_throws_no_exception_if_no_queue(self) -> None:
        self.assertNotRaises(MusicQueueLocked, self.obj.check_if_queue_not_locked, 10)

    async def test_check_if_song_playing_throws_exception_if_is_not(self) -> None:
        self.vc_mock_obj.currently_playing = None
        await self.obj.connect(10, AsyncMock())

        self.assertRaises(NoSongPlaying, self.obj.check_if_song_playing, 10)

    async def test_check_if_song_playing_throws_no_exception_if_is(self) -> None:
        self.vc_mock_obj.currently_playing = AsyncMock()
        await self.obj.connect(10, AsyncMock())

        self.assertNotRaises(NoSongPlaying, self.obj.check_if_song_playing, 10)

    def test_check_if_song_playing_throws_no_exception_if_no_queue(self) -> None:
        self.assertNotRaises(NoSongPlaying, self.obj.check_if_song_playing, 10)

    async def test_connect_check_if_connects(self) -> None:
        channel = AsyncMock()

        await self.obj.connect(10, channel)

        channel.connect.assert_called_once()
        self.vc_mock.assert_called_once_with(channel.connect.return_value, False, [], None, None, False)

    async def test_disconnect_check_if_disconnects(self) -> None:
        self.vc_mock_obj.connection = AsyncMock()
        await self.obj.connect(10, AsyncMock())

        await self.obj.disconnect(10)

        self.vc_mock_obj.connection.disconnect.assert_called_once_with(force=True)

    async def test_play_adds_songs_from_playlist(self) -> None:
        self.song_service.get_playlist.return_value = ['song1', 'song2', 'song3']
        self.vc_mock_obj.connection.is_playing.return_value = True
        self.vc_mock_obj.queue.__iadd__.return_value = self.vc_mock_obj.queue
        on_added_playlist = AsyncMock()
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, on_added_playlist, None, None, None, 'link', True)

        self.song_service.get_playlist.assert_called_once_with('link')
        self.vc_mock_obj.queue.__iadd__.assert_called_with(['song1', 'song2', 'song3'])
        on_added_playlist.assert_called_once_with(3)

    async def test_play_adds_song_from_link(self) -> None:
        song = AsyncMock()
        self.song_service.get_song = AsyncMock()
        self.song_service.get_song.return_value = song
        self.vc_mock_obj.connection.is_playing.return_value = True
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, AsyncMock(), None, None, None, None, 'songlink', False)

        self.song_service.get_song.assert_called_once_with('songlink')
        self.vc_mock_obj.queue.append.assert_called_once_with(song)

    async def test_play_enqueues_song_when_other_is_playing(self) -> None:
        song = AsyncMock()
        song.title = 'songtitle'
        song.url = 'songurl'
        self.song_service.get_song = AsyncMock()
        self.song_service.get_song.return_value = song
        self.vc_mock_obj.connection.is_playing.return_value = True
        on_added = AsyncMock()
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, on_added, None, None, None, None, None, False)

        on_added.assert_called_once_with('songtitle', 'songurl')

    async def test_play_starts_playback_when_queue_is_empty(self) -> None:
        song = AsyncMock()
        song.title = 'song1 title'
        song.url = 'http://song1url'
        song.get_instance.return_value = 'an instance of song1'
        self.song_service.get_song = AsyncMock()
        self.song_service.get_song.return_value = song
        self.vc_mock_obj.queue = []
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        on_play = AsyncMock()
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, None, on_play, None, None, 'link', False)

        song.get_instance.assert_called_once()
        self.assertEqual(self.vc_mock_obj.queue, [])
        self.assertEqual(self.vc_mock_obj.currently_playing_song, song)
        self.assertEqual(self.vc_mock_obj.currently_playing, 'an instance of song1')
        on_play.assert_called_once_with('song1 title', 'http://song1url')
        self.assertEqual(self.vc_mock_obj.connection.play.call_args[0][0], 'an instance of song1')

    async def test_play_plays_next_song_in_queue_on_playback_end(self) -> None:
        song1, song2 = AsyncMock(), AsyncMock()
        song1.title, song2.title = 'song1 title', 'song2 title'
        song1.url, song2.url = 'http://song1url', 'http://song2url'
        song1.get_instance.return_value, song2.get_instance.return_value = 'an instance of song1', 'an instance of song2'
        self.song_service.get_playlist.return_value = [song1, song2]
        self.vc_mock_obj.queue = []
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        on_play = AsyncMock()
        asyncio_mock = self.patch('asyncio')
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, AsyncMock(), on_play, None, None, 'link', True)
        self.vc_mock_obj.connection.play.call_args[1]['after'](None)
        await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]

        self.assertEqual(self.vc_mock_obj.queue, [])
        self.assertHasCalls(on_play, [(song1.title, song1.url), (song2.title, song2.url)])
        self.assertListEqual(
            ['an instance of song1', 'an instance of song2'],
            [args[0][0] for args in self.vc_mock_obj.connection.play.call_args_list]
        )

    async def test_play_ends_queue_after_finishing_playing_last_song(self) -> None:
        song = AsyncMock()
        song.title = 'song title'
        song.url = 'http://songurl'
        song.get_instance.return_value = 'an instance of song'
        self.vc_mock_obj.queue = []
        self.song_service.get_playlist.return_value = [song]
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        on_end = AsyncMock()
        asyncio_mock = self.patch('asyncio')
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, AsyncMock(), AsyncMock(), on_end, None, 'link', True)
        self.vc_mock_obj.is_queue_empty.return_value = True
        self.vc_mock_obj.connection.play.call_args[1]['after'](None)
        await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]

        self.assertEqual(self.vc_mock_obj.currently_playing_song, None)
        self.assertEqual(self.vc_mock_obj.currently_playing, None)
        on_end.assert_called_once()
    
    async def test_play_repeats_current_song_if_queue_is_looped(self) -> None:
        song = AsyncMock()
        song.title = 'song title'
        song.url = 'http://songurl'
        song.get_instance.return_value = 'an instance of song'
        self.vc_mock_obj.queue = []
        self.song_service.get_playlist.return_value = [song]
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        asyncio_mock = self.patch('asyncio')
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, AsyncMock(), AsyncMock(), None, None, 'link', True)
        self.vc_mock_obj.is_looped = True
        song.get_instance.return_value = 'second instance of song'
        self.vc_mock_obj.connection.play.call_args[1]['after'](None)
        await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]
        song.get_instance.return_value = 'third instance of song'
        self.vc_mock_obj.connection.play.call_args[1]['after'](None)
        await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]

        self.assertEqual(self.vc_mock_obj.currently_playing_song, song)
        self.assertEqual(self.vc_mock_obj.currently_playing, 'third instance of song')
        self.assertListEqual(
            ['an instance of song', 'second instance of song', 'third instance of song'],
            [args[0][0] for args in self.vc_mock_obj.connection.play.call_args_list]
        )

    async def test_play_logs_missing_current_song_while_looping(self) -> None:
        song = AsyncMock()
        song.title = 'song title'
        song.url = 'http://songurl'
        song.get_instance.return_value = 'an instance of song'
        self.vc_mock_obj.queue = []
        self.song_service.get_playlist.return_value = [song]
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        asyncio_mock = self.patch('asyncio')
        logging_mock = self.patch('logging')
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, AsyncMock(), AsyncMock(), None, None, 'link', True)
        self.vc_mock_obj.is_looped = True
        self.vc_mock_obj.currently_playing_song = None
        self.vc_mock_obj.connection.play.call_args[1]['after'](None)
        
        with self.assertRaises(Exception):
            await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]
        logging_mock.error.assert_called()

    async def test_play_handles_errors_while_playing_songs(self) -> None:
        song = AsyncMock()
        song.title = 'song title'
        song.url = 'http://songurl'
        song.get_instance.return_value = song
        self.vc_mock_obj.queue = []
        self.song_service.get_playlist.return_value = [song]
        self.vc_mock_obj.connection.is_playing.return_value = False
        self.vc_mock_obj.is_looped = False
        self.vc_mock_obj.is_queue_empty.return_value = False
        asyncio_mock = self.patch('asyncio')
        logging_mock = self.patch('logging')
        await self.obj.connect(10, AsyncMock())

        await self.obj.play(10, None, AsyncMock(), AsyncMock(), AsyncMock(), None, 'link', True)
        self.vc_mock_obj.is_queue_empty.return_value = True
        self.vc_mock_obj.connection.play.call_args[1]['after']('an error')
        await asyncio_mock.run_coroutine_threadsafe.call_args[0][0]

        logging_mock.error.assert_called()

    async def test_now_playing_throws_exception_if_no_song_playing(self) -> None:
        self.vc_mock_obj.currently_playing = None
        await self.obj.connect(10, AsyncMock())

        self.assertRaises(NoSongPlaying, self.obj.now_playing, 10)
    
    async def test_now_playing_returns_correct_object(self) -> None:
        self.patch('CurrentlyPlaying').side_effect = lambda a, b, c, d: {
            'title_mocked': a,
            'url_mocked': b,
            'current_duration_mocked': c,
            'total_duration_mocked': d
        }
        self.patch('Duration').side_effect = lambda x: f'very c00l duration {x}'
        self.vc_mock_obj.currently_playing.title = 'test title of a song'
        self.vc_mock_obj.currently_playing.url = 'http://example.com'
        self.vc_mock_obj.currently_playing.current_time.return_value = 27
        self.vc_mock_obj.currently_playing.duration = 56
        await self.obj.connect(10, AsyncMock())

        ret = self.obj.now_playing(10)

        self.assertEqual(ret['title_mocked'], 'test title of a song')
        self.assertEqual(ret['url_mocked'], 'http://example.com')
        self.assertEqual(ret['current_duration_mocked'], 'very c00l duration 27')
        self.assertEqual(ret['total_duration_mocked'], 'very c00l duration 56')

    async def test_skip_correctly_skips_song(self) -> None:
        await self.obj.connect(10, AsyncMock())

        self.obj.skip(10)

        self.assertEqual(self.vc_mock_obj.is_looped, False)
        self.vc_mock_obj.connection.stop.assert_called_once()

    async def test_queue_throws_exception_if_no_song_playing(self) -> None:
        self.vc_mock_obj.currently_playing = None
        await self.obj.connect(10, AsyncMock())

        self.assertRaises(NoSongPlaying, self.obj.queue, 10)
    
    async def test_queue_correctly_returns_music_queue_information(self) -> None:
        self.vc_mock_obj.currently_playing = 'currently playing this song'
        self.vc_mock_obj.queue = 'this is the queue'
        self.vc_mock_obj.is_looped = 'is the queue looped'
        await self.obj.connect(10, AsyncMock())

        ret = self.obj.queue(10)

        self.assertEqual(ret[0], 'currently playing this song')
        self.assertEqual(ret[1], 'this is the queue')
        self.assertEqual(ret[2], 'is the queue looped')
    
    async def test_loop_correctly_loops_queue(self) -> None:
        self.vc_mock_obj.is_looped = False
        await self.obj.connect(10, AsyncMock())

        ret = self.obj.loop(10)

        self.assertEqual(self.vc_mock_obj.is_looped, True)
        self.assertEqual(self.vc_mock_obj.is_looped, ret)
    
    async def test_loop_correctly_unloops_queue(self) -> None:
        self.vc_mock_obj.is_looped = True
        await self.obj.connect(10, AsyncMock())

        ret = self.obj.loop(10)

        self.assertEqual(self.vc_mock_obj.is_looped, False)
        self.assertEqual(self.vc_mock_obj.is_looped, ret)

    async def test_purge_clears_queue(self) -> None:
        self.vc_mock_obj.is_looped = True
        self.vc_mock_obj.queue = ['a', 'b', 'c', 10]
        await self.obj.connect(10, AsyncMock())

        self.obj.purge(10)

        self.assertEqual(self.vc_mock_obj.is_looped, False)
        self.assertEqual(self.vc_mock_obj.queue, [])
    
    async def test_purge_stops_currently_playing_song(self) -> None:
        await self.obj.connect(10, AsyncMock())

        self.obj.purge(10)

        self.vc_mock_obj.connection.stop.assert_called_once()
