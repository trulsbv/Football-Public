import tools.prints as prints
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.statistic_tools as statt
import settings
from bs4 import BeautifulSoup
from classes.Page import Page
from classes.Player import Player
from classes.Event import (
    OwnGoal,
    PenaltyGoal,
    PlayGoal,
    RedCard,
    YellowCard,
    Goal,
)


class Team:
    def __init__(self, page, tournament):
        self.tournament = tournament
        self.players: list[Player] = []
        self.page = page
        self.name = None
        self.games = {"home": [], "away": []}
        self.conceded_goals = []
        self._init_players()
        self.points = 0
        self.goal_diff = 0
        self.goals_scored_home = 0
        self.goals_conceded_home = 0
        self.goals_scored_away = 0
        self.goals_conceded_away = 0
        self.goals_scored_total = 0
        self.goals_conceded_total = 0

    def stat_to_str(self, lst) -> str:
        s = ""
        for item in lst:
            if not s:
                s += f"{item:>2}"
                continue
            s += f", {item:>2}"
        return s

    def print_team_stats(self) -> None:
        stats = [Goal, PlayGoal, PenaltyGoal, OwnGoal, YellowCard, RedCard]
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

    def get_all_games(self):
        out = []
        out.extend(self.games["home"])
        out.extend(self.games["away"])
        out = sorted(out, key=lambda x: x.date)
        return out

    def add_game(self, game):
        self.tournament.weather.add(game.weather.conditions)
        self.tournament.pitches["surfaces"].add(game.pitch.surface)
        home, away = game.score
        (
            self.games["home"].append(game)
            if game.home == self
            else self.games["away"].append(game)
        )
        if game.home == self:
            self.goal_diff += home - away
            self.goals_scored_home += home
            self.goals_conceded_home += away
            self.goals_scored_total += home
            self.goals_conceded_total += away
            if home > away:
                self.points += 3
            elif home == away:
                self.points += 1
        elif game.away == self:
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
            prints.error(self, f"Was not {game.home} or {game.away}")
            exit()

    def print_team(self):
        self.players.sort()
        a = 55 - len(self)
        prints.header(f"{self} ({len(self.players)}){' '*a}(ST, SI, SO, BE)")
        for player in self.players:
            prints.row(f"   {player.print_row()}")

    def set_navn(self):
        self.name = self._set_navn()

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
        inp = sorted(inp, key=lambda x: x[0], reverse=True)
        for i in inp:
            s = f"{str(i[2]):>35}, personal total: {str(i[1][0]):>3}"
            s += f" | avg. {' '*(5-len(str(i[1][1])))}"
            s += f"{prints.get_fore_color_int(i[1][1])} per game "
            s += f"({str(len(i[2].results_while_playing())):>2})"
            s += f" | avg. {str(int(i[1][2])):>2} minutes per game"
            s += f" | avg. {' '*(8-len(str(i[1][3])))}"
            s += f"{prints.get_fore_color_int(i[1][3])} points per minute"

            print(s)

    def print_team_influence(self, individual=True):
        first = True
        for player in self.players:
            if not first:
                print("\n")
            first = False
            player.print_influence(individual)

    def get_player(
        self,
        name="UnreportedPlayer",
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
        if warning:
            prints.warning(
                self,
                f"Created a new player: {name} ({url}), lacking number and position",
            )
        player = Player(self, name, url)
        ft.log(f"Created {player} ({url})")
        self.players.append(player)
        return player

    def _init_players(self):
        url = self.page.url.replace("hjem", "spillere")
        players = Page(url)
        document = BeautifulSoup(players.html.text, "html.parser")
        ul = document.find("section")
        for found in ul.find_all("li"):
            number, link, name, position = rt.get_player_info(found)
            player = self.get_player(name, link)
            player.number = number
            player.position = position

    def _set_navn(self):
        if not rt.get_team_name(self.page.html.text):
            exit()
        return rt.get_team_name(self.page.html.text)

    def _set_krets(self):
        return rt.get_krets(self.html.text)

    def __len__(self):
        return len(self.name.title().replace("Menn Senior ", ""))

    def __repr__(self) -> str:
        if self.name is None:
            self.set_navn()

        return (
            self.name.title()
            .replace("Menn Senior ", "")
            .replace(" A", "")
            .replace(" Men 01", "")
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            if self.name:
                return self.name.title().replace("Menn Senior ", "") == other
        if isinstance(other, Team):
            return self.name == other.name