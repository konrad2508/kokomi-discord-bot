from __future__ import annotations

from typing import Type

from audio_source.i_pcm_source import IPCMSource


class Song:
    song_type: Type[IPCMSource]
    title: str
    url: str

    @classmethod
    async def create(cls, song_type: Type[IPCMSource], source: str) -> Song:
        self = cls()
        
        self.song_type = song_type

        instance = await self.song_type.from_search(source)

        self.title = instance.title
        self.url = instance.url

        return self

    async def get_instance(self) -> IPCMSource:
        return await self.song_type.from_search(self.url)
