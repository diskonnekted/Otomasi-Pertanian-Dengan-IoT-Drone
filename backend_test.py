#!/usr/bin/env python3
"""
Smart Farm Monitoring System Backend API Tests
Tests comprehensive backend functionality including API endpoints, data flow, and smart farm logic.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://farm-sense-control.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class SmartFarmTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.zones = []
        self.irrigation_systems = []
        self.drones = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_root_endpoint(self):
        """Test GET /api/ root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Smart Farm" in data["message"]:
                    self.log_test("Root Endpoint", True, "Root endpoint accessible and returns correct message")
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Root endpoint returns unexpected response", data)
            else:
                self.log_test("Root Endpoint", False, f"Root endpoint returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Root endpoint request failed: {str(e)}")
        return False
    
    def test_simulate_data(self):
        """Test POST /api/simulate-data to generate sample data"""
        try:
            response = requests.post(f"{self.base_url}/simulate-data", headers=self.headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "sensors_created" in data:
                    self.log_test("Simulate Data", True, f"Sample data generated successfully. Created {data.get('sensors_created', 0)} sensors")
                    return True
                else:
                    self.log_test("Simulate Data", False, "Simulate data returned unexpected response", data)
            else:
                self.log_test("Simulate Data", False, f"Simulate data returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Simulate Data", False, f"Simulate data request failed: {str(e)}")
        return False
    
    def test_get_zones(self):
        """Test GET /api/zones to retrieve farm zones"""
        try:
            response = requests.get(f"{self.base_url}/zones", headers=self.headers, timeout=10)
            if response.status_code == 200:
                zones = response.json()
                if isinstance(zones, list) and len(zones) > 0:
                    self.zones = zones
                    # Verify zone structure
                    zone = zones[0]
                    required_fields = ["id", "zone_name", "area_size", "crop_type", "latitude", "longitude", "irrigation_threshold"]
                    missing_fields = [field for field in required_fields if field not in zone]
                    
                    if not missing_fields:
                        # Check irrigation thresholds
                        thresholds = zone.get("irrigation_threshold", {})
                        if "soil_moisture" in thresholds and "nutrient_n" in thresholds:
                            self.log_test("Get Zones", True, f"Retrieved {len(zones)} zones with proper structure and thresholds")
                            return True
                        else:
                            self.log_test("Get Zones", False, "Zones missing proper irrigation thresholds", thresholds)
                    else:
                        self.log_test("Get Zones", False, f"Zones missing required fields: {missing_fields}", zone)
                else:
                    self.log_test("Get Zones", False, "No zones found or invalid response format", zones)
            else:
                self.log_test("Get Zones", False, f"Get zones returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Zones", False, f"Get zones request failed: {str(e)}")
        return False
    
    def test_get_sensors(self):
        """Test GET /api/sensors to retrieve sensor data"""
        try:
            response = requests.get(f"{self.base_url}/sensors", headers=self.headers, timeout=10)
            if response.status_code == 200:
                sensors = response.json()
                if isinstance(sensors, list) and len(sensors) > 0:
                    # Verify sensor structure and data
                    sensor = sensors[0]
                    required_fields = ["id", "zone_id", "sensor_type", "value", "unit", "timestamp", "alert_level"]
                    missing_fields = [field for field in required_fields if field not in sensor]
                    
                    if not missing_fields:
                        # Check sensor types
                        sensor_types = set(s["sensor_type"] for s in sensors)
                        expected_types = {"soil_moisture", "nutrient_n", "nutrient_p", "nutrient_k", "ph_level", "temperature", "humidity"}
                        
                        if expected_types.issubset(sensor_types):
                            # Check alert levels
                            alert_levels = set(s["alert_level"] for s in sensors if s["alert_level"])
                            critical_sensors = [s for s in sensors if s["alert_level"] == "critical"]
                            warning_sensors = [s for s in sensors if s["alert_level"] == "warning"]
                            
                            self.log_test("Get Sensors", True, 
                                        f"Retrieved {len(sensors)} sensors with all expected types. "
                                        f"Alert levels: {len(critical_sensors)} critical, {len(warning_sensors)} warning")
                            return True
                        else:
                            missing_types = expected_types - sensor_types
                            self.log_test("Get Sensors", False, f"Missing sensor types: {missing_types}", sensor_types)
                    else:
                        self.log_test("Get Sensors", False, f"Sensors missing required fields: {missing_fields}", sensor)
                else:
                    self.log_test("Get Sensors", False, "No sensors found or invalid response format", sensors)
            else:
                self.log_test("Get Sensors", False, f"Get sensors returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Sensors", False, f"Get sensors request failed: {str(e)}")
        return False
    
    def test_get_irrigation(self):
        """Test GET /api/irrigation to retrieve irrigation systems"""
        try:
            response = requests.get(f"{self.base_url}/irrigation", headers=self.headers, timeout=10)
            if response.status_code == 200:
                irrigation_systems = response.json()
                if isinstance(irrigation_systems, list) and len(irrigation_systems) > 0:
                    self.irrigation_systems = irrigation_systems
                    # Verify irrigation system structure
                    system = irrigation_systems[0]
                    required_fields = ["id", "zone_id", "status", "flow_rate"]
                    missing_fields = [field for field in required_fields if field not in system]
                    
                    if not missing_fields:
                        # Check status values
                        statuses = set(s["status"] for s in irrigation_systems)
                        valid_statuses = {"idle", "active", "scheduled", "maintenance"}
                        
                        if statuses.issubset(valid_statuses):
                            self.log_test("Get Irrigation", True, 
                                        f"Retrieved {len(irrigation_systems)} irrigation systems with valid statuses: {statuses}")
                            return True
                        else:
                            invalid_statuses = statuses - valid_statuses
                            self.log_test("Get Irrigation", False, f"Invalid irrigation statuses: {invalid_statuses}")
                    else:
                        self.log_test("Get Irrigation", False, f"Irrigation systems missing required fields: {missing_fields}", system)
                else:
                    self.log_test("Get Irrigation", False, "No irrigation systems found or invalid response format", irrigation_systems)
            else:
                self.log_test("Get Irrigation", False, f"Get irrigation returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Irrigation", False, f"Get irrigation request failed: {str(e)}")
        return False
    
    def test_activate_irrigation(self):
        """Test PUT /api/irrigation/{system_id}/activate to activate irrigation"""
        if not self.irrigation_systems:
            self.log_test("Activate Irrigation", False, "No irrigation systems available for testing")
            return False
        
        try:
            # Test with valid system ID
            system_id = self.irrigation_systems[0]["id"]
            duration = 15
            
            response = requests.put(
                f"{self.base_url}/irrigation/{system_id}/activate?duration={duration}", 
                headers=self.headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "duration" in data:
                    # Verify the system status was updated
                    time.sleep(1)  # Brief delay for database update
                    verify_response = requests.get(f"{self.base_url}/irrigation", headers=self.headers, timeout=10)
                    
                    if verify_response.status_code == 200:
                        updated_systems = verify_response.json()
                        activated_system = next((s for s in updated_systems if s["id"] == system_id), None)
                        
                        if activated_system and activated_system["status"] == "active":
                            self.log_test("Activate Irrigation", True, 
                                        f"Irrigation system activated successfully with duration {duration} minutes")
                            return True
                        else:
                            self.log_test("Activate Irrigation", False, 
                                        "Irrigation system status not updated to active", activated_system)
                    else:
                        self.log_test("Activate Irrigation", False, "Could not verify irrigation system status update")
                else:
                    self.log_test("Activate Irrigation", False, "Activate irrigation returned unexpected response", data)
            else:
                self.log_test("Activate Irrigation", False, 
                            f"Activate irrigation returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Activate Irrigation", False, f"Activate irrigation request failed: {str(e)}")
        return False
    
    def test_activate_irrigation_invalid_id(self):
        """Test PUT /api/irrigation/{invalid_id}/activate with invalid system ID"""
        try:
            invalid_id = "invalid-system-id-12345"
            response = requests.put(
                f"{self.base_url}/irrigation/{invalid_id}/activate?duration=10", 
                headers=self.headers, 
                timeout=10
            )
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data and "not found" in data["detail"].lower():
                    self.log_test("Activate Irrigation Invalid ID", True, "Correctly returned 404 for invalid irrigation system ID")
                    return True
                else:
                    self.log_test("Activate Irrigation Invalid ID", False, "404 response missing proper error message", data)
            else:
                self.log_test("Activate Irrigation Invalid ID", False, 
                            f"Expected 404 but got status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Activate Irrigation Invalid ID", False, f"Invalid ID test request failed: {str(e)}")
        return False
    
    def test_get_drones(self):
        """Test GET /api/drones to retrieve drone fleet"""
        try:
            response = requests.get(f"{self.base_url}/drones", headers=self.headers, timeout=10)
            if response.status_code == 200:
                drones = response.json()
                if isinstance(drones, list) and len(drones) > 0:
                    self.drones = drones
                    # Verify drone structure
                    drone = drones[0]
                    required_fields = ["id", "drone_name", "status", "battery_level", "current_lat", "current_lng", "payload_remaining"]
                    missing_fields = [field for field in required_fields if field not in drone]
                    
                    if not missing_fields:
                        # Check status values
                        statuses = set(d["status"] for d in drones)
                        valid_statuses = {"idle", "in_flight", "spraying", "returning", "charging", "maintenance"}
                        
                        if statuses.issubset(valid_statuses):
                            self.log_test("Get Drones", True, 
                                        f"Retrieved {len(drones)} drones with valid statuses: {statuses}")
                            return True
                        else:
                            invalid_statuses = statuses - valid_statuses
                            self.log_test("Get Drones", False, f"Invalid drone statuses: {invalid_statuses}")
                    else:
                        self.log_test("Get Drones", False, f"Drones missing required fields: {missing_fields}", drone)
                else:
                    self.log_test("Get Drones", False, "No drones found or invalid response format", drones)
            else:
                self.log_test("Get Drones", False, f"Get drones returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Drones", False, f"Get drones request failed: {str(e)}")
        return False
    
    def test_drone_mission(self):
        """Test PUT /api/drones/{drone_id}/mission to assign drone mission"""
        if not self.drones:
            self.log_test("Drone Mission", False, "No drones available for testing")
            return False
        
        try:
            # Test with valid drone ID
            drone_id = self.drones[0]["id"]
            mission_data = {
                "target_lat": -6.2095,
                "target_lng": 106.8470,
                "payload_type": "water"
            }
            
            response = requests.put(
                f"{self.base_url}/drones/{drone_id}/mission", 
                params=mission_data,
                headers=self.headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "target" in data:
                    # Verify the drone status was updated
                    time.sleep(1)  # Brief delay for database update
                    verify_response = requests.get(f"{self.base_url}/drones", headers=self.headers, timeout=10)
                    
                    if verify_response.status_code == 200:
                        updated_drones = verify_response.json()
                        mission_drone = next((d for d in updated_drones if d["id"] == drone_id), None)
                        
                        if mission_drone and mission_drone["status"] == "in_flight":
                            self.log_test("Drone Mission", True, 
                                        f"Drone mission assigned successfully. Status changed to in_flight")
                            return True
                        else:
                            self.log_test("Drone Mission", False, 
                                        "Drone status not updated to in_flight", mission_drone)
                    else:
                        self.log_test("Drone Mission", False, "Could not verify drone status update")
                else:
                    self.log_test("Drone Mission", False, "Drone mission returned unexpected response", data)
            else:
                self.log_test("Drone Mission", False, 
                            f"Drone mission returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Drone Mission", False, f"Drone mission request failed: {str(e)}")
        return False
    
    def test_drone_mission_invalid_id(self):
        """Test PUT /api/drones/{invalid_id}/mission with invalid drone ID"""
        try:
            invalid_id = "invalid-drone-id-12345"
            mission_data = {
                "target_lat": -6.2095,
                "target_lng": 106.8470,
                "payload_type": "water"
            }
            
            response = requests.put(
                f"{self.base_url}/drones/{invalid_id}/mission", 
                params=mission_data,
                headers=self.headers, 
                timeout=10
            )
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data and "not found" in data["detail"].lower():
                    self.log_test("Drone Mission Invalid ID", True, "Correctly returned 404 for invalid drone ID")
                    return True
                else:
                    self.log_test("Drone Mission Invalid ID", False, "404 response missing proper error message", data)
            else:
                self.log_test("Drone Mission Invalid ID", False, 
                            f"Expected 404 but got status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Drone Mission Invalid ID", False, f"Invalid drone ID test request failed: {str(e)}")
        return False
    
    def test_dashboard_summary(self):
        """Test GET /api/dashboard to retrieve dashboard summary"""
        try:
            response = requests.get(f"{self.base_url}/dashboard", headers=self.headers, timeout=15)
            if response.status_code == 200:
                dashboard = response.json()
                required_fields = ["total_zones", "active_irrigations", "drones_active", "critical_alerts", 
                                 "recent_sensor_data", "irrigation_systems", "drone_fleet"]
                missing_fields = [field for field in required_fields if field not in dashboard]
                
                if not missing_fields:
                    # Verify data consistency
                    total_zones = dashboard["total_zones"]
                    active_irrigations = dashboard["active_irrigations"]
                    drones_active = dashboard["drones_active"]
                    critical_alerts = dashboard["critical_alerts"]
                    
                    if (isinstance(total_zones, int) and total_zones >= 0 and
                        isinstance(active_irrigations, int) and active_irrigations >= 0 and
                        isinstance(drones_active, int) and drones_active >= 0 and
                        isinstance(critical_alerts, int) and critical_alerts >= 0):
                        
                        self.log_test("Dashboard Summary", True, 
                                    f"Dashboard summary retrieved successfully. "
                                    f"Zones: {total_zones}, Active Irrigation: {active_irrigations}, "
                                    f"Active Drones: {drones_active}, Critical Alerts: {critical_alerts}")
                        return True
                    else:
                        self.log_test("Dashboard Summary", False, "Dashboard contains invalid count values", dashboard)
                else:
                    self.log_test("Dashboard Summary", False, f"Dashboard missing required fields: {missing_fields}", dashboard)
            else:
                self.log_test("Dashboard Summary", False, f"Dashboard returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Dashboard Summary", False, f"Dashboard request failed: {str(e)}")
        return False
    
    def test_sensor_alert_logic(self):
        """Test sensor alert logic for critical and warning levels"""
        try:
            response = requests.get(f"{self.base_url}/sensors", headers=self.headers, timeout=10)
            if response.status_code == 200:
                sensors = response.json()
                
                # Check soil moisture alerts
                soil_sensors = [s for s in sensors if s["sensor_type"] == "soil_moisture"]
                critical_soil = [s for s in soil_sensors if s["alert_level"] == "critical" and s["value"] < 20]
                warning_soil = [s for s in soil_sensors if s["alert_level"] == "warning" and s["value"] >= 20 and s["value"] < 30]
                
                # Check nutrient alerts
                nutrient_sensors = [s for s in sensors if s["sensor_type"] in ["nutrient_n", "nutrient_p", "nutrient_k"]]
                critical_nutrients = [s for s in nutrient_sensors if s["alert_level"] == "critical" and s["value"] < 25]
                warning_nutrients = [s for s in nutrient_sensors if s["alert_level"] == "warning" and s["value"] >= 25 and s["value"] < 40]
                
                alert_logic_correct = True
                issues = []
                
                # Verify critical soil moisture alerts
                for sensor in soil_sensors:
                    if sensor["value"] < 20 and sensor["alert_level"] != "critical":
                        alert_logic_correct = False
                        issues.append(f"Soil moisture {sensor['value']} should be critical but is {sensor['alert_level']}")
                    elif 20 <= sensor["value"] < 30 and sensor["alert_level"] != "warning":
                        alert_logic_correct = False
                        issues.append(f"Soil moisture {sensor['value']} should be warning but is {sensor['alert_level']}")
                
                # Verify nutrient alerts
                for sensor in nutrient_sensors:
                    if sensor["value"] < 25 and sensor["alert_level"] != "critical":
                        alert_logic_correct = False
                        issues.append(f"Nutrient {sensor['sensor_type']} {sensor['value']} should be critical but is {sensor['alert_level']}")
                    elif 25 <= sensor["value"] < 40 and sensor["alert_level"] != "warning":
                        alert_logic_correct = False
                        issues.append(f"Nutrient {sensor['sensor_type']} {sensor['value']} should be warning but is {sensor['alert_level']}")
                
                if alert_logic_correct:
                    self.log_test("Sensor Alert Logic", True, 
                                f"Alert logic working correctly. Critical: {len(critical_soil + critical_nutrients)}, "
                                f"Warning: {len(warning_soil + warning_nutrients)}")
                    return True
                else:
                    self.log_test("Sensor Alert Logic", False, f"Alert logic issues found: {issues}")
            else:
                self.log_test("Sensor Alert Logic", False, f"Could not retrieve sensors for alert logic test")
        except Exception as e:
            self.log_test("Sensor Alert Logic", False, f"Alert logic test failed: {str(e)}")
        return False
    
    def test_historical_sensor_data_default(self):
        """Test GET /api/sensors/historical with default 24 hours"""
        try:
            response = requests.get(f"{self.base_url}/sensors/historical", headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["data", "hours", "zone_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    chart_data = data["data"]
                    hours = data["hours"]
                    
                    if isinstance(chart_data, list) and len(chart_data) > 0 and hours == 24:
                        # Verify data structure
                        sample_point = chart_data[0]
                        if "time" in sample_point:
                            # Check for sensor type fields
                            sensor_fields = ["soil_moisture", "nutrient_n", "nutrient_p", "nutrient_k"]
                            found_fields = [field for field in sensor_fields if field in sample_point]
                            
                            if found_fields:
                                # Verify realistic trends - moisture should vary throughout day
                                moisture_values = [point.get("soil_moisture", 0) for point in chart_data if "soil_moisture" in point]
                                if moisture_values and max(moisture_values) - min(moisture_values) > 5:
                                    self.log_test("Historical Data Default", True, 
                                                f"Retrieved {len(chart_data)} hourly data points for {hours} hours with realistic trends. "
                                                f"Sensor fields: {found_fields}")
                                    return True
                                else:
                                    self.log_test("Historical Data Default", False, 
                                                f"Historical data lacks realistic variation. Moisture range: {min(moisture_values) if moisture_values else 0}-{max(moisture_values) if moisture_values else 0}")
                            else:
                                self.log_test("Historical Data Default", False, 
                                            f"Historical data missing sensor type fields", sample_point)
                        else:
                            self.log_test("Historical Data Default", False, 
                                        "Historical data points missing 'time' field", sample_point)
                    else:
                        self.log_test("Historical Data Default", False, 
                                    f"Invalid historical data format. Length: {len(chart_data)}, Hours: {hours}")
                else:
                    self.log_test("Historical Data Default", False, 
                                f"Historical data missing required fields: {missing_fields}", data)
            else:
                self.log_test("Historical Data Default", False, 
                            f"Historical data returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Historical Data Default", False, f"Historical data request failed: {str(e)}")
        return False
    
    def test_historical_sensor_data_custom_hours(self):
        """Test GET /api/sensors/historical with custom hours parameter"""
        try:
            custom_hours = 12
            response = requests.get(f"{self.base_url}/sensors/historical?hours={custom_hours}", 
                                  headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                chart_data = data.get("data", [])
                hours = data.get("hours", 0)
                
                if len(chart_data) == custom_hours and hours == custom_hours:
                    # Verify hourly aggregation
                    if len(chart_data) > 1:
                        # Check time intervals (should be roughly 1 hour apart)
                        from datetime import datetime
                        time1 = datetime.fromisoformat(chart_data[0]["time"].replace('Z', '+00:00'))
                        time2 = datetime.fromisoformat(chart_data[1]["time"].replace('Z', '+00:00'))
                        time_diff = abs((time2 - time1).total_seconds() / 3600)  # Convert to hours
                        
                        if 0.8 <= time_diff <= 1.2:  # Allow some tolerance
                            self.log_test("Historical Data Custom Hours", True, 
                                        f"Retrieved {len(chart_data)} data points for {custom_hours} hours with proper hourly intervals")
                            return True
                        else:
                            self.log_test("Historical Data Custom Hours", False, 
                                        f"Time intervals not hourly. Difference: {time_diff} hours")
                    else:
                        self.log_test("Historical Data Custom Hours", True, 
                                    f"Retrieved {len(chart_data)} data points for {custom_hours} hours")
                        return True
                else:
                    self.log_test("Historical Data Custom Hours", False, 
                                f"Expected {custom_hours} data points but got {len(chart_data)}")
            else:
                self.log_test("Historical Data Custom Hours", False, 
                            f"Custom hours request returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Historical Data Custom Hours", False, f"Custom hours request failed: {str(e)}")
        return False
    
    def test_historical_sensor_data_zone_filter(self):
        """Test GET /api/sensors/historical with zone_id filter"""
        if not self.zones:
            self.log_test("Historical Data Zone Filter", False, "No zones available for testing")
            return False
        
        try:
            zone_id = self.zones[0]["id"]
            response = requests.get(f"{self.base_url}/sensors/historical?zone_id={zone_id}", 
                                  headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                chart_data = data.get("data", [])
                returned_zone_id = data.get("zone_id")
                
                if returned_zone_id == zone_id and isinstance(chart_data, list):
                    if len(chart_data) > 0:
                        # Verify data structure for zone-specific data
                        sample_point = chart_data[0]
                        if "time" in sample_point and any(field in sample_point for field in ["soil_moisture", "nutrient_n", "nutrient_p", "nutrient_k"]):
                            self.log_test("Historical Data Zone Filter", True, 
                                        f"Retrieved {len(chart_data)} data points filtered by zone {zone_id}")
                            return True
                        else:
                            self.log_test("Historical Data Zone Filter", False, 
                                        "Zone-filtered data missing required fields", sample_point)
                    else:
                        self.log_test("Historical Data Zone Filter", True, 
                                    f"Zone filter working (no data for zone {zone_id})")
                        return True
                else:
                    self.log_test("Historical Data Zone Filter", False, 
                                f"Zone filter not working. Expected zone: {zone_id}, Got: {returned_zone_id}")
            else:
                self.log_test("Historical Data Zone Filter", False, 
                            f"Zone filter request returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Historical Data Zone Filter", False, f"Zone filter request failed: {str(e)}")
        return False
    
    def test_drone_positions_api(self):
        """Test GET /api/drones/positions for map visualization"""
        try:
            response = requests.get(f"{self.base_url}/drones/positions", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["drones", "last_updated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    drones = data["drones"]
                    last_updated = data["last_updated"]
                    
                    if isinstance(drones, list) and len(drones) > 0:
                        # Verify drone position structure
                        drone = drones[0]
                        required_drone_fields = ["id", "name", "status", "battery", "payload", "payload_type", "position"]
                        missing_drone_fields = [field for field in required_drone_fields if field not in drone]
                        
                        if not missing_drone_fields:
                            # Verify position coordinates
                            position = drone["position"]
                            if isinstance(position, list) and len(position) == 2:
                                lat, lng = position
                                # Check if coordinates are valid (Jakarta area)
                                if -7 <= lat <= -5 and 106 <= lng <= 108:
                                    # Verify battery is percentage
                                    battery = drone["battery"]
                                    if 0 <= battery <= 100:
                                        # Check for target coordinates if drone is in flight
                                        target = drone.get("target")
                                        if drone["status"] == "in_flight" and target:
                                            if isinstance(target, list) and len(target) == 2:
                                                self.log_test("Drone Positions API", True, 
                                                            f"Retrieved {len(drones)} drone positions with valid coordinates, "
                                                            f"battery levels, and flight targets")
                                                return True
                                            else:
                                                self.log_test("Drone Positions API", False, 
                                                            f"Invalid target coordinates format for in-flight drone", target)
                                        else:
                                            self.log_test("Drone Positions API", True, 
                                                        f"Retrieved {len(drones)} drone positions with valid coordinates and battery levels")
                                            return True
                                    else:
                                        self.log_test("Drone Positions API", False, 
                                                    f"Invalid battery level: {battery}. Should be 0-100")
                                else:
                                    self.log_test("Drone Positions API", False, 
                                                f"Invalid GPS coordinates: [{lat}, {lng}]. Should be in Jakarta area")
                            else:
                                self.log_test("Drone Positions API", False, 
                                            f"Invalid position format: {position}. Should be [lat, lng]")
                        else:
                            self.log_test("Drone Positions API", False, 
                                        f"Drone position missing required fields: {missing_drone_fields}", drone)
                    else:
                        self.log_test("Drone Positions API", False, 
                                    f"No drone positions found or invalid format", drones)
                else:
                    self.log_test("Drone Positions API", False, 
                                f"Drone positions response missing required fields: {missing_fields}", data)
            else:
                self.log_test("Drone Positions API", False, 
                            f"Drone positions returned status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Drone Positions API", False, f"Drone positions request failed: {str(e)}")
        return False
    
    def test_clear_data_api(self):
        """Test DELETE /api/clear-data to clear all database records"""
        try:
            # First verify we have data
            sensors_before = requests.get(f"{self.base_url}/sensors", headers=self.headers, timeout=10)
            zones_before = requests.get(f"{self.base_url}/zones", headers=self.headers, timeout=10)
            
            if sensors_before.status_code == 200 and zones_before.status_code == 200:
                sensors_count_before = len(sensors_before.json())
                zones_count_before = len(zones_before.json())
                
                if sensors_count_before > 0 or zones_count_before > 0:
                    # Clear all data
                    response = requests.delete(f"{self.base_url}/clear-data", headers=self.headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "message" in data and "cleared" in data["message"].lower():
                            # Verify all collections are cleared
                            time.sleep(2)  # Allow time for database operations
                            
                            sensors_after = requests.get(f"{self.base_url}/sensors", headers=self.headers, timeout=10)
                            zones_after = requests.get(f"{self.base_url}/zones", headers=self.headers, timeout=10)
                            irrigation_after = requests.get(f"{self.base_url}/irrigation", headers=self.headers, timeout=10)
                            drones_after = requests.get(f"{self.base_url}/drones", headers=self.headers, timeout=10)
                            
                            if (sensors_after.status_code == 200 and zones_after.status_code == 200 and
                                irrigation_after.status_code == 200 and drones_after.status_code == 200):
                                
                                sensors_count_after = len(sensors_after.json())
                                zones_count_after = len(zones_after.json())
                                irrigation_count_after = len(irrigation_after.json())
                                drones_count_after = len(drones_after.json())
                                
                                if (sensors_count_after == 0 and zones_count_after == 0 and
                                    irrigation_count_after == 0 and drones_count_after == 0):
                                    self.log_test("Clear Data API", True, 
                                                f"Successfully cleared all data. Before: {sensors_count_before} sensors, "
                                                f"{zones_count_before} zones. After: all collections empty")
                                    # Reset our cached data
                                    self.zones = []
                                    self.irrigation_systems = []
                                    self.drones = []
                                    return True
                                else:
                                    self.log_test("Clear Data API", False, 
                                                f"Data not fully cleared. After: {sensors_count_after} sensors, "
                                                f"{zones_count_after} zones, {irrigation_count_after} irrigation, "
                                                f"{drones_count_after} drones")
                            else:
                                self.log_test("Clear Data API", False, "Could not verify data clearing")
                        else:
                            self.log_test("Clear Data API", False, "Clear data returned unexpected response", data)
                    else:
                        self.log_test("Clear Data API", False, 
                                    f"Clear data returned status {response.status_code}", response.text)
                else:
                    self.log_test("Clear Data API", True, "No data to clear (database already empty)")
                    return True
            else:
                self.log_test("Clear Data API", False, "Could not verify initial data state")
        except Exception as e:
            self.log_test("Clear Data API", False, f"Clear data request failed: {str(e)}")
        return False
    
    def test_integration_flow(self):
        """Test complete integration flow: clear data -> simulate -> verify endpoints"""
        try:
            print("   🔄 Starting integration flow test...")
            
            # Step 1: Clear all data
            clear_response = requests.delete(f"{self.base_url}/clear-data", headers=self.headers, timeout=15)
            if clear_response.status_code != 200:
                self.log_test("Integration Flow", False, "Failed to clear data in integration test")
                return False
            
            time.sleep(2)  # Allow database operations to complete
            
            # Step 2: Generate fresh simulation data
            simulate_response = requests.post(f"{self.base_url}/simulate-data", headers=self.headers, timeout=30)
            if simulate_response.status_code != 200:
                self.log_test("Integration Flow", False, "Failed to simulate data in integration test")
                return False
            
            time.sleep(3)  # Allow data generation to complete
            
            # Step 3: Verify historical endpoint returns 24 hours of realistic data
            historical_response = requests.get(f"{self.base_url}/sensors/historical", headers=self.headers, timeout=15)
            if historical_response.status_code != 200:
                self.log_test("Integration Flow", False, "Historical endpoint failed after data refresh")
                return False
            
            historical_data = historical_response.json()
            chart_data = historical_data.get("data", [])
            if len(chart_data) != 24:
                self.log_test("Integration Flow", False, f"Expected 24 hours of data, got {len(chart_data)}")
                return False
            
            # Verify realistic patterns
            moisture_values = [point.get("soil_moisture", 0) for point in chart_data if "soil_moisture" in point]
            if not moisture_values or max(moisture_values) - min(moisture_values) < 5:
                self.log_test("Integration Flow", False, "Historical data lacks realistic moisture variation")
                return False
            
            # Step 4: Verify drone positions endpoint returns proper map data
            positions_response = requests.get(f"{self.base_url}/drones/positions", headers=self.headers, timeout=10)
            if positions_response.status_code != 200:
                self.log_test("Integration Flow", False, "Drone positions endpoint failed after data refresh")
                return False
            
            positions_data = positions_response.json()
            drones = positions_data.get("drones", [])
            if len(drones) == 0:
                self.log_test("Integration Flow", False, "No drone positions after data refresh")
                return False
            
            # Verify drone data structure
            drone = drones[0]
            if not all(field in drone for field in ["id", "name", "status", "battery", "position"]):
                self.log_test("Integration Flow", False, "Drone position data missing required fields")
                return False
            
            # Step 5: Test dashboard endpoint still works
            dashboard_response = requests.get(f"{self.base_url}/dashboard", headers=self.headers, timeout=15)
            if dashboard_response.status_code != 200:
                self.log_test("Integration Flow", False, "Dashboard endpoint failed after data refresh")
                return False
            
            dashboard_data = dashboard_response.json()
            if dashboard_data.get("total_zones", 0) == 0:
                self.log_test("Integration Flow", False, "Dashboard shows no zones after data refresh")
                return False
            
            self.log_test("Integration Flow", True, 
                        f"Complete integration flow successful: cleared data, generated fresh simulation, "
                        f"verified {len(chart_data)} hours of historical data, {len(drones)} drone positions, "
                        f"and dashboard with {dashboard_data.get('total_zones', 0)} zones")
            
            # Update cached data for subsequent tests
            zones_response = requests.get(f"{self.base_url}/zones", headers=self.headers, timeout=10)
            if zones_response.status_code == 200:
                self.zones = zones_response.json()
            
            return True
            
        except Exception as e:
            self.log_test("Integration Flow", False, f"Integration flow test failed: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Smart Farm Monitoring System Backend Tests")
        print("=" * 60)
        
        # Test sequence following the smart farm workflow
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Integration Flow", self.test_integration_flow),  # Test complete flow first
            ("Get Zones", self.test_get_zones),
            ("Get Sensors", self.test_get_sensors),
            ("Sensor Alert Logic", self.test_sensor_alert_logic),
            ("Historical Data Default", self.test_historical_sensor_data_default),
            ("Historical Data Custom Hours", self.test_historical_sensor_data_custom_hours),
            ("Historical Data Zone Filter", self.test_historical_sensor_data_zone_filter),
            ("Drone Positions API", self.test_drone_positions_api),
            ("Get Irrigation", self.test_get_irrigation),
            ("Activate Irrigation", self.test_activate_irrigation),
            ("Activate Irrigation Invalid ID", self.test_activate_irrigation_invalid_id),
            ("Get Drones", self.test_get_drones),
            ("Drone Mission", self.test_drone_mission),
            ("Drone Mission Invalid ID", self.test_drone_mission_invalid_id),
            ("Dashboard Summary", self.test_dashboard_summary),
            ("Clear Data API", self.test_clear_data_api),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            if test_func():
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results Summary:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed, failed, self.test_results

def main():
    """Main test execution"""
    tester = SmartFarmTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "summary": {"passed": passed, "failed": failed, "total": passed + failed},
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to backend_test_results.json")
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)