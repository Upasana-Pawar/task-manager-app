import { useEffect } from "react";
import confetti from "canvas-confetti";

export default function BadgePopup({ badge, onClose }) {
  useEffect(() => {
    if (!badge) return;
    confetti({
      particleCount: 120,
      spread: 70,
      origin: { y: 0.4 }
    });
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [badge]);

  if (!badge) return null;

  return (
    <div style={{
      position: "fixed",
      left: "50%",
      top: "18%",
      transform: "translateX(-50%)",
      background: "white",
      padding: "20px",
      borderRadius: "12px",
      boxShadow: "0 8px 30px rgba(0,0,0,0.2)",
      zIndex: 9999,
      textAlign: "center",
      minWidth: "260px"
    }}>
      <div style={{ fontSize: "42px" }}>{badge.emoji}</div>
      <h3 style={{ margin: "6px 0" }}>{badge.name}</h3>
      <p style={{ margin: 0 }}>{badge.description}</p>
    </div>
  );
}
