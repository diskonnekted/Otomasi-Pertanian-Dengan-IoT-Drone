from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
import random
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums
class SensorType(str, Enum):
    SOIL_MOISTURE = "soil_moisture"
    NUTRIENT_N = "nutrient_n"
    NUTRIENT_P = "nutrient_p" 
    NUTRIENT_K = "nutrient_k"
    PH_LEVEL = "ph_level"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"

class IrrigationStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    MAINTENANCE = "maintenance"

class DroneStatus(str, Enum):
    IDLE = "idle"
    IN_FLIGHT = "in_flight"
    SPRAYING = "spraying"
    RETURNING = "returning"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"


# Models
class SensorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    alert_level: Optional[str] = None  # normal, warning, critical

class SensorDataCreate(BaseModel):
    zone_id: str
    sensor_type: SensorType
    value: float
    unit: str
    alert_level: Optional[str] = None

class IrrigationSystem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_id: str
    status: IrrigationStatus
    fertilizer_type: Optional[str] = None
    flow_rate: float  # liter per minute
    duration: Optional[int] = None  # minutes
    scheduled_time: Optional[datetime] = None
    last_activated: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IrrigationSystemCreate(BaseModel):
    zone_id: str
    status: IrrigationStatus
    fertilizer_type: Optional[str] = None
    flow_rate: float
    duration: Optional[int] = None
    scheduled_time: Optional[datetime] = None

class DroneData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    drone_name: str
    status: DroneStatus
    battery_level: float  # percentage
    current_lat: float
    current_lng: float
    target_lat: Optional[float] = None
    target_lng: Optional[float] = None
    payload_type: Optional[str] = None  # water, fertilizer, pesticide
    payload_remaining: float  # percentage
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DroneDataCreate(BaseModel):
    drone_name: str
    status: DroneStatus
    battery_level: float
    current_lat: float
    current_lng: float
    target_lat: Optional[float] = None
    target_lng: Optional[float] = None
    payload_type: Optional[str] = None
    payload_remaining: float = 100.0

class FarmZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_name: str
    area_size: float  # hectares
    crop_type: str
    latitude: float
    longitude: float
    irrigation_threshold: dict  # {"soil_moisture": 30, "nutrient_n": 50}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FarmZoneCreate(BaseModel):
    zone_name: str
    area_size: float
    crop_type: str
    latitude: float
    longitude: float
    irrigation_threshold: dict

class DashboardSummary(BaseModel):
    total_zones: int
    active_irrigations: int
    drones_active: int
    critical_alerts: int
    recent_sensor_data: List[SensorData]
    irrigation_systems: List[IrrigationSystem]
    drone_fleet: List[DroneData]


# Routes
@api_router.get("/")
async def root():
    return {"message": "Smart Farm Monitoring System API"}

# Sensor Data Endpoints
@api_router.post("/sensors", response_model=SensorData)
async def create_sensor_data(sensor_data: SensorDataCreate):
    sensor_dict = sensor_data.dict()
    sensor_obj = SensorData(**sensor_dict)
    await db.sensor_data.insert_one(sensor_obj.dict())
    return sensor_obj

@api_router.get("/sensors", response_model=List[SensorData])
async def get_sensor_data(zone_id: Optional[str] = None, sensor_type: Optional[str] = None, limit: int = 100):
    query = {}
    if zone_id:
        query["zone_id"] = zone_id
    if sensor_type:
        query["sensor_type"] = sensor_type
    
    sensors = await db.sensor_data.find(query).sort("timestamp", -1).limit(limit).to_list(length=None)
    return [SensorData(**sensor) for sensor in sensors]

# Farm Zones Endpoints
@api_router.post("/zones", response_model=FarmZone)
async def create_farm_zone(zone: FarmZoneCreate):
    zone_dict = zone.dict()
    zone_obj = FarmZone(**zone_dict)
    await db.farm_zones.insert_one(zone_obj.dict())
    return zone_obj

@api_router.get("/zones", response_model=List[FarmZone])
async def get_farm_zones():
    zones = await db.farm_zones.find().to_list(length=None)
    return [FarmZone(**zone) for zone in zones]

# Irrigation System Endpoints
@api_router.post("/irrigation", response_model=IrrigationSystem)
async def create_irrigation_system(irrigation: IrrigationSystemCreate):
    irrigation_dict = irrigation.dict()
    irrigation_obj = IrrigationSystem(**irrigation_dict)
    await db.irrigation_systems.insert_one(irrigation_obj.dict())
    return irrigation_obj

@api_router.get("/irrigation", response_model=List[IrrigationSystem])
async def get_irrigation_systems(zone_id: Optional[str] = None):
    query = {}
    if zone_id:
        query["zone_id"] = zone_id
        
    systems = await db.irrigation_systems.find(query).sort("created_at", -1).to_list(length=None)
    return [IrrigationSystem(**system) for system in systems]

@api_router.put("/irrigation/{system_id}/activate")
async def activate_irrigation(system_id: str, duration: int = 10):
    result = await db.irrigation_systems.update_one(
        {"id": system_id},
        {
            "$set": {
                "status": IrrigationStatus.ACTIVE,
                "duration": duration,
                "last_activated": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Irrigation system not found")
    return {"message": "Irrigation system activated", "duration": duration}

# Drone Endpoints
@api_router.post("/drones", response_model=DroneData)
async def create_drone(drone: DroneDataCreate):
    drone_dict = drone.dict()
    drone_obj = DroneData(**drone_dict)
    await db.drones.insert_one(drone_obj.dict())
    return drone_obj

@api_router.get("/drones", response_model=List[DroneData])
async def get_drones():
    drones = await db.drones.find().sort("last_updated", -1).to_list(length=None)
    return [DroneData(**drone) for drone in drones]

@api_router.put("/drones/{drone_id}/mission")
async def send_drone_mission(drone_id: str, target_lat: float, target_lng: float, payload_type: str):
    result = await db.drones.update_one(
        {"id": drone_id},
        {
            "$set": {
                "status": DroneStatus.IN_FLIGHT,
                "target_lat": target_lat,
                "target_lng": target_lng,
                "payload_type": payload_type,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Drone not found")
    return {"message": "Mission assigned to drone", "target": {"lat": target_lat, "lng": target_lng}}

@api_router.get("/sensors/historical")
async def get_historical_sensor_data(zone_id: Optional[str] = None, hours: int = 24):
    """Get historical sensor data for charts - hourly aggregated"""
    # Calculate time range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    query = {"timestamp": {"$gte": start_time.isoformat(), "$lt": end_time.isoformat()}}
    if zone_id:
        query["zone_id"] = zone_id
    
    # Get sensor data and group by hour
    sensors = await db.sensor_data.find(query).sort("timestamp", 1).to_list(length=None)
    
    # Group data by hour and sensor type
    hourly_data = {}
    for sensor in sensors:
        # Handle both string and datetime timestamp formats
        timestamp_str = sensor["timestamp"]
        if isinstance(timestamp_str, str):
            if timestamp_str.endswith('Z'):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = timestamp_str
            
        hour_key = timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        sensor_type = sensor["sensor_type"]
        
        if hour_key not in hourly_data:
            hourly_data[hour_key] = {}
        
        if sensor_type not in hourly_data[hour_key]:
            hourly_data[hour_key][sensor_type] = []
        
        hourly_data[hour_key][sensor_type].append(sensor["value"])
    
    # Calculate averages for each hour
    chart_data = []
    for hour_key in sorted(hourly_data.keys()):
        hour_data = {"time": hour_key}
        for sensor_type, values in hourly_data[hour_key].items():
            hour_data[sensor_type] = sum(values) / len(values) if values else 0
        chart_data.append(hour_data)
    
    return {"data": chart_data, "hours": hours, "zone_id": zone_id}

@api_router.get("/drones/positions")
async def get_drone_positions():
    """Get real-time drone positions for map"""
    drones = await db.drones.find().to_list(length=None)
    positions = []
    
    for drone in drones:
        position = {
            "id": drone["id"],
            "name": drone["drone_name"],
            "status": drone["status"],
            "battery": drone["battery_level"],
            "payload": drone["payload_remaining"],
            "payload_type": drone.get("payload_type", "unknown"),
            "position": [drone["current_lat"], drone["current_lng"]],
            "target": [drone.get("target_lat"), drone.get("target_lng")] if drone.get("target_lat") else None
        }
        positions.append(position)
    
    return {"drones": positions, "last_updated": datetime.now(timezone.utc).isoformat()}

# Dashboard Summary
@api_router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary():
    # Get counts
    total_zones = await db.farm_zones.count_documents({})
    active_irrigations = await db.irrigation_systems.count_documents({"status": IrrigationStatus.ACTIVE})
    drones_active = await db.drones.count_documents({"status": {"$in": [DroneStatus.IN_FLIGHT, DroneStatus.SPRAYING]}})
    critical_alerts = await db.sensor_data.count_documents({"alert_level": "critical"})
    
    # Get recent data
    recent_sensors = await db.sensor_data.find().sort("timestamp", -1).limit(10).to_list(length=None)
    irrigation_systems = await db.irrigation_systems.find().sort("created_at", -1).limit(5).to_list(length=None)
    drone_fleet = await db.drones.find().sort("last_updated", -1).to_list(length=None)
    
    return DashboardSummary(
        total_zones=total_zones,
        active_irrigations=active_irrigations,
        drones_active=drones_active,
        critical_alerts=critical_alerts,
        recent_sensor_data=[SensorData(**sensor) for sensor in recent_sensors],
        irrigation_systems=[IrrigationSystem(**system) for system in irrigation_systems],
        drone_fleet=[DroneData(**drone) for drone in drone_fleet]
    )

# Clear all data for fresh simulation
@api_router.delete("/clear-data")
async def clear_all_data():
    """Clear all data for fresh simulation"""
    await db.sensor_data.delete_many({})
    await db.farm_zones.delete_many({})
    await db.irrigation_systems.delete_many({})
    await db.drones.delete_many({})
    return {"message": "All data cleared"}

@api_router.post("/simulate-data")
async def simulate_sensor_data():
    """Generate sample sensor data for testing"""
    zones = await db.farm_zones.find().to_list(length=None)
    
    if not zones:
        # Create sample zones first
        sample_zones = [
            FarmZone(zone_name="Zone A - Tomat", area_size=2.5, crop_type="Tomat", latitude=-6.2088, longitude=106.8456, irrigation_threshold={"soil_moisture": 30, "nutrient_n": 50}),
            FarmZone(zone_name="Zone B - Cabai", area_size=1.8, crop_type="Cabai", latitude=-6.2090, longitude=106.8460, irrigation_threshold={"soil_moisture": 25, "nutrient_n": 45}),
            FarmZone(zone_name="Zone C - Selada", area_size=3.2, crop_type="Selada", latitude=-6.2085, longitude=106.8465, irrigation_threshold={"soil_moisture": 35, "nutrient_n": 40}),
        ]
        
        for zone in sample_zones:
            await db.farm_zones.insert_one(zone.dict())
        
        zones = await db.farm_zones.find().to_list(length=None)
    
    # Generate historical data for the last 24 hours
    current_time = datetime.now(timezone.utc)
    sensor_types_config = [
        (SensorType.SOIL_MOISTURE, (15, 80), "%"),
        (SensorType.NUTRIENT_N, (20, 100), "ppm"),
        (SensorType.NUTRIENT_P, (10, 80), "ppm"),
        (SensorType.NUTRIENT_K, (15, 90), "ppm"),
        (SensorType.PH_LEVEL, (5.5, 7.5), "pH"),
        (SensorType.TEMPERATURE, (22, 35), "°C"),
        (SensorType.HUMIDITY, (40, 90), "%"),
    ]
    
    created_sensors = []
    
    # Generate data for the last 24 hours (hourly)
    for hour_offset in range(24):
        timestamp = current_time - timedelta(hours=hour_offset)
        
        for zone in zones:
            for sensor_type, (min_val, max_val), unit in sensor_types_config:
                # Add some trend and randomness
                base_value = random.uniform(min_val, max_val)
                
                # Add some realistic trends
                if sensor_type == SensorType.SOIL_MOISTURE:
                    # Moisture tends to decrease during day, increase at night
                    hour = timestamp.hour
                    if 6 <= hour <= 18:  # Daytime
                        base_value -= random.uniform(5, 15)
                    else:  # Nighttime
                        base_value += random.uniform(2, 8)
                    base_value = max(min_val, min(max_val, base_value))
                
                elif sensor_type in [SensorType.NUTRIENT_N, SensorType.NUTRIENT_P, SensorType.NUTRIENT_K]:
                    # Nutrients decrease over time, spike after fertilization
                    if hour_offset == 8 or hour_offset == 16:  # Fertilization times
                        base_value += random.uniform(20, 40)
                    else:
                        base_value -= hour_offset * random.uniform(0.5, 2)
                    base_value = max(min_val, min(max_val, base_value))
                
                elif sensor_type == SensorType.TEMPERATURE:
                    # Temperature varies by time of day
                    hour = timestamp.hour
                    if 10 <= hour <= 16:  # Midday
                        base_value += random.uniform(5, 10)
                    elif hour <= 6 or hour >= 20:  # Night
                        base_value -= random.uniform(3, 8)
                    base_value = max(min_val, min(max_val, base_value))
                
                value = round(base_value, 1)
                
                # Determine alert level
                alert_level = "normal"
                if sensor_type == SensorType.SOIL_MOISTURE and value < 30:
                    alert_level = "critical" if value < 20 else "warning"
                elif sensor_type in [SensorType.NUTRIENT_N, SensorType.NUTRIENT_P, SensorType.NUTRIENT_K] and value < 40:
                    alert_level = "critical" if value < 25 else "warning"
                
                sensor_data = SensorData(
                    zone_id=zone["id"],
                    sensor_type=sensor_type,
                    value=value,
                    unit=unit,
                    alert_level=alert_level,
                    timestamp=timestamp
                )
                
                await db.sensor_data.insert_one(sensor_data.dict())
                if hour_offset == 0:  # Only count current data
                    created_sensors.append(sensor_data)
    
    # Create sample irrigation systems
    irrigation_count = await db.irrigation_systems.count_documents({})
    if irrigation_count == 0:
        for zone in zones:
            irrigation = IrrigationSystem(
                zone_id=zone["id"],
                status=random.choice([IrrigationStatus.IDLE, IrrigationStatus.SCHEDULED]),
                fertilizer_type=random.choice(["NPK", "Organik", "Urea"]),
                flow_rate=random.uniform(5.0, 15.0)
            )
            await db.irrigation_systems.insert_one(irrigation.dict())
    
    # Create sample drones with realistic positions
    drone_count = await db.drones.count_documents({})
    if drone_count == 0:
        sample_drones = [
            DroneData(drone_name="Drone-1", status=DroneStatus.IDLE, battery_level=85.0, 
                     current_lat=-6.2088, current_lng=106.8456, payload_remaining=75.0, payload_type="water"),
            DroneData(drone_name="Drone-2", status=DroneStatus.IN_FLIGHT, battery_level=65.0, 
                     current_lat=-6.2090, current_lng=106.8460, target_lat=-6.2085, target_lng=106.8465,
                     payload_remaining=90.0, payload_type="fertilizer"),
            DroneData(drone_name="Drone-3", status=DroneStatus.CHARGING, battery_level=25.0, 
                     current_lat=-6.2085, current_lng=106.8465, payload_remaining=100.0, payload_type="pesticide"),
        ]
        for drone in sample_drones:
            await db.drones.insert_one(drone.dict())
    
    return {"message": "Historical data generated successfully", "sensors_created": len(created_sensors), "hours_generated": 24}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()