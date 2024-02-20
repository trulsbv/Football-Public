class Game():
    def __init__(self, home, away, bets, result):
        self.home = home
        self.away = away
        self.bets = bets
        self.result = result   
        #print(self)
        self.betHome = float(bets[0])
        self.betDraw = float(bets[1])
        self.betAway = float(bets[2])
    
    def play(self, team, bet):
        if team != self.home and team != self.away:
            return None
        if self.home == team and self.result == 0:
            return bet*self.betHome
        if self.away == team and self.result == 2:
            return bet*self.betAway
        return 0

    def __repr__(self) -> str:
        return f"{self.home} - {self.away}: {self.result} {self.bets}"


def read_game(game):
    home = game[2]
    away = game[8]
    bets = (game[11], game[13], game[15])
    result = 1
    if int(game[5])>int(game[7]):
        result = 0
    elif int(game[5])<int(game[7]):
        result = 2
    return (Game(home, away, bets, result), home)

def read_start(filename):
    games = []
    teams = set()
    file = open(filename, 'r', encoding="UTF-8")
    
    text = file.read().split("\n")
    i = 0
    while i in range(len(text)):
        if ":" in text[i]:
            game, team = read_game(text[i:i+18])
            games.append(game)
            teams.add(team)
        i += 1
    return (games, teams)

def bet_on_team(team, bank, bet, games):
    ctr = 0
    for game in games:
        if bank == 0:
           # print(f" -> Broke after {ctr} games!")
            return 0
        if bank-bet<0:
            current_bet = bank
        else:
            current_bet = bet
        res = game.play(team, current_bet)
        if res != None:
            bank = bank-current_bet
            bank += res
            ctr += 1
    #print(f" -> Bank: {bank}")
    return bank

def read_league(league):
    games, teams = read_start(league)
    if league == "PL22_23.txrt":
        teams = ["Arsenal",
                 "Manchester City",
                 "Newcastle",
                 "Tottenham",
                 "Manchester Utd"]
    if league == "LaLiga22_23.txt":
        teams == ["Real Madrid",
                  "Atl. Madrid",
                  "Villarreal",
                  "Barcelona",
                  "Betis"]
    
    ratios = range(1, 10)
    sum = 500
    start = sum * len(teams)
    res = []
    for ratio in ratios:
        bet = sum/ratio
        profit = 0
        for team in teams:
            #print(team)
            profit += bet_on_team(team, sum, bet, games)
        res.append(round(profit-start, 2))
    print(f"   =>  {res}")
        

def start_app():
    leagues = ["Eredevise22_23.txt",
               "LaLiga22_23.txt",
               "PL22_23.txt"]
    
    ratios = range(1, 10)
    sum = 500
    for ratio in ratios:
        bet = sum/ratio
        print(f"Total: {sum}, bet: {bet}")
    for league in leagues:
        print(league)
        read_league(league)

start_app()
