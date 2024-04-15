from bs4 import BeautifulSoup
import tools.regex_tools as rt
import tools.file_tools as ft
import settings
from classes.Game import Game
from classes.Page import Page
from datetime import datetime, timedelta, time
# This whole class might be excessive


class Schedule:
    def __init__(self, parent, url):
        self.tournament = parent
        self.games: list[Game] = []
        self.url = url

    def add_betting_data(self):
        ft.clear_betting_data(
            str(self.tournament.name) + "_" + settings.DATE.year
        )
        for game in self.games:
            ft.add_betting_data(
                game, str(self.tournament.name) + "_" + settings.DATE.year
            )

    def fetch_games(self):
        self.page = Page(self.url)
        date_string = self.page.html.text.split("\n")[0]
        date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
        if date_object < settings.DATE:
            self.page.html.force_fetch_html()
        self.games = []
        document = BeautifulSoup(self.page.html.text, "html.parser")
        lastweek = document.find(class_="large-6 columns end")
        matchweeks = document.find_all(class_="large-6 columns")
        matchweeks.append(lastweek)

        for matchweek in matchweeks:
            doc = BeautifulSoup(str(matchweek), "html.parser")
            table = doc.find("table")
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all(["th", "td"])
                if not cells:
                    continue
                cells_text = [cell.get_text(strip=True) for cell in cells]
                if len(cells_text) == 7:
                    if cells_text[0]:
                        date = datetime.strptime(cells_text[0][3:], "%m/%d/%y").date()
                        time = self.convert_time(cells_text[1])
                    if self._is_played(date, time):
                        urls = rt.find_urls(str(row))
                        for url in urls:
                            if "spielbericht" in url and "-" not in cells_text[4]:
                                game = Game(url, self.tournament, valid_from=date)
                                self.games.append(game)

    def _is_played(self, d, t):
        t_datetime = datetime.combine(d, t)
        t_plus3 = t_datetime + timedelta(hours=3)
        return t_plus3 <= settings.NOW()

    def convert_time(self, t):
        if t == "Unknown":
            return time(20, 59)
        time_format = "%I:%M %p"
        t = datetime.strptime(t, time_format).time()
        return t
