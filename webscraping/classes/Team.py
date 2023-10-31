import tools.prints as prints
import tools.regex_tools as rt
from bs4 import BeautifulSoup
from classes.Page import Page
from classes.Player import Player


class Team():
    def __init__(self, page):
        self.players = []
        self.page = page
        self.name = None
        self.number = None
        self.position = None
        self._init_players()

    def print_team(self):
        self.players.sort()
        a = (55-len(self))
        prints.header(f"{self} ({len(self.players)}){' '*a}(ST, SI, SO, BE)")
        for player in self.players:
            prints.row(f"   {player.print_row()}")

    def set_navn(self):
        self.name = self._set_navn()

    def get_player_influence(self):
        for player in self.players:
            result = player.results_while_playing()
            output = []
            first = True
            for res in result:
                if first:
                    print(player)
                    first = False
                if res:
                    game, results, sub_time = res
                    in_t, out_t = sub_time
                    pre, post, end = results
                    home_pre, away_pre = pre
                    home_post, away_post = post
                    for_goals = 0
                    against_goals = 0

                    if game.home == self:
                        for_goals = home_post - home_pre
                        against_goals = away_post - away_pre

                    elif game.away == self:
                        for_goals = away_post - away_pre
                        against_goals = home_post - home_pre

                    actual_res = "(draw)"
                    if end[0] > end[1]:
                        if game.home == self:
                            actual_res = "(win) "
                        else:
                            actual_res = "(loss)"
                    if end[0] < end[1]:
                        if game.home == self:
                            actual_res = "(loss)"
                        else:
                            actual_res = "(win) "


                    personal_res = "(draw)"
                    if for_goals > against_goals:
                        personal_res = "(win) "
                    elif for_goals < against_goals:
                        personal_res = "(loss)"

                    
                    total_goals = for_goals-against_goals
                    in_t = "'"+str(in_t)
                    out_t = "'"+str(out_t)
                    print(f" {in_t:>3}-{out_t:>3} | {home_pre:>2} - {away_pre:<2} -> {home_post:>2} - {away_post:<2} {personal_res:<4} | Result {end[0]:>2} - {end[1]:<2} {actual_res:<4} | for: {for_goals:>2}, agst: {against_goals:>2}, tot: {total_goals:>3} | {game.result.page.url}")

    def get_player(self, name, url=False, warning=False):
        if not url:
            prints.warning(self, "Player url not provided")
            exit()

        
        # Only suggest unless we have the correct url.
        for player in self.players:
            if url == player.url:
                return player
            if name == player.name:
                input(f"HÆÆÆÆ: {url} !=??? {player.url}")
        if warning:
            prints.warning(self, f"Created a new player: {name}, lacking number and position")

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
        return self.name.title().replace("Menn Senior ", "")

    def __eq__(self, other) -> bool:
        if type(other) == str:
            return self.name.title().replace("Menn Senior ", "") == other
        if type(other) == Team:
            return self.name == other.name
