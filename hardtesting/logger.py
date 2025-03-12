# For testing purposes, designed to gain a read on how the moisuture data evolves. 

import os
import tkinter as tk
from tkinter import ttk
import serial
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

def log_moisture(serial_port='/dev/ttyACM0', baud_rate=9600):
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        ser.reset_input_buffer()  # Clear any buffered data
    except Exception as e:
        update_status(f"Serial error: {e}")
        return

    # Use moisturelog.csv in the neptune_interface folder.
    log_file = os.path.join(os.path.dirname(__file__), "moisturelog.csv")
    update_status(f"Logging moisture data to {log_file}.")

    while logging_running:
        # Read until a valid data line is received
        line = ""
        while logging_running and not line:
            line = ser.readline().decode('utf-8').strip()

        if not logging_running:
            break

        try:
            sensor_value = int(line)
            percent = moist_percent(sensor_value)
            level = get_moisttext(percent)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, percent, level])
            update_status(f"{timestamp} - {percent}%, {sensor_value}, ({level})")
        except ValueError:
            update_status("Unable to parse sensor value.")

        # 5 minutes between logging (300 seconds)
        for _ in range(300):
            if not logging_running:
                break
            time.sleep(1)
    ser.close()
    update_status("Session terminated.")

def start_logging():
    global logging_running, logging_thread
    logging_running = True
    logging_thread = threading.Thread(target=log_moisture, daemon=True)
    logging_thread.start()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_logging():
    global logging_running
    logging_running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Build Tkinter UI
root = tk.Tk()
root.title("Moisture Logger (Raspberry Pi)")

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
