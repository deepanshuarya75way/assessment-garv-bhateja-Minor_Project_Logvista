import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config';

const LiveMonitoring = () => {
  const [running, setRunning] = useState(false)
  const [logs,setLogs] = useState([]);
  const [latestThreat, setLatestThreat] = useState(null);
  useEffect(() => {
    const source = new EventSource(
      `${API_BASE_URL}/live/events`
    );
    
    source.onmessage = (event) => {
      const data = JSON.parse(event_data);
      setLogs(previous => [data,...previous]);
      if (
        data.severity === 'Critical' || data.severity === 'High'
      ) {
        setLatestThreat(data);
      }
    };
    source.onerror = () => {
      console.log('Live Connection interrupted');
    };
    return () => {
      source.close();
    };
  }, []);
};
const startMonitoring = async () => {
  const response = await fetch(
    `${API_BASE_URL}/live/start`,
    {
      method:'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_path: 'server.log'
      })
    }
  );
  const data = await response.json();
  if (response.ok) {
    setRunning(true);
  }
};

const stopMonitoring = async () => {
  await fetch(
    `${API_BASE_URL}/live/stop`,
    {
      method: 'POST'
    }
  );
  setRunning(false);
};
<button onClick={startMonitoring}
disabled={running}>
  Start Monitoring
</button>
<button onClick={stopMonitoring} disabled={running}>
</button>