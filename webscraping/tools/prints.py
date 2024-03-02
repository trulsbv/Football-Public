from colorama import Fore, Back
import time

time_start = 0.0
prev_len = 0
pos = "✓"
neg = "✘"
prev_str = ""


def fill_blanks(string: str, meta: int) -> str:
    """
    Takes a string and the number of characters that the previous string
    was, and fills the string with white-space if meta > len(string)
    Returns the string
    """
    while len(string) - meta < prev_len:
        string += " "
    if prev_str == "":
        string += "  "
    return string


def _prints(s: str, newline: bool, meta: int = 0) -> None:
    """
    Prints a string, and a newline if newline set true.
    Meta is used to calculate how many white-spaces is needed
    if there is no new-line
    """
    global prev_len
    s = fill_blanks(s, meta)
    if newline:
        if prev_str != "":
            print("  " + s)
        else:
            print(s)
    else:
        if prev_str != "":
            print("  " + s, end="\r")
        else:
            print(s, end="\r")
        prev_len = len(s) - meta


def success(where: str = None) -> None:
    """
    Lets the user know the task it was working on is completed. If
    where is not indicated, uses the last thing that start() worked on
    """
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


def start(where: str) -> None:
    """
    Starts a timer and prints a message to the user indicating
    what the script is working on, i.e. a loading screen
    """
    global prev_str
    global time_start
    s = f"{Fore.CYAN}→{Fore.RESET} {where}"
    meta = len(f"{Fore.CYAN}{Fore.RESET}")
    prev_str = where
    time_start = time.perf_counter()
    _prints(s, False, meta)


def error(where: any, message: any = "No reason given, sorry.") -> None:
    """
    Lets the user know an error occured, where and if possible a message of what
    kind of error.
    """
    s = f"{Fore.RED}{neg}{Fore.RESET} {where}: {message}"
    meta = len(f"{Fore.RED}{Fore.RESET}")
    _prints(s, True, meta)


def warning(where: any = "", message: any = "", newline: bool = True) -> None:
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


def download(url: str) -> None:
    """
    Lets the user know the url is being downloaded
    """
    s = f"{Fore.CYAN}↓{Fore.RESET} {url}"
    meta = len(f"{Fore.CYAN}{Fore.RESET}")
    _prints(s, False, meta)


def info(message: any, sender: any = "?", newline: bool = False) -> None:
    """
    Takes a message, a sender and a boolean and prints to terminal
    """
    s = f"{sender} {message}"
    _prints(s, newline)


def STOP() -> None:
    """
    Warns the user that script is stopping
    """
    global prev
    prev = False
    s = f"{Back.RED}{Fore.BLACK}STOPPING THE SCRIPT{Fore.RESET}{Back.RESET}"
    meta = len(f"{Back.RED}{Fore.BLACK}{Fore.RESET}{Back.RESET}")
    _prints(s, newline=True, meta=meta)


def header(message: str) -> None:
    """
    Prints a table header
    """
    _prints(message, newline=True)


def row(message: str) -> None:
    """
    Prints rows in a table
    """
    _prints(message, newline=True)


def whiteline() -> None:
    """
    Prints a whiteline/newline
    """
    print()


def get_green_fore(message: any) -> str:
    """
    Takes a message and returns it with green text
    """
    return f"{Fore.GREEN}{message}{Fore.RESET}"


def get_yellow_fore(message: any) -> str:
    """
    Takes a message and returns it with yellow text
    """
    return f"{Fore.YELLOW}{message}{Fore.RESET}"


def get_red_fore(message: any) -> str:
    """
    Takes a message and returns it with red text
    """
    return f"{Fore.RED}{message}{Fore.RESET}"


def get_blue_back(message: any) -> str:
    """
    Takes a message and returns it with blue background
    """
    return f"{Back.BLUE}{message}{Back.RESET}"


def get_fore_color_int(int) -> str:
    """
    Takes a integer and returns a colored string
    - Negative: Red
    - Zero: Yellow
    - Positive: Green
    """
    if int > 0:
        return get_green_fore(int)
    if int < 0:
        return get_red_fore(int)
    return get_yellow_fore(int)


def START() -> None:
    """
    Starts the public timer
    """
    global START_TIME
    START_TIME = time.perf_counter()


def FINISH() -> None:
    """
    Finishes the timer and prints the time
    """
    t = round((time.perf_counter() - START_TIME), 3)
    message = f" => {t} s"
    _prints(message, newline=True)
