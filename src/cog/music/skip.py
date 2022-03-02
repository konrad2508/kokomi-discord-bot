from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.no_song_playing import NoSongPlaying
from model.exception.not_in_server import NotInServer
from model.exception.not_yet_connected import NotYetConnected
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.music_player_service import MusicPlayerService, music_player_service


class SkipCog(commands.Cog):
    '''Class representing the skip command. This command skips the currently playing song.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            mps: MusicPlayerService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.music_player_service = mps

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the skip command can be run.
        
        The command can be run if invoked in the server, the bot is connected to a voice channel,
        the music queue is not locked, and a song is being played.'''

        @wraps(func)
        async def decorator(self: 'SkipCog', ctx: commands.Context, *args):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()
                self.music_player_service.check_if_connected(api.get_server_id())
                self.music_player_service.check_if_queue_not_locked(api.get_server_id())
                self.music_player_service.check_if_song_playing(api.get_server_id())

                await func(self, ctx, api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotYetConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_NOT_IN_VOICE_CHAT)
            
            except MusicQueueLocked:
                await self.embed_sender_service.send_error(ctx, Messages.MUSIC_QUEUE_IS_LOCKED)

            except NoSongPlaying:
                await self.embed_sender_service.send_error(ctx, Messages.NO_SONG_PLAYING)

        return decorator

    @commands.command(name='skip', aliases=['s'])
    @checker
    async def skip_command(self, ctx: commands.Context, api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()

        self.music_player_service.skip(server_id)

        await self.embed_sender_service.send_success(ctx, Messages.SKIPPED_SONG)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(SkipCog(APIWrapperService, embed_sender_service, music_player_service))
