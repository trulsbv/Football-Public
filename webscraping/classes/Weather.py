import tools.weather_tools as wet

class Weather():
    def __init__(self, game):
        self.game = game
        self.time = game.time
        self.date = game.date
        self.pitch = game.pitch
        self.data = wet.get_weather_data(self.pitch, self.date, self.time) # should be a map or something
        if self.data:
            self.handle_data()

    def handle_data(self):
        self.temp = round((int(self.data["currentConditions"]["temp"]) - 32) * 5/9, 1)
        self.humidity = self.data["currentConditions"]["humidity"] # % air saturation
        self.precip = self.data["currentConditions"]["precip"] # how much rain/hail/snow
        self.preciptype = self.data["currentConditions"]["preciptype"] # type of precip
        self.windgust = self.data["currentConditions"]["windgust"]
        self.windspeed = self.data["currentConditions"]["windspeed"]
        self.cloudcover = self.data["currentConditions"]["cloudcover"]
        self.conditions = self.data["currentConditions"]["conditions"] # String
        self.sunrise = self.data["currentConditions"]["sunrise"] # time
        self.sunset = self.data["currentConditions"]["sunset"] # time

    def get_analysis_str(self):
        items = [self.temp, self.humidity, self.precip, self.preciptype,
                 self.windgust, self.windspeed, self.cloudcover, self.conditions,
                 self.sunrise, self.sunset]
        s = ""

        f = True
        for item in items:
            if not item:
                continue
            if not f:
                s += ","
            f = False
            s += str(item)

        return s

# Future data: https://api.met.no/weatherapi/locationforecast/2.0/documentation

