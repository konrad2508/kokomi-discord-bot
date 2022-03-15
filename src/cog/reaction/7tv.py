from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.enum.emote_providers import EmoteProviders
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.invalid_option import InvalidOption
from model.exception.missing_argument import MissingArgument
from model.exception.no_emote_results import NoEmoteResults
from model.exception.not_in_server import NotInServer
from model.exception.too_large_emote import TooLargeEmote
from service.api_wrapper_service import APIWrapperService
from service.database_service import DatabaseService, database_service
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.emote_service import EmoteService, emote_service


class SeventvCog(commands.Cog):
    '''Class representing the 7tv command. This returns a 7TV emote based on the user's input.
    First, the repository is checked whether the emote has already been cached and can be reused.
    If not, retrieves the emote from 7TV.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            es: EmoteService,
            ds: DatabaseService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.emote_service = es
        self.database_service = ds

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the 7tv command can be run.
        
        The command can be run if invoked in the server, and the user provided an argument
        to the command.'''

        @wraps(func)
        async def decorator(self: 'SeventvCog', ctx: commands.Context, *, query: str):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()

                if query is ...:
                    raise MissingArgument

                splitted_query = query.split(' ')
                opts = {
                    'use_raw': '--raw'
                }

                if splitted_query[0].startswith('--') and splitted_query[0] not in opts.values():
                    raise InvalidOption

                use_raw = splitted_query[0] == opts['use_raw']

                await func(self, ctx, query=query, use_raw=use_raw)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except NoEmoteResults:
                await self.embed_sender_service.send_error(ctx, Messages.NO_EMOTES_FOUND(query))
            
            except EmoteFetchError:
                await self.embed_sender_service.send_error(ctx, Messages.ERROR_FETCHING_EMOTES)
            
            except TooLargeEmote:
                await self.embed_sender_service.send_error(ctx, Messages.EMOTE_TOO_LARGE)
            
            except InvalidOption:
                await self.embed_sender_service.send_error(ctx, Messages.INVALID_OPTION)

        return decorator

    @commands.command(name='7tv')
    @checker
    async def emote_command(self, ctx: commands.Context, *, query: str = ..., use_raw: bool = ...) -> None:
        '''Body of the command.'''

        possible_emote = await self.database_service.get_emote(query, EmoteProviders.SEVENTV)

        if possible_emote is not None:
            await self.embed_sender_service.send_emote(ctx, possible_emote)

        else:
            emote = await self.emote_service.get_emote(query, EmoteProviders.SEVENTV, use_raw)

            uploaded_url = await self.embed_sender_service.send_emote(ctx, emote)

            await self.database_service.cache_emote(emote, query, EmoteProviders.SEVENTV, uploaded_url)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(SeventvCog(APIWrapperService, embed_sender_service, emote_service, database_service))
