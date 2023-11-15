
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
        "Eliteserien",
        #"Post Nord-ligaen avd. 1",
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

    def league_top_performers():
        inp = ""
        page = 1
        total = ...
        while inp.upper() != "E" and inp.upper() != "Q":
            print(f"Page {page}/{total} (Previous: P | Next: N | Quit: Q)")
            
            # Her skal printingen gjøres:
            ...
            for i in range(10):
                if len(...) > page*10+i:
                    print(...[page*10+i])

            inp = input(" => ")
            if inp.upper() == "E" or inp.upper() == "Q":
                continue
            elif inp.upper() == "P":
                page -= 1
                if page < 1:
                    page = total
            elif inp.upper() == "N":
                page += 1
                if page > total:
                    page = 1
            else:
                print("Invalid input!")

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

    def menu_page(func, header):
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print(header.upper())
            print("Type club name, to see clubs: type 'clubs'")
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
    
    def team_stats():
        inp = ""
        while inp.upper() != "E" and inp.upper() != "Q":
            print("Get data for club: type club name, to see clubs: type 'clubs'")
            inp = input(" => ")

            if inp.upper() == "CLUBS":
                for club in club_list(saved):
                    print(club)
            if inp.upper() == "CLS":
                os.system('cls' if os.name == 'nt' else 'clear')
            for league in saved:
                if inp in league.team:
                    league.team[inp].print_team()
                    league.team[inp].print_team_influence()
                    prints.whiteline()
    
    inp = ""
    while inp.upper() != "Q":
        print(f"[0] Team overview")
        print(f"[1] Team stats")
        print(f"[2] Top performers for team")
        print(f"[3] Top performers league")
        print(f"[Q] Quit")
        inp = input(" => ")
        if inp.isnumeric():
            if int(inp) == 0:
                menu_page(_print_team_overview, "Team overview")
            if int(inp) == 1:
                menu_page(_print_team_influence, "Team stats")
            if int(inp) == 2:
                menu_page(_print_top_performers, "Top performers for team")
            if int(inp) == 3:
                league_top_performers()



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
        
    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        settings.current_date = datetime.strptime("11.04.2023", "%d.%m.%Y").date()
    else:
        settings.current_date = datetime.today().date()
    main()
