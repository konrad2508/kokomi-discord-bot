from functools import wraps
from typing import Callable, Type

from nextcord.ext import commands

from messages import Messages
from model.exception.banned import Banned
from model.exception.music_queue_locked import MusicQueueLocked
from model.exception.not_in_server import NotInServer
from model.exception.not_yet_connected import NotYetConnected
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.music_player_service import MusicPlayerService, music_player_service
from service.user_management_service import UserManagementService, user_management_service


class LeaveCog(commands.Cog):
    '''Class representing the leave command. This command disconnects the bot from a voice channel.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService,
            mps: MusicPlayerService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums
        self.music_player_service = mps

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the leave command can be run.
        
        The command can be run if invoked in the server, the bot is connected to a voice channel,
        and the music queue is not locked.'''

        @wraps(func)
        async def decorator(self: 'LeaveCog', ctx: commands.Context, *args) -> None:
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_not_banned(api.get_author_id())

                api.check_if_author_in_server()
                self.music_player_service.check_if_connected(api.get_server_id())
                self.music_player_service.check_if_queue_not_locked(api.get_server_id())

                await func(self, ctx, api)
            
            except Banned:
                pass

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except NotYetConnected:
                await self.embed_sender_service.send_error(ctx, Messages.BOT_NOT_IN_VOICE_CHAT)

            except MusicQueueLocked:
                await self.embed_sender_service.send_error(ctx, Messages.MUSIC_QUEUE_IS_LOCKED)
        
        return decorator

    @commands.command(name='leave')
    @checker
    async def leave_command(self, ctx: commands.Context, api: APIWrapperService = ...) -> None:
        '''Body of the command.'''

        server_id = api.get_server_id()

        await self.music_player_service.disconnect(server_id)

        await self.embed_sender_service.send_success(ctx, Messages.BOT_LEFT_VOICE_CHAT)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(LeaveCog(APIWrapperService, embed_sender_service, user_management_service, music_player_service))
