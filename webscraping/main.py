import web_tools as wt
import regex_tools as rt
import file_tools as ft
from datetime import date
from bs4 import BeautifulSoup
import prints, sys
from errors.PageNotFoundError import PageNotFoundError

serier=["Eliteserien"]
log_bool=False

def log(where, msg):
    if log_bool:
        print
        ft.log(where, msg)

class HTML():
    def __init__(self, page, search):
        self.page = page
        self.fetched = date.today()
        self.expires_after_days = 1
        self.text = self._set_html(search)
        self.title = self._set_title()
    
    def _set_title(self):
        if not self.text:
            return ""
        else:
            return rt.get_title(self.text)

    def _set_html(self, search=False, force=False):
        # TODO: Sørg for at den bare oppdaterer om den er utdatert!
        if (search and ft.is_expired(self.page.id, self.expires_after_days)) or force:
            text = wt.get_html(self.page.url)
            self._save_html(text)
            return text
        else:
            value = ft.find_html(self.page.id)
            if value == 1:
                return self._set_html(True)
            if value == 0:
                return False
            return ft.find_html(self.page.id)

    def _save_html(self, text=False):
        t = text if text else self.text
        ft.save_html(self.page.id, t)

class Page():
    def __init__(self, url, search=True, force = False):
        """
        Set search to false if you don't want to keep the page updated / fetch the page at all
        """
        self.url = url
        self.id = self._set_id()
        self.fetched = False
        self.html = HTML(self, search)
        if force:
            self.html._set_html(force=True)

    def update_html(self):
        if not self.html.text:
            self._update_html()
            return
        if self.html.text.split("\n")[0] != str(date.today()):
            self._update_html()
    
    def _update_html(self):
        self.html._set_html(True)

    def _set_id(self):
        return self.url.replace("https://www.", "")

    def __hash__(self):
        return hash(self.url)
    
    def __lt__(self, obj):
        return ((self.id) < (obj.id)) 

    def __eq__(self, other):
        if type(other) == str:
            return other == self.url
        if type(other) == Page:
            return other.url == self.url
        return False

    def __repr__(self) -> str:
        return self.url
      

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
            bortelag = self.turnering.create_lag(_hjemmelag, urls[3])
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

class Hendelser():
    hendelser = []
    page = None

    def __repr__(self) -> str:
        home_goals = 0
        away_goals = 0 
        for item in self.hendelser:
            if type(item) == Hjemmemaal:
                home_goals += 1
            if type(item) == Bortemaal:
                away_goals += 1

class Hendelse():
    def __init__(self, hvem, hva, hvor):
        ...

class Kort(Hendelse):
    ...

class GultKort(Kort):
    ...

class RodtKort(Kort):
    ...

class Bytte(Hendelse):
    ...

class Maal(Hendelse):
    ...

class Hjemmemaal(Maal):
    ...

class Bortemaal(Maal):
    ...

class Bane():
    page = None

    def fetch_info(self):
        self.navn, self.underlag, self.banetype, self.belysning, self.lengde, self.bredde, self.driftsform, self.krets = ft.get_baneinfo(self.page.html.text)
        
    def __repr__(self) -> str:
        if self.navn == None:
            self.fetch_info()
        return self.navn

class Lag():
    spillere = []
    page = None

    def _set_navn(self):
        if not rt.get_team_name(self.page.html.text):
            exit()
        return rt.get_team_name(self.page.html.text)

    def _set_krets(self):
        return rt.get_krets(self.html.text)
    
    def __repr__(self) -> str:
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
    try:
        dager = {}
        pn1_terminliste.fetch_kamper()
        for game in pn1_terminliste.kamper:
            #print(f"Runde {game.runde} ({game.dato}, kl.{game.tid}), {game.hjemmelag} {game.resultat} {game.bortelag} på {game.bane} ({game.kampnummer})")
            if game.dag in dager:
                dager[game.dag] += 1
            else:
                dager[game.dag] = 1
        prints.success("Finne dager")
        print(dager)
        print(f"Antall sider hentet: {wt.fetches}")
    except:
        prints.error("Finne dager")
        exit()



if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
    main()
