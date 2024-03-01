import os
from pathlib import Path
import json
def take_csv_convert_json(filename, folder):
    file = open(filename)
    content = file.readlines()

    date = content[0].rstrip()
    header = content[1].rstrip()
    home_XI = content[2].rstrip()
    home_sub = content[3].rstrip()
    away_XI = content[4].rstrip()
    away_sub = content[5].rstrip()
    stadium = content[6].rstrip()
    weather = content[7].rstrip()
    evts = content[8:]
    events = []

    def strip(x):
        events.append(x.rstrip())
        
    result = map(strip, evts)
    for _ in result:
        pass

    data = {
        "v1": {        
            "date": date,
            "header": header,
            "home_XI": home_XI,
            "home_sub": home_sub,
            "away_XI": away_XI,
            "away_sub": away_sub,
            "stadium": stadium,
            "weather": weather,
            "events": events
        }
    }
    newfile = open(str(filename).replace(".csv", ".json"), "w")
    json.dump(data, newfile, indent=4, ensure_ascii=False)



folder = Path(str(os.curdir) + "/files/2023/analysis")
for file in folder.glob("**/*.csv"):
    take_csv_convert_json(file, folder)
