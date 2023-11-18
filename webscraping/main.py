
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

def main():
    #search = "Eliteserien"
    leagues = [
        "Eliteserien - Norges Fotballforbund",
        "Post Nord-ligaen avd. 1",
        #"Post Nord-ligaen avd. 2",
        #"Norsk Tipping-Ligaen avd. 2",
        ]
    #search = "Toppserien"
    #search = "Norsk Tipping-Ligaen avd. 2"
    prints.START()
    prints.start("Mainpage")
    main = Mainpage()
    main.page = Page("https://www.fotball.no/turneringer/")
    prints.success()
    
    
    prints.start("Tournaments")
    main.fetch_tournament()
    prints.success()

    saved = []

    for leg in leagues:
        prints.start(f"Reading league: {leg}")
        tournament = main.get_tournament(leg)
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

    def select_tournament(team=None):
        if len(saved) == 1:
            return saved[0]
        if not team:
            i = 0
            prints.info("Choose a league:", newline=True)
            for league in saved:
                print(f"[{i}] {league}")
                i+=1
            inp = i+1
            while not str(inp).isnumeric() or int(inp) > i:
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
        for game in team.games:
            print(game)

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

    inp = ""
    while inp.upper() != "Q":
        print()
        print(f"[1] Team overview")
        print(f"[2] Team stats")
        print(f"[3] Top performers for team")
        print(f"[4] List team games")
        print(f"[5] Top performers league")
        print(f"[-] League tables")
        print()
        print(f"[Q] Quit, [CLS] Clear")
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
            continue
        if inp.upper() == "CLS":
            os.system('cls' if os.name == 'nt' else 'clear')



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
        
    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        settings.current_date = datetime.strptime("11.04.2023", "%d.%m.%Y").date()
    else:
        settings.current_date = datetime.today().date()
    main()
