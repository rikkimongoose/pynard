PYNARD_VER = "0.1"

#imports
import copy
import random
import os

#constants
BG_FIELD_SIZE = 24
BG_FIELD_SIZE_HALF = BG_FIELD_SIZE / 2
BG_END_INDEX = BG_FIELD_SIZE - 1
BG_USER_CHECKERS_COUNT = 15

BG_START_HOUSE_END = 5
BG_END_HOUSE_START = 19

GAMESTATUS_UNKNOWN, GAMESTATUS_START, GAMESTATUS_MIDDLE, GAMESTATUS_END = 0, 1, 2, 3
NO_PLAYER, PLAYER1, PLAYER2 = 0, 1, -1
NO_WIN_TURKISH_MARS, NO_WIN_MARS, NO_WIN, DRAW, WIN, MARS, TURKISH_MARS = -4, -2, -1, 0, 1, 2, 4

class Playboard:
    fields = []
    player1_stack = 0
    player2_stack = 0

    def __eq__(self, obj):
        if not isinstance(obj, PlayTable):
            return False
        return self.fields == obj.fields and self.player1 == obj.player1 and self.player2 == obj.player2

    def __ne__(self, obj):
        return not self == obj

    def __str__(self):
        return str(self.fields) + " - %s . %s" % (self.player1_stack, self.player2_stack)

MOV_DEFAULT, MOV_OUT = 0, 1

class PlayboardController:

    def _inc_by_player(self, player):
        return player

    def _pos_by_player(self, player, pos):
        if player == PLAYER1:
            return pos
        elif player == PLAYER2:
            if pos < BG_FIELD_SIZE_HALF:
                return pos + BG_FIELD_SIZE_HALF
            return pos - BG_FIELD_SIZE_HALF

    def _get_raw(self, playboard, player, pos):
        pos = self._pos_by_player(player, pos)
        return self.get_raw_by_pos(playboard, pos)

    def _get_by_player(self, playboard, player, pos):
        val = self._get_raw(playboard, player, pos)
        if player == PLAYER1:
            return val
        elif player == PLAYER2:
            return -val

    def init_start(self, data):
        board = Playboard()
        board.fields = data
        return board

    def get_raw_by_pos(self, playboard, pos):
        return playboard.fields[pos]

    def player_get_stack(self, playboard, player):
        if player == PLAYER1:
            return playboard.player1_stack
        elif player == PLAYER2:
            return playboard.player2_stack

    def player_stack_inc(self, playboard, player):
        if player == PLAYER1:
            playboard.player1_stack += 1
        elif player == PLAYER2:
            playboard.player2_stack += 1

    def get(self, playboard, player, pos):
        return self._get_by_player(playboard, player, pos)

    def move_to(self, playboard, player, pos):
        inc_val = self._inc_by_player(player)
        pos_from = self._pos_by_player(player, pos)
        playboard.fields[pos_from] += inc_val

    def move_from(self, playboard, player, pos):
        inc_val = self._inc_by_player(player)
        pos_from = self._pos_by_player(player, pos)
        playboard.fields[pos_from] -= inc_val

    def get_player(self, playboard, player, pos):
        val = self._get_raw(playboard, player, pos)
        if val > 0:
            return PLAYER1
        if val < 0:
            return PLAYER2
        # if val == 0:
        return NO_PLAYER
class RulesController:
    start_exceptional = [ {6, 6}, {4, 4}, {3, 3} ]
    _init_position = [BG_USER_CHECKERS_COUNT] + [0] * (BG_FIELD_SIZE_HALF - 1) + [-BG_USER_CHECKERS_COUNT] + [0] * (BG_FIELD_SIZE_HALF - 1)

    def __init__(self, playboard_controller_item):
        self._playboard_controller = playboard_controller_item

    PLAYER_START_HOUSE = range(0, 6)
    PLAYER_END_HOUSE = range(18, 24)

    @classmethod
    def init_playboard(self, playboard = None):
        if playboard is not None:
            return copy.deepcopy(playboard)
        return copy.deepcopy(self._init_position)

    def set_start(self, init_position = None):
        return self._playboard_controller.init_start(self.init_playboard(init_position))

    def is_win(self, playboard, player):
        if self._playboard_controller.player_get_stack(playboard, player) >= BG_USER_CHECKERS_COUNT:
            return WIN
        return NO_WIN

    def get_game_status(self, playboard, player):
        _play_table_controller_get = self._playboard_controller.get
        if self._playboard_controller.player_get_stack(playboard, player):
            return GAMESTATUS_END
        if _play_table_controller_get(playboard, player, 0) == BG_USER_CHECKERS_COUNT:
            return GAMESTATUS_START
        checkers_count = 0
        for iterator in self.PLAYER_END_HOUSE:
            val = _play_table_controller_get(playboard, player, iterator)
            if val > 0:
                checkers_count += val
            if checkers_count == BG_USER_CHECKERS_COUNT:
                return GAMESTATUS_END
        return GAMESTATUS_MIDDLE

    def can_move(self, playboard, player, pos, step):
        play_table_status = self.get_game_status(playboard, player)
        if play_table_status == GAMESTATUS_START:
            return self.can_move_start(playboard, player, pos, step)
        if play_table_status == GAMESTATUS_MIDDLE:
            return self.can_move_middle(playboard, player, pos, step)
        elif play_table_status == GAMESTATUS_END:
            return self.can_move_end(playboard, player, pos, step)
        return False

    def do_move(self, playboard, player, pos, step):
        play_table_status = self.get_game_status(playboard, player)
        if play_table_status == GAMESTATUS_START and self.can_move_start(playboard, player, pos, step):
            return self.do_move_start(playboard, player, pos, step)
        if play_table_status == GAMESTATUS_MIDDLE and self.can_move_middle(playboard, player, pos, step):
            return self.do_move_middle(playboard, player, pos, step)
        elif play_table_status == GAMESTATUS_END and self.can_move_end(playboard, player, pos, step):
            return self.do_move_end(playboard, player, pos, step)
        return None

    def _is_this_player(self, playboard, player, pos):
        field_player = self._playboard_controller.get_player(playboard, player, pos)
        return field_player == player

    def _is_enemy_player(self, playboard, player, pos):
        field_player = self._playboard_controller.get_player(playboard, player, pos)
        return field_player != NO_PLAYER and field_player != player

    def _is_before_border(self, pos, step):
        return pos + step < BG_FIELD_SIZE

    def can_move_start(self, playboard, player, pos, step):
        return pos == 0

    def can_move_middle(self, playboard, player, pos, step):
        return self._is_this_player(playboard, player, pos) and self._is_before_border(pos, step) and not self._is_enemy_player(playboard, player, pos + step)

    def can_move_end(self, playboard, player, pos, step):
        return self._is_this_player(playboard, player, pos) and (not self._is_before_border(pos, step) or not self._is_enemy_player(playboard, player, pos + step))

    def do_move_start(self, playboard, player, pos, step):
        return self.do_move_middle(playboard, player, pos, step)

    def do_move_middle(self, playboard, player, pos, step):
        playboard_new = self.init_playboard(playboard)
        self._playboard_controller.move_from(playboard_new, player, pos)
        self._playboard_controller.move_to(playboard_new, player, pos + step)
        return playboard_new

    def do_move_end(self, playboard, player, pos, step):
        if self._is_before_border(pos, step):
            return self.do_move_middle(playboard, player, pos, step)
        playboard_new = self.init_playboard(playboard)
        self._playboard_controller.move_from(playboard_new, player, pos)
        self._playboard_controller.player_stack_inc(playboard_new, player)
        return playboard_new

class DiceController(object):
    @staticmethod
    def get_dice(self, numbers = 6):
        return (random.randint(1, numbers), random.randint(1, numbers))

    @staticmethod
    def get_all_dices(self, numbers = 6):
        i = 1
        j = 1
        dices = []
        for i in range(numbers):
            dices.add({i, i, i, i})
            for j in range(i):
                dices.add({i, j})
        return dices

    @staticmethod
    def dice_probability(self, dice):
        if dice[0] == dice[1]:
            return 1/36
        else:
            return 2/36

class GameController:
    def __init__(self, rules_controller_item):
        self._rules_controller = rules_controller_item
        self._playboard_controller = self._rules_controller._playboard_controller
        self.all_dices = DiceController.get_all_dices()

    def get_all_moves(self, player, playboard, dices):
        pos = 0
        marbles = 0
        moves = []
        move.player = player
        marbles_limit = BG_USER_CHECKERS_COUNT - self._playboard_controller.player_get_stack(player, playboard)
        dice = dices[0]
        while marbles < marbles_limit and pos < BG_FIELD_SIZE:
            val = self._playboard_controller.get(player, playboard, pos)
            if val > 0:
                marbles += val
                new_board = self._rules_controller.do_move(player, playboard, pos, dice)
                if new_board is not None:
                    move = Move()
                    move.player = player
                    move.playboard = new_board
                    move.moves.add((pos, dice))
                    moves.add(move)
            pos += 1
        new_moves = []
        while dice_pos in range(1, len(dices)):
            dice = dices[dice_pos]
            for move in moves:
                pos = 0
                marbles = 0
                while marbles < marbles_limit and pos < BG_FIELD_SIZE:
                    val = self._playboard_controller.get(player, move.playboard, pos)
                    if val > 0:
                        marbles += val
                        new_board = self._rules_controller.do_move(player, move.playboard, pos, dice)
                        if new_board is not None:
                            new_move = Move()
                            new_move.player = player
                            new_move.playboard = new_board
                            new_move.moves += move.moves
                            new_move.moves.add((pos, dice))
                            new_moves.add(move)
                    pos += 1
            if not len(new_moves):
                break
            moves = new_moves
        for move in moves:
            move.probability = DiceController.dice_probability(dices)
        return moves

    def load_all_child_moves(self, move, is_recursive = False):
        dices = get_all_dices
        for dice in dices:
            move.children += self.get_all_moves(get_next_player(move.player), move.playboard, dice)

        #remove playboard to free memory
        move.playboard = None

        for child in move.children:
            child.parent = move
            if self._rules_controller.is_win(child.board, child.player):
                child.winner = child.player
                child.playboard = None
                continue
            if is_recursive:
                self.load_all_child_moves(child, True)

    def get_first_player(self):
        return PLAYER1

    def get_next_player(self, player):
        if player == PLAYER1:
            return PLAYER2
        elif player == PLAYER2:
            return PLAYER1
        return NO_PLAYER

    def load_moves_tree(self, player, playboard):
        base_move = Move()
        base_move.player = NO_PLAYER
        base_move.playboard = playboard

        children = []

class MoveNetItem:
    moves = []
    player = NO_PLAYER
    playboard = None

    parent = None
    children = []

    estimation = 0.0
    probability = 0.0

    winner = NO_PLAYER

    def __str__(self):
        return "est: %f, prob: %f: " % (estimation, probability) + ','.join([PlayboardVisualiser.show_move(move) for move in moves])

class PlayboardVisualiser:
    @staticmethod
    def show_move(move_tuple):
        if x[1] <= 0:
            return "%s - =>" % (x[0])
        return "%s - %s" % (x[0], x[1])

if __name__ == "__main__":
    print("PyNard %s by rikkimongoose (http://github.com/rikkimongoose/pynard/)" % PYNARD_VER)
