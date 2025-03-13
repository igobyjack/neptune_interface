document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const toggleSensorButton = document.getElementById('toggle-sensor');
    const sensorValueSpan = document.getElementById('sensor-value');
    const sensorPercentSpan = document.getElementById('sensor-percent');
    const sensorMoistureTextSpan = document.getElementById('sensor-moisture-text');

    // State variables
    let sensorRunning = false;
    let serialPort = null;
    let currentMoisturePercent = 0;

    // WebSocket client to receive moisture data from the Raspberry Pi
    const websocket = new WebSocket('ws://localhost:8765');

    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const sensorValue = parseInt(data.value);
        const percent = parseInt(data.percent);
        updateMoistureData(sensorValue, percent, getMoistText(percent));
    };

    async function startReading() {
        try {
            serialPort = await navigator.serial.requestPort();
            await serialPort.open({ baudRate: 9600 });
            
            // Reset sensorRunning to ensure we start fresh
            sensorRunning = true;

            // Create a reader and start reading loop
            const reader = serialPort.readable.getReader();
            try {
                // Buffer to accumulate data
                let buffer = '';
                
                while (sensorRunning) {
                    const { value, done } = await reader.read();
                    if (done) {
                        // The stream was closed
                        break;
                    }
                    
                    // Decode and accumulate the received data
                    buffer += new TextDecoder().decode(value);
                    
                    // Process complete lines
                    const lines = buffer.split('\n');
                    // Keep the last potentially incomplete line in the buffer
                    buffer = lines.pop();
                    
                    // Process each complete line
                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (trimmedLine) {
                            try {
                                // Parse and update UI with the value
                                const sensorValue = parseInt(trimmedLine);
                                if (!isNaN(sensorValue)) {
                                    const percent = moistPercent(sensorValue);
                                    updateMoistureData(sensorValue, percent, getMoistText(percent));
                                }
                            } catch (e) {
                                console.error('Error parsing sensor data:', e);
                            }
                        }
                    }
                }
            } finally {
                // Always release the lock when done
                reader.releaseLock();
            }
        } catch (error) {
            console.error('Error reading from serial port:', error);
            sensorRunning = false;
            toggleSensorButton.textContent = 'Start';
        }
    }

    function stopReading() {
        if (serialPort) {
            serialPort.close();
            serialPort = null;
        }
    }

    // Helper functions
    function updateMoistureData(value, percent, moistureText) {
        sensorValueSpan.textContent = value;
        sensorPercentSpan.textContent = `${percent}%`;
        sensorMoistureTextSpan.textContent = moistureText;
        currentMoisturePercent = percent; // Store for recommendation
        
        // Update the moisture bar
        const moistureBar = document.getElementById('moisture-bar');
        const moistureBarText = document.getElementById('moisture-bar-text');
        
        if (moistureBar && moistureBarText) {
            // Cap at 100%
            const cappedPercent = Math.min(percent, 100);
            moistureBar.style.width = `${cappedPercent}%`;
            moistureBarText.textContent = `${percent}%`;
            
            // Change color based on moisture level
            if (percent < 10) {
                moistureBar.style.background = 'linear-gradient(90deg, #e74c3c 0%, #c0392b 100%)'; // Red
            } else if (percent < 30) {
                moistureBar.style.background = 'linear-gradient(90deg, #f39c12 0%, #d35400 100%)'; // Orange
            } else if (percent < 50) {
                moistureBar.style.background = 'linear-gradient(90deg, #2ecc71 0%, #27ae60 100%)'; // Green
            } else {
                moistureBar.style.background = 'linear-gradient(90deg, #3498db 0%, #2980b9 100%)'; // Blue
            }
        }
    }

    function moistPercent(value) {
        let percent = (value * (-1 / 259) + 1.78) * 100;
        return Math.round(percent);
    }

    function getMoistText(percent) {
        if (percent < 10) {
            return 'Dry';
        } else if (percent < 30) {
            return 'Moist';
        } else if (percent < 50) {
            return 'Wet';
        } else {
            return 'Very Wet';
        }
    }

    // Combined function for Start/Stop
    function toggleStartStop() {
        if (!sensorRunning) {
            startReading();
            toggleSensorButton.textContent = 'Stop';
            sensorRunning = true;
        } else {
            stopReading();
            toggleSensorButton.textContent = 'Start';
            sensorRunning = false;
        }
    }

    // Event listeners
    toggleSensorButton.addEventListener('click', toggleStartStop);
});
