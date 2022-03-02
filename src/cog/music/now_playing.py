from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.no_song_playing import NoSongPlaying
from model.exception.not_in_server import NotInServer
from model.exception.not_yet_connected import NotYetConnected
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.music_player_service import MusicPlayerService, music_player_service


class NowPlayingCog(commands.Cog):
    '''Class representing the now playing command. This command sends a message containing information about
    the currently playing song.'''

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
        '''Decorator checking whether the now playing command can be run.
        
        The command can be run if invoked in the server, the bot is connected to a voice channel,
        and a song is being played.'''

        @wraps(func)
        async def decorator(self: 'NowPlayingCog', ctx: commands.Context, *args):
            api = self.api_wrapper(ctx)

            try:
                api.check_if_author_in_server()
                self.music_player_service.check_if_connected(api.get_server_id())
                self.music_player_service.check_if_song_playing(api.get_server_id())

                await func(self, ctx, api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotYetConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_NOT_IN_VOICE_CHAT)
            
            except NoSongPlaying:
                await self.embed_sender_service.send_error(ctx, Messages.NO_SONG_PLAYING)

        return decorator

    @commands.command(name='nowplaying', aliases=['np'])
    @checker
    async def now_playing_command(self, ctx: commands.Context, api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()
        
        currently_playing = self.music_player_service.now_playing(server_id)

        await self.embed_sender_service.send_success(ctx, Messages.CURRENTLY_PLAYING(currently_playing))

def setup(bot: commands.Bot) -> None:
    bot.add_cog(NowPlayingCog(APIWrapperService, embed_sender_service, music_player_service))
