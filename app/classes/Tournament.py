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

    def _get_league_table(self):
        out = []
        for team in self.team:
            out.append(self.team[team])
        out = sorted(out, key=lambda x: x.goals_scored_home, reverse=True)
        out = sorted(out, key=lambda x: x.goals_scored_total, reverse=True)
        out = sorted(out, key=lambda x: x.goal_diff, reverse=True)
        out = sorted(out, key=lambda x: x.points, reverse=True)

        return out

    def print_league_table(self):
        i = 1
        print(f"POS | {'TEAM':>20} | GP ( H/A ) | GS ( H/A ) | GC ( H/A ) | +/- | P ")
        print("-" * 76)
        for team in self._get_league_table():
            s = f"{i:>3} | {team.nickname:>15} | "
            s += f"{str(len(team.games['home']) + len(team.games['away'])):>2} "
            s += f"({str(len(team.games['home'])):>2}/{str(len(team.games['away'])):>2}) | "
            s += f"{str(team.goals_scored_total):>2} ({str(team.goals_scored_home):>2}/"
            s += f"{str(team.goals_scored_away):>2}) | "
            s += f"{str(team.goals_conceded_total):>2} ({str(team.goals_conceded_home):>2}"
            s += f"/{str(team.goals_conceded_away):>2}) | "
            s += f"{str(team.goal_diff):>3} | "
            s += f"{team.points}"
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

    def get_top_performers(self):
        output = []
        for team in self.team:
            output.extend(self.team[team].get_top_performers())
        return output

    def print_top_performers(self, hightlight=None):
        inp = sorted(self.get_top_performers(), key=lambda x: x[0], reverse=True)
        for i in inp:
            s = f"{i[2].team}{' '*(20-len(i[2].team))}"
            s += f" | {str(i[2]):>30}, personal total: {str(i[1][0]):>3}"
            s += f" | avg. {' '*(5-len(str(i[1][1])))}{prints.get_fore_color_int(i[1][1])}"
            s += f" per game ({str(len(i[2].results_while_playing())):>2})"
            s += f" | avg. {str(int(i[1][2])):>2} minutes per game"
            s += f" | avg. {'' if i[1][3]<0 else ' '}{prints.get_fore_color_int(i[1][3])}"
            s += f"{' '*(8-len(str(i[1][3])))} points per minute"
            if hightlight and str(i[2].team).upper() == hightlight.upper():
                print(prints.get_blue_back(s))
            else:
                print(s)

    def __lt__(self, other):
        self.page.html.title < other.page.html.title

    def __repr__(self) -> str:
        return self.page.html.title
