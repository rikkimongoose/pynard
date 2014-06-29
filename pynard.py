PYNARD_VER = "0.1"

#imports
from collections import deque

import copy
import random
import os

#constants
TABLE_SIZE = 24
TABLE_SIZE_HALF = TABLE_SIZE / 2
USER_CHECKERS_COUNT = 15

DICE_VARIANTS = 27

START_HOUSE_END = 5
END_HOUSE_START = 18

(GAMESTATUS_UNKNOWN, GAMESTATUS_START, GAMESTATUS_MIDDLE, GAMESTATUS_END) = (0, 1, 2, 3)
(NO_PLAYER, PLAYER1, PLAYER2) = (0, 1, -1)
(NO_WIN_TURKISH_MARS, NO_WIN_MARS, NO_WIN, DRAW, WIN, MARS, TURKISH_MARS) = (-4, -2, -1, 0, 1, 2, 4)
(MOVE_OK, ERROR_MOVE_NO_INDEX, ERROR_MOVE_NO_STACK) = (1, -1, -2)

class Playboard:
    """ Current game state as play board.
    """
    def __init__(self):
        fields = [0] * TABLE_SIZE
        player1_stack = 0
        player2_stack = 0

    def __eq__(self, obj):
        if not isinstance(obj, Playboard): return False
        return self.fields == obj.fields and self.player1 == obj.player1 and self.player2 == obj.player2

    def __ne__(self, obj):
        return not self == obj

    def __str__(self):
        return str(self.fields) + " - %s . %s" % (self.player1_stack, self.player2_stack)

class Position:
    """ Current game state as positions for every checker.
    """
    POS_OUT_OF_BOARD = -1
    MASK_OUT_OF_BOARD = 0b10000000

    def __init__(self):
        self.player1_values = [0] * USER_CHECKERS_COUNT
        self.player2_values = [0] * USER_CHECKERS_COUNT
        self.estimation = 0.0
        self.probability = 0.0
        self.used_times = 1
        self.dice_nodes = None

    def data_for(self, player):
        if player == PLAYER1: return self.player1_values
        elif player == PLAYER2: return self.player2_values
        return None

    def to_playboard(self, rules):
        """ Returns current position in play-board format. If position is wrong, returns None.
        """
        playboard = Playboard()
        for val in player1_values:
            if val & MASK_OUT_OF_BOARD:
                playboard.player1_stack += 1
            elif val >= TABLE_SIZE:
                return None
            else:
                playboard.fields[rules.absolute_pos(PLAYER1, val)] += 1
        for val in player2_values:
            if val & MASK_OUT_OF_BOARD:
                playboard.player2_stack += 1
            elif val >= TABLE_SIZE:
                return None
            else:
                playboard.fields[rules.absolute_pos(PLAYER2, val)] -= 1
        return playboard

    @staticmethod
    def _cmp_array_data(array_data1, array_data2):
        check_mask = 0
        for i in range(USER_CHECKERS_COUNT):
            has_value = False
            for j in range(USER_CHECKERS_COUNT):
                check_mask_val = 1 << j
                if check_mask & check_mask_val: continue
                if(array_data1[i] == array_data2[j]):
                    check_mask |= check_mask_val
                    has_value = True
                    break;
            if not has_value: return False
        return True

    def __eq__(self, obj):
        if not isinstance(obj, Position): return False
        return Position._cmp_array_data(self.player1_values, obj.player1_values) and \
                    Position._cmp_array_data(self.player2_values, obj.player2_values)

    def __ne__(self, obj):
        return not self == obj

    def __str__(self):
        str_result = ""
        for player_data in (self.player1_values, self.player2_values):
            index = 0
            for data in player_data:
                str_result += "checker[%s] = %s\n" % (index, data)
                index += 1
            str_result += "checker[%s] = %s\n"
        return str_result

class DiceNode:
    def __init__(self, init_dice, init_position):
        dice = init_dice
        positions = init_position

    dice = None
    positions = []

class PositionController:
    def _pos_index(self, pos):
        if pos & MASK_OUT_OF_BOARD: return POS_OUT_OF_BOARD
        else: return pos

    def pos_index(self, player_data, index):
        return self._pos_index(player_data[index])

    def checker_index(self, player_data, pos):
        index = 0
        for data_item in player_data:
            if self._pos_index(data_item) == pos: return index
            index += 1
        return index

    def checker(self, player_data, pos):
        for data_item in player_data:
            if self._pos_index(data_item) == pos: return data_item
        return None

    def all_checkers(self, player_data, pos):
        checkers = []
        for data_item in player_data:
            if self._pos_index(data_item) == pos: checkers.append(data_item)
        return None

    def stack_val(self, player_data):
        stack_num = 0
        for data_item in player_data:
            if data_item & MASK_OUT_OF_BOARD:
                stack_num += 1
        return 0

    def can_move(self, player_data, checker_item_index, steps, move_to_stack = False):
        """ Can move checker to new position from index in player_data.
            Returns:
            - MOVE_OK if it's ok
            - ERROR_MOVE_NO_INDEX is there aren't any checker this index
            - ERROR_MOVE_NO_STACK if it's not allowed to move checker to stack
        """
        checker_item = player_data[checker_item_index]
        if checker_item is None: return ERROR_MOVE_NO_INDEX
        if checker_item + pos >= TABLE_SIZE and not move_to_stack: return ERROR_MOVE_NO_STACK
        return MOVE_OK

    def move(self, player_data, checker_item_index, steps, move_to_stack = False):
        """ Move checker to new position from index in player_data.
            Returns:
            - MOVE_OK if it's ok
            - ERROR_MOVE_NO_INDEX is there aren't any checker this index
            - ERROR_MOVE_NO_STACK if it's not allowed to move checker to stack
        """
        checker_item = player_data[checker_item_index]
        if checker_item is None: return ERROR_MOVE_NO_INDEX
        if checker_item + pos < TABLE_SIZE:
            player_data[checker_item_index] = checker_item + pos
        elif move_to_stack:
            player_data[checker_item_index] = MASK_OUT_OF_BOARD
        else:
            return ERROR_MOVE_NO_STACK
        return MOVE_OK

class DiceController:
    DICE_MAX = 7
    dices = deque(maxlen = DICE_VARIANTS)

    @staticmethod
    def _do_init():
        for i in range(1, DICE_MAX):
            DiceController.dices.append(([i, i, i, i], 1/36))
            for j in range(i + 1, DICE_MAX): DiceController.dices.append(([i, j], 1/18))

    @staticmethod
    def get_dices():
        if not len(DiceController.dices): DiceController._do_init()
        return DiceController.dices

    @staticmethod
    def rnd_dice():
        if not len(DiceController.dices): DiceController._do_init()
        dice1, dice2 = random.randint(1, DICE_MAX), random.randint(1, DICE_MAX)
        return filter(lambda x: x[0][0] == dice1 and x[0][1] == dice2, DiceController.dices)[:1]

class NardiRulesController():
    def __init__(self, position_controller_init):
        self.position_controller = position_controller_init

    def next_player(self, player):
        if player == PLAYER1: return PLAYER2
        elif player == PLAYER2: return PLAYER1
        return NO_PLAYER

    def move(self, position, player, checker_index, steps, game_state):
        player_data = position.data_for(player)
        return self.position_controller.move(player_data, checker_index, steps, game_state == GAMESTATUS_END)

    def can_move(self, position, player, checker_index, steps, game_state):
        player_data = position.data_for(player)
        enemy_player_data = position.data_for(self.next_player(player))
        pos = self.position_controller.pos(player_data, checker_index)
        if game_state == GAMESTATUS_MIDDLE and \
            self.position_controller.can_move(player_data, checker_index, steps) and \
            self.position_controller.checker(enemy_player_data, pos + steps) is None:
            return True
        if game_state == GAMESTATUS_END and \
            self.position_controller.can_move(player_data, checker_index, steps, True) and \
            (pos + steps >= TABLE_SIZE or \
                self.position_controller.checker(enemy_player_data, pos + steps)):
            return True
        return False

    def game_state(self, array_data):
        for data in array_data:
            if data & MASK_OUT_OF_BOARD: return GAMESTATUS_END
            if data < END_HOUSE_START: return GAMESTATUS_MIDDLE
        return GAMESTATUS_END

    def get_winner(self, position):
        while player in (PLAYER1, PLAYER2):
            if self.position_controller.stack_val(position.data_for(player)) == USER_CHECKERS_COUNT:
                return player
        return NO_PLAYER

    def absolute_pos(self, player, pos):
        if player == PLAYER1: return pos
        elif player == PLAYER2:
            if pos < FIELD_SIZE_HALF: return pos + FIELD_SIZE_HALF
            return pos - FIELD_SIZE_HALF

class GameController:
    def __init__(self, rules_controller_item):
        self._rules_controller = rules_controller_item
        self._playboard_controller = self._rules_controller._playboard_controller
        self.all_positions = deque()

    def moves(self, player, position):
        dice_nodes = []
        dices = DiceController.get_dices()
        for dice in dices:
            moves = self.moves_by_dice(player, position, dice)
            if moves is None or not len(modes): continue
            dice_nodes.append(DiceNode(dice, moves))
        position.dice_nodes = dice_nodes

    def moves_by_dice(self, player, position, dice):
        position_items = [position]
        new_position_items = []
        for dice_item in dice:
            for position_item in position_items:
                if position_item.dice_nodes is not None: continue
                player_data = position_item.data_for(player)
                game_state = self._playboard_controller.game_state(player_data)
                for checker_index in range(USER_CHECKERS_COUNT):
                    if not self._rules_controller.can_move(player_data, checker_index, dice_item[0], game_state): continue
                    playboard_new = copy.deepcopy(playboard)
                    if not self._rules_controller.move(playboard_new, checker_index, dice_item[0], game_state): continue
                    playboard_new_prev = filter(lambda x: x == playboard_new, self.all_positions)[:1]
                    if playboard_new_prev is not None:
                        new_position_items.append(playboard_new_prev)
                        playboard_new_prev.used_times += 1
                        playboard_new.probability += position.probability * dice_item[1]
                    else
                        new_position_items.append(playboard_new)
                        playboard_new.probability = position.probability * dice_item[1]
            if len(new_position_items):
                position_items = list(new_position_items)
                new_position_items = []
            else: break
        return position_items

if __name__ == "__main__":
    print("PyNard %s by rikkimongoose (http://github.com/rikkimongoose/pynard/)" % PYNARD_VER)