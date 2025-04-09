import asyncio
import websockets
import random
import json
import time

# Configuration
HOST = "localhost"
PORT = 8765
INTERVAL = 2  # Interval in seconds to send data

async def send_moisture_data():
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        while True:
            # Generate random moisture data
            moisture_value = random.randint(0, 1023)
            moisture_percent = (moisture_value * (-1/259) + 1.78) * 100
            moisture_percent = round(moisture_percent, 2)
            
            # Create a JSON message
            message = json.dumps({
                "value": moisture_value,
                "percent": moisture_percent
            })
            
            # Send the message to the WebSocket server
            await websocket.send(message)
            print(f"Sent: {message}")
            
            # Wait for the specified interval
            await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(send_moisture_data())
    except KeyboardInterrupt:
        print("Simulation stopped by user")
