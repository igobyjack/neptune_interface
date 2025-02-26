# For testing purposes, designed to gain a read on how the moisuture data evolves. 

import os
import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import threading
import time
import csv
import datetime

def moist_percent(value):
    percent = (value * (-1/259) + 1.78)
    percent *= 100
    return round(percent)

def get_moisttext(percent):
    if percent < 10:
        return "Dry"
    elif percent < 30:
        return "Moist"
    elif percent < 50:
        return "Wet"
    else:
        return "Very Wet"

def update_status(message):
    status_label.config(text=message)
    print(message)

def log_moisture():
    log_file = os.path.join(os.path.dirname(__file__), "moisturelog.csv")
    update_status(f"Logging moisture data to {log_file}.")

    while logging_running:
        moisture_value = GPIO.input(17)
        percent = moist_percent(moisture_value)
        level = get_moisttext(percent)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, percent, level])
        update_status(f"{timestamp} - {percent}%, {moisture_value}, ({level})")

        # 5 minutes between logging (300 seconds)
        for _ in range(300):
            if not logging_running:
                break
            time.sleep(1)
    update_status("Session terminated.")

def start_logging():
    global logging_running, logging_thread
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN)
    logging_running = True
    logging_thread = threading.Thread(target=log_moisture, daemon=True)
    logging_thread.start()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_logging():
    global logging_running
    logging_running = False
    GPIO.cleanup()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Build Tkinter UI
root = tk.Tk()
root.title("Moisture Logger")

# Start and Stop buttons
start_button = ttk.Button(root, text="Start Logging", command=start_logging)
start_button.pack(pady=5)
stop_button = ttk.Button(root, text="Stop Logging", command=stop_logging, state=tk.DISABLED)
stop_button.pack(pady=5)

# Status label for logging messages
status_label = ttk.Label(root, text="Status messages will appear here.", wraplength=300)
status_label.pack(pady=10)

logging_running = False
logging_thread = None

root.mainloop()
