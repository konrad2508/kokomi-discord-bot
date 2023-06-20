from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from composer import embed_sender_service, gif_service, user_management_service
from messages import Messages
from model.exception.banned import Banned
from model.exception.gif_fetch_error import GifFetchError
from model.exception.missing_argument import MissingArgument
from model.exception.no_gif_results import NoGifResults
from model.exception.not_in_server import NotInServer
from model.exception.query_too_long import QueryTooLong
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.gif_service import GifService
from service.user_management_service import UserManagementService


class GifCog(commands.Cog):
    '''Class representing the gif command. This command returns a GIF based on the user's input.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService,
            gs: GifService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums
        self.gif_service = gs

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the gif command can be run.
        
        The command can be run if invoked in the server, and the user provided an argument
        to the command.'''

        @wraps(func)
        async def decorator(self: 'GifCog', ctx: commands.Context, *, query: str):
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_not_banned(api.get_author_id())

                api.check_if_author_in_server()

                if query is ...:
                    raise MissingArgument

                if len(query) > 256:
                    raise QueryTooLong

                await func(self, ctx, query=query, api=api)

            except Banned:
                pass

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except NoGifResults:
                await self.embed_sender_service.send_error(ctx, Messages.NO_GIFS_FOUND(query))
            
            except GifFetchError:
                await self.embed_sender_service.send_error(ctx, Messages.ERROR_FETCHING_GIFS)
            
            except QueryTooLong:
                await self.embed_sender_service.send_error(ctx, Messages.QUERY_TOO_LONG)

        return decorator

    @commands.command(name='gif')
    @checker
    async def gif_command(self, ctx: commands.Context, *, query: str = ..., api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        gif = await self.gif_service.get_random_gif(query)

        await self.embed_sender_service.send_gif(ctx, gif)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GifCog(APIWrapperService, embed_sender_service, user_management_service, gif_service))
