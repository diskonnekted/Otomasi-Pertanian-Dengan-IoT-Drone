import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default Leaflet markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SensorChart = ({ title, data, dataKeys, colors }) => {
  const formatTime = (timeStr) => {
    const date = new Date(timeStr);
    return date.toLocaleTimeString('id-ID', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              tickFormatter={formatTime}
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip 
              labelFormatter={(value) => `Waktu: ${formatTime(value)}`}
              formatter={(value, name) => [
                `${value?.toFixed(1) || 0}`, 
                name === 'soil_moisture' ? 'Kelembaban Tanah (%)' : 
                name === 'nutrient_n' ? 'Nitrogen (ppm)' :
                name === 'nutrient_p' ? 'Fosfor (ppm)' :
                name === 'nutrient_k' ? 'Kalium (ppm)' : name
              ]}
            />
            <Legend />
            {dataKeys.map((key, index) => (
              <Line 
                key={key}
                type="monotone" 
                dataKey={key} 
                stroke={colors[index]}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                name={
                  key === 'soil_moisture' ? 'Kelembaban Tanah' : 
                  key === 'nutrient_n' ? 'Nitrogen' :
                  key === 'nutrient_p' ? 'Fosfor' :
                  key === 'nutrient_k' ? 'Kalium' : key
                }
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const DroneMap = ({ dronePositions }) => {
  // Custom drone icons based on status
  const getDroneIcon = (status, battery) => {
    const getColor = () => {
      if (status === 'in_flight' || status === 'spraying') return '#10b981'; // green
      if (status === 'charging') return '#f59e0b'; // yellow
      if (status === 'maintenance') return '#ef4444'; // red
      return '#6b7280'; // gray
    };

    return L.divIcon({
      html: `<div style="
        background-color: ${getColor()};
        border: 2px solid white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      ">
        <div style="
          position: absolute;
          top: -25px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.7);
          color: white;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 10px;
          white-space: nowrap;
        ">🚁 ${battery.toFixed(0)}%</div>
      </div>`,
      className: 'drone-marker',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🗺️ Peta Drone Real-time</h3>
      <div className="h-80 rounded-lg overflow-hidden border">
        <MapContainer 
          center={[-6.2088, 106.8456]} 
          zoom={15} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {dronePositions?.map((drone, index) => (
            <React.Fragment key={drone.id}>
              {/* Drone position marker */}
              <Marker 
                position={drone.position} 
                icon={getDroneIcon(drone.status, drone.battery)}
              >
                <Popup>
                  <div className="text-sm">
                    <div className="font-bold text-blue-600">{drone.name}</div>
                    <div className="mt-1 space-y-1">
                      <div>Status: <span className={`font-medium ${
                        drone.status === 'in_flight' ? 'text-blue-600' :
                        drone.status === 'spraying' ? 'text-green-600' :
                        drone.status === 'charging' ? 'text-yellow-600' :
                        drone.status === 'maintenance' ? 'text-red-600' : 'text-gray-600'
                      }`}>{drone.status}</span></div>
                      <div>Baterai: <span className={`font-medium ${
                        drone.battery > 50 ? 'text-green-600' : 
                        drone.battery > 20 ? 'text-yellow-600' : 'text-red-600'
                      }`}>{drone.battery.toFixed(0)}%</span></div>
                      <div>Muatan: {drone.payload.toFixed(0)}% ({drone.payload_type})</div>
                      <div className="text-xs text-gray-500">
                        Posisi: {drone.position[0].toFixed(4)}, {drone.position[1].toFixed(4)}
                      </div>
                    </div>
                  </div>
                </Popup>
              </Marker>
              
              {/* Flight path to target */}
              {drone.target && drone.target[0] && drone.target[1] && (
                <>
                  <Polyline 
                    positions={[drone.position, drone.target]}
                    color="#3b82f6"
                    weight={2}
                    opacity={0.7}
                    dashArray="5, 10"
                  />
                  <Marker position={drone.target}>
                    <Popup>
                      <div className="text-sm">
                        <div className="font-bold text-red-600">🎯 Target {drone.name}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {drone.target[0].toFixed(4)}, {drone.target[1].toFixed(4)}
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                </>
              )}
            </React.Fragment>
          ))}
        </MapContainer>
      </div>
      
      {/* Map legend */}
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span>Aktif/Penyiraman</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span>Charging</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
          <span>Idle</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span>Maintenance</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 border-2 border-blue-500 border-dashed bg-transparent rounded-full"></div>
          <span>Jalur Terbang</span>
        </div>
      </div>
    </div>
  );
};

// Components
const SensorCard = ({ title, value, unit, alertLevel, icon }) => {
  const getAlertColor = (level) => {
    switch (level) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-green-500 bg-green-50';
    }
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${getAlertColor(alertLevel)} transition-all hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <div className="flex items-baseline mt-1">
            <span className="text-2xl font-bold text-gray-900">{value}</span>
            <span className="text-sm text-gray-500 ml-1">{unit}</span>
          </div>
        </div>
        <div className="text-2xl">{icon}</div>
      </div>
      {alertLevel !== 'normal' && (
        <div className={`mt-2 text-xs font-medium ${alertLevel === 'critical' ? 'text-red-600' : 'text-yellow-600'}`}>
          {alertLevel === 'critical' ? '⚠️ Critical' : '⚡ Warning'}
        </div>
      )}
    </div>
  );
};

const IrrigationControl = ({ system, onActivate }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'scheduled': return 'text-blue-600 bg-blue-100';
      case 'maintenance': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg border shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">Zone {system.zone_id.slice(-4)}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(system.status)}`}>
          {system.status}
        </span>
      </div>
      
      <div className="space-y-2 text-sm text-gray-600">
        <div>Pupuk: {system.fertilizer_type || 'N/A'}</div>
        <div>Flow Rate: {system.flow_rate.toFixed(1)} L/min</div>
        {system.last_activated && (
          <div>Terakhir: {new Date(system.last_activated).toLocaleString('id-ID')}</div>
        )}
      </div>
      
      <button
        onClick={() => onActivate(system.id)}
        disabled={system.status === 'active'}
        className="mt-3 w-full px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
      >
        {system.status === 'active' ? 'Sedang Aktif' : 'Aktifkan Sistem'}
      </button>
    </div>
  );
};

const DroneCard = ({ drone, onSendMission }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'in_flight': return 'text-blue-600 bg-blue-100';
      case 'spraying': return 'text-green-600 bg-green-100';
      case 'charging': return 'text-yellow-600 bg-yellow-100';
      case 'maintenance': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getBatteryColor = (level) => {
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-4 bg-white rounded-lg border shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">🚁 {drone.drone_name}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(drone.status)}`}>
          {drone.status}
        </span>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span>Baterai:</span>
          <span className={`font-medium ${getBatteryColor(drone.battery_level)}`}>
            {drone.battery_level.toFixed(0)}%
          </span>
        </div>
        <div className="flex justify-between">
          <span>Payload:</span>
          <span>{drone.payload_remaining.toFixed(0)}%</span>
        </div>
        <div className="text-xs text-gray-500">
          Posisi: {drone.current_lat.toFixed(4)}, {drone.current_lng.toFixed(4)}
        </div>
        {drone.payload_type && (
          <div className="text-xs">Muatan: {drone.payload_type}</div>
        )}
      </div>
      
      <button
        onClick={() => onSendMission(drone.id)}
        disabled={drone.status === 'in_flight' || drone.status === 'spraying'}
        className="mt-3 w-full px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
      >
        {drone.status === 'in_flight' || drone.status === 'spraying' ? 'Dalam Misi' : 'Kirim Misi'}
      </button>
    </div>
  );
};

const SmartFarmDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [dronePositions, setDronePositions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError('Gagal memuat data dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      const response = await axios.get(`${API}/sensors/historical?hours=24`);
      setHistoricalData(response.data.data);
    } catch (err) {
      console.error('Historical data error:', err);
    }
  };

  const fetchDronePositions = async () => {
    try {
      const response = await axios.get(`${API}/drones/positions`);
      setDronePositions(response.data.drones);
    } catch (err) {
      console.error('Drone positions error:', err);
    }
  };

  const simulateData = async () => {
    try {
      await axios.post(`${API}/simulate-data`);
      fetchDashboardData();
    } catch (err) {
      console.error('Simulation error:', err);
    }
  };

  const activateIrrigation = async (systemId) => {
    try {
      await axios.put(`${API}/irrigation/${systemId}/activate`, null, {
        params: { duration: 15 }
      });
      fetchDashboardData();
    } catch (err) {
      console.error('Irrigation activation error:', err);
    }
  };

  const sendDroneMission = async (droneId) => {
    try {
      // Sample coordinates for mission
      await axios.put(`${API}/drones/${droneId}/mission`, null, {
        params: {
          target_lat: -6.2088 + (Math.random() - 0.5) * 0.01,
          target_lng: 106.8456 + (Math.random() - 0.5) * 0.01,
          payload_type: 'water'
        }
      });
      fetchDashboardData();
    } catch (err) {
      console.error('Drone mission error:', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  const getSensorIcon = (type) => {
    const icons = {
      soil_moisture: '💧',
      nutrient_n: '🌱',
      nutrient_p: '🌿',
      nutrient_k: '🍃',
      ph_level: '⚗️',
      temperature: '🌡️',
      humidity: '💨'
    };
    return icons[type] || '📊';
  };

  const getSensorTitle = (type) => {
    const titles = {
      soil_moisture: 'Kelembaban Tanah',
      nutrient_n: 'Nitrogen (N)',
      nutrient_p: 'Fosfor (P)',
      nutrient_k: 'Kalium (K)',
      ph_level: 'pH Tanah',
      temperature: 'Suhu',
      humidity: 'Kelembaban Udara'
    };
    return titles[type] || type;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">🌾 Smart Farm Dashboard</h1>
              <div className="flex space-x-2">
                <div className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                  {dashboardData?.total_zones || 0} Zona
                </div>
                <div className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {dashboardData?.active_irrigations || 0} Sistem Aktif
                </div>
                <div className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                  {dashboardData?.drones_active || 0} Drone Terbang
                </div>
                {dashboardData?.critical_alerts > 0 && (
                  <div className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium animate-pulse">
                    ⚠️ {dashboardData.critical_alerts} Alert
                  </div>
                )}
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={simulateData}
                className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm"
              >
                Generate Data Test
              </button>
              <button
                onClick={fetchDashboardData}
                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Sensor Data */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Data Sensor Real-time</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
            {dashboardData?.recent_sensor_data.slice(0, 7).map((sensor, index) => (
              <SensorCard
                key={index}
                title={getSensorTitle(sensor.sensor_type)}
                value={sensor.value}
                unit={sensor.unit}
                alertLevel={sensor.alert_level}
                icon={getSensorIcon(sensor.sensor_type)}
              />
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Irrigation Systems */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">💧 Sistem Pemupukan Otomatis</h2>
            <div className="space-y-4">
              {dashboardData?.irrigation_systems.map((system, index) => (
                <IrrigationControl
                  key={index}
                  system={system}
                  onActivate={activateIrrigation}
                />
              ))}
            </div>
          </div>

          {/* Drone Fleet */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">🚁 Armada Drone</h2>
            <div className="space-y-4">
              {dashboardData?.drone_fleet.map((drone, index) => (
                <DroneCard
                  key={index}
                  drone={drone}
                  onSendMission={sendDroneMission}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Status Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Terakhir diupdate: {new Date().toLocaleString('id-ID')}</p>
          <p className="mt-1">Status sistem: <span className="text-green-600 font-medium">Aktif ✓</span></p>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <SmartFarmDashboard />
    </div>
  );
}

export default App;