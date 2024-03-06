import tools.weather_tools as wet


class Weather:
    def __init__(self, game, search=True):
        self.temp = None
        self.humidity = None
        self.precip = None
        self.preciptype = None
        self.windgust = None
        self.windspeed = None
        self.cloudcover = None
        self.conditions = None
        self.sunrise = None
        self.sunset = None
        self.game = game
        self.time = game.time
        self.date = game.date
        self.pitch = game.pitch
        if search:
            self.data = wet.get_weather_data(
                self.pitch, self.date, self.time
            )  # should be a map or something
            if self.data:
                self.handle_data()

    def handle_data(self):
        self.temp = round((int(self.data["currentConditions"]["temp"]) - 32) * 5 / 9, 1)
        self.humidity = self.data["currentConditions"]["humidity"]  # % air saturation
        self.precip = self.data["currentConditions"][
            "precip"
        ]  # how much rain/hail/snow
        self.preciptype = (
            None
            if not self.data["currentConditions"]["preciptype"]
            else ";".join(map(str, self.data["currentConditions"]["preciptype"]))
        )  # type of precip
        self.windgust = self.data["currentConditions"]["windgust"]
        self.windspeed = self.data["currentConditions"]["windspeed"]
        self.cloudcover = self.data["currentConditions"]["cloudcover"]
        self.conditions = self.data["currentConditions"]["conditions"].replace(
            ",", ";"
        )  # String
        self.sunrise = self.data["currentConditions"]["sunrise"]  # time
        self.sunset = self.data["currentConditions"]["sunset"]  # time

    def insert_data(self, data):
        self.temp = data["temp"]
        self.humidity = data["humidity"]
        self.precip = data["precipitation"]
        self.preciptype = data["precipitation_type"]
        self.windgust = data["windgust"]
        self.windspeed = data["windspeed"]
        self.cloudcover = data["cloudcover"]
        self.conditions = data["conditions"]
        self.sunrise = data["sunrise"]
        self.sunset = data["sunset"]

    def get_analysis(self):
        return {
            "temp": self.temp,
            "humidity": self.humidity,
            "precipitation": self.precip,
            "precipitation_type": self.preciptype,
            "windgust": self.windgust,
            "windspeed": self.windspeed,
            "cloudcover": self.cloudcover,
            "conditions": self.conditions,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
        }


# Future data: https://api.met.no/weatherapi/locationforecast/2.0/documentation
