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
        output = {}
        for player in self.players:
            result = player.results_while_playing()
            for res in result:
                if res:
                    game, results, sub_time = res
                    pre, post, end = results
                    home_pre, away_pre = pre
                    home_post, away_post = post
                    goals_for = 0
                    goals_against = 0
                    loc = "Home"

                    if game.home == self:
                        goals_for = home_post - home_pre
                        goals_against = away_post - away_pre
                    elif game.away == self:
                        goals_for = away_post - away_pre
                        goals_against = home_post - home_pre
                        loc = "Away"

                    if not player in output:
                        output[player] = []

                    if not "goals_for" in player.influence:
                        player.influence["goals_for"] = goals_for
                        player.influence["goals_against"] = goals_against
                        player.influence["num_games"] = 1
                        player.influence["num_minutes"] = sub_time[1]-sub_time[0]
                    else:
                        player.influence["goals_for"] += goals_for
                        player.influence["goals_against"] += goals_against
                        player.influence["num_games"] += 1
                        player.influence["num_minutes"] += (sub_time[1])-sub_time[0]
                    
                    output[player].append([game, loc, sub_time, pre, post, end, goals_for, goals_against])
        return output
    
    def get_top_performers(self, category="ppg"):
        output = []
        influence = self.get_player_influence()
        for player in influence:
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


    def print_top_perfomers(self):
        inp = self.get_top_performers()
        inp = sorted(inp, key=lambda x: x[0], reverse=True)
        for i in inp:
            s = f"{i[2]}, personal total: {i[1][0]}"
            s += f" | avg. {prints.get_fore_color_int(i[1][1])} per game"
            s += f" | avg. {i[1][2]} minutes per game"
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
        print(f" {in_t:>3}-{out_t:>3} | {home_pre:>2} - {away_pre:<2} -> {home_post:>2} - {away_post:<2} {personal_res:<4} | {loc} | Result {end[0]:>2} - {end[1]:<2} {actual_res:<4} | for: {goals_for:>2}, agst: {goals_against:>2}, tot: {total_goals:>3} | {game.opponent(self)}, {game.result.page.url}")

    def print_team_influence(self, individual = True):
        influence = self.get_player_influence()
        first = True
        for player in influence:
            if not first:
                print("\n")
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

    def get_player(self, name="UnreportedPlayer", url=False, warning=False):
        if name == False:
            name = "UnreportedPlayer"
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
            if self.name:
                return self.name.title().replace("Menn Senior ", "") == other
        if type(other) == Team:
            return self.name == other.name
