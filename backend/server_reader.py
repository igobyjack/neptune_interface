import asyncio
import websockets
import serial
import json
from datetime import datetime

# Configuration
HOST = "0.0.0.0"  # Bind to all network interfaces
PORT = 8765       # WebSocket port
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600  # Change if your device uses a different baud rate

# A set to keep track of connected clients
connected_clients = set()

# Flag to control reading from serial
running = True

async def send_to_clients(data):
    """Send data to all connected WebSocket clients"""
    if not connected_clients:
        return
    
    # Create a formatted message to send
    message = data.strip()
    
    # Send to all connected clients
    websockets_tasks = []
    for websocket in connected_clients:
        websockets_tasks.append(asyncio.create_task(websocket.send(message)))
    
    if websockets_tasks:
        await asyncio.gather(*websockets_tasks, return_exceptions=True)
        print(f"Sent to {len(connected_clients)} client(s): {message}")

async def read_serial():
    """Read data from serial port and send to all WebSocket clients"""
    print(f"Opening serial port {SERIAL_PORT} at {BAUD_RATE} baud")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Serial port opened successfully")
        
        while running:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='replace')
                await send_to_clients(data)
            else:
                # Small sleep to prevent CPU hogging when no data
                await asyncio.sleep(0.01)
                
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")

async def handle_websocket(websocket):
    """Handle WebSocket client connections"""
    connected_clients.add(websocket)
    client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"Client connected: {client_info}")
    
    try:
        # Keep the connection alive and handle any incoming messages
        async for message in websocket:
            print(f"Received from {client_info}: {message}")
            # You can process incoming messages here if needed
    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed for {client_info}")
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected: {client_info}")

async def main():
    """Main function to start the WebSocket server and serial reader"""
    # Start the serial reading task
    serial_task = asyncio.create_task(read_serial())
    
    # Start the WebSocket server
    server = await websockets.serve(handle_websocket, HOST, PORT)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")
    
    try:
        # Keep the server running
        await server.wait_closed()
    finally:
        # Cleanup
        global running
        running = False
        await serial_task

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")