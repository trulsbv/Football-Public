from bs4 import BeautifulSoup
from datetime import date as d, datetime
from pathlib import Path
import os
import re
import json
import settings
import traceback

main_data = {}

log_entries = 0
log_first = True


def clear_betting_data(id: str, extension: str = ".csv") -> None:
    """
    Deletes the file containing the betting data
    """
    folder = create_folder(["betting_analysis"])
    file = find_file(folder, str(id) + extension)
    if file:
        os.remove(file)


def add_betting_data(data: map, id: str, extension: str = ".csv") -> None:
    """
    TODO: This is a temporary location for this fucntion - it should not
          be in this file!

    Adds a new line to the data
    Expects data to be:
        {
            hometeam: str,
            awayteam: str,
            score: set,
            odds: set
         }
    """
    folder = create_folder(["betting_analysis"])
    file = find_file(folder, str(id) + extension)
    if not file:
        file = folder / (str(id) + extension)
    file = open(file, "a", encoding="UTF-8")
    file.write(str(d.today()) + "\n")

    ht = data.home
    at = data.away
    res = data["score"]
    odds = data["odds"]

    if not odds:
        confirm = "F"
        while confirm.upper() != "T":
            odds = input(f"Odds for {ht} {res} {at} ('1.4,4.53,3.5')")
            confirm = input(f"Review: {odds}\n  [Y/N]:")
        odds = set(odds.split(","))

    file.write(f"{ht},{res},{at},{odds}")
    file.close()


def TF_url_to_id(url):
    url = url.split(".com/")[1].replace("/", "_")
    return url


def push_json():
    folder = create_folder()
    file = find_file(folder, (settings.CURRENT_TOURNAMENT + ".json"))
    if not file:
        file = folder / (settings.CURRENT_TOURNAMENT + ".json")
    file = open(file, "w", encoding="UTF-8")
    json.dump(main_data, file, indent=4, ensure_ascii=False)


def write_json(data: map, id: str, folder: str):
    global main_data
    if main_data is None:
        read_json()
    if folder not in main_data:
        main_data[folder] = {}
    main_data[folder][id] = data
    push_json()


def delete_analysis(team: str = ""):
    global main_data
    read_json()
    if not team:
        main_data.pop("Games")
        push_json()
        return
    remove = set()
    for game in main_data["Games"]:
        if team in game:
            remove.add(game)
    for game in remove:
        main_data["Games"].pop(game)
    push_json()


def read_json():
    global main_data
    folder = create_folder()
    file = find_file(folder, (settings.CURRENT_TOURNAMENT + ".json"))
    if not file:
        return
    file = open(file, encoding="UTF-8")
    s = ""
    for line in file.readlines():
        s += line.rstrip()
    main_data = json.loads(s)


def _write_json(data: map, id: str, folder: str, extension: str = ".json") -> None:
    if folder == "Players":
        first = id[0]
        if "-" in id:
            second = id.split("-")[1][0]
        else:
            second = "_"
        folder = create_folder([str(folder), first, second])
    elif folder == "Games":
        folder = create_folder([str(folder), id[:2]])
    elif folder == "Pitches":
        folder = create_folder([str(folder), id.split("_")[3][1]])
    elif folder == "Teams":
        folder = create_folder([str(folder), id[0]])
    else:
        folder = create_folder([str(folder)])
    file = find_file(folder, str(id) + extension)
    if not file:
        file = folder / (str(id) + extension)
    file = open(file, "w", encoding="UTF-8")
    json.dump(data, file, indent=4, ensure_ascii=False)


def get_json(id: str, folder: str) -> map:
    """
    Returns map from json file stored in folder, with id and extension

    Returns None if the file can't be found
    """
    global main_data
    if main_data is None or folder not in main_data or id not in main_data[folder]:
        read_json()
    if folder not in main_data or id not in main_data[folder]:
        return None
    return main_data[folder][id]


def is_analysed(id, extension):
    return find_file(create_folder(["analysis"]), id + extension)


def url_to_folder_name(id, extension=".html"):
    splitted = id.split("/")
    name = (splitted[-1] + extension).replace("?", "")
    folder = create_folder(splitted[:-1])
    return (folder, name)


def find_file(folder, name):
    """
    Finds a file in a given folder

    Input:
        - Path/String folder
        - String name

    Output:
        - Path file or False
    """
    folder = Path(folder)
    file = folder / name
    if file.is_file():
        if file not in settings.FILES_FETCHED:
            settings.FILES_FETCHED[file] = 0
        settings.FILES_FETCHED[file] += 1
        return file
    return False


def find_html(id, extension=".html"):
    """
    Takes an id and searches through the files folder for a [id].txt file
    to see if we already have the html from a previous fetch
    This is to reduce requests.

    The file is structured:
    DATE
    DATA ...

    Input:
        - String id

    Output:
        - String html (success)
        - int 0 (failed to find page)
        - int 1 (found outdated page)
    """
    splitted = id.split("/")
    filename = (splitted[-1] + extension).replace("?", "")
    folder = create_folder(splitted[:-1])
    file = find_file(folder, filename)
    if not file:
        return 0
    file = open(file, encoding="UTF-8")
    lines = file.readlines()
    s = ""
    for line in lines:
        s += line
    return s


def save_html(id, html, extension):
    """
    Takes a id and a string and saves it in [id].txt with todays date

    Input:
        - String id
        - String html content

    Output:
        - None
    """
    splitted = id.split("/")
    filename = splitted[-1].replace("?", "")
    folder = create_folder(splitted[:-1])

    file = find_file(folder, str(filename) + extension)
    if not file:
        file = folder / (str(filename) + extension)
    file = open(file, "w", encoding="UTF-8")
    file.write(str(d.today()) + "\n")
    file.write(html)
    file.close()


def delete_html(id: str = "", url: str = "", extension: str = ".html") -> None:
    """
    Takes a id and deletes the file associated to it
    Input:
        - String id

    Output:
        - None
    """
    if not id and url:
        id = url.replace("https://www.", "")
        id = id[:-1] if id[-1] == "/" else id

    splitted = id.split("/")
    filename = splitted[-1].replace("?", "")
    folder = create_folder(splitted[:-1])
    file = find_file(folder, str(filename) + extension)
    print(folder, filename)
    if file:
        os.remove(file)
        return True
    return False


def load_json(id):
    splitted = id.split("/")
    filename = (splitted[-1] + ".json").replace("?", "")
    folder = create_folder(splitted[:-1])
    file = find_file(folder, filename)
    if not file:
        return 0
    file = open(file, encoding="UTF-8")
    s = ""
    for line in file.readlines():
        s += line.rstrip()
    d = json.loads(s)
    file.close()
    return d


def save_json(id, data):
    """
    Takes a id and a string and saves it in [id].txt with todays date

    Input:
        - String id
        - String html content

    Output:
        - None
    """
    splitted = id.split("/")
    filename = splitted[-1].replace("?", "")
    folder = create_folder(splitted[:-1])

    file = find_file(folder, str(filename) + ".json")
    if not file:
        file = folder / (str(filename) + ".json")
    file = open(file, "w", encoding="UTF-8")
    json.dump(data, file, indent=4, ensure_ascii=False)
    file.close()


def create_folder(inp: str = ""):
    if inp:
        folders = ["files"] + [str(settings.DATE.year)] + inp
    else:
        folders = ["files"] + [str(settings.DATE.year)]
    place = str(os.curdir)
    for folder in folders:
        place += "/" + folder
        f = Path(place)
        if not f.exists():
            os.mkdir(f)
    return Path(place)


def is_not_valid(id, valid_from, ext):
    # Når er den valid?
    # - Filen finnes
    # - Datoen filen er hentet er etter valid_from
    folder, name = url_to_folder_name(id, ext)
    if not find_file(folder, name):
        return True
    if valid_from is False:
        return False

    str_date = find_html(id).split("\n")[:1][0]
    date_date = datetime.strptime(str_date, "%Y-%m-%d").date()
    return date_date < valid_from


def get_baneinfo(html):
    document = BeautifulSoup(html, "html.parser")
    title = document.select("h1")[0].text.strip()
    info = document.find(class_="section-heading", string=re.compile("^Baneinfo"))
    info = info.find_next("ul")
    dict = {
        "navn": title,
        "underlag": None,
        "banetype": None,
        "belysning": None,
        "lengde": None,
        "bredde": None,
        "driftsform": None,
        "krets": None,
    }
    for item in [li.get_text(strip=True) for li in info]:
        if item and ":" in item:
            if len(item.split(":")) > 2:
                continue
            n, v = item.split(":")
            if n.lower() in dict:
                dict[n.lower()] = v

    out = []
    for key in dict:
        out.append(dict[key])
    return out


def log(msg):
    if not settings.LOG_BOOL:
        return
    global log_entries
    global log_first
    if log_first:
        clear_log()
        log_first = False
    f = open("files/log.txt", "a", encoding="UTF-8")
    f.write(f"{log_entries}: {msg}\n")
    for line in traceback.format_stack():
        li = line.strip().replace('File "C:\\Users\\Truls\\Documents\\Fotball\\app', '..')
        f.write(f"\t{li}\n")
    f.close()
    log_entries += 1


def clear_log():
    f = open("files/log.txt", "w")
    f.write(str(d.today()) + "\n")
    f.close()
    global log_entries
    log_entries = 0
