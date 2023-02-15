from functools import wraps
from typing import Callable, Type, Union

from nextcord import TextChannel
from nextcord.ext import commands

from messages import Messages
from model.exception.bad_argument import BadArgument
from model.exception.banned import Banned
from model.exception.missing_argument import MissingArgument
from model.exception.no_new_messages import NoNewMessages
from model.exception.not_in_server import NotInServer
from service.api_wrapper_service import APIWrapperService
from service.embed_sender_service import EmbedSenderService, embed_sender_service
from service.markov_service import MarkovService, markov_service
from service.user_management_service import UserManagementService, user_management_service


class LearnCog(commands.Cog):
    '''Class representing the learn command. This starts the learning process on the specified channel,
    or updates the model on new messages.'''

    def __init__(
            self,
            aw: Type[APIWrapperService],
            ess: EmbedSenderService,
            ums: UserManagementService,
            ms: MarkovService) -> None:
        self.api_wrapper = aw
        self.embed_sender_service = ess
        self.user_management_service = ums
        self.markov_service = ms

    @staticmethod
    def checker(func: Callable) -> Callable:
        '''Decorator checking whether the learn command can be run.
        
        The command can be run if invoked in the server, the user provided a correct argument, and there are messages
        the bot can learn from.'''

        @wraps(func)
        async def decorator(self: 'LearnCog', ctx: commands.Context, *, channel: Union[TextChannel, str]):
            api = self.api_wrapper(ctx)

            try:
                await self.user_management_service.check_if_not_banned(api.get_author_id())

                api.check_if_author_in_server()

                if channel is ...:
                    raise MissingArgument
                
                if type(channel) is not TextChannel:
                    raise BadArgument

                await func(self, ctx, channel=channel)

            except Banned:
                pass

            except NotInServer:
                await self.embed_sender_service.send_error(ctx, Messages.AUTHOR_NOT_IN_SERVER)

            except MissingArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MISSING_ARGUMENTS)
            
            except BadArgument:
                await self.embed_sender_service.send_error(ctx, Messages.MARKOV_BAD_ARGUMENT)
        
            except NoNewMessages:
                await self.embed_sender_service.send_error(ctx, Messages.MARKOV_NO_NEW_MESSAGES)

        return decorator

    @commands.command(name='learn')
    @checker
    async def learn_command(self, ctx: commands.Context, *, channel: Union[TextChannel, str] = ...) -> None:
        '''Body of the command.'''

        number_of_messages = await self.markov_service.learn(channel)

        await self.embed_sender_service.send_success(ctx, Messages.FINISHED_LEARNING(number_of_messages))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(LearnCog(APIWrapperService, embed_sender_service, user_management_service, markov_service))
