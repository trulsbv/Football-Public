import os
from pathlib import Path


class Team:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.gs = 0  # Goals scored
        self.gc = 0  # Goals conceded
        self.gp = 0  # Games played

    def spg(self):
        """
        Score per game
        """
        return self.points/self.gp

    def reset(self):
        self.points = 0
        self.gs = 0
        self.gc = 0
        self.gp = 0

    def __repr__(self):
        return f"{self.name} ({self.points} / {self.gp})"

    def __lt__(self, other):
        """
        Sort by points, then goals
        """
        if self.points > other.points:
            return True
        if self.points < other.points:
            return False
        if (self.gs - self.gc) > (other.gs - other.gc):
            return True
        if (self.gs - self.gc) < (other.gs - other.gc):
            return False
        if self.gs > other.gs:
            return True
        return False


class Game:
    def __init__(self, home, score, away, h, u, b):
        self.home: Team = home
        self.score: str = score
        self.away: Team = away
        self.h = h
        self.u = u
        self.b = b
        self.played = False

    def win(self, team: Team) -> bool:
        """
        Returns true if the team won the game,
        no check for team's involvement, must be asserted prior
        """
        self.play()
        s = self.score.split(" - ")
        s = int(s[0])-int(s[1])
        if s > 0 and team == self.home:
            return True
        elif s < 0 and team == self.away:
            return True
        return False

    def win_or_draw(self, team: Team) -> bool:
        """
        NB! No check for team involvement
        TODO: Write the check and handle the error
        """
        return (self.win(team) or self.draw())

    def draw(self, team: Team = None) -> bool:
        """
        Returns true if the team drawed the game,
        no check for team's involvement, must be asserted prior
        """
        self.play()
        s = self.score.split(" - ")
        s = int(s[0])-int(s[1])
        if s == 0:
            return True
        return False

    def draw_or_lose(self, team: Team) -> None:
        """
        NB! No check for team involvement
        """
        return (self.lose(team) or self.draw())

    def lose(self, team: Team):
        """
        Returns true if the team lost the game,
        no check for team's involvement, must be asserted prior
        """
        self.play()
        s = self.score.split(" - ")
        s = int(s[0])-int(s[1])
        if s < 0 and team == self.home:
            return True
        elif s > 0 and team == self.away:
            return True
        return False

    def play(self):
        self.played = True

    def reset(self):
        self.played = False

    def inv(self, team):
        return (team == self.home or team == self.away)

    def __repr__(self):
        if self.played:
            return f"{self.home} {self.score} {self.away}"
        return f"{self.home} - {self.away}"


class League():
    def __init__(self, name, games, teams, fav):
        self.name = name
        self.games: list[Game] = games
        self.played_games = []
        self.teams = teams
        self.fav = fav

        self.n_teams = len(self.teams)
        self.gpr = self.n_teams//2

    def reset(self):
        for game in self.games:
            game.reset()
        for team in self.teams:
            self.teams[team].reset()

    def table(self):
        table = []
        for team in self.teams:
            table.append(self.teams[team])
        table.sort()
        return table

    def home_win(self) -> float:
        total = 0
        win = 0

        for game in self.games:
            home = game.home
            total += 1
            if game.win(home):
                win += 1
        return win/total

    def away_win(self) -> float:
        total = 0
        win = 0

        for game in self.games:
            home = game.away
            total += 1
            if game.win(home):
                win += 1
        return win/total

    def win_percent(self, teams: list[Team]) -> float:
        total = 0
        win = 0
        for game in self.games:
            for team in teams:
                if game.played(team):
                    total += 1
                    if game.win(team):
                        win += 1


def read_league_games(filename):
    """
    1. Read the files
    2. Create the teams and match objects
    3. Return the list
    """
    teams = {}
    games = []

    file = open(filename, "r", encoding="UTF-8")
    for line in file.readlines():
        home, score, away, h, u, b = line.strip().split(",")
        if home not in teams:
            teams[home] = Team(home)
            home = teams[home]
        else:
            home = teams[home]
        if away not in teams:
            teams[away] = Team(away)
            away = teams[away]
        else:
            away = teams[away]
        games.append(Game(home, score, away, float(h), float(u), float(b)))

    return (teams, games)


def main():
    cur = Path(str(os.curdir))
    leagues = cur / "files" / "static_bet_data"
    eliteserien = leagues / "ES23.csv"   # 16 teams (8 games per round)
    eredevise = leagues / "Eredevise22_23.csv"   # 18 teams (9 games per round)
    laLiga = leagues / "LaLiga22_23.csv"  # 20 teams (10 games per round)
    premierLeague = leagues / "PL22_23.csv"  # 20 teams (10 games per round)
    ES_teams, ES_games = read_league_games(eliteserien)
    ED_t, ED_g = read_league_games(eredevise)
    LL_t, LL_g = read_league_games(laLiga)
    PL_t, PL_g = read_league_games(premierLeague)

    ES = League("Eliteserien", ES_games, ES_teams, ["Bodø/Glimt",
                                                    "Viking",
                                                    "Tromsø",
                                                    "Brann",
                                                    "Molde"])
    ED = League("Eredivise", ED_g, ED_t, ["PSV",
                                          "Feyenoord",
                                          "Ajax",
                                          "AZ Alkmaar",
                                          "Twente"])
    LL = League("LaLiga", LL_g, LL_t, ["Real Madrid",
                                       "Girona",
                                       "Barcelona",
                                       "Atl. Madrid",
                                       "Ath Bilbao"])
    PL = League("Premier League", PL_g, PL_t, ["Manchester City",
                                               "Liverpool",
                                               "Arsenal",
                                               "Aston Villa",
                                               "Tottenham"])

    lgs = [ES, ED, LL, PL]
    for league in lgs:
        print(f"=== {league.name} ===")
        print("       Home | Away")
        print(f" Win: {round(league.home_win()*100, 1)}% | {round(league.away_win()*100, 1)}%")

        print()


if __name__ == "__main__":
    main()
