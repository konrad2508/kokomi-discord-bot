from abc import ABC, abstractmethod


class IEmoteDownloadingService(ABC):
    '''Class responsible for downloading an emote from a provider.'''

    @abstractmethod
    async def download(self, emote_mime: str, emote_content: bytes) -> str:
        '''Downloads an emote from emote_content based on it's type set in emote_mime. Returns
        a filepath to the downloaded emote.'''
