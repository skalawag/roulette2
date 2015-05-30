import os
import unittest
from roulette import *

class TestRoulette(unittest.TestCase):

    def test_load_players_first_time(self):
        if os.path.isfile('roulette.db'):
            os.system('mv roulette.db roulette.db.bak')
        self.assertEqual(load_players(), [])
        if os.path.isfile('roulette.db.bak'):
            os.system('mv roulette.db.bak roulette.db')

    def test_player_init(self):
        player = Player('fyv')
        self.assertEqual(player.name, 'fyv')
        self.assertEqual(player.wins, 0)
        self.assertEqual(player.losses, 0)
        self.assertEqual(player.seppuku, 0)
        self.assertFalse(player.invisible())

    def test_player_saves_self(self):
        if os.path.isfile('roulette.db'):
            os.system('mv roulette.db roulette.db.bak')
        player = Player('fyv')
        player_dict = player.__dict__
        player.save()
        player = load_players()[0]
        self.assertEqual(player_dict, player.__dict__)
        if os.path.isfile('roulette.db.bak'):
            os.system('mv roulette.db.bak roulette.db')

    def test_seppuku(self):
        if os.path.isfile('roulette.db'):
            os.system('mv roulette.db roulette.db.bak')
        p = Player('fyv')
        p.save()
        seppuku(p)
        p = load_players()[0]
        self.assertNotEqual(p.seppuku, 0)
        self.assertTrue(p.invisible())
        if os.path.isfile('roulette.db.bak'):
            os.system('mv roulette.db.bak roulette.db')

    def test_get_champ(self):
        if os.path.isfile('roulette.db'):
            os.system('mv roulette.db roulette.db.bak')

        p1 = Player('fyv', wins=2, losses=2)
        p1.save()
        p2 = Player('mark', wins=2, losses=0)
        p2.save()
        print get_champ()
        self.assertEqual(get_champ().name, 'mark')

        if os.path.isfile('roulette.db.bak'):
            os.system('mv roulette.db.bak roulette.db')

if __name__ == '__main__':
    unittest.main()
