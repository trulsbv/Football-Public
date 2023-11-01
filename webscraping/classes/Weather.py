import tools.weather_tools as wet

class Weather():
    def __init__(self, game):
        self.game = game
        self.time = game.time
        self.date = game.date
        self.pitch = game.pitch
        self.data = wet.get_weather_data(self.pitch, self.date, self.time) # should be a map or something

# Future data: https://api.met.no/weatherapi/locationforecast/2.0/documentation

