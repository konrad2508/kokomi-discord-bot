from model.entity.emote_entity import EmoteEntity
from model.enum.emote_providers import EmoteProviders
from model.reaction.cached_emote import CachedEmote
from model.reaction.emote import Emote


class ConvertorService:
    '''Class responsible for converting data classes into entities, and vice-versa.'''

    def emote_data_to_entity(self, data: Emote, query: str, provider: EmoteProviders, url: str) -> EmoteEntity:
        '''Converts Emote with additional arguments to EmoteEntity.'''

        entity = EmoteEntity(data.name, query, provider, url)

        return entity
    
    def emote_entity_to_data(self, entity: EmoteEntity) -> CachedEmote:
        '''Converts EmoteEntity to CachedEmote.'''

        data = CachedEmote(entity.name, entity.url)

        return data

convertor_service = ConvertorService()
