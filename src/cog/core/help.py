from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands
from messages import Messages

from model.exception.not_in_server import NotInServer
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service


class HelpCog(commands.Cog):
    '''Class representing the help command. This command returns a message containing information about using the bot.'''

    def __init__(self, aw: Type[APIWrapperService], ess: EmbedSenderService, bot: commands.Bot) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.bot = bot

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the help command can be run.
        
        The command can be run if invoked in the server.'''

        @wraps(func)
        async def decorator(self: 'HelpCog', ctx: commands.Context) -> None:
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()

                await func(self, ctx)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

        return decorator

    @commands.command(name='help', aliases=['h'])
    @checker
    async def help_command(self, ctx: commands.Context) -> None:
        '''Body of the command.'''

        commands = Messages.HELP(self.bot.command_prefix)

        await self.embed_sender_service.send_help(ctx, commands)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(HelpCog(APIWrapperService, embed_sender_service, bot))
