import tools.regex_tools as rt
import tools.file_tools as ft
import tools.web_tools as wt
from datetime import date
from classes.Pitch import Pitch


def get_weather_data(pitch: Pitch, date: date, time: str) -> dict:
    """
    Takes a pitch and returns the weather for the given date/time

    Arguments:
        * Pitch
        * date
        * time

    Returns:
        * Dict with weatherdata
    """
    ds = str(date).split("-")
    ts = str(time).split(".")
    t = f"{ds[0]}-{ds[1]}-{ds[2]}T{ts[0]}:{ts[1]}:00"
    file_name = f"weather/{pitch.name}/{t}"
    file_name = file_name.replace("Æ", "Ae")
    file_name = file_name.replace("æ", "ae")
    file_name = file_name.replace("Ø", "O")
    file_name = file_name.replace("ø", "o")
    file_name = file_name.replace("Å", "Aa")
    file_name = file_name.replace("å", "aa")
    file_name = file_name.replace(":", "_")
    data = ft.load_json(file_name)
    if data:
        return data
    cords = get_coords(pitch)
    try:
        data = wt.get_historic_data(cords, t)
    except LookupError:  # Random error
        print("\nERROR FETCHING FROM weather_tools.py!")
        exit()
    ft.save_json(file_name, data)
    return data


def get_coords(pitch: Pitch) -> tuple:
    """
    Takes a pitch and searches throug it's webpage to find the Google-Maps search
    containing coordinates

    Arguments:
        * Pitch

    Returns:
        * Tuple coordinates
    """
    res = rt.get_pitch_coords(pitch.page.html.text)
    return res
