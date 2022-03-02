from nextcord import VoiceChannel
from nextcord.ext import commands

from model.exception.not_in_server import NotInServer
from model.exception.not_in_voice_chat import NotInVoiceChat


class APIWrapperService:
    '''Class that serves as an API wrapper of Nextcord.'''

    def __init__(self, ctx: commands.Context) -> None:
        self.ctx = ctx

    def check_if_author_in_server(self) -> None:
        '''Checks if the author's message is in a server. Throws NotInServer exception
        if it is not.'''

        if not self.ctx.message.guild:
            raise NotInServer

    def check_if_author_in_vc(self) -> None:
        '''Checks if the message's author is in a voice channel. Throws NotInVoiceChat exception
        if is not.'''

        if not self.ctx.message.author.voice:
            raise NotInVoiceChat

    def get_server_id(self) -> int:
        '''Returns the ID of a server.'''

        return self.ctx.message.guild.id

    def get_author_vc(self) -> VoiceChannel:
        '''Returns a reference to the author's voice channel.'''

        return self.ctx.message.author.voice.channel
