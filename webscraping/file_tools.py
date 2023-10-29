from datetime import date as d, datetime
import web_tools as wt
from pathlib import Path
import prints, os, re
from bs4 import BeautifulSoup

def id_to_folder_name(id, extension=".txt"):
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

def find_html(id, extension=".txt"):
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
    if lines[0].strip() != str(d.today()):
        return 1
    for line in lines:
        s+=line
    return s

def find_name(i):
    """
    Takes an id and searches through known_ids.csv
    to see if we already know the name of the id from a previous fetch
    This is to reduce requests.

    The file is structured:
    ID;NAME;DATE

    Input: 
        - String id
    
    Output:
        - String name or False
    """
    file = open("known_ids.csv", "r", encoding="UTF-8")
    lines = file.readlines()
    for line in lines:
        id, name, _date = line.split(";")
        date = _date.strip()
        if id == i:
            if date != str(d.today()):
                prints.warning(message=f"{id}: The name '{name}' might be outdated", sender="file_tools\\find_name")
            return name
    return False

def save_name(n, i):
    """
    Takes a name and id and saves it in known_ids.csv with todays date

    Input: 
        - String name
        - String id
    
    Output: 
        - None
    """
    file = "known_ids.csv"
    fileLines = open(file, 'r', encoding="UTF-8").readlines()
    modified = False
    modifyLines = open(file, 'w', encoding="UTF-8")
    for line in fileLines:
        id, _name, _date = line.split(";")
        if i == id:
            modified = True
            modifyLines.write(f"{i};{n};{d.today()}\n")
        else:
            modifyLines.write(line)
    if not modified:
        modifyLines.write(f"{i};{n};{d.today()}\n")
    modifyLines.close()

def save_html(id, html):
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

    file = find_file(folder, str(filename)+".txt")
    if not file:
        file = folder / (str(filename)+".txt")
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

def is_expired(id, days_before_expiration = 0):
    folder, name = id_to_folder_name(id)
    if not find_file(folder, name):
        return True
    if find_html(id) == 1:
        prints.warning(message=f"The content is outdated: {id}", sender="file_tools\\find_html")
        return True
    date_str = find_html(id).split("\n")[:1][0]
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    delta = date - d.today()
    return delta.days > days_before_expiration

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
    f = open("log.txt", "a")
    f.write(f"{entries} {where}: {msg}\n")
    f.close()
    entries+=1

def clear_log():
    f = open("log.txt", "w")
    f.write(str(d.today()) + "\n")
    f.close()
