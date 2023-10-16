from colorama import Fore, Back
import io
from operator import itemgetter

class League():
    def __init__(self, name):
        self.name = name
        self.teams = []
        self.games = []
        self.table = []
        self.expected_table = []

    def _add_table_title(self, title, columns):
        s = self._add_table_line(columns, special="-")
        s = "+"+s[1:-1]+"+\n"
        t = len(s)-len(title)-3
        h = t//2
        v = t-h
        s += f"|{' '*h}{title}{' '*v}|"
        return s

    def _add_table_header(self, columns):
        s = ""
        for header in columns:
            s+= "| " + header + " "
        s+=" |"
        return s

    def _add_table_line(self, columns, type="-", special="+"):
        s = ""
        for header in columns:
            s+=f"{special}{type}" + f"{type}"*(len(header)+1)
        s+=f"{type}{special}"
        return s
    
    def _add_cell(self, header, content, back_color=Back.RESET):
        t = (len(header)-len(content)+1)
        m = t//2
        s = f"|{back_color} "
        s+=f"{' '*m}{content}{' '*(t-m)}{Back.RESET}"
        return s

    def get_table(self, ctx, exp=False):
        table = []
        for team in self.teams:
            row = {}
            row["name"] = team.name
            row["total_games"] = team.total_games(ctx, exp)
            row["wins"] = team.wins(ctx, exp)
            row["draws"] = team.draws(ctx, exp)
            row["losses"] = team.losses(ctx, exp)
            row["goals"] = f"{team.goals_for(ctx)} - {team.goals_against(ctx)}" if not exp else "N/A"
            row["goal_dif"] = f"{team.goal_difference(ctx)}" if not exp else "N/A"

            table.append([team.get_points(ctx, exp), row])

        return sorted(table, key=lambda x: x[0], reverse=True)
    
    def comp_table(self, ctx="total"):
        t_exp = self.get_table(ctx, True)
        t_org = self.get_table(ctx)
        w = self.teams[0].padding//2
        columns = ["Placement", f"{' '*w}Team{' '*w}", "Games played", "Win", "Draw", "Loss", "Goals F-A", "Goal diff.", "Points"]

        print(self._add_table_title(("compare " + ctx), columns))
        print(self._add_table_line(columns))
        print(self._add_table_header(columns))
        print(self._add_table_line(columns))
        i = 1
        for _ in t_exp:
            t=_[1]
            s=""
            color = Back.RESET
            if i == 1:
                color=Back.GREEN
            elif i == 2:
                print(self._add_table_line(columns))
                color=Back.YELLOW
            elif i > 11:
                if i == 12:
                    print(self._add_table_line(columns))
                color=Back.RED
            j=1
            for __ in t_org:
                if t["name"] == __[1]["name"]:
                    break
                j += 1

            if i < j:
                sign = "^" 
            elif i > j:
                sign = "v"
            else: sign = ""
            
            s+=self._add_cell(columns[0], f"{i} {sign}", color)
            s+=self._add_cell(columns[1], f"{t['name']}", color)
            s+=self._add_cell(columns[2], f"{t['total_games']}", color)
            s+=self._add_cell(columns[3], f"{t['wins']}", color)
            s+=self._add_cell(columns[4], f"{t['draws']}", color)
            s+=self._add_cell(columns[5], f"{t['losses']}", color)
            s+=self._add_cell(columns[6], f"{t['goals']}", color)
            s+=self._add_cell(columns[7], f"{t['goal_dif']}", color)
            s+=self._add_cell(columns[8], f"{_[0]}", color)
            s+=f"{color} {Back.RESET}|"
            print(s)
            i += 1
        print(self._add_table_line(columns))


    def print_table_full(self, ctx="total", exp=False):
        table = self.get_table(ctx, exp)

        w = self.teams[0].padding//2
        columns = ["Placement", f"{' '*w}Team{' '*w}", "Games played", "Win", "Draw", "Loss", "Goals F-A", "Goal diff.", "Points"]
        
        print(self._add_table_title(ctx + (" expected" if exp else ""), columns))
        print(self._add_table_line(columns))
        print(self._add_table_header(columns))
        print(self._add_table_line(columns))
        
        i = 1
        for _ in table:
            t=_[1]
            s=""
            color = Back.RESET
            if i == 1:
                color=Back.GREEN
            elif i == 2:
                print(self._add_table_line(columns))
                color=Back.YELLOW
            elif i > 11:
                if i == 12:
                    print(self._add_table_line(columns))
                color=Back.RED
            s+=self._add_cell(columns[0], f"{i}", color)
            s+=self._add_cell(columns[1], f"{t['name']}", color)
            s+=self._add_cell(columns[2], f"{t['total_games']}", color)
            s+=self._add_cell(columns[3], f"{t['wins']}", color)
            s+=self._add_cell(columns[4], f"{t['draws']}", color)
            s+=self._add_cell(columns[5], f"{t['losses']}", color)
            s+=self._add_cell(columns[6], f"{t['goals']}", color)
            s+=self._add_cell(columns[7], f"{t['goal_dif']}", color)
            s+=self._add_cell(columns[8], f"{_[0]}", color)
            s+=f"{color} {Back.RESET}|"
            print(s)
            i += 1
        print(self._add_table_line(columns))
    
    def add_game(self, game):
        for played_game in self.games:
            if played_game.gameId == game.gameId:
                return False
        self.games.append(game)
        ht = game.hometeam
        at = game.awayteam
        ht.games.append(game)       
        at.games.append(game)

        if game.homeresult == False:
            ht.remaining_games += 1
            at.remaining_games += 1
            return True
        if game.awayresult < game.homeresult:
            game.game_home_win(ht, at)
        elif game.awayresult > game.homeresult:
            ht.home_losses += 1
            at.away_wins += 1
        else:
            ht.home_draws += 1
            at.away_draws += 1

        ht.goals_scored_home += int(game.homeresult)       
        ht.goals_conceded_home += int(game.awayresult)    
        at.goals_scored_away += int(game.awayresult)       
        at.goals_conceded_away += int(game.homeresult)            
        return True

    def get_team(self, name):
        for team in self.teams:
            if team.name == name:
                return team
        t = Team(name)
        self.teams.append(t)
        return t

class Team():
    def __init__(self, name):
        self.name = name
        self.home_wins = 0
        self.away_wins = 0
        self.home_draws = 0
        self.away_draws = 0
        self.home_losses = 0
        self.away_losses = 0
        self.remaining_games = 0
        self.goals_scored_home = 0
        self.goals_conceded_home = 0
        self.goals_scored_away = 0
        self.goals_conceded_away = 0

        self.padding = None
        self.games = []

    def games_remaining(self):
        out = []
        for g in self.games:
            if not g.homeresult:
                out.append(g)
        return out

    def avg_points(self, ctx, rnd=3):
        return round(self.get_points(ctx)/self.total_games(ctx), rnd)
    
    def calculate_game(self, g):
        h = self.avg_points("home")
        a = self.avg_points("away")

        if self == g.hometeam:
            # Hjemmekamp
            op = g.awayteam
            opavg = op.avg_points("away")
            if h > opavg:
                return 3
            elif h == opavg:
                return 1
        else:
            # Bortekamp
            op = g.hometeam
            opavg = op.avg_points("away")
            if a > opavg:
                return 3
            elif a == opavg:
                return 1
        return 0
    
    def avg_points_remaining(self, rnd=3):
        points = 0
        games = 0

        for g in self.games_remaining():
            games+=1
            points += self.calculate_game(g)
            
        return round(points/games, rnd)

    def wins(self, ctx, exp=False):
        if exp: return self.home_wins+self.away_wins+(self.exp_results()[0])
        if ctx=="total": return self.home_wins+self.away_wins
        if ctx=="home": return self.home_wins
        if ctx=="away": return self.away_wins

    def draws(self, ctx, exp=False):
        if exp: return self.home_draws+self.away_draws+(self.exp_results()[1])
        if ctx=="total": return self.home_draws+self.away_draws
        if ctx=="home": return self.home_draws
        if ctx=="away": return self.away_draws

    def losses(self, ctx, exp=False):
        if exp: return self.home_losses+self.away_losses+(self.exp_results()[2])
        if ctx=="total": return self.home_losses+self.away_losses
        if ctx=="home": return self.home_losses
        if ctx=="away": return self.away_losses

    def home_games(self):
        return self.home_wins+self.home_draws+self.home_losses
    
    def away_games(self):
        return self.away_wins+self.away_draws+self.away_losses
    
    def exp_results(self):
        w = 0
        d = 0
        l = 0
        for g in self.games_remaining():
            res = self.calculate_game(g)
            if res == 3: w+=1
            elif res == 1: d+=1
            else: l+=1
        return [w, d, l]

    
    def total_games(self, ctx, exp=False):
        if exp: return 26
        if ctx=="total": return self.home_games()+self.away_games()
        if ctx=="home": return self.home_games()
        if ctx=="away": return self.away_games()
    
    def goals_for(self, ctx):
        if ctx=="total": return self.goals_scored_home+self.goals_scored_away
        if ctx=="home": return self.goals_scored_home
        if ctx=="away": return self.goals_scored_away
    
    def goals_against(self, ctx):
        if ctx=="total": return self.goals_conceded_home+self.goals_conceded_away
        if ctx=="home": return self.goals_conceded_home
        if ctx=="away": return self.goals_conceded_away
    
    def goal_difference(self, ctx):
        return (self.goals_for(ctx)-self.goals_against(ctx))
    
    def get_points(self, ctx="total", exp=False):
        p = (self.wins(ctx)*3 + self.draws(ctx))
        if self.name == "Notodden":
            # Notodden was deducted 3 points due to financial issues
            p=p-3
        if exp:
            p+=(self.avg_points_remaining()*self.remaining_games)
        return p

class Game():
    def __init__(self):
        self.round = None
        self.date = None
        self.day = None
        self.time = None
        self.hometeam = None
        self.homeresult = None
        self.awayresult = None
        self.homeresult = None
        self.awayresult = None
        self.awayteam = None
        self.pitch = None
        self.gameId = None

    def game_home_win(self, home, away):
        home.home_wins += 1
        away.away_losses += 1

    def game_away_win(self, home, away):
        home.home_losses += 1
        away.away_wins += 1

    def game_draw(self, home, away):
        home.home_draws += 1
        away.away_draws += 1
    
    def get_short_info(self):
        width = self.hometeam.padding
        if self.homeresult:
            if self.homeresult == self.awayresult:
                return f"{Fore.YELLOW}{self.hometeam.name:>{width}}{Fore.RESET} {self.homeresult} - {self.awayresult} {Fore.YELLOW}{self.awayteam.name}{Fore.RESET}"
            if self.homeresult < self.awayresult:
                return f"{Fore.RED}{self.hometeam.name:>{width}}{Fore.RESET} {self.homeresult} - {self.awayresult} {Fore.GREEN}{self.awayteam.name}{Fore.RESET}"
            if self.homeresult > self.awayresult:
                return f"{Fore.GREEN}{self.hometeam.name:>{width}}{Fore.RESET} {self.homeresult} - {self.awayresult} {Fore.RED}{self.awayteam.name}{Fore.RESET}"
        return f"{self.hometeam.name:>{width}}   -   {{:<{width}}}".format(self.awayteam.name) + f" ==> to be played {self.date}"

    def get_long_info(self):
        s = ""
        if self.homeresult:
            s += f"{self.hometeam.name} {self.homeresult} - {self.awayresult} {self.awayteam.name}\n"
        s += "-"*len(s)
        s += f"\nRound: {self.round}"
        s += f"\n{self.day} {self.date} ({self.time})"
        s += f"\nGame id: {self.gameId}"
        return s
    
    def read_game(self, split, league):
        self.round = split[0]
        self.date = split[1]
        self.day = split[2]
        self.time = split[3]
        self.hometeam = league.get_team(split[4])
        if split[5] != "-":
            self.homeresult, self.awayresult = split[5].split(" - ")
        else:
            self.homeresult = False
            self.awayresult = False
        self.awayteam = league.get_team(split[6])
        self.pitch = split[7]
        self.gameId = split[9]

def readGames(league: League):
    f = io.open("kamper.csv", mode="r", encoding="utf-8")
    f.readline()
    max_width = 0
    for line in f.readlines():
        g = Game()
        g.read_game(line.split(";"), league)
        league.add_game(g)
        if len(g.hometeam.name) > max_width:
            max_width = len(g.hometeam.name)
    
    for t in league.teams:
        t.padding = max_width
    

def main():
    liga = League("PostNord avd. 1")
    readGames(liga)


    liga.print_table_full("total", exp=True)
    liga.print_table_full("total")

    print()
    print()
    print()
    liga.comp_table()

main()
