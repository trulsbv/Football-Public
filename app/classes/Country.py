import errors.PageNotFoundError as PageNotFoundError
import tools.regex_tools as rt
import tools.prints as prints
from classes.Page import Page
from classes.Tournament import Tournament
from bs4 import BeautifulSoup
import settings


class Country:
    def __init__(self, url):
        self.tournaments = []
        self.page = Page(url)

    def avaliable_tournaments(self):
        prints.info("Avaliable Tournaments", "", True)
        for tournament in self.tournaments:
            prints.info(tournament.page.html.title.split(str(settings.DATE.year))[0],
                        " - ",
                        True)

    def __repr__(self) -> str:
        return self.page.html.title

    def get_tournament(self, name):  # This shit doesn't work
        if self.tournaments is []:
            self.fetch_tournament()
        possible = []
        for tournament in self.tournaments:
            if name in tournament.page.html.title:  # TODO: This should be in
                possible.append(tournament)
        if not possible:
            return None
        if len(possible) == 1:
            return possible[0]
        i = 0
        for p in possible:
            print(f"[{i}]", f"{p.page.html.title}")
            i += 1
        inp = i + 1
        while not str(inp).isnumeric() or int(inp) > i:
            inp = input(" => ")
        return possible[int(inp)]

    def fetch_tournament(self):
        if self.page is None:
            raise PageNotFoundError("Country", self.page)

        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(class_="responsive-table")
        links = f.find_all(class_="hauptlink")
        urls = rt.find_urls(str(links))
        for url in urls:
            if "startseite" in url:
                dup = False
                for trnmnt in self.tournaments:
                    if url == trnmnt.page.url:
                        dup = True
                if dup:
                    continue
                self.tournaments.append(Tournament(self, url))
