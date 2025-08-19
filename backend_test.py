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
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Smart Farm Monitoring System Backend Tests")
        print("=" * 60)
        
        # Test sequence following the smart farm workflow
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Simulate Data", self.test_simulate_data),
            ("Get Zones", self.test_get_zones),
            ("Get Sensors", self.test_get_sensors),
            ("Sensor Alert Logic", self.test_sensor_alert_logic),
            ("Get Irrigation", self.test_get_irrigation),
            ("Activate Irrigation", self.test_activate_irrigation),
            ("Activate Irrigation Invalid ID", self.test_activate_irrigation_invalid_id),
            ("Get Drones", self.test_get_drones),
            ("Drone Mission", self.test_drone_mission),
            ("Drone Mission Invalid ID", self.test_drone_mission_invalid_id),
            ("Dashboard Summary", self.test_dashboard_summary),
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