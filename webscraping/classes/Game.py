from datetime import datetime
from classes.Weather import Weather
import tools.prints as prints
import tools.file_tools as ft
import settings

unplayed_games = 0

class Game():
    def __init__(self, round, date, day, time, home, result, away, pitch, gameId):
        self.round = round
        self.date = date
        self.day = day
        self.time = time
        self.home = home # Page - To the team
        self.result = result # Page - To the game
        self.away = away # Page - To the team
        self.pitch = pitch # Page - To the pitch
        self.gameId = gameId
        self.events = []
        
        self.weather = None
        self.hometeam = None
        self.awayteam = None
        self._save_home = [[], []]
        self._save_away = [[], []]
        self.spectators = None
        self.winner = None
        self.score = None
        self.odds = None # Not yet implemented a way to get the odds

    def break_rules(self):
        rules = [
            settings.display_weather and self.weather.conditions not in settings.display_weather,
            settings.display_surface and self.pitch.surface not in settings.display_surface
        ]
        for rule in rules:
            if rule:
                return True
        return False


    def _is_played(self):
        return self.date < settings.current_date
    
    def write_analysis(self):
        direct_items = [self.date, self.day, self.time, self.home.page.url, f"{self.score[0]} - {self.score[1]}", self.away.page.url, str(self.spectators)]
        callable_items = [self.pitch, self.weather]
        s = ""

        f = True
        for item in direct_items:
            if item is None:
                continue
            if not f:
                s += ","
            s += str(item)
            f = False
        s += "\n"

        for team in [self._save_home, self._save_away]:
            for group in team: # [Starting, bench]
                f = True
                for player in group:
                    if not f:
                        s += ","
                    s += player.get_analysis_str()
                    f = False
                s += "\n"
        for item in callable_items:
            if item is None:
                continue
            s += item.get_analysis_str() + "\n"

        s += self.result.get_analysis_str()

        ft.write_analysis(s, self.gameId, ".csv")

    def extract_players(self, team, start, bench):
        out = ([], [])
        for data in start.split(","):
            url, name, number, position = data.split(";")
            player = team.get_player(name=name, url=url, number=number, position=position)
            player.matches["started"].append(self)
            out[0].append(player)
        for data in bench.split(","):
            url, name, number, position = data.split(";")
            player = team.get_player(name=name, url=url, number=number, position=position)
            player.matches["benched"].append(self)
            out[1].append(player)
        return out
    
    def extract_weather(self, data):
        weather = Weather(self, False)
        weather.insert_data(data.split(","))
        return weather
    
    def extract_events(self, data):
        out = []
        for item in data:
            if not item:
                continue
            try:
                event, time, team_url, player1 = item.split(",")
                player2 = None
            except:
                event, time, team_url, player1, player2= item.split(",")
                
            team = self.home if self.home.page.url == team_url else self.away
            out.append(self.result.insert_data(event, time, team, player1, player2, self))
            
    def extract_score(self, data):
        data = data.split(" - ")
        return (int(data[0]), int(data[1]))

    def read_analysis(self, data):
        data = data.split("\n")[1:]
        self.weather = self.extract_weather(data[6])
        if self.break_rules():
            return
        date, self.day, self.time, _hometeam, score, _awayteam, self.spectators = data[0].split(",")
        self.date = datetime.strptime(date, "%Y-%m-%d").date()
        if not self._is_played():
            global unplayed_games
            unplayed_games += 1
            prints.warning("Read analysis", f"{self.home} - {self.away} has not been played yet! (Unplayed games: {unplayed_games})", False)
            return
        self.hometeam = self.extract_players(self.home, data[1], data[2])
        self.awayteam = self.extract_players(self.away, data[3], data[4])
        self.events = self.extract_events(data[7:])
        self.score = self.extract_score(score)
        if self.score[0] > self.score[1]:
            self.winner = self.home
        elif self.score[0] < self.score[1]:
            self.winner = self.away
        self.home.add_game(self)
        self.away.add_game(self)

    def analyse(self):
        if ft.is_analysed(self.gameId, ".csv"):
            self.read_analysis(ft.get_analysis(self.gameId, ".csv"))
            return
        if not self._is_played():
            global unplayed_games
            unplayed_games += 1
            prints.warning("Analyse", f"{self.home} - {self.away} has not been played yet! (Unplayed games: {unplayed_games})", False)
            return
             
        self.weather = Weather(self)
        if self.break_rules():
            return
        result = self.result.get_team_sheet(self)
        if result:
            self.hometeam, self.awayteam = result
            self._save_home[0] = self.hometeam[0].copy()
            self._save_home[1] = self.hometeam[1].copy()
            self._save_away[0] = self.awayteam[0].copy()
            self._save_away[1] = self.awayteam[1].copy()
        self.events = self.result.analyse()
        self.score = self.result.get_result()
        if self.score[0] > self.score[1]:
            self.winner = self.home
        elif self.score[0] < self.score[1]:
            self.winner = self.away
            
        self.home.add_game(self)
        self.away.add_game(self)
        self.write_analysis()
    
    def opponent(self, team):
        if team == self.home:
            return self.away
        if team == self.away:
            return self.home
        return False
    
    def __repr__(self) -> str:
        try:
            s = f"{str(self.round):>2} {('(' + str(self.day)):>8} {self.date} at {self.time}) {str(self.home):>18} "
            if self.date < settings.current_date:
                s += f"{self.result} "
            else:
                s += " - "
            s += f"{str(self.away):<18} {str(self.pitch):>25} ({self.gameId})"
            if self.spectators and self.spectators != "None":
                s += f" - {str(self.spectators):>5} attended"
            return s
        except:
            return ""
