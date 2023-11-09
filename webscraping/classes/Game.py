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
        self.spectators = None
        self.winner = None
        self.score = None

    def _is_played(self):
        return datetime.strptime(self.date, "%d.%m.%Y") < settings.current_date
    
    def write_analysis(self):
        direct_items = [self.date, self.day, self.time, self.home.name, f"{self.score[0]} - {self.score[1]}", self.away.name, str(self.spectators)]
        callable_items = [self.pitch, self.weather]
        s = ""

        f = True
        for item in direct_items:
            if item is None:
                continue
            if not f:
                s += ","
            s += item
            f = False
        s += "\n"

        for team in [self.hometeam, self.awayteam]:
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

    def extract_players(self, start, bench):
        print(start)

        print(bench)

    def read_analysis(self, data):
        data = data.split("\n")[1:]
        self.date, self.day, self.time, _hometeam, score, _awayteam, self.spectators = data[0].split(",")
        self.hometeam = self.extract_players(data[1], data[2])
        self.awayteam = self.extract_players(data[3], data[4])
        self.weather = self.extract_weather(data[6])
        self.events = self.extract_events(data[7:])
        self.score = self.extract_score(score)
        if self.score[0] > self.score[1]:
            self.winner = self.home
        elif self.score[0] < self.score[1]:
            self.winner = self.away
        for item in data:
            print()
            print(item)
        exit()


    def analyse(self):
        if ft.is_analysed(self.gameId, ".csv"):
            self.read_analysis(ft.get_analysis(self.gameId, ".csv"))
        if self._is_played():
            self.weather = Weather(self)
            result = self.result.get_team_sheet(self)
            if result:
                self.hometeam, self.awayteam = result
            self.events = self.result.analyse()
            self.score = self.result.get_result()
            if self.score[0] > self.score[1]:
                self.winner = self.home
            elif self.score[0] < self.score[1]:
                self.winner = self.away
                
            self.home.games.append(self.gameId)
            self.away.games.append(self.gameId)
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
        s = f"{self.round} ({self.day} {self.date} at {self.time}) {self.home} "
        if datetime.strptime(self.date, "%d.%m.%Y") < settings.current_date:
            s += f"{self.result} "
        else:
            s += " -  "
        s += f"{self.away}, {self.pitch} ({self.gameId})"
        if self.spectators:
            s += f" - {self.spectators} attended"
        return s
