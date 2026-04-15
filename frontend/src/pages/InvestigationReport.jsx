import React, { useState, useEffect } from 'react';
import { Download, Printer, Shield, FileText, Activity, AlertCircle } from 'lucide-react';
import './InvestigationReport.css';

const InvestigationReport = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/analysis/summary')
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch report data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state"><FileText className="pulse" /> Compiling Forensic Report...</div>;

  const story = data?.timeline?.story || ["No incident narrative available."];
  const events = (data?.timeline?.ordered_events || []).slice(0, 10); // Show top 10 for brevity in report

  return (
    <div className="report-page">
      <div className="page-header no-print">
        <h1>Investigation Report</h1>
        <div className="header-actions">
          <button className="outline-btn" onClick={() => window.print()}>
            <Printer size={16} /> Print
          </button>
          <button className="primary-btn">
            <Download size={16} /> Export PDF
          </button>
        </div>
      </div>

      <div className="report-document printable">
        <div className="report-header">
          <div className="report-brand">
            <Shield size={32} className="text-blue" />
            <h2>LOGVISTA Forensics</h2>
          </div>
          <div className="report-meta">
            <p><strong>Case ID:</strong> INC-{Math.floor(Math.random() * 10000)}</p>
            <p><strong>Date Generated:</strong> {new Date().toLocaleDateString()}</p>
            <p><strong>Analyst:</strong> Admin (System)</p>
          </div>
        </div>

        <div className="report-section">
          <h3><Shield size={18}/> Correlated Incidents</h3>
          <div className="incidents-summary-grid">
            {(data?.correlation?.incidents || []).map((inc, i) => (
              <div key={i} className={`incident-card-mini ${inc.risk_score > 50 ? 'high-risk' : 'med-risk'}`}>
                 <div className="incident-id">{inc.id}</div>
                 <div className="incident-actor">Actor: {inc.user !== 'N/A' ? inc.user : inc.ip}</div>
                 <div className="incident-score">Risk: {inc.risk_score}</div>
                 <div className="incident-attack">{inc.global_attack}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="report-section">
          <h3><FileText size={18}/> Case Summary & AI Narrative</h3>
          <p>
            The LogVista AI engine has correlated {data?.correlation?.incidents?.length || 0} distinct incidents. 
            The following narrative explores the progression of these events:
          </p>
          <div className="narrative-box">
             {story.map((line, i) => <p key={i} className="story-line">• {line}</p>)}
          </div>
        </div>

        <div className="report-section">
          <h3><Activity size={18}/> Incident Timeline (Top Events)</h3>
          <table className="report-table">
            <thead>
              <tr>
                <th>Time (UTC)</th>
                <th>Phase / Type</th>
                <th>Log Fragment</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e, i) => (
                <tr key={i}>
                  <td>{e.time.split('T').pop().split('.')[0]}</td>
                  <td>{e.attack || 'General'}</td>
                  <td className="font-mono">{e.log.substring(0, 60)}...</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="report-section">
          <h3><AlertCircle size={18}/> Global AI Findings</h3>
          <div className="finding-box">
            <h4>Global Attack Pattern: {data?.correlation?.global_attack || "None Detected"}</h4>
            <p>
              The AI reasoning engine correlated the sequence of events across multiple sources and IPs. 
              The analysis suggests that the actor focused on targets associated with {events[0]?.type || 'general'} activity.
            </p>
          </div>
        </div>

        <div className="report-section">
          <h3>Conclusion & Next Steps</h3>
          <p>
            The incident analysis provides a clear sequence of events for further manual review. 
            No further automated exfiltration blocks were triggered post-analysis.
          </p>
          <ul className="next-steps-list">
            <li>Verify the source of identified suspicious IPs.</li>
            <li>Compare extracted log fragments with system configuration changes.</li>
            <li>Review credentials associated with identified Linux Auth or Web events.</li>
          </ul>
        </div>
        
        <div className="report-footer">
          <p>CONFIDENTIAL - INTERNAL SEC-OPS USE ONLY</p>
        </div>
      </div>
    </div>
  );
};

export default InvestigationReport;
