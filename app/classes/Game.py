from datetime import datetime, timedelta
import settings
import tools.points as points
from classes.Event import Substitute, PlayGoal, OwnGoal, Penalty, Assist, YellowCard, RedCard
from classes.Pitch import Pitch
from classes.Page import Page
from bs4 import BeautifulSoup
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.prints as prints


class Game:
    def __init__(self, url, tournament, valid_from):
        self.url = url
        self.valid_from = valid_from
        self.page = None
        self.tournament = tournament
        self.events = []
        self.temp_events = []
        self.teams = {
            "home": {
                "team": None,
                "name": None,
                "manager": None,
                "formation": None,
                "lineup": [[], []],
                "goals": 0,  # Subject to change during the game
                "xi": [],  # Subject to change during the game
                "bench": [],  # Subject to change during the game
                "stats": {},
                "number": None,
                "points": None,
                "previous": [],
            },
            "away": {
                "team": None,
                "name": None,
                "manager": None,
                "formation": None,
                "lineup": [[], []],
                "goals": 0,  # Subject to change during the game
                "xi": [],  # Subject to change during the game
                "bench": [],  # Subject to change during the game
                "stats": {},
                "number": None,
                "points": None,
                "previous": [],
            }
        }
        self.spectators = None
        self.winner = None
        self.score = None
        self.odds = None  # Not yet implemented a way to get the odds
        self.analysised = False
        self.post_game_points = {}
        self._load()

    def _load(self):
        data = ft.get_json(ft.TF_url_to_id(self.url), "Games")
        if data:
            self.fetched = datetime.strptime(data["meta"]["date"], '%Y-%m-%d').date()
            data = data["data"]
            self.date = datetime.strptime(data["date"], '%Y-%m-%d').date()
            if self.refetch():
                return
            self.gameId = data["gameId"]
            self.day = data["day"]
            self.time = data["time"]
            self.round = int(data["round"])
            for team in ["home", "away"]:
                self.teams[team]["name"] = data[f"{team}_name"]
                self.teams[team]["team"] = self.tournament.get_team(data[f"{team}_name"],
                                                                    data[f"{team}_url"])
                self.teams[team]["number"] = self.teams[team]["team"].current_position()
                self.teams[team]["points"] = self.teams[team]["team"].points
                self.teams[team]["previous"] = self.teams[team]["team"].get_prev_5_games()
            if self.date > settings.DATE:
                return
            self.pitch = Pitch(data["pitch_url"])
            for team in ["home", "away"]:
                self.teams[team]["manager"] = data[f"{team}_manager"]
                self.teams[team]["formation"] = data[f"{team}_lineup"]
                self.teams[team]["stats"] = data[f"{team}_stats"]
            self.score = data["score"]
            if not self.teams["home"]["stats"]:
                prints.warning("Statistics data not avaliable", f"{self.url}")
            else:
                for team in ["home", "away"]:
                    for category in self.teams[team]["stats"]:
                        self.teams[team]["team"].assign_points_stats(
                            category, int(self.teams[team]["stats"][category]), self)
            for team in ["home", "away"]:
                for player in data[f"{team}_start"]:
                    player = self.teams[team]["team"].get_player(url=player)
                    self.teams[team]["xi"].append(player)
                    player.matches["started"].append(self)
                for player in data[f"{team}_bench"]:
                    player = self.teams[team]["team"].get_player(url=player)
                    self.teams[team]["bench"].append(player)
                    player.matches["benched"].append(self)
                self.teams[team]["lineup"] = [self.teams[team]["xi"].copy(),
                                              self.teams[team]["bench"].copy()]
                for player in self.teams[team]["xi"]:
                    player.points += points.START
                self.teams[team]["team"].add_game(self)  # Used to add this after the events

            for event in data["events"]:
                if not event:
                    continue
                if event["team_url"] == data["home_url"]:
                    team = self.teams["home"]["team"]
                else:
                    team = self.teams["away"]["team"]
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
                        assist = None
                        if event["fouled"]:
                            fouled = team.get_player(url=event["fouled"]["player_url"])
                            assist = Assist(player=fouled,
                                            info=event["fouled"]["info"],
                                            url=self.url)
                        pen = Penalty(game=self,
                                      time=int(event["time"]),
                                      team=team,
                                      player=team.get_player(url=event["player_url"]),
                                      goal=event["goal"],
                                      keeper=opposition.get_player(url=event["keeper_url"]),
                                      fouled=assist)
                        if assist:
                            assist.goal = pen
                        self.events.append(pen)
                    case "OwnGoal":
                        own = OwnGoal(game=self,
                                      time=int(event["time"]),
                                      team=team,
                                      player=team.get_player(url=event["player_url"]),
                                      keeper=opposition.get_player(url=event["keeper_url"]))
                        self.events.append(own)
                    case "Playgoal":
                        assist = None
                        if event["assist"]:
                            player = team.get_player(url=event["assist"]["player_url"])
                            assist = Assist(player=player,
                                            info=event["assist"]["info"],
                                            url=self.url)
                        goal = PlayGoal(game=self,
                                        time=int(event["time"]),
                                        team=team,
                                        player=team.get_player(url=event["player_url"]),
                                        assist=assist,
                                        info=event["info"],
                                        keeper=opposition.get_player(url=event["keeper_url"]))
                        if assist:
                            assist.goal = goal
                            team.graphs["assists"].add_edge(assist.player.name,
                                                            goal.player.name)
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
                        prints.error(self, f"{event['type']} not handled")
            self.get_result()
            self.analysised = True
            return
        self.TM_analysis()

    def _analysed_to_json(self):
        m = {
            "meta": {
                "version": 1,
                "date": str(self.fetched),
            },
            "data": {
                "gameId": self.gameId,
                "day": self.day,
                "time": str(self.time),
                "date": str(self.date),
                "round": self.round,
                "home_name": self.teams["home"]["team"].name,
                "home_url": self.teams["home"]["team"].url,
                "home_manager": self.teams["home"]["manager"],
                "home_stats": self.teams["home"]["stats"],
                "home_lineup": self.teams["home"]["formation"],
                "away_name": self.teams["away"]["team"].name,
                "away_url": self.teams["away"]["team"].url,
                "away_manager": self.teams["away"]["manager"],
                "away_stats": self.teams["away"]["stats"],
                "away_lineup": self.teams["away"]["formation"],
                "score": self.score,
                "pitch_url": self.pitch.url,
                "home_start": [],
                "home_bench": [],
                "away_start": [],
                "away_bench": [],
                "events": [],

            }
        }
        for team in ["home", "away"]:
            for player in self.teams[team]["lineup"][0]:
                m["data"][f"{team}_start"].append(player.url)
            for player in self.teams[team]["lineup"][1]:
                m["data"][f"{team}_bench"].append(player.url)
        events = sorted(self.events, key=lambda x: x.time)
        for event in events:
            m["data"]["events"].append(event.to_json())

        return m

    def px_to_minute(self, data):
        left, right = data.split("px ")
        left = int(left)*-1
        right = int(right)*-1
        for i in range(0, 10):
            if left == i*36:
                left = i+1
                break

        for i in range(1, 10):
            if right == i*36:
                right = i
                break
        if right > 10:
            right = 0
        if left >= 10:
            left = 0
            right += 1
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
            if keeper in self.teams["home"]["team"].get_player_urls():
                keeper = self.teams["home"]["team"].get_player(url=keeper)
                taker = self.teams["away"]["team"].get_player(url=taker)
                team = self.teams["away"]["team"]
            else:
                keeper = self.teams["away"]["team"].get_player(url=keeper)
                taker = self.teams["home"]["team"].get_player(url=taker)
                team = self.teams["home"]["team"]
            px = rt.standard_reg(document, r'(-\d+px -\d+)')
            time = self.px_to_minute(px)
            self.temp_events.append(["Penalty",
                                     self,
                                     time,
                                     team,
                                     taker,
                                     False,
                                     False])

    def TM_goals(self, document: BeautifulSoup):
        for team in [self.teams["home"]["team"], self.teams["away"]["team"]]:
            string = "sb-aktion-heim" if team == self.teams["home"]["team"] else "sb-aktion-gast"

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

                            assist = Assist(team.get_player(name=splitted[0]), info, url=self.url)
                        else:
                            prints.warning(self, f"{splitted[0]} does not play for {team}")

                splitted = data[0].split(",")
                if "OWN-GOAL" in splitted[1].upper():
                    temp_team = self.opponent(team)
                    self.temp_events.append(["OwnGoal",
                                             self,
                                             time,
                                             temp_team,
                                             temp_team.get_player(name=splitted[0])])
                    continue
                if "PENALTY" in splitted[1].upper():
                    player = team.get_player(name=splitted[0])
                    self.temp_events.append(["Penalty",
                                             self,
                                             time,
                                             team,
                                             player,
                                             True,
                                             assist])
                    continue
                info = splitted[1] if "Goal of the Season" not in splitted[1] else None
                self.temp_events.append(["PlayGoal",
                                        self,
                                        time,
                                        team,
                                        team.get_player(name=splitted[0]),
                                        assist,
                                        info])

    def TM_cards(self, document: BeautifulSoup):
        for team in [self.teams["home"]["team"], self.teams["away"]["team"]]:
            string = "sb-aktion-heim" if team == self.teams["home"]["team"] else "sb-aktion-gast"

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
                    self.temp_events.append(["YellowCard", self, time, team, player, reason])
                if "RED" in color.upper():
                    self.temp_events.append(["RedCard", self, time, team, player, reason])

    def TM_substitutions(self, document: BeautifulSoup):
        for team in [self.teams["home"]["team"], self.teams["away"]["team"]]:
            string = "sb-aktion-heim" if team == self.teams["home"]["team"] else "sb-aktion-gast"

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
                    self.temp_events.append(["Substitute",
                                            self,
                                            time,
                                            team,
                                            [player_in, player_out],
                                            reason])
                    continue
                if "Substitution without replacement" in sub.get_text(strip=True):
                    player_out = inout[0]
                    self.temp_events.append(["Substitute",
                                            self,
                                            time,
                                            team,
                                            [player_out, None],
                                            reason])

    def TM_individual_lineup(self, team, xi, bench, document: BeautifulSoup):
        data = document.find_all(class_="large-7 columns small-12 aufstellung-vereinsseite")
        if data:
            for url in rt.find_urls(str(data[0])):
                player = team.get_player(url=url)
                player.matches["started"].append(self)
                xi.append(player)

            table = document.find("table")
            for url in rt.find_urls(str(table)):
                if "spieler" in url:
                    player = team.get_player(url=url)
                    player.matches["benched"].append(self)
                    bench.append(player)
                if "trainer" in url:
                    if team == self.teams["home"]["team"]:
                        self.teams["home"]["manager"] = url
                    else:
                        self.teams["away"]["manager"] = url
            return
        data = document.find("table")
        urls = rt.standard_findall(data, r'<a href="(.[^"]*)"')
        if team == self.teams["home"]["team"]:
            self.teams["home"]["manager"] = "https://www.transfermarkt.com" + urls[-1]
        else:
            self.teams["away"]["manager"] = "https://www.transfermarkt.com" + urls[-1]
        if len(urls[:-1]) == 11:
            for url in urls[:-1]:
                player = team.get_player(url=("https://www.transfermarkt.com" + url))
                player.matches["started"].append(self)
                xi.append(player)
        else:
            prints.warning(self, f"Who are these {len(urls)} players? {urls}")

    def TM_line_ups(self, document: BeautifulSoup):
        divs = document.find_all("div", recursive=False)
        i = 0
        for team in ["home", "away"]:
            self.TM_individual_lineup(self.teams[team]["team"],
                                      self.teams[team]["xi"],
                                      self.teams[team]["bench"],
                                      divs[i])
            i += 1
            self.teams[team]["lineup"] = [self.teams[team]["xi"].copy(),
                                          self.teams[team]["bench"].copy()]

    def TM_analysis(self):
        self.page = Page(self.url, valid_from=self.valid_from)
        self.fetched = self.page.html.fetched
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
            self.round = int(matchday.split(".")[0])
        else:
            self.round = 0
            prints.warning(self.url, "Round not found")

        if date:
            self.day, self.date = date.split(", ")
            self.date = datetime.strptime(self.date, "%m/%d/%y").date()
            if self.refetch():
                return
        else:
            self.day = None
            self.date = None
            prints.warning(self.url, "Day/date not found")

        if time:
            self.time = datetime.strptime(time.strip(), "%H:%M PM")
            if "PM" in time:
                self.time = str(self.time + timedelta(hours=12)).split(" ")[1]
            else:
                self.time = str(self.time).split(" ")[1]
        else:
            self.time = None
            prints.warning(self.url, "Time not found")

        hometeam = document.find(class_="sb-team sb-heim")
        url = rt.find_urls(str(hometeam))[0]
        title = rt.standard_reg(str(hometeam), r'<a href=.[^>]* title="(.[^"]*)">')
        self.teams["home"]["team"] = self.tournament.get_team(title, url)

        awayteam = document.find(class_="sb-team sb-gast")
        url = rt.find_urls(str(awayteam))[0]
        title = rt.standard_reg(str(awayteam), r'<a href=.[^>]* title="(.[^"]*)">')
        self.teams["away"]["team"] = self.tournament.get_team(title, url)

        for team in ["home", "away"]:
            self.teams[team]["number"] = self.teams[team]["team"].current_position()
            self.teams[team]["previous"] = self.teams[team]["team"].get_prev_5_games()

        if self.date > settings.DATE:
            return
        if self.analysised:
            prints.info("Read from analysis", self)
            return

        string = "large-7 aufstellung-vereinsseite columns small-12 "
        string += "unterueberschrift aufstellung-unterueberschrift"
        data = document.find_all(class_=string)
        for d in data:
            if self.teams["home"]["lineup"][0]:
                self.teams["home"]["lineup"][0] = d.get_text(strip=True).strip("Starting Line-up: ")
                continue
            self.teams["home"]["lineup"][0] = d.get_text(strip=True).strip("Starting Line-up: ")

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
        lineup_found = False
        for box in boxes:
            header = rt.standard_reg(box, r'content-box-headline">\n(.[^<]*)')
            if not header:
                continue
            head = header.strip()
            if head == "Line-Ups":
                lineup_found = True
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

        if not lineup_found:
            prints.warning(self, f"No lineup: {self.url}")
            ft.delete_html(url=self.url)
            return

        events = {
            "PlayGoal": PlayGoal,
            "Substitute": Substitute,
            "Penalty": Penalty,
            "OwnGoal": OwnGoal,
            "RedCard": RedCard,
            "YellowCard": YellowCard,
        }
        START_POINTS = 10
        for player in self.teams["home"]["lineup"][0]:
            player.points += START_POINTS
        for player in self.teams["away"]["lineup"][0]:
            player.points += START_POINTS

        self.temp_events = sorted(self.temp_events, key=lambda x: x[2])

        for item in self.temp_events:
            if item[0] in ["Penalty", "PlayGoal", "OwnGoal"]:
                keeper = self.get_keeper(self.opponent(item[3]))
                item.append(keeper)
            e = events[item[0]](lst=(item[1:]))
            if item[0] == "Penalty":
                if item[6]:
                    item[6].goal = e
            if item[0] == "PlayGoal":
                if item[5]:
                    item[5].goal = e
                    e.player.graphs["assists"].add_edge(item[5].player.name,
                                                        e.player.name)
            self.events.append(e)
        self.score = self.get_result()
        self.teams["home"]["team"].add_game(self)
        self.teams["away"]["team"].add_game(self)
        statistics = Page(url=self.url.replace("index", "statistik"))
        soup = BeautifulSoup(statistics.html.text, 'html.parser')
        unterueberschrift_elements = soup.find_all(class_="unterueberschrift")
        stats = {}
        for unterueberschrift in unterueberschrift_elements[:len(unterueberschrift_elements)-2]:
            # Get the next sibling (which is the element after "unterueberschrift")
            key = unterueberschrift.get_text().strip()
            next_sibling = unterueberschrift.find_next_sibling()
            if next_sibling:
                values = []
                for value in next_sibling.get_text().split("\n"):
                    if value.strip():
                        values.append(value)
                if values:
                    stats[key] = values
        for category in stats:
            self.teams["home"]["team"].assign_points_stats(category, int(stats[category][0]), self)
            self.teams["away"]["team"].assign_points_stats(category, int(stats[category][1]), self)
            self.teams["home"]["stats"][category] = stats[category][0]
            self.teams["away"]["stats"][category] = stats[category][1]
        if not self.teams["home"]["stats"]:
            prints.warning("Statistics data not avaliable", f"{self.url}")

        ft.write_json(self._analysed_to_json(), ft.TF_url_to_id(self.url), "Games")
        self.analysised = True
        prints.info("Analysed", self)

    def _is_played(self):
        return self.date < settings.DATE

    def get_keeper(self, team):
        if team == self.teams["home"]["team"]:
            xi = self.teams["home"]["xi"]
        else:
            xi = self.teams["away"]["xi"]
        for player in xi:
            if player.position == "Goalkeeper":
                return player
        prints.error("Game: get_keeper", f"Failed to find keeper: {self.url}")
        return None

    def opponent(self, team):
        if team == self.teams["home"]["team"]:
            return self.teams["away"]["team"]
        if team == self.teams["away"]["team"]:
            return self.teams["home"]["team"]
        return False

    def refetch(self):
        two_weeks_ago = datetime.today() - timedelta(days=14)
        if self.fetched <= two_weeks_ago.date():
            if self.fetched - timedelta(days=14) > self.date:
                if not self.page:
                    self.page = Page(self.url, force=True, valid_from=self.valid_from)
                self.page.html.force_fetch_html()
                self.TM_analysis()
                return True
        return False

    def get_timed_result(self, time):
        home_goals = 0
        away_goals = 0

        for item in self.events:
            if item.time > time:
                continue
            # changed from type(item)
            if isinstance(item, PlayGoal):
                if item.team == self.teams["home"]["team"]:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, Penalty):
                if not item.goal:
                    continue
                if item.team == self.teams["home"]["team"]:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, OwnGoal):
                if item.team == self.teams["home"]["team"]:
                    away_goals += 1
                else:
                    home_goals += 1
        self.winner = None
        if home_goals > away_goals:
            self.winner = self.teams["home"]["team"]
        elif home_goals < away_goals:
            self.winner = self.teams["away"]["team"]

        return (home_goals, away_goals)

    def WDL_team(self, team):
        if not self.winner:
            return f"{prints.get_yellow_fore('D')}"
        if team == self.winner:
            return f"{prints.get_green_fore('W')}"
        return f"{prints.get_red_fore('L')}"

    def get_result(self):
        home_goals = 0
        away_goals = 0

        for item in self.events:
            # changed from type(item)
            if isinstance(item, PlayGoal):
                if item.team == self.teams["home"]["team"]:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, Penalty):
                if not item.goal:
                    continue
                if item.team == self.teams["home"]["team"]:
                    home_goals += 1
                else:
                    away_goals += 1
            if isinstance(item, OwnGoal):
                if item.team == self.teams["home"]["team"]:
                    away_goals += 1
                else:
                    home_goals += 1
        self.winner = None
        if home_goals > away_goals:
            self.winner = self.teams["home"]["team"]
        elif home_goals < away_goals:
            self.winner = self.teams["away"]["team"]

        return (home_goals, away_goals)

    def __repr__(self) -> str:
        s = f"{self.date} "
        s += f"({str(self.teams['home']['number']):>2}){self.teams['home']['team'].nickname:>12}"
        if self.score:
            s += f" {self.score[0]}-{self.score[1]} "
        else:
            s += " - "
        s += f"{self.teams['away']['team'].nickname:<12}({str(self.teams['away']['number']):>2})"
        return s
