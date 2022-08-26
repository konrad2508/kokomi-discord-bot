import unittest
from unittest.mock import MagicMock, patch

from factory.standard_discord_bot_factory import StandardDiscordBotFactory


class StandardDiscordBotFactoryUnitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.bot_ctor_mock = patch('factory.standard_discord_bot_factory.commands.Bot').start()
        self.bot_obj_mock = self.bot_ctor_mock.return_value

        self.cfg = MagicMock()
        self.obj = StandardDiscordBotFactory(self.cfg)
    
    def tearDown(self) -> None:
        patch.stopall()
    
    def test_get_bot_returns_instance_of_bot(self) -> None:
        ret = self.obj.get_bot()

        self.assertEqual(ret, self.bot_obj_mock)
    
    def test_get_bot_returned_instance_received_correct_ctor_params(self) -> None:
        self.obj.get_bot()

        self.bot_ctor_mock.assert_called_once_with(command_prefix=self.cfg.prefix, help_command=None)
    
    def test_get_bot_loads_extensions_to_bot(self) -> None:
        self.obj.get_bot()

        self.bot_obj_mock.load_extension.assert_called()

        calls = self.bot_obj_mock.load_extension.call_args_list
        for call in calls:
            print(call)
