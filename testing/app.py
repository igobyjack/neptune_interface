import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import serial
import threading
import time
import json
import asyncio
import websockets

# Global flag for sensor reading
sensor_running = False

# WebSocket server address
websocket_address = "ws://localhost:8765"

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
            asyncio.run(send_data_via_websocket(line, lolpercent))
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

# Function to send data via WebSocket
async def send_data_via_websocket(value, percent):
    async with websockets.connect(websocket_address) as websocket:
        data = json.dumps({"value": value, "percent": percent})
        await websocket.send(data)

# Function to handle WebSocket connections
async def websocket_handler(websocket, path):
    while True:
        try:
            message = await websocket.recv()
            print(f"Received message: {message}")
        except websockets.ConnectionClosed:
            print("Connection closed")
            break

# Start WebSocket server
def start_websocket_server():
    start_server = websockets.serve(websocket_handler, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

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

# Single toggle button for starting/stopping sensor reading & getting rain prediction
toggle_btn = ttk.Button(root, text="Start", command=toggle_start_stop)
toggle_btn.pack(pady=10)

# Start WebSocket server in a separate thread
threading.Thread(target=start_websocket_server, daemon=True).start()

root.mainloop()
