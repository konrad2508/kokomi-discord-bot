from abc import ABC, abstractmethod

from model.reaction.emote import Emote


class IEmoteProviderService(ABC):
    '''Class responsible for getting an emote from a provider.'''

    @abstractmethod
    async def get_emote(self, query: str) -> Emote:
        '''Gets an emote based on query. Returns it as Emote object.'''
