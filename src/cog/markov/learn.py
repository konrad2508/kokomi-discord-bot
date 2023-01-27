from functools import wraps
from typing import Callable, Type, Union

from nextcord import TextChannel
from nextcord.abc import GuildChannel
# from nextcord.abc import GuildChannel
from nextcord.ext import commands

from messages import Messages
from model.exception.missing_argument import MissingArgument
from model.exception.not_in_server import NotInServer
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.markov_service import MarkovService, markov_service


class LearnCog(commands.Cog):
    '''Class representing the learn command. This starts the learning process on the specified channel,
    or updates the model on new messages.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ms: MarkovService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.markov_service = ms

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the learn command can be run.
        
        The command can be run if invoked in the server, and the user has privileges to do so.'''

        @wraps(func)
        async def decorator(self: 'LearnCog', ctx: commands.Context, *, channel: Union[TextChannel, str]):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()

                if channel is ...:
                    raise MissingArgument
                
                if type(channel) is not TextChannel:
                    raise Exception

                await func(self, ctx, channel=channel)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)

        return decorator

    @commands.command(name='learn')
    @checker
    async def learn_command(self, ctx: commands.Context, *, channel: Union[TextChannel, str] = ...) -> None:
        '''Body of the command.'''

        await self.markov_service.learn(channel)

        await self.embed_sender_service.send_success(ctx, channel)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(LearnCog(APIWrapperService, embed_sender_service, markov_service))
