import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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