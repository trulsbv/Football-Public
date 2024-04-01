from datetime import datetime


def TIME():
    return datetime.now().time()


FORCE = False
DATE = datetime.today().date()
FILES_FETCHED = {}
NUMBER_OF_PLAYERS = 0
SURFACES = []
LOG_BOOL = False
GAME_LENGTH = 90
FRAME_SIZE = 5
SAVED_TOURNAMENTS = []
SURFACE_TYPES = []
CURRENT_TOURNAMENT = ""
RESET_A = False
LEAGUES = [
    "Eliteserien",
    "OBOS-ligaen",
    "PostNord-ligaen Avd. 1",
    "PostNord-ligaen Avd. 2",
    "Premier League"
]
COUNTRIES = [
    "England",
    "Norway"
]
