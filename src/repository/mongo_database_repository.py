import pymongo

from config import Config, conf
from model.entity.emote_entity import EmoteEntity
from model.enum.emote_providers import EmoteProviders
from repository.i_database_repository import IDatabaseRepository


class MongoDatabaseRepository(IDatabaseRepository):
    '''Class responsible for accessing the MongoDB database.'''

    def __init__(self, config: Config) -> None:
        client = pymongo.MongoClient(config.database_connection_string)
        database = client[config.database_name]

        self.emote_collection = database[config.database_emote_collection_name]

    async def get_emote(self, query: str, provider: EmoteProviders) -> EmoteEntity | None:
        emote = self.emote_collection.find_one({'query': query, 'provider': provider.encode()})

        if emote is None:
            return emote

        emote = EmoteEntity.from_dict(emote)

        return emote
    
    async def save_emote(self, emote: EmoteEntity) -> EmoteEntity:
        self.emote_collection.insert_one(emote.to_dict())

        return emote

mongo_database_repository = MongoDatabaseRepository(conf)
