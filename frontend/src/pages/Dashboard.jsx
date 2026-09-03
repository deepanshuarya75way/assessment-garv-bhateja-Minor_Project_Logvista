import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Cpu, Database } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './Dashboard.css';


const Dashboard = () => {
  const [stats, setStats] = useState({
    totalLogs: '124.5M',
    threatsDetected: '3,492',
    activeIncidents: '18',
    health: '99.9%'
  });

  useEffect(() => {
    fetch(`${API_BASE_URL}/stats`)
      .then(res => res.json())
      .then(data => {
        setStats(prev => ({
          ...prev,
          totalLogs: data.total_logs || 0,
          threatsDetected: data.threats_detected || 0,
          activeIncidents: data.active_incidents || 0,
        }));
      })
      .catch(err => console.error("Failed to fetch stats:", err));
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Global Operations Center</h1>
        <p className="text-muted">Real-time threat monitoring and log analysis</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon-wrap bg-blue-dim">
            <Database className="text-blue" size={24} />
          </div>
          <div className="kpi-content">
            <h3>Total Logs Analyzed</h3>
            <div className="kpi-value">{typeof stats.totalLogs === 'number' ? stats.totalLogs.toLocaleString() : stats.totalLogs}</div>
            <div className="kpi-trend text-green">+12% from yesterday</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon-wrap bg-red-dim">
            <ShieldAlert className="text-red" size={24} />
          </div>
          <div className="kpi-content">
            <h3>Threats Detected</h3>
            <div className="kpi-value">{typeof stats.threatsDetected === 'number' ? stats.threatsDetected.toLocaleString() : stats.threatsDetected}</div>
            <div className="kpi-trend text-red">+4.2% from yesterday</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon-wrap bg-yellow-dim">
            <Activity className="text-yellow" size={24} />
          </div>
          <div className="kpi-content">
            <h3>Active Incidents</h3>
            <div className="kpi-value">{stats.activeIncidents}</div>
            <div className="kpi-trend text-muted">Awaiting resolution</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon-wrap bg-green-dim">
            <Cpu className="text-green" size={24} />
          </div>
          <div className="kpi-content">
            <h3>System Health</h3>
            <div className="kpi-value">99.9%</div>
            <div className="kpi-trend text-green">All nodes operational</div>
          </div>
        </div>
      </div>


    </div>
  );
};

export default Dashboard;
