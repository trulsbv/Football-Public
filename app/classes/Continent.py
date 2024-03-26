from classes.Page import Page
import tools.regex_tools as rt
from bs4 import BeautifulSoup
import tools.prints as prints
import settings


class Continent():
    def __init__(self, continent, url):
        self.name = continent
        self.url = url
        self.countries = {}
        self._load()

    def _load(self):
        self.page = Page(self.url)
        document = BeautifulSoup(self.page.html.text, "html.parser")
        map = document.find("map")
        area = map.find_all("area")
        prints.info(f"Possible countries in {self.name}", "", True)
        for a in area:
            name = rt.standard_reg(a, r'title="(.[^"]*)"')
            url = "https://www.transfermarkt.com" + rt.standard_reg(a, r'href="(.[^"]*)"')
            url += f"/plus/0?saison_id={int(settings.DATE.year)-1}"
            if name not in self.countries:
                self.countries[name] = url
            prints.info(f"{name}", "*", True)

    def __repr__(self) -> str:
        return self.name
