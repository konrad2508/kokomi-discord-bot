from abc import ABC, abstractmethod

from model.entity.emote_entity import EmoteEntity
from model.enum.emote_providers import EmoteProviders


class IDatabaseRepository(ABC):
    '''Class responsible for accessing the database.'''

    @abstractmethod
    async def get_emote(self, query: str, provider: EmoteProviders) -> EmoteEntity | None:
        '''Gets an emote from the database. Returns EmoteEntity if an emote was found, None otherwise.'''

    @abstractmethod
    async def save_emote(self, emote: EmoteEntity) -> EmoteEntity:
        '''Saves an emote in the database. Returns the saved emote.'''
