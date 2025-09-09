import NPC from "./NPC";

function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>משחקון React</h1>
      <p>תזיז את ה־NPC עם מקשי החיצים ← ↑ ↓ →</p>
      <NPC />
    </div>
  );
}

export default App;
