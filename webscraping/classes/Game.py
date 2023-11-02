from datetime import datetime
from classes.Weather import Weather
import tools.prints as prints
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
    
    def analyse(self):
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
