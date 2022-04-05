import unittest

from model.exception.not_yet_connected import NotYetConnected
from service.music_player_service import MusicPlayerService


class MusicPlayerServiceTestCase(unittest.TestCase):
    def test_check_if_connected(self):
        obj = MusicPlayerService(None)

        self.assertRaises(NotYetConnected, obj.check_if_connected, 1)

if __name__ == '__main__':
    unittest.main()
