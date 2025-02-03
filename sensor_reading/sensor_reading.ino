const int SENSOR_PIN = A0; // Change this if your sensor is on a different pin

void setup() {
  Serial.begin(9600);
  delay(500);
}

void loop() {
  // Read from the moisture sensor (range typically 0-1023 for a 10-bit ADC)
  int moistureValue = analogRead(SENSOR_PIN);
  

  // Print to Serial (this will be read by the Python script)
  Serial.println(moistureValue);

  

  // Short delay before taking the next reading
  delay(500);
}
