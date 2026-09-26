from __future__ import annotations

from typing import Type

from audio_source.i_pcm_source import IPCMSource


class Song:
    '''Class representing a song.'''

    def __init__(self, song_type: Type[IPCMSource], title: str, url: str) -> None:
        self.song_type = song_type
        self.title = title
        self.url = url

    @classmethod
    async def from_search(cls, song_type: Type[IPCMSource], source: str) -> Song:
        '''Creates an instance of Song by fetching song's info from the Internet.'''

        instance = await song_type.from_search(source)
        
        self = cls(song_type, instance.title, instance.url)

        return self

    async def get_instance(self) -> IPCMSource:
        '''Returns a fresh instance of the song.'''

        return await self.song_type.from_search(self.url)
