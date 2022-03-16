import asyncio
import logging
from typing import Callable

from nextcord import VoiceChannel

from audio_source.i_pcm_source import IPCMSource
from model.exception.already_connected import AlreadyConnected
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.no_song_playing import NoSongPlaying
from model.exception.not_yet_connected import NotYetConnected
from model.music.currently_playing import CurrentlyPlaying
from model.music.duration import Duration
from model.music.vc import VC
from service.song_service import SongService, song_service


class MusicPlayerService:
    '''Class responsible for the music playback capabilities of the bot.'''

    def __init__(self, song_service: SongService) -> None:
        self.song_service = song_service
        self.voice_channels: dict[int, VC] = {}

    def check_if_not_connected(self, id: int) -> None:
        '''Checks if the bot is not connected to a voice channel. Throws AlreadyConnected exception
        if it is.'''

        if id in self.voice_channels:
            raise AlreadyConnected

    def check_if_connected(self, id: int) -> None:
        '''Checks if the bot is connected to a voice channel. Throws NotYetConnected exception
        if it is not.'''

        if id not in self.voice_channels:
            raise NotYetConnected

    def check_if_queue_not_locked(self, id: int) -> None:
        '''Checks if the music queue of a server is not locked. Throws MusicQueueLocked exception
        if it is.'''

        if self.voice_channels[id] and self.voice_channels[id].is_queue_locked:
            raise MusicQueueLocked

    def check_if_song_playing(self, id: int) -> None:
        '''Checks if the bot is playing a song. Throws NoSongPlaying if it is not.'''

        if self.voice_channels[id] and self.voice_channels[id].currently_playing is None:
            raise NoSongPlaying

    async def connect(self, id: int, channel: VoiceChannel) -> None:
        '''Connects the bot to a voice channel.'''

        conn = await channel.connect()
        self.voice_channels[id] = VC(conn, False, [], None, None, False)

    async def disconnect(self, id: int) -> None:
        '''Disconnects the bot from a voice channel.'''

        await self.voice_channels[id].connection.disconnect(force=True)
        del self.voice_channels[id]

    async def play(
            self,
            id: int,
            on_added: Callable,
            on_added_playlist: Callable,
            on_play: Callable,
            on_end: Callable,
            loop: asyncio.AbstractEventLoop,
            link: str,
            use_playlist: bool) -> None:
        '''Plays a song in a voice channel.'''
        
        server = self.voice_channels[id]

        if use_playlist:
            songs = self.song_service.get_playlist(link)
            server.queue += songs

            await on_added_playlist(len(songs))
        
        else:
            song = await self.song_service.get_song(link)
            server.queue.append(song)

        if not server.connection.is_playing():
            await self._play_from_queue(id, on_play, on_end, loop, None)

        elif not use_playlist:
            await on_added(song.title, song.url)

    def now_playing(self, id: int) -> CurrentlyPlaying:
        '''Returns the currently playing song.'''

        currently_playing = self.voice_channels[id].currently_playing

        if currently_playing is None:
            raise NoSongPlaying

        return CurrentlyPlaying(
            currently_playing.title,
            currently_playing.url,
            Duration(currently_playing.current_time()),
            Duration(currently_playing.duration)
        )

    def skip(self, id: int) -> None:
        '''Skips the currently playing song.'''

        server = self.voice_channels[id]

        server.is_looped = False

        server.connection.stop()

    def queue(self, id: int) -> tuple[IPCMSource, list[IPCMSource], bool]:
        '''Returns a tuple containing in order: the currently playing song, the song queue,
        information whether the queue is locked.'''

        server = self.voice_channels[id]

        if server.currently_playing is None:
            raise NoSongPlaying

        return server.currently_playing, server.queue, server.is_looped

    def loop(self, id: int) -> bool:
        '''Toggles the looping status of the currently playing song.'''

        server = self.voice_channels[id]

        result = server.is_looped = not server.is_looped

        return result

    async def _play_from_queue(
            self,
            id: int,
            on_play: Callable,
            on_end: Callable,
            loop: asyncio.AbstractEventLoop,
            error: Exception | None) -> None:
        '''Handles the song playback from the queue.'''

        server = self.voice_channels[id]

        if error:
            logging.error(f'_play_from_queue has error: "{error}"')

            if server.currently_playing is not None:
                logging.error(f'song: title="{server.currently_playing.title}" url="{server.currently_playing.url}"')
            
            else:
                logging.error('server.currently_playing is None')

        if server.is_looped:
            song = server.currently_playing_song

            if song is None:
                logging.error('_play_from_queue: server.is_looped = True and song is None')
                logging.error(error)

                raise Exception

            song_instance = await song.get_instance()
            server.currently_playing = song_instance

            server.connection.play(
                song_instance,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._play_from_queue(id, on_play, on_end, loop, e),
                    loop
                )
            )

        elif not server.is_queue_empty():
            song = server.queue.pop(0)
            song_instance = await song.get_instance()

            server.currently_playing_song = song
            server.currently_playing = song_instance

            await on_play(song.title, song.url)

            server.connection.play(
                song_instance,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._play_from_queue(id, on_play, on_end, loop, e),
                    loop
                )
            )

        else:
            server.currently_playing_song = None
            server.currently_playing = None
            await on_end()


music_player_service = MusicPlayerService(song_service)
