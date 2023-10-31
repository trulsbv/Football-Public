from bs4 import BeautifulSoup
from classes.Page import Page
from datetime import date, datetime
from errors.PageNotFoundError import PageNotFoundError
import os
import re
import settings
import sys
import tools.file_tools as ft
import tools.prints as prints
import tools.regex_tools as rt
import tools.web_tools as wt

serier=["Eliteserien"]

class Hovedside():
    def __init__(self):
        self.turneringer = []
        self.page = None
    
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
    def __init__(self, parent):
        self.hovedside = parent
        self.terminliste = None
        self.lag = {}
        self.analyser = None
        self.page = None

    def get_termin_url(self):
        document = BeautifulSoup(self.page.html.text, "html.parser")
        ml = document.find(class_="match-list")
        btn = ml.find_next(class_="btn btn--default")
        return rt.find_urls(str(btn))[0]
    
    def create_lag(self, navn, url):
        if not navn in self.lag:
            self.lag[navn] = Lag(Page(url))
            # Dette er dust, må ha en egen funksjon for dette din dritt
            self.lag[navn].navn = self.lag[navn]._set_navn()
        return self.lag[navn]
        

class Terminliste():
    def __init__(self, parent):
        self.turnering = parent
        self.kamper = []
        self.page = None

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
            try:
                runde, dato, dag, tid, _, _hjemmelag, _resultat, _bortelag, _bane, kampnr = cells_text
            except:
                runde, dato, dag, tid, _, _hjemmelag, _resultat, _bortelag, _bane, kampnr, _live = cells_text
            
            hjemmelag = self.turnering.create_lag(_hjemmelag, urls[1])
            bortelag = self.turnering.create_lag(_bortelag, urls[3])
            hendelser = Hendelser(Page(urls[2]))
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
        self.hendelser = []

        self.hometeam = None
        self.awayteam = None
        self.spectators = None
        self.winner = None
        self.score = None

    def _is_played(self):
        return datetime.strptime(self.dato, "%d.%m.%Y") < current_date
    
    def analyse(self):
        if self._is_played():
            result = self.resultat.get_team_sheet(self)
            self.hendelser = self.resultat.analyse()
            if result:
                self.hometeam, self.awayteam = result
            self.score = self.resultat.get_result()
            if self.score[0] > self.score[1]:
                self.winner = self.hjemmelag
            elif self.score[0] < self.score[1]:
                self.winner = self.bortelag
        else:
            prints.warning(f"{self.hjemmelag} - {self.bortelag} has not been played yet!")
    
    def __repr__(self) -> str:
        s = f"{self.runde} ({self.dag} {self.dato} kl. {self.tid}) {self.hjemmelag} "
        if datetime.strptime(self.dato, "%d.%m.%Y") < current_date:
            s += f"{self.resultat} "
        else:
            s += " -  "
        s += f"{self.bortelag}, {self.bane} ({self.kampnummer})"
        if self.spectators:
            s += f" - {self.spectators} attended"
        return s

class Hendelser():
    def __init__(self, page):
        self.page = page
        self.hendelser = []
        self.uref_hendelser = []
        self.kamp = None

    def analyse(self):
        self.hendelser = []
        if len(self.uref_hendelser) == 0:
            self._get_events()
            
        for text in self.uref_hendelser:
            h = self._analyse(text)
            if h:
                self.hendelser.append(h)
            elif h == False:
                if input("\nRestart? Press [Enter] for accept") == "":
                    prints.RESTART()
                    os.execv(sys.executable, ['python'] + sys.argv)

        document = BeautifulSoup(self.page.html.text, "html.parser")
        gi = document.find(class_="grid__item grid__item match__arenainfo one-third margin-top--two right-bordered mobile--one-whole")
        if gi:
            self.kamp.spectators = rt.get_spectators(gi)
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
    
    def get_team_sheet(self, parent):
        self.kamp = parent
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
                player.matches["benched"].append(self.kamp)
                hometeam[1].append(player)
            else:
                player.matches["started"].append(self.kamp)
                hometeam[0].append(player)
            i+=1

        table = table.find_next("ul")
        i = 1
        for found in table.find_all("li"):
            player_name, player_url = rt.get_name_url(found)
            player = self.kamp.bortelag.get_player(player_name, player_url)

            if i > 11:
                player.matches["benched"].append(self.kamp)
                awayteam[1].append(player)
            else:
                player.matches["started"].append(self.kamp)
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

        lag = self.kamp.hjemmelag if "home-team" == lag else self.kamp.bortelag
        match type:
            case "Spillemål": type = Spillemaal(self.kamp, minutt, lag, (navn, lenke))
            case "Straffemål": type = Straffemaal(self.kamp, minutt, lag, (navn, lenke))
            case "Selvmål": type = Selvmaal(self.kamp, minutt, lag, (navn, lenke))
            case "Advarsel": type = GultKort(self.kamp, minutt, lag, (navn, lenke))
            case "Utvisning": type = RodtKort(self.kamp, minutt, lag, (navn, lenke))
            case "Bytte inn": type = Bytte(self.kamp, minutt, lag, navn)
            case "Bytte ut": type = Bytte(self.kamp, minutt, lag, navn)
            case "Advarsel for Leder": return None
            case "Utvisning for Leder": return None
            case "Kampen er slutt": return None
            case _: prints.error(self, f"\"{type}\" not handled! {self.page.url}\n{text}"); return False
        return type # Spiller, tid, spillemål/straffe?

    def _get_team(self, str):
        if str == "home-team":
            return self.kamp.hjemmelag
        if str == "away-team":
            return self.kamp.bortelag
        prints.warning(self, f"'{str}' not valid for team")

    def get_result(self):
        home_goals = 0
        away_goals = 0

        if self.kamp == None:
            return
        
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
        return (home_goals, away_goals)
        

    def __repr__(self) -> str:
        home_goals, away_goals = self.get_result()
        return f"{home_goals} - {away_goals}"

class Hendelse():
    def __init__(self, game, time, team):
        self.game = game
        self.time = time
        self.team = team
    
    def __repr__(self) -> str:
        return f"{self.time} "

class Kort(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = team.get_player(player[0], player[1], warning=True)
        self.player.events.append(self)
    
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
        _out, _in = player
        super().__init__(game, time, team)
        self.player_in = team.get_player(_in[0], _in[1], warning=True)
        self.player_out = team.get_player(_out[0], _out[1], warning=True)
        self.player_in.matches["sub in"] = {game: self}
        self.player_out.matches["sub out"] = {game: self}
        self.current_score = game.resultat.get_result()
    
    def __repr__(self) -> str:
        return super().__repr__()+" bytte"

class Maal(Hendelse):
    def __init__(self, game, time, team, player):
        super().__init__(game, time, team)
        self.player = team.get_player(player[0], player[1], warning=True)
        self.player.events.append(self)
    
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
        self.number = None
        self.position = None
        self._init_players()

    def print_team(self):
        self.spillere.sort()
        a = (55-len(self))
        prints.header(f"{self} ({len(self.spillere)}){' '*a}(ST, SI, SO, BE)")
        for player in self.spillere:
            prints.row(f"   {player.print_row()}")

    def set_navn(self):
        self.navn = self._set_navn()

    def get_player_influence(self):
        for spiller in self.spillere:
            result = spiller.results_while_playing()
            output = []
            for res in result:
                if res:
                    game, results = res
                    pre, post = results
                    home_pre, away_pre = pre
                    home_post, away_post = post
                    for_goals = 0
                    against_goals = 0

                    if game.hjemmelag == self:
                        for_goals = home_post - home_pre
                        against_goals = away_post - away_pre

                    elif game.bortelag == self:
                        for_goals = away_post - away_pre
                        against_goals = home_post - home_pre
                    
                    total_goals = for_goals-against_goals
                    print(f"   {home_pre}-{away_pre} -> {home_post}-{away_post} | for: {for_goals}, agst: {against_goals}, tot: {total_goals}")

    def get_player(self, name, url=False, warning=False):
        if not url:
            prints.warning(self, "Player url not provided")
            exit()

        
        # Only suggest unless we have the correct url.
        for player in self.spillere:
            if url == player.url:
                return player
            if name == player.name:
                input(f"HÆÆÆÆ: {url} !=??? {player.url}")
        if warning:
            prints.warning(self, f"Created a new player: {name}, lacking number and position")

        player = Spiller(self, name, url)
        self.spillere.append(player)
        return player
    
    def _init_players(self):
        url = self.page.url.replace("hjem", "spillere")
        players = Page(url)
        document = BeautifulSoup(players.html.text, "html.parser")
        ul = document.find("section")
        for found in ul.find_all("li"):
            number, link, name, position = rt.get_player_info(found)
            player = self.get_player(name, link)
            player.number = number
            player.position = position

    def _set_navn(self):
        if not rt.get_team_name(self.page.html.text):
            exit()
        return rt.get_team_name(self.page.html.text)

    def _set_krets(self):
        return rt.get_krets(self.html.text)
    
    def __len__(self):
        return len(self.navn.title().replace("Menn Senior ", ""))
    
    def __repr__(self) -> str:
        if self.navn == None:
            self.set_navn()
        return self.navn.title().replace("Menn Senior ", "")

    def __eq__(self, other) -> bool:
        if type(other) == str:
            return self.navn.title().replace("Menn Senior ", "") == other
        if type(other) == Lag:
            return self.navn == other.navn

class Spiller():
    def __init__(self, team, name, url):
        self.team = team
        self.name = name
        self.url = url
        self.number = False
        self.position = False
        self.matches = {"started": [], "sub in": {}, "sub out": {}, "benched": []}
        self.events = []
    
    def iterate_events(self, event_type):
        types = []
        return_types = []
        if event_type == Maal:
            types.append(Selvmaal)
            types.append(Spillemaal)
            types.append(Straffemaal)
        elif event_type == Kort:
            types.append(RodtKort)
            types.append(GultKort)
        else:
            types.append(event_type)

        for item in self.events:
            if type(item) in types:
                return_types.append(item)
        return return_types

    def results_while_playing(self):
        results_while_playing = [] # <-- (before, after)
        games = self.matches["started"]
        for game in games:
            cur = (0, 0)
            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
            else:
                fin = game.resultat.get_result()
            results_while_playing.append((game, (cur, fin)))
        
        for game in self.matches["sub in"]:
            cur = self.matches["sub in"][game].current_score
            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
            else:
                fin = game.resultat.get_result()
            results_while_playing.append((game, (cur, fin)))        
        return results_while_playing
    
    def get_goals(self):
        goals = self.iterate_events(Maal)
        goal_counter = 0
        for g in goals:
            if type(g) == Selvmaal:
                goal_counter -= 1
            else:
                goal_counter += 1
        return goal_counter

    def get_num_games_result(self):
        win = 0
        draw = 0
        loss = 0
        for game in self.matches["started"]:
            if game.winner == self.team:
                win += 1
            elif game.winner == None:
                draw += 1
            else:
                loss += 1

        for sub in self.matches["sub in"]:
            if self.matches["sub in"][sub].game.winner == self.team:
                win += 1
            elif self.matches["sub in"][sub].game.winner == None:
                draw += 1
            else:
                loss += 1
        
        if win+draw+loss==0:
            return None
        
        return (win, draw, loss)

    def __lt__(self, obj):
        return ((self.name) < (obj.name)) 
    
    def __repr__(self) -> str:
        return self.name

    def print_row(self) -> str:
        s = ""
        if self.position:
            s += f"{self.position.upper():>8}, "
        else:
            s += "          "

        split = self.name.split(" ")    
        navn = f"{split[0]} ... {split[-1]}" if len(self.name.split(" ")) > 4 and len(self.name) > 40 else self.name 
        s += f"{navn:>40}"
        if self.number:
            s += f", {self.number:>2} - "
        else:
            s += "       "
        s += f"({len(self.matches['started']):>2}, {len(self.matches['sub in']):>2}, {len(self.matches['sub out']):>2}, {len(self.matches['benched']):>2})"
        s += f" - {self.get_goals():>2} goals"
        res = self.get_num_games_result()
        if res:
            win, draw, loss = res
            sum = win+draw+loss
            win_percent = round((win/sum)*100, 2)
            draw_percent = round((draw/sum)*100, 2)
            loss_percent = round((loss/sum)*100, 2)
            s+= f" ({win} {win_percent}%, {draw} {draw_percent}%, {loss} {loss_percent}%)"
        return s

def main():
    #search = "Eliteserien"
    search = "Post Nord-ligaen avd. 1"
    #search = "Post Nord-ligaen avd. 2"
    #search = "Toppserien"
    #search = "Norsk Tipping-Ligaen avd. 2"
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

    prints.start(search)
    try:
        liga = hoved.get_turnering(search)
        prints.success()
    except:
        prints.error(search)
        exit()
    liga.get_termin_url()

    prints.start("Terminliste")
    try:
        terminliste = Terminliste(liga)
        terminliste.page = Page(liga.get_termin_url())
        prints.success()
    except:
        prints.error("Terminliste")
        exit()

    prints.start("Analysere kamper")
    terminliste.fetch_kamper()
    
    for game in terminliste.kamper:
        game.analyse()
        prints.info(game, newline=False)
    prints.success()

    print("Antall lag:", len(liga.lag))

    for lag in liga.lag:
        print(lag)
        liga.lag[lag].print_team()
        liga.lag[lag].get_player_influence()
            
        prints.whiteline()

    print(f"Antall sider hentet: {wt.fetches}")

if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-log":
        ft.clear_log()
        log_bool = True
        
    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        current_date = datetime.strptime("11.04.2023", "%d.%m.%Y")
    else:
        current_date = datetime.today()
    main()
