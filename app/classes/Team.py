import tools.prints as prints
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.statistic_tools as statt
import settings
from classes.Graphs import DirectedCumulativeGraph
from classes.Page import Page
from bs4 import BeautifulSoup
from classes.Player import Player
from classes.Event import (
    OwnGoal,
    Penalty,
    PlayGoal,
    RedCard,
    YellowCard,
    Goal,
    Substitute,
)


class Team:
    def __init__(self, url, tournament):
        self.tournament = tournament  # TODO: Don't work with multiple competitons
        self.url = url

        self.games = {"home": [], "away": []}
        self.conceded_goals = []
        self.points = 0
        self.goal_diff = 0
        self.goals_scored_home = 0
        self.goals_conceded_home = 0
        self.goals_scored_away = 0
        self.goals_conceded_away = 0
        self.goals_scored_total = 0
        self.goals_conceded_total = 0
        self.players = []
        self.player_by_role = {}
        self.graphs = {
            "assists": DirectedCumulativeGraph()
        }
        self._load()

    def _load(self):
        data = ft.get_json(ft.TF_url_to_id(self.url), "Teams")

        if data:
            self.name = data["data"]["name"]
            self.nickname = data["data"]["nickname"]
            self.players: list[Player] = []
            urls = data["data"]["player_urls"].split(",")
            for i in range(len(urls)):
                urls[i] = urls[i].replace("'", "").replace("[", "").replace("]", "").strip()
            for url in urls:
                self.players.append(Player(self, url=url, graphs=self.graphs))
        else:
            self.page = Page(self.url)
            document = BeautifulSoup(self.page.html.text, "html.parser")
            table = document.find("table", class_="items")
            rows = table.find_all("tr")
            self.player_urls = set()
            for row in rows[1:]:
                cells = row.find_all(["th", "td"])
                if not cells:
                    continue
                urls = rt.find_urls(str(row))
                for url in urls:
                    if "profil" in url:
                        self.player_urls.add(url)

            self.players: list[Player] = []
            for url in self.player_urls:
                self.players.append(Player(self, url=url, graphs=self.graphs))

            data = document.find("h1", class_="data-header__headline-wrapper")
            self.name = " ".join(data.get_text().strip().split())
            self.nickname = input(f"\n{self.name} as: ")
            while len(self.nickname) > 11:
                self.nickname = input("Too long, try again: ")

            ft.write_json(self._to_json(), ft.TF_url_to_id(self.url), "Teams")

    def _to_json(self):
        m = {
            "meta": {
                "version": 1,
                "date": str(settings.DATE)
            },
            "data": {
                "name": self.name,
                "nickname": self.nickname,
                "player_urls": str(list(self.player_urls))
            }
        }
        return m

    def stat_to_str(self, lst) -> str:
        s = ""
        for item in lst:
            if not s:
                s += f"{item:>2}"
                continue
            s += f", {item:>2}"
        return s

    def print_team_stats(self) -> None:
        stats = [Goal, PlayGoal, Penalty, OwnGoal, YellowCard, RedCard]
        team_stats = {}
        for player in self.players:
            player_stats = player.get_player_stats(stats)
            for stat in player_stats:
                if stat not in team_stats:
                    team_stats[stat] = player_stats[stat]
                else:
                    team_stats[stat] = [x + y for x, y in zip(team_stats[stat], player_stats[stat])]
        s = f"{self}\n"
        s += "Event / Time "
        for time in statt.times_x_fits_in_y(settings.FRAME_SIZE, settings.GAME_LENGTH):
            s += f"-{time:<3}"
        conceded = statt.iterate_events(self.conceded_goals)
        s += f"\n   Conceded: {self.stat_to_str(conceded)}"
        s += f"   ({sum(conceded)})"
        for stat in team_stats:
            s += f"\n{stat.__name__:>11}: {self.stat_to_str(team_stats[stat])}"
            s += f"   ({sum(team_stats[stat])})"
        print(s)

    def __hash__(self):
        return hash(self.name)

    def current_position(self):
        if len(self.games["home"]) + len(self.games["away"]) < 5:
            return "-"
        return self.tournament.current_position(self)

    def get_all_games(self):
        out = []
        out.extend(self.games["home"])
        out.extend(self.games["away"])
        out = sorted(out, key=lambda x: x.round)
        return out

    def get_all_games_by_date(self):
        out = []
        out.extend(self.games["home"])
        out.extend(self.games["away"])
        out = sorted(out, key=lambda x: x.date)
        return out

    def get_prev_5_games(self):
        lst = self.get_all_games_by_date().copy()
        lst.reverse()
        if len(lst) < 5:
            return lst
        return lst[:5]

    def WDL_games(self, games):
        s = ""
        for game in games:
            s += game.WDL_team(self)
        return s

    def add_game(self, game):
        self.tournament.pitches["surfaces"].add(game.pitch.surface)
        home, away = game.score
        if game.teams["home"]["team"] == self:
            self.games["home"].append(game)
        else:
            self.games["away"].append(game)
        if game.teams["home"]["team"] == self:
            self.goal_diff += home - away
            self.goals_scored_home += home
            self.goals_conceded_home += away
            self.goals_scored_total += home
            self.goals_conceded_total += away
            if home > away:
                self.points += 3
            elif home == away:
                self.points += 1
        elif game.teams["away"]["team"] == self:
            self.goal_diff += away - home
            self.goals_scored_away += away
            self.goals_conceded_away += home
            self.goals_scored_total += away
            self.goals_conceded_total += home
            if home < away:
                self.points += 3
            elif home == away:
                self.points += 1
        else:
            prints.error(self, f"Was not {game.teams['home']['team']} or {game.teams['away']['team']}")
            exit()

    def print_team(self):
        self.players.sort(key=lambda x: x.role)
        prints.header(f"{self} ({len(self.players)} players)")
        s = "  POSITION"
        s += " " * 23 + "NAME       NR    PTS  SRT  IN OUT BNCH  SCR  AS"
        s += "   W   D   L"
        prints.header(s)
        for player in self.players:
            prints.row(f"{player.print_row()}")

    def get_player_influence(self):
        output = {}
        for player in self.players:
            output[player] = player.get_influence()
        return output

    def get_top_performers(self, category="ppg"):
        output = []
        self.get_player_influence()
        for player in self.players:
            result = player.get_performance(category)
            if result:
                output.append(result)
        return output

    def print_top_performers(self):
        inp = self.get_top_performers()
        inp = sorted(inp, key=lambda x: x[2].get_points(), reverse=True)
        for i in inp:
            s = f"{str(i[2]):>35}, personal total: {str(i[1][0]):>3}"
            s += f" | avg. {' '*(5-len(str(i[1][1])))}"
            s += f"{prints.get_fore_color_int(i[1][1])} per game "
            s += f"({str(len(i[2].results_while_playing())):>2})"
            s += f" | avg. {str(int(i[1][2])):>2} minutes per game"
            s += f" | avg. {' '*(8-len(str(i[1][3])))}"
            s += f"{prints.get_fore_color_int(i[1][3])} points per minute"
            s += f" | POINTS: {i[2].get_points()} ({i[2].points})"

            print(s)

    def print_team_influence(self, individual=True):
        first = True
        for player in self.players:
            if not first:
                print("\n")
            first = False
            player.print_influence(individual)

    def get_player_names(self):
        names = []
        for player in self.players:
            names.append(player.name)
        return names

    def get_player_urls(self):
        names = []
        for player in self.players:
            names.append(player.url)
        return names

    def get_player(
        self,
        name=False,
        url=False,
        warning=False,
        number=False,
        position=False,
    ):
        if url and "=" in url:
            url = url.split("=")[1]
        if name is False:
            name = "UnreportedPlayer"
        # Only suggest unless we have the correct url.
        for player in self.players:
            if url == player.url:
                return player
            if name == player.name:
                return player
        if warning:
            prints.warning(
                self,
                f"Created a new player: {name} ({url}), lacking number and position",
            )
        if not url:
            ft.log(name)
            prints.error(self, f"{name} does not have URL!")
        player = Player(self, url=url, graphs=self.graphs)
        ft.log(f"Created {player} ({url})")
        self.players.append(player)
        return player

    def _set_krets(self):
        return rt.get_krets(self.html.text)

    def __len__(self):
        return len(self.name.title().replace("Menn Senior ", ""))

    def __repr__(self) -> str:
        return self.nickname

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            if self.name:
                return self.name.title().replace("Menn Senior ", "") == other
        if isinstance(other, Team):
            return self.name == other.name

    def average_player_points(self):
        return round(self.total_player_points()/len(self.get_all_games()), 4)

    def total_player_points(self):
        ctr = 0
        for player in self.players:
            ctr += player.points
        return ctr

    def assign_points_stats(self, stat, number, game):
        if stat not in ["Total shots",
                        "Shots off target",
                        "Shots saved",
                        "Corners",
                        "Free kicks",
                        "Fouls",
                        "Offsides"]:
            prints.warning("Team assign_points_stats", f"'{stat}' not handled")
            exit()
        hometeam = {}
        awayteam = {}
        for player in self.players:
            hometeam[player] = player.get_playtime_game(game)/90
        for player in game.opponent(self).players:
            awayteam[player] = player.get_playtime_game(game)/90

        if stat == "Total shots":
            ATTACK_SHOT = 0.5 * number
            DEFENCE_SHOT = -0.5 * number
            self.share_points_stats(hometeam,
                                    ATTACK_SHOT,
                                    ATTACK_SHOT*0.5,
                                    ATTACK_SHOT*0.2,
                                    ATTACK_SHOT*0.1)
            self.share_points_stats(awayteam,
                                    DEFENCE_SHOT*0.1,
                                    DEFENCE_SHOT*0.4,
                                    DEFENCE_SHOT,
                                    DEFENCE_SHOT*0.2)
        elif stat == "Shots off target":
            ATTACK_SHOT_OFF_TARGET = -0.1 * number
            DEFENCE_SHOT_OFF_TARGET = 0.2 * number
            self.share_points_stats(hometeam,
                                    ATTACK_SHOT_OFF_TARGET,
                                    ATTACK_SHOT_OFF_TARGET*0.5,
                                    ATTACK_SHOT_OFF_TARGET*0.1,
                                    ATTACK_SHOT_OFF_TARGET*0)
            self.share_points_stats(awayteam,
                                    DEFENCE_SHOT_OFF_TARGET*0.1,
                                    DEFENCE_SHOT_OFF_TARGET*0.4,
                                    DEFENCE_SHOT_OFF_TARGET,
                                    DEFENCE_SHOT_OFF_TARGET*0.3)
        elif stat == "Shots saved":
            KEEPER_SAVED = 0.3 * number
            self.share_points_stats(hometeam,
                                    KEEPER_SAVED*0,
                                    KEEPER_SAVED*0,
                                    KEEPER_SAVED*0.2,
                                    KEEPER_SAVED)
        elif stat == "Corners":
            ATTACK_CORNER = 0.1 * number
            DEFENCE_CORNER = -0.1 * number
            self.share_points_stats(hometeam,
                                    ATTACK_CORNER,
                                    ATTACK_CORNER*0.8,
                                    ATTACK_CORNER*0.3,
                                    ATTACK_CORNER*0.1)
            self.share_points_stats(awayteam,
                                    DEFENCE_CORNER*0,
                                    DEFENCE_CORNER*0.3,
                                    DEFENCE_CORNER,
                                    DEFENCE_CORNER*0.4)
        elif stat == "Free kicks":
            return
        elif stat == "Fouls":
            ATTACK_FOUL = 0.02 * number
            DEFENCE_FOUL = -0.01 * number
            self.share_points_stats(awayteam,
                                    ATTACK_FOUL,
                                    ATTACK_FOUL,
                                    ATTACK_FOUL,
                                    ATTACK_FOUL)
            self.share_points_stats(hometeam,
                                    DEFENCE_FOUL,
                                    DEFENCE_FOUL,
                                    DEFENCE_FOUL,
                                    DEFENCE_FOUL*0.1)
        elif stat == "Offsides":
            ATTACK_OFFSIDE = -0.2 * number
            DEFENCE_OFFSIDE = 0.2 * number
            self.share_points_stats(hometeam,
                                    ATTACK_OFFSIDE,
                                    ATTACK_OFFSIDE*0.7,
                                    ATTACK_OFFSIDE*0.1,
                                    ATTACK_OFFSIDE*0)
            self.share_points_stats(awayteam,
                                    DEFENCE_OFFSIDE*0,
                                    DEFENCE_OFFSIDE*0.1,
                                    DEFENCE_OFFSIDE,
                                    DEFENCE_OFFSIDE*0.1)

    def share_points_stats(self, players, attack, midfield, defence, goalkeeper):
        for player in [value for value in players if value in self.player_by_role["Attack"]]:
            self.give_points(player, attack*players[player])
        for player in [value for value in players if value in self.player_by_role["midfield"]]:
            self.give_points(player, midfield*players[player])
        for player in [value for value in players if value in self.player_by_role["Defender"]]:
            self.give_points(player, defence*players[player])
        for player in [value for value in players if value in self.player_by_role["Goalkeeper"]]:
            self.give_points(player, goalkeeper*players[player])

    def assign_points(self, event):
        """
            This needs to be moved! Does not make sense to assign points in Team
        """
        START_POINTS = 10  # Connected to Game.py
        GOAL_POINTS = 12
        GOAL_SHARE_ATTACK = 0.6
        GOAL_SHARE_MIDFIELD = 0.4
        GOAL_SHARE_DEFENCE = 0.2
        GOAL_SHARE_GOALKEEPER = 0.2
        ASSIST_POINTS = 10
        PENALTY_POINTS = 3
        PENALTY_FOULED_POINTS = 3
        PENALTY_SAVED = -10
        GOALKEEPER_PENALTY_NOT_SAVED = -2
        GOALKEEPER_PENALTY_SAVED = 10
        OWN_GOAL_POINTS = -5
        OWN_GOAL_SHARE_ATTACK = 0.2
        OWN_GOAL_SHARE_MIDFIELD = 0.4
        OWN_GOAL_SHARE_DEFENCE = 0.7
        OWN_GOAL_SHARE_GOALKEEPER = 0.3
        YELLOW_PENALTY = -8
        RED_PENALTY = -20

        xi = event.game.teams["home"]["xi"] if self == event.game.teams["home"]["team"] else event.game.teams["away"]["xi"]
        if isinstance(event, Goal):
            self.give_points(event.player, GOAL_POINTS)
            if event.assist:
                self.give_points(event.assist.player, ASSIST_POINTS)
            self.share_points(xi,
                              GOAL_POINTS,
                              GOAL_SHARE_ATTACK,
                              GOAL_SHARE_MIDFIELD,
                              GOAL_SHARE_DEFENCE,
                              GOAL_SHARE_GOALKEEPER)

        if isinstance(event, Penalty):
            if event.goal:
                self.give_points(event.player, PENALTY_POINTS)
                if event.keeper:
                    self.give_points(event.keeper, GOALKEEPER_PENALTY_NOT_SAVED)
            else:
                self.give_points(event.player, PENALTY_SAVED)
                if event.keeper:
                    self.give_points(event.keeper, GOALKEEPER_PENALTY_SAVED)
            if event.assist:
                self.give_points(event.assist.player, PENALTY_FOULED_POINTS)

        if isinstance(event, OwnGoal):
            self.give_points(event.player, OWN_GOAL_POINTS)
            self.share_points(xi,
                              OWN_GOAL_POINTS,
                              OWN_GOAL_SHARE_ATTACK,
                              OWN_GOAL_SHARE_MIDFIELD,
                              OWN_GOAL_SHARE_DEFENCE,
                              OWN_GOAL_SHARE_GOALKEEPER)

        if isinstance(event, Substitute):
            diff = round(event.time/90*START_POINTS, 4)
            if event._in:
                self.give_points(event._in, START_POINTS-diff)
            self.give_points(event._out, START_POINTS-diff)

        if isinstance(event, Substitute):
            diff = START_POINTS-round(event.time/90*START_POINTS, 4)
            if event._in:
                self.give_points(event._in, diff)
            self.give_points(event._out, diff*-1)

        if isinstance(event, YellowCard):
            self.give_points(event.player,  YELLOW_PENALTY)

        if isinstance(event, RedCard):
            self.give_points(event.player,  RED_PENALTY)

    def give_points(self, player, points):
        player.points = round(player.points + points, 4)

    def share_points(self, xi, points, attack, midfield, defence, goalkeeper):
        for player in [value for value in xi if value in self.player_by_role["Attack"]]:
            self.give_points(player, points * attack)
        for player in [value for value in xi if value in self.player_by_role["midfield"]]:
            self.give_points(player, points * midfield)
        for player in [value for value in xi if value in self.player_by_role["Defender"]]:
            self.give_points(player, points * defence)
        for player in [value for value in xi if value in self.player_by_role["Goalkeeper"]]:
            self.give_points(player, points * goalkeeper)
