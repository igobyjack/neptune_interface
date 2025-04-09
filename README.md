# Neptune Lawncare Project

### The system uses a microcontroller, moisture sensor, and raspberry pi. The idea was that you could stick this in your yard and it would give you an accurate say on whether to water your lawn or not, using data from the moisture sensor and the open weather api, to prevent overwatering. 

### Setup: 

### sensor_reading.ino is an arduino script, written in C++, it's my first real attempt at C++ and Arduino.

### server_reader.py is an async websocket server designed to run on the raspberry pi, reading the incoming arduino data and broadcasting it to the webpage clients. All the python scripts in testing were for figuring out how to read and format the data off the serial port, and uses tkinter. 

### the webpage lives on the pi, which is broadcasting a wifi network, so that when you connect to it, it directs you to the website where the interface and data can be found. It uses javascript to read the data coming in off the websocket, and update the page of anyone reading in real time.

### Simulating Moisture Data for Testing

To simulate moisture data on your local machine and send it to the WebSocket server, you can use the `simulate_moisture_data.py` script located in the `testing` directory. This script generates random moisture data and sends it to the WebSocket server at regular intervals.

#### Running the Simulation Script

1. Ensure you have Python installed on your machine.
2. Install the required libraries using pip:
   ```
   pip install asyncio websockets
   ```
3. Navigate to the `testing` directory:
   ```
   cd testing
   ```
4. Run the simulation script:
   ```
   python simulate_moisture_data.py
   ```

The script will start generating random moisture data and sending it to the WebSocket server. You can then observe the data being received by the server and displayed on the webpage.
