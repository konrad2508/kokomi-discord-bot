from config import Config
from model.exception.banned import Banned
from model.exception.not_authorized import NotAuthorized
from model.exception.not_bannable import NotBannable
from model.exception.not_owner import NotOwner
from model.exception.user_authorized import UserAuthorized
from model.exception.user_banned import UserBanned
from model.exception.user_not_authorized import UserNotAuthorized
from model.exception.user_not_banned import UserNotBanned
from service.database_service import DatabaseService


class UserManagementService:
    '''Class responsible for managing users.'''

    def __init__(self, conf: Config, ds: DatabaseService) -> None:
        self.owner: int = conf.owner
        self.database = ds

    async def ban_user(self, user: int) -> None:
        '''Bans the user.'''

        await self.database.ban_user(user)

    async def unban_user(self, user: int) -> None:
        '''Unbans the user.'''

        await self.database.unban_user(user)

    async def get_banned_users(self) -> list[int]:
        '''Returns banned users.'''

        banned_users = await self.database.get_banned_users()

        return banned_users

    async def authorize_user(self, user: int) -> None:
        '''Authorizes the user.'''

        await self.database.authorize_user(user)
    
    async def unauthorize_user(self, user: int) -> None:
        '''Unauthorizes the user.'''

        await self.database.unauthorize_user(user)

    async def get_authorized_users(self) -> list[int]:
        '''Returns authorized users.'''

        authorized_users = await self.database.get_authorized_users()

        return authorized_users

    async def check_if_authorized(self, user: int) -> None:
        '''Checks if the user is authorized. Throws NotAuthorized exception if not.'''

        authorized_users = await self.database.get_authorized_users()

        if user not in authorized_users and user != self.owner:
            raise NotAuthorized

    def check_if_owner(self, user: int) -> None:
        '''Checks if the user is the owner. Throws NotOwner exception if not.'''

        if user != self.owner:
            raise NotOwner

    async def check_if_not_banned(self, user: int) -> None:
        '''Checks if the user is not banned. Throws Banned exception if is.'''

        banned_users = await self.database.get_banned_users()

        if user in banned_users and user != self.owner:
            raise Banned

    async def check_if_user_bannable(self, user: int) -> None:
        '''Checks if the user can be banned. Throws NotBannable exception if not.'''

        authorized_users = await self.database.get_authorized_users()

        if user in authorized_users or user == self.owner:
            raise NotBannable

    async def check_if_user_not_banned(self, user: int) -> None:
        '''Checks if the user is not banned. Throws UserBanned exception if is.'''

        banned_users = await self.database.get_banned_users()

        if user in banned_users:
            raise UserBanned

    async def check_if_user_banned(self, user: int) -> None:
        '''Checks if the user is banned. Throws UserNotBanned exception if not.'''

        banned_users = await self.database.get_banned_users()

        if user not in banned_users:
            raise UserNotBanned
    
    async def check_if_user_not_authorized(self, user: int) -> None:
        '''Checks if the user is not authorized. Throws UserAuthorized exception if is.'''

        authorized_users = await self.database.get_authorized_users()

        if user in authorized_users:
            raise UserAuthorized

    async def check_if_user_authorized(self, user: int) -> None:
        '''Checks if the user is authorized. Throws UserNotAuthorized exception if not.'''

        authorized_users = await self.database.get_authorized_users()

        if user not in authorized_users:
            raise UserNotAuthorized
