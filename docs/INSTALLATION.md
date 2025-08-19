# 🛠️ Installation Guide - Smart Farm Monitoring System

Panduan lengkap untuk menginstall dan menjalankan Smart Farm Monitoring System secara lokal.

## 📋 Prerequisites

Pastikan sistem Anda memiliki:

- **Node.js** v16.0.0 atau lebih tinggi
- **Python** v3.8.0 atau lebih tinggi  
- **MongoDB** v5.0 atau lebih tinggi
- **yarn** package manager
- **Git** untuk cloning repository

### Cek Versi Prerequisites

```bash
# Check Node.js version
node --version

# Check Python version
python --version

# Check MongoDB status
mongosh --eval "db.runCommand({connectionStatus : 1})"

# Check yarn
yarn --version
```

## 🗂️ Project Structure Overview

```
smart-farm-monitoring/
├── backend/                 # FastAPI Python Backend
│   ├── server.py           # Main server file
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling
│   │   └── index.js       # Entry point
│   ├── package.json       # Node.js dependencies
│   └── .env              # Frontend environment variables
└── docs/                  # Documentation
```

## ⚡ Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/username/smart-farm-monitoring.git
cd smart-farm-monitoring
```

### 2. Setup Backend

```bash
cd backend

# Install Python dependencies
pip install fastapi motor pymongo python-dotenv pydantic uvicorn

# Create environment file
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="smart_farm_jenggawur"
CORS_ORIGINS="http://localhost:3000"
EOF

# Start backend server
python server.py
```

Backend akan tersedia di: `http://localhost:8001`

### 3. Setup Frontend (Terminal Baru)

```bash
cd frontend

# Install dependencies
yarn install

# Create environment file
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
EOF

# Start frontend
yarn start
```

Frontend akan tersedia di: `http://localhost:3000`

### 4. Generate Test Data

```bash
# Generate sample data untuk testing
curl -X POST http://localhost:8001/api/simulate-data
```

## 🔧 Detailed Setup

### Backend Setup Lengkap

#### Step 1: Install Python Dependencies

```bash
cd backend

# Method 1: Install dari requirements.txt
pip install -r requirements.txt

# Method 2: Install manual
pip install fastapi==0.104.1
pip install motor==3.3.2
pip install pymongo==4.6.0
pip install python-dotenv==1.0.0
pip install pydantic==2.5.0
pip install uvicorn[standard]==0.24.0
```

#### Step 2: MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
mongosh --eval "db.runCommand({connectionStatus : 1})"
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# Dapatkan connection string dari MongoDB Atlas
# Update .env file:
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/"
```

#### Step 3: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

File `.env` untuk backend:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="smart_farm_jenggawur"
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
```

#### Step 4: Start Backend Server

```bash
# Method 1: Direct Python
python server.py

# Method 2: Uvicorn (production-like)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Method 3: Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001
```

### Frontend Setup Lengkap

#### Step 1: Install Node.js Dependencies

```bash
cd frontend

# Install all dependencies
yarn install

# Or install manually
yarn add react@18.2.0
yarn add react-dom@18.2.0
yarn add react-router-dom@6.8.0
yarn add axios@1.6.2
yarn add recharts@2.8.0
yarn add react-leaflet@4.2.1
yarn add leaflet@1.9.4
```

#### Step 2: Environment Configuration

File `.env` untuk frontend:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
```

#### Step 3: Tailwind CSS Setup (if not configured)

```bash
# Install Tailwind CSS
yarn add -D tailwindcss@3.3.6
yarn add -D postcss@8.4.32
yarn add -D autoprefixer@10.4.16

# Initialize Tailwind config
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

#### Step 4: Start Frontend

```bash
# Development mode with hot reload
yarn start

# Build for production
yarn build

# Test production build locally
yarn add -g serve
serve -s build
```

## 🧪 Verification & Testing

### 1. Backend Health Check

```bash
# Test API health
curl http://localhost:8001/api/

# Expected response:
{"message":"Smart Farm Monitoring System API"}

# Test dashboard endpoint
curl http://localhost:8001/api/dashboard | jq
```

### 2. Frontend Verification

1. Buka browser ke `http://localhost:3000`
2. Verifikasi dashboard load dengan benar
3. Check browser console untuk errors
4. Test responsive design di mobile view

### 3. Full System Test

```bash
# Generate test data
curl -X POST http://localhost:8001/api/simulate-data

# Verify data in frontend
# 1. Sensor cards menampilkan data
# 2. Charts menampilkan trend 24 jam  
# 3. Map menampilkan drone positions
# 4. Controls berfungsi normal
```

## 🚨 Common Issues & Solutions

### Issue 1: Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Pastikan virtual environment aktif
pip install -r backend/requirements.txt

# Or install global
sudo pip install fastapi motor pymongo
```

### Issue 2: Frontend Build Errors

**Error**: `Module not found: Can't resolve 'react-leaflet'`

**Solution**:
```bash
cd frontend
rm -rf node_modules yarn.lock
yarn install
yarn start
```

### Issue 3: MongoDB Connection Failed

**Error**: `ServerSelectionTimeoutError`

**Solution**:
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check connection string in .env
cat backend/.env
```

### Issue 4: CORS Issues

**Error**: `Access to fetch blocked by CORS policy`

**Solution**:
```bash
# Update backend/.env
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# Restart backend server
```

### Issue 5: Charts Not Rendering

**Error**: Charts show as empty or don't load

**Solution**:
```bash
# Clear data dan regenerate
curl -X DELETE http://localhost:8001/api/clear-data
curl -X POST http://localhost:8001/api/simulate-data

# Check browser console for JavaScript errors
# Refresh browser
```

## 🔄 Development Workflow

### Daily Development

```bash
# Terminal 1: Backend
cd backend
python server.py

# Terminal 2: Frontend  
cd frontend
yarn start

# Terminal 3: MongoDB (if local)
mongosh smart_farm_jenggawur
```

### Code Changes

```bash
# Backend changes - server auto-reloads
# Edit backend/server.py

# Frontend changes - hot reload active
# Edit frontend/src/App.js

# Database changes - use MongoDB compass or CLI
mongosh smart_farm_jenggawur
```

### Production Preparation

```bash
# Backend production server
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app

# Frontend production build
cd frontend
yarn build
```

## 💾 Data Management

### Backup Data

```bash
# MongoDB backup
mongodump --db smart_farm_jenggawur --out ./backup

# Restore from backup
mongorestore --db smart_farm_jenggawur ./backup/smart_farm_jenggawur
```

### Reset Development Data

```bash
# Clear all data
curl -X DELETE http://localhost:8001/api/clear-data

# Generate fresh sample data
curl -X POST http://localhost:8001/api/simulate-data
```

## 📈 Performance Optimization

### Backend Optimization

```python
# Add to server.py for production
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        workers=4,
        loop="uvloop",
        http="httptools"
    )
```

### Frontend Optimization

```javascript
// Add to App.js for production
import { memo, useMemo } from 'react';

const OptimizedComponent = memo(() => {
  const memoizedValue = useMemo(() => {
    // expensive calculation
  }, [dependencies]);
});
```

## 🎯 Next Steps

Setelah installation berhasil:

1. ✅ **Customize data zones** - Edit farm zones sesuai lokasi
2. ✅ **Integrate real sensors** - Connect Arduino/ESP32
3. ✅ **Deploy to production** - Setup hosting
4. ✅ **Monitor & maintain** - Setup logging dan alerts

---

**🌾 Happy Farming dengan Smart Technology! 🌾**