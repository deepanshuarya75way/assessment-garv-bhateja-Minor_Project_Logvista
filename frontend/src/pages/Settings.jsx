import React, { useState } from 'react';
import { Save, Plus, Database, Users, Brain, Shield } from 'lucide-react';
import './Settings.css';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('sources');

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Platform Configuration</h1>
        <button className="primary-btn"><Save size={16}/> Save Changes</button>
      </div>

      <div className="settings-layout">
        <aside className="settings-sidebar">
          <nav>
            <ul>
              <li 
                className={activeTab === 'sources' ? 'active' : ''} 
                onClick={() => setActiveTab('sources')}
              >
                <Database size={18}/> Log Sources
              </li>
              <li 
                className={activeTab === 'users' ? 'active' : ''} 
                onClick={() => setActiveTab('users')}
              >
                <Users size={18}/> User Roles
              </li>
              <li 
                className={activeTab === 'ai' ? 'active' : ''} 
                onClick={() => setActiveTab('ai')}
              >
                <Brain size={18}/> AI Detection Engine
              </li>
              <li 
                className={activeTab === 'security' ? 'active' : ''} 
                onClick={() => setActiveTab('security')}
              >
                <Shield size={18}/> Security Policies
              </li>
            </ul>
          </nav>
        </aside>

        <div className="settings-content">
          {activeTab === 'sources' && (
            <div className="settings-panel">
              <div className="panel-header-flex">
                <h2>Data Sources</h2>
                <button className="outline-btn"><Plus size={16}/> Add New Source</button>
              </div>
              <div className="source-list">
                <div className="source-item">
                  <div className="source-info">
                    <h4>Primary Auth Gateway</h4>
                    <span className="text-muted">Type: syslog • Status: Connected</span>
                  </div>
                  <div className="toggle-switch active"></div>
                </div>
                <div className="source-item">
                  <div className="source-info">
                    <h4>AWS CloudTrail (Production)</h4>
                    <span className="text-muted">Type: API • Status: Connected</span>
                  </div>
                  <div className="toggle-switch active"></div>
                </div>
                <div className="source-item">
                  <div className="source-info">
                    <h4>Legacy Mainframe</h4>
                    <span className="text-muted">Type: File Transfer • Status: Error</span>
                  </div>
                  <div className="toggle-switch"></div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ai' && (
            <div className="settings-panel">
              <h2>AI Detection Engine</h2>
              <p className="panel-desc">Configure machine learning sensitivity and automated response behaviors.</p>
              
              <div className="form-group mt-2">
                <label>Threat Detection Sensitivity</label>
                <select className="form-control">
                  <option>Aggressive (Max Catch Rate, Higher False Positives)</option>
                  <option selected>Balanced (Standard)</option>
                  <option>Conservative (Minimal False Positives)</option>
                </select>
              </div>

              <div className="settings-toggle-group">
                <div className="toggle-row">
                  <div className="toggle-text">
                    <h4>Auto-Ban High Confidence Actors</h4>
                    <p>Automatically block IPs/Accounts flagged with &gt;95% confidence.</p>
                  </div>
                  <div className="toggle-switch active"></div>
                </div>
                
                <div className="toggle-row">
                  <div className="toggle-text">
                    <h4>Zero-Day Heuristic Analysis</h4>
                    <p>Use predictive modelling for unknown attack patterns.</p>
                  </div>
                  <div className="toggle-switch active"></div>
                </div>

                <div className="toggle-row">
                  <div className="toggle-text">
                    <h4>Deep Payload Inspection (DPI)</h4>
                    <p>Warning: May impact ingestion performance.</p>
                  </div>
                  <div className="toggle-switch"></div>
                </div>
              </div>
            </div>
          )}
          
          {(activeTab === 'users' || activeTab === 'security') && (
            <div className="settings-panel placeholder-panel">
              <p className="text-muted">Configuration section locked pending admin authorization.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
