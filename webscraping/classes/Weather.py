import tools.weather_tools as wet

class Weather():
    def __init__(self, game, search=True):
        self.temp = None
        self.humidity = None
        self.precip = None
        self.preciptype = None
        self.windgust = None
        self.windspeed = None
        self.cloudcover = None
        self.conditions =None
        self.sunrise = None
        self.sunset = None
        self.game = game
        self.time = game.time
        self.date = game.date
        self.pitch = game.pitch
        if search:
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

    def insert_data(self, data):
        self.temp = data[0]
        self.humidity = data[1]
        self.precip = data[2]
        self.preciptype = data[3]
        self.windgust = data[4]
        self.windspeed = data[5]
        self.cloudcover = data[6]
        self.conditions = data[7]
        self.sunrise = data[8]
        self.sunset = data[9]

    def get_analysis_str(self):
        items = [self.temp, self.humidity, self.precip, self.preciptype,
                 self.windgust, self.windspeed, self.cloudcover, self.conditions,
                 self.sunrise, self.sunset]
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

# Future data: https://api.met.no/weatherapi/locationforecast/2.0/documentation

