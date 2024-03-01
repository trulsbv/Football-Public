import os
import re
import sys

import tools.prints as prints
import tools.regex_tools as rt
from bs4 import BeautifulSoup
from classes.Event import (
    OwnGoal,
    PenaltyGoal,
    PlayGoal,
    RedCard,
    Substitute,
    YellowCard,
)


class Events:
    def __init__(self, page):
        self.page = page
        self.events = []
        self.uref_hendelser = []
        self.game = None

    def insert_data(self, event, time, team, player1, player2, game):
        self.game = game
        if event == "Playgoal":
            event = PlayGoal(game, time, team, (None, player1))
        elif event == "PenaltyGoal":
            event = PenaltyGoal(game, time, team, (None, player1))
        elif event == "OwnGoal":
            event = OwnGoal(game, time, team, (None, player1))
        elif event == "Yellow card":
            event = YellowCard(game, time, team, (None, player1))
        elif event == "Red card":
            event = RedCard(game, time, team, (None, player1))
        elif event == "Substitution":
            event = Substitute(game, time, team, ((None, player2), (None, player1)))
        else:
            prints.error(self, f"{event} is not handled!")
            exit()
        self.events.append(event)
        return event

    def analyse(self, restart=0):
        self.events = []
        if len(self.uref_hendelser) == 0:
            self._get_events()
        for text in self.uref_hendelser:
            h = self._analyse(text)
            if h:
                self.events.append(h)
            elif h == False:
                if restart == 2:
                    prints.STOP()
                    exit()
                prints.warning(self, f"Failed to read data, retrying {2-restart} times")
                return self.analyse(restart=restart + 1)

        document = BeautifulSoup(self.page.html.text, "html.parser")
        gi = document.find(
            class_="grid__item grid__item match__arenainfo one-third margin-top--two right-bordered mobile--one-whole"
        )
        if gi:
            self.game.spectators = rt.get_spectators(gi)
        return self.events

    def _get_events(self):

        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(
            class_="section-heading no-margin--bottom", string=re.compile("^Hendelser")
        )
        if not f:
            return
        table = f.find_next("ul")
        for found in table.find_all("li"):
            if rt.li_class(found) == "clear-li":
                continue
            self.uref_hendelser.append(found)

    def get_team_sheet(self, parent):
        self.game = parent
        hometeam = [[], []]
        awayteam = [[], []]
        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(class_="section-heading", string=re.compile("^Kamptroppen"))
        if not f:
            prints.error(self, f"Failed to find 'Kamptroppen' in {self.page.url}")
            return False
        table = f.find_next("ul")
        i = 1
        for found in table.find_all("li"):
            player_name, player_url = rt.get_name_url(found)
            player = self.game.home.get_player(player_name, player_url)

            if i > 11:
                player.matches["benched"].append(self.game)
                hometeam[1].append(player)
            else:
                player.matches["started"].append(self.game)
                hometeam[0].append(player)
            i += 1

        table = table.find_next("ul")
        i = 1
        for found in table.find_all("li"):
            player_name, player_url = rt.get_name_url(found)
            player = self.game.away.get_player(player_name, player_url)

            if i > 11:
                player.matches["benched"].append(self.game)
                awayteam[1].append(player)
            else:
                player.matches["started"].append(self.game)
                awayteam[0].append(player)
            i += 1

        return [hometeam, awayteam]

    def _analyse(self, text):
        r = rt.analysis(text)
        team = r["team"]
        type = r["type"]
        minute = r["minute"]
        url = r["url"]
        name = r["name"]

        team = self.game.home if "home-team" == team else self.game.away
        match type:
            case "Spillemål":
                type = PlayGoal(self.game, minute, team, (name, url))
            case "Straffemål":
                type = PenaltyGoal(self.game, minute, team, (name, url))
            case "Selvmål":
                type = OwnGoal(self.game, minute, team, (name, url))
            case "Advarsel":
                type = YellowCard(self.game, minute, team, (name, url))
            case "Utvisning":
                type = RedCard(self.game, minute, team, (name, url))
            case "Bytte inn":
                type = Substitute(self.game, minute, team, name)
            case "Bytte ut":
                type = Substitute(self.game, minute, team, name)
            case "Advarsel for Leder":
                return None
            case "Utvisning for Leder":
                return None
            case "Kampen er slutt":
                return None
            case _:
                prints.warning(self, f"Failed to read '{type}', trying again")
                return False
        return type  # Player, time, spillemål/straffe?

    def _get_team(self, str):
        if str == "home-team":
            return self.game.home
        if str == "away-team":
            return self.game.away
        prints.warning(self, f"'{str}' not valid for team")

    def get_result(self):
        home_goals = 0
        away_goals = 0

        if self.game == None:
            return

        for item in self.events:
            if type(item) == PlayGoal or type(item) == PenaltyGoal:
                if item.team == self.game.home:
                    home_goals += 1
                else:
                    away_goals += 1
            if type(item) == OwnGoal:
                if item.team == self.game.home:
                    away_goals += 1
                else:
                    home_goals += 1
        return (home_goals, away_goals)

    def get_analysis(self):
        data = []
        for item in self.events:
            data.append(item.get_analysis())
        return data

    def __repr__(self) -> str:
        home_goals, away_goals = self.get_result()
        return f"{home_goals} - {away_goals}"
