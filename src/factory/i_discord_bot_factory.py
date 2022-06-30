from abc import ABC, abstractmethod

from nextcord.ext import commands


class IDiscordBotFactory(ABC):
    '''Factory responsible for constructing and returning an instance of the bot.'''

    @abstractmethod
    def get_bot(self) -> commands.Bot:
        '''Returns an instance of the bot.'''
