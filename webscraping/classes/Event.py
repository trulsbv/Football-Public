import tools.prints as prints

class Event():
    def __init__(self, game, time, team):
        self.game = game
        self.time = int(time)
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
        player_a = team.get_player(_in[0], _in[1], warning=True)
        player_b = team.get_player(_out[0], _out[1], warning=True)

        if team == game.home:
            sheet = game.hometeam
        elif team == game.away:
            sheet = game.awayteam

        if player_a in sheet[0]:    # Player_a is on pitch, player b is on 
            self.player_in = player_b
            assert player_b in sheet[1]
            self.player_out = player_a

            sheet[0].append(player_b)
            sheet[0].remove(player_a)
            sheet[1].append(player_a)
            sheet[1].remove(player_b)
            assert (not player_a in sheet[0]) and (player_a in sheet[1])
            assert (not player_b in sheet[1]) and (player_b in sheet[0])
        elif player_b in sheet[0]:                       # Player_b is on pitch, player a is on bench
            #print("\nb on pitch")
            #print(player_b)
            self.player_in = player_a
            assert player_a in sheet[1]
            self.player_out = player_b
            sheet[0].append(player_a)
            sheet[0].remove(player_b)
            sheet[1].append(player_b)
            sheet[1].remove(player_a)
            assert (not player_a in sheet[1]) and (player_a in sheet[0])
            assert (not player_b in sheet[0]) and (player_b in sheet[1])
        else:
            prints.warning("SUBSTITUTION", f"Tries to sub off player thats not on the pitch. {team}, {player_a} => {player_b} ({self.game.date})")
            return
        
        if self.player_in.matches["sub out"]:
            if game in self.player_in.matches["sub out"]:
                prints.warning("SUBSTITUTION", f"Tries to sub in player thats been subbed off: {self}")
                return

        self.player_in.matches["sub in"][game] = self
        self.player_out.matches["sub out"][game] = self
        self.current_score = game.result.get_result()

        self.player_in.matches["benched"].remove(game)
        assert game in self.player_in.matches["sub in"], f"{self.player_in} subbed in, but not saved"
        assert game in self.player_out.matches["sub out"], f"{self.player_out} subbed out, but not saved"
        assert not self in self.player_in.matches["benched"], f"{self.player_in} subbed in, but still in benched"

    def __repr__(self) -> str:
        return f"{self.team}, {self.player_in} => {self.player_out} ({self.game.date})"


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
