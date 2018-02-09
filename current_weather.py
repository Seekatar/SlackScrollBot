""" get current weather
"""
import os
import threading
import requests
from processor import Runner

class CurrentWeather(Runner):
    """ get the current weather
    """

    def __init__(self, zip_code, api_key, frequency):
        super(CurrentWeather, self).__init__("CurrentWeather")
        self.url = "http://api.openweathermap.org/data/2.5/weather?zip="+zip_code+\
                 ",us&appid="+api_key+"&units=Imperial"
        self.frequency = frequency
        self.lock = threading.Lock()
        self.temperature = 0

    def get_temperature(self):
        """ get recent temperature
        """
        with self.lock:
            return self.temperature

    def process(self):
        """ run it
        """
        result = requests.get(self.url)
        with self.lock:
            self.temperature = result.json()["main"]["temp"]
        return self.frequency, False

if __name__ == "__main__":
    # pylint: disable=C0103
    key = os.environ["SLACK_BOT_WEATHER_KEY"]
    cw = CurrentWeather("30022", key, 60)
    cw.process()
    print("Current temp is", cw.get_temperature())
