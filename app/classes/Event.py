import tools.prints as prints


class Event:
    def __init__(self, game, time, team):
        self.game = game
        self.time = int(time)
        self.team = team

    def __repr__(self) -> str:
        return f"{self.time} "


class Booking(Event):
    def __init__(self, game, time, team, player, reason):
        super().__init__(game, time, team)
        self.player = player
        self.player.events.append(self)
        self.reason = reason

    def __repr__(self) -> str:
        return super().__repr__()


class YellowCard(Booking):
    def __init__(self, game, time, team, player, reason):
        super().__init__(game, time, team, player, reason)

    def __repr__(self) -> str:
        return super().__repr__() + " gult kort"

    def to_json(self):
        return {
            "type": "Yellow card",
            "reason": self.reason,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }


class RedCard(Booking):
    def __init__(self, game, time, team, player, reason):
        super().__init__(game, time, team, player, reason)

    def __repr__(self) -> str:
        return super().__repr__() + " rødt kort"

    def to_json(self):
        return {
            "type": "Red card",
            "reason": self.reason,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }


class Substitute(Event):
    def __init__(self, game, time, team, players, reason):
        super().__init__(game, time, team)
        self.reason = reason
        _out, _in = players
        if _in:
            self._out = team.get_player(url=_out, warning=True)
            self._in = team.get_player(url=_in, warning=True)

            if team == game.home:
                xi = game.home_xi
                bench = game.home_bench
            else:
                xi = game.away_xi
                bench = game.away_bench

            res = self.replace_item(xi, self._out, self._in)
            if res is False:
                prints.warning(self, f"{self._out} not in xi? {xi}")
            res = self.replace_item(bench, self._in, self._out)
            if res is False:
                prints.warning(self, f"{self._in} not on bench: {bench}")
        else:
            self._in = None
            self._out = team.get_player(url=_out, warning=True)
            if team == game.home:
                xi = game.home_xi
            else:
                xi = game.away_xi
            res = self.replace_item(xi, self._out, None)
            if res is False:
                prints.warning(self, f"{self._out} not in xi? {xi}")

        self._out.matches["sub out"][game] = self
        if self._in:
            self._in.matches["sub in"][game] = self
            if game not in self._in.matches["benched"]:
                if team == game.home:
                    game._save_home[1].append(self._in)
                elif team == game.away:
                    game._save_away[1].append(self._in)
                else:
                    prints.error(self, f"Failed to put {team} as home/away: {game}")

            else:
                self._in.matches["benched"].remove(game)

        self.current_score = game.get_timed_result(self.time)

    def replace_item(self, lst, old_item, new_item):
        for i in range(len(lst)):
            if lst[i] == old_item:
                lst[i] = new_item
                return
        return False

    def __repr__(self) -> str:
        return f"{self.team}, {self._in} => {self._out} ({self.game.date})"

    def to_json(self):
        out = None
        _in = None
        if self._in:
            _in = self._in.url
        try:
            out = {
                "type": "Substitution",
                "time": self.time,
                "team_url": self.team.url,
                "in_url": _in,
                "out_url": self._out.url,
                "reason": self.reason,
            }
        finally:
            return out


class Assist():
    def __init__(self, player, info):
        self.player = player
        player.events.append(self)
        self.info = info
        self.goal = None

    def to_json(self):
        return {
            "player_url": self.player.url,
            "info": self.info,
        }

    def __repr__(self) -> str:
        return f"{self.how} by {self.player}"


class Goal(Event):
    def __init__(self, game, time, team, player, assist):
        super().__init__(game, time, team)
        self.player = player
        self.player.events.append(self)
        self.assist = assist

    def __repr__(self) -> str:
        return super().__repr__()


class PlayGoal(Goal):
    def __init__(self, game, time, team, player, assist, info):
        super().__init__(game, time, team, player, assist)
        game.opponent(team).conceded_goals.append(self)
        self.info = info

    def __repr__(self) -> str:
        if self.assist:
            return super().__repr__() + f" active play goal (assist: {self.assist})"
        return super().__repr__() + " active play goal"

    def to_json(self):
        return {
            "type": "Playgoal",
            "time": self.time,
            "info": self.info,
            "assist": self.assist.to_json() if self.assist else None,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }


class Penalty(Goal):
    def __init__(self, game, time, team, player, goal: bool, keeper):
        super().__init__(game, time, team, player, False)
        self.goal = goal
        self.keeper = keeper
        if self.keeper:
            self.keeper.events.append(self)
        if goal:
            game.opponent(team).conceded_goals.append(self)

    def __repr__(self) -> str:
        return super().__repr__() + " penalty " + "goal" if self.goal else "miss"

    def to_json(self):
        return {
            "type": "Penalty",
            "goal": True if self.goal else False,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
            "keeper_url": None if not self.keeper else self.keeper.url
        }


class OwnGoal(Goal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player, None)
        team.conceded_goals.append(self)

    def __repr__(self) -> str:
        return super().__repr__() + " own goal"

    def to_json(self):
        return {
            "type": "OwnGoal",
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }
