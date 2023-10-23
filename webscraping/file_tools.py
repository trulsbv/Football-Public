from datetime import date as d
from pathlib import Path
import prints

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

def find_html(i, extension=".txt"):
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
        - String html or False
    """
    file = find_file("pages", str(i)+extension)
    if not file:
        return False
    file = open(file, encoding="UTF-8")
    lines = file.readlines()
    s = ""
    if lines[0].strip() != str(d.today()):
        prints.warning(message=f"{i}: The content is outdated", sender="file_tools\\find_html")
        return False
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
                prints.warning(message=f"{id}: The name might be outdated", sender="file_tools\\find_name")
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

def save_html(i, h):
    """
    Takes a id and a string and saves it in [id].txt with todays date

    Input: 
        - String id
        - String html content
    
    Output: 
        - None
    """
    file = find_file("pages", str(i)+".txt")
    if not file:
        file = Path("pages") / (str(i)+".txt")
    file = open(file, 'w', encoding="UTF-8")
    file.write(str(d.today())+"\n")
    file.write(h)
    file.close()


