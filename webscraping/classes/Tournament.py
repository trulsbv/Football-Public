from bs4 import BeautifulSoup
from classes.Page import Page
from classes.Schedule import Schedule
from classes.Team import Team
import tools.regex_tools as rt


class Tournament():
    def __init__(self, parent):
        self.mainpage = parent
        self.schedule = None
        self.team = {}
        self.analyser = None
        self.page = None

    def _get_schedule_url(self):
        document = BeautifulSoup(self.page.html.text, "html.parser")
        ml = document.find(class_="match-list")
        btn = ml.find_next(class_="btn btn--default")
        return rt.find_urls(str(btn))[0]
    
    def create_team(self, name, url):
        if not name in self.team:
            self.team[name] = Team(Page(url))
            # Dette er dust, må ha en egen funksjon for dette din dritt
            self.team[name].name = self.team[name]._set_navn()
        return self.team[name]
    
    def create_schedule(self):
        self.schedule = Schedule(self, Page(self._get_schedule_url()))