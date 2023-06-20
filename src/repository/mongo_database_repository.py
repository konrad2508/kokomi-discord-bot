import pymongo

from config import Config
from model.entity.emote_entity import EmoteEntity
from model.entity.user_entity import UserEntity
from model.enum.emote_providers import EmoteProviders
from repository.i_database_repository import IDatabaseRepository


class MongoDatabaseRepository(IDatabaseRepository):
    '''Class responsible for accessing the MongoDB database.'''

    def __init__(self, config: Config) -> None:
        client = pymongo.MongoClient(config.database_connection_string)
        database = client[config.database_name]

        self.emote_collection = database[config.database_emote_collection_name]
        self.banned_user_collection = database[config.database_banned_user_collection_name]
        self.authorized_user_collection = database[config.database_authorized_user_collection_name]

    async def get_emote(self, query: str, provider: EmoteProviders) -> EmoteEntity | None:
        '''Returns the emote from the specified provider from the database.'''

        emote = self.emote_collection.find_one({'query': query, 'provider': provider.encode()})

        if emote is None:
            return emote

        emote = EmoteEntity.from_dict(emote)

        return emote

    async def save_emote(self, emote: EmoteEntity) -> EmoteEntity:
        '''Saves the emote in the database. Returns the saved emote.'''

        self.emote_collection.insert_one(emote.to_dict())

        return emote

    async def ban_user(self, user: UserEntity) -> UserEntity:
        '''Bans an user and saves its data in the database. Returns the banned user.'''
    
        self.banned_user_collection.insert_one(user.to_dict())

        return user
    
    async def unban_user(self, user: UserEntity) -> UserEntity:
        '''Unbans an user and removes its data from the database. Returns the unbanned user.'''

        self.banned_user_collection.delete_one(user.to_dict())

        return user
    
    async def list_banned_users(self) -> list[UserEntity]:
        '''Lists banned users present in the database. Returns the list of banned users.'''

        banned_users = self.banned_user_collection.find()
        banned_users = list(map(UserEntity.from_dict, banned_users))

        return banned_users

    async def authorize_user(self, user: UserEntity) -> UserEntity:
        '''Authorizes an user and saves its data in the database. Returns the authorized user.'''
    
        self.authorized_user_collection.insert_one(user.to_dict())

        return user
    
    async def unauthorize_user(self, user: UserEntity) -> UserEntity:
        '''Unauthorizes an user and removes its data from the database. Returns the unauthorized user.'''

        self.authorized_user_collection.delete_one(user.to_dict())

        return user

    
    async def list_authorized_users(self) -> list[UserEntity]:
        '''Lists authorized users present in the database. Returns the list of authorized users.'''

        authorized_users = self.authorized_user_collection.find()
        authorized_users = list(map(UserEntity.from_dict, authorized_users))

        return authorized_users
