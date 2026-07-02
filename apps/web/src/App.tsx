import React from "react";

function App() {
  return (
    <div className="welcome-card">
      <h1>Brain</h1>
      <p className="subtitle">Local-first AI Knowledge Platform</p>
      <div style={{ margin: "2rem 0", color: "#8b949e" }}>
        Repository foundation initialized successfully. Ready for UI development.
      </div>
      <div className="tech-grid">
        <div className="tech-tag">React</div>
        <div className="tech-tag">TypeScript</div>
        <div className="tech-tag">Vite</div>
        <div className="tech-tag">FastAPI</div>
        <div className="tech-tag">PySide6</div>
        <div className="tech-tag">Ollama</div>
      </div>
    </div>
  );
}

export default App;
