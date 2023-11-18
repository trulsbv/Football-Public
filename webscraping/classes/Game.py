from datetime import datetime
from classes.Weather import Weather
import tools.prints as prints
import tools.file_tools as ft
import settings

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
        date, self.day, self.time, _hometeam, score, _awayteam, self.spectators = data[0].split(",")
        self.date = datetime.strptime(date, "%Y-%m-%d").date()
        self.hometeam = self.extract_players(self.home, data[1], data[2])
        self.awayteam = self.extract_players(self.away, data[3], data[4])
        self.weather = self.extract_weather(data[6])
        self.events = self.extract_events(data[7:])
        self.score = self.extract_score(score)
        if self.score[0] > self.score[1]:
            self.winner = self.home
        elif self.score[0] < self.score[1]:
            self.winner = self.away
        self.home.games.append(self)
        self.away.games.append(self)

    def analyse(self):
        if ft.is_analysed(self.gameId, ".csv"):
            self.read_analysis(ft.get_analysis(self.gameId, ".csv"))
            return
        if self._is_played():
            self.weather = Weather(self)
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
                
            self.home.games.append(self)
            self.away.games.append(self)
            self.write_analysis()
        else:
            prints.warning(f"{self.home} - {self.away} has not been played yet!")
        
    
    def opponent(self, team):
        if team == self.home:
            return self.away
        if team == self.away:
            return self.home
        return False
    
    def __repr__(self) -> str:
        s = f"{str(self.round):>2} {('(' + str(self.day)):>8} {self.date} at {self.time}) {str(self.home):>18} "
        if self.date < settings.current_date:
            s += f"{self.result} "
        else:
            s += " - "
        s += f"{str(self.away):<18} {str(self.pitch):>25} ({self.gameId})"
        if self.spectators and self.spectators != "None":
            s += f" - {str(self.spectators):>5} attended"
        return s
