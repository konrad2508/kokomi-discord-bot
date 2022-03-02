import logging

import nextcord

from config import Config
from factory.i_discord_bot_factory import IDiscordBotFactory
from runner.i_discord_bot_runner import IDiscordBotRunner


class StandardDiscordBotRunner(IDiscordBotRunner):
    '''Class responsible for running the standard, used in production, bot.'''

    def __init__(self, cfg: Config, fac: IDiscordBotFactory) -> None:
        self.cfg = cfg
        self.extensions = fac.get_extensions()
        self.bot = fac.get_bot()

    def run(self) -> None:
        @self.bot.event
        async def on_ready() -> None:
            if self.bot.user is not None:
                logging.info(f'logged in as {self.bot.user.name} - {self.bot.user.id}')
                logging.info(f'nextcord version {nextcord.__version__}')

            await self.bot.change_presence(activity=nextcord.Game(name=f'{self.bot.command_prefix}help'))

        for extension in self.extensions:
            self.bot.load_extension(extension)

        self.bot.run(self.cfg.token, reconnect=True)
