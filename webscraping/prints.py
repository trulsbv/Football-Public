from colorama import Fore
prev_len = 0
pos = "✓"
neg = "✘"
prev_str = ""

def fill_blanks(string, meta):
    while len(string)-meta < prev_len:
        string += " "
    return string

def _prints(s, newline, meta=0):
    global prev_len
    s = fill_blanks(s, meta)
    if newline:
        print(s)
        prev_len = 0
    else:
        print(s, end='\r')
        prev_len = len(s)-meta

def success(where=None):
    global prev_str
    s = ""
    if where:
        s += f"{Fore.GREEN}{pos}{Fore.RESET} {where}"
    else:
        s += f"{Fore.GREEN}{pos}{Fore.RESET} {prev_str}"
    meta = len(f"{Fore.RESET}{Fore.RESET}")
    _prints(s, True, meta)

def start(where):
    global prev_str
    s = f"{Fore.CYAN}→{Fore.RESET} {where}"
    meta = len(f"{Fore.CYAN}{Fore.RESET}")
    prev_str = where
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
