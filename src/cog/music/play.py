from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from composer import embed_sender_service, music_player_service, user_management_service
from messages import Messages
from model.exception.banned import Banned
from model.exception.cannot_add_playlist import CannotAddPlaylist
from model.exception.invalid_option import InvalidOption
from model.exception.missing_argument import MissingArgument
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.not_in_server import NotInServer
from model.exception.not_yet_connected import NotYetConnected
from model.exception.playlist_is_song import PlaylistIsSong
from model.exception.playlist_source_not_supported import PlaylistSourceNotSupported
from model.exception.song_is_playlist import SongIsPlaylist
from model.exception.unsupported_source import UnsupportedSource
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService
from service.music_player_service import MusicPlayerService
from service.user_management_service import UserManagementService


class PlayCog(commands.Cog):
    '''Class representing the play command. This command uses the argument provided by the user (either a direct url or a query)
    to find and play the song in a voice channel.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService,
            mps: MusicPlayerService,
            bot: commands.Bot) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums
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
                await self.user_management_service.check_if_not_banned(api.get_author_id())

                api.check_if_author_in_server()
                self.music_player_service.check_if_connected(api.get_server_id())
                self.music_player_service.check_if_queue_not_locked(api.get_server_id())
                
                if text is ...:
                    raise MissingArgument

                splitted_query = text.split(' ')
                opts = {
                    'use_playlist': '--playlist'
                }

                if splitted_query[0].startswith('--') and splitted_query[0] not in opts.values():
                    raise InvalidOption

                use_playlist = splitted_query[0] == opts['use_playlist']

                await func(self, ctx, text=text, api=api, use_playlist=use_playlist)

            except Banned:
                pass

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotYetConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_NOT_IN_VOICE_CHAT)

            except MusicQueueLocked:
                await self.embed_sender_service.send_error(ctx, Messages.MUSIC_QUEUE_IS_LOCKED)
            
            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except UnsupportedSource:
                await self.embed_sender_service.send_error(ctx, Messages.UNSUPPORTED_SONG_SOURCE)
            
            except SongIsPlaylist:
                await self.embed_sender_service.send_error(ctx, Messages.SONG_IS_PLAYLIST)
            
            except PlaylistIsSong:
                await self.embed_sender_service.send_error(ctx, Messages.PLAYLIST_IS_SONG)

            except PlaylistSourceNotSupported:
                await self.embed_sender_service.send_error(ctx, Messages.UNSUPPORTED_PLAYLIST_SOURCE)
            
            except CannotAddPlaylist:
                await self.embed_sender_service.send_error(ctx, Messages.CANNOT_ADD_PLAYLIST)

        return decorator

    @commands.command(name='play', aliases=['p'])
    @checker
    async def play_command(self, ctx: commands.Context, *, text: str = ..., api: APIWrapperService = ..., use_playlist: bool) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()
        
        await self.music_player_service.play(
            server_id,
            lambda t, u: self.embed_sender_service.send_success(ctx, Messages.ADDED_SONG(t, u)),
            lambda c: self.embed_sender_service.send_success(ctx, Messages.ADDED_PLAYLIST(c)),
            lambda t, u: self.embed_sender_service.send_success(ctx, Messages.PLAYING_SONG(t, u)),
            lambda: self.embed_sender_service.send_success(ctx, Messages.QUEUE_ENDED),
            self.bot.loop,
            text,
            use_playlist
        )

def setup(bot: commands.Bot) -> None:
    bot.add_cog(PlayCog(APIWrapperService, embed_sender_service, user_management_service, music_player_service, bot))
