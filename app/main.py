import sys
from datetime import datetime
from classes.Country import Country
from classes.Continent import Continent
import tools.prints as prints
import tools.file_tools as ft
import settings
from menus.presets import preset_menu
from menus.menu import menu


def main() -> None:
    preset_menu()
    exit()
    args = ", ".join(sys.argv[1:])
    if len(sys.argv) > 1 and "-help" in args:
        pos_args = [
            "Run cur season: -run [league] [country]",
            "Run historical: -[year] [league] [country]",
            "   Delete file: -deleteU [year] [url]",
            "   Reset saved: -reset[P/G] [league] [country]",
            ]
        print("Current valid arguments:")
        for arg in pos_args:
            print(f" * {arg}")
        exit()
    if sys.argv[1] == "-run":
        settings.LEAGUES = [sys.argv[2]]
        settings.COUNTRIES = [sys.argv[3]]
    if len(sys.argv[1]) == 5 and sys.argv[1].strip("-").isnumeric():
        settings.DATE = datetime.strptime(f"31.12.{sys.argv[1].strip('-')}", "%d.%m.%Y").date()
        settings.LEAGUES = [sys.argv[2]]
        settings.COUNTRIES = [sys.argv[3]]
    if sys.argv[1] == "-deleteU":
        settings.DATE = datetime.strptime(f"31.12.{sys.argv[2].strip('-')}", "%d.%m.%Y").date()
        print(f"Url {sys.argv[3]} deleted: {ft.delete_html(url=sys.argv[3])}")
        exit()
    if len(sys.argv) > 1 and "-resetP" in args:
        settings.RESET_P = True
    if len(sys.argv) > 1 and "-resetG" in args:
        settings.RESET_G = True
    if len(sys.argv) > 1 and "-mute" in args:
        settings.NO_PRINT = True

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
                if settings.RESET_P or settings.RESET_G:
                    prints.start(f"Deleting data from: {leg}")
                else:
                    prints.start(f"Reading league: {leg}")
                tournament = main.get_tournament(leg)
                if not tournament:
                    continue
                name = tournament.page.html.title.strip(" | Transfermarkt").replace("/", "_")
                settings.CURRENT_TOURNAMENT = name
                if settings.RESET_P:
                    ft.delete_analysis(selection="Players")
                if settings.RESET_G:
                    ft.delete_analysis(selection="Games")
                if settings.RESET_P or settings.RESET_G:
                    prints.success()
                    prints.FINISH()
                    exit()
                tournament.name = name
                prints.success()

                prints.start("Schedule")
                tournament.create_schedule()
                prints.success()

                prints.start("Read games")
                pn1_schedule = tournament.schedule
                pn1_schedule.fetch_games()
                ft.push_json()  # TODO: This might not be neeeded
                settings.SAVED_TOURNAMENTS.append(tournament)
                prints.success()
    if not settings.CURRENT_TOURNAMENT:
        prints.failed("No tournament found")
        exit()
    prints.FINISH()


if __name__ == "__main__":
    # PROBLEM: Dersom man ikke leser en kamp, er den en bitch
    main()
