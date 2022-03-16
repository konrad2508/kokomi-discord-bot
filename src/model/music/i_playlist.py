from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type
from audio_source.i_pcm_source import IPCMSource

from model.music.song import Song


class IPlaylist(ABC):
    '''Class representing a playlist, which fetches and stores songs from a playlist.'''

    songs: list[Song]

    @classmethod
    @abstractmethod
    def create(cls, song_type: Type[IPCMSource], source: str) -> IPlaylist:
        '''Creates an instance of IPlaylist with songs array.'''
