import requests
import json

api_key = "8142ceef20f88fdf993574705d67004a"

base_url = "http://api.openweathermap.org/data/2.5/weather?"

city_name = input("Enter city name : ")

complete_url = base_url + "appid=" + api_key + "&q=" + city_name
response = requests.get(complete_url)
 
# json method of response object 
# convert json format data into
# python format data
x = response.json()
 
# Now x contains list of nested dictionaries
# Check the value of "cod" key is equal to
# "404", means city is found otherwise,
# city is not found
if x["cod"] != "404":
 
    # store the value of "main"
    # key in variable y
    y = x["main"]
 
    z = x["weather"]
    
    # store the value corresponding
    # to the "temp" key of y
    current_temperature = y["temp"]
 
    # store the value corresponding
    # to the "pressure" key of y
    current_pressure = y["pressure"]
 
    # store the value corresponding
    # to the "humidity" key of y
    current_humidity = y["humidity"]

    rain = z["main"]

    # store the value of "weather"
    # key in variable z
 
    # store the value corresponding 
    # to the "description" key at 
    # the 0th index of z
    weather_description = z[0]["description"]
 

    print(str(rain))
    # print following values
    # print(" Temperature (in kelvin unit) = " +
    #                 str(current_temperature) +
    #       "\n atmospheric pressure (in hPa unit) = " +
    #                 str(current_pressure) +
    #       "\n humidity (in percentage) = " +
    #                 str(current_humidity) +
    #       "\n description = " +
    #                 str(weather_description))
 
else:
    print(" City Not Found ")
