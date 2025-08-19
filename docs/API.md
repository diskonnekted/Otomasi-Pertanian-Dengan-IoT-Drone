# 📊 API Documentation - Smart Farm Monitoring System

Complete API reference untuk Smart Farm Monitoring System Desa Jenggawur.

## 🌐 Base URL

```
Production: https://farm-sense-control.preview.emergentagent.com/api
Local Dev:  http://localhost:8001/api
```

## 🔑 Authentication

Currently, the API doesn't require authentication for MVP version. For production deployment, consider implementing:

- API Keys for hardware devices
- JWT tokens for web dashboard
- Rate limiting per client

## 📋 API Endpoints Overview

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Health check | No |
| `/dashboard` | GET | Complete dashboard data | No |
| `/sensors` | GET | Get sensor readings | No |
| `/sensors` | POST | Submit sensor data | No |
| `/sensors/historical` | GET | Historical data for charts | No |
| `/zones` | GET | Get farm zones | No |
| `/zones` | POST | Create new zone | No |
| `/irrigation` | GET | Get irrigation systems | No |
| `/irrigation/{id}/activate` | PUT | Activate irrigation | No |
| `/drones` | GET | Get drone fleet | No |
| `/drones/positions` | GET | Get drone positions for map | No |
| `/drones/{id}/mission` | PUT | Assign drone mission | No |
| `/simulate-data` | POST | Generate test data | No |
| `/clear-data` | DELETE | Clear all data | No |

## 🏥 Health Check

### GET `/`

Simple health check endpoint.

**Response:**
```json
{
  "message": "Smart Farm Monitoring System API"
}
```

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/
```

## 📊 Dashboard Data

### GET `/dashboard`

Get complete dashboard summary with all metrics.

**Response:**
```json
{
  "total_zones": 3,
  "active_irrigations": 1,
  "drones_active": 2,
  "critical_alerts": 5,
  "recent_sensor_data": [
    {
      "id": "sensor-uuid",
      "zone_id": "zone-uuid",
      "sensor_type": "soil_moisture",
      "value": 35.2,
      "unit": "%",
      "timestamp": "2025-08-19T10:30:00Z",
      "alert_level": "normal"
    }
  ],
  "irrigation_systems": [...],
  "drone_fleet": [...]
}
```

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/dashboard
```

## 🌡️ Sensor Data

### GET `/sensors`

Get real-time sensor readings with optional filtering.

**Query Parameters:**
- `zone_id` (optional): Filter by specific zone
- `sensor_type` (optional): Filter by sensor type
- `limit` (optional, default: 100): Maximum number of records

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "zone_id": "550e8400-e29b-41d4-a716-446655440001", 
    "sensor_type": "soil_moisture",
    "value": 45.7,
    "unit": "%",
    "timestamp": "2025-08-19T14:30:00Z",
    "alert_level": "normal"
  }
]
```

**Sensor Types:**
- `soil_moisture` - Soil moisture percentage
- `nutrient_n` - Nitrogen level (ppm)
- `nutrient_p` - Phosphorus level (ppm)
- `nutrient_k` - Potassium level (ppm)
- `ph_level` - Soil pH level
- `temperature` - Air temperature (°C)
- `humidity` - Air humidity (%)

**Alert Levels:**
- `normal` - Values within acceptable range
- `warning` - Values approaching threshold
- `critical` - Values requiring immediate attention

**Examples:**
```bash
# Get all sensors
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors"

# Get sensors for specific zone
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors?zone_id=zone-uuid"

# Get only soil moisture readings
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors?sensor_type=soil_moisture&limit=50"
```

### POST `/sensors`

Submit new sensor reading (for Arduino/ESP32 devices).

**Request Body:**
```json
{
  "zone_id": "550e8400-e29b-41d4-a716-446655440001",
  "sensor_type": "soil_moisture",
  "value": 42.5,
  "unit": "%",
  "alert_level": "normal"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "zone_id": "550e8400-e29b-41d4-a716-446655440001",
  "sensor_type": "soil_moisture",
  "value": 42.5,
  "unit": "%",
  "timestamp": "2025-08-19T14:35:00Z",
  "alert_level": "normal"
}
```

**Example:**
```bash
curl -X POST https://farm-sense-control.preview.emergentagent.com/api/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": "your-zone-uuid",
    "sensor_type": "soil_moisture", 
    "value": 42.5,
    "unit": "%",
    "alert_level": "normal"
  }'
```

### GET `/sensors/historical`

Get historical sensor data for charts (hourly aggregated).

**Query Parameters:**
- `hours` (optional, default: 24): Number of hours of historical data
- `zone_id` (optional): Filter by specific zone

**Response:**
```json
{
  "data": [
    {
      "time": "2025-08-19T00:00:00Z",
      "soil_moisture": 45.2,
      "nutrient_n": 67.8,
      "nutrient_p": 23.4,
      "nutrient_k": 56.1,
      "ph_level": 6.8,
      "temperature": 26.5,
      "humidity": 73.2
    }
  ],
  "hours": 24,
  "zone_id": null
}
```

**Examples:**
```bash
# Get 24 hours of data
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors/historical"

# Get 12 hours of data
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors/historical?hours=12"

# Get data for specific zone
curl "https://farm-sense-control.preview.emergentagent.com/api/sensors/historical?zone_id=zone-uuid"
```

## 🌾 Farm Zones

### GET `/zones`

Get all farm zones with their configurations.

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "zone_name": "Zone A - Padi Sawah",
    "area_size": 2.5,
    "crop_type": "Padi",
    "latitude": -7.39222,
    "longitude": 109.6775,
    "irrigation_threshold": {
      "soil_moisture": 35,
      "nutrient_n": 50
    },
    "created_at": "2025-08-19T10:00:00Z"
  }
]
```

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/zones
```

### POST `/zones`

Create a new farm zone.

**Request Body:**
```json
{
  "zone_name": "Zone D - Jagung Manis",
  "area_size": 1.2,
  "crop_type": "Jagung Manis", 
  "latitude": -7.3925,
  "longitude": 109.6780,
  "irrigation_threshold": {
    "soil_moisture": 30,
    "nutrient_n": 45
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "zone_name": "Zone D - Jagung Manis",
  "area_size": 1.2,
  "crop_type": "Jagung Manis",
  "latitude": -7.3925,
  "longitude": 109.6780,
  "irrigation_threshold": {
    "soil_moisture": 30,
    "nutrient_n": 45
  },
  "created_at": "2025-08-19T14:40:00Z"
}
```

## 💧 Irrigation Systems

### GET `/irrigation`

Get all irrigation systems with their status.

**Query Parameters:**
- `zone_id` (optional): Filter by specific zone

**Response:**
```json
[
  {
    "id": "irrigation-uuid",
    "zone_id": "zone-uuid",
    "status": "idle",
    "fertilizer_type": "NPK",
    "flow_rate": 8.5,
    "duration": 15,
    "scheduled_time": null,
    "last_activated": "2025-08-19T12:30:00Z",
    "created_at": "2025-08-19T10:00:00Z"
  }
]
```

**Status Values:**
- `idle` - System is ready but not running
- `active` - Currently irrigating
- `scheduled` - Scheduled to run at specific time
- `maintenance` - Under maintenance

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/irrigation
```

### PUT `/irrigation/{system_id}/activate`

Activate irrigation system for specific duration.

**Query Parameters:**
- `duration` (optional, default: 10): Duration in minutes

**Response:**
```json
{
  "message": "Irrigation system activated",
  "duration": 15
}
```

**Examples:**
```bash
# Activate for default 10 minutes
curl -X PUT https://farm-sense-control.preview.emergentagent.com/api/irrigation/system-uuid/activate

# Activate for 15 minutes
curl -X PUT "https://farm-sense-control.preview.emergentagent.com/api/irrigation/system-uuid/activate?duration=15"
```

**Error Response:**
```json
{
  "detail": "Irrigation system not found"
}
```

## 🚁 Drone Management

### GET `/drones`

Get drone fleet with current status.

**Response:**
```json
[
  {
    "id": "drone-uuid",
    "drone_name": "Drone-Sawah-1",
    "status": "idle",
    "battery_level": 85.0,
    "current_lat": -7.39222,
    "current_lng": 109.6775,
    "target_lat": null,
    "target_lng": null,
    "payload_type": "air",
    "payload_remaining": 75.0,
    "last_updated": "2025-08-19T14:30:00Z"
  }
]
```

**Status Values:**
- `idle` - Drone ready for mission
- `in_flight` - Flying to target location
- `spraying` - Performing spray operation
- `returning` - Returning to base
- `charging` - Battery charging
- `maintenance` - Under maintenance

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/drones
```

### GET `/drones/positions`

Get drone positions optimized for map display.

**Response:**
```json
{
  "drones": [
    {
      "id": "drone-uuid",
      "name": "Drone-Sawah-1",
      "status": "idle",
      "battery": 85.0,
      "payload": 75.0,
      "payload_type": "air",
      "position": [-7.39222, 109.6775],
      "target": null
    }
  ],
  "last_updated": "2025-08-19T14:30:00Z"
}
```

**Example:**
```bash
curl https://farm-sense-control.preview.emergentagent.com/api/drones/positions
```

### PUT `/drones/{drone_id}/mission`

Assign mission to drone with target coordinates.

**Query Parameters:**
- `target_lat` (required): Target latitude
- `target_lng` (required): Target longitude  
- `payload_type` (optional): Type of payload (air, pupuk_organik, pestisida_organik)

**Response:**
```json
{
  "message": "Mission assigned to drone",
  "target": {
    "lat": -7.3925,
    "lng": 109.6780
  }
}
```

**Example:**
```bash
curl -X PUT "https://farm-sense-control.preview.emergentagent.com/api/drones/drone-uuid/mission?target_lat=-7.3925&target_lng=109.6780&payload_type=air"
```

## 🧪 Testing & Utilities

### POST `/simulate-data`

Generate sample data for testing (creates zones, sensors, irrigation systems, drones).

**Response:**
```json
{
  "message": "Historical data generated successfully",
  "sensors_created": 21,
  "hours_generated": 24
}
```

**Example:**
```bash
curl -X POST https://farm-sense-control.preview.emergentagent.com/api/simulate-data
```

### DELETE `/clear-data`

Clear all data from database (useful for testing).

**Response:**
```json
{
  "message": "All data cleared"
}
```

**Example:**
```bash
curl -X DELETE https://farm-sense-control.preview.emergentagent.com/api/clear-data
```

## 🚨 Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Input validation failed |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-08-19T14:30:00Z"
}
```

### Common Errors

#### 404 Not Found
```json
{
  "detail": "Irrigation system not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "value"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

## 📝 Data Models

### Sensor Data Model
```typescript
interface SensorData {
  id: string;
  zone_id: string;
  sensor_type: "soil_moisture" | "nutrient_n" | "nutrient_p" | "nutrient_k" | "ph_level" | "temperature" | "humidity";
  value: number;
  unit: string;
  timestamp: string; // ISO 8601
  alert_level: "normal" | "warning" | "critical";
}
```

### Farm Zone Model
```typescript
interface FarmZone {
  id: string;
  zone_name: string;
  area_size: number; // hectares
  crop_type: string;
  latitude: number;
  longitude: number;
  irrigation_threshold: {
    soil_moisture: number;
    nutrient_n: number;
  };
  created_at: string; // ISO 8601
}
```

### Irrigation System Model
```typescript
interface IrrigationSystem {
  id: string;
  zone_id: string;
  status: "idle" | "active" | "scheduled" | "maintenance";
  fertilizer_type: string;
  flow_rate: number; // L/min
  duration?: number; // minutes
  scheduled_time?: string; // ISO 8601
  last_activated?: string; // ISO 8601
  created_at: string; // ISO 8601
}
```

### Drone Model
```typescript
interface Drone {
  id: string;
  drone_name: string;
  status: "idle" | "in_flight" | "spraying" | "returning" | "charging" | "maintenance";
  battery_level: number; // percentage
  current_lat: number;
  current_lng: number;
  target_lat?: number;
  target_lng?: number;
  payload_type?: string;
  payload_remaining: number; // percentage
  last_updated: string; // ISO 8601
}
```

## 🔄 Rate Limiting

For production deployment, consider implementing rate limiting:

- **Sensor data submission**: 1 request per 10 seconds per device
- **Dashboard API**: 60 requests per minute per IP
- **Control actions**: 10 requests per minute per IP

## 📱 SDK Examples

### JavaScript/TypeScript

```typescript
class SmartFarmAPI {
  constructor(private baseURL: string) {}

  async getSensorData(zoneId?: string): Promise<SensorData[]> {
    const params = zoneId ? `?zone_id=${zoneId}` : '';
    const response = await fetch(`${this.baseURL}/sensors${params}`);
    return response.json();
  }

  async submitSensorReading(data: SensorDataInput): Promise<SensorData> {
    const response = await fetch(`${this.baseURL}/sensors`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async activateIrrigation(systemId: string, duration: number = 10): Promise<void> {
    await fetch(`${this.baseURL}/irrigation/${systemId}/activate?duration=${duration}`, {
      method: 'PUT'
    });
  }
}
```

### Python

```python
import requests
from typing import List, Dict, Optional

class SmartFarmAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_sensor_data(self, zone_id: Optional[str] = None) -> List[Dict]:
        params = {'zone_id': zone_id} if zone_id else {}
        response = requests.get(f"{self.base_url}/sensors", params=params)
        return response.json()
    
    def submit_sensor_reading(self, data: Dict) -> Dict:
        response = requests.post(
            f"{self.base_url}/sensors",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    
    def activate_irrigation(self, system_id: str, duration: int = 10) -> Dict:
        response = requests.put(
            f"{self.base_url}/irrigation/{system_id}/activate",
            params={'duration': duration}
        )
        return response.json()
```

## 🔐 Security Considerations

For production deployment:

1. **Implement API authentication** (JWT tokens)
2. **Add request validation** and sanitization
3. **Set up rate limiting** per endpoint
4. **Use HTTPS** for all communications
5. **Implement API versioning** (/api/v1/)
6. **Add request logging** for monitoring
7. **Validate coordinates** to prevent injection attacks
8. **Implement CORS** properly for production domains

---

**🌾 Smart Farm API ready untuk integrasi IoT dan aplikasi farming! 🌾**

*Complete API documentation untuk sistem pertanian modern Desa Jenggawur.*