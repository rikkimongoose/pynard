#imports
from pynard import *
import unittest

class PlayboardControllerInput(unittest.TestCase):
    """ Test for PlayboardController """
    def init(self):
        return PlayboardController()

    def testinit_start(self):
        playboard_controller = self.init()
        playboard = playboard_controller.init_start([1] + [0] * BG_END_INDEX)
        self.assertEqual(len(playboard.fields), BG_FIELD_SIZE)
        self.assertEqual(playboard.fields[0], 1)

    def testplayer_get_stack(self):
        playboard_controller = self.init()
        playboard = Playboard()
        self._player1_test(playboard_controller, playboard)
        self._player2_test(playboard_controller, playboard)

    def _player1_test(self, playboard_controller, playboard):
        playboard.player1_stack = 1
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER1), 1)
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER2), 0)

    def _player2_test(self, playboard_controller, playboard):
        playboard.player1_stack = 0
        playboard.player2_stack = 1
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER2), 1)
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER1), 0)

    def testplayer_stack_inc(self):
        playboard_controller = self.init()
        playboard = Playboard()
        playboard_controller.player_stack_inc(playboard, PLAYER1)
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER1), 1)
        playboard_controller.player_stack_inc(playboard, PLAYER2)
        self.assertEqual(playboard_controller.player_get_stack(playboard, PLAYER2), 1)

    def testget(self):
        playboard_controller = self.init()
        playboard = playboard_controller.init_start([1] + [0] * (BG_END_INDEX - 1) + [-1])
        self.assertEqual(playboard_controller.get(playboard, PLAYER1, 0), 1)
        self.assertEqual(playboard_controller.get(playboard, PLAYER2, 0), 1)
        self.assertEqual(playboard_controller.get(playboard, PLAYER1, 1), 0)
        self.assertEqual(playboard_controller.get(playboard, PLAYER2, 1), 0)

    def testmove_to(self):
        playboard_controller = self.init()
        playboard = playboard_controller.init_start([1] + [0] * (BG_END_INDEX - 1) + [-1])
        playboard_controller.move_to(playboard, PLAYER1, 1)
        self.assertEqual(playboard_controller.get(playboard, PLAYER1, 1), 1)
        playboard_controller.move_to(playboard, PLAYER2, 1)
        self.assertEqual(playboard_controller.get(playboard, PLAYER2, 1), 1)

    def testmove_from(self):
        playboard_controller = self.init()
        playboard = playboard_controller.init_start([2] + [0] * (BG_END_INDEX - 1) + [-2])
        playboard_controller.move_from(playboard, PLAYER1, 0)
        self.assertEqual(playboard_controller.get(playboard, PLAYER1, 0), 1)
        playboard_controller.move_from(playboard, PLAYER2, 0)
        self.assertEqual(playboard_controller.get(playboard, PLAYER2, 0), 1)

    def testget_player(self):
        playboard_controller = self.init()
        playboard = playboard_controller.init_start([1] + [0] * (BG_FIELD_SIZE - 2) + [-1])
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER1, 0), PLAYER1)
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER1, BG_END_INDEX), PLAYER2)
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER2, 0), PLAYER2)
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER2, BG_END_INDEX), PLAYER1)
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER1, 1), NO_PLAYER)
        self.assertEqual(playboard_controller.get_player(playboard, PLAYER2, 1), NO_PLAYER)


class RulesControllerInput(unittest.TestCase):
    def init(self):
        return RulesController(PlayboardController())

    def init_PlayboardController(self):
        return PlayboardController()

    def testset_start(self):
        control = self.init()
        board = control.set_start()
        i = 0
        while i < len(RulesController.init_position):
            self.assertEqual(board.fields[i], RulesController.init_position[i])
            i += 1

    def testis_win(self):
        control = self.init()
        playboard_controller = self.init_PlayboardController()
        playboard = playboard_controller.init_start([0] * BG_FIELD_SIZE)
        playboard.player1_stack = BG_USER_CHECKERS_COUNT
        self.assertTrue(control.is_win(playboard, PLAYER1))
        playboard.player2_stack = BG_USER_CHECKERS_COUNT
        self.assertTrue(control.is_win(playboard, PLAYER2))

    def testget_game_status(self):
        control = self.init()
        playboard_controller = self.init_PlayboardController()
        #test start
        playboard = control.set_start()
        self.assertEqual(control.get_game_status(playboard, PLAYER1), GAMESTATUS_START)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_START)
        #test middle
        playboard = control.set_start()
        playboard_controller.move_from(playboard, PLAYER1, 0)
        playboard_controller.move_to(playboard, PLAYER1, 1)
        self.assertEqual(control.get_game_status(playboard, PLAYER1), GAMESTATUS_MIDDLE)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_START)
        playboard_controller.move_from(playboard, PLAYER2, 0)
        playboard_controller.move_to(playboard, PLAYER2, 1)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_MIDDLE)

        #test end
        playboard = control.set_start()
        playboard.fields[0] = -playboard.fields[0]
        playboard.fields[BG_END_INDEX] = -playboard.fields[BG_END_INDEX]
        self.assertEqual(control.get_game_status(playboard, PLAYER1), GAMESTATUS_END)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_END)
        #test end 2
        playboard = control.set_start()
        playboard_controller.player_stack_inc(playboard, PLAYER1)
        self.assertEqual(control.get_game_status(playboard, PLAYER1), GAMESTATUS_END)
        playboard_controller.player_stack_inc(playboard, PLAYER2)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_END)
        #test end 3
        playboard = control.set_start()
        playboard.fields[1] = -playboard.fields[0]
        playboard.fields[BG_END_INDEX-1] = -playboard.fields[BG_END_INDEX]
        playboard.fields[0] = 1
        playboard.fields[BG_END_INDEX] = -1
        self.assertEqual(control.get_game_status(playboard, PLAYER1), GAMESTATUS_END)
        self.assertEqual(control.get_game_status(playboard, PLAYER2), GAMESTATUS_END)

    def testcan_move(self):
        control = self.init()
        playboard_controller = self.init_PlayboardController()
        #test start
        playboard = control.set_start()
        self.assertTrue(control.can_move(playboard, PLAYER1, 0, 1))
        self.assertTrue(control.can_move(playboard, PLAYER2, 0, 1))
        playboard_controller.move_from(playboard, PLAYER1, 0)
        playboard_controller.move_from(playboard, PLAYER2, 0)
        playboard_controller.move_to(playboard, PLAYER1, BG_END_INDEX - 1)
        playboard_controller.move_to(playboard, PLAYER2, BG_END_INDEX - 1)
        self.assertFalse(control.can_move(playboard, PLAYER1, 0, 1))
        self.assertFalse(control.can_move(playboard, PLAYER2, 0, 1))
        #test middle
        playboard = control.set_start()
        playboard_controller.move_from(playboard, PLAYER1, 0)
        playboard_controller.move_from(playboard, PLAYER2, 0)
        playboard_controller.move_to(playboard, PLAYER1, 1)
        playboard_controller.move_to(playboard, PLAYER2, 1)
        playboard_controller.move_to(playboard, PLAYER1, BG_END_INDEX - 2)
        playboard_controller.move_to(playboard, PLAYER2, BG_END_INDEX - 2)
        self.assertFalse(control.can_move(playboard, PLAYER1, 1, 1))
        self.assertFalse(control.can_move(playboard, PLAYER2, 1, 1))
        #test end
        playboard = control.set_start()
        playboard.fields[1] = -playboard.fields[0]
        playboard.fields[BG_END_INDEX-1] = -playboard.fields[BG_END_INDEX]
        playboard.fields[0] = 1
        playboard.fields[BG_END_INDEX] = -1
        self.assertFalse(control.can_move(playboard, PLAYER1, 1, 1))
        self.assertFalse(control.can_move(playboard, PLAYER2, 1, 1))

    def testdo_move(self):
        control = self.init()
        playboard_controller = self.init_PlayboardController()
        #test start player 1
        for player in (PLAYER1, PLAYER2):
            playboard = control.set_start()
            #start
            playboard = control.do_move(playboard, player, 0, 1)
            self.assertEqual(playboard_controller.get(playboard, player, 1), 1)
            self.assertIsNone(control.do_move(playboard, player, 2, 1))
            #middle
            playboard = control.do_move(playboard, player, 1, 1)
            self.assertEqual(playboard_controller.get(playboard, player, 1), 0)
            self.assertEqual(playboard_controller.get(playboard, player, 2), 1)
        #end
        for player in (PLAYER1, PLAYER2):
            playboard = control.set_start()
            playboard.fields[1] = -playboard.fields[0]
            playboard.fields[0] = 0
            playboard.fields[BG_END_INDEX-1] = -playboard.fields[BG_END_INDEX]
            playboard.fields[BG_END_INDEX] = 0
            playboard = control.do_move(playboard, player, BG_END_INDEX-1, 1)
            self.assertEqual(playboard_controller.get(playboard, player, BG_END_INDEX), 1)
            playboard = control.do_move(playboard, player, BG_END_INDEX-1, 2)
            self.assertEqual(playboard_controller.player_get_stack(playboard, player), 1)

if __name__ == "__main__":
    unittest.main()