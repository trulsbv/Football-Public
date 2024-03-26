import sys
from datetime import datetime
from classes.Country import Country
from classes.Continent import Continent
import tools.prints as prints
import tools.file_tools as ft
import settings
import os
from menu import menu


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "-help":
        args = ["-test", "-testES", "-test2"]
        print("Current valid arguments:")
        for arg in args:
            print(f" * {arg}")
        exit()

    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        settings.DATE = datetime.strptime("24.12.2023", "%d.%m.%Y").date()
        settings.LEAGUES = ["OBOS-ligaen"]
        settings.COUNTRIES = ["Norway"]
    elif len(sys.argv) > 1 and sys.argv[1] == "-testES":
        settings.DATE = datetime.strptime("24.12.2023", "%d.%m.%Y").date()
        settings.LEAGUES = ["Eliteserien"]
        settings.COUNTRIES = ["Norway"]
    elif len(sys.argv) > 1 and sys.argv[1] == "-testPL":
        settings.DATE = datetime.today().date()
        settings.LEAGUES = ["Premier League"]
        settings.COUNTRIES = ["England"]
    elif len(sys.argv) > 1 and sys.argv[1] == "-test2":
        settings.DATE = datetime.strptime("24.04.2023", "%d.%m.%Y").date()
        settings.LEAGUES = [
            "Eliteserien",
        ]
        settings.COUNTRIES = ["Norway"]
    else:
        settings.DATE = datetime.today().date()
        print("Suggested minimum terminal width:")
        print("-" * 145)
        input("[Enter]")
        os.system("cls" if os.name == "nt" else "clear")
    settings.SURFACES = []

    update()
    menu(update)


def initialize_settings() -> None:
    """
    Run when starting update, to keep counts and other data clear for each restarted iteration
    """
    settings.NUMBER_OF_PLAYERS = 0


def update() -> None:
    """
    Reads data and creates all the objects. Sets settings.SAVED_TOURNAMENTS to a list of
    league-objects
    """
    initialize_settings()
    prints.START()
    prints.start("Continent")
    continent = Continent("Europe", "https://www.transfermarkt.com/wettbewerbe/europa")
    prints.success()
    settings.SAVED_TOURNAMENTS = []
    for country in continent.countries:
        if country in settings.COUNTRIES:
            prints.start(f"{country}")
            main = Country(continent.countries[country])
            prints.success()

            prints.start("Tournaments")
            main.fetch_tournament()
            prints.success()

            main.avaliable_tournaments()

            for leg in settings.LEAGUES:
                settings.CURRENT_TOURNAMENT = leg
                prints.start(f"Reading league: {leg}")
                tournament = main.get_tournament(leg)
                if not tournament:
                    prints.failed(leg)
                    continue
                tournament.name = leg
                prints.success()

                prints.start("Schedule")
                tournament.create_schedule()
                prints.success()

                prints.start("Read games")
                pn1_schedule = tournament.schedule
                pn1_schedule.fetch_games()
                prints.success()
                ft.push_json()  # TODO: This might not be neeeded
                settings.SAVED_TOURNAMENTS.append(tournament)
                prints.success()
    prints.FINISH()


if __name__ == "__main__":
    # PROBLEM: Dersom man ikke leser en kamp, er den en bitch
    main()
