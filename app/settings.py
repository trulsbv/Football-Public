from datetime import datetime


def TIME():
    return datetime.now().time()


def NOW():
    return datetime.combine(DATE, TIME())


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
RESET_P = False
RESET_G = False
LEAGUES = []
COUNTRIES = []
FOLDER = "files"
NO_PRINT = False
