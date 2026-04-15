import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import Dashboard from './pages/Dashboard';
import LogExplorer from './pages/LogExplorer';
import ThreatDetection from './pages/ThreatDetection';
import ThreatDetails from './pages/ThreatDetails';
import TimelineReconstruction from './pages/TimelineReconstruction';
import InvestigationReport from './pages/InvestigationReport';
import EvidenceIntegrity from './pages/EvidenceIntegrity';
import Settings from './pages/Settings';
import Login from './pages/Login';
import UploadLogs from './pages/UploadLogs';

import './App.css';

// Simple protected route checker
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="logs" element={<LogExplorer />} />
          <Route path="upload" element={<UploadLogs />} />
          <Route path="threats" element={<ThreatDetection />} />
          <Route path="threats/:id" element={<ThreatDetails />} />
          <Route path="timeline" element={<TimelineReconstruction />} />
          <Route path="report" element={<InvestigationReport />} />
          <Route path="evidence" element={<EvidenceIntegrity />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
