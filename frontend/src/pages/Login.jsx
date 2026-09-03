import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User, Terminal } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
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
        setError(data.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Connection to backend failed. Ensure server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="forensic-grid-background"></div>
      
      <div className="login-card glass-morph">
        <div className="brand-logo">
          <div className="logo-outer-glow">
            <Shield size={48} className="logo-icon neon-pulse-blue" />
          </div>
          <div className="brand-text">
            <h2>LOGVISTA</h2>
            <span className="status-badge">AI CORE ACTIVE</span>
          </div>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group-premium">
            <User size={18} className="input-icon-neon" />
            <input 
              type="text" 
              placeholder="ANALYST USERNAME" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
            />
          </div>

          <div className="input-group-premium">
            <Lock size={18} className="input-icon-neon" />
            <input 
              type="password" 
              placeholder="ACCESS CREDENTIALS" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          {error && <div className="forensic-error"><Terminal size={14} /> SECURITY ALERT: {error}</div>}

          <button type="submit" className="login-button-neon" disabled={loading}>
            {loading ? 'AUTHENTICATING...' : 'ESTABLISH SECURE LINK'}
          </button>
        </form>
        
        <div className="login-footer-forensic">
          <p>WARNING: SYSTEM ACCESS IS LOGGED BY AI CORE [V5.1]</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
