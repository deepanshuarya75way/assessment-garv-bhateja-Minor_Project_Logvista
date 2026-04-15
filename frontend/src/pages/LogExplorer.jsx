import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';
import './LogExplorer.css';

const MOCK_LOGS = [
  { id: 'log-100', timestamp: '2026-04-03 14:32:11', source: 'Auth Gateway', eventType: 'Failed Login', severity: 'Medium', status: 'Blocked', raw: '{"user":"admin","ip":"192.168.1.104","reason":"invalid_creds"}' },
  { id: 'log-101', timestamp: '2026-04-03 14:32:05', source: 'DB Server P', eventType: 'SQL Injection Attempt', severity: 'Critical', status: 'Mitigated', raw: '{"query":"SELECT * FROM users WHERE id = 1 OR 1=1","ip":"45.33.22.1","action":"drop_conn"}' },
  { id: 'log-102', timestamp: '2026-04-03 14:30:45', source: 'API Endpoint /api/v2/data', eventType: 'Rate Limit Exceeded', severity: 'Low', status: 'Throttled', raw: '{"endpoint":"/api/v2/data","req_count":1500,"limit":1000}' },
  { id: 'log-103', timestamp: '2026-04-03 14:28:10', source: 'Firewall-DMZ', eventType: 'Port Scan Detected', severity: 'High', status: 'Monitoring', raw: '{"src_ip":"112.55.44.33","ports":"22,80,443,3389,8080","action":"log"}' },
  { id: 'log-104', timestamp: '2026-04-03 14:25:00', source: 'System Kernel', eventType: 'OOM Killed Process', severity: 'High', status: 'Recovered', raw: '{"process":"node","pid":5532,"mem_usage":"4GB"}' },
  { id: 'log-105', timestamp: '2026-04-03 14:20:11', source: 'Web Server', eventType: 'Access', severity: 'Info', status: 'Success', raw: '{"path":"/dashboard","user":"analyst_jon","ip":"10.0.0.55"}' },
];

const LogExplorer = () => {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [logs, setLogs] = useState(MOCK_LOGS);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/logs')
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          const formattedLogs = data.map((log, index) => ({
            id: `api-log-${index}`,
            timestamp: log.timestamp,
            source: log.source,
            eventType: log.event,
            severity: log.severity,
            status: log.status,
            raw: JSON.stringify(log)
          }));
          setLogs([...formattedLogs, ...MOCK_LOGS]);
        }
      })
      .catch(err => console.error("Failed to fetch logs:", err));
  }, []);

  const toggleRow = (id) => {
    const newSet = new Set(expandedRows);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setExpandedRows(newSet);
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    // Check if it matches /Date(...)/ format
    const match = /^\/Date\((\d+)\)\/$/.exec(dateString);
    if (match) {
      const epoch = parseInt(match[1], 10);
      return new Date(epoch).toLocaleString();
    }
    // If it's already normal ISO string or standard format, return directly (or parse slightly)
    try {
      const date = new Date(dateString);
      if (!isNaN(date)) return date.toLocaleString();
    } catch {}
    
    return dateString;
  };

  const getRowClass = (severity) => {
    if (severity === 'Critical') return 'row-critical';
    if (severity === 'High') return 'row-high';
    return '';
  };

  return (
    <div className="log-explorer">
      <div className="page-header">
        <h1>Log Explorer</h1>
        <div className="header-actions">
          <button className="primary-btn"><Download size={16}/> Export CSV</button>
        </div>
      </div>

      <div className="filters-bar">
        <div className="search-box">
          <Search size={18} className="text-muted"/>
          <input type="text" placeholder="Search logs (e.g. SQL Injection...)" />
        </div>
        <div className="filter-group">
          <select className="filter-select">
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
            <option value="Info">Info</option>
          </select>
          <select className="filter-select">
            <option value="">Any Threat Type</option>
            <option value="DoS">DoS/DDoS</option>
            <option value="SQLi">SQL Injection</option>
            <option value="BruteForce">Brute Force</option>
          </select>
          <select className="filter-select">
            <option value="1h">Last 1 Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <button className="icon-btn-square"><Filter size={18}/></button>
        </div>
      </div>

      <div className="table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th width="40"></th>
              <th>Timestamp</th>
              <th>Source</th>
              <th>Event Type</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <React.Fragment key={log.id}>
                <tr 
                  className={`log-row ${getRowClass(log.severity)} ${expandedRows.has(log.id) ? 'expanded' : ''}`}
                  onClick={() => toggleRow(log.id)}
                >
                  <td className="expand-icon">
                    {expandedRows.has(log.id) ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  </td>
                  <td className="font-mono">{formatDate(log.timestamp)}</td>
                  <td>{log.source}</td>
                  <td className="event-type">
                    {(log.severity === 'Critical' || log.severity === 'High') && <AlertCircle size={14} className="alert-icon"/>}
                    {log.eventType}
                  </td>
                  <td>
                    <span className={`severity-tag ${log.severity.toLowerCase()}`}>{log.severity}</span>
                  </td>
                  <td>{log.status}</td>
                </tr>
                {expandedRows.has(log.id) && (
                  <tr className="log-details-row">
                    <td colSpan="6">
                      <div className="log-details-content">
                        <h4>Raw JSON</h4>
                        <pre>{JSON.stringify(JSON.parse(log.raw), null, 2)}</pre>
                        <div className="investigate-actions">
                          <button className="outline-btn">View Related Events</button>
                          <button className="outline-btn">Create Rule</button>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LogExplorer;
