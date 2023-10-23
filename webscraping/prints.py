from colorama import Fore
def warning(message, sender="WARNING"):
    """
    Prints a message to the user in with the sender in yellow

    Input:
        - String message
        - String sender
    
    Output:
        - None
    """
    print(f"[{Fore.YELLOW}{sender.upper()}{Fore.RESET}] {message}")

def info(message, sender="INFO"):
    """
    Prints a message to the user
    """
    print(f"[{sender.upper()}] {message}")
