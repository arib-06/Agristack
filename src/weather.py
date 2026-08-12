##`open meteo
import requests
url = "https://api.open-meteo.com/v1/forecast"

city = "Ludhiana"
geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

params = {"name": city}
##params is parametre required for api and the other params is our parametre which we are passing
response = requests.get(geocoding_url, params=params)
data = response.json()   #stores data as a response 
print(response.status_code) #server code 
print(response.text)       #body
latitude = data["results"][0]["latitude"]
longitude = data["results"][0]["longitude"]
weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m"
}
weather_response = requests.get(url, params=weather_params)
print(weather_response.status_code)
print(weather_response.text)
weather_data = weather_response.json()#got converted into a python dic
temperatures = weather_data["hourly"]["temperature_2m"]#nested dic access
times = weather_data["hourly"]["time"]
for time, temperature in zip(times, temperatures): #zip attaches them together
    print(time, temperature)#sync temp and times data together
# for i in range(len(times)):
#     print(times[i], temperatures[i])