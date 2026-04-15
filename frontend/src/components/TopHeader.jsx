import React from 'react';
import { Bell, Search, User } from 'lucide-react';
import './TopHeader.css';

const TopHeader = () => {
  return (
    <header className="top-header">
      <div className="header-search">
        <Search className="search-icon" size={18} />
        <input 
          type="text" 
          placeholder="Search logs, queries, threats..." 
          className="search-input"
        />
        <div className="search-shortcut">Ctrl+K</div>
      </div>
      
      <div className="header-actions">
        <button className="icon-btn notification-btn">
          <Bell size={20} />
          <span className="badge">3</span>
        </button>
        <div className="user-profile">
          <div className="user-avatar">
            <User size={20} />
          </div>
          <div className="user-info">
            <span className="user-name">Admin</span>
            <span className="user-role">SecOps Lead</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
