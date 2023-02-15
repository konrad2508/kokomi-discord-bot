from abc import ABC, abstractmethod

from model.entity.emote_entity import EmoteEntity
from model.entity.user_entity import UserEntity
from model.enum.emote_providers import EmoteProviders


class IDatabaseRepository(ABC):
    '''Class responsible for accessing the database.'''

    @abstractmethod
    async def get_emote(self, query: str, provider: EmoteProviders) -> EmoteEntity | None:
        '''Gets an emote from the database. Returns EmoteEntity if an emote was found, None otherwise.'''

    @abstractmethod
    async def save_emote(self, emote: EmoteEntity) -> EmoteEntity:
        '''Saves an emote in the database. Returns the saved emote.'''
    
    @abstractmethod
    async def ban_user(self, user: UserEntity) -> UserEntity:
        '''Bans an user and saves its data in the database. Returns the banned user.'''
    
    @abstractmethod
    async def unban_user(self, user: UserEntity) -> UserEntity:
        '''Unbans an user and removes its data from the database. Returns the unbanned user.'''
    
    @abstractmethod
    async def list_banned_users(self) -> list[UserEntity]:
        '''Lists banned users present in the database. Returns the list of banned users.'''
    
    @abstractmethod
    async def authorize_user(self, user: UserEntity) -> UserEntity:
        '''Authorizes an user and saves its data in the database. Returns the authorized user.'''
    
    @abstractmethod
    async def unauthorize_user(self, user: UserEntity) -> UserEntity:
        '''Unauthorizes an user and removes its data from the database. Returns the unauthorized user.'''
    
    @abstractmethod
    async def list_authorized_users(self) -> list[UserEntity]:
        '''Lists authorized users present in the database. Returns the list of authorized users.'''
