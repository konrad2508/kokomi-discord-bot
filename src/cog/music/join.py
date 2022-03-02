from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.already_connected import AlreadyConnected
from model.exception.not_in_server import NotInServer
from model.exception.not_in_voice_chat import NotInVoiceChat
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.music_player_service import MusicPlayerService, music_player_service


class JoinCog(commands.Cog):
    '''Class representing the join command. This command connects the bot to a voice channel.'''

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
        '''Decorator checking whether the join command can be run.
        
        The command can be run if invoked in the server, the author is in a voice channel,
        and the bot is not already connected to any voice channel in the server.'''
        
        @wraps(func)
        async def decorator(self: 'JoinCog', ctx: commands.Context, *args) -> None:
            api = self.api_wrapper(ctx)
            
            try:
                api.check_if_author_in_server()
                api.check_if_author_in_vc()
                self.music_player_service.check_if_not_connected(api.get_server_id())

                await func(self, ctx, api)

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotInVoiceChat:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_VOICE_CHAT)

            except AlreadyConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_ALREADY_IN_VOICE_CHAT)
        
        return decorator

    @commands.command(name='join')
    @checker
    async def join_command(self, ctx: commands.Context, api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()
        voice_channel = api.get_author_vc()
        
        await self.music_player_service.connect(server_id, voice_channel)

        await self.embed_sender_service.send_success(ctx, Messages.BOT_JOINED_VOICE_CHAT)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(JoinCog(APIWrapperService, embed_sender_service, music_player_service))
