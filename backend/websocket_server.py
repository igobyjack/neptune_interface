import asyncio
import websockets

# Bind to all network interfaces so that other devices can connect
HOST = "0.0.0.0"
PORT = 8765

# A set to keep track of connected clients
connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    print("Client connected:", websocket.remote_address)
    try:
        async for message in websocket:
            # For this example, we don't expect the browser to send messages.
            pass
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected:", websocket.remote_address)

async def main():
    server = await websockets.serve(handler, HOST, PORT)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())