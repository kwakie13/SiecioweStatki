class Game:
    def __init__(self):
        self.id = 0
        self.turn = 0
        self.your_id = 0
        self.players_dictionary = {1: 'null', 2: 'null', 3: 'null', 4: 'null'}
        self.dead_players = []
        self.whose_turn_player_id = 0
        self.attacked_player = 0
        self.position_attacked = (0, 0)
        self.success_of_attack = 0
        self.winner_player_id = 0
