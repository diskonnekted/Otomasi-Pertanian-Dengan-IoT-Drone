# 🔧 Hardware Integration Guide - Arduino/ESP32

Panduan lengkap untuk mengintegrasikan sensor IoT dan sistem hardware dengan Smart Farm Monitoring System.

## 📋 Overview Hardware Architecture

```
[Sensor Field] → [Arduino/ESP32] → [WiFi] → [Smart Farm API] → [Dashboard]
     ↓              ↓               ↓           ↓               ↓
Soil Moisture   Data Collection   HTTP POST   Database     Real-time
pH Sensor       Signal Processing   Request    Storage      Monitoring
Temperature     WiFi Connection    JSON Data   Processing   Alerts
Humidity        Error Handling     API Call    Analysis     Control
```

## 🛠️ Required Hardware

### Essential Components
- **ESP32 DevKit** (recommended) atau Arduino Uno + WiFi Shield
- **Soil Moisture Sensor** (Capacitive recommended)
- **pH Sensor Module** (Analog pH sensor)
- **DHT22** (Temperature & Humidity sensor)
- **NPK Sensor** (N-P-K nutrient sensor) 
- **Water Pumps** untuk irrigation system
- **Relay Modules** untuk kontrol pump
- **Breadboards & Jumper Wires**
- **Power Supply** 12V untuk pumps, 5V untuk ESP32

### Optional Advanced Components
- **LoRa Module** untuk long-range communication
- **Solar Panel + Battery** untuk remote locations
- **LCD Display** untuk local monitoring
- **SD Card Module** untuk local data logging

## 📡 Smart Farm API Endpoints

### 1. Sensor Data Submission
```http
POST /api/sensors
Content-Type: application/json

{
  "zone_id": "zone-uuid-from-dashboard",
  "sensor_type": "soil_moisture",
  "value": 45.2,
  "unit": "%",
  "alert_level": "normal"
}
```

### 2. Get Zone Information
```http
GET /api/zones

Response:
[
  {
    "id": "zone-uuid",
    "zone_name": "Zone A - Padi Sawah",
    "irrigation_threshold": {
      "soil_moisture": 35,
      "nutrient_n": 50
    }
  }
]
```

### 3. Irrigation Control
```http
PUT /api/irrigation/{system_id}/activate?duration=15

Response:
{
  "message": "Irrigation system activated",
  "duration": 15
}
```

## 💻 ESP32 Code Implementation

### Complete ESP32 Smart Farm Code

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "https://your-domain.com/api/sensors";

// Sensor Pins
#define SOIL_MOISTURE_PIN 34    // Analog pin
#define PH_SENSOR_PIN 35        // Analog pin  
#define DHT_PIN 4               // Digital pin
#define DHT_TYPE DHT22
#define PUMP_RELAY_PIN 2        // Digital pin for irrigation

// Your zone ID from dashboard
const char* ZONE_ID = "your-zone-uuid-here";

// Sensor objects
DHT dht(DHT_PIN, DHT_TYPE);

// Timing variables
unsigned long lastSensorReading = 0;
const unsigned long sensorInterval = 30000; // 30 seconds

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  digitalWrite(PUMP_RELAY_PIN, LOW);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("Smart Farm ESP32 System Started");
  Serial.println("Zone ID: " + String(ZONE_ID));
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  // Read and send sensor data every interval
  if (millis() - lastSensorReading >= sensorInterval) {
    readAndSendSensorData();
    lastSensorReading = millis();
  }
  
  delay(1000);
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void readAndSendSensorData() {
  Serial.println("\n--- Reading Sensors ---");
  
  // Read soil moisture (0-4095, convert to percentage)
  int soilMoistureRaw = analogRead(SOIL_MOISTURE_PIN);
  float soilMoisture = map(soilMoistureRaw, 0, 4095, 0, 100);
  
  // Read pH sensor (0-4095, convert to pH scale)
  int phRaw = analogRead(PH_SENSOR_PIN);
  float phValue = map(phRaw, 0, 4095, 0, 14);
  
  // Read temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Validate readings
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error: Failed to read DHT sensor!");
    return;
  }
  
  // Send each sensor reading
  sendSensorReading("soil_moisture", soilMoisture, "%");
  delay(1000);
  sendSensorReading("ph_level", phValue, "pH");
  delay(1000);
  sendSensorReading("temperature", temperature, "°C");
  delay(1000);
  sendSensorReading("humidity", humidity, "%");
  
  // Check irrigation threshold
  checkAndControlIrrigation(soilMoisture);
  
  Serial.println("--- Sensor Reading Complete ---\n");
}

void sendSensorReading(String sensorType, float value, String unit) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    return;
  }
  
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  
  // Determine alert level
  String alertLevel = "normal";
  if (sensorType == "soil_moisture") {
    if (value < 20) alertLevel = "critical";
    else if (value < 30) alertLevel = "warning";
  } else if (sensorType == "ph_level") {
    if (value < 5.5 || value > 7.5) alertLevel = "warning";
    if (value < 5.0 || value > 8.0) alertLevel = "critical";
  }
  
  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["zone_id"] = ZONE_ID;
  doc["sensor_type"] = sensorType;
  doc["value"] = round(value * 10) / 10.0; // Round to 1 decimal
  doc["unit"] = unit;
  doc["alert_level"] = alertLevel;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST request
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("✅ " + sensorType + ": " + String(value) + unit + " (Response: " + String(httpResponseCode) + ")");
  } else {
    Serial.println("❌ Error sending " + sensorType + ": " + String(httpResponseCode));
  }
  
  http.end();
}

void checkAndControlIrrigation(float soilMoisture) {
  // Automatic irrigation control based on soil moisture
  const float IRRIGATION_THRESHOLD = 30.0; // 30% moisture threshold
  
  if (soilMoisture < IRRIGATION_THRESHOLD) {
    Serial.println("🚨 Low soil moisture detected: " + String(soilMoisture) + "%");
    Serial.println("💧 Activating irrigation system...");
    
    // Turn on irrigation pump
    digitalWrite(PUMP_RELAY_PIN, HIGH);
    delay(5000); // Run for 5 seconds (adjust as needed)
    digitalWrite(PUMP_RELAY_PIN, LOW);
    
    Serial.println("💧 Irrigation completed");
    
    // Send notification to dashboard (optional)
    sendIrrigationEvent(soilMoisture);
  }
}

void sendIrrigationEvent(float moistureLevel) {
  // Send irrigation event to dashboard for logging
  HTTPClient http;
  http.begin("https://your-domain.com/api/irrigation/log");
  http.addHeader("Content-Type", "application/json");
  
  DynamicJsonDocument doc(512);
  doc["zone_id"] = ZONE_ID;
  doc["event_type"] = "auto_irrigation";
  doc["trigger_moisture"] = moistureLevel;
  doc["duration"] = 5;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  http.POST(jsonString);
  http.end();
}

// Error handling and recovery functions
void handleSensorError(String sensorName) {
  Serial.println("⚠️ Sensor error: " + sensorName);
  // Implement error recovery logic
  // E.g., retry reading, skip this cycle, send error report
}

void printSystemStatus() {
  Serial.println("\n=== SYSTEM STATUS ===");
  Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected"));
  Serial.println("IP: " + WiFi.localIP().toString());
  Serial.println("Zone ID: " + String(ZONE_ID));
  Serial.println("Uptime: " + String(millis() / 1000) + " seconds");
  Serial.println("Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
  Serial.println("=====================\n");
}
```

### Sensor Calibration Code

```cpp
// Calibration functions for accurate readings

float calibrateSoilMoisture(int rawValue) {
  // Calibrate based on your sensor
  // Dry soil: ~3000-4095
  // Wet soil: ~1000-1500
  const int DRY_SOIL = 3000;
  const int WET_SOIL = 1500;
  
  if (rawValue > DRY_SOIL) return 0;
  if (rawValue < WET_SOIL) return 100;
  
  return map(rawValue, DRY_SOIL, WET_SOIL, 0, 100);
}

float calibratePH(int rawValue) {
  // pH sensor calibration
  // Use standard buffer solutions (pH 4.0, 7.0, 10.0)
  // Adjust these values based on your calibration
  const float PH_4_VOLTAGE = 3.2;
  const float PH_7_VOLTAGE = 2.5;
  const float PH_10_VOLTAGE = 1.8;
  
  float voltage = rawValue * (3.3 / 4095.0);
  
  // Linear interpolation for pH calculation
  if (voltage > PH_7_VOLTAGE) {
    return map(voltage * 100, PH_7_VOLTAGE * 100, PH_4_VOLTAGE * 100, 700, 400) / 100.0;
  } else {
    return map(voltage * 100, PH_10_VOLTAGE * 100, PH_7_VOLTAGE * 100, 1000, 700) / 100.0;
  }
}
```

## 🔌 Hardware Wiring Diagram

### ESP32 Pin Connections

```
ESP32 DevKit         Sensor/Component
GPIO34 (Analog)  →   Soil Moisture Sensor (Signal)
GPIO35 (Analog)  →   pH Sensor (Signal)
GPIO4  (Digital) →   DHT22 (Data)
GPIO2  (Digital) →   Relay Module (IN)
3.3V             →   Sensors VCC
GND              →   Sensors GND

Relay Module     →   Water Pump
12V Power Supply →   Pump VCC
GND              →   Pump & Relay GND
```

### Circuit Diagram (Text)

```
                    ESP32 DevKit
                   ┌─────────────┐
                   │             │
    Soil Moisture  │GPIO34   3.3V│──── VCC (All Sensors)
         Sensor ───│             │
                   │GPIO35   GND │──── GND (All Sensors)
        pH Sensor ─│             │
                   │GPIO4    GPIO2│──── Relay Module
         DHT22 ────│             │
                   │             │
                   └─────────────┘
                           │
                    WiFi Connection
                           │
                  Smart Farm Dashboard
```

## 📱 Mobile Controller App (Optional)

### Flutter App untuk Field Monitoring

```dart
// main.dart - Basic Flutter app for field monitoring
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SmartFarmApp extends StatefulWidget {
  @override
  _SmartFarmAppState createState() => _SmartFarmAppState();
}

class _SmartFarmAppState extends State<SmartFarmApp> {
  Map<String, dynamic> sensorData = {};
  
  @override
  void initState() {
    super.initState();
    fetchSensorData();
  }
  
  Future<void> fetchSensorData() async {
    final response = await http.get(
      Uri.parse('https://your-domain.com/api/dashboard'),
    );
    
    if (response.statusCode == 200) {
      setState(() {
        sensorData = json.decode(response.body);
      });
    }
  }
  
  Future<void> activateIrrigation(String systemId) async {
    await http.put(
      Uri.parse('https://your-domain.com/api/irrigation/$systemId/activate?duration=10'),
    );
    fetchSensorData(); // Refresh data
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Smart Farm Jenggawur')),
      body: RefreshIndicator(
        onRefresh: fetchSensorData,
        child: ListView(
          children: [
            // Sensor cards, irrigation controls, etc.
            Card(
              child: ListTile(
                title: Text('Soil Moisture'),
                subtitle: Text('${sensorData['soil_moisture'] ?? 'N/A'}%'),
                trailing: Icon(Icons.water_drop),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🔋 Power Management

### Battery-powered Remote Sensors

```cpp
#include "esp_sleep.h"

// Deep sleep configuration
#define SLEEP_DURATION 300000000 // 5 minutes in microseconds

void setupDeepSleep() {
  // Configure wake up source
  esp_sleep_enable_timer_wakeup(SLEEP_DURATION);
  
  // Read sensors quickly
  readAndSendSensorData();
  
  // Enter deep sleep
  Serial.println("Going to sleep for 5 minutes...");
  esp_deep_sleep_start();
}

void optimizePowerConsumption() {
  // Reduce CPU frequency
  setCpuFrequencyMhz(80);
  
  // Disable WiFi when not needed
  WiFi.mode(WIFI_OFF);
  
  // Use lower ADC resolution for sensors
  analogReadResolution(10); // Instead of 12
}
```

## 🌐 Long-Range Communication (LoRa)

### ESP32 LoRa Gateway Code

```cpp
#include <LoRa.h>

// LoRa pins for ESP32
#define SS_PIN 18
#define RST_PIN 14
#define DIO0_PIN 26

void setupLoRa() {
  LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);
  
  if (!LoRa.begin(433E6)) { // 433MHz
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  
  Serial.println("LoRa initialized successfully!");
}

void sendLoRaData(String data) {
  LoRa.beginPacket();
  LoRa.print(data);
  LoRa.endPacket();
  
  Serial.println("LoRa data sent: " + data);
}

void receiveLoRaData() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String receivedData = "";
    while (LoRa.available()) {
      receivedData += (char)LoRa.read();
    }
    
    // Process received sensor data
    processRemoteSensorData(receivedData);
  }
}
```

## 🚨 Error Handling & Reliability

### Robust Error Handling

```cpp
class SensorManager {
private:
  int connectionRetries = 0;
  const int MAX_RETRIES = 3;
  
public:
  bool sendDataWithRetry(String endpoint, String data) {
    for (int i = 0; i < MAX_RETRIES; i++) {
      if (sendHTTPRequest(endpoint, data)) {
        connectionRetries = 0;
        return true;
      }
      
      connectionRetries++;
      Serial.println("Retry " + String(i + 1) + " failed");
      delay(1000 * (i + 1)); // Exponential backoff
    }
    
    // Store data locally if all retries fail
    storeDataLocally(data);
    return false;
  }
  
  void storeDataLocally(String data) {
    // Store in EEPROM or SD card
    Serial.println("Storing data locally: " + data);
  }
};
```

## 📊 Data Logging & Analytics

### Local Data Storage

```cpp
#include <EEPROM.h>
#include <time.h>

class DataLogger {
private:
  int currentAddress = 0;
  
public:
  void logSensorReading(float value, String sensorType) {
    // Create data entry
    String logEntry = String(millis()) + "," + sensorType + "," + String(value);
    
    // Store in EEPROM
    for (int i = 0; i < logEntry.length(); i++) {
      EEPROM.write(currentAddress + i, logEntry[i]);
    }
    EEPROM.write(currentAddress + logEntry.length(), '\0');
    
    currentAddress += logEntry.length() + 1;
    EEPROM.commit();
    
    Serial.println("Data logged locally: " + logEntry);
  }
  
  void uploadStoredData() {
    // Read stored data from EEPROM and upload to server
    // Implement batch upload functionality
  }
};
```

## 🧪 Testing & Validation

### Hardware Test Functions

```cpp
void runDiagnostics() {
  Serial.println("\n=== HARDWARE DIAGNOSTICS ===");
  
  // Test WiFi
  Serial.print("WiFi Connection: ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "✅ OK" : "❌ FAILED");
  
  // Test sensors
  testSensorReadings();
  
  // Test irrigation system
  testIrrigationSystem();
  
  Serial.println("============================\n");
}

void testSensorReadings() {
  Serial.println("Testing sensor readings...");
  
  // Test soil moisture
  int soilRaw = analogRead(SOIL_MOISTURE_PIN);
  Serial.println("Soil Moisture Raw: " + String(soilRaw) + (soilRaw > 0 ? " ✅" : " ❌"));
  
  // Test pH sensor
  int phRaw = analogRead(PH_SENSOR_PIN);
  Serial.println("pH Sensor Raw: " + String(phRaw) + (phRaw > 0 ? " ✅" : " ❌"));
  
  // Test DHT sensor
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  Serial.println("Temperature: " + String(temp) + "°C" + (!isnan(temp) ? " ✅" : " ❌"));
  Serial.println("Humidity: " + String(hum) + "%" + (!isnan(hum) ? " ✅" : " ❌"));
}

void testIrrigationSystem() {
  Serial.println("Testing irrigation system...");
  
  // Test relay
  digitalWrite(PUMP_RELAY_PIN, HIGH);
  delay(100);
  digitalWrite(PUMP_RELAY_PIN, LOW);
  
  Serial.println("Irrigation relay: ✅ OK");
}
```

## 🔧 Maintenance & Troubleshooting

### Common Hardware Issues

#### 1. Sensor Calibration Drift
```cpp
void recalibrateSensors() {
  // Implement sensor recalibration routine
  Serial.println("Starting sensor recalibration...");
  
  // Soil moisture calibration in air and water
  Serial.println("Place soil moisture sensor in air, press any key...");
  // Wait for input, then read and store dry value
  
  Serial.println("Place soil moisture sensor in water, press any key...");
  // Wait for input, then read and store wet value
}
```

#### 2. WiFi Connection Issues
```cpp
void diagnoseWiFiIssues() {
  Serial.println("WiFi Diagnostics:");
  Serial.println("SSID: " + String(ssid));
  Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
  Serial.println("MAC Address: " + WiFi.macAddress());
  
  // Try to reconnect
  WiFi.disconnect();
  delay(1000);
  connectToWiFi();
}
```

#### 3. Power Supply Issues
```cpp
void checkPowerSupply() {
  // Check battery voltage (if using battery)
  float batteryVoltage = analogRead(BATTERY_PIN) * (3.3 / 4095.0) * 2;
  Serial.println("Battery Voltage: " + String(batteryVoltage) + "V");
  
  if (batteryVoltage < 3.0) {
    Serial.println("⚠️ Low battery warning!");
    // Enter power saving mode
    enterPowerSavingMode();
  }
}
```

---

## 📋 Installation Checklist

- [ ] ✅ **Hardware assembled** dan wiring sesuai diagram
- [ ] ✅ **Arduino IDE setup** dengan ESP32 board package
- [ ] ✅ **Libraries installed** (WiFi, HTTPClient, ArduinoJson, DHT)
- [ ] ✅ **Code uploaded** ke ESP32 dengan konfigurasi yang benar
- [ ] ✅ **WiFi credentials** configured
- [ ] ✅ **Zone ID** dari dashboard di-copy ke code
- [ ] ✅ **Sensor calibration** completed
- [ ] ✅ **API connection** tested dan working
- [ ] ✅ **Irrigation system** tested secara manual
- [ ] ✅ **Data appearing** di Smart Farm dashboard
- [ ] ✅ **Error handling** tested dengan disconnect scenarios

---

**🌾 Hardware integration complete! Smart Farm Desa Jenggawur siap dengan IoT monitoring! 🌾**

*Happy farming dengan teknologi IoT yang canggih!*