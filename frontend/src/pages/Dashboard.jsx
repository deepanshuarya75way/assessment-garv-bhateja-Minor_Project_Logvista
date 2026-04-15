import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, ShieldAlert, Cpu, Database } from 'lucide-react';
import './Dashboard.css';

const lineData = [
  { time: '00:00', logs: 1200 },
  { time: '04:00', logs: 1900 },
  { time: '08:00', logs: 3000 },
  { time: '12:00', logs: 5000 },
  { time: '16:00', logs: 4800 },
  { time: '20:00', logs: 3800 },
  { time: '24:00', logs: 2000 },
];

const pieData = [
  { name: 'DoS/DDoS', value: 400 },
  { name: 'Brute Force', value: 300 },
  { name: 'SQL Injection', value: 300 },
  { name: 'Malware', value: 200 },
  { name: 'Insider', value: 100 },
  { name: 'Privilege Esc.', value: 150 },
];
const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

const recentAlerts = [
  { id: 1, title: 'Multiple Failed Login Attempts', severity: 'High', source: 'Auth Server', time: '5m ago' },
  { id: 2, title: 'Unusual outbound traffic spike', severity: 'Critical', source: 'Gateway', time: '12m ago' },
  { id: 3, title: 'SQL Injection signature detected', severity: 'High', source: 'DB Firewall', time: '1h ago' },
  { id: 4, title: 'Suspicious payload downloaded', severity: 'Medium', source: 'Endpoint X', time: '2h ago' },
  { id: 5, title: 'Port scanning activity', severity: 'Low', source: 'Public IP', time: '3h ago' },
];

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalLogs: '124.5M',
    threatsDetected: '3,492',
    activeIncidents: '18',
    health: '99.9%'
  });

  useEffect(() => {
    fetch('http://127.0.0.1:5000/stats')
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

      <div className="charts-grid">
        <div className="chart-card logs-chart">
          <h2>Logs Volume Over Time</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#11151f', borderColor: '#334155' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Line type="monotone" dataKey="logs" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} activeDot={{ r: 6, fill: '#60a5fa', stroke: '#60a5fa', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card threats-chart">
          <h2>Threat Distribution</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#11151f', borderColor: '#334155' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="pie-legend">
            {pieData.map((entry, i) => (
              <div key={entry.name} className="legend-item">
                <span className="legend-color" style={{ backgroundColor: COLORS[i] }}></span>
                <span className="legend-label">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-card alerts-panel">
          <h2>Recent Alerts</h2>
          <div className="alerts-list">
            {recentAlerts.map(alert => (
              <div key={alert.id} className="alert-item">
                <div className="alert-header">
                  <span className={`severity-badge ${alert.severity.toLowerCase()}`}>
                    {alert.severity}
                  </span>
                  <span className="alert-time">{alert.time}</span>
                </div>
                <div className="alert-title">{alert.title}</div>
                <div className="alert-source">Source: {alert.source}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
