import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User, Terminal, Sparkles, Zap, ArrowRight } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();
      
      if (data.success) {
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError(data.message || 'Authentication failed. Please check credentials.');
      }
    } catch (err) {
      setError('Connection to backend timed out or waking up. You can use 1-Click Demo Access above!');
    } finally {
      setLoading(false);
    }
  };

  const handleAutofill = () => {
    setUsername('admin');
    setPassword('password');
    setError('');
  };

  const handleDemoAccess = async () => {
    setUsername('admin');
    setPassword('password');
    setError('');
    setDemoLoading(true);

    try {
      // Fast timeout so evaluator is never kept waiting if Render free tier is waking up
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'password' }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      const data = await response.json();
      if (data.success) {
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
        return;
      }
    } catch (err) {
      console.warn("Backend auth unavailable or cold-starting. Entering instant demo mode:", err);
    }

    // Seamless instant fallback for recruiters (guaranteed zero friction)
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'recruiter_evaluator', role: 'Security Evaluator (Demo)' }));
    navigate('/dashboard');
  };

  return (
    <div className="login-container">
      <div className="forensic-grid-background"></div>
      
      <div className="login-card glass-morph">
        <div className="brand-logo">
          <div className="logo-outer-glow">
            <Shield size={44} className="logo-icon pulse" />
          </div>
          <div className="brand-text">
            <h2>LOGVISTA</h2>
            <span className="status-badge">AI CYBER FORENSICS PLATFORM</span>
          </div>
        </div>

        {/* Recruiter / Quick Demo Box */}
        <div className="demo-access-card">
          <div className="demo-badge-wrap">
            <span className="demo-pill">
              <Sparkles size={13} className="text-cyan" /> RECRUITER & EVALUATOR DEMO
            </span>
          </div>
          <p className="demo-text">
            Explore the full investigation dashboard without manual credentials.
          </p>
          <button 
            type="button" 
            onClick={handleDemoAccess} 
            className="demo-action-btn"
            disabled={loading || demoLoading}
          >
            <Zap size={16} className="zap-icon" />
            <span>{demoLoading ? 'LAUNCHING DEMO SESSION...' : '1-CLICK DEMO ACCESS'}</span>
            <ArrowRight size={15} />
          </button>
          
          <div className="demo-credentials-hint">
            <span>Default: <strong onClick={handleAutofill} className="clickable-cred">admin / password</strong></span>
            <button type="button" onClick={handleAutofill} className="autofill-btn">Auto-Fill</button>
          </div>
        </div>

        <div className="login-divider">
          <span>OR SIGN IN MANUALLY</span>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <User size={18} className="input-icon" />
            <input 
              type="text" 
              placeholder="ANALYST USERNAME" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
            />
          </div>

          <div className="input-group">
            <Lock size={18} className="input-icon" />
            <input 
              type="password" 
              placeholder="ACCESS CREDENTIALS" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          {error && (
            <div className="error-message">
              <Terminal size={14} /> {error}
            </div>
          )}

          <button type="submit" className="login-button" disabled={loading || demoLoading}>
            {loading ? 'AUTHENTICATING...' : 'ESTABLISH SECURE LINK'}
          </button>
        </form>
        
        <div className="login-footer">
          <p>LOGVISTA AI FORENSIC CORE [V5.1] • MITRE-ATT&CK ALIGNED</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
