import tools.regex_tools as rt
import tools.file_tools as ft
import requests

visualcrossing_key = "2REC7AEQW2EWVYQZ4BZUT745W"

def get_weather_data(pitch, date, time):
    ds = date.split(".")
    ts = time.split(".")
    time = f"{ds[2]}-{ds[1]}-{ds[0]}T{ts[0]}:{ts[1]}:00"
    file_name = f"weather/{time}/{pitch.name}"
    file_name = file_name.replace("Æ", "Ae")
    file_name = file_name.replace("æ", "ae")
    file_name = file_name.replace("Ø", "O")
    file_name = file_name.replace("ø", "o")
    file_name = file_name.replace("Å", "Aa")
    file_name = file_name.replace("å", "aa")
    file_name = file_name.replace(":", "_")
    data = ft.find_html(file_name)
    if not data:
        cords = get_coords(pitch)
        data = get_historic_data(cords, time)
        ft.save_html(file_name, str(data))
    return data


def get_historic_data(coordinates, time):
    x_coord, y_coord = coordinates
    # time must be in YYYY-MM-DDTHH:MM:SS format
    endpoint = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{x_coord},{y_coord}/{time}?key={visualcrossing_key}&include=current"

    r = requests.get(endpoint)

    json = r.json()

    return json


def get_coords(pitch):
    res = rt.get_pitch_coords(pitch.page.html.text)
    return res