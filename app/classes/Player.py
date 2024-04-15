from classes.Event import (
    OwnGoal,
    Penalty,
    PlayGoal,
    RedCard,
    YellowCard,
    Goal,
    Assist,
    ConcededGoal,
)
import tools.prints as prints
import tools.regex_tools as rt
import tools.file_tools as ft
import tools.statistic_tools as statt
from classes.Page import Page
import settings
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


class Player:
    def __init__(self, team, url, graphs):
        self.team = team
        self.url = url
        self.graphs = graphs
        self.datasets = []
        self.matches = {"started": [], "sub in": {}, "sub out": {}, "benched": []}
        self.events = []
        self.influence = {}
        self.name = None
        self.number = None
        self.birthday = None
        self.height = None
        self.role = None
        self.position = None
        self.nationality = None
        self.points = 0
        self._load()

    def events_to_df(self):
        temp = []
        for event in self.events:
            temp.append(event.to_dict())
        return pd.DataFrame(temp)

    def print_stats(self) -> None:
        """
        Prints info about the player to the terminal
        """
        container = statt.times_x_fits_in_y(settings.FRAME_SIZE, settings.GAME_LENGTH)
        print(self)
        s = "Event / Time "
        for time in container:
            s += f"-{time:<3} "
        print(s)
        stats = [Goal, PlayGoal, Penalty, OwnGoal, YellowCard, RedCard]
        s = " Min played: "
        minutes = [0 for _ in range(len(container))]

        for game in self.matches["started"]:
            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            else:
                out_time = 90
            for i in range(1, 90):
                if i <= out_time:
                    for j, upper_bound in enumerate(container):
                        if i <= upper_bound:
                            minutes[j] += 1
                            break

        for game in self.matches["sub in"]:
            in_time = self.matches["sub in"][game].time
            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            else:
                out_time = 90
            for i in range(0, 90):
                if in_time < i <= out_time:
                    for j, upper_bound in enumerate(container):
                        if i <= upper_bound:
                            minutes[j] += 1
                            break
        first = True
        for item in minutes:
            if first:
                s += f"{item:>3}"
                first = False
                continue
            s += f", {item:>3}"
        s += f" (= {sum(minutes)} min)"

        for stat in stats:
            result = statt.iterate_events(self.events, stat)
            s += f"\n{stat.__name__:>11}: "
            first = True
            for item in result:
                if first:
                    s += f"{item:>3}"
                    first = False
                    continue
                s += f", {item:>3}"
            s += f" (= {sum(result)})"
        print(s)

    def get_player_stats(self, stats: list) -> dict:
        output = {}
        for stat in stats:
            output[stat] = statt.iterate_events(self.events, stat)
        return output

    def get_points(self):
        if not self.points or not self.minutes_played():
            return 0
        return round(self.points/self.minutes_played(), 4)

    def minutes_played(self):
        total = 0
        for game in self.matches["started"]:
            in_time = 0
            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            else:
                out_time = 90
            total += (out_time-in_time)

        for game in self.matches["sub in"]:
            in_time = self.matches["sub in"][game].time

            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            else:
                out_time = 90
            total += (out_time-in_time)
        return total

    def results_while_playing(self):
        results_while_playing = []  # <-- (game, (before, after, end), (in, out))
        for game in self.matches["started"]:
            cur = (0, 0)
            in_time = 0
            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.get_result()
                out_time = 90
            end = game.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))

        for game in self.matches["sub in"]:
            cur = self.matches["sub in"][game].current_score
            in_time = self.matches["sub in"][game].time

            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.get_result()
                out_time = 90
            end = game.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))
        results_while_playing.sort(key=lambda x: x[0].date)
        # (x[0].date.year, x[0].date.month, x[0].date.day)
        return results_while_playing

    def num_goals(self):
        goals = statt.find_event(self.events, Goal)
        goal_counter = 0
        for g in goals:
            if isinstance(g, OwnGoal):
                goal_counter -= 1
            else:
                goal_counter += 1
        return goal_counter

    def num_assists(self):
        return len(statt.find_event(self.events, Assist))

    def get_num_games_result(self):
        win = 0
        draw = 0
        loss = 0
        for game in self.matches["started"]:
            if game.winner == self.team:
                win += 1
            elif game.winner is None:
                draw += 1
            else:
                loss += 1

        for sub in self.matches["sub in"]:
            if self.matches["sub in"][sub].game.winner == self.team:
                win += 1
            elif self.matches["sub in"][sub].game.winner is None:
                draw += 1
            else:
                loss += 1

        if win + draw + loss == 0:
            return None

        return (win, draw, loss)

    def print_events(self):
        WIDTH = 75
        for event in self.events:
            if not isinstance(event, Assist):
                continue
            if isinstance(event, Assist):
                s = f"({str(event.goal.time):>2}) Assist: "
                s += prints.mid(f"{event.inf} to {event.goal.player}", WIDTH-len(s))
            elif isinstance(event, PlayGoal):
                s = f"({str(event.time):>2}) Goal: "
                c = f"{event.inf}"
                if event.assist:
                    c += f", assist by {event.assist.player}"
                s += prints.mid(c, WIDTH-len(s))
            elif isinstance(event, Penalty):
                s = f"({str(event.time):>2}) "
                if event.goal:
                    s += "Penalty: "
                    c = f"Scored by {event.player}"
                else:
                    s += "Pen. Miss: "
                    s += "Miss: "
                if event.fouled:
                    c += f", accuired by {event.assist.player}"
                s += prints.mid(c, WIDTH-len(s))
            elif isinstance(event, YellowCard):
                s = f"({str(event.time):>2}) Yellow card: "
                s += prints.mid(f"for {event.reason}", WIDTH-len(s))
            elif isinstance(event, RedCard):
                s = f"({str(event.time):>2}) Red card: "
                s += prints.mid(f"for {event.reason}", WIDTH-len(s))
            elif isinstance(event, ConcededGoal):
                s = f"({str(event.goal.time):>2}) Conceded: "
                s += prints.mid(f"{event.goal.inf} by {event.goal.player}", WIDTH-len(s))
            else:
                data = event.to_dict()
                print(data)
                continue
            try:
                s += f" | {event.game}"
            except AttributeError:
                s += f" | {event.goal.game}"
            print(s)

    def get_analysis(self):
        return {
            "url": self.url,
            "name": self.name,
            "number": self.number,
            "role": self.role,
            "position": self.position,
        }

    def get_age(self):
        if not self.birthday:
            return None
        today = settings.DATE
        return today.year - self.birthday.year - ((today.month,
                                                   today.day) < (self.birthday.month,
                                                                 self.birthday.day))

    def print_row(self) -> str:
        s = ""
        if self.role:
            s += f"{self.role.title():>10}, "
        else:
            s += "          "
        split = self.name.split(" ")
        if len(self.name.split(" ")) >= 3 and len(self.name) > 25:
            if len(" ".join(split[1:-1])) < len(" ... "):
                name = f"{split[0][0]}. {split[-1]}"
            else:
                name = f"{split[0]} ... {split[-1]}"
        else:
            name = self.name
        s += f"{name:>25}"
        age = self.get_age()
        if age:
            s += f" ({age})"
        else:
            s += "     "
        if self.number:
            s += f", {self.number:>2} - "
        else:
            s += "     - "
        s += f" {self.get_points():>5}"
        s += f" {len(self.matches['started']):>2}, {len(self.matches['sub in']):>2},"
        s += f" {len(self.matches['sub out']):>2}, {len(self.matches['benched']):>2} "
        s += f" - {self.num_goals():>2}, {self.num_assists():>2}"
        res = self.get_num_games_result()
        if res:
            win, draw, loss = res
            sum = win + draw + loss
            win_percent = round((win / sum) * 100, 2)
            draw_percent = round((draw / sum) * 100, 2)
            loss_percent = round((loss / sum) * 100, 2)
            s += f" ({win:>2}, {draw:>2}, {loss:>2} |"
            s += f" {win_percent:>5}%, {draw_percent:>5}%, {loss_percent:>5}%)"
        return s

    def get_influence(self):
        output = []
        result = self.results_while_playing()
        self.influence.clear()
        for res in result:
            if res:
                game, results, sub_time = res
                pre, post, end = results
                home_pre, away_pre = pre
                home_post, away_post = post
                goals_for = 0
                goals_against = 0
                loc = "Home"

                if game.teams["home"]["team"] == self.team:
                    goals_for = home_post - home_pre
                    goals_against = away_post - away_pre
                elif game.teams["away"]["team"] == self.team:
                    goals_for = away_post - away_pre
                    goals_against = home_post - home_pre
                    loc = "Away"

                if "goals_for" not in self.influence:
                    self.influence["goals_for"] = goals_for
                    self.influence["goals_against"] = goals_against
                    self.influence["num_games"] = 1
                    self.influence["num_minutes"] = sub_time[1] - sub_time[0]
                else:
                    self.influence["goals_for"] += goals_for
                    self.influence["goals_against"] += goals_against
                    self.influence["num_games"] += 1
                    self.influence["num_minutes"] += (sub_time[1] - sub_time[0])
                output.append(
                    [game, loc, sub_time, pre, post, end, goals_for, goals_against]
                )
        return output

    def get_playtime_game(self, game):
        {"started": [], "sub in": {}, "sub out": {}, "benched": []}

        for game in self.matches["started"]:
            in_time = 0
            out_time = 90
            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            return out_time-in_time

        for game in self.matches["sub in"]:
            in_time = self.matches["sub in"][game].time
            out_time = 90
            if game in self.matches["sub out"]:
                out_time = self.matches["sub out"][game].time
            return out_time-in_time
        return 0

    def get_performance(self, category):
        if "goals_for" not in self.influence:
            if not self.get_influence():
                return
        p_tot = self.influence["goals_for"] - self.influence["goals_against"]
        ppg = (
            0
            if self.influence["num_games"] == 0
            else round(p_tot / self.influence["num_games"], 2)
        )
        if self.influence["num_games"]:
            mpg = round(self.influence["num_minutes"] / self.influence["num_games"], 0)
        else:
            mpg = 0
        ppm = 0
        if self.influence["num_minutes"]:
            ppm = round(p_tot / self.influence["num_minutes"], 5)
        li = [p_tot, ppg, mpg, ppm]
        if category == "p_tot":
            return [p_tot, li, self, self.team]
        if category == "ppg":
            return [ppg, li, self, self.team]
        if category == "mpg":
            return [mpg, li, self, self.team]
        if category == "ppm":
            return [ppm, li, self, self.team]

    def print_influence(self, individual):
        influence = self.get_influence()
        if "goals_for" not in self.influence:
            if not self.get_influence():
                print("No registered data for", self)
                return
        p_tot = self.influence["goals_for"] - self.influence["goals_against"]
        ppg = (
            0
            if self.influence["num_games"] == 0
            else round(p_tot / self.influence["num_games"], 2)
        )
        mpg = round(self.influence["num_minutes"] / self.influence["num_games"], 0)
        s = f"{self}, personal total: {p_tot}"
        s += f" | avg. {prints.get_fore_color_int(ppg)} per game"
        s += f" | avg. {mpg} minutes per game"
        try:
            ppm = round(p_tot / self.influence["num_minutes"], 5)
            s += f" | avg. {prints.get_fore_color_int(ppm)} points per minute"
        except ZeroDivisionError:
            s += "_"
        print(s)
        if individual:
            for inf in influence:
                self._print_influence(inf)

    def _print_influence(self, influence):
        game, loc, sub_time, pre, post, end, goals_for, goals_against = influence
        in_t, out_t = sub_time
        home_pre, away_pre = pre
        home_post, away_post = post
        total_goals = goals_for - goals_against
        actual_res = prints.get_yellow_fore("(draw)")
        if end[0] > end[1]:
            if game.teams["home"]["team"] == self:
                actual_res = prints.get_green_fore("(win) ")
            else:
                actual_res = prints.get_red_fore("(loss)")
        if end[0] < end[1]:
            if game.teams["home"]["team"] == self:
                actual_res = prints.get_red_fore("(loss)")
            else:
                actual_res = prints.get_green_fore("(win) ")

        personal_res = prints.get_yellow_fore("(draw)")
        if goals_for > goals_against:
            personal_res = prints.get_green_fore("(win) ")
        elif goals_for < goals_against:
            personal_res = prints.get_red_fore("(loss)")

        in_t = "'" + str(in_t)
        out_t = "'" + str(out_t)
        print(
            f" {in_t:>3}-{out_t:>3} | {home_pre:>2} - {away_pre:<2} ->",
            f"{home_post:>2} - {away_post:<2} {personal_res:<4} | {loc}",
            f"| Result {end[0]:>2} - {end[1]:<2} {actual_res:<4} | for:",
            f"{goals_for:>2}, agst: {goals_against:>2}, tot: {total_goals:>3}",
            f"| {game.date}, {game.opponent(self.team).nickname}",
        )

    def _to_json(self):
        m = {
            "meta": {
                "version": 1,
                "date": str(settings.DATE)
            },
            "data": {
                "name": self.name,
                "number": self.number,
                "birthday": str(self.birthday.strftime('%d/%m/%Y')),  # strftime might be unneeded
                "height": str(self.height),
                "foot": self.foot,
                "role": self.role,
                "position": self.position,
                "nationality": self.nationality,
            }
        }
        return m

    def _load(self):
        data = ft.get_json(ft.TF_url_to_id(self.url), "Players")
        settings.NUMBER_OF_PLAYERS += 1
        if not settings.NUMBER_OF_PLAYERS % 7:
            prints.info(f"Reading players from json: {settings.NUMBER_OF_PLAYERS}")
        if data:
            self.name = data["data"]["name"]
            self.number = data["data"]["number"]
            if data["data"]["birthday"] != "None":
                self.birthday = datetime.strptime(data["data"]["birthday"], "%d/%m/%Y")
            else:
                self.birthday = None
            self.height = data["data"]["height"]
            self.role = data["data"]["role"]
            self.position = data["data"]["position"]
            self.foot = data["data"]["foot"]
            self.nationality = data["data"]["nationality"]
            if self.role in self.team.player_by_role:
                self.team.player_by_role[self.role].append(self)
            else:
                self.team.player_by_role[self.role] = [self]
            return True
        self.page = Page(self.url, search=False)
        if not self.page.html.text:
            self.page.html.force_fetch_html()
        document = BeautifulSoup(self.page.html.text, "html.parser")
        data = document.find("h1", class_="data-header__headline-wrapper")
        try:
            self.number = int(data.get_text().strip().split()[0].strip("#"))
            self.name = " ".join(data.get_text().strip().split()[1:])
        except ValueError:
            self.number = None
            self.name = " ".join(data.get_text().strip().split())

        table = document.find(class_="info-table info-table--right-space")
        if not table:
            table = document.find(class_="info-table info-table--right-space min-height-audio")
        if not table:
            print(f"Could not find stats for {self.name}")
        self.birthday = rt.tm_player_birth(str(table))
        if self.birthday:
            self.birthday = datetime.strptime(self.birthday, '%b %d, %Y')
        self.height = rt.tm_player_height(str(table))
        if self.height:
            self.height = float(self.height.replace(",", "."))
        self.nationality = rt.tm_player_nationality(str(table))
        self.foot = rt.tm_player_foot(str(table))
        res = rt.tm_player_position(str(table)).strip()
        if res:
            if res == "Goalkeeper":
                self.position = "Goalkeeper"
                self.role = "Goalkeeper"
            else:
                res = res.split(" - ")
                if len(res) == 2:
                    self.role, self.position = res
                else:
                    prints.warning("Player.py 406", f"{res} for {self.url}")
                    self.role = res[0]
                    self.position = None
        if self.role in self.team.player_by_role:
            self.team.player_by_role[self.role].append(self)
        else:
            self.team.player_by_role[self.role] = [self]
        ft.write_json(self._to_json(), ft.TF_url_to_id(self.url), "Players")
        return False

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "number": self.number,
            "age": self.get_age(),
            "height": self.height,
            "foot": self.foot,
            "role": self.role,
            "position": self.position,
            "nationality": self.nationality
            }

    def __lt__(self, obj):
        return (self.name) < (obj.name)

    def __repr__(self) -> str:
        if not self.name:
            return "None"
        if len(self.name) > 30:
            split = self.name.split(" ")
            return f"{split[0]} ... {split[-1]}"
        return self.name

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.url == other.url
        if isinstance(other, str):
            return self.name == other
