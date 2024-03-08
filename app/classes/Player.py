from classes.Event import (
    OwnGoal,
    PenaltyGoal,
    PlayGoal,
    RedCard,
    YellowCard,
    Goal,
)
import tools.prints as prints
import tools.statistic_tools as statt
import settings


class Player:
    def __init__(self, team, name, url):
        self.team = team
        self.name = name
        self.url = url
        self.number = False
        self.position = False
        self.matches = {"started": [], "sub in": {}, "sub out": {}, "benched": []}
        self.events = []
        self.influence = {}

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
        stats = [Goal, PlayGoal, PenaltyGoal, OwnGoal, YellowCard, RedCard]
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
            result = statt.iterate_events(self.events, stat, settings.FRAME_SIZE)
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
            output[stat] = statt.iterate_events(self.events, stat, settings.FRAME_SIZE)
        return output

    def results_while_playing(self):
        results_while_playing = []  # <-- (game, (before, after, end), (in, out))
        for game in self.matches["started"]:
            cur = (0, 0)
            in_time = 0
            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.result.get_result()
                out_time = 90
            end = game.result.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))

        for game in self.matches["sub in"]:
            cur = self.matches["sub in"][game].current_score
            in_time = self.matches["sub in"][game].time

            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.result.get_result()
                out_time = 90
            end = game.result.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))
        results_while_playing.sort(
            key=lambda x: x[0].date
        )  # (x[0].date.year, x[0].date.month, x[0].date.day)
        return results_while_playing

    def get_goals(self):
        goals = statt.find_event(self.events, Goal)
        goal_counter = 0
        for g in goals:
            if isinstance(g, OwnGoal):
                goal_counter -= 1
            else:
                goal_counter += 1
        return goal_counter

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

    def get_analysis(self):
        return {
            "url": self.url,
            "name": self.name,
            "number": self.number,
            "position": self.position,
        }

    def print_row(self) -> str:
        s = ""
        if self.position:
            s += f"{self.position.upper():>8}, "
        else:
            s += "          "

        split = self.name.split(" ")
        name = (
            f"{split[0]} ... {split[-1]}"
            if len(self.name.split(" ")) > 4 and len(self.name) > 40
            else self.name
        )
        s += f"{name:>40}"
        if self.number:
            s += f", {self.number:>2} - "
        else:
            s += "       "
        s += f"({len(self.matches['started']):>2}, {len(self.matches['sub in']):>2},"
        s += f" {len(self.matches['sub out']):>2}, {len(self.matches['benched']):>2})"
        s += f" - {self.get_goals():>2} goals"
        res = self.get_num_games_result()
        if res:
            win, draw, loss = res
            sum = win + draw + loss
            win_percent = round((win / sum) * 100, 2)
            draw_percent = round((draw / sum) * 100, 2)
            loss_percent = round((loss / sum) * 100, 2)
            s += f" ({win} {win_percent}%, {draw} {draw_percent}%, {loss} {loss_percent}%)"
        return s

    def get_influence(self):
        output = []
        result = self.results_while_playing()
        for res in result:
            if res:
                game, results, sub_time = res
                pre, post, end = results
                home_pre, away_pre = pre
                home_post, away_post = post
                goals_for = 0
                goals_against = 0
                loc = "Home"

                if game.home == self.team:
                    goals_for = home_post - home_pre
                    goals_against = away_post - away_pre
                elif game.away == self.team:
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
                    self.influence["num_minutes"] += (sub_time[1]) - sub_time[0]
                output.append(
                    [game, loc, sub_time, pre, post, end, goals_for, goals_against]
                )
        return output

    def get_performance(self, category):
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
        ppm = 0
        try:
            ppm = round(p_tot / self.influence["num_minutes"], 5)
        finally:
            ...
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
            if game.home == self:
                actual_res = prints.get_green_fore("(win) ")
            else:
                actual_res = prints.get_red_fore("(loss)")
        if end[0] < end[1]:
            if game.home == self:
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
            f"| {game.date}, {game.opponent(self.team)}",
        )
