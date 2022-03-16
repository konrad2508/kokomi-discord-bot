from __future__ import annotations

from typing import Type

import youtubesearchpython as ytsp

from audio_source.i_pcm_source import IPCMSource
from model.exception.cannot_add_playlist import CannotAddPlaylist
from model.music.i_playlist import IPlaylist
from model.music.song import Song


class YoutubePlaylist(IPlaylist):
    songs: list[Song]

    @classmethod
    def create(cls, song_type: Type[IPCMSource], source: str) -> YoutubePlaylist:
        '''Creates an instance of YoutubePlaylist with Youtube songs array.'''

        self = cls()

        try:
            playlist_songs = ytsp.Playlist.getVideos(source)['videos']

        except Exception:
            raise CannotAddPlaylist

        self.songs = [ Song(song_type, song['title'], f'https://youtube.com/watch?v={song["id"]}') for song in playlist_songs ]

        return self
