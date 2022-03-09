from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.enum.emote_providers import EmoteProviders
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.missing_argument import MissingArgument
from model.exception.no_emote_results import NoEmoteResults
from model.exception.not_in_server import NotInServer
from model.exception.too_large_emote import TooLargeEmote
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.emote_service import EmoteService, emote_service


class SevenTVCog(commands.Cog):
    '''Class representing the 7tv command. This returns a 7TV emote based on the user's input.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            es: EmoteService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.emote_service = es

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the 7tv command can be run.
        
        The command can be run if invoked in the server, and the user provided an argument
        to the command.'''

        @wraps(func)
        async def decorator(self: 'SevenTVCog', ctx: commands.Context, *, query: str):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()

                if query is ...:
                    raise MissingArgument

                await func(self, ctx, query=query, api=api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except NoEmoteResults:
                await self.embed_sender_service.send_error(ctx, Messages.NO_EMOTES_FOUND(query))
            
            except EmoteFetchError:
                await self.embed_sender_service.send_error(ctx, Messages.ERROR_FETCHING_EMOTES)
            
            except TooLargeEmote:
                await self.embed_sender_service.send_error(ctx, 'Requested emote is too large')

        return decorator

    @commands.command(name='7tv')
    @checker
    async def emote_command(self, ctx: commands.Context, *, query: str = ..., api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        emote = await self.emote_service.get_emote(query, EmoteProviders.SEVENTV)

        await self.embed_sender_service.send_emote(ctx, emote)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(SevenTVCog(APIWrapperService, embed_sender_service, emote_service))
