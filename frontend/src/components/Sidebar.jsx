import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, LayoutDashboard, FileText, AlertTriangle, Clock, Search, Fingerprint, Settings } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', name: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/logs', name: 'Log Explorer', icon: <Search size={20} /> },
    { path: '/upload', name: 'Upload Logs', icon: <Search size={20} /> },
    { path: '/threats', name: 'Threat Detection', icon: <AlertTriangle size={20} /> },
    { path: '/timeline', name: 'Timeline Reconstruct', icon: <Clock size={20} /> },
    { path: '/report', name: 'Investigations', icon: <FileText size={20} /> },
    { path: '/evidence', name: 'Evidence Integrity', icon: <Fingerprint size={20} /> },
    { path: '/settings', name: 'Settings', icon: <Settings size={20} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Shield size={28} className="brand-icon text-blue" />
        <span className="brand-text">LOGVISTA</span>
      </div>
      <nav className="sidebar-nav">
        <ul>
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink 
                to={item.path} 
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-name">{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="sidebar-footer">
        <div className="system-status">
          <div className="status-dot"></div>
          <span>System Healthy</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
