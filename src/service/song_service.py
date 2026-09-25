from __future__ import annotations

import base64
import logging
import re
import tempfile

from audio_source.ytdlp_pcm_source import YtdlpPCMSource
from config import Config
from model.exception.playlist_is_song import PlaylistIsSong
from model.exception.playlist_source_not_supported import PlaylistSourceNotSupported
from model.exception.song_is_playlist import SongIsPlaylist
from model.music.song import Song
from model.music.youtube_playlist import YoutubePlaylist


class SongService:
    '''Class responsible for returning a song object as an adequate class.'''

    def __init__(self, conf: Config) -> None:
        if not conf.youtube_cookies_base64:
            logging.error('no youtube cookies present')

            return

        cookies = base64.b64decode(conf.youtube_cookies_base64).decode('utf-8')

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as cookies_file:
            cookies_file.write(cookies)

            self.youtube_cookies = cookies_file.name


    async def get_song(self, source: str) -> Song:
        logging.info(f'getting song for {source}')

        if re.match(r'^.*youtube\.com\/playlist', source) is not None:
            raise SongIsPlaylist

        song_source = YtdlpPCMSource

        song = await Song.from_search(song_source, source, self.youtube_cookies)

        return song
    
    def get_playlist(self, source: str) -> list[Song]:
        logging.info(f'getting playlist for {source}')

        if re.match(r'^.*youtube\.com', source) is None:
            raise PlaylistSourceNotSupported

        if re.match(r'^.*youtube\.com\/playlist', source) is None:
            raise PlaylistIsSong
        
        playlist = YoutubePlaylist.create(YtdlpPCMSource, source)
        songs = playlist.songs

        return songs
