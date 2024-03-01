import tools.prints as prints
from errors import DontCare


class Event:
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
        return super().__repr__() + " gult kort"

    def get_analysis(self):
        return {
            "type": "Yellow card",
            "time": self.time,
            "team_url": self.team.page.url,
            "player_url": self.player.url,
        }


class RedCard(Booking):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

    def __repr__(self) -> str:
        return super().__repr__() + " rødt kort"

    def get_analysis(self):
        return {
            "type": "Red card",
            "time": self.time,
            "team_url": self.team.page.url,
            "player_url": self.player.url,
        }


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

        if player_a in sheet[0]:  # Player_a is on pitch, player b is on
            self.player_in = player_b
            if player_b not in sheet[1]:
                prints.warning(
                    "SUBSTITUTION",
                    f"{game} -> {player_b} not on {sheet[1]} bench, perheps on field: {sheet[0]}",
                )
                return
            self.player_out = player_a

            sheet[0].append(player_b)
            sheet[0].remove(player_a)
            sheet[1].append(player_a)
            sheet[1].remove(player_b)
            assert (player_a not in sheet[0]) and (player_a in sheet[1])
            assert (player_b not in sheet[1]) and (player_b in sheet[0])
        elif player_b in sheet[0]:  # Player_b is on pitch, player a is on bench
            self.player_in = player_a
            if player_a not in sheet[1]:
                prints.warning(
                    "SUBSTITUTION",
                    f"{game} -> {player_a} not on {sheet[1]} bench, perheps on field: {sheet[0]}",
                )
                return
            self.player_out = player_b
            sheet[0].append(player_a)
            sheet[0].remove(player_b)
            sheet[1].append(player_b)
            sheet[1].remove(player_a)
            assert (player_a not in sheet[1]) and (player_a in sheet[0])
            assert (player_b not in sheet[0]) and (player_b in sheet[1])
        else:
            prints.warning(
                "SUBSTITUTION",
                "Tries to sub off player thats not on the pitch.",
                "{team}, {player_a} => {player_b} ({self.game.date})",
            )
            return

        if self.player_in.matches["sub out"]:
            if game in self.player_in.matches["sub out"]:
                prints.warning(
                    "SUBSTITUTION",
                    f"Tries to sub in player thats been subbed off: {self}",
                )
                return

        self.player_in.matches["sub in"][game] = self
        self.player_out.matches["sub out"][game] = self
        self.current_score = game.result.get_result()
        print("\n\n\n\n\\n\n\n")
        print(self.player_in.matches["benched"])

        self.player_in.matches["benched"].remove(game)
        assert (
            game in self.player_in.matches["sub in"]
        ), f"{self.player_in} subbed in, but not saved"
        assert (
            game in self.player_out.matches["sub out"]
        ), f"{self.player_out} subbed out, but not saved"
        assert (
            self not in self.player_in.matches["benched"]
        ), f"{self.player_in} subbed in, but still in benched"

    def __repr__(self) -> str:
        return f"{self.team}, {self.player_in} => {self.player_out} ({self.game.date})"

    def get_analysis(self):
        try:
            return {
                "type": "Substitution",
                "time": self.time,
                "team_url": self.team.page.url,
                "in_url": self.player_in.url,
                "out_url": self.player_out.url,
            }
        except DontCare:
            return None


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
        return super().__repr__() + " spillemål"

    def get_analysis(self):
        return {
            "type": "Playgoal",
            "time": self.time,
            "team_url": self.team.page.url,
            "player_url": self.player.url,
        }


class PenaltyGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

    def __repr__(self) -> str:
        return super().__repr__() + " straffemål"

    def get_analysis(self):
        return {
            "type": "PenaltyGoal",
            "time": self.time,
            "team_url": self.team.page.url,
            "player_url": self.player.url,
        }


class OwnGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

    def __repr__(self) -> str:
        return super().__repr__() + " own goal"

    def get_analysis(self):
        return {
            "type": "OwnGoal",
            "time": self.time,
            "team_url": self.team.page.url,
            "player_url": self.player.url,
        }
