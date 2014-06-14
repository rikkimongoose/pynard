#imports
import copy

#constants
BG_FIELD_SIZE = 24
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

MOV_DEFAULT, MOV_OUT = 0, 1

class PlayboardController:

    def _inc_by_player(self, player):
        return player

    def _pos_by_player(self, player, pos):
        if player == PLAYER1:
            return pos
        elif player == PLAYER2:
            return BG_FIELD_SIZE - pos - 1

    def player_get_stack(self, playboard, player):
        if player == PLAYER1:
            return playboard.player1_stack
        elif player == PLAYER2:
            return playboard.player2_stack

    def _get_raw(self, playboard, player, pos):
        pos = _pos_by_player(playboard, player, pos)
        return playboard.fields[pos]

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

    def player_stack_inc(self, playboard, player):
        if player == PLAYER1:
            playboard.player1 += 1
        elif player == PLAYER2:
            playboard.player2 += 1

    def get(self, playboard, player, pos):
        return _get_by_player(playboard, player, pos)

    def move_to(self, playboard, player, pos):
        inc_val = _inc_by_player(player)
        pos_from = _pos_by_player(playboard, player, pos)
        playtable.fields[pos] += inc_val

    def move_from(self, playboard, player, pos):
        inc_val = _inc_by_player(player)
        pos_from = _pos_by_player(playboard, player, pos)
        playtable.fields[pos] -= inc_val

    def get_player(self, playboard, player, pos):
        val = _get_raw(playboard, player, pos)
        if val > 0:
            return PLAYER1
        if val < 0:
            return PLAYER2
        # if val == 0:
        return NO_PLAYER

class RulesController:
    start_exceptional = [ {6, 6}, {4, 4}, {3, 3} ]
    init_position = [BG_USER_CHECKERS_COUNT] + [0] * (BG_FIELD_SIZE - 2) + [-BG_USER_CHECKERS_COUNT]

    def __init__(self, playboard_controller_item):
        self._playboard_controller = playboard_controller_item

    def set_start(self):
        new_board = Playboard()
        _playboard_controller.set_start(new_board)
        return new_board

    def is_win(self, playboard, player):
        if _play_table_controller.player_stack_var(playboard, player) >= BG_USER_CHECKERS_COUNT:
            return WIN
        return NO_WIN

    def get_game_status(self, playboard, player):
        _play_table_controller_get = _play_table_controller.get
        if _play_table_controller_get(playboard, player, 0) == BG_USER_CHECKERS_COUNT:
            return GAMESTATUS_START
        checkers_count = 0
        for iterator in range(BG_END_HOUSE_START, BG_FIELD_SIZE): checkers_count += _play_table_controller_get(playboard, player, iterator)
        if checkers_count == BG_USER_CHECKERS_COUNT:
            return GAMESTATUS_END
        return GAMESTATUS_MIDDLE

    def do_move(self, playboard, player, pos, step):
        play_table_status = get_game_status(playboard, player)

        if play_table_status == GAMESTATUS_START and can_move_start(playboard, player, pos, step):
            return do_move_start(playboard, player, pos, step)
        if play_table_status == GAMESTATUS_MIDDLE and can_move_middle(playboard, player, pos, step):
            return do_move_middle(playboard, player, pos, step)
        elif play_table_status == GAMESTATUS_END and can_move_end(playboard, player, 0, step):
            return do_move_end(playboard, player, pos, step)

    def can_move_start(self, playboard, player, pos, step):
        return pos == 0

    def _is_enemy_player(self, player, pos):
        field_player = _playboard_controller.get_player(playboard, player, pos)
        return field_player != NO_PLAYER and field_player != player

    def _is_before_border(self, pos, step):
        return pos + step < BG_FIELD_SIZE

    def can_move_middle(self, playboard, player, pos, step):
        return _is_before_border(pos, step) and not _is_enemy_player(pos + step)

    def can_move_end(self, playboard, player, pos, step):
        return not _is_enemy_player(pos + step)

    def do_move_start(self, playboard, player, pos, step):
        return do_move_middle(playboard, player, pos, step)

    def do_move_middle(self, playboard, player, pos, step):
        move_item = _init_move(playboard, player, pos, step)
        _playboard_controller.move_from(move_item.playboard, player, pos)
        _playboard_controller.move_to(move_item.playboard, player, pos + step)
        return move_item

    def do_move_end(self, playboard, player, pos, step):
        if _is_before_border(pos, step):
            return do_move_middle(playboard, player, pos, step)
        move_item = _init_move(playboard, player, pos, step)
        _playboard_controller.move_from(move_item.playboard, player, pos)
        _playboard_controller.player_stack_inc(move_item.playboard, player)
        return move_item

    def _init_move(self, playboard, player, pos, step):
        return Move(deepcopy(playboard), player, pos, step)

class Move:
    def __init__(self, playboard_init, player_init, pos_init, step_init):
        playboard_ = playboard_init
        player = player_init
        pos = pos_init
        step = step_init

    player = NO_PLAYER

    pos = -1
    step = 0
    playboard = None

    parent = None
    children = None

    estimation = 0.0