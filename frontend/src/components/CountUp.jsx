import React, { useState, useEffect } from "react";

export default function CountUp({ end, duration = 800, suffix = "" }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * end));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }, [end, duration]);
  return <span>{count}{suffix}</span>;
}
