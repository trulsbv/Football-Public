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
            self.lag[navn] = Lag(Page(url))
            # Dette er dust, må ha en egen funksjon for dette din dritt
            self.lag[navn].navn = self.lag[navn]._set_navn()
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
            hendelser = Hendelser(Page(urls[2]))
            bane = Bane()
            bane.page = Page(urls[4])

            kamp = Kamp(runde, dato, dag, tid, hjemmelag, hendelser, bortelag, bane, kampnr)
            self.kamper.append(kamp)
    

class Kamp():
    hendelser = []
    hometeam = None,
    awayteam = None

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

    def _is_played(self):
        return datetime.strptime(self.dato, "%d.%m.%Y") < datetime.today()
    
    def analyse(self):
        if self._is_played():
            self.hendelser = self.resultat.analyse(self)
            result = self.resultat.get_team_sheet()
            if result:
                hometeam, awayteam = self.resultat.get_team_sheet()
        else:
            prints.warning(f"{self.hjemmelag} - {self.bortelag} has not been played yet!")
    
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

    def __init__(self, page):
        self.page = page

    def analyse(self, parent):
        self.hendelser = []
        self.kamp = parent
        if len(self.uref_hendelser) == 0:
            self._get_events()
            
        for text in self.uref_hendelser:
            h = self._analyse(text)
            if h:
                self.hendelser.append(h)
        return self.hendelser

    def _get_events(self):
        self.uref_hendelser = []
        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(class_="section-heading no-margin--bottom", string=re.compile("^Hendelser"))
        if not f:
            return
        table = f.find_next("ul")
        for found in table.find_all("li"):
            if rt.li_class(found) == "clear-li":
                continue
            self.uref_hendelser.append(found)
    
    def get_team_sheet(self):
        hometeam = [[], []]
        awayteam = [[], []]
        document = BeautifulSoup(self.page.html.text, "html.parser")
        f = document.find(class_="section-heading", string=re.compile("^Kamptroppen"))
        if not f:
            prints.error(self, f"Failed to find 'Kamptroppen' in {self.page.url}")
            return False
        table = f.find_next("ul")
        i = 1
        for found in table.find_all("li"):
            player_name, player_url = rt.get_name_url(found)
            player = self.kamp.hjemmelag.get_player(player_name, player_url)

            if i > 11:
                hometeam[1].append(player)
            else:
                hometeam[0].append(player)
            i+=1

        table = table.find_next("ul")
        i = 1
        for found in table.find_all("li"):
            player_name, player_url = rt.get_name_url(found)
            player = self.kamp.bortelag.get_player(player_name, player_url)

            if i > 11:
                awayteam[1].append(player)
            else:
                awayteam[0].append(player)
            i+=1

        return (hometeam, awayteam)
    
    def _analyse(self, text):
        r = rt.analysis(text)
        lag = r["lag"]
        type = r["type"]
        minutt = r["minutt"]
        lenke = r["lenke"]
        navn = r["navn"]
        
        match type:
            case "Spillemål": type = Spillemaal(self.kamp, minutt, lag, (navn, lenke))
            case "Straffemål": type = Straffemaal(self.kamp, minutt, lag, (navn, lenke))
            case "Selvmål": type = Selvmaal(self.kamp, minutt, lag, (navn, lenke))
            case "Advarsel": type = GultKort(self.kamp, minutt, lag, (navn, lenke))
            case "Utvisning": type = RodtKort(self.kamp, minutt, lag, (navn, lenke))
            case "Bytte inn": type = Bytte(self.kamp, minutt, lag, (navn, lenke))
            case "Bytte ut": type = Bytte(self.kamp, minutt, lag, (navn, lenke))
            case "Advarsel for Leder": return None
            case "Utvisning for Leder": return None
            case _: prints.error(self, f"{type} not handled! {self.parent.page.url}\n{text}"); type = None; exit()
        return type # Spiller, tid, spillemål/straffe?

    def _get_team(self, str):
        if str == "home-team":
            return self.kamp.hjemmelag
        if str == "away-team":
            return self.kamp.bortelag
        prints.warning(self, f"'{str}' not valid for team")

    def __repr__(self) -> str:
        home_goals = 0
        away_goals = 0

        if self.kamp == None:
            return f"{home_goals} - {away_goals}"
        
        for item in self.hendelser:
            if (type(item) == Spillemaal or type(item) == Straffemaal): # Spillemaal / straffemaal?
                if item.team == self.kamp.hjemmelag:
                    home_goals += 1
                else:
                    away_goals += 1
            if (type(item) == Selvmaal):
                if item.team == self.kamp.hjemmelag:
                    away_goals += 1
                else:
                    home_goals += 1
        return f"{home_goals} - {away_goals}"

class Hendelse():
    def __init__(self, game, time, team):
        self.game = game
        self.time = time
        self.team = game.hjemmelag if team == "home-team" else game.bortelag
    
    def __repr__(self) -> str:
        return f"{self.time} "

class Kort(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = player
    
    def __repr__(self) -> str:
        return super().__repr__()

class GultKort(Kort):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" gult kort"

class RodtKort(Kort):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" rødt kort"

class Bytte(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player_in = player[0]
        self.player_out = player[1]
    
    def __repr__(self) -> str:
        return super().__repr__()+" bytte"

class Maal(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = player
    
    def __repr__(self) -> str:
        return super().__repr__()

class Spillemaal(Maal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" spillemål"

class Straffemaal(Maal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" straffemål"

class Selvmaal(Maal):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team, player)
    
    def __repr__(self) -> str:
        return super().__repr__()+" selvmål"

class Bane():
    def __init__(self):
        self.page = None
        self.navn = None

    def fetch_info(self):
        self.navn, self.underlag, self.banetype, self.belysning, self.lengde, self.bredde, self.driftsform, self.krets = ft.get_baneinfo(self.page.html.text)
        
    def __repr__(self) -> str:
        if self.navn == None:
            self.fetch_info()
        return self.navn

class Lag():
    def __init__(self, page):
        self.spillere = []
        self.page = page
        self.navn = None

    def print_team(self):
        self.spillere.sort()
        print(self.navn, f"({len(self.spillere)})")
        for player in self.spillere:
            print(" -",player)

    def set_navn(self):
        self.navn = self._set_navn()

    def get_player(self, name, url=False):
        if not url:
            prints.warning(self, "Player url not provided")
            exit()
        
        # Only suggest unless we have the correct url.
        for player in self.spillere:
            if url == player.url and name == player.name:
                return player
            if url == player.url:
                inp = input(f"Is {url} the url of {player.name} instead of {name}? [Enter for yes]")
                if inp == "":
                    player.name = name
                    return player
        
        player = Spiller(self, name, url)
        prints.warning(self, f"Created a new player: {name}, lacking number and position", newline=False)
        self.spillere.append(player)
        return player

    def _set_navn(self):
        if not rt.get_team_name(self.page.html.text):
            exit()
        return rt.get_team_name(self.page.html.text)

    def _set_krets(self):
        return rt.get_krets(self.html.text)
    
    def __repr__(self) -> str:
        if self.navn == None:
            self.set_navn()
        return self.navn


class Spiller():
    def __init__(self, team, name, url):
        self.team = team
        self.name = name
        self.url = url
        self.number = False
        self.position = False

    def __lt__(self, obj):
        return ((self.name) < (obj.name)) 

    def __repr__(self) -> str:
        return self.name

def main():
    hoved = Hovedside()
    prints.start("Hovedside")
    hoved.page = Page("https://www.fotball.no/turneringer/")
    prints.success()

    
    prints.start("Turneringer")
    try:
        hoved.fetch_turneringer()
        prints.success()
    except PageNotFoundError as e:
        prints.error("Turneringer", e)
        exit()
    except:
        prints.error("Turneringer")
        exit()

    prints.start("Postnord avd. 1")
    try:
        postnord1 = hoved.get_turnering("Post Nord-ligaen avd. 1")
        prints.success()
    except:
        prints.error("Postnord avd. 1")
        exit()

    prints.start("Terminliste")
    try:
        pn1_terminliste = Terminliste(postnord1)
        pn1_terminliste.page = Page(postnord1.get_termin_url())
        prints.success()
    except:
        prints.error("Terminliste")
        exit()

    prints.start("Analysere kamper")
    pn1_terminliste.fetch_kamper()
    
    for game in pn1_terminliste.kamper:
        game.analyse()
        prints.info(game, newline=False)
    prints.success()

    print("Antall lag:", len(postnord1.lag))

    for lag in postnord1.lag:
        postnord1.lag[lag].print_team()

    print(f"Antall sider hentet: {wt.fetches}")

if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
    main()
