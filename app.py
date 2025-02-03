import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time


# Function to read from the serial port
def read_serial():
    global ser, stop_thread
    while not stop_thread:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            lolpercent = moist_percent(int(line))

            #update % value 
            update_percent(f"{lolpercent}%")

            #update soil status text
            # soil_status(lolpercent)

            #update the actual reading
            update_label(line)

        time.sleep(0.1)

# Function to update the label in the UI
def update_label(value):
    lbl_value.config(text=value)

def update_percent(value):
    lbl_percent.config(text=value)

def moist_percent(value):
    percent = (value * (-1/259) + 1.78)
    percent *= 100
    percent = round(percent)
    return percent

# def soil_status(value):
#     if value < 40 or value > 20 :
#         update_status("GOOD")
#         return
#     elif value < 20:
#         update_status("DRY")
#         return
#     else:
#         update_status("WET")
#         return

        
# def update_status(status):
#     #TODO: IMPLEMENT WITH STATUS TEXT
#     if status == "DRY":
#         lbl_text.config(text="Soil is dry")
#     if status == "GOOD":
#         lbl_text.config(text="Soil is good")
#     if status == "WET":
#         lbl_text.config(text="Soil is oversaturated")
    

# Function to start the serial reading thread
def start_reading():
    global ser, stop_thread
    
    # Get the selected COM port
    com_port = com_var.get()
    try:
        ser = serial.Serial(com_port, 9600, timeout=1)
        stop_thread = False
        threading.Thread(target=read_serial, daemon=True).start()
        lbl_status.config(text=f"Connected to {com_port}")
    except serial.SerialException as e:
        lbl_status.config(text=f"Error: {e}")

# Function to stop the serial reading thread
def stop_reading():
    global stop_thread
    stop_thread = True
    if ser.is_open:
        ser.close()
        lbl_status.config(text="Disconnected")

# Function to list all available COM ports
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Create the main window
root = tk.Tk()
root.title("Neptune Systems Interface (BY JACK)")

# Create a label to display the value
lbl_value = ttk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
lbl_value.pack(pady=20)

#create a label to display the percent
lbl_percent = ttk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
lbl_percent.pack(pady=20)

#create label for soil status
# lbl_text = ttk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
# lbl_text.pack(pady=20)

# Create a dropdown menu to select the COM port
com_var = tk.StringVar()
com_ports = list_serial_ports()
com_var.set(com_ports[0] if com_ports else "No COM ports found")
com_menu = ttk.OptionMenu(root, com_var, *com_ports)
com_menu.pack(pady=10)

# Create start and stop buttons
btn_start = ttk.Button(root, text="Start", command=start_reading)
btn_start.pack(side=tk.LEFT, padx=10, pady=10)

btn_stop = ttk.Button(root, text="Stop", command=stop_reading)
btn_stop.pack(side=tk.RIGHT, padx=10, pady=10)

# Create a label to display the connection status
lbl_status = ttk.Label(root, text="", font=("Helvetica", 10))
lbl_status.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()