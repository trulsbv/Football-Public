import tools.file_tools as ft

class Pitch():
    def __init__(self, page):
        self.page = page
        self.name = None
        self.games = [] # not used yet? But the pitch could keep the games played at it
        self.fetch_info()

    def fetch_info(self):
        self.name, self.underlag, self.banetype, self.belysning, self.lengde, self.bredde, self.driftsform, self.krets = ft.get_baneinfo(self.page.html.text)

    def get_analysis_str(self):
        items = [self.name, self.underlag, self.banetype, self.belysning, self.lengde, self.bredde, self.driftsform, self.krets]
        s = ""

        f = True
        for item in items:
            if not f:
                s += ","
            f = False
            if not item:
                continue
            s += str(item)

        return s

    def __repr__(self) -> str:
        if self.name == None:
            self.fetch_info()
        return self.name
