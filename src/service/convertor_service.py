from model.entity.emote_entity import EmoteEntity
from model.entity.user_entity import UserEntity
from model.enum.emote_providers import EmoteProviders
from model.reaction.online_emote import OnlineEmote
from model.reaction.emote import Emote


class ConvertorService:
    '''Class responsible for converting data classes into entities, and vice-versa.'''

    def emote_data_to_entity(self, data: Emote, query: str, provider: EmoteProviders, url: str) -> EmoteEntity:
        '''Converts Emote with additional arguments to EmoteEntity.'''

        entity = EmoteEntity(data.name, query, provider, url)

        return entity
    
    def emote_entity_to_data(self, entity: EmoteEntity) -> OnlineEmote:
        '''Converts EmoteEntity to CachedEmote.'''

        data = OnlineEmote(entity.name, entity.url)

        return data
    
    def user_data_to_entity(self, id: int) -> UserEntity:
        '''Converts User to UserEntity.'''

        entity = UserEntity(id)

        return entity

convertor_service = ConvertorService()
