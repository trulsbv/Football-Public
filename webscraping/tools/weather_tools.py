import http.client, urllib.parse
import tools.regex_tools as rt
import tools.file_tools as ft
import requests

visualcrossing_key = "2REC7AEQW2EWVYQZ4BZUT745W"
positionstack_key = "42823db8e0906080f89377abc4223bbb"

def get_weather_data(stadium_name, hometeam, time):
    file_name = f"weather/{stadium_name}"
    file_name = file_name.replace("Æ", "Ae")
    file_name = file_name.replace("æ", "ae")
    file_name = file_name.replace("Ø", "O")
    file_name = file_name.replace("ø", "o")
    file_name = file_name.replace("Å", "Aa")
    file_name = file_name.replace("å", "aa")
    data = ft.find_html(file_name)
    data = get_coords(stadium_name)
    if data[0] != "Norway":
        print("Wrraa")
        data = get_coords(hometeam)
    print(data)

    return
    ft.save_html(file_name, "4")

    print(get_coords("Intility Arena"))
    #print(get_historic_data(get_coords("Bislett"), "2020-12-15T13:00:00"))

def get_historic_data(coordinates, time):
    x_coord, y_coord = coordinates
    # time must be in YYYY-MM-DDTHH:MM:SS format
    endpoint = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{x_coord},{y_coord}/{time}?key={visualcrossing_key}&include=current"

    r = requests.get(endpoint)

    json = r.json()

    return json


def get_coords(name, region=False):
    conn = http.client.HTTPConnection('api.positionstack.com')

    if not region:
        params = urllib.parse.urlencode({
            'access_key': positionstack_key,
            'query': name,
            'country': "NO",
            'limit': 1,
        })
    if region:
        params = urllib.parse.urlencode({
            'access_key': positionstack_key,
            'query': name,
            'country': "NO",
            'region': "Oslo",
            'limit': 1,
        })

    conn.request('GET', '/v1/forward?{}'.format(params))

    res = conn.getresponse()
    data = res.read()
    print(data.decode('utf-8'))
    return rt.get_coords(data.decode('utf-8'))
