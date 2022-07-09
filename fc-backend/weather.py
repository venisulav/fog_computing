from config import *
import requests


def getWeather( lat, lon):
  url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
  response = requests.request("GET", url, headers={}, data={}).json()
#   response = {
#     "coord": {
#         "lon": 13,
#         "lat": 53
#     },
#     "weather": [
#         {
#             "id": 802,
#             "main": "Clouds",
#             "description": "scattered clouds",
#             "icon": "03d"
#         }
#     ],
#     "base": "stations",
#     "main": {
#         "temp": 31.68,
#         "feels_like": 30.35,
#         "temp_min": 31.68,
#         "temp_max": 31.7,
#         "pressure": 1013,
#         "humidity": 29,
#         "sea_level": 1013,
#         "grnd_level": 1008
#     },
#     "visibility": 10000,
#     "wind": {
#         "speed": 2.85,
#         "deg": 101,
#         "gust": 2.6
#     },
#     "clouds": {
#         "all": 28
#     },
#     "dt": 1655991791,
#     "sys": {
#         "type": 2,
#         "id": 2042410,
#         "country": "DE",
#         "sunrise": 1655952136,
#         "sunset": 1656013079
#     },
#     "timezone": 7200,
#     "id": 2952865,
#     "name": "Banzendorf",
#     "cod": 200
# }
  return filter(response), windAlert(response["wind"])


def filter(data):
  return {
    "weatherCondition" : data["weather"][0]["main"],
    "temprature" : data["main"]["temp"],
    "humidity" : data["main"]["humidity"]
  }
  
def windAlert(wind):
  # TODO
  return False














  #   return {
  # "coord": {
  #   "lon": -122.08,
  #   "lat": 37.39
  # },
  # "weather": [
  #   {
  #     "id": 800,
  #     "main": "Clear",
  #     "description": "clear sky",
  #     "icon": "01d"
  #   }
  # ],
  # "base": "stations",
  # "main": {
  #   "temp": 282.55,
  #   "feels_like": 281.86,
  #   "temp_min": 280.37,
  #   "temp_max": 284.26,
  #   "pressure": 1023,
  #   "humidity": 100
  # },
  # "visibility": 10000,
  # "wind": {
  #   "speed": 1.5,
  #   "deg": 350
  # },
  # "clouds": {
  #   "all": 1
  # },
  # "dt": 1560350645,
  # "sys": {
  #   "type": 1,
  #   "id": 5122,
  #   "message": 0.0139,
  #   "country": "US",
  #   "sunrise": 1560343627,
  #   "sunset": 1560396563
  # },
  # "timezone": -25200,
  # "id": 420006353,
  # "name": "Mountain View",
  # "cod": 200
  # }