import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { Video, RefreshCw, AlertTriangle, ArrowLeft } from "lucide-react";
import { API_URL } from "../config";

export default function MobileCaptureView({ token, onBack }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  const [stream, setStream] = useState(null);
  const [facingMode, setFacingMode] = useState("environment"); // default to rear environment camera
  const [loading, setLoading] = useState(false);
  const [isCapturing, setIsCapturing] = useState(true);
  const [detections, setDetections] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  // Start the video stream
  const startStream = async () => {
    setErrorMessage("");
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: facingMode,
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Camera access error:", err);
      setErrorMessage("Could not access camera. Please allow camera permissions and ensure no other app is using it.");
    }
  };

  useEffect(() => {
    startStream();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [facingMode]);

  // Toggle front/rear camera
  const toggleCamera = () => {
    setFacingMode(prev => (prev === "environment" ? "user" : "environment"));
  };

  // Capture frame and send to AI Service for evaluation
  const captureFrameAndAnalyze = async () => {
    if (!videoRef.current || !canvasRef.current || !isCapturing || loading) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Match canvas size to video frame size
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Draw video frame to hidden canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas image to blob and upload
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      
      setLoading(true);
      const formData = new FormData();
      formData.append("image", blob, "mobile_frame.jpg");
      formData.append("location", "Mobile Inspection Feed");
      formData.append("area_type", "Active Site Inspection");

      try {
        const res = await axios.post(`${API_URL}/api/detect/upload`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            "Authorization": `Bearer ${token}`
          }
        });
        setDetections(res.data.detections || []);
      } catch (err) {
        console.error("Mobile inspection upload failed:", err);
      } finally {
        setLoading(false);
      }
    }, "image/jpeg", 0.85);
  };

  // Run analysis every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (stream) {
        captureFrameAndAnalyze();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [stream, facingMode, isCapturing]);

  return (
    <div style={{ minHeight: "100vh", background: "#080c14", color: "#fff", display: "flex", flexDirection: "column", padding: "1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
        <button 
          type="button" 
          className="btn-premium" 
          style={{ background: "transparent", border: "1px solid var(--border-glass)", padding: "0.5rem 1rem" }}
          onClick={onBack}
        >
          <ArrowLeft size={16} /> Back
        </button>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: "700" }}>Mobile Safety Inspector</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Real-time supervisor safety patrol stream</p>
        </div>
      </div>

      {errorMessage ? (
        <div className="glass-panel" style={{ padding: "2rem", textAlign: "center", background: "rgba(239, 68, 68, 0.05)", border: "1px solid rgba(239, 68, 68, 0.15)" }}>
          <AlertTriangle size={48} style={{ color: "var(--severity-high)", marginBottom: "1rem" }} />
          <p>{errorMessage}</p>
          <button type="button" className="btn-premium" style={{ marginTop: "1rem" }} onClick={startStream}>
            Retry Camera Access
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", flex: 1 }}>
          <div className="camera-monitor" style={{ flex: 1, aspectRatio: "4/3", maxHeight: "60vh", background: "#000", position: "relative", borderRadius: "8px", overflow: "hidden", border: "1px solid var(--border-glass)" }}>
            <video 
              ref={videoRef}
              autoPlay 
              playsInline 
              muted 
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            
            {/* Real-time bounding boxes canvas overlays */}
            <canvas ref={canvasRef} style={{ display: "none" }} />

            {/* Detections Overlay HUD */}
            <div style={{ position: "absolute", bottom: "1rem", left: "1rem", right: "1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap", zIndex: 10 }}>
              {detections.map((d, idx) => (
                <span 
                  key={idx} 
                  className={`badge-pill ${d.is_violation ? "high" : "resolved"}`}
                  style={{ textShadow: "0 1px 2px rgba(0,0,0,0.8)", boxShadow: "0 2px 4px rgba(0,0,0,0.5)" }}
                >
                  {d.label} ({Math.round(d.confidence * 100)}%)
                </span>
              ))}
              {detections.length === 0 && (
                <span className="badge-pill resolved" style={{ background: "rgba(22, 163, 74, 0.8)", color: "#fff" }}>
                  ✓ Scanning environment...
                </span>
              )}
            </div>

            <div className="camera-overlay">
              <span className="status-dot active"></span>
              <span style={{ fontSize: "0.75rem", fontWeight: "600", textTransform: "uppercase" }}>
                Active: {facingMode === "environment" ? "Rear (Patrol)" : "Front (Selfie)"}
              </span>
            </div>

            {loading && (
              <div style={{ position: "absolute", top: "1rem", right: "1rem", background: "rgba(0,0,0,0.6)", padding: "0.4rem 0.8rem", borderRadius: "4px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <RefreshCw style={{ animation: "spin 2s linear infinite" }} size={12} />
                <span>AI evaluating frame...</span>
              </div>
            )}
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button 
              type="button" 
              className="btn-premium" 
              style={{ flex: 1, height: "46px" }}
              onClick={toggleCamera}
            >
              Switch to {facingMode === "environment" ? "Front Selfie Camera" : "Rear Patrol Camera"}
            </button>
            <button 
              type="button" 
              className="btn-premium" 
              style={{ 
                flex: 1, 
                height: "46px",
                background: isCapturing ? "rgba(239, 68, 68, 0.15)" : "rgba(14, 165, 233, 0.15)",
                border: isCapturing ? "1px solid #ef4444" : "1px solid var(--primary)",
                color: isCapturing ? "#ef4444" : "var(--primary)"
              }}
              onClick={() => setIsCapturing(prev => !prev)}
            >
              {isCapturing ? "Pause Scanning" : "Resume Scanning"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
