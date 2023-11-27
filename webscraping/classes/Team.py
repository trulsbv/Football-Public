import tools.prints as prints
import tools.regex_tools as rt
from bs4 import BeautifulSoup
from classes.Page import Page
from classes.Player import Player

class Team():
    s = 0
    def __init__(self, page, tournament):
        self.tournament = tournament
        self.players = []
        self.page = page
        self.name = None
        self.games = {"home": [], "away": []}
        self._init_players()
        self.points = 0
        self.goal_diff = 0
        self.goals_scored_home = 0
        self.goals_conceded_home= 0
        self.goals_scored_away = 0
        self.goals_conceded_away = 0
        self.goals_scored_total = 0
        self.goals_conceded_total = 0

    def get_all_games(self):
        out = []
        out.extend(self.games['home'])
        out.extend(self.games['away'])
        out = sorted(out, key=lambda x: x.date)
        return out

    def add_game(self, game):
        self.tournament.weather.add(game.weather.conditions)
        self.tournament.pitches["surfaces"].add(game.pitch.surface)
        home, away = game.score
        self.games["home"].append(game) if game.home == self else self.games["away"].append(game)
        if game.home == self:
            self.goal_diff += home-away
            self.goals_scored_home += home
            self.goals_conceded_home += away
            self.goals_scored_total += home
            self.goals_conceded_total += away
            if home > away:
                self.points += 3
            elif home == away:
                self.points += 1
        elif game.away == self:
            self.goal_diff += away-home
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
        a = (55-len(self))
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
            s += f" | avg. {' '*(5-len(str(i[1][1])))}{prints.get_fore_color_int(i[1][1])} per game ({str(len(i[2].results_while_playing())):>2})"
            s += f" | avg. {str(int(i[1][2])):>2} minutes per game"
            s += f" | avg. {' '*(8-len(str(i[1][3])))}{prints.get_fore_color_int(i[1][3])} points per minute"
            
            print(s)
    
    def print_team_influence(self, individual = True):
        first = True
        for player in self.players:
            if not first:
                print("\n")
            first = False
            player.print_influence(individual)
            
    def get_player(self, name="UnreportedPlayer", url=False, warning=False, number=False, position=False):
        if name == False:
            name = "UnreportedPlayer"
        # Only suggest unless we have the correct url.
        for player in self.players:
            if url == player.url:
                return player
        if warning:
            prints.warning(self, f"Created a new player: {name} ({url}), lacking number and position")
        player = Player(self, name, url)
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
        if self.name == None:
            self.set_navn()
        return self.name.title().replace("Menn Senior ", "").replace(" A", "").replace(" Men 01", "")

    def __eq__(self, other) -> bool:
        if type(other) == str:
            if self.name:
                return self.name.title().replace("Menn Senior ", "") == other
        if type(other) == Team:
            return self.name == other.name
