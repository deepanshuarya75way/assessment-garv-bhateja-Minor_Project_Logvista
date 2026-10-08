import { useEffect, useState } from "react";
const API_URL="http://localhost:5000"

function LiveMonitoring(){
  const [running,setRunning] = useState(false);
  const [logs,setLogs] = useState([]);
  const[latestThreat, setLatestThreat] = useState(null)

  // const startMonitoring =async () => {
  //   try {
  //     const response = await fetch(
  //       "http://localhost:5000/live/start",
  //       {
  //         method:"POST",
  //         headers: {
  //           "Content-Type": "application/json"
  //         },
  //         body: JSON.stringify({
  //           file_path: "server.log"
  //         })
  //       }
  //     );
  //     const data = await response.json();
  //     if (!response.ok) {
  //       throw new error(
  //         data.error || "Failed to start monitoring"
  //       );
  //     }
  //     setRunning(true)}
  //   catch (error) {
  //     console.error(error);
  //     alert(error.message);
  //   }
  // };
  const startMonitoring = async () => {
    console.log("Start button clicked");
    try{
      const response = await fetch(
        "http://localhost:5000/live/start",
        {
          method: "POST",
          headers: {
            "content-Type": "application/json"
          },
          body:JSON.stringify({
            file_path: "/home/coder/workspace/assessment-garv-bhateja-Minor_Project_Logvista/server.log"
          })
        }
      );
      console.log("Response status:",response.status);
      const data = await response.json();
      console.log("Response data:", data)
      if (!response.ok) {
        throw new Error(
          data.error || "Failed to start monitoring"
        );
      }
      setRunning(true);
    } catch (error) {
      console.error("Start Error: ",error);
      alert(error.messaage);
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
  useEffect(()=> {
    console.log("sse effect start");
    const eventSource= new EventSource("http://localhost:5000/live/events");
    const handleSSE = (event) => {
      console.log("SSE Event recieved:",event)
      console.log("SSE Event recieved:",event.type)
      console.log("SSE Event recieved:",event.data)
      if (!event.data){
        console.log("ignoring sse event without data");
        return;
      }
      try {
        const data = JSON.parse(Event.data);
        if (data.type === "connected") {
          console.log("SSE Connected");
          return;
        }
        if (data.type === "logs"){
          setLogs((previousLogs) => [
            data, ...previousLogs
          ]);
        }
        if (data.type ==="threat"){
          setLatestThreat(data);
          setLogs((previousLogs)=> [
            data,
            ...previousLogs
          ]);
        }
      } catch (error) {
        console.error("SSE parse error:",error);
      }
    };
    eventSource.onmessage=handleSSE;
    eventSource.addEventListener("Log",handleSSE);
    eventSource.addEventListener("threat",handleSSE);
    eventSource.onopen = () => {
      console.log("SSE connection opened");
    };
    eventSource.onerror = (error) => {
      console.error("sse error: ",error)
    };
    return () => {
      console.log("SSE connection closed");
    
      
      eventSource.removeEventListener("log",handleSSE);
      eventSource.removeEventListener("threat",handleSSE);
      eventSource.close();
    };
  },[])
  // useEffect(() => {
  //   console.log("sse effect staart")
  //   const eventSource = new EventSource("http://localhost:5000/live/events");
  //   eventSource.onopen = () => {
  //     console.log("sse open");
  //   };
  //   eventSource.onmessage = (event) => {
  //     alert ("sse recieved");
  //     console.log("sse:",event.data);
  //     const data = JSON.parse(event.data);
  //     setLogs(prev=> [data, ...prev]);
  //   }
  //   // eventSource.onmessage= (event) => {
  //   //   console.log("frontend see: ",event.data)
  //   //   console.log("raw sse message")
  //   //   console.log(event);
  //   //   console.log("data:",event.data)
  //   //   setLogs((prev)=>{
  //   //     console.log("updating logs,previous:",prev);
  //   //     return [
  //   //       {
  //   //         type: "log",
  //   //         message:event.data,
  //   //       },
  //   //       ...prev,
  //   //     ];
  //   //   });
  //   // };
  //   eventSource.onerror = (error) => {
  //     console.error("sse error",error);
  //   };
  //   return () => {
  //     console.log("sse cleanup");
  //     eventSource.close()
  //   };
  // },[]
  // )

  // useEffect(() => {
  //   const eventSource = new EventSource(`${API_URL}/live/events`);
  //   console.log("Opening SSE Connection...");
  //   console.log("EventSource created: ",eventSource);
  //   eventSource.onopen = () => {
  //     console.log("SSE Connection Opened");
  //   };
  //   eventSource.onmessage = (event) => {
  //     console.log("SSE event recieved:",event.data);
  //     try {
  //       const data=JSON.parse(event.data);
  //       console.log("Parsed sse data:",data);
  //       if (data.type ==="connected") {
  //         console.log("sse connected");
  //         return;
  //       }
  //       if (data.type === "log") {
  //         setLogs(previousLogs => [data, ...previousLogs]);
  //       }
  //       if (data.type ==="threat"){
  //         setLatestThreat(data);
  //       }
  //     } catch (error) {
  //       console.error("SSE JSON ERROR:",error);
  //     }
  //   //   const data = JSON.parse(event.data);
  //   //   setLogs(previousLogs => [
  //   //     data,
  //   //     ...previousLogs
  //   //   ]);
    
  //   // if (
  //   //   data.severity === "Critical" || data.severity === "High"){
  //   //     setLatestThreat(data);
  //   //   }
  //   };
  //   // eventSource.onmessage = (event) => {
  //   //   try {
  //   //     const data = JSON.parse(event.data);
  //   //     setLogs(previousLogs => [data,...previousLogs]);
  //   //     if (
  //   //     data.severity === "Critical" || data.severity === "High"
  //   //   ) {
  //   //     setLatestThreat(data);
  //   //   }} catch (error) {
  //   //     console.error(
  //   //       "Failed to parse live event.",error
  //   //     );
  //   //   }
  //   // };
  //   eventSource.onerror = () => {
  //     console.log("SSE ERROR", error);
  //   };
  //   return () => {
  //     console.log("Closing SSE");
  //     // eventSource.close();
  //   };
  // },[]);
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
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-4">
            Live Logs
          </h2>
          {logs.length===0 ? (<p className="text-gray-500">No logs recieved yet.</p>)
          : (
            <div className="space-y-3">
              {logs.map((log, index) => (
                <div key={index} className="border rounded-lg p-4">
                  {log.messaage}
                  <p className="font-medium">{log.message}</p>
                </div>
              ))}
            </div>
          )
        }
        </div>
      </div>
    </div>
  )
}
export default LiveMonitoring;