import errors.PageNotFoundError as PageNotFoundError
from classes.Page import Page
import tools.regex_tools as rt
from classes.Tournament import Tournament

class Mainpage():
    def __init__(self):
        self.tournaments = []
        self.page = None
    
    def get_tournament(self, name):
        if self.tournaments is []:
            self.fetch_tournament()
        possible = []
        for turnering in self.tournaments:
            if name in turnering.page.html.title:
                possible.append(turnering)
        if not possible:
            return None
        if len(possible) == 1:
            return possible[0]
        i = 0
        for p in possible:
            print(f"[{i}] {p.page.html.title}")
            i+=1
        inp = i+1
        while not str(inp).isnumeric() or int(inp) > i:
            inp = input(" => ")
        return possible[int(inp)]
    
    def fetch_tournament(self):
        if self.page == None:
            raise PageNotFoundError("Mainpage", self.page)
        urls = set(rt.find_urls(self.page.html.text))
        for url in urls:
            u = rt.find_league_from_url(url.rstrip("/"))
            if u:
                new = Tournament(self)
                new.page = Page(url)
                self.tournaments.append(new)
