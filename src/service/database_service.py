from model.enum.emote_providers import EmoteProviders
from model.reaction.emote import Emote
from repository.i_database_repository import IDatabaseRepository
from repository.mongo_database_repository import mongo_database_repository
from service.convertor_service import ConvertorService, convertor_service


class DatabaseService:
    '''Class responsible for communication with a database repository.'''

    def __init__(self, database_repository: IDatabaseRepository, convertor_service: ConvertorService) -> None:
        self.database_repository = database_repository
        self.convertor_service = convertor_service

    async def get_emote(self, query: str, provider: EmoteProviders) -> Emote | None:
        '''Gets an emote from a database. Returns found Emote or None if specified emote does not exist.'''

        emote_entity = await self.database_repository.get_emote(query, provider)
        
        if emote_entity is None:
            return None

        emote = self.convertor_service.emote_entity_to_data(emote_entity)

        return emote
    
    async def cache_emote(self, emote: Emote, query: str, provider: EmoteProviders, url: str) -> None:
        '''Saves an emote in a database.'''

        emote_entity = self.convertor_service.emote_data_to_entity(emote, query, provider, url)

        await self.database_repository.save_emote(emote_entity)

    async def ban_user(self, user: int) -> None:
        '''Bans an user.'''

        user_entity = self.convertor_service.user_data_to_entity(user)

        await self.database_repository.ban_user(user_entity)

    async def unban_user(self, user: int) -> None:
        '''Unbans an user.'''

        user_entity = self.convertor_service.user_data_to_entity(user)

        await self.database_repository.unban_user(user_entity)

    async def get_banned_users(self) -> list[int]:
        '''Gets banned users.'''

        banned_users = await self.database_repository.list_banned_users()
        banned_users = [ user.id for user in banned_users ]

        return banned_users

    async def authorize_user(self, user: int) -> None:
        '''Authorizes an user.'''

        user_entity = self.convertor_service.user_data_to_entity(user)

        await self.database_repository.authorize_user(user_entity)

    async def unauthorize_user(self, user: int) -> None:
        '''Unauthorizes an user.'''

        user_entity = self.convertor_service.user_data_to_entity(user)

        await self.database_repository.unauthorize_user(user_entity)

    async def get_authorized_users(self) -> list[int]:
        '''Gets authorized users.'''

        authorized_users = await self.database_repository.list_authorized_users()
        authorized_users = [ user.id for user in authorized_users ]

        return authorized_users


database_service = DatabaseService(mongo_database_repository, convertor_service)
