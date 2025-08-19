# 🚀 Deployment Guide - Smart Farm Monitoring System

Panduan lengkap untuk deploy Smart Farm Monitoring System ke berbagai platform hosting.

## 📋 Overview Deployment Options

| Platform | Type | Kompleksitas | Biaya | Recommended For |
|----------|------|--------------|-------|-----------------|
| **Emergent** | Full-stack | ⭐ Easy | 50 credits/bulan | Quick deployment |
| **Vercel + Railway** | Hybrid | ⭐⭐ Medium | $5-20/bulan | Modern stack |
| **Heroku** | Full-stack | ⭐⭐ Medium | $7-25/bulan | Traditional |
| **DigitalOcean** | VPS | ⭐⭐⭐ Advanced | $12-50/bulan | Full control |
| **Docker** | Container | ⭐⭐⭐ Advanced | Varies | Any platform |

## 🟢 Option 1: Deploy ke Emergent (Recommended)

### Keunggulan Emergent
- ✅ **Paling mudah** - One-click deployment
- ✅ **Full-stack support** - Frontend + Backend + Database
- ✅ **Auto-scaling** dan managed infrastructure
- ✅ **Built-in monitoring** dan logging
- ✅ **Environment management** 

### Step-by-step Emergent Deployment

#### 1. Persiapkan Project
```bash
# Pastikan project sudah di Git repository
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Deploy via Emergent Dashboard
1. **Login** ke dashboard Emergent
2. **Connect repository** yang berisi smart farm project
3. **Preview test** terlebih dahulu menggunakan Preview button
4. **Klik "Deploy"** untuk production deployment
5. **Wait deployment** (biasanya 5-10 menit)
6. **Dapatkan production URL** yang permanent

#### 3. Configuration
```bash
# Environment variables otomatis ter-setup:
# - MONGO_URL: Managed MongoDB instance
# - REACT_APP_BACKEND_URL: Auto-configured backend URL
# - CORS_ORIGINS: Auto-configured
```

#### 4. Custom Domain (Optional)
1. **Beli domain** (contoh: smartfarm-jenggawur.com)
2. **Setup DNS** pointing ke Emergent servers
3. **Configure SSL** certificate (auto)

**💰 Cost**: 50 credits per bulan (~$5-10)

---

## 🔵 Option 2: Vercel (Frontend) + Railway (Backend)

### Architecture
- **Vercel**: Host React frontend (CDN global)
- **Railway**: Host FastAPI backend + MongoDB
- **High performance** dengan separation of concerns

### Step 1: Deploy Backend ke Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login ke Railway
railway login

# Deploy backend
cd backend
railway init
railway up

# Add environment variables di Railway dashboard:
# MONGO_URL: Railway akan provide managed MongoDB
# CORS_ORIGINS: https://your-vercel-app.vercel.app
```

### Step 2: Deploy Frontend ke Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel

# Set environment variables:
# REACT_APP_BACKEND_URL: https://your-app.railway.app
```

### Step 3: Configure Environment Variables

**Railway (Backend)**:
```env
MONGO_URL=mongodb://mongo:27017/smart_farm_jenggawur
DB_NAME=smart_farm_jenggawur  
CORS_ORIGINS=https://smart-farm-jenggawur.vercel.app
```

**Vercel (Frontend)**:
```env
REACT_APP_BACKEND_URL=https://smart-farm-jenggawur.railway.app
```

**💰 Cost**: ~$5-20/bulan (Railway $5 + Vercel free)

---

## 🟣 Option 3: Heroku Full-stack

### Persiapan Heroku Files

#### 1. Create Procfile
```bash
# /Procfile
web: cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT
```

#### 2. Create runtime.txt
```bash
# /runtime.txt
python-3.9.18
```

#### 3. Update requirements.txt
```bash
cd backend
pip freeze > requirements.txt

# Add gunicorn
echo "gunicorn==21.2.0" >> requirements.txt
```

### Deploy ke Heroku

```bash
# Install Heroku CLI
# Download dari: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create smart-farm-jenggawur

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set CORS_ORIGINS=https://smart-farm-jenggawur.herokuapp.com

# Deploy
git add .
git commit -m "Heroku deployment"
git push heroku main

# Scale dyno
heroku ps:scale web=1
```

### Configure Frontend untuk Heroku

Update `frontend/.env`:
```env
REACT_APP_BACKEND_URL=https://smart-farm-jenggawur.herokuapp.com
```

Build dan serve frontend:
```bash
cd frontend
yarn build

# Serve via backend (update server.py)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
```

**💰 Cost**: ~$7-25/bulan

---

## 🔶 Option 4: DigitalOcean VPS

### Setup VPS Server

#### 1. Create Droplet
- **OS**: Ubuntu 22.04
- **Size**: 2GB RAM, 1 CPU ($12/month)
- **Region**: Singapore (closest to Indonesia)

#### 2. Initial Server Setup
```bash
# SSH ke server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip nodejs npm mongodb nginx

# Install yarn
npm install -g yarn

# Create user
adduser smartfarm
usermod -aG sudo smartfarm
su - smartfarm
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/username/smart-farm-monitoring.git
cd smart-farm-monitoring

# Setup backend
cd backend
pip3 install -r requirements.txt

# Setup environment
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="smart_farm_jenggawur"
CORS_ORIGINS="https://your-domain.com"
EOF

# Setup frontend
cd ../frontend
yarn install
yarn build
```

#### 4. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/smartfarm

# Nginx configuration:
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (React build)
    location / {
        root /home/smartfarm/smart-farm-monitoring/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/smartfarm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Setup Process Manager (PM2)
```bash
# Install PM2
npm install -g pm2

# Start backend
cd backend
pm2 start server.py --name smart-farm-backend --interpreter python3

# Auto-start on reboot
pm2 startup
pm2 save
```

#### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**💰 Cost**: ~$12-50/bulan

---

## 🐳 Option 5: Docker Deployment

### Create Docker Files

#### 1. Backend Dockerfile
```dockerfile
# /backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8001

# Run server
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "server:app", "--bind", "0.0.0.0:8001"]
```

#### 2. Frontend Dockerfile
```dockerfile
# /frontend/Dockerfile
FROM node:16-alpine AS builder

WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install

COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Docker Compose
```yaml
# /docker-compose.yml
version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:5.0
    container_name: smart-farm-mongo
    restart: always
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: smart_farm_jenggawur
    ports:
      - "27017:27017"

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: smart-farm-backend
    restart: always
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=smart_farm_jenggawur
      - CORS_ORIGINS=http://localhost:3000
    ports:
      - "8001:8001"
    depends_on:
      - mongodb

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: smart-farm-frontend
    restart: always
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

#### 4. Deploy dengan Docker
```bash
# Build dan start semua services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
docker-compose build
docker-compose up -d
```

---

## 🔧 Production Optimization

### Environment Variables Security

```bash
# Use secrets management
# Jangan commit .env files ke git

# Example production .env
MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/smart_farm_jenggawur"
SECRET_KEY="your-super-secret-key-here"
CORS_ORIGINS="https://smartfarm-jenggawur.com"
```

### Performance Tuning

#### Backend Optimization
```python
# server.py production settings
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Production server
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        workers=4,
        access_log=False
    )
```

#### Frontend Optimization
```bash
# Build with optimizations
cd frontend
yarn build

# Analyze bundle size
npx webpack-bundle-analyzer build/static/js/*.js
```

### Monitoring & Logging

```bash
# Setup application monitoring
# 1. Add logging to backend
# 2. Setup error tracking (Sentry)
# 3. Add health check endpoints
# 4. Monitor database performance
```

## 🛡️ Security Checklist

- ✅ **HTTPS enabled** dengan valid SSL certificate
- ✅ **Environment variables** tidak ter-expose
- ✅ **CORS properly configured** untuk production domains
- ✅ **Database access** restricted dan authenticated  
- ✅ **API rate limiting** enabled
- ✅ **Input validation** di semua endpoints
- ✅ **Regular security updates** untuk dependencies

## 📊 Monitoring Production

### Health Checks
```bash
# Backend health
curl https://your-domain.com/api/

# Database connection
curl https://your-domain.com/api/dashboard

# Frontend performance
lighthouse https://your-domain.com --view
```

### Logging
```bash
# Application logs
tail -f /var/log/smart-farm/app.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

## 🚨 Troubleshooting Deployment

### Common Issues

#### 1. Build Failures
```bash
# Check Node.js version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
yarn install
```

#### 2. Database Connection Issues
```bash
# Check MongoDB connection string
echo $MONGO_URL

# Test connection
mongosh $MONGO_URL --eval "db.runCommand({ping:1})"
```

#### 3. CORS Errors in Production
```bash
# Update backend CORS settings
CORS_ORIGINS="https://your-frontend-domain.com"

# Restart backend server
```

#### 4. SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate validity
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

---

## 🎯 Post-deployment Checklist

- [ ] ✅ **Application accessible** via production URL
- [ ] ✅ **All features working** (sensors, charts, map, controls)
- [ ] ✅ **HTTPS configured** dan certificate valid  
- [ ] ✅ **Database populated** dengan sample data
- [ ] ✅ **Performance acceptable** (page load < 3s)
- [ ] ✅ **Mobile responsive** berfungsi normal
- [ ] ✅ **Error monitoring** setup dan tested
- [ ] ✅ **Backup strategy** implemented
- [ ] ✅ **Custom domain** configured (if applicable)

---

**🌾 Selamat! Smart Farm Desa Jenggawur sudah live di production! 🌾**

*Happy farming dengan teknologi modern!*