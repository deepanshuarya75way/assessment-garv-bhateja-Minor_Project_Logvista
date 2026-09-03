import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Brain, Shield, Crosshair, AlertTriangle, Activity } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './ThreatDetails.css';

const ThreatDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/analysis/threat/${id}`)
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch threat details:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div className="loading-state"><Activity className="pulse" /> Fetching AI Threat Analysis...</div>;
  if (!data || data.error) return <div className="error-state">Threat analysis not available for this ID.</div>;

  return (
    <div className="threat-details">
      <button className="back-btn" onClick={() => navigate('/threats')}>
        <ArrowLeft size={18} /> Back to Threats
      </button>

      <div className="details-header">
        <div className="title-section">
          <h1>{data.name}</h1>
          <span className={`severity-badge ${data.confidence > 50 ? 'critical' : 'high'}`}>
            {data.confidence > 80 ? 'CRITICAL SEVERITY' : 'HIGH SEVERITY'}
          </span>
        </div>
        <div className="action-section">
          <button className="primary-btn bg-red">Block IP Sources</button>
          <button className="outline-btn">Generate Yara Rule</button>
        </div>
      </div>

      <div className="details-grid">
        <div className="main-panel panel-card">
          <div className="panel-header">
            <Brain className="text-purple" />
            <h2>AI Reasoning Engine</h2>
          </div>
          <div className="panel-content">
            <p className="reasoning-text">
              {data.reasoning}
            </p>
            <div className="confidence-meter">
              <div className="meter-label">AI Confidence Score</div>
              <div className="meter-bar">
                <div className="meter-fill" style={{ width: `${data.confidence}%` }}></div>
              </div>
              <div className="meter-value">{data.confidence}%</div>
            </div>
          </div>
        </div>

        <div className="side-panel panel-card">
          <div className="panel-header">
            <Crosshair className="text-red" />
            <h2>Attack Impact</h2>
          </div>
          <div className="panel-content">
            <ul className="impact-list">
              {data.impact.map((imp, index) => (
                <li key={index}><AlertTriangle size={16} /> {imp}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="full-panel panel-card">
          <div className="panel-header">
            <Activity className="text-blue" />
            <h2>Associated Log Fragments</h2>
          </div>
          <div className="panel-content log-samples">
             {data.samples && data.samples.length > 0 ? (
               data.samples.map((sample, index) => (
                 <pre key={index} className="log-sample-item">
                    {sample}
                 </pre>
               ))
             ) : (
                <p className="text-muted">No specific log samples correlated for this threat type.</p>
             )}
          </div>
        </div>

        <div className="full-panel panel-card">
          <div className="panel-header">
            <Shield className="text-green" />
            <h2>Suggested Mitigation</h2>
          </div>
          <div className="panel-content mitigation-content">
            {data.mitigation.map((step, index) => (
              <div key={index} className="mitigation-step">
                <div className="step-num">{step.step}</div>
                <div className="step-desc">
                  <h4>{step.title}</h4>
                  <p>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreatDetails;
