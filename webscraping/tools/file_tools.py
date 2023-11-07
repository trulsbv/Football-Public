from bs4 import BeautifulSoup
from datetime import date as d, datetime
from pathlib import Path
import os
import re
import tools.prints as prints
import tools.web_tools as wt

def id_to_folder_name(id, extension=".html"):
    splitted = id.split("/")
    name = (splitted[-1]+extension).replace("?", "")
    folder = create_folder(["pages"] + splitted[:-1])
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
        return file
    return False

def find_html(id, extension=".html"):
    """
    Takes an id and searches through the pages folder for a [id].txt file
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
    filename = (splitted[-1]+extension).replace("?", "")
    folder = create_folder(["pages"] + splitted[:-1])
    file = find_file(folder, filename)
    if not file:
        return 0
    file = open(file, encoding="UTF-8")
    lines = file.readlines()
    s = ""
    for line in lines:
        s+=line
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
    folder = create_folder(["pages"] + splitted[:-1])

    file = find_file(folder, str(filename)+extension)
    if not file:
        file = folder / (str(filename)+extension)
    file = open(file, 'w', encoding="UTF-8")
    file.write(str(d.today())+"\n")
    file.write(html)
    file.close()

def create_folder(folders):
    place = str(os.curdir)
    for folder in folders:
        place += "/"+folder
        f = Path(place)
        if not f.exists():
            os.mkdir(f)
    return Path(place)

def is_not_valid(id, valid_from, ext):
    # Når er den valid?
    # - Filen finnes
    # - Datoen filen er hentet er etter valid_from
    folder, name = id_to_folder_name(id, ext)
    if not find_file(folder, name):
        return True
    if valid_from == False:
        return False
    
    str_date = find_html(id).split("\n")[:1][0]
    date_date = datetime.strptime(str_date, "%Y-%m-%d").date()
    return date_date < valid_from

def get_baneinfo(html):
    document = BeautifulSoup(html, "html.parser")
    title = document.select('h1')[0].text.strip()
    info = document.find(class_="section-heading", string=re.compile("^Baneinfo"))
    info = info.find_next("ul")
    dict = {"navn": title, "underlag": None, "banetype": None, "belysning": None, "lengde": None, "bredde": None, "driftsform": None, "krets": None}
    for item in [li.get_text(strip=True) for li in info]:
        if item and ":" in item:
            if len(item.split(":")) > 2:
                continue
            n, v = item.split(":")
            if n in dict:
                dict[n] = v

    out = []
    for key in dict:
        out.append(dict[key])
    return out

entries = 1
def log(where, msg):
    global entries
    f = open("log/log.txt", "a")
    f.write(f"{entries} {where}: {msg}\n")
    f.close()
    entries+=1

def clear_log():
    f = open("log/log.txt", "w")
    f.write(str(d.today()) + "\n")
    f.close()
