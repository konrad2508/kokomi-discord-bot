from __future__ import annotations

import logging
import re

from audio_source.spotipy_pcm_source import SpotipyPCMSource
from audio_source.ytdlp_pcm_source import YtdlpPCMSource
from model.exception.playlist_is_song import PlaylistIsSong
from model.exception.playlist_source_not_supported import PlaylistSourceNotSupported
from model.exception.song_is_playlist import SongIsPlaylist
from model.music.song import Song
from model.music.youtube_playlist import YoutubePlaylist


class SongService:
    '''Class responsible for returning a song object as an adequate class.'''

    async def get_song(self, source: str) -> Song:
        logging.info(f'getting song for {source}')

        if re.match(r'^.*youtube\.com\/playlist', source) is not None:
            raise SongIsPlaylist

        if re.match(r'^.*open\.spotify\.com', source) is not None:
            song_source = SpotipyPCMSource
        else:
            song_source = YtdlpPCMSource

        song = await Song.from_search(song_source, source)

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


song_service = SongService()
