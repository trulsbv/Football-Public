import tools.regex_tools as rt
import tools.file_tools as ft
import tools.web_tools as wt


def parse_map_string(map_string):
    d = eval(map_string.split("\n")[1])
    assert type(d) == dict
    return d

def get_weather_data(pitch, date, time):
    ds = str(date).split("-")
    ts = str(time).split(".")
    time = f"{ds[2]}-{ds[1]}-{ds[0]}T{ts[0]}:{ts[1]}:00"
    file_name = f"weather/{pitch.name}/{time}"
    file_name = file_name.replace("Æ", "Ae")
    file_name = file_name.replace("æ", "ae")
    file_name = file_name.replace("Ø", "O")
    file_name = file_name.replace("ø", "o")
    file_name = file_name.replace("Å", "Aa")
    file_name = file_name.replace("å", "aa")
    file_name = file_name.replace(":", "_")
    data = ft.find_html(file_name, extension=".txt")
    if data:
        return parse_map_string(data)
    cords = get_coords(pitch)
    try:
        data = wt.get_historic_data(cords, time)
    except:
        return False
    ft.save_html(file_name, str(data), ".txt")
    return data

def get_coords(pitch):
    res = rt.get_pitch_coords(pitch.page.html.text)
    return res
