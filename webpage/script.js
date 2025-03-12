document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const toggleSensorButton = document.getElementById('toggle-sensor');
    const getWeatherButton = document.getElementById('get-weather');
    const cityNameInput = document.getElementById('city-name');
    const weatherResultDiv = document.getElementById('weather-result');
    const sensorValueSpan = document.getElementById('sensor-value');
    const sensorPercentSpan = document.getElementById('sensor-percent');
    const sensorMoistureTextSpan = document.getElementById('sensor-moisture-text');

    // State variables
    let sensorRunning = false;
    let serialPort = null;
    let currentMoisturePercent = 0;
    let weatherForecastData = null;

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
                                    updateSensorData(sensorValue, percent, getMoistText(percent));
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
    function updateSensorData(value, percent, moistureText) {
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
        
        // Update the watering recommendation if we have weather data
        if (weatherForecastData) {
            updateWateringRecommendation();
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

    // Weather forecast function
    async function fetchWeatherData() {
        const city = cityNameInput.value.trim();
        if (!city) {
            weatherResultDiv.innerHTML = '<p class="error">Please enter a city name.</p>';
            return;
        }

        const apiKey = '8142ceef20f88fdf993574705d67004a';
        const baseUrl = 'http://api.openweathermap.org/data/2.5/forecast?';
        const completeUrl = `${baseUrl}appid=${apiKey}&q=${city}&units=metric`;

        try {
            weatherResultDiv.innerHTML = '<p>Loading forecast data...</p>';
            const response = await fetch(completeUrl);
            const data = await response.json();
            
            if (data.cod !== '404') {
                weatherForecastData = data; // Store the forecast data globally
                
                const dailyRainPredictions = [];
                data.list.forEach(forecast => {
                    const dateTime = forecast.dt_txt;
                    const date = dateTime.split(' ')[0];
                    if (!dailyRainPredictions.some(d => d.date === date)) {
                        const rainChance = forecast.rain ? forecast.rain['3h'] : 0;
                        // Get more weather details for a richer forecast
                        const temp = forecast.main.temp;
                        const description = forecast.weather[0].description;
                        const icon = forecast.weather[0].icon;
                        dailyRainPredictions.push({ 
                            date, 
                            rainChance,
                            temp,
                            description,
                            icon
                        });
                    }
                    if (dailyRainPredictions.length === 4) {
                        return;
                    }
                });

                // Format date to be more readable (e.g., "Mon, Jan 15")
                function formatDate(dateStr) {
                    const date = new Date(dateStr);
                    return date.toLocaleDateString('en-US', { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric'
                    });
                }

                // Build HTML for the forecast
                let html = `
                    <div class="forecast-header">
                        <h3>4-Day Forecast for ${city}</h3>
                    </div>
                    <div class="forecast-container">
                `;
                
                dailyRainPredictions.forEach(prediction => {
                    const formattedDate = formatDate(prediction.date);
                    const iconUrl = `http://openweathermap.org/img/wn/${prediction.icon}.png`;
                    
                    html += `
                        <div class="forecast-day">
                            <div class="forecast-date">${formattedDate}</div>
                            <div class="forecast-icon">
                                <img src="${iconUrl}" alt="${prediction.description}">
                            </div>
                            <div class="forecast-temp">${Math.round(prediction.temp)}°C</div>
                            <div class="forecast-desc">${prediction.description}</div>
                            <div class="forecast-rain">
                                <span class="rain-icon">💧</span> 
                                <span class="rain-amount">${prediction.rainChance} mm</span>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                weatherResultDiv.innerHTML = html;

                // Update the watering recommendation
                updateWateringRecommendation();
            } else {
                weatherResultDiv.innerHTML = '<p class="error">City Not Found</p>';
                weatherForecastData = null;
            }
        } catch (error) {
            weatherResultDiv.innerHTML = `<p class="error">Error: ${error}</p>`;
            weatherForecastData = null;
        }
    }

    // Add this function to check if it will rain in the next 2 days
    function willRainInNext2Days() {
        if (!weatherForecastData) return false;
        
        const today = new Date();
        const twoDaysLater = new Date();
        twoDaysLater.setDate(today.getDate() + 2);
        
        // Check the forecast for rain in the next 2 days
        for (const forecast of weatherForecastData.list) {
            const forecastDate = new Date(forecast.dt * 1000);
            
            // Only check forecasts within the next 2 days
            if (forecastDate <= twoDaysLater) {
                // Check if rain is predicted (> 0mm or exists in the forecast)
                if (forecast.rain && forecast.rain['3h'] > 0) {
                    return true;
                }
            }
        }
        
        return false;
    }

    // Add this function to generate and update the watering recommendation
    function updateWateringRecommendation() {
        const recommendationDiv = document.getElementById('watering-recommendation');
        if (!recommendationDiv) return;
        
        const isMoistureLow = currentMoisturePercent < 20; // Consider "dry" as below 20%
        const willRain = willRainInNext2Days();
        
        let recommendation = '';
        
        if (isMoistureLow && !willRain) {
            recommendation = `
                <div class="recommendation-alert">
                    <span>⚠️ Water Needed!</span>
                </div>
                <p>Your soil moisture is low (${currentMoisturePercent}%) and no rain is expected in the next 2 days.</p>
                <p>It's recommended to water your grass today.</p>
            `;
        } else if (isMoistureLow && willRain) {
            recommendation = `
                <div class="recommendation-alert">
                    <span>⚠️ Consider Watering</span>
                </div>
                <p>Your soil moisture is low (${currentMoisturePercent}%), but rain is expected in the next 2 days.</p>
                <p>Consider waiting to see if the rain will be sufficient.</p>
            `;
        } else {
            recommendation = `
                <div class="recommendation-alert">
                    <span>✅ No Watering Needed</span>
                </div>
                <p>Your soil moisture is sufficient (${currentMoisturePercent}%).</p>
                <p>No need to water your grass today.</p>
            `;
        }
        
        recommendationDiv.innerHTML = recommendation;
    }

    // Combined function for Start/Stop and Weather
    function toggleStartStop() {
        if (!sensorRunning) {
            if (!cityNameInput.value.trim()) {
                weatherResultDiv.innerHTML = '<p class="error">Please enter a city name.</p>';
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

    // Event listeners
    toggleSensorButton.addEventListener('click', toggleStartStop);
    getWeatherButton.addEventListener('click', fetchWeatherData);
});
