import requests
import json

# Your API key here
api_key = "8142ceef20f88fdf993574705d67004a"
base_url = "http://api.openweathermap.org/data/2.5/forecast?"

# City name
city_name = input("Enter city name : ")
complete_url = base_url + "appid=" + api_key + "&q=" + city_name

response = requests.get(complete_url)
x = response.json()

if x["cod"] != "404":
    # List to store daily forecasts
    daily_forecasts = []

    # Iterate through the forecast list
    for forecast in x["list"]:
        # Extract date and time
        date_time = forecast["dt_txt"]
        # Extract date only
        date = date_time.split(" ")[0]

        # Check if the date is already in the daily_forecasts list
        if date not in [d["date"] for d in daily_forecasts]:
            # Extract weather data
            temp = forecast["main"]["temp"]
            pressure = forecast["main"]["pressure"]
            humidity = forecast["main"]["humidity"]
            description = forecast["weather"][0]["description"]

            # Extract chance of rain if available
            rain_chance = forecast.get("rain", {}).get("3h", 0)  # Rain volume for the last 3 hours

            # Append the daily forecast
            daily_forecasts.append({
                "date": date,
                "temp": temp,
                "pressure": pressure,
                "humidity": humidity,
                "description": description,
                "rain_chance": rain_chance
            })

        # Stop after 4 days
        if len(daily_forecasts) == 4:
            break

    # Print the 4-day weather forecast
    for forecast in daily_forecasts:
        print(f"Date: {forecast['date']}")
        print(f" Temperature (in kelvin unit) = {forecast['temp']}")
        print(f" Atmospheric pressure (in hPa unit) = {forecast['pressure']}")
        print(f" Humidity (in percentage) = {forecast['humidity']}")
        print(f" Description = {forecast['description']}")
        print(f" Rain chance (in mm) = {forecast['rain_chance']}\n")

else:
    print(" City Not Found ")
