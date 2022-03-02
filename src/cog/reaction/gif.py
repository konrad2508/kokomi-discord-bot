from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.gif_fetch_error import GifFetchError
from model.exception.missing_argument import MissingArgument
from model.exception.no_gif_results import NoGifResults
from model.exception.not_in_server import NotInServer
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.gif_service import GifService, gif_service


class GifCog(commands.Cog):
    '''Class representing the skip command. This command skips the currently playing song.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            gs: GifService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
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
                api.check_if_author_in_server()

                if query is ...:
                    raise MissingArgument

                await func(self, ctx, query=query, api=api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except NoGifResults:
                await self.embed_sender_service.send_error(ctx, Messages.NO_GIFS_FOUND(query))
            
            except GifFetchError:
                await self.embed_sender_service.send_error(ctx, Messages.ERROR_FETCHING_GIFS)

        return decorator

    @commands.command(name='gif')
    @checker
    async def gif_command(self, ctx: commands.Context, *, query: str = ..., api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        gif = await self.gif_service.get_random_gif(query)

        await self.embed_sender_service.send_gif(ctx, gif)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GifCog(APIWrapperService, embed_sender_service, gif_service))
