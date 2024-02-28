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
        self.preciptype = None if not self.data["currentConditions"]["preciptype"] else ";".join(map(str, self.data["currentConditions"]["preciptype"])) # type of precip
        self.windgust = self.data["currentConditions"]["windgust"]
        self.windspeed = self.data["currentConditions"]["windspeed"]
        self.cloudcover = self.data["currentConditions"]["cloudcover"]
        self.conditions = self.data["currentConditions"]["conditions"].replace(",", ";") # String
        self.sunrise = self.data["currentConditions"]["sunrise"] # time
        self.sunset = self.data["currentConditions"]["sunset"] # time

    def insert_data(self, data):
        self.temp =         data[0] if data[0] != "None" else None
        self.humidity =     data[1] if data[1] != "None" else None
        self.precip =       data[2] if data[2] != "None" else None
        self.preciptype =   data[3] if data[3] != "None" else None
        self.windgust =     data[4] if data[4] != "None" else None
        self.windspeed =    data[5] if data[5] != "None" else None
        self.cloudcover =   data[6] if data[6] != "None" else None
        self.conditions =   data[7] if data[7] != "None" else None
        self.sunrise =      data[8] if data[8] != "None" else None
        self.sunset =       data[9] if data[9] != "None" else None

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
                s+="None,"
            s += str(item)

        return s

# Future data: https://api.met.no/weatherapi/locationforecast/2.0/documentation

