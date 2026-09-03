import React, { useState, useEffect } from 'react';
import { Clock, ShieldAlert, Monitor, Terminal, FileCode, CheckCircle, Activity, Info } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './TimelineReconstruction.css';

const ICON_MAP = {
  'linux_auth': Terminal,
  'web': Monitor,
  'firewall': ShieldAlert,
  'windows': Activity,
  'unknown': Info
};

const TimelineReconstruction = () => {
  const [events, setEvents] = useState([]);
  const [story, setStory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/analysis/summary`)
      .then(res => res.json())
      .then(data => {
        const timeline = data.timeline || {};
        setEvents(timeline.ordered_events || []);
        setStory(timeline.story || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch timeline:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state-forensic"><Clock className="spin-neon" /> Establishing Forensic Sequence...</div>;

  return (
    <div className="timeline-page">
      <div className="page-header-forensic">
        <div className="header-main">
          <h1>Attack Timeline Reconstruction</h1>
          <span className="version-tag">AI CORE V5.1</span>
        </div>
        <p className="text-muted">Multi-stage event correlation engine</p>
      </div>

      {story.length > 0 && (
        <div className="ai-story-board glass-morph">
          <h3><ShieldAlert size={20} className="text-red" /> AI INCIDENT NARRATIVE</h3>
          <div className="story-content">
            {story.map((line, i) => (
              <p key={i} className="story-line"><span>[{i+1}]</span> {line}</p>
            ))}
          </div>
        </div>
      )}

      <div className="timeline-container-premium">
        <div className="timeline-track-neon"></div>
        
        {events.length > 0 ? (
          events.map((event, index) => {
            const Icon = ICON_MAP[event.type] || Info;
            return (
              <div key={index} className="timeline-node-premium">
                <div className="timeline-time-col">
                  {event.time.split('T').pop().split('.')[0]}
                </div>
                
                <div className="timeline-marker-premium">
                  <div className="marker-icon-glow"><Icon size={16} /></div>
                </div>
                
                <div className="timeline-content-premium glass-morph">
                  <div className="node-phase-tag">{event.phase}</div>
                  <h3 className="node-attack-title">{event.attack}</h3>
                  <p className="node-log-snippet">"{event.log.substring(0, 150)}..."</p>
                  <div className="node-metadata-row">
                    <span className="sensor-type"><Terminal size={12} /> {event.type}</span>
                    <button className="expand-log-btn">View Forensic Detail</button>
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="empty-timeline-state">
            <Activity size={48} className="pulse-muted" />
            <p>Waiting for forensic log ingestion...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimelineReconstruction;
