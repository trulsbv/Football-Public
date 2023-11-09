from classes.Event import (OwnGoal, PenaltyGoal, PlayGoal, RedCard,
                   YellowCard, Goal, Booking)
class Player():
    def __init__(self, team, name, url):
        self.team = team
        self.name = name
        self.url = url
        self.number = False
        self.position = False
        self.matches = {"started": [], "sub in": {}, "sub out": {}, "benched": []}
        self.events = []
        self.influence = {}
    
    def iterate_events(self, event_type):
        types = []
        return_types = []
        if event_type == Goal:
            types.append(OwnGoal)
            types.append(PlayGoal)
            types.append(PenaltyGoal)
        elif event_type == Booking:
            types.append(RedCard)
            types.append(YellowCard)
        else:
            types.append(event_type)

        for item in self.events:
            if type(item) in types:
                return_types.append(item)
        return return_types

    def results_while_playing(self):
        results_while_playing = [] # <-- (game, (before, after, end), (in, out))
        for game in self.matches["started"]:
            cur = (0, 0)
            in_time = 0
            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.result.get_result()
                out_time = 90
            end = game.result.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))

        for game in self.matches["sub in"]:
            cur = self.matches["sub in"][game].current_score
            in_time = self.matches["sub in"][game].time

            if game in self.matches["sub out"]:
                fin = self.matches["sub out"][game].current_score
                out_time = self.matches["sub out"][game].time
            else:
                fin = game.result.get_result()
                out_time = 90
            end = game.result.get_result()
            results_while_playing.append((game, (cur, fin, end), (in_time, out_time)))

        return results_while_playing
    
    def get_goals(self):
        goals = self.iterate_events(Goal)
        goal_counter = 0
        for g in goals:
            if type(g) == OwnGoal:
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
    
    def __hash__(self) -> int:
        return hash(self.url)
    
    def __eq__(self, other):
        if type(other) == Player:
            return self.url == other.url
        if type(other) == str:
            return self.name == other
        
    def get_analysis_str(self):
        return self.url

    def print_row(self) -> str:
        s = ""
        if self.position:
            s += f"{self.position.upper():>8}, "
        else:
            s += "          "

        split = self.name.split(" ")    
        name = f"{split[0]} ... {split[-1]}" if len(self.name.split(" ")) > 4 and len(self.name) > 40 else self.name 
        s += f"{name:>40}"
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
