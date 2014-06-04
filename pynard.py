#constants
BG_FIELD_SIZE = 24
BG_USER_CHECKERS_COUNT = 15

BG_START_HOUSE_END = 5
BG_END_HOUSE_START = 19

GAMESTATUS_UNKNOWN, GAMESTATUS_START, GAMESTATUS_MIDDLE, GAMESTATUS_END = 0, 1, 2, 3
NO_PLAYER, PLAYER1, PLAYER2 = 0, 1, -1
NO_WIN, WIN, MARS, TURKISH_MARS = 0, 1, 2, 4

class PlayTable:
    fields = []
    player1 = 0
    player2 = 0
    player1_game_status = GAMESTATUS_UNKNOWN
    player2_game_status = GAMESTATUS_UNKNOWN

    def __eq__(self, obj):
        if not isinstance(obj, PlayTable):
            return False

        return self.fields == obj.fields and self.player1 == obj.player1 and self.player2 == obj.player2

    def __ne__(self, obj):
        return not self == obj

MOV_DEFAULT, MOV_OUT = 0, 1

class PlayTableController:
    def next_player(self, player):
        if player == PLAYER1:
            return PLAYER2
        else:
            return PLAYER1

    def inc_by_player(self, player):
        return player

    def pos_by_player(self, play_table, player, pos):
        if player == PLAYER1:
            return pos
        elif player == PLAYER2:
            return BG_FIELD_SIZE - pos - 1

    def player_stack_var(self, play_table, player):
        if player == PLAYER1:
            return play_table.player1
        elif player == PLAYER2:
            return lay_table.player2

    def player_stack_inc(self, play_table, player):
        if player == PLAYER1:
            play_table.player1 += 1
        elif player == PLAYER2:
            play_table.player2 += 1

    def _get(self, play_table, player, pos):
        pos = self.pos_by_player(play_table, player, pos)
        return play_table.fields[pos]

    def get(self, play_table, player, pos):
        return abs(_get(play_table, player, pos))

    def get_player(self, play_table, player, pos):
        val = _get(play_table, player, pos)
        if val > o:
            return PLAYER1
        if val < o:
            return PLAYER2
        # if val == 0:
        return NO_PLAYER

    def move(self, play_table, player, pos, steps):
        player_inc = self.inc_by_player(player)
        pos = self.pos_by_player(play_table, player, pos)
        play_table.fields[pos] -= player_inc
        if pos + steps >= BG_FIELD_SIZE:
            return MOV_OUT
        play_table.fields[pos + steps] += player_inc
        return MOV_DEFAULT

    def set_start(self, play_table, data):
        fields = data

class NardRulesController:
    start_exceptional = [ {6, 6}, {4, 4}, {3, 3} ]
    def __init__(self, play_table_controller):
        self._play_table_controller = play_table_controller

    def parse_game_status(self, play_table, player):
        _play_table_controller_get = _play_table_controller.get
        if _play_table_controller_get(play_table, player, 0) == BG_USER_CHECKERS_COUNT:
            return GAMESTATUS_START

        if _play_table_controller.player_stack_var(play_table, player):
            return GAMESTATUS_END
        checkers_count = 0
        for iterat in range(BG_END_HOUSE_START, BG_FIELD_SIZE): checkers_count += _play_table_controller_get(play_table, player, iterat)
        if checkers_count == BG_USER_CHECKERS_COUNT:
            return GAMESTATUS_END

        return GAMESTATUS_MIDDLE

    def get_game_status(self, play_table, player):
        game_status = GAMESTATUS_UNKNOWN
        if player == PLAYER1:
            game_status = play_table.player1_game_status
        else:
            game_status = play_table.player2_game_status
        if game_status != GAMESTATUS_UNKNOWN:
            return game_status
        return self.parse_game_status(play_table, player)

    def set_start(self, play_table, data):
        self._play_table_controller.set_start(data)

    def can_move(self, play_table, player, pos, step):
        pass

    def can_move_start(self, play_table, player, pos, step):
        pass

    def can_move_middle(self, play_table, player, pos, step):
        pass

    def can_move_end(self, play_table, player, pos, step):
        pass

    def is_win(self, play_table, player):
        pass

class Move:
    player=NO_PLAYER
    pos=-1
    steps=0

class AnalyseItem:
    parent = None
    children = []

    playtable = None
    move = None

    probability = None
    estimation = None