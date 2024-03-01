from bs4 import BeautifulSoup
import tools.regex_tools as rt
import tools.file_tools as ft
import settings
from classes.Events import Events
from classes.Game import Game
from classes.Page import Page
from classes.Pitch import Pitch
from datetime import date, datetime
from errors import DontCare


class Schedule:
    def __init__(self, parent, page):
        self.turnering = parent
        self.games: list[Game] = []
        self.page = page

    def add_betting_data(self):
        ft.clear_betting_data(
            str(self.turnering.name) + "_" + settings.current_date.year
        )
        for game in self.games:
            ft.add_betting_data(
                game, str(self.turnering.name) + "_" + settings.current_date.year
            )

    def fetch_games(self):
        self.games = []
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
                (
                    round,
                    date,
                    day,
                    time,
                    _,
                    _hometeam,
                    _result,
                    _awayteam,
                    _pitch,
                    gameId,
                ) = cells_text
            except DontCare:
                (
                    round,
                    date,
                    day,
                    time,
                    _,
                    _hometeam,
                    _result,
                    _awayteam,
                    _pitch,
                    gameId,
                    _live,
                ) = cells_text
            date = datetime.strptime(date, "%d.%m.%Y").date()
            if self._is_played(date):
                home = self.turnering.create_team(_hometeam, urls[1])
                away = self.turnering.create_team(_awayteam, urls[3])
                events = Events(Page(urls[2], valid_from=date))
                pitch = Pitch(Page(urls[4], valid_from=date))
                game = Game(round, date, day, time, home, events, away, pitch, gameId)
                self.games.append(game)

    def _is_played(self, d):
        return d < date.today()
