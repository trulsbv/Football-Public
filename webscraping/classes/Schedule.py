from bs4 import BeautifulSoup
import tools.regex_tools as rt
from classes.Events import Events
from classes.Game import Game
from classes.Page import Page
from classes.Pitch import Pitch
from datetime import date, datetime

class Schedule():
    def __init__(self, parent, page):
        self.turnering = parent
        self.games = []
        self.page = page

    def fetch_games(self):
        document = BeautifulSoup(self.page.html.text, "html.parser")
        table = document.find("table")

        rows = table.find_all("tr")
        column_names = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        assert "Hjemmelag" in column_names
        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            if not cells:
                continue
            urls = rt.find_urls(str(row))
            cells_text = [cell.get_text(strip=True) for cell in cells]
            try:
                round, date, day, time, _, _hometeam, _result, _awayteam, _pitch, gameId = cells_text
            except:
                round, date, day, time, _, _hometeam, _result, _awayteam, _pitch, gameId, _live = cells_text
            
            home = self.turnering.create_team(_hometeam, urls[1])
            away = self.turnering.create_team(_awayteam, urls[3])
            if self._is_played(date):
                events = Events(Page(urls[2], expires_after_days=False))
                pitch = Pitch(Page(urls[4], expires_after_days=False))
                game = Game(round, date, day, time, home, events, away, pitch, gameId)
                self.games.append(game)

    def _is_played(self, d):
        return datetime.strptime(d, "%d.%m.%Y").date() < date.today()
    