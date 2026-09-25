import logging

from composer import conf
from factory.standard_discord_bot_factory import StandardDiscordBotFactory
from runner.hosted_discord_bot_runner import HostedDiscordBotRunner
from runner.standard_discord_bot_runner import StandardDiscordBotRunner


class App:
    '''Entry point of the program.'''

    def start(self) -> None:
        '''Starts the program.'''

        fac = StandardDiscordBotFactory(conf)
        runner = HostedDiscordBotRunner if conf.run_webserver else StandardDiscordBotRunner

        runner(conf, fac).run()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s,%(levelname)s,%(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        force=True
    )

    App().start()
