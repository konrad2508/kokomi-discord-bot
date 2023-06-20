from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from composer import embed_sender_service, emote_service, user_management_service
from messages import Messages
from model.enum.emote_providers import EmoteProviders
from model.exception.banned import Banned
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.invalid_option import InvalidOption
from model.exception.missing_argument import MissingArgument
from model.exception.no_emote_results import NoEmoteResults
from model.exception.not_in_server import NotInServer
from model.exception.too_large_emote import TooLargeEmote
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.emote_service import EmoteService
from service.user_management_service import UserManagementService


class BttvCog(commands.Cog):
    '''Class representing the bttv command. This returns a bttv emote based on the user's input.
    First, the repository is checked whether the emote has already been cached and can be reused.
    If not, retrieves the emote from BTTV.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService,
            es: EmoteService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums
        self.emote_service = es

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the bttv command can be run.
        
        The command can be run if invoked in the server, and the user provided an argument
        to the command.'''

        @wraps(func)
        async def decorator(self: 'BttvCog', ctx: commands.Context, *, query: str):
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_not_banned(api.get_author_id())

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

            except Banned:
                pass

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

    @commands.command(name='bttv')
    @checker
    async def emote_command(self, ctx: commands.Context, *, query: str = ..., use_raw: bool = ...) -> None:
        '''Body of the command.'''

        emote = await self.emote_service.get_emote(query, EmoteProviders.BTTV, use_raw)

        await self.embed_sender_service.send_emote(ctx, emote)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(BttvCog(APIWrapperService, embed_sender_service, user_management_service, emote_service))
