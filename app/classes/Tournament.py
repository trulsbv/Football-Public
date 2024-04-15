from classes.Schedule import Schedule
from classes.Team import Team
from classes.Page import Page
import tools.regex_tools as rt
import tools.prints as prints


class Tournament:
    def __init__(self, parent, url):
        self.mainpage = parent
        self.schedule = None
        self.team = {}
        self.analyser = None
        self.page = Page(url)
        self.weather = set()
        self.pitches = {"surfaces": set()}
        self.name = None

    def _get_league_table(self):
        out = []
        for team in self.team:
            out.append(self.team[team])
        out = sorted(out, key=lambda x: x.goals_scored_home, reverse=True)
        out = sorted(out, key=lambda x: x.goals_scored_total, reverse=True)
        out = sorted(out, key=lambda x: x.goal_diff, reverse=True)
        out = sorted(out, key=lambda x: x.points, reverse=True)

        return out

    def current_position(self, team):
        i = 1
        for t in self._get_league_table():
            if team == t:
                return i
            i += 1
        prints.error("current_position", "team not in league")
        exit()

    def print_league_table_by_points(self):
        self.print_league_table(self._get_league_table())

    def print_league_table_by_score(self):
        ut = sorted(self._get_league_table(), key=lambda x: x.average_player_points(), reverse=True)
        self.print_league_table(ut)

    def print_league_table(self, table):
        i = 1
        print(f"POS | {'TEAM':>15} | GP ( H/A ) | GS ( H/A ) | GC ( H/A ) | +/- | P | Rating")
        print("-" * 81)
        for team in table:
            s = f"{i:>3} | {team.nickname:>15} | "
            s += f"{str(len(team.games['home']) + len(team.games['away'])):>2} "
            s += f"({str(len(team.games['home'])):>2}/{str(len(team.games['away'])):>2}) | "
            s += f"{str(team.goals_scored_total):>2} ({str(team.goals_scored_home):>2}/"
            s += f"{str(team.goals_scored_away):>2}) | "
            s += f"{str(team.goals_conceded_total):>2} ({str(team.goals_conceded_home):>2}"
            s += f"/{str(team.goals_conceded_away):>2}) | "
            s += f"{str(team.goal_diff):>3} | "
            s += f"{team.points}"
            s += f" | {team.average_player_points()}"
            print(s)
            i += 1

    def print_surface_types(self):
        s = "["
        for p in self.pitches["surfaces"]:
            if len(s) != 1:
                s += ", "
            s += f'"{p}"'
        s += "]"
        # print("\nTypes of surface:")
        # print(s)

    def print_weather_types(self):
        # Do the same with ranges of temperatures aswell
        s = "["
        for w in self.weather:
            if len(s) != 1:
                s += ", "
            s += f'"{w}"'
        s += "]"
        # print("\nTypes of weather:")
        # print(s)

    def get_weather_results(self, weather):
        for game in self.schedule.games():
            if weather == game.weather.conditions:
                print(game)
        ...

    def _get_schedule_url(self):
        urls = rt.find_urls(self.page.html.text)
        for url in urls:
            if "gesamtspielplan" in url:
                return url  # TODO: Not very safe? But works for now

    def get_team(self, name, url):
        if name in self.team:
            return self.team[name]
        return self.create_team(name, url)

    def create_team(self, name, url):
        if name not in self.team:
            self.team[name] = Team(url, self)
            self.team[name].name = name
        return self.team[name]

    def create_schedule(self):
        self.schedule = Schedule(self, self._get_schedule_url())

    def get_all_players(self):
        output = []
        for team in self.team:
            output.extend(self.team[team].players)
        return output

    def print_top_performers(self, hightlight: Team = None):
        tournament_players = sorted(self.get_all_players(),
                                    key=lambda x: x.get_points(),
                                    reverse=True)
        tournament_players = sorted(tournament_players,
                                    key=lambda x: x.role,
                                    reverse=True)
        defenders = list(filter(lambda player: player.role == "Defender", tournament_players))
        attackers = list(filter(lambda player: player.role == "Attack", tournament_players))
        midfielders = list(filter(lambda player: player.role == "midfield", tournament_players))
        goalkeepers = list(filter(lambda player: player.role == "Goalkeeper", tournament_players))
        for group in [attackers, midfielders, defenders, goalkeepers]:
            for player in group:
                possible_minutes = (len(player.team.games["home"]) +
                                    len(player.team.games["away"]))*90
                if player.minutes_played() == 0:
                    continue
                percentage_played = player.minutes_played()/possible_minutes
                s = f"{prints.mid(player.team.nickname, 12)}"
                s += f" | {prints.mid(player.role, 10)}"
                s += f" | {prints.mid(player.name, 31)}"
                s += f" | {prints.mid(player.get_points(), 7)}"
                s += f" | {round(player.points, 4):<8}/ {player.minutes_played():<4}"
                s += f" ({round((percentage_played)*100, 2)} %)"
                if hightlight and str(player.team).upper() == hightlight.nickname.upper():
                    s = prints.get_blue_back(s)
                if percentage_played > 0.80:
                    s = prints.get_green_fore(s)
                if percentage_played < 0.50 and percentage_played > 0.20:
                    s = prints.get_lightblack_fore(s)
                if percentage_played < 0.20 and percentage_played > 0.10:
                    s = prints.get_yellow_fore(s)
                if percentage_played < 0.10:
                    s = prints.get_red_fore(s)
                print(s)
            print()

    def __lt__(self, other):
        self.page.html.title < other.page.html.title

    def __repr__(self) -> str:
        return self.page.html.title
