from unittest.mock import MagicMock

from repository.mongo_database_repository import MongoDatabaseRepository
from utils.test_utils import TestCase, tested_module


TEST_MODULE = 'repository.mongo_database_repository'


@tested_module(TEST_MODULE)
class MongoDatabaseRepositoryUnitTestCase(TestCase):
    def setUp(self) -> None:
        cfg = MagicMock()
        cfg.database_name = 'db name'
        cfg.database_emote_collection_name = 'db emote col name'
        cfg.database_banned_user_collection_name = 'db ban usr col name'
        cfg.database_authorized_user_collection_name = 'db auth usr col name'

        self.emote_collection_mock = MagicMock()
        self.banned_user_collection_mock = MagicMock()
        self.authorized_user_collection_mock = MagicMock()
        self.patch('pymongo').MongoClient.return_value = {
            'db name': {
                'db emote col name': self.emote_collection_mock,
                'db ban usr col name': self.banned_user_collection_mock,
                'db auth usr col name': self.authorized_user_collection_mock
            }
        }

        self.obj = MongoDatabaseRepository(cfg)

    async def test_get_emote_formulates_correct_database_query(self) -> None:
        provider = MagicMock()
        self.emote_collection_mock.find_one.return_value = None

        await self.obj.get_emote('a query', provider)

        provider.encode.assert_called_once()
        self.emote_collection_mock.find_one.assert_called_once_with(
            { 'query': 'a query', 'provider': provider.encode.return_value }
        )

    async def test_get_emote_returns_none_if_emote_not_found(self) -> None:
        self.emote_collection_mock.find_one.return_value = None

        ret = await self.obj.get_emote(None, MagicMock())

        self.assertEqual(ret, None)

    async def test_get_emote_returns_correct_object(self) -> None:
        self.emote_collection_mock.find_one.return_value = 'found emote'
        emote_entity = self.patch('EmoteEntity')
        emote_entity.from_dict.return_value = 'emote entity object'

        ret = await self.obj.get_emote(None, MagicMock())

        emote_entity.from_dict.assert_called_once_with('found emote')
        self.assertEqual(ret, 'emote entity object')
    
    async def test_save_emote_correctly_persists_emote(self) -> None:
        emote = MagicMock()
        
        await self.obj.save_emote(emote)

        emote.to_dict.assert_called_once()
        self.emote_collection_mock.insert_one.assert_called_once_with(emote.to_dict.return_value)

    async def test_save_emote_returns_persisted_emote(self) -> None:
        emote = MagicMock()

        ret = await self.obj.save_emote(emote)

        self.assertEqual(ret, emote)

    async def test_ban_user_correctly_persists_banned_user(self) -> None:
        user = MagicMock()
        
        await self.obj.ban_user(user)

        user.to_dict.assert_called_once()
        self.banned_user_collection_mock.insert_one.assert_called_once_with(user.to_dict.return_value)

    async def test_ban_user_returns_banned_user(self) -> None:
        user = MagicMock()

        ret = await self.obj.ban_user(user)

        self.assertEqual(ret, user)
    
    async def test_unban_user_removes_user_from_ban_list(self) -> None:
        user = MagicMock()

        await self.obj.unban_user(user)

        user.to_dict_assert_called_once()
        self.banned_user_collection_mock.delete_one.assert_called_once_with(user.to_dict.return_value)

    async def test_unban_user_returns_unbanned_user(self) -> None:
        user = MagicMock()

        ret = await self.obj.unban_user(user)

        self.assertEqual(ret, user)
    
    async def test_list_banned_users_gets_all_banned_users_from_database(self) -> None:
        self.patch('UserEntity')

        await self.obj.list_banned_users()

        self.banned_user_collection_mock.find.assert_called_once()
    
    async def test_list_banned_users_returns_banned_users_as_correct_objects(self) -> None:
        self.banned_user_collection_mock.find.return_value = ['user1', 'user2', 'user3']
        user_entity = self.patch('UserEntity')
        def from_dict_side_effect():
            call_counter = 0
            while True:
                call_counter += 1
                yield f'user_entity {call_counter}'
        gen = from_dict_side_effect()
        user_entity.from_dict.side_effect = lambda _: next(gen)

        ret = await self.obj.list_banned_users()

        self.assertListEqual(ret, ['user_entity 1', 'user_entity 2', 'user_entity 3'])


    async def test_authorize_user_correctly_persists_authorized_user(self) -> None:
        user = MagicMock()
        
        await self.obj.authorize_user(user)

        user.to_dict.assert_called_once()
        self.authorized_user_collection_mock.insert_one.assert_called_once_with(user.to_dict.return_value)

    async def test_authorize_user_returns_authorized_user(self) -> None:
        user = MagicMock()

        ret = await self.obj.authorize_user(user)

        self.assertEqual(ret, user)

    async def test_unauthorize_user_removes_user_from_authorized_list(self) -> None:
        user = MagicMock()

        await self.obj.unauthorize_user(user)

        user.to_dict_assert_called_once()
        self.authorized_user_collection_mock.delete_one.assert_called_once_with(user.to_dict.return_value)

    async def test_unauthorize_user_returns_unauthorized_user(self) -> None:
        user = MagicMock()

        ret = await self.obj.unauthorize_user(user)

        self.assertEqual(ret, user)

    async def test_list_authorized_users_gets_all_authorized_users_from_database(self) -> None:
        self.patch('UserEntity')

        await self.obj.list_authorized_users()

        self.authorized_user_collection_mock.find.assert_called_once()

    async def test_list_authorized_users_returns_authorized_users_as_correct_objects(self) -> None:
        self.authorized_user_collection_mock.find.return_value = ['user1', 'user2', 'user3']
        user_entity = self.patch('UserEntity')
        def from_dict_side_effect():
            call_counter = 0
            while True:
                call_counter += 1
                yield f'user_entity {call_counter}'
        gen = from_dict_side_effect()
        user_entity.from_dict.side_effect = lambda _: next(gen)

        ret = await self.obj.list_authorized_users()

        self.assertListEqual(ret, ['user_entity 1', 'user_entity 2', 'user_entity 3'])
