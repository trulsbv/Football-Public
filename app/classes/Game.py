from datetime import date as d, datetime
from classes.Weather import Weather
import tools.prints as prints
import tools.file_tools as ft
import settings
import classes.Team as Team


class Game:
    def __init__(self, round, date, day, time, home, result, away, pitch, gameId):
        self.round = round
        self.date = date
        self.day = day
        self.time = time
        self.home = home  # Page - To the team
        self.result = result  # Page - To the game
        self.away = away  # Page - To the team
        self.pitch = pitch  # Page - To the pitch
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
        self.odds = None  # Not yet implemented a way to get the odds

    def break_rules(self):
        rules = [
            settings.display_weather
            and self.weather.conditions not in settings.display_weather,
            settings.display_surface
            and self.pitch.surface not in settings.display_surface,
        ]
        for rule in rules:
            if rule:
                return True
        return False

    def _is_played(self):
        return self.date < settings.current_date

    def ask_user_for_odds(self) -> list:
        """
        Prompts the user to insert odds for the game
        Format: 1.23,4.56,7.89
        """
        inp = input(f"\n\nInsert odds for {self.home} - {self.away} ({self.gameId})\n"
                    " => ")
        out = None
        try:
            h, u, b = inp.split(",")
            out = [float(h.strip()), float(u.strip()), float(b.strip())]
        finally:
            return out

    def write_analysis(self):
        """
        Takes the game-data and formats it to json v1.1
        """
        data = {
            "meta": {
                "version": 1,
                "date": str(d.today()),
            },
            "data": {
                "date": str(self.date),
                "day": self.day,
                "time": self.time,
                "home_url": self.home.page.url,
                "away_url": self.away.page.url,
                "score_home": self.score[0],
                "score_away": self.score[1],
                "spectators": self.spectators,
                "odds": self.odds if self.odds else self.ask_user_for_odds(),
                "stadium": self.pitch.get_analysis(),
                "weather": self.weather.get_analysis(),
                "home_team": {"starting": [], "bench": []},
                "away_team": {"starting": [], "bench": []},
                "events": [],
            },
        }

        for player in self._save_home[0]:
            data["data"]["home_team"]["starting"].append(player.get_analysis())
        for player in self._save_home[1]:
            data["data"]["home_team"]["bench"].append(player.get_analysis())
        for player in self._save_away[0]:
            data["data"]["away_team"]["starting"].append(player.get_analysis())
        for player in self._save_away[1]:
            data["data"]["away_team"]["bench"].append(player.get_analysis())
        for event in self.events:
            data["data"]["events"].append(event.get_analysis())

        ft.write_analysis(data, self.gameId, ".json")

    def extract_players(self, team: Team, data: map) -> set:
        out = ([], [])
        for player in data["starting"]:

            player = team.get_player(
                name=player["name"],
                url=player["url"],
                number=player["number"],
                position=player["position"],
            )
            player.matches["started"].append(self)
            out[0].append(player)
        for player in data["bench"]:
            player = team.get_player(
                name=player["name"],
                url=player["url"],
                number=player["number"],
                position=player["position"],
            )
            player.matches["benched"].append(self)
            out[1].append(player)
        return out

    def extract_weather(self, data):
        weather = Weather(self, False)
        weather.insert_data(data)
        return weather

    def extract_events(self, data):
        out = []
        for dt in data:
            event = dt["type"]
            time = dt["time"]
            team_url = dt["team_url"]
            if event == "Substitution":
                player1 = dt["in_url"]
                player2 = dt["out_url"]
            else:
                player1 = dt["player_url"]
                player2 = None

            team = self.home if self.home.page.url == team_url else self.away
            out.append(
                self.result.insert_data(event, time, team, player1, player2, self)
            )
        return out

    def extract_score(self, data):
        data = data.split(" - ")
        return (int(data[0]), int(data[1]))

    def read_analysis(self, data: map) -> None:
        """
        Reads the data map
        """
        data = data["data"]
        self.weather = self.extract_weather(data["weather"])
        if self.break_rules():
            return

        self.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        self.day = data["day"]
        self.time = data["time"]

        if not self._is_played():
            prints.warning(
                "Read analysis",
                f"{self.home} - {self.away} has not been played yet!",
                False,
            )
            return

        self.spectators = data["spectators"]
        self.odds = data["odds"]
        self.hometeam = self.extract_players(self.home, data["home_team"])
        self.awayteam = self.extract_players(self.away, data["away_team"])
        self.events = self.extract_events(data["events"])
        self.score = (data["score_home"], data["score_away"])
        if self.score[0] > self.score[1]:
            self.winner = self.home
        elif self.score[0] < self.score[1]:
            self.winner = self.away
        self.home.add_game(self)
        self.away.add_game(self)

    def analyse(self):
        # TODO: Her er det unødvendig å finne filen, si true, og så finne
        # og lese filen igjen
        if ft.is_analysed(self.gameId, ".json"):
            self.read_analysis(ft.get_analysis(self.gameId, ".json"))
            return
        if not self._is_played():
            prints.warning(
                "Analyse", f"{self.home} - {self.away} has not been played yet!", False
            )
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
        s = ""
        try:
            s += f"{str(self.round):>2} {('(' + str(self.day)):>8} "
            s += f"{self.date} at {self.time}) {str(self.home):>18} "
            if self.date < settings.current_date:
                s += f"{self.result} "
            else:
                s += " - "
            s += f"{str(self.away):<18} {str(self.pitch):>25} ({self.gameId})"
            if self.spectators and self.spectators != "None":
                s += f" - {str(self.spectators):>5} attended"
        finally:
            return s
