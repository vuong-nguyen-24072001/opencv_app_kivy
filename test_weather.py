import pyowm
from datetime import datetime
owm = pyowm.OWM("609cbc06dacb44b7727b818875ee6923")
obs = owm.weather_at_place("Ha Noi")
weather = obs.get_weather()
wind = weather.get_temperature('celsius')["temp"]
print(int(wind))