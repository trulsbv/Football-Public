from dotenv import load_dotenv
import os
import requests
import tools.prints as prints


load_dotenv()

visualcrossing_key = os.getenv("VISUALCROSSING_KEY")
fetches = 0

def utfify(s):
    s = s.replace("&#248;", "ø")
    s = s.replace("&#216;", "Ø")
    s = s.replace("&#229;", "å")
    s = s.replace("&#197;", "Å")
    s = s.replace("&#230;", "æ")
    s = s.replace("&#198;", "Æ")
    s = s.replace("&#39;", "'")
    return s

def get_html(url: str, params: dict | None = None, output: str | None = None):
    """Get an HTML page and return its contents.

    Args:
        url (str):
            The URL to retrieve.
        params (dict, optional):
            URL parameters to add.
        output (str, optional):
            (optional) path where output should be saved.
    Returns:
        html (str):
            The HTML of the page, as text.
    """
    global fetches
    fetches += 1
    prints.download(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Charset': 'utf-8'
    }
    # passing the optional parameters argument to the get function
    response = requests.get(url, params=params, headers=headers)

    html_str = utfify(response.text)
    if output:
        # if output is specified, the response url and text content are written to
        # the file `output`
        f = open(output, "w", encoding="UTF-8")
        f.write(url+"\n")
        f.write(html_str)
        f.close()

    return html_str

def get_historic_data(coordinates, time):
    global fetches
    fetches+=1
    x_coord, y_coord = coordinates
    
    prints.download(coordinates)
    endpoint = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{x_coord},{y_coord}/{time}?key={visualcrossing_key}&include=current"

    return requests.get(endpoint).json()
