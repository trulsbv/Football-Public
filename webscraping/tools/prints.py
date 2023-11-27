from colorama import Fore, Back
import time

time_start = 0.0
prev_len = 0
pos = "✓"
neg = "✘"
prev_str = ""

def fill_blanks(string, meta):
    while len(string)-meta < prev_len:
        string += " "
    if prev_str == "":
        string += "  "
    return string

def _prints(s, newline, meta=0):
    global prev_len
    s = fill_blanks(s, meta)
    if newline:
        if prev_str != "":
            print("  " + s)
        else:
            print(s)
    else:
        if prev_str != "":
            print("  " + s, end='\r')
        else:
            print(s, end='\r')
        prev_len = len(s)-meta

def success(where=None):
    global prev_str
    s = ""
    t = round((time.perf_counter() - time_start), 3)

    if where:
        s += f"{Fore.GREEN}{pos}{Fore.RESET} {where} ({t} s)"
    else:
        s += f"{Fore.GREEN}{pos}{Fore.RESET} {prev_str} ({t} s)"
    meta = len(f"{Fore.RESET}{Fore.RESET}")
    prev_str = ""

    _prints(s, True, meta)

def start(where):
    global prev_str
    global time_start
    s = f"{Fore.CYAN}→{Fore.RESET} {where}"
    meta = len(f"{Fore.CYAN}{Fore.RESET}")
    prev_str = where
    time_start = time.perf_counter()
    _prints(s, False, meta)

def error(where, message="No reason given, sorry."):
    s = f"{Fore.RED}{neg}{Fore.RESET} {where}: {message}"
    meta = len(f"{Fore.RED}{Fore.RESET}")
    _prints(s, True, meta)

def warning(where, message="", newline=True):
    """
    Prints a message to the user in with the sender in yellow

    Input:
        - String message
        - String sender
    
    Output:
        - None
    """
    s = f"{Fore.YELLOW}{pos}{Fore.RESET} {where}{':'if message else ''} {message}"
    meta = len(f"{Fore.YELLOW}{Fore.RESET}")
    _prints(s, newline, meta)

def download(url):
    s = f"{Fore.CYAN}↓{Fore.RESET} {url}"
    meta = len(f"{Fore.CYAN}{Fore.RESET}")
    _prints(s, False, meta)

def info(message, sender="?", newline=False):
    s = f"{sender} {message}"
    _prints(s, newline)

def STOP():
    global prev 
    prev = False
    s = f"{Back.RED}{Fore.BLACK}STOPPING THE SCRIPT{Fore.RESET}{Back.RESET}"
    meta = len(f"{Back.RED}{Fore.BLACK}{Fore.RESET}{Back.RESET}")
    _prints(s, newline=True, meta=meta)

def header(message):
    _prints(message, newline=True)

def row(message):
    _prints(message, newline=True)

def whiteline():
    print()

def get_green_fore(message):
    return f"{Fore.GREEN}{message}{Fore.RESET}" 

def get_yellow_fore(message):
    return f"{Fore.YELLOW}{message}{Fore.RESET}" 


def get_red_fore(message):
    return f"{Fore.RED}{message}{Fore.RESET}" 

def get_blue_back(message):
    return f"{Back.BLUE}{message}{Back.RESET}"

def get_fore_color_int(int):
    if int > 0: return get_green_fore(int)
    if int < 0: return get_red_fore(int)
    return get_yellow_fore(int)

def START():
    global START_TIME
    START_TIME = time.perf_counter()

def FINISH():
    t = round((time.perf_counter() - START_TIME), 3)
    message = f" => {t} s"
    _prints(message, newline=True)
