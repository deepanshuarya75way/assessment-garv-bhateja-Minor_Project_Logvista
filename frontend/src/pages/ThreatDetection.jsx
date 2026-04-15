import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ServerCrash, Key, Database, Bug, FolderLock, Users, ArrowUpRight, Activity } from 'lucide-react';
import './ThreatDetection.css';

const DEFAULT_THREAT_CONFIG = [
  { id: 'dos', name: 'DoS/DDoS Attacks', icon: ServerCrash, type: 'firewall' },
  { id: 'bruteforce', name: 'Brute Force Attempts', icon: Key, type: 'linux_auth' },
  { id: 'web', name: 'Web Exploitation', icon: Database, type: 'web' },
  { id: 'windows', name: 'Windows Anomalies', icon: ArrowUpRight, type: 'windows' },
  { id: 'unknown', name: 'Unclassified Threats', icon: ShieldAlert, type: 'unknown' }
];

const ThreatDetection = () => {
  const navigate = useNavigate();
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/analysis/summary')
      .then(res => res.json())
      .then(data => {
        const events = data.events || [];
        const counts = {};
        
        // Count events by type
        events.forEach(e => {
          const t = e.type || 'unknown';
          counts[t] = (counts[t] || 0) + 1;
        });

        // Map to UI cards
        const populatedThreats = DEFAULT_THREAT_CONFIG.map(config => {
          const occ = counts[config.type] || 0;
          return {
            ...config,
            severity: occ > 10 ? 'Critical' : occ > 0 ? 'High' : 'Low',
            confidence: occ > 0 ? 85 : 0,
            occurrences: occ,
            lastDetected: occ > 0 ? 'Recently Analyzed' : 'Not Detected'
          };
        });

        setThreats(populatedThreats);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch threat analysis:", err);
        setLoading(false);
      });
  }, []);

  const getSeverityColor = (sev) => {
    switch(sev) {
      case 'Critical': return 'var(--accent-red)';
      case 'High': return 'var(--accent-yellow)';
      case 'Medium': return 'var(--accent-blue)';
      default: return 'var(--accent-green)';
    }
  };

  if (loading) return <div className="loading-state"><Activity className="pulse" /> Generating Threat Analysis...</div>;

  return (
    <div className="threat-detection">
      <div className="page-header">
        <h1>Threat Detection Engine</h1>
        <p className="text-muted">Real-time classification based on active AI model analysis</p>
      </div>

      <div className="threats-grid">
        {threats.map(threat => {
          const Icon = threat.icon;
          return (
            <div key={threat.id} className="threat-card group">
              <div className="threat-card-header">
                <div className="threat-icon" style={{ backgroundColor: `${getSeverityColor(threat.severity)}22`, color: getSeverityColor(threat.severity) }}>
                  <Icon size={24} />
                </div>
                <div className="threat-severity" style={{ borderColor: getSeverityColor(threat.severity), color: getSeverityColor(threat.severity) }}>
                  {threat.severity}
                </div>
              </div>
              
              <h3 className="threat-name">{threat.name}</h3>
              
              <div className="threat-stats">
                <div className="stat">
                  <span className="stat-label">Confidence</span>
                  <span className="stat-value">{threat.confidence}%</span>
                </div>
                <div className="stat-divider"></div>
                <div className="stat">
                  <span className="stat-label">Occurrences</span>
                  <span className="stat-value">{threat.occurrences.toLocaleString()}</span>
                </div>
              </div>

              <div className="threat-footer">
                <span className="last-detected">Last: {threat.lastDetected}</span>
                <button className="details-btn" onClick={() => navigate(`/threats/${threat.id}`)}>
                  View Details <ArrowUpRight size={16} />
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  );
};

export default ThreatDetection;
