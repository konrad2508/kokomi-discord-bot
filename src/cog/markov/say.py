from functools import wraps
from typing import Callable, Type, Union

from nextcord import TextChannel
from nextcord.ext import commands

from messages import Messages
from model.exception.bad_argument import BadArgument
from model.exception.channel_not_learned import ChannelNotLearned
from model.exception.missing_argument import MissingArgument
from model.exception.not_enough_data import NotEnoughData
from model.exception.not_in_server import NotInServer
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.markov_service import MarkovService, markov_service


class SayCog(commands.Cog):
    '''Class representing the say command. This generates a message based on previous messages sent on the specified
    channel, and sends it.'''

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
        '''Decorator checking whether the say command can be run.
        
        The command can be run if invoked in the server, the user provided a correct argument, .'''

        @wraps(func)
        async def decorator(self: 'SayCog', ctx: commands.Context, *, channel: Union[TextChannel, str]):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()

                if channel is ...:
                    raise MissingArgument
                
                if type(channel) is not TextChannel:
                    raise BadArgument

                await func(self, ctx, channel=channel)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except BadArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MARKOV_BAD_ARGUMENT)
            
            except ChannelNotLearned:
                await self.embed_sender_service.send_error(ctx, Messages.MARKOV_CHANNEL_NOT_LEARNED)
                
            except NotEnoughData:
                await self.embed_sender_service.send_error(ctx, Messages.MARKOV_NOT_ENOUGH_DATA)

        return decorator

    @commands.command(name='say')
    @checker
    async def say_command(self, ctx: commands.Context, *, channel: Union[TextChannel, str] = ...) -> None:
        '''Body of the command.'''

        msg = await self.markov_service.say(channel)

        await self.embed_sender_service.send_success(ctx, msg)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(SayCog(APIWrapperService, embed_sender_service, markov_service))
