from functools import wraps
from typing import Callable, Type, Union

from nextcord.ext import commands

from composer import embed_sender_service, user_management_service
from messages import Messages
from model.exception.bad_argument import BadArgument
from model.exception.in_server import InServer
from model.exception.missing_argument import MissingArgument
from model.exception.not_owner import NotOwner
from model.exception.user_authorized import UserAuthorized
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.user_management_service import UserManagementService


class AuthorizeCog(commands.Cog):
    '''Class representing the authorize command. This command promotes an user to an authorized user.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the authorize command can be run.

        The command can be run if invoked in the private chat, by an authorized user, and only if the user to-be-authorized
        is not authorized.'''

        @wraps(func)
        async def decorator(self: 'AuthorizeCog', ctx: commands.Context, *, user: Union[int, str]) -> None:
            api = self.api_wrapper(ctx)

            try:
                self.user_management_service.check_if_owner(api.get_author_id())

                api.check_if_author_not_in_server()

                if user is ...:
                    raise MissingArgument

                if type(user) is not int:
                    raise BadArgument

                await self.user_management_service.check_if_user_not_authorized(user)

                await func(self, ctx, user=user)

            except NotOwner:
                pass

            except InServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_IN_SERVER)
            
            except UserAuthorized:
                await self.embed_sender_service.send_error(ctx, Messages.USER_AUTHORIZED)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except BadArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_USER_ID)

        return decorator

    @commands.command(name='authorize')
    @checker
    async def authorize_command(self, ctx: commands.Context, *, user: Union[int, str] = ...) -> None:
        '''Body of the command.'''

        await self.user_management_service.authorize_user(user)

        await self.embed_sender_service.send_success(ctx, Messages.USER_SUCCESSFULLY_AUTHORIZED)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AuthorizeCog(APIWrapperService, embed_sender_service, user_management_service))
