from unittest.mock import MagicMock

from model.exception.in_server import InServer
from model.exception.not_in_server import NotInServer
from model.exception.not_in_voice_chat import NotInVoiceChat
from service.api_wrapper_service import APIWrapperService
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'service.api_wrapper_service'


@tested_module(TEST_MODULE)
class APIWrapperServiceUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.ctx_mock = MagicMock()

        self.obj = APIWrapperService(self.ctx_mock)
    
    def test_check_if_author_in_server_throws_exception_if_not(self) -> None:
        self.ctx_mock.message.guild = None

        self.assertRaises(NotInServer, self.obj.check_if_author_in_server)
    
    def test_check_if_author_in_server_doesnt_throw_exception_if_is(self) -> None:
        self.ctx_mock.message.guild = 'server'

        self.assertNotRaises(NotInServer, self.obj.check_if_author_in_server)

    def test_check_if_author_not_in_server_throws_exception_if_is(self) -> None:
        self.ctx_mock.message.guild = 'server'

        self.assertRaises(InServer, self.obj.check_if_author_not_in_server)
    
    def test_check_if_author_not_in_server_doesnt_throw_exception_if_not(self) -> None:
        self.ctx_mock.message.guild = None

        self.assertNotRaises(InServer, self.obj.check_if_author_not_in_server)
    
    def test_check_if_author_in_vc_throws_exception_if_not(self) -> None:
        self.ctx_mock.message.author.voice = None

        self.assertRaises(NotInVoiceChat, self.obj.check_if_author_in_vc)
    
    def test_check_if_author_in_vc_doesnt_throw_exception_if_is(self) -> None:
        self.ctx_mock.message.author.voice = 'voice'

        self.assertNotRaises(NotInVoiceChat, self.obj.check_if_author_in_vc)
    
    def test_get_author_id_correctly_returns_id(self) -> None:
        self.ctx_mock.message.author.id = 25

        ret = self.obj.get_author_id()

        self.assertEqual(ret, 25)
    
    def test_get_server_id_correctly_returns_id(self) -> None:
        self.ctx_mock.message.guild.id = 56

        ret = self.obj.get_server_id()

        self.assertEqual(ret, 56)
    
    def test_get_author_vc_correctly_returns_channel(self) -> None:
        self.ctx_mock.message.author.voice.channel = 'a voice channel'

        ret = self.obj.get_author_vc()

        self.assertEqual(ret, 'a voice channel')
