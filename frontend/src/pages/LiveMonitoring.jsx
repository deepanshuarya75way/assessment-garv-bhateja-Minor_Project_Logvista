import { useEffect, useState } from "react";
const API_URL="http://localhost:5000"

function LiveMonitoring(){
  const [running,setRunning] = useState(false);
  const [logs,setLogs] = useState([]);
  const[latestThreat, setLatestThreat] = useState(null)

  const startMonitoring =async () => {
    try {
      const response = await fetch(
        `${API_URL}/live/start`,
        {
          method:"POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            file_path: "server.log"
          })
        }
      );
      const data = await response.json();
      if (response.ok) {
        setRunning(true);
      } else {
        console.error(data);
      }
    }
    catch (error) {
      console.error("Failed to start monitoring",);
    }
  };

  const stopMonitoring = async () => {
    try {
      await fetch(
        `${API_URL}/live/stop`,
        {
          method: "POST"
        }
      );
      setRunning(false);
    } catch (error) {
      console.error(
        "Failed to stop monitoring:",error
      );
    }
  };

  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/live/events`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(previousLogs => [data,...previousLogs]);
      if (
        data.severity === "Critical" || data.severity === "High"
      ) {
        setLatestThreat(data);
      }
    };
    eventSource.onerror = () => {
      console.log("SSE Connection error");
    };
    return () => {
      eventSource.close();
    };
  },[]);
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Live Threat</h1>
          <p className="text-gray-500">MOnitor incoming logs in real time</p>
        </div>
        <div className="flex gap-3">  
          <button onClick={startMonitoring} disabled={running} className="px-4 py-2 bg-green-600 text-white rounded">
            Start Monitoring
          </button>
          <button onClick={stopMonitoring} disabled={!running} className="px-4 py-2 bg-red-600 text-white rounded">
            Stop Monitoring
          </button>
        </div>
      </div>
      <div className="mb-4">
        <span>
          Status:
        </span>
        <span className="ml-2 font-semibold">
          {running ? "Monitoring" : "Stopped"}
        </span>
      </div>
    </div>
  )
}
export default LiveMonitoring;