from colorama import Fore, Back
import io
from operator import itemgetter

class League():
    def __init__(self, name):
        self.name = name
        self.teams = []
        self.games = []

    def get_team(self, name):
        for team in self.teams:
            if team.name == name:
                return team
        team = Team(name)
        self.teams.append(team)
        return team
            
    def reset_points(self):
        for team in self.teams:
            team.points = 0
    
    def update_points(self):
        for game in self.games:
            if game.played:
                if game.result[0] == game.result[1]:
                    game.hometeam.points += 1
                    game.awayteam.points += 1
                elif game.result[0] > game.result[1]:
                    game.hometeam.points += 3
                else: game.awayteam.points += 3
    
    def add_points(self, game):
        if game.result[0] == game.result[1]:
            game.hometeam.points += 1
            game.awayteam.points += 1
        elif game.result[0] > game.result[1]:
            game.hometeam.points += 3
        else: game.awayteam.points += 3
        self._sort_teams()

    def _sort_teams(self):
        self.teams = sorted(self.teams, key=lambda x: x.points, reverse=True)

    def debug_table(self):
        self.reset_points()
        self.update_points()
        self._sort_teams()

    def read_game(self, data, league):
        g = Game()
        g.round = data[0]
        g.date = data[1]
        g.day = data[2]
        g.time = data[3]
        g.hometeam = league.get_team(data[4])
        g.awayteam = league.get_team(data[6])
        res = data[5].split(" - ")
        if len(res) > 1:
            g.result = [int(res[0]), int(res[1])]
            g.played = True
            self.add_points(g)
        g.pitch = data[7]
        g.gameId = data[9]
        return g

    def read_game_file(self, filename):
        f = io.open(filename, mode="r", encoding="utf-8")
        f.readline()
        max_width = 0
        for line in f.readlines():
            self.games.append(self.read_game(line.split(";"), self))

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
        self.games_played = []
        self.games_remaining = []
        self.points = 0

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class Game():
    def __init__(self):
        self.round = None
        self.date = None
        self.day = None
        self.time = None
        self.hometeam = None
        self.result = None
        self.awayteam = None
        self.pitch = None
        self.gameId = None
        self.played = False

        self.happenings = []
        self.lineup = []

class Player():
    ...


# ABSTRACT
class Happening:
    def __init__(self, a):
        print(a)
        ...
    
class Goal(Happening):
    def __init__(self, a, b):
        print(a, b)

class Substitute(Happening):
    ...



def main():
    liga = League("PostNord avd. 1")
    liga.read_game_file("kamper.csv")

    print(liga.teams)
    Goal(1, 2)
    Substitute(1)
main()
