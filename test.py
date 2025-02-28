import serial

ser = serial.Serial('/dev/ttyACM0',9600)
s=[0,1]

while True:
	read_serial = ser.readline()
	cleandata = read_serial.decode('utf-8').strip()
	print(cleandata)
