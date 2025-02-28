document.addEventListener('DOMContentLoaded', function() {
    const comPortSelect = document.getElementById('com-port');
    const toggleSensorButton = document.getElementById('toggle-sensor');
    const getWeatherButton = document.getElementById('get-weather');
    const cityNameInput = document.getElementById('city-name');
    const weatherResultDiv = document.getElementById('weather-result');
    const sensorValueSpan = document.getElementById('sensor-value');
    const sensorPercentSpan = document.getElementById('sensor-percent');
    const sensorMoistureTextSpan = document.getElementById('sensor-moisture-text');

    let sensorRunning = false;
    let serialPort = null;

    async function listSerialPorts() {
        try {
            const ports = await navigator.serial.getPorts();
            comPortSelect.innerHTML = '';
            ports.forEach(port => {
                const option = document.createElement('option');
                option.value = port;
                option.textContent = port.getInfo().usbVendorId + ':' + port.getInfo().usbProductId;
                comPortSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error listing serial ports:', error);
        }
    }

    async function startReading() {
        try {
            const port = comPortSelect.value;
            serialPort = await navigator.serial.requestPort();
            await serialPort.open({ baudRate: 9600 });

            const reader = serialPort.readable.getReader();
            while (sensorRunning) {
                const { value, done } = await reader.read();
                if (done) {
                    break;
                }
                const line = new TextDecoder().decode(value).trim();
                const percent = moistPercent(parseInt(line));
                updateSensorData(line, percent, getMoistText(percent));
            }
            reader.releaseLock();
        } catch (error) {
            console.error('Error reading from serial port:', error);
        }
    }

    function stopReading() {
        if (serialPort) {
            serialPort.close();
            serialPort = null;
        }
    }

    function updateSensorData(value, percent, moistureText) {
        sensorValueSpan.textContent = value;
        sensorPercentSpan.textContent = `${percent}%`;
        sensorMoistureTextSpan.textContent = moistureText;
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

    async function fetchWeatherData() {
        const city = cityNameInput.value.trim();
        if (!city) {
            weatherResultDiv.textContent = 'Please enter a city name.';
            return;
        }

        const apiKey = '8142ceef20f88fdf993574705d67004a';
        const baseUrl = 'http://api.openweathermap.org/data/2.5/forecast?';
        const completeUrl = `${baseUrl}appid=${apiKey}&q=${city}`;

        try {
            const response = await fetch(completeUrl);
            const data = await response.json();
            if (data.cod !== '404') {
                const dailyRainPredictions = [];
                data.list.forEach(forecast => {
                    const dateTime = forecast.dt_txt;
                    const date = dateTime.split(' ')[0];
                    if (!dailyRainPredictions.some(d => d.date === date)) {
                        const rainChance = forecast.rain ? forecast.rain['3h'] : 0;
                        dailyRainPredictions.push({ date, rainChance });
                    }
                    if (dailyRainPredictions.length === 4) {
                        return;
                    }
                });

                let result = '';
                dailyRainPredictions.forEach(prediction => {
                    result += `Date: ${prediction.date}\n Rain Prediction (mm/3h): ${prediction.rainChance}\n\n`;
                });
                weatherResultDiv.textContent = result;
            } else {
                weatherResultDiv.textContent = 'City Not Found';
            }
        } catch (error) {
            weatherResultDiv.textContent = `Error: ${error}`;
        }
    }

    function toggleStartStop() {
        if (!sensorRunning) {
            if (!cityNameInput.value.trim()) {
                weatherResultDiv.textContent = 'Please enter a city name.';
                return;
            }
            startReading();
            fetchWeatherData();
            toggleSensorButton.textContent = 'Stop';
            sensorRunning = true;
        } else {
            stopReading();
            toggleSensorButton.textContent = 'Start';
            sensorRunning = false;
        }
    }

    toggleSensorButton.addEventListener('click', toggleStartStop);
    getWeatherButton.addEventListener('click', fetchWeatherData);

    listSerialPorts();
});
