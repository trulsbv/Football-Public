import math
import tools.prints as prints
import settings
import os
from classes.Tournament import Tournament
from classes.Team import Team
from datetime import datetime


def menu(update_function) -> None:
    inp = ""
    while inp.upper() != "QUIT":
        display_info()
        print("[1] Team overview")
        print("[2] Team stats")
        print("[3] Top performers for team")
        print("[4] List team games")
        print("[5] Top performers league")
        print("[6] League tables")
        print("[7] Player stats")
        print("[8] Team stats")
        print()
        print("[QUIT] Quit, [CLS] Clear, [S] Settings, [T] System stats")
        inp = input(" => ")
        if inp.isnumeric():
            if int(inp) == 1:
                _print_team_overview()
            if int(inp) == 2:
                _print_team_influence()
            if int(inp) == 3:
                _print_top_performers()
            if int(inp) == 4:
                _print_team_games()
            if int(inp) == 5:
                league_top_performers()
            if int(inp) == 6:
                league_table()
            if int(inp) == 7:
                choose_player_stats()
            if int(inp) == 8:
                print_team_stats()
            continue
        if inp.upper() == "T":
            print_system_stats()
        if inp.upper() == "S":
            if setting():
                update_function()
        if inp.upper() == "CLS":
            os.system("cls" if os.name == "nt" else "clear")


def _list_items(items: list, per_page: int = 10, page=0, accept_none=False) -> any:
    """
    Takes a list and items per page. Lets the user
    Choose one of the items in the list

    Arguments:
        * List of items
        * Number of items to show per page

    Returns:
        * String name of item
    """
    max_pages = math.floor(len(items) / per_page)
    if len(items) - (max_pages * per_page) > 0:
        max_pages = max_pages + 1

    ctr = per_page * page
    i = 0
    inp = ""
    print(f"\nPage {page+1}/{max_pages}")
    while ctr < len(items) and i < per_page:
        print(f"[{i}] {items[ctr]}")
        ctr += 1
        i += 1
    print(f"[0 - {per_page-1}] Select, " + "[Q] Quit, [P] Previous page, [N] Next page")
    inp = input(" => ")
    if accept_none and inp == "":
        return None

    if inp.isnumeric():
        inp = int(inp)
        if not (inp < 0 or inp >= i):
            return items[page * per_page + inp]
    else:
        inp = inp.upper()
        if inp == "Q":
            return None
        if inp == "N":
            if ctr >= len(items):
                return _list_items(items, per_page, 0)
            return _list_items(items, per_page, page + 1)
        if inp == "P":
            if page == 0:
                return _list_items(items, per_page, max_pages - 1)
            return _list_items(items, per_page, page - 1)

    prints.error("Select item", "Invalid input")
    return _list_items(items, per_page, page)


def print_system_stats() -> None:
    print("\n=== System statisics ===")
    print(f"Files accessed: ({prints.get_blue_back(len(settings.FILES_FETCHED))})")
    for file in settings.FILES_FETCHED:
        print(f" * {file} accessed {prints.get_blue_back(settings.FILES_FETCHED[file])} time(s)")
    print(f"Total: {prints.get_blue_back(sum(settings.FILES_FETCHED.values()))} times")


def select_team(tournament: Tournament = None, accept_none: bool = False) -> Team:
    if not tournament:
        tournament = select_tournament()
    team = _list_items(list(tournament.team), 10, accept_none=accept_none)
    if team:
        return tournament.team[team]
    return None


def print_players_events() -> None:
    team = select_team()
    for player in team.players:
        print(f"\n === {player} ===")
        for event in player.events:
            print(" * ", event.info())


def print_surface_types() -> None:
    """
    Displays all types of pitch surfaces to the user
    """
    for tournament in settings.SAVED_TOURNAMENTS:
        tournament.print_surface_types()

    if not settings.SURFACES:
        print("ENABLED:")
        for w in settings.SURFACE_TYPES:
            print(f" * {w}")
        return
    not_enabled = []
    for item in settings.SURFACE_TYPES:
        if item not in settings.SURFACES:
            not_enabled.append(item)
    enabled = list(set(settings.SURFACES).intersection(settings.SURFACE_TYPES))
    print("NOT ENABLED:")
    for w in not_enabled:
        print(f" * {w}")

    print("ENABLED:")
    for w in enabled:
        print(f" * {w}")


def select_tournament(team: Team = None) -> Tournament:
    """
    Displays loaded leagues to the user and
    asks the user to choose one.

    Returns:
        * Tournament
    """
    if len(settings.SAVED_TOURNAMENTS) == 1:
        return settings.SAVED_TOURNAMENTS[0]

    if not team:
        inp = ""
        i = 0
        while not (str(inp).isnumeric() and int(inp) < i and int(inp) >= 0):
            prints.info("Choose a league:", newline=True)
            for league in settings.SAVED_TOURNAMENTS:
                print(f"[{i}] {league}")
                i += 1
            inp = i + 1
            inp = input(" => ")
        return settings.SAVED_TOURNAMENTS[int(inp)]

    for tournament in settings.SAVED_TOURNAMENTS:
        if team in tournament.team:
            return tournament


def league_top_performers() -> None:
    """
    Prints a list of players from a user-chosen tournament
    """
    tournament = select_tournament()
    team = select_team(tournament=tournament, accept_none=True)
    tournament.print_top_performers(team)


def club_list(list_of_leagues: list[Tournament]) -> list[Team]:
    """
    Gets all the teams from the list of tournaments and returns
    a sorted list of them.

    Arguments:
        * List of tournaments

    Returns:
        * Sorted list of Teams
    """
    clubs = []
    for league in list_of_leagues:
        for team in league.team:
            clubs.append(team)
    clubs.sort()
    return clubs


def _print_top_performers() -> None:
    """
    Prints players performances for a team

    Arguments:
        * Team
    """
    team = select_team()
    team.print_top_performers()
    print()


def _print_team_overview() -> None:
    """
    Prints all players, their position, started, benched, and sub in/out games
    as well as % of win/draw/loss in games they were on the pitch
    """
    team = select_team()
    team.print_team()


def _print_team_influence() -> None:
    """
    Prints all players and show the minutes they played in each game
    showing if the team won or lost when they played and in total
    """
    team = select_team()
    team.print_team_influence()


def _print_team_games() -> None:
    """
    Prints all the games a team has played

    Arguments:
        * Team
    """
    team = select_team()
    for game in team.get_all_games():
        print(game)


def edit_surface() -> bool:
    """
    Displays the different surfaces to the user
    and lets the user choose what surfaces to view. Returns
    a boolean where True will trigger update()

    Returns:
        * bool
    """
    inp = ""
    changed = False
    while inp.upper() != "E" and inp.upper() != "Q":
        print_surface_types()
        inp = input(" => ")
        for word in inp.split(", "):
            if word in settings.SURFACE_TYPES:
                if word in settings.SURFACES:
                    settings.SURFACES.remove(word)
                else:
                    settings.SURFACES.append(word)
            changed = True
        if inp.upper() == "ALL":
            settings.SURFACES = []
            changed = True
    return changed


def edit_date() -> bool:
    """
    Lets the user change the internal DATE to select what matches
    to be played. Returns a boolean where True will trigger update()

    Returns:
        * bool
    """
    inp = ""
    while inp.upper() != "E" and inp.upper() != "Q":
        print("\nSet date DD.MM.YYYY")
        inp = input(" => ")
        bool = False
        try:
            settings.DATE = datetime.strptime(inp, "%d.%m.%Y").date()
            bool = True
        finally:
            if not bool:
                print("Invalid input.")
            return bool


def choose_player_stats() -> None:
    """
    Ask user to choose league, then prints players in the league
    and asks user to choose one. Then displays stats about that player.
    """
    tournament = select_tournament()
    team_name = _list_items(list(tournament.team), 10)
    if not team_name:
        return
    team = tournament.team[team_name]
    player = _list_items(list(team.players), 10)
    player.print_stats()


def menu_page(func: callable, header: str) -> None:
    """
    A generic menu-page for user interaction. Takes a callable-function
    and a header to display to the user. The function must
    take 1 argument of type Team

    Arguments:
        * callable function
        * string header
    """
    inp = ""
    while inp.upper() != "E" and inp.upper() != "Q":
        print()
        print(header.upper())
        print("Type club name (case sensitive), to see clubs: type 'clubs'")
        inp = input(" => ")
        if inp.upper() == "CLS":
            os.system("cls" if os.name == "nt" else "clear")
            continue
        if inp.upper() == "CLUBS":
            for club in club_list(settings.SAVED_TOURNAMENTS):
                print(club)
            continue
        for league in settings.SAVED_TOURNAMENTS:
            if inp in league.team:
                func(league.team[inp])


def league_table() -> None:
    """
    Prints all the loaded leagues and their league table
    """
    for league in settings.SAVED_TOURNAMENTS:
        print(f"\nLEAGUE: {league}")
        league.print_league_table()


def print_team_stats() -> None:
    """
    Prints team stats
    """
    tournament = select_tournament()
    team = _list_items(list(tournament.team), 10)
    if team:
        team = tournament.team[team]
        team.print_team_stats()


def display_info() -> None:
    """
    Prints info about the current settings
    """
    s = "\nINFO"
    s += "\nLeagues:"
    for league in settings.SAVED_TOURNAMENTS:
        s += f"\n * {str(league).strip(' | Transfermarkt')}"
    year, month, day = str(settings.DATE).split("-")
    date = f"Date: {day}.{month}.{year}"
    surfaces = "Surfaces: "
    surfaces += "All" if not settings.SURFACES else ", ".join(map(str, settings.SURFACES))

    lines = [date, surfaces]
    for line in lines:
        s += "\n"
        s += str(line)
    print(s)


def setting() -> None:
    """
    A menu where the user can edit the current settings.
    Reloads the page if sub-pages has been edited
    """
    inp = ""
    while inp.upper() != "E" and inp.upper() != "Q":
        print("\nSETTINGS:")
        print("[D] Edit date")
        print("[S] Edit surface")
        print("\n[Q] Quit")
        inp = input(" => ")
        if inp.upper() == "D":
            edited = edit_date()
        if inp.upper() == "S":
            edited = edit_surface()
    if edited:
        return True
