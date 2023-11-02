import tools.regex_tools as rt
import tools.file_tools as ft
import requests
import json

visualcrossing_key = "2REC7AEQW2EWVYQZ4BZUT745W"

def parse_map_string(map_string):
    try:
        # Parse the input string as JSON
        data = json.loads(map_string)
        
        # Recursively convert data types
        def convert_data_types(obj):
            if isinstance(obj, list):
                return [convert_data_types(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_data_types(value) for key, value in obj.items()}
            elif isinstance(obj, str):
                # Check if the string represents a number and convert it if possible
                try:
                    return int(obj)
                except ValueError:
                    try:
                        return float(obj)
                    except ValueError:
                        return obj
            else:
                return obj

        # Convert the data types in the parsed JSON
        converted_data = convert_data_types(data)

        return converted_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

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
    data = ft.find_html(file_name)[1:]
    if not data:
        cords = get_coords(pitch)
        data = get_historic_data(cords, time)
        ft.save_html(file_name, str(data))
    return parse_map_string(data)


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
