import { useState, useEffect } from "react";

export default function NPC() {
  const [pos, setPos] = useState({ x: 100, y: 100 });
  const speed = 10;

  useEffect(() => {
    const handleKey = (e) => {
      setPos((prev) => {
        switch (e.key) {
          case "ArrowLeft":
            return { ...prev, x: prev.x - speed };
          case "ArrowRight":
            return { ...prev, x: prev.x + speed };
          case "ArrowUp":
            return { ...prev, y: prev.y - speed };
          case "ArrowDown":
            return { ...prev, y: prev.y + speed };
          default:
            return prev;
        }
      });
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  return (
    <div
      style={{
        position: "relative",
        width: "600px",
        height: "400px",
        border: "2px solid #333",
        marginTop: "20px",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: pos.x,
          top: pos.y,
          width: "50px",
          height: "50px",
          borderRadius: "50%",
          background: "#4cc9f0",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "24px",
        }}
      >
        🙂
      </div>
    </div>
  );
}
