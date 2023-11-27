
import sys
from datetime import datetime

from classes.Mainpage import Mainpage as Mainpage
import tools.file_tools as ft
import tools.prints as prints
import tools.web_tools as wt
import tools.weather_tools as wet
from classes.Page import Page
import settings
import os

saved = []
types_of_weather = ["Overcast", "Clear", "Partially cloudy", "Rain; Overcast",
                    "Rain; Partially cloudy", "Rain", "Snow"]
types_of_surfaces = ["Naturgress", "Kunstgress m/Sand", "Kunstgress m/gummispon", "Kunstgress u/Sand"]
def update():
    leagues = [
    "Eliteserien - Norges Fotballforbund",
    "OBOS-ligaen - Norges Fotballforbund",
    "Post Nord-ligaen avd. 1",
    "Post Nord-ligaen avd. 2",
    #"Norsk Tipping-Ligaen avd. 2",
    ]
    
    prints.START()
    prints.start("Mainpage")
    main = Mainpage()
    main.page = Page("https://www.fotball.no/turneringer/")
    prints.success()
    
    
    prints.start("Tournaments")
    main.fetch_tournament()
    prints.success()
    global saved
    saved = []

    for leg in leagues:
        prints.start(f"Reading league: {leg}")
        tournament = main.get_tournament(leg)
        tournament.name = leg
        prints.success()

        prints.start("Schedule")
        tournament.create_schedule()
        prints.success()

        prints.start("Read games")
        pn1_schedule = tournament.schedule
        pn1_schedule.fetch_games()
        prints.success()

        prints.start("Analyse games")
        for game in pn1_schedule.games:
            game.analyse()
            prints.info(game, newline=False)
        saved.append(tournament)
        prints.success()
    prints.FINISH()

    num_teams = 0
    for league in saved:
        num_teams += len(league.team)

    print(f"Number of teams: {num_teams}")
    print(f"Pages fetched: {wt.fetches}")

def main(): 
    update()

    def print_weather_types():
        for tournament in saved:
            tournament.print_weather_types()

        if not settings.display_weather:
            print("ENABLED:")
            for w in types_of_weather:
                print(f" * {w}")
            return
        not_enabled = []
        for item in types_of_weather:
            if item not in settings.display_weather:
                not_enabled.append(item)
        enabled = list(set(settings.display_weather).intersection(types_of_weather))
        print("NOT ENABLED:")
        for w in not_enabled:
            print(f" * {w}")

        print("ENABLED:")
        for w in enabled:
            print(f" * {w}")

    def print_surface_types():
        for tournament in saved:
            tournament.print_surface_types()

        if not settings.display_surface:
            print("ENABLED:")
            for w in types_of_surfaces:
                print(f" * {w}")
            return
        not_enabled = []
        for item in types_of_surfaces:
            if item not in settings.display_surface:
                not_enabled.append(item)
        enabled = list(set(settings.display_surface).intersection(types_of_surfaces))
        print("NOT ENABLED:")
        for w in not_enabled:
            print(f" * {w}")

        print("ENABLED:")
        for w in enabled:
            print(f" * {w}")

    def select_tournament(team=None):
        if len(saved) == 1:
            return saved[0]
        if not team:
            i = None
            while not str(inp).isnumeric() or int(inp) > i:
                prints.info("Choose a league:", newline=True)
                for league in saved:
                    print(f"[{i}] {league}")
                    i+=1
                inp = i+1
                inp = input(" => ")
            return saved[int(inp)]

        for league in saved:
            if team in league.team:
                return league
            

    def league_top_performers():
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print("Type club name to hightlight (case sensitive), to see clubs: type 'clubs'")
            inp = input(" => ")
            if inp.upper() == "CLS":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            if inp.upper() == "CLUBS":
                for club in club_list(saved):
                    print(club)
                continue
            if inp == "":
                select_tournament().print_top_performers()
            for league in saved:
                if inp in league.team:
                    select_tournament(inp).print_top_performers(inp)

    def club_list(list_of_leagues):
        clubs = []
        for league in list_of_leagues:
            for team in league.team:
                clubs.append(team)
        clubs.sort()
        return clubs
        
    def _print_top_performers(team):
        team.print_top_performers()
        print()

    def _print_team_overview(team):
        team.print_team()
    
    def _print_team_influence(team):
        team.print_team_influence()

    def _print_team_games(team):
        for game in team.get_all_games():
            print(game)

    def edit_surface():
        inp = ""
        changed = False
        while inp.upper() != "E" and inp.upper() != "Q":
            print_surface_types()
            inp = input(" => ")
            for word in inp.split(", "):
                if word in types_of_surfaces:     
                    if word in settings.display_surface:
                        settings.display_surface.remove(word)
                    else:
                        settings.display_surface.append(word)
                changed = True
            if inp.upper() == "ALL":
                settings.display_surface = []
                changed = True
        if changed:
            print()
            update()

    def edit_weather():
        inp = ""
        changed = False
        while inp.upper() != "E" and inp.upper() != "Q":
            print_weather_types()
            inp = input(" => ")
            for word in inp.split(", "):
                if word in types_of_weather:     
                    if word in settings.display_weather:
                        settings.display_weather.remove(word)
                    else:
                        settings.display_weather.append(word)
                changed = True
            if inp.upper() == "ALL":
                settings.display_weather = []
                changed = True
        if changed:
            print()
            update()

    def edit_date():
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print("\nSet date DD.MM.YYYY")
            inp = input(" => ")
            
            try:
                settings.current_date = datetime.strptime(inp, "%d.%m.%Y").date()
                print()
                update()
            except:
                print("Invalid input.")

    def menu_page(func, header):
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print()
            print(header.upper())
            print("Type club name (case sensitive), to see clubs: type 'clubs'")
            inp = input(" => ")
            if inp.upper() == "CLS":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            if inp.upper() == "CLUBS":
                for club in club_list(saved):
                    print(club)
                continue
            for league in saved:
                if inp in league.team:
                    func(league.team[inp])
    def league_table():
        for league in saved:
            print(f"\nLEAGUE: {league}")
            league.print_league_table()

    def display_info():
        s = "\nINFO"
        year, month, day = str(settings.current_date).split("-")
        date = f"Date: {day}.{month}.{year}"
        weather = f"Weather: {'All' if not settings.display_weather else ', '.join(map(str, settings.display_weather))}"
        surfaces = f"Surfaces: {'All' if not settings.display_surface else ', '.join(map(str, settings.display_surface))}"

        lines = [date, weather, surfaces]
        for line in lines:
            s += "\n"
            s += line
        print(s)

    def setting():
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print("\nSETTINGS:")
            print("[D] Edit date")
            print("[S] Edit surface")
            print("[W] Edit weather")
            print("\n[Q] Quit")
            inp = input(" => ")
            if inp.upper() == "D":
                edit_date()
            if inp.upper() == "S":
                edit_surface()
            if inp.upper() == "W":
                edit_weather()

    inp = ""
    while inp.upper() != "Q":
        display_info()
        print(f"[1] Team overview")
        print(f"[2] Team stats")
        print(f"[3] Top performers for team")
        print(f"[4] List team games")
        print(f"[5] Top performers league")
        print(f"[6] League tables")
        print()
        print(f"[Q] Quit, [CLS] Clear, [S] Settings")
        inp = input(" => ")
        if inp.isnumeric():
            if int(inp) == 1:
                menu_page(_print_team_overview, "Team overview")
            if int(inp) == 2:
                menu_page(_print_team_influence, "Team stats")
            if int(inp) == 3:
                menu_page(_print_top_performers, "Top performers for team")
            if int(inp) == 4:
                menu_page(_print_team_games, "See team games")
            if int(inp) == 5:
                league_top_performers()
            if int(inp) == 6:
                league_table()
            continue
        if inp.upper() == "S":
            setting()
        if inp.upper() == "CLS":
            os.system('cls' if os.name == 'nt' else 'clear')



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
        
    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        settings.current_date = datetime.strptime("20.04.2023", "%d.%m.%Y").date()
    else:
        settings.current_date = datetime.today().date()
    settings.display_weather = []
    settings.display_surface = []
    # PROBLEM: Dersom man ikke leser en kamp, er den en bitch 
    main()
