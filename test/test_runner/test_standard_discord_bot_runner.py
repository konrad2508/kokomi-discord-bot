from typing import Callable
from unittest.mock import MagicMock, AsyncMock

from runner.standard_discord_bot_runner import StandardDiscordBotRunner
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'runner.standard_discord_bot_runner'


@tested_module(TEST_MODULE)
class StandardDiscordBotRunnerCtorUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.factory_mock = MagicMock()

    def test_ctor_gets_bot_instance_from_factory(self) -> None:
        StandardDiscordBotRunner(None, self.factory_mock)

        self.factory_mock.get_bot.assert_called_once()


@tested_module(TEST_MODULE)
class StandardDiscordBotRunnerUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.cfg_mock = MagicMock()
        self.factory_mock = MagicMock()

        self.obj = StandardDiscordBotRunner(self.cfg_mock, self.factory_mock)
    
    def test_run_correctly_runs_bot(self) -> None:
        self.obj.run()

        self.factory_mock.get_bot.return_value.run.assert_called_once_with(self.cfg_mock.token, reconnect=True)

    def test_run_sets_callback_for_on_ready_event(self) -> None:
        self.obj.run()

        self.assertIsInstance(self.factory_mock.get_bot.return_value.event.call_args[0][0], Callable)
        self.assertEqual(self.factory_mock.get_bot.return_value.event.call_args[0][0].__name__, 'on_ready')

    async def test_run_on_ready_callback_uses_logging(self) -> None:
        nextcord_mock = self.patch('nextcord')
        nextcord_mock.__version__ = ''
        logging_mock = self.patch('logging')
        self.factory_mock.get_bot.return_value.change_presence = AsyncMock()

        self.obj.run()
        callback = self.factory_mock.get_bot.return_value.event.call_args[0][0]
        await callback()

        logging_mock.info.assert_called()
    
    async def test_run_on_ready_callback_sets_presence_to_gaming_activity(self) -> None:
        nextcord_mock = self.patch('nextcord')
        nextcord_mock.__version__ = ''
        self.patch('logging')
        self.factory_mock.get_bot.return_value.change_presence = AsyncMock()

        self.obj.run()
        callback = self.factory_mock.get_bot.return_value.event.call_args[0][0]
        await callback()

        nextcord_mock.Game.assert_called_once()
        self.factory_mock.get_bot.return_value.change_presence.assert_called_once_with(activity=nextcord_mock.Game.return_value)
