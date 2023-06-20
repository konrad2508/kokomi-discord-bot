from functools import wraps
from typing import Callable, Type, Union

from nextcord.ext import commands

from composer import embed_sender_service, user_management_service
from messages import Messages
from model.exception.bad_argument import BadArgument
from model.exception.in_server import InServer
from model.exception.missing_argument import MissingArgument
from model.exception.not_authorized import NotAuthorized
from model.exception.not_bannable import NotBannable
from model.exception.user_banned import UserBanned
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.user_management_service import UserManagementService


class BanCog(commands.Cog):
    '''Class representing the ban command. This command bans an user from using the bot.'''

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
        '''Decorator checking whether the ban command can be run.

        The command can be run if invoked in the private chat, by an authorized user, and only if the user to-be-banned
        is not banned and can be banned.'''

        @wraps(func)
        async def decorator(self: 'BanCog', ctx: commands.Context, *, user: Union[int, str]) -> None:
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_authorized(api.get_author_id())

                api.check_if_author_not_in_server()

                if user is ...:
                    raise MissingArgument

                if type(user) is not int:
                    raise BadArgument

                await self.user_management_service.check_if_user_bannable(user)

                await self.user_management_service.check_if_user_not_banned(user)

                await func(self, ctx, user=user)

            except NotAuthorized:
                pass

            except InServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_IN_SERVER)

            except NotBannable:
                await self.embed_sender_service.send_error(ctx, Messages.USER_NOT_BANNABLE)

            except UserBanned:
                await self.embed_sender_service.send_error(ctx, Messages.USER_BANNED)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)

            except BadArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_USER_ID)

        return decorator

    @commands.command(name='ban')
    @checker
    async def ban_command(self, ctx: commands.Context, *, user: Union[int, str] = ...) -> None:
        '''Body of the command.'''

        await self.user_management_service.ban_user(user)

        await self.embed_sender_service.send_success(ctx, Messages.USER_SUCCESSFULLY_BANNED)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(BanCog(APIWrapperService, embed_sender_service, user_management_service))
