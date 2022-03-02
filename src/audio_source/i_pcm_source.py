from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type

from audio_source.countable_pcm_volume_transformer import CountablePCMVolumeTransformer


class IPCMSource(ABC, CountablePCMVolumeTransformer):
    '''Interface representing a song.
    
    Classes implementing this interface must contain title, url and duration fields.
    Instances of extending classes should be instantiated using from_search method.'''

    title: str
    url: str
    duration: int

    @classmethod
    @abstractmethod
    async def from_search(cls: Type[IPCMSource], search: str) -> IPCMSource:
        '''Returns an instance representing a song identified by the search argument, being either a url or a query.'''

    @abstractmethod
    async def get_new_instance(self) -> IPCMSource:
        '''Returns a new instance representing the same song. Used to play the same song again.'''
