from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands
from messages import Messages
from model.exception.in_server import InServer
from model.exception.not_owner import NotOwner

from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.user_management_service import UserManagementService, user_management_service


class ListauthorizedCog(commands.Cog):
    '''Class representing the listauthorized command. This command lists authorized users.'''

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
        '''Decorator checking whether the listauthorized command can be run.

        The command can be run if invoked in the private chat, and by an authorized user.'''

        @wraps(func)
        async def decorator(self: 'ListauthorizedCog', ctx: commands.Context) -> None:
            api = self.api_wrapper(ctx)

            try:
                self.user_management_service.check_if_owner(api.get_author_id())

                api.check_if_author_not_in_server()

                await func(self, ctx)

            except NotOwner:
                pass

            except InServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_IN_SERVER)

        return decorator

    @commands.command(name='listauthorized')
    @checker
    async def listauthorized_command(self, ctx: commands.Context) -> None:
        '''Body of the command.'''

        authorized_users = await self.user_management_service.get_authorized_users()

        await self.embed_sender_service.send_success(ctx, Messages.LIST_AUTHORIZED_USERS(authorized_users))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ListauthorizedCog(APIWrapperService, embed_sender_service, user_management_service))
