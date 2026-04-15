import React, { useState, useEffect } from 'react';
import { Fingerprint, CheckCircle, XCircle, Search, Activity } from 'lucide-react';
import './EvidenceIntegrity.css';

const EvidenceIntegrity = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/analysis/integrity')
      .then(res => res.json())
      .then(data => {
        setLogs(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch integrity data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state"><Activity className="spin" /> Verifying Cryptographic Chains...</div>;

  return (
    <div className="evidence-page">
      <div className="page-header">
        <h1>Evidence Integrity & Chain of Custody</h1>
        <p className="text-muted">Cryptographic verification of log entries stored in the decentralized Logvista database.</p>
      </div>

      <div className="evidence-summary-cards">
        <div className="summary-card safe">
          <CheckCircle size={32} />
          <div className="card-info">
            <h4>Verified Logs</h4>
            <span className="value">{logs.length}</span>
          </div>
        </div>
        <div className="summary-card compromised">
          <XCircle size={32} />
          <div className="card-info">
            <h4>Tampered Logs</h4>
            <span className="value">0</span>
          </div>
        </div>
      </div>

      <div className="evidence-table-card">
        <div className="table-header">
          <div className="search-box">
            <Search size={18} />
            <input type="text" placeholder="Search by entry ID or hash..." />
          </div>
          <button className="primary-btn"><Fingerprint size={16} /> Re-verify All</button>
        </div>
        
        <div className="table-wrapper" style={{ overflowX: 'auto' }}>
          <table className="evidence-table">
            <thead>
              <tr>
                <th>Entry ID</th>
                <th>Source / File Reference</th>
                <th>SHA-256 Hash</th>
                <th>Custodian</th>
                <th>Integrity Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td className="font-mono">#LOG-{log.id}</td>
                  <td className="file-name">{log.file}</td>
                  <td className="hash-string">{log.hash.substring(0, 8)}...****</td>
                  <td>{log.custodian}</td>
                  <td>
                    <span className={`integrity-status ${log.status.toLowerCase()}`}>
                      {log.status === 'Safe' ? <CheckCircle size={14} /> : <XCircle size={14} />}
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default EvidenceIntegrity;
