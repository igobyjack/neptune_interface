import os
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
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

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def update_status(message):
    status_label.config(text=message)
    print(message)

def log_moisture(serial_port, baud_rate=9600):
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
    com_port = com_var.get()
    if not com_port:
        update_status("Please select a COM port.")
        return
    logging_running = True
    logging_thread = threading.Thread(target=log_moisture, args=(com_port,), daemon=True)
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
root.title("Moisture Logger")

# COM Port selection
com_var = tk.StringVar()
ports = list_serial_ports()
com_var.set(ports[0] if ports else "")
com_label = ttk.Label(root, text="Select COM Port:")
com_label.pack(pady=5)
com_menu = ttk.OptionMenu(root, com_var, com_var.get(), *ports)
com_menu.pack(pady=5)

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