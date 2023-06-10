from unittest.mock import MagicMock

from factory.standard_discord_bot_factory import StandardDiscordBotFactory
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'factory.standard_discord_bot_factory'


@tested_module(TEST_MODULE)
class StandardDiscordBotFactoryUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.bot_mock = self.patch('commands.Bot')
        self.bot_mock_obj = self.bot_mock.return_value

        self.cfg = MagicMock()
        self.obj = StandardDiscordBotFactory(self.cfg)

    def test_get_bot_returns_instance_of_bot(self) -> None:
        ret = self.obj.get_bot()

        self.assertEqual(ret, self.bot_mock_obj)

    def test_get_bot_returned_instance_received_correct_ctor_params(self) -> None:
        intents = self.patch('Intents').default.return_value

        self.obj.get_bot()

        self.bot_mock.assert_called_once_with(command_prefix=self.cfg.prefix, help_command=None, intents=intents)
        self.assertEqual(intents.message_content, True)

    def test_get_bot_loads_extensions_to_bot(self) -> None:
        self.obj.get_bot()

        self.bot_mock_obj.load_extension.assert_called()
