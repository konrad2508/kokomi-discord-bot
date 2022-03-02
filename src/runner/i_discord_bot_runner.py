from abc import ABC, abstractmethod


class IDiscordBotRunner(ABC):
    '''Class responsible for running the bot.'''

    @abstractmethod
    def run(self) -> None:
        '''Runs the bot.'''
