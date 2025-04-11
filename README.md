# Neptune Lawncare Project

### The system uses a microcontroller, moisture sensor, and raspberry pi. The idea was that you could stick this in your yard and it would give you an accurate say on whether to water your lawn or not, using data from the moisture sensor and the open weather api, to prevent overwatering. 

### Setup: 

### sensor_reading.ino is an arduino script, written in C++, it's my first real attempt at C++ and Arduino.

### server_reader.py is an async websocket server designed to run on the raspberry pi, reading the incoming arduino data and broadcasting it to the webpage clients. All the python scripts in testing were for figuring out how to read and format the data off the serial port, and uses tkinter. 

### the webpage lives on the pi, which is broadcasting a wifi network, so that when you connect to it, it directs you to the website where the interface and data can be found. It uses javascript to read the data coming in off the websocket, and update the page of anyone reading in real time.

### Local Testing with Mock Data:

To test the webpage on your local machine without connecting to the moisture sensor and Arduino, follow these steps:

1. Navigate to the `backend` directory:
   ```sh
   cd backend
   ```

2. Run the `server_reader.py` script with the `--mock` argument to use the mock data generator:
   ```sh
   python server_reader.py --mock
   ```

3. Open the `webpage/index.html` file in your web browser to view the interface and see the mock data being updated in real-time.
