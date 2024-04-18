import tools.prints as prints


class Event:
    def __init__(self, game, time, team):
        self.game = game
        self.time = int(time)
        self.team = team

    def to_dict(self) -> str:
        return {"game": self.game, "time": self.time, "team": self.team}

    def __repr__(self) -> str:
        return f"{self.time} "


class Booking(Event):
    def __init__(self, game, time, team, player, reason):
        super().__init__(game, time, team)
        self.player = player
        self.player.events.append(self)
        self.reason = reason

    def to_dict(self) -> str:
        cur = {
            "type": "Booking",
            "player": self.player,
            "reason": self.reason if self.reason else "Unknown",
        }
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return super().__repr__()


class YellowCard(Booking):
    def __init__(
        self, game=None, time=None, team=None, player=None, reason=None, lst=None
    ):
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            player = lst[3]
            reason = lst[4]
        super().__init__(game, time, team, player, reason)
        team.assign_points(self)
        self.name = "Yellow card"

    def to_dict(self) -> str:
        cur = {
            "card": "Yellow",
        }
        return {**cur, **super().to_dict()}

    def high_level_dict(self) -> str:
        return {
            "name": "Yellow card",
            "team": self.team,
            "time": self.time,
            "player": self.player
        }

    def __repr__(self) -> str:
        return super().__repr__() + " yellow card"

    def to_json(self):
        return {
            "type": "Yellow card",
            "reason": self.reason,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }


class RedCard(Booking):
    def __init__(
        self, game=None, time=None, team=None, player=None, reason=None, lst=None
    ):
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            player = lst[3]
            reason = lst[4]
        super().__init__(game, time, team, player, reason)
        team.assign_points(self)
        self.name = "Red card"

    def to_dict(self) -> str:
        cur = {
            "card": "Red",
        }
        return {**cur, **super().to_dict()}

    def high_level_dict(self) -> str:
        return {
            "name": "Red card",
            "team": self.team,
            "time": self.time,
            "player": self.player
        }

    def __repr__(self) -> str:
        return super().__repr__() + " red card"

    def to_json(self):
        return {
            "type": "Red card",
            "reason": self.reason,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
        }


class Substitute(Event):
    def __init__(
        self, game=None, time=None, team=None, players=None, reason=None, lst=None
    ):
        self.name = "Substitution"
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            players = lst[3]
            reason = lst[4]
        super().__init__(game, time, team)
        self.reason = reason
        _out, _in = players
        if team == game.teams["home"]["team"]:
            xi = game.teams["home"]["xi"]
            bench = game.teams["home"]["bench"]
        else:
            xi = game.teams["away"]["xi"]
            bench = game.teams["away"]["bench"]

        self._out = team.get_player(url=_out, warning=True)
        if _in:
            self._in = team.get_player(url=_in, warning=True)

            res = self.replace_item(xi, self._out, self._in)
            if res is False:
                prints.warning(self, f"{self._out} not on pitch. {self.game.url}")
            res = self.replace_item(bench, self._in, self._out)
            if res is False:
                if bench:  # Only display the warning if there is a bench
                    prints.warning(self, f"{self._in} not on bench! {self.game.url}")
        else:
            self._in = None
            res = self.replace_item(xi, self._out, None)
            if res is False:
                prints.warning(self, f"{self._out} not on pitch! {self.game.url}")

        self._out.matches["sub out"][game] = self
        if self._in:
            self._in.matches["sub in"][game] = self
            if game not in self._in.matches["benched"]:
                if team == game.teams["home"]["team"]:
                    game.teams["home"]["lineup"][1].append(self._in)
                elif team == game.teams["away"]["team"]:
                    game.teams["away"]["lineup"][1].append(self._in)
                else:
                    prints.error(self, f"Failed to put {team} as home/away: {game}")
            else:
                self._in.matches["benched"].remove(game)
        self.current_score = game.get_timed_result(self.time)
        team.assign_points(self)

    def replace_item(self, lst, old_item, new_item):
        for i in range(len(lst)):
            if lst[i] == old_item:
                lst[i] = new_item
                return
        return False

    def to_dict(self) -> str:
        cur = {
            "type": "Substitution",
            "in": self._in,
            "out": self._out,
            "reason": self.reason if self.reason else "Unknown",
        }
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return (
            super().__repr__()
            + f"{self.team}, {self._in} => {self._out} ({self.game.date})"
        )

    def high_level_dict(self) -> str:
        return {
            "name": "Substitution",
            "team": self.team,
            "time": self.time
        }

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
    def __init__(self, player, info, url):
        self.player = player
        player.events.append(self)
        self.inf = None if not info else info.strip()
        self.goal = None
        self.url = url
        self.name = "Assist"

    def to_dict(self) -> str:
        return {
            "type": "Assist",
            "by": self.player,
            "how": self.inf,
            "to": "ERROR: Unknown" if not self.goal else self.goal.player,
            "time": "ERROR: Unknown" if not self.goal else self.goal.time,
            "game": "ERROR: Unknown" if not self.goal else self.goal.game,
            "team": "ERROR: Unknown" if not self.goal else self.goal.team,
        }

    def to_json(self):
        return {
            "player_url": self.player.url,
            "info": self.inf,
        }

    def __repr__(self) -> str:
        if not self.goal:
            return self.url
        return f"Assist to {self.goal.player}: {self.inf} by {self.player}"


class Goal(Event):
    def __init__(self, game, time, team, player, assist, keeper):
        super().__init__(game, time, team)
        self.player = player
        self.player.events.append(self)
        self.assist = assist
        self.keeper = keeper

    def to_dict(self) -> str:
        cur = {
            "type": "Goal",
            "by": self.player,
            "assist": self.assist,
        }
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return super().__repr__()


class PlayGoal(Goal):
    def __init__(
        self,
        game=None,
        time=None,
        team=None,
        player=None,
        assist=None,
        info=None,
        keeper=None,
        lst=None,
    ):
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            player = lst[3]
            assist = lst[4]
            info = lst[5]
            keeper = lst[6]
        super().__init__(game, time, team, player, assist, keeper)
        opponent = game.opponent(team)
        opponent.conceded_goals.append(self)
        ConcededGoal(self, game.get_keeper(opponent))
        self.inf = info
        team.assign_points(self)
        self.name = "Play goal"

    def high_level_dict(self) -> str:
        return {
            "name": "Goal",
            "team": self.team,
            "time": self.time,
            "player": self.player,
            "type": self.inf
        }

    def to_dict(self) -> str:
        cur = {"action": "Active", "assist": self.assist, "how": self.inf}
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return super().__repr__() + f"Active goal by {self.player} against {self.keeper}"

    def to_json(self):
        return {
            "type": "Playgoal",
            "time": self.time,
            "info": self.inf,
            "assist": self.assist.to_json() if self.assist else None,
            "team_url": self.team.url,
            "player_url": self.player.url,
            "keeper_url": self.keeper.url,
        }


class Penalty(Goal):
    def __init__(
        self,
        game=None,
        time=None,
        team=None,
        player=None,
        goal=None,
        fouled=False,
        keeper=None,
        lst=None,
    ):
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            player = lst[3]
            goal = lst[4]
            fouled = lst[5]
            keeper = lst[6]
        super().__init__(game, time, team, player, fouled, keeper)
        self.goal = goal
        self.fouled = fouled
        self.inf = "Penalty"
        self.name = "Penalty goal"
        if goal:
            opponent = game.opponent(team)
            opponent.conceded_goals.append(self)
            ConcededGoal(self, game.get_keeper(opponent))
        team.assign_points(self)

    def high_level_dict(self) -> str:
        return {
            "name": "Goal",
            "team": self.team,
            "time": self.time,
            "player": self.player,
            "type": self.inf
        }

    def to_dict(self) -> str:
        cur = {
            "action": "Penalty",
            "keeper": self.keeper,
            "fouled": self.fouled if self.fouled else "Unknown",
            "goal": self.goal,
            "how": "Penalty"
        }
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return super().__repr__() + " penalty goal" if self.goal else "miss"

    def to_json(self):
        return {
            "type": "Penalty",
            "goal": True if self.goal else False,
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
            "keeper_url": None if not self.keeper else self.keeper.url,
            "fouled": self.fouled.to_json() if self.fouled else None,
        }


class OwnGoal(Goal):
    def __init__(self, game=None, time=None, team=None, player=None, keeper=None, lst=None):
        if lst:
            game = lst[0]
            time = lst[1]
            team = lst[2]
            player = lst[3]
            keeper = lst[4]
        super().__init__(game, time, team, player, None, keeper)
        team.conceded_goals.append(self)
        ConcededGoal(self, game.get_keeper(team))
        team.assign_points(self)
        self.inf = "Own goal"

    def high_level_dict(self) -> str:
        return {
            "name": "Goal",
            "team": self.game.opponent(self.team),
            "time": self.time,
            "player": "Own goal",
            "type": self.inf
        }

    def to_dict(self) -> str:
        cur = {
            "type": "Own goal",
        }
        return {**cur, **super().to_dict()}

    def __repr__(self) -> str:
        return super().__repr__() + f"Own goal by {self.player} at {self.time}"

    def to_json(self):
        return {
            "type": "OwnGoal",
            "time": self.time,
            "team_url": self.team.url,
            "player_url": self.player.url,
            "keeper_url": self.keeper.url,
        }


class ConcededGoal():
    def __init__(self, goal, keeper):
        self.goal = goal
        self.keeper = keeper
        self.keeper.events.append(self)

    def __repr__(self) -> str:
        return f"{self.keeper} conceded goal to {self.goal.player}"

    def to_dict(self) -> str:
        return {
                "type": "ConcededGoal",
                "time": self.goal.time,
                "by": self.keeper,
                "goal": self.goal,
                "game": self.goal.game,
                "how": self.goal.inf,
                "assist": None if not self.goal.assist else self.goal.assist.inf
            }
