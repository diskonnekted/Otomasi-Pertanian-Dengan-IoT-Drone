# 🌾 Smart Farm Monitoring System - Desa Jenggawur

> Sistem monitoring smart farm real-time dengan IoT sensors, automated irrigation, dan drone control untuk Desa Jenggawur, Kabupaten Banjarnegara, Jawa Tengah.

![Smart Farm Dashboard](docs/dashboard_overview.png)

## 📋 **Deskripsi Project**

Smart Farm Monitoring System adalah aplikasi web modern yang memungkinkan monitoring dan kontrol sistem pertanian otomatis dengan fitur:

- **Real-time sensor monitoring** (kelembaban tanah, nutrisi N-P-K, pH, suhu, kelembaban udara)
- **Interactive trend charts** untuk analisis data 24 jam
- **Live drone tracking** dengan peta interaktif Leaflet
- **Automated irrigation system** dengan kontrol per zona
- **Alert system** dengan threshold monitoring
- **Responsive design** untuk desktop dan mobile

## 🚀 **Live Demo**

- **Demo URL**: [https://farm-sense-control.preview.emergentagent.com](https://farm-sense-control.preview.emergentagent.com)
- **Lokasi**: Desa Jenggawur, Kabupaten Banjarnegara, Jawa Tengah
- **Koordinat**: -7.392220°, 109.677500°

## 📷 **Screenshots**

### Dashboard Overview
Akses langsung ke [Live Demo](https://farm-sense-control.preview.emergentagent.com) untuk melihat:
- *Real-time sensor monitoring dengan alert system*

### Interactive Charts  
- *Trend analysis untuk kelembaban tanah dan nutrisi tanaman*

### Live Drone Map
- *Peta real-time dengan tracking drone dan flight paths*

### Control Systems
- *Sistem kontrol irigasi dan drone management*

### Mobile Responsive
- *Tampilan mobile-friendly untuk monitoring di lapangan*

## 📁 **Project Structure**

```
smart-farm-monitoring/
├── backend/
│   ├── server.py          # FastAPI server utama
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # React component utama
│   │   ├── App.css       # Styling dengan Tailwind
│   │   └── index.js      # Entry point
│   ├── package.json      # Node.js dependencies
│   ├── tailwind.config.js
│   └── .env              # Frontend environment
├── docs/                 # Documentation assets
├── scripts/              # Utility scripts
└── README.md            # Documentation
```

## ⚙️ **Installation & Setup**

### Prerequisites

- **Node.js** v16+ dan yarn
- **Python** 3.8+ dan pip
- **MongoDB** (local atau cloud)

### 1. Clone Repository

```bash
git clone https://github.com/username/smart-farm-monitoring.git
cd smart-farm-monitoring
```

### 2. Backend Setup

```bash
# Masuk ke direktori backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env sesuai konfigurasi:
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="smart_farm_db"
# CORS_ORIGINS="http://localhost:3000"

# Jalankan server
python server.py
```

Server akan berjalan di `http://localhost:8001`

### 3. Frontend Setup

```bash
# Masuk ke direktori frontend (terminal baru)
cd frontend

# Install dependencies
yarn install

# Setup environment variables
cp .env.example .env
# Edit .env:
# REACT_APP_BACKEND_URL=http://localhost:8001

# Jalankan development server
yarn start
```

Frontend akan berjalan di `http://localhost:3000`

### 4. Generate Sample Data

```bash
# Generate data simulasi untuk testing
curl -X POST http://localhost:8001/api/simulate-data
```

## 🌐 **Deployment Guide**

### Option 1: Deploy ke Emergent (Recommended)

1. **Push ke repository** yang sudah terintegrasi dengan Emergent
2. **Preview testing** menggunakan preview URL
3. **Deploy production**:
   ```bash
   # Klik tombol "Deploy" di dashboard Emergent
   # Atau menggunakan CLI jika tersedia
   ```

**Biaya**: 50 credits/bulan untuk hosting production

### Option 2: Deploy ke VPS/Cloud Server

#### Prepare for Production

```bash
# Backend - Setup production server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001

# Frontend - Build for production
cd frontend
yarn build

# Serve static files dengan Nginx atau Apache
```

#### Docker Deployment

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "server:app", "--bind", "0.0.0.0:8001"]

# Dockerfile.frontend  
FROM node:16-alpine
WORKDIR /app
COPY frontend/package.json frontend/yarn.lock .
RUN yarn install
COPY frontend/ .
RUN yarn build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:5.0
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
      
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=smart_farm_db
      
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

### Option 3: Deploy ke Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
heroku create smart-farm-app
git push heroku main
```

#### Vercel (Frontend) + Railway (Backend)
```bash
# Frontend ke Vercel
vercel --prod

# Backend ke Railway
railway login
railway init
railway up
```

## 🔧 **Hardware Integration**

### Arduino/ESP32 Integration

Sistem sudah siap untuk integrasi dengan hardware IoT:

#### Sensor Data Endpoint
```bash
POST /api/sensors
Content-Type: application/json

{
  "zone_id": "zone-uuid",
  "sensor_type": "soil_moisture",
  "value": 45.2,
  "unit": "%",
  "alert_level": "normal"
}
```

#### Sample Arduino Code
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "https://your-domain.com/api/sensors";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
}

void sendSensorData(float soilMoisture, float temperature) {
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  
  DynamicJsonDocument doc(1024);
  doc["zone_id"] = "your-zone-id";
  doc["sensor_type"] = "soil_moisture";
  doc["value"] = soilMoisture;
  doc["unit"] = "%";
  doc["alert_level"] = soilMoisture < 30 ? "warning" : "normal";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  Serial.println("HTTP Response: " + String(httpResponseCode));
  
  http.end();
}
```

## 📊 **API Documentation**

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | Health check |
| GET | `/api/dashboard` | Complete dashboard data |
| GET | `/api/sensors` | Real-time sensor data |
| POST | `/api/sensors` | Add new sensor reading |
| GET | `/api/sensors/historical` | Historical data for charts |
| GET | `/api/zones` | Farm zones information |
| GET | `/api/irrigation` | Irrigation systems status |
| PUT | `/api/irrigation/{id}/activate` | Activate irrigation |
| GET | `/api/drones` | Drone fleet status |
| GET | `/api/drones/positions` | Drone positions for map |
| PUT | `/api/drones/{id}/mission` | Assign drone mission |
| POST | `/api/simulate-data` | Generate test data |

### Response Examples

#### Dashboard Summary
```json
{
  "total_zones": 3,
  "active_irrigations": 1,
  "drones_active": 2,
  "critical_alerts": 5,
  "recent_sensor_data": [...],
  "irrigation_systems": [...],
  "drone_fleet": [...]
}
```

#### Sensor Data
```json
{
  "id": "sensor-uuid",
  "zone_id": "zone-uuid", 
  "sensor_type": "soil_moisture",
  "value": 35.2,
  "unit": "%",
  "timestamp": "2025-08-19T10:30:00Z",
  "alert_level": "normal"
}
```

## 🚨 **Troubleshooting**

### Common Issues

#### 1. Backend tidak start
```bash
# Check Python dependencies
pip install -r backend/requirements.txt

# Check MongoDB connection
# Pastikan MongoDB running di localhost:27017
mongosh # test connection
```

#### 2. Frontend tidak load data
```bash
# Check environment variables
cat frontend/.env
# Pastikan REACT_APP_BACKEND_URL correct

# Check CORS settings
# Tambahkan frontend URL ke CORS_ORIGINS di backend/.env
```

#### 3. Charts tidak muncul
```bash
# Clear data dan regenerate
curl -X DELETE http://localhost:8001/api/clear-data
curl -X POST http://localhost:8001/api/simulate-data
```

#### 4. Map tidak load
```bash
# Check Leaflet CSS import di App.css
# Pastikan internet connection untuk tiles
```

### Development Tips

```bash
# Monitor backend logs
tail -f /var/log/supervisor/backend.err.log

# Hot reload frontend
yarn start

# Test API endpoints
curl http://localhost:8001/api/dashboard | jq
```

## 🤝 **Contributing**

1. Fork repository
2. Buat feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push ke branch (`git push origin feature/new-feature`)
5. Buat Pull Request

## 📄 **License**

MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 👥 **Credits**

- **Developer**: Smart Farm Team
- **Location**: Desa Jenggawur, Kabupaten Banjarnegara
- **Maps**: OpenStreetMap contributors
- **Icons**: Tailwind UI & Custom emojis

## 📧 **Contact & Support**

- **Issues**: [GitHub Issues](https://github.com/username/smart-farm-monitoring/issues)
- **Discussion**: [GitHub Discussions](https://github.com/username/smart-farm-monitoring/discussions)
- **Email**: support@smartfarm-jenggawur.com

---

**🌾 Smart Farm Desa Jenggawur - Teknologi untuk Pertanian Berkelanjutan 🌾**

*Built with ❤️ for Indonesian Agriculture*
