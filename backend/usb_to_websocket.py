import serial
import asyncio
import websockets

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
WEBSOCKET_URI = 'ws://localhost:8765'

async def read_from_serial_and_send():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    # Establish connection with the WebSocket server
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        print("Connected to WebSocket server.")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                await websocket.send(data)
                print(f"Sent: {data}")

async def main():
    await read_from_serial_and_send()

if __name__ == '__main__':
    asyncio.run(main())