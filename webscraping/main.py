import web_tools as wt
import regex_tools as rt
import file_tools as ft
from bs4 import BeautifulSoup
import prints, sys
from errors.PageNotFoundError import PageNotFoundError
from Page import Page
import settings, re
from datetime import date, datetime

serier=["Eliteserien"]

class Hovedside():
    turneringer = []
    page = None
    
    def get_turnering(self, navn):
        if self.turneringer is []:
            self.fetch_turneringer()
        for turnering in self.turneringer:
            if navn in turnering.page.html.title:
                return turnering
        return None
    
    def fetch_turneringer(self):
        if self.page == None:
            raise PageNotFoundError("Hovedside", self.page)
        urls = set(rt.find_urls(self.page.html.text))
        for url in urls:
            u = rt.find_league_from_url(url.rstrip("/"))
            if u:
                new = Turnering(self)
                new.page = Page(url)
                self.turneringer.append(new)


class Turnering():
    terminliste = None
    lag = {}
    analyser = None
    page = None

    def __init__(self, parent):
        self.hovedside = parent

    def get_termin_url(self):
        return self.page.url.replace("hjem", "terminliste")
    
    def create_lag(self, navn, url):
        if not navn in self.lag:
            self.lag[navn] = Lag()
            self.lag[navn].page = Page(url)
        return self.lag[navn]
        

class Terminliste():
    kamper = []
    page = None

    def __init__(self, parent):
        self.turnering = parent

    def fetch_kamper(self):
        document = BeautifulSoup(self.page.html.text, "html.parser")
        table = document.find("table")

        rows = table.find_all("tr")
        column_names = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        assert "Hjemmelag" in column_names
        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            if not cells:
                continue
            urls = rt.find_urls(str(row))
            cells_text = [cell.get_text(strip=True) for cell in cells]
            runde, dato, dag, tid, _, _hjemmelag, _resultat, _bortelag, _bane, kampnr = cells_text
            
            hjemmelag = self.turnering.create_lag(_hjemmelag, urls[1])
            bortelag = self.turnering.create_lag(_bortelag, urls[3])
            hendelser = Hendelser()
            hendelser.page = Page(urls[2])
            bane = Bane()
            bane.page = Page(urls[4])

            kamp = Kamp(runde, dato, dag, tid, hjemmelag, hendelser, bortelag, bane, kampnr)
            self.kamper.append(kamp)
    

class Kamp():
    def __init__(self, runde, dato, dag, tid, hjemmelag, resultat, bortelag, bane, kampnummer):
        self.runde = runde
        self.dato = dato
        self.dag = dag
        self.tid = tid
        self.hjemmelag = hjemmelag # Page - To the team
        self.resultat = resultat # Page - To the game
        self.bortelag = bortelag # Page - To the team
        self.bane = bane # Page - To the pitch
        self.kampnummer = kampnummer
    
    def analyse(self):
        self.resultat.analyse(self)
    
    def __repr__(self) -> str:
        s = f"{self.runde} ({self.dag} {self.dato} kl. {self.tid}) {self.hjemmelag} "
        if datetime.strptime(self.dato, "%d.%m.%Y") < datetime.today():
            s += f"{self.resultat} "
        else:
            s += " -  "
        s += f"{self.bortelag}, {self.bane} ({self.kampnummer})"
        return s

class Hendelser():
    hendelser = []
    uref_hendelser = []
    page = None
    kamp = None

    def analyse(self, parent):
        self.kamp = parent
        if len(self.uref_hendelser) == 0:
            print("Henter events")
            self._get_events()
            
            print("Hentet events")
        for text in self.uref_hendelser:
            f = Factory(parent, text)
            self.hendelser.append(f.analyse())
        
        i = 0
        while i < len(self.hendelser):
            if type(self.hendelser[i]) == Bytte:
                self.hendelser[i] = self.hendelser[i] + self.hendelser[i+1]
                self.hendelser.remove(self.hendelser[i+1])

        print(self.hendelser)

    def _get_events(self):
        self.uref_hendelser = []
        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(class_="section-heading no-margin--bottom", string=re.compile("^Hendelser"))
        table = f.find_next("ul")

        self.uref_hendelser = table.find_all("li")

    def __repr__(self) -> str:
        home_goals = 0
        away_goals = 0 
        if self.kamp == None:
            return f"{home_goals} - {away_goals}"
        
        for item in self.hendelser:
            if type(item) == Maal(): # Spillemaal / straffemaal?
                if item.team == self.kamp.hjemmelag:
                    home_goals += 1
                else:
                    away_goals += 1
        return f"{home_goals} - {away_goals}"

class Factory():
    def __init__(self, game, text):
        self.game = game
        self.text = text

    def analyse(self):
        r = rt.analysis(self.text)
        lag = r["lag"]
        type = r["type"]
        minutt = r["minutt"]
        lenke = r["lenke"]
        navn = r["navn"]
        id = r["id"]
        print(type)

        match type:
            case "Spillemål": type = Spillemaal(self.game, minutt, lag, (navn, lenke))
            case "Advarsel": type = GultKort(self.game, minutt, lag, (navn, lenke))
            case "Bytte inn": type = Bytte(self.game, minutt, lag, (navn, lenke), None, id)
            case "Bytte ut": type = Bytte(self.game, minutt, lag, None, (navn, lenke), id)
            case _: prints.warning(self, f"{type} not handled!"); type = None

        return type # Spiller, tid, spillemål/straffe?
class Hendelse():
    def __init__(self, game, time, team):
        self.game = game
        self.time = time
        self.team = game.hjemmelag if team == "home team" else game.bortelag

class Kort(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = player

class GultKort(Kort):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

class RodtKort(Kort):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

class Bytte(Hendelse):
    def __init__(self, game, time, team, player_in, player_out, id):
        super().__init__(game, time, team)
        self.player_in = player_in
        self.player_out = player_out
        self.id = id

class Maal(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = player

class Spillemaal(Maal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

class Straffemaal(Maal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)

class Bane():
    page = None
    navn = None

    def fetch_info(self):
        self.navn, self.underlag, self.banetype, self.belysning, self.lengde, self.bredde, self.driftsform, self.krets = ft.get_baneinfo(self.page.html.text)
        
    def __repr__(self) -> str:
        if self.navn == None:
            self.fetch_info()
        return self.navn

class Lag():
    spillere = []
    page = None
    navn = None

    def _set_navn(self):
        if not rt.get_team_name(self.page.html.text):
            exit()
        return rt.get_team_name(self.page.html.text)

    def _set_krets(self):
        return rt.get_krets(self.html.text)
    
    def __repr__(self) -> str:
        if self.navn == None:
            self.navn = self._set_navn()
        return self.navn


class Spiller():
    def __init__(self, team, name, number, position):
        self.team = team
        self.name = name
        self.number = number
        self.position = position

def main():
    hoved = Hovedside()
    prints.start("Hovedside")
    hoved.page = Page("https://www.fotball.no/turneringer/")
    prints.success("Hovedside")

    
    prints.start("Turneringer")
    try:
        hoved.fetch_turneringer()
        prints.success("Turneringer")
    except PageNotFoundError as e:
        prints.error("Turneringer", e)
        exit()
    except:
        prints.error("Turneringer")
        exit()

    prints.start("Postnord avd. 1")
    try:
        postnord1 = hoved.get_turnering("Post Nord-ligaen avd. 1")
        prints.success("Postnord avd. 1")
    except:
        prints.error("Postnord avd. 1")
        exit()

    prints.start("Terminliste")
    try:
        pn1_terminliste = Terminliste(postnord1)
        pn1_terminliste.page = Page(postnord1.get_termin_url())
        prints.success("Terminliste")
    except:
        prints.error("Terminliste")
        exit()

    prints.start("Finne dager")
    dager = {}
    pn1_terminliste.fetch_kamper()
    
    for game in pn1_terminliste.kamper:
        game.analyse()
        return
        print(game)
        if game.dag in dager:
            dager[game.dag] += 1
        else:
            dager[game.dag] = 1
    prints.success("Finne dager")
    print(dager)
    print(f"Antall sider hentet: {wt.fetches}")



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
    main()
