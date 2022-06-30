from nextcord.ext import commands

from config import Config
from factory.i_discord_bot_factory import IDiscordBotFactory


class StandardDiscordBotFactory(IDiscordBotFactory):
    '''Factory responsible for constructing and returning a standard, used in production, instance of the bot.'''

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
    
    def get_bot(self) -> commands.Bot:
        bot = commands.Bot(command_prefix=self.cfg.prefix, help_command=None)

        for extension in self._get_extensions():
            bot.load_extension(extension)

        return bot

    def _get_extensions(self) -> list[str]:
        extensions = [
            'cog.core.help',
            'cog.music.join',
            'cog.music.leave',
            'cog.music.play',
            'cog.music.now_playing',
            'cog.music.skip',
            'cog.music.queue',
            'cog.music.loop',
            'cog.music.purge',
            'cog.reaction.gif',
            'cog.reaction.7tv',
            'cog.reaction.bttv'
        ]

        return extensions
