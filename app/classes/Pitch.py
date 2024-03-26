from classes.Page import Page
from bs4 import BeautifulSoup
import tools.file_tools as ft
import settings


class Pitch:
    def __init__(self, url) -> None:
        self.url = url
        self.name = None
        self.width = None
        self.length = None
        self.surface = None
        self.address = None
        self.capacity = None
        self.running_track = None
        self.undersoil_heating = None
        self._load()

    def _load(self):
        data = ft.get_json(ft.TF_url_to_id(self.url), "Pitches")

        if data:
            self.name = data["data"]["name"]
            self.width = data["data"]["width"]
            self.length = data["data"]["length"]
            self.address = data["data"]["address"]
            self.surface = data["data"]["surface"]
            self.capacity = data["data"]["capacity"]
            self.running_track = data["data"]["running_track"]
            self.undersoil_heating = data["data"]["undersoil_heating"]
        else:
            self.page = Page(self.url)
            document = BeautifulSoup(self.page.html.text, "html.parser")
            for row in document.find_all(["tr"]):
                cells = row.find_all(["th", "td"])
                if not cells or len(cells) == 1:
                    continue

                head = cells[0].get_text(strip=True)
                data = cells[1].get_text(strip=True)
                if "Name of stadium" in head:
                    self.name = data
                if "Total capacity" in head:
                    self.capacity = data
                if "Running track" in head:
                    self.running_track = False if "No" in data else True
                if "Undersoil heating" in head:
                    self.undersoil_heating = data
                if "Surface" in head:
                    self.surface = data
                if "Pitch size" in head:
                    self.length, self.width = data.split(" x ")
                if "Address" in head:
                    self.address = data
            ft.write_json(self._to_json(), ft.TF_url_to_id(self.url), "Pitches")

    def _to_json(self):
        m = {
            "meta": {
                "version": 1,
                "date": str(settings.DATE)
            },
            "data": {
                "name": self.name,
                "width": self.width,
                "length": self.length,
                "address": self.address,
                "surface": self.surface,
                "capacity": self.capacity,
                "running_track": self.running_track,
                "undersoil_heating": self.undersoil_heating,
            }
        }
        return m

    def get_analysis(self):
        return {
            "name": self.name,
            "capacity": self.capacity,
            "surface": self.surface,
            "running_track": self.running_track,
            "undersoil_heating": self.undersoil_heating,
            "length": self.length,
            "width": self.width,
            "address": self.address
        }

    def __repr__(self) -> str:
        return self.name
