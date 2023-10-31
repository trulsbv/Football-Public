class Event():
    def __init__(self, game, time, team):
        self.game = game
        self.time = time
        self.team = team
    
    def __repr__(self) -> str:
        return f"{self.time} "

class Booking(Event):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = team.get_player(player[0], player[1], warning=True)
        self.player.events.append(self)
    
    def __repr__(self) -> str:
        return super().__repr__()

class YellowCard(Booking):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" gult kort"

class RedCard(Booking):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" rødt kort"

class Substitute(Event):
    def __init__(self, game, time, team, player):
        _out, _in = player
        super().__init__(game, time, team)
        self.player_in = team.get_player(_in[0], _in[1], warning=True)
        self.player_out = team.get_player(_out[0], _out[1], warning=True)
        self.player_in.matches["sub in"] = {game: self}
        self.player_out.matches["sub out"] = {game: self}
        self.current_score = game.result.get_result()
    
    def __repr__(self) -> str:
        return super().__repr__()+" bytte"

class Goal(Event):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = team.get_player(player[0], player[1], warning=True)
        self.player.events.append(self)
    
    def __repr__(self) -> str:
        return super().__repr__()

class PlayGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" spillemål"

class PenaltyGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" straffemål"

class OwnGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" selvmål"