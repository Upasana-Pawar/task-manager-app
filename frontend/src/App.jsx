import { useState } from "react";
import BadgePopup from "./components/BadgePopup";

function App() {
  const [badge, setBadge] = useState(null);

  async function addTask() {
  console.log("DEBUG: addTask clicked");
  try {
    const url = "http://127.0.0.1:5000/tasks"; // try localhost if this fails
    console.log("DEBUG: calling", url);
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Test task from FE", description: "debug" })
    });
    console.log("DEBUG: fetch returned status", res.status);
    const data = await res.json();
   

    console.log("DEBUG: response json", data);
    if (data.badge_awarded) setBadge(data.badge_awarded);
  } catch (err) {
    console.error("DEBUG: fetch error", err);
  }
}


  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h1>🚀 Productivity App</h1>
      <button 
        onClick={addTask} 
        style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}
      >
        Add Task
      </button>

      <BadgePopup badge={badge} onClose={() => setBadge(null)} />
    </div>
  );
}

export default App;
