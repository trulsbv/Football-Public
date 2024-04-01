from datetime import datetime, timedelta
import settings
from classes.Event import Substitute, PlayGoal, OwnGoal, Penalty, Assist, YellowCard, RedCard
from classes.Pitch import Pitch
from classes.Page import Page
from bs4 import BeautifulSoup
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.prints as p


class Game:
    def __init__(self, url, tournament, valid_from):
        self.url = url
        self.valid_from = valid_from
        self.tournament = tournament
        self.events = []

        self.hometeam = None
        self.awayteam = None
        self._save_home = [[], []]
        self._save_away = [[], []]
        self.spectators = None
        self.winner = None
        self.score = None
        self.odds = None  # Not yet implemented a way to get the odds
        self.home_lineup = None
        self.away_lineup = None
        self.analysised = False
        self._load()

    def _load(self):
        data = ft.get_json(ft.TF_url_to_id(self.url), "Games")
        if data:
            data = data["data"]
            self.gameId = data["gameId"]
            self.day = data["day"]
            self.time = data["time"]
            self.date = datetime.strptime(data["date"], '%Y-%m-%d').date()
            self.home_name = data["home_name"]
            self.home = self.tournament.get_team(data["home_name"], data["home_url"])
            self.away_name = data["away_name"]
            self.away = self.tournament.get_team(data["away_name"], data["away_url"])

            if self.date > settings.DATE:
                return
            self.pitch = Pitch(data["pitch_url"])
            self.home_manager = data["home_manager"]
            self.home_lineup = data["home_lineup"]
            self.away_manager = data["away_manager"]
            self.away_lineup = data["away_lineup"]
            self.score = data["score"]
            self.home_xi = []
            self.home_bench = []
            self.away_xi = []
            self.away_bench = []

            for player in data["home_start"]:
                player = self.home.get_player(url=player)
                self.home_xi.append(player)
                player.matches["started"].append(self)
            for player in data["home_bench"]:
                player = self.home.get_player(url=player)
                self.home_bench.append(player)
                player.matches["benched"].append(self)
            for player in data["away_start"]:
                player = self.away.get_player(url=player)
                self.away_xi.append(player)
                player.matches["started"].append(self)
            for player in data["away_bench"]:
                player = self.away.get_player(url=player)
                self.away_bench.append(player)
                player.matches["benched"].append(self)

            self._save_home = [self.home_xi.copy(), self.home_bench.copy()]
            self._save_away = [self.away_xi.copy(), self.away_bench.copy()]

            for event in data["events"]:
                if not event:
                    continue
                team = self.home if event["team_url"] == data["home_url"] else self.away
                opposition = self.opponent(team)
                match event["type"]:
                    case "Substitution":
                        sub = Substitute(game=self,
                                         time=int(event["time"]),
                                         team=team,
                                         players=[event["out_url"], event["in_url"]],
                                         reason=event["reason"])
                        self.events.append(sub)
                    case "Penalty":
                        k = event["keeper_url"]
                        keeper = None if not k else opposition.get_player(url=k)
                        assist = None
                        if event["fouled"]:
                            fouled = team.get_player(url=event["fouled"]["player_url"])
                            assist = Assist(player=fouled,
                                            info=event["fouled"]["info"])
                        pen = Penalty(game=self,
                                      time=int(event["time"]),
                                      team=team,
                                      player=team.get_player(url=event["player_url"]),
                                      goal=event["goal"],
                                      keeper=keeper,
                                      fouled=assist)
                        if assist:
                            assist.goal = pen
                        self.events.append(pen)
                    case "OwnGoal":
                        own = OwnGoal(game=self,
                                      time=int(event["time"]),
                                      team=team,
                                      player=team.get_player(url=event["player_url"]))
                        self.events.append(own)
                    case "Playgoal":
                        assist = None
                        if event["assist"]:
                            player = team.get_player(url=event["assist"]["player_url"])
                            assist = Assist(player=player,
                                            info=event["assist"]["info"])
                        goal = PlayGoal(game=self,
                                        time=int(event["time"]),
                                        team=team,
                                        player=team.get_player(url=event["player_url"]),
                                        assist=assist,
                                        info=event["info"])
                        if assist:
                            assist.goal = goal
                        self.events.append(goal)
                    case "Yellow card":
                        card = YellowCard(game=self,
                                          time=int(event["time"]),
                                          team=team,
                                          player=team.get_player(url=event["player_url"]),
                                          reason=event["reason"])
                        self.events.append(card)
                    case "Red card":
                        card = RedCard(game=self,
                                       time=int(event["time"]),
                                       team=team,
                                       player=team.get_player(url=event["player_url"]),
                                       reason=event["reason"])
                        self.events.append(card)
                    case _:
                        p.error(self, f"{event['type']} not handled")

            self.analysised = True
            self.home.add_game(self)
            self.away.add_game(self)
            return
        # TODO: See if games can be analysed immediatly
        self.TM_analysis()

    def _unanalysed_to_json(self):
        m = {
            "meta": {
                "version": 2,
                "date": str(settings.DATE),
            },
            "data": {
                "home_name": self.home.name,
                "home_url": self.home.url,
                "away_name": self.away.name,
                "away_url": self.away.url,
                "gameId": self.gameId,
                "day": self.day,
                "time": str(self.time),
                "date": self.date,
            }
        }
        return m

    def _analysed_to_json(self):
        m = {
            "meta": {
                "version": 1,
                "date": str(settings.DATE),
            },
            "data": {
                "gameId": self.gameId,
                "day": self.day,
                "time": str(self.time),
                "date": str(self.date),
                "home_name": self.home.name,
                "home_url": self.home.url,
                "home_manager": self.home_manager,
                "home_lineup": self.home_lineup,
                "away_name": self.away.name,
                "away_url": self.away.url,
                "away_manager": self.away_manager,
                "away_lineup": self.away_lineup,
                "score": self.score,
                "pitch_url": self.pitch.url,
                "home_start": [],
                "home_bench": [],
                "away_start": [],
                "away_bench": [],
                "events": [],

            }
        }
        for player in self.home_start_xi:
            m["data"]["home_start"].append(player.url)
        for player in self.home_start_bench:
            m["data"]["home_bench"].append(player.url)
        for player in self.away_start_xi:
            m["data"]["away_start"].append(player.url)
        for player in self.away_start_bench:
            m["data"]["away_bench"].append(player.url)
        events = sorted(self.events, key=lambda x: x.time)
        for event in events:
            m["data"]["events"].append(event.to_json())

        return m

    def px_to_minute(self, data):
        left, right = data.split("px ")
        left = int(left)*-1
        right = int(right)*-1
        for i in range(0, 9):
            if left == i*36:
                left = i+1
                break
        if left > 10:
            left = 0

        for i in range(1, 10):
            if right == i*36:
                right = i
                break
        if right > 10:
            right = 0
        return int(str(right) + str(left))

    def TM_missed_penalties(self, document: BeautifulSoup):
        # TODO: Problem with multiple missed penalties!
        # https://www.transfermarkt.com/molde-fk_fk-bodo-glimt/index/spielbericht/3993145
        urls = rt.find_urls(str(document))
        chosen = []
        for url in urls:
            if "spieler" in url and "leistungsdatendetails" not in url:
                chosen.append(url)
        while chosen:
            keeper = chosen.pop(0)
            taker = chosen.pop(0)
            if keeper in self.home.get_player_urls():
                keeper = self.home.get_player(url=keeper)
                taker = self.away.get_player(url=taker)
                team = self.away
            else:
                keeper = self.away.get_player(url=keeper)
                taker = self.home.get_player(url=taker)
                team = self.home
            px = rt.standard_reg(document, r'(-\d+px -\d+)')
            time = self.px_to_minute(px)
            self.events.append(Penalty(self, time, team, taker, False, keeper))

    def TM_goals(self, document: BeautifulSoup):
        for team in [self.home, self.away]:
            if team == self.home:
                string = "sb-aktion-heim"
            else:
                string = "sb-aktion-gast"

            gls = document.find_all(class_=string)
            for goal in gls:
                involved = goal.find(class_="sb-aktion-aktion")
                data = involved.get_text(strip=True).split("Assist:")
                px = rt.standard_reg(goal, r'(-\d+px -\d+)')
                time = self.px_to_minute(px)
                assist = None
                if len(data) > 1:
                    splitted = data[1].split(",")
                    if len(splitted) > 1:
                        if splitted[0] in team.get_player_names():
                            info = splitted[1] if "Assist of the Season" not in splitted[1] else ""

                            assist = Assist(team.get_player(name=splitted[0]), info)
                        else:
                            p.warning(self, f"{splitted[0]} does not play for {team}")

                splitted = data[0].split(",")
                if "OWN-GOAL" in splitted[1].upper():
                    temp_team = self.opponent(team)
                    self.events.append(OwnGoal(self,
                                               time,
                                               temp_team,
                                               temp_team.get_player(name=splitted[0])))
                    continue
                if "PENALTY" in splitted[1].upper():
                    player = team.get_player(name=splitted[0])

                    if team == self.home:
                        keeper_team = self.away_xi
                    else:
                        keeper_team = self.home_xi
                    keeper = None
                    for plyer in keeper_team:
                        if plyer.position == "Goalkeeper":
                            keeper = plyer
                            break
                    if not keeper:
                        p.warning(self, "No keeper found at penalty")
                    g = Penalty(self, time, team, player, True, keeper, assist)
                    if assist:
                        assist.goal = g
                    self.events.append(g)
                    continue
                g = PlayGoal(self,
                             time=time,
                             team=team,
                             player=team.get_player(name=splitted[0]),
                             assist=assist,
                             info=splitted[1].strip())
                if assist:
                    assist.goal = g
                self.events.append(g)

    def TM_cards(self, document: BeautifulSoup):
        for team in [self.home, self.away]:
            if team == self.home:
                string = "sb-aktion-heim"
            else:
                string = "sb-aktion-gast"

            crd = document.find_all(class_=string)
            for card in crd:
                player = card.find(class_="sb-aktion-aktion")
                time = self.px_to_minute(rt.standard_reg(card, r'(-\d+px -\d+)'))
                name = rt.standard_reg(player, r'title="(.[^"]*)"')
                type = rt.standard_reg(player, r'title=".[^\n]*\n(.[^<]*)<').strip()
                player = team.get_player(name=name)
                if "," in type:
                    color, reason = (type.split(","))
                    reason = reason.strip()
                else:
                    color = type
                    reason = None
                if "YELLOW" in color.upper():
                    self.events.append(YellowCard(self, time, team, player, reason))
                if "RED" in color.upper():
                    self.events.append(RedCard(self, time, team, player, reason))

    def TM_substitutions(self, document: BeautifulSoup):
        for team in [self.home, self.away]:
            if team == self.home:
                string = "sb-aktion-heim"
            else:
                string = "sb-aktion-gast"

            subs = document.find_all(class_=string)
            for sub in subs:
                inout = []
                for url in rt.find_urls(str(sub)):
                    if "spieler" in url and "leistungsdatendetails" not in url:
                        inout.append(url)
                time = self.px_to_minute(rt.standard_reg(sub, r'(-\d+px -\d+)'))
                reason = rt.standard_reg(sub, r'hide-for-small">,(.[^<]*)<')
                if reason:
                    reason = reason.strip()
                if len(inout) == 2:
                    player_in, player_out = inout
                    self.events.append(Substitute(self,
                                                  time,
                                                  team,
                                                  [player_in, player_out],
                                                  reason))
                    continue
                if "Substitution without replacement" in sub.get_text(strip=True):
                    player_out = inout[0]
                    self.events.append(Substitute(self, time, team, [player_out, None], reason))

    def TM_individual_lineup(self, team, xi, bench, document: BeautifulSoup):
        data = document.find_all(class_="large-7 columns small-12 aufstellung-vereinsseite")
        if data:
            for url in rt.find_urls(str(data[0])):
                player = team.get_player(url=url)
                player.matches["started"].append(self)
                xi.append(player)

            table = document.find("table")
            self.home_manager = None
            self.away_manager = None
            for url in rt.find_urls(str(table)):
                if "spieler" in url:
                    player = team.get_player(url=url)
                    player.matches["benched"].append(self)
                    bench.append(player)
                if "trainer" in url:
                    if team == self.home:
                        self.home_manager = url
                    else:
                        self.away_manager = url
            return
        data = document.find("table")
        names = rt.standard_findall(data, r'title="(.[^"]*)"')
        if team == self.home:
            self.home_manager = names[-1]
        else:
            self.away_manager = names[-1]
        if len(names[:-1]) == 11:
            for name in names[:-1]:
                player = team.get_player(name=name)
                player.matches["started"].append(self)
                xi.append(player)
        else:
            p.warning(self, f"Who are these {len(names)} players? {names}")

    def TM_line_ups(self, document: BeautifulSoup):
        divs = document.find_all("div", recursive=False)

        self.home_xi = []
        self.home_bench = []
        self.away_xi = []
        self.away_bench = []

        self.TM_individual_lineup(self.home, self.home_xi, self.home_bench, divs[0])
        self.TM_individual_lineup(self.away, self.away_xi, self.away_bench, divs[1])

        self.home_start_xi = self.home_xi.copy()
        self.home_start_bench = self.home_bench.copy()
        self.away_start_xi = self.away_xi.copy()
        self.away_start_bench = self.away_bench.copy()

    def TM_analysis(self):
        self.page = Page(self.url, self.valid_from)
        document = BeautifulSoup(self.page.html.text, "html.parser")
        self.gameId = self.url.split("/")[-1]
        items = document.find(class_="sb-datum hide-for-small").get_text(strip=True).split("|")
        matchday = None
        date = None
        time = None
        for item in items:
            if "day" in item:
                matchday = item
            if "/" in item:
                date = item
            if ":" in item:
                time = item

        if matchday:
            self.round = matchday.split(".")[0]
        else:
            self.round = None
            p.warning(self.url, "Round not found")

        if date:
            self.day, self.date = date.split(", ")
            self.date = datetime.strptime(self.date, "%m/%d/%y").date()
        else:
            self.day = None
            self.date = None
            p.warning(self.url, "Day/date not found")

        if time:
            self.time = datetime.strptime(time.strip(), "%H:%M PM")
            if "PM" in time:
                self.time = str(self.time + timedelta(hours=12)).split(" ")[1]
            else:
                self.time = str(self.time).split(" ")[1]
        else:
            self.time = None
            p.warning(self.url, "Time not found")

        hometeam = document.find(class_="sb-team sb-heim")
        url = rt.find_urls(str(hometeam))[0]
        title = rt.standard_reg(str(hometeam), r'<a href=.[^>]* title="(.[^"]*)">')
        self.home = self.tournament.get_team(title, url)

        awayteam = document.find(class_="sb-team sb-gast")
        url = rt.find_urls(str(awayteam))[0]
        title = rt.standard_reg(str(awayteam), r'<a href=.[^>]* title="(.[^"]*)">')
        self.away = self.tournament.get_team(title, url)

        if self.date > settings.DATE:
            return
        if self.analysised:
            p.info("Read from analysis", self)
            return

        string = "large-7 aufstellung-vereinsseite columns small-12 "
        string += "unterueberschrift aufstellung-unterueberschrift"
        data = document.find_all(class_=string)
        for d in data:
            if self.home_lineup:
                self.away_lineup = d.get_text(strip=True).strip("Starting Line-up: ")
                continue
            self.home_lineup = d.get_text(strip=True).strip("Starting Line-up: ")

        info = document.find("p", class_="sb-zusatzinfos")
        self.spectators = rt.standard_reg(str(info), r'Attendance: (\d+?.\d+)<')
        if self.spectators:
            self.spectators = int(self.spectators.replace(".", ""))
        self.referee = rt.standard_reg(str(info), r'Referee:.*title.[^>]*>(.[^<]*)<')

        urls = rt.find_urls(str(info))
        for url in urls:
            if "stadion" in url:
                self.pitch = Pitch(url)
        boxes = document.find_all(class_="box")

        for box in boxes:
            header = rt.standard_reg(box, r'content-box-headline">\n(.[^<]*)')
            if not header:
                continue
            head = header.strip()
            if head == "Line-Ups":
                self.TM_line_ups(box)
            if head == "Special events":
                continue
            if head == "missed penalties":
                self.TM_missed_penalties(box)
            if head == "Goals":
                self.TM_goals(box)
            if head == "Substitutions":
                self.TM_substitutions(box)
            if head == "Cards":
                self.TM_cards(box)

        self.score = self.get_result()
        self.home.add_game(self)
        self.away.add_game(self)
        ft.write_json(self._analysed_to_json(), ft.TF_url_to_id(self.url), "Games")
        self.analysised = True
        p.info("Analysed", self)

    def break_rules(self):
        rules = [
            settings.display_surface
            and self.pitch.surface not in settings.display_surface,
        ]
        for rule in rules:
            if rule:
                return True
        return False

    def _is_played(self):
        return self.date < settings.DATE

    def opponent(self, team):
        if team == self.home:
            return self.away
        if team == self.away:
            return self.home
        return False

    def get_timed_result(self, time):
        home_goals = 0
        away_goals = 0

        for item in self.events:
            if item.time > time:
                continue
            # changed from type(item)
            if isinstance(item, PlayGoal):
                if item.team == self.home:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, Penalty):
                if not item.goal:
                    continue
                if item.team == self.home:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, OwnGoal):
                if item.team == self.home:
                    away_goals += 1
                else:
                    home_goals += 1

        if home_goals > away_goals:
            self.winner = self.home
        elif home_goals < away_goals:
            self.winner = self.away

        return (home_goals, away_goals)

    def get_result(self):
        home_goals = 0
        away_goals = 0

        for item in self.events:
            # changed from type(item)
            if isinstance(item, PlayGoal):
                if item.team == self.home:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, Penalty):
                if not item.goal:
                    continue
                if item.team == self.home:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, OwnGoal):
                if item.team == self.home:
                    away_goals += 1
                else:
                    home_goals += 1

        if home_goals > away_goals:
            self.winner = self.home
        elif home_goals < away_goals:
            self.winner = self.away

        return (home_goals, away_goals)

    def __repr__(self) -> str:
        s = ""
        s += f"{self.date} {self.home.nickname}"
        if self.score:
            s += f" {self.score[0]}-{self.score[1]} "
        else:
            s += " - "
        s += f"{self.away.nickname}"
        return s
