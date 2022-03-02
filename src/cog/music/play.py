from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.missing_argument import MissingArgument
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.not_in_server import NotInServer
from model.exception.not_yet_connected import NotYetConnected
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.music_player_service import MusicPlayerService, music_player_service


class PlayCog(commands.Cog):
    '''Class representing the play command. This command uses the argument provided by the user (either a direct url or a query)
    to find and play the song in a voice channel.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            mps: MusicPlayerService,
            bot: commands.Bot) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.music_player_service = mps
        self.bot = bot

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the play command can be run.
        
        The command can be run if invoked in the server, the bot is connected to a voice channel,
        the music queue is not locked, and the user provided an argument to the command.'''

        @wraps(func)
        async def decorator(self: 'PlayCog', ctx: commands.Context, *, text: str):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()
                self.music_player_service.check_if_connected(api.get_server_id())
                self.music_player_service.check_if_queue_not_locked(api.get_server_id())
                
                if text is ...:
                    raise MissingArgument

                await func(self, ctx, text=text, api=api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotYetConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_NOT_IN_VOICE_CHAT)

            except MusicQueueLocked:
                await self.embed_sender_service.send_error(ctx, Messages.MUSIC_QUEUE_IS_LOCKED)
            
            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)

        return decorator

    @commands.command(name='play', aliases=['p'])
    @checker
    async def play_command(self, ctx: commands.Context, *, text: str = ..., api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()
        
        await self.music_player_service.play(
            server_id,
            lambda t, u: self.embed_sender_service.send_success(ctx, Messages.ADDED_SONG(t, u)),
            lambda t, u: self.embed_sender_service.send_success(ctx, Messages.PLAYING_SONG(t, u)),
            lambda: self.embed_sender_service.send_success(ctx, Messages.QUEUE_ENDED),
            self.bot.loop,
            text
        )

def setup(bot: commands.Bot) -> None:
    bot.add_cog(PlayCog(APIWrapperService, embed_sender_service, music_player_service, bot))
