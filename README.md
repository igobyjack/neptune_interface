# Neptune Lawncare Project

### The system uses an aurdino microcontroller, a raspberry pi, and a basic moisture sensor.

# Setup: 

### sensor_reading.ino is an arduino script, written in C++, download it to your arduino and start, with the moisture sensor data plugged into A0 on the arduino.

### server_reader.py is an async websocket server designed to run on the raspberry pi, reading the incoming arduino data and broadcasting it to the webpage clients. All the python scripts in testing were for figuring out how to read and format the data off the serial port, and uses tkinter. Connct the arduino to the raspberry pi via the USB port.

### the webpage lives on the pi, which you'll need to setup to broadcast a wifi network. I used hostapd and dnsmasq. It should work so when you connect to the pi's wifi, it directs you to the website where the interface and data can be found. The webpage is pretty standard html and javascript, since I didn't want to push the capabilities of the pi.
