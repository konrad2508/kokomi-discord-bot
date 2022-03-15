from abc import ABC, abstractmethod

from model.reaction.downloaded_emote import DownloadedEmote


class IEmoteProviderService(ABC):
    '''Class responsible for getting an emote from a provider.'''

    @abstractmethod
    async def get_emote(self, query: str, use_raw: bool) -> DownloadedEmote:
        '''Gets an emote based on query. Returns it as Emote object.'''
