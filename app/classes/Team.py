import tools.prints as prints
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.statistic_tools as statt
import settings
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
                self.players.append(Player(self, url=url))
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
                self.players.append(Player(self, url=url))

            data = document.find("h1", class_="data-header__headline-wrapper")
            self.name = " ".join(data.get_text().strip().split())
            self.nickname = input(f"\n{self.name} as: ")

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

    def get_all_games(self):
        out = []
        out.extend(self.games["home"])
        out.extend(self.games["away"])
        out = sorted(out, key=lambda x: x.date)
        return out

    def add_game(self, game):
        self.tournament.pitches["surfaces"].add(game.pitch.surface)
        home, away = game.score
        if game.home == self:
            self.games["home"].append(game)
        else:
            self.games["away"].append(game)
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
        self.players.sort(key=lambda x: x.position)
        prints.header(f"{self} ({len(self.players)} players)")
        s = " " * 22 + "POSITION"
        s += " " * 23 + "NAME  NR   SRT  IN OUT BNCH  SCR AS."
        s += "  WIN, LOSS, DRAW"
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
        player = Player(self, url)
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
