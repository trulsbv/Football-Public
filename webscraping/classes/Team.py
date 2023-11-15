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
        self.games = []
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
        output = {}
        for player in self.players:
            output[player] = player.get_influence()
        return output
    
    def get_top_performers(self, category="ppg"):
        output = []
        influence = self.get_player_influence()
        for player in self.players:
            if "goals_for" not in player.influence:
                # Skipping players that hasn't played any minutes
                continue
            p_tot = player.influence['goals_for'] - player.influence['goals_against']    
            ppg = 0 if player.influence['num_games'] == 0 else round(p_tot/player.influence['num_games'], 2)
            mpg = round(player.influence['num_minutes']/player.influence['num_games'], 0)
            if p_tot != 0:
                ppm = round(p_tot/player.influence['num_minutes'], 5)
            else: ppm = 0
            li = [p_tot, ppg, mpg, ppm]
            if category == "p_tot": output.append([p_tot, li, player])
            if category == "ppg": output.append([ppg, li, player])
            if category == "mpg": output.append([mpg, li, player])
            if category == "ppm": output.append([ppm, li, player])
        return output


    def print_top_performers(self):
        inp = self.get_top_performers()
        inp = sorted(inp, key=lambda x: x[0], reverse=True)
        for i in inp:
            s = f"{str(i[2]):>35}, personal total: {str(i[1][0]):>3}"
            s += f" | avg. {' '*(5-len(str(i[1][1])))}{prints.get_fore_color_int(i[1][1])} per game ({str(len(i[2].results_while_playing())):>2})"
            s += f" | avg. {str(int(i[1][2])):>2} minutes per game"
            s += f" | avg. {prints.get_fore_color_int(i[1][3])} points per minute"
            
            print(s)
    
    def print_player_influence(self, influence):
        game, loc, sub_time, pre, post, end, goals_for, goals_against = influence
        in_t, out_t = sub_time
        home_pre, away_pre = pre
        home_post, away_post = post
        total_goals = goals_for-goals_against
        actual_res = prints.get_yellow_fore("(draw)")
        if end[0] > end[1]:
            if game.home == self:
                actual_res = prints.get_green_fore("(win) ")
            else:
                actual_res = prints.get_red_fore("(loss)")
        if end[0] < end[1]:
            if game.home == self:
                actual_res = prints.get_red_fore("(loss)")
            else:
                actual_res = prints.get_green_fore("(win) ")

        personal_res = prints.get_yellow_fore("(draw)")
        if goals_for > goals_against:
            personal_res = prints.get_green_fore("(win) ")
        elif goals_for < goals_against:
            personal_res = prints.get_red_fore("(loss)")

        in_t = "'"+str(in_t)
        out_t = "'"+str(out_t)
        print(f" {in_t:>3}-{out_t:>3} | {home_pre:>2} - {away_pre:<2} -> {home_post:>2} - {away_post:<2} {personal_res:<4} | {loc} | Result {end[0]:>2} - {end[1]:<2} {actual_res:<4} | for: {goals_for:>2}, agst: {goals_against:>2}, tot: {total_goals:>3} | {game.date}, {game.opponent(self)}")

    def print_team_influence(self, individual = True):
        influence = self.get_player_influence()
        first = True
        for player in influence:
            if not first:
                print("\n")
            if "goals_for" not in player.influence:
                # Skipping players that hasn't played any minutes
                print(player, "- No minutes registerd")
                continue
            first = False
            p_tot = player.influence['goals_for'] - player.influence['goals_against']    
            ppg = 0 if player.influence['num_games'] == 0 else round(p_tot/player.influence['num_games'], 2)
            mpg = round(player.influence['num_minutes']/player.influence['num_games'], 0)
            s = f"{player}, personal total: {p_tot}"
            s += f" | avg. {prints.get_fore_color_int(ppg)} per game"
            s += f" | avg. {mpg} minutes per game"
            try:
                ppm = round(p_tot/player.influence['num_minutes'], 5)
                s += f" | avg. {prints.get_fore_color_int(ppm)} points per minute"
            except:
                ...
            print(s)
            if individual:
                for i in range(len(influence[player])):
                    self.print_player_influence(influence[player][i])

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
        return self.name.title().replace("Menn Senior ", "")

    def __eq__(self, other) -> bool:
        if type(other) == str:
            if self.name:
                return self.name.title().replace("Menn Senior ", "") == other
        if type(other) == Team:
            return self.name == other.name
