from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from composer import embed_sender_service, user_management_service
from messages import Messages
from model.exception.in_server import InServer
from model.exception.not_authorized import NotAuthorized
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.user_management_service import UserManagementService


class ListbansCog(commands.Cog):
    '''Class representing the listbans command. This command lists banned users.'''

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
        '''Decorator checking whether the listbans command can be run.

        The command can be run if invoked in the private chat, and by an authorized user.'''

        @wraps(func)
        async def decorator(self: 'ListbansCog', ctx: commands.Context) -> None:
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_authorized(api.get_author_id())

                api.check_if_author_not_in_server()

                await func(self, ctx)

            except NotAuthorized:
                pass

            except InServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_IN_SERVER)

        return decorator

    @commands.command(name='listbans')
    @checker
    async def listbans_command(self, ctx: commands.Context) -> None:
        '''Body of the command.'''

        banned_users = await self.user_management_service.get_banned_users()

        await self.embed_sender_service.send_success(ctx, Messages.LIST_BANNED_USERS(banned_users))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ListbansCog(APIWrapperService, embed_sender_service, user_management_service))
