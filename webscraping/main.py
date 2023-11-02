
import sys
from datetime import datetime

from classes.Mainpage import Mainpage as Mainpage
import tools.file_tools as ft
import tools.prints as prints
import tools.web_tools as wt
import tools.weather_tools as wet
from classes.Page import Page
import settings

def main():
    #search = "Eliteserien"
    search = "Post Nord-ligaen avd. 1"
    #search = "Post Nord-ligaen avd. 2"
    #search = "Toppserien"
    #search = "Norsk Tipping-Ligaen avd. 2"
    main = Mainpage()
    prints.start("Mainpage")
    main.page = Page("https://www.fotball.no/turneringer/")
    prints.success()
    
    
    prints.start("Tournaments")
    main.fetch_tournament()
    prints.success()

    prints.start(search)
    league = main.get_tournament(search)
    prints.success()

    prints.start("Schedule")
    league.create_schedule()
    prints.success()

    prints.start("Read games")
    terminliste = league.schedule
    terminliste.fetch_games()
    prints.success()
    
    prints.start("Analyse games")
    for game in terminliste.games:
        game.analyse()
        prints.info(game, newline=False)
    prints.success()

    print("Antall team:", len(league.team))
    print(f"Antall sider hentet: {wt.fetches}")

    inp = ""
    while inp.upper() != "E" and inp.upper() != "Q":
        print("Get data for club: type club name, to see clubs: type 'clubs'")
        inp = input("Inp: ")

        if inp.upper() == "CLUBS":
            for team in league.team:
                print(team)
        elif inp in league.team:
            league.team[inp].print_team()
            league.team[inp].print_team_influence()
            prints.whiteline()



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
        
    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        settings.current_date = datetime.strptime("11.04.2023", "%d.%m.%Y")
    else:
        settings.current_date = datetime.today()
    main()
