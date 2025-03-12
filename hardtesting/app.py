import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import serial
import threading
import time
import requests
import json

# Your API key for the weather forecast
api_key = "8142ceef20f88fdf993574705d67004a"
base_url = "http://api.openweathermap.org/data/2.5/forecast?"

# Global flag for sensor reading
sensor_running = False

# Function to read from the serial port
def read_serial():
    global ser, stop_thread
    while not stop_thread:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            lolpercent = moist_percent(int(line))
            update_percent(f"{lolpercent}%")
            update_label(line)
            update_moisttext(get_moisttext(lolpercent))
        time.sleep(0.1)

# Function to update the sensor reading label
def update_label(value):
    lbl_value.config(text=value)

#update soil description text
def update_moisttext(word):
    lbl_moisttext.config(text=word)


def get_recommendation(percent, rainfall):
    
    return

#finding soil description text; what it should be
def get_moisttext(percent):
    if percent < 10:
        return "Dry"
    elif percent < 30:
        return "Moist"
    elif percent < 50:
        return "Wet"
    else:
        return "Very Wet"

# Function to update the sensor percent label
def update_percent(value):
    lbl_percent.config(text=value)

#moisture as a percentage, idrk if this function is right
def moist_percent(value):
    percent = (value * (-1/259) + 1.78)
    percent *= 100
    percent = round(percent)
    return percent

# Function to start the serial reading thread
def start_reading():
    global ser, stop_thread
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        stop_thread = False
        threading.Thread(target=read_serial, daemon=True).start()
        lbl_status.config(text=f"Connected to /dev/ttyACM0")
    except serial.SerialException as e:
        lbl_status.config(text=f"Error: {e}")

# Function to stop the serial reading thread
def stop_reading():
    global stop_thread
    stop_thread = True
    if ser.is_open:
        ser.close()
        lbl_status.config(text="Disconnected")

# Function to get the rain prediction from the weather API
def get_rain_prediction():
    city = city_entry.get()
    if not city:
        weather_result.config(text="Please enter a city name.")
        return

    complete_url = base_url + "appid=" + api_key + "&q=" + city
    try:
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            daily_rain_predictions = []
            for forecast in x["list"]:
                date_time = forecast["dt_txt"]
                date = date_time.split(" ")[0]
                if date not in [d["date"] for d in daily_rain_predictions]:
                    rain_chance = forecast.get("rain", {}).get("3h", 0)
                    daily_rain_predictions.append({
                        "date": date,
                        "rain_chance": rain_chance
                    })
                if len(daily_rain_predictions) == 4:
                    break

            result = ""
            for prediction in daily_rain_predictions:
                result += f"Date: {prediction['date']}\n Rain Prediction (mm/3h): {prediction['rain_chance']}\n\n"
            weather_result.config(text=result)
        else:
            weather_result.config(text="City Not Found")
    except Exception as e:
        weather_result.config(text=f"Error: {e}")

# Toggle function to start or stop sensor reading and trigger rain API on start
def toggle_start_stop():
    global sensor_running
    if not sensor_running:
        if not city_entry.get().strip():
            weather_result.config(text="Please enter a city name.")
            return
        # Start sensor reading and get rain prediction
        start_reading()
        get_rain_prediction()
        toggle_btn.config(text="Stop")
        sensor_running = True
    else:
        stop_reading()
        toggle_btn.config(text="Start")
        sensor_running = False

# Create the main window
root = tk.Tk()
root.title("Neptune Systems Interface (Raspberry Pi)")

# # Sensor reading UI components
lbl_value = ttk.Label(root, text="Waiting for sensor data...", font=("SF Pro", 16, "bold"))
lbl_value.pack(pady=10)

lbl_percent = ttk.Label(root, text="Waiting for sensor data...", font=("SF Pro", 16, "bold"))
lbl_percent.pack(pady=10)

lbl_moisttext = ttk.Label(root, text="Waiting for sensor data...", font=("SF Pro", 16, "bold"))
lbl_moisttext.pack(pady=10)

lbl_status = ttk.Label(root, text="", font=("SF Pro", 10, "bold"))
lbl_status.pack(pady=10)

# Weather prediction UI components
separator = ttk.Separator(root, orient='horizontal')
separator.pack(fill='x', pady=15)

city_label = ttk.Label(root, text="Enter City for Rain Prediction:", font=("SF Pro", 12, "bold"))
city_label.pack(pady=5)

city_entry = ttk.Entry(root, width=30)
city_entry.pack(pady=5)

weather_result = ttk.Label(root, text="", font=("SF Pro", 10, "bold"), justify=tk.LEFT)
weather_result.pack(pady=10)

# Single toggle button for starting/stopping sensor reading & getting rain prediction
toggle_btn = ttk.Button(root, text="Start", command=toggle_start_stop)
toggle_btn.pack(pady=10)

root.mainloop()
