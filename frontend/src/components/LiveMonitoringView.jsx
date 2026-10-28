import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { RefreshCw, Upload, Video, Eye, Camera, CheckCircle, AlertTriangle } from "lucide-react";
import { API_URL } from "../config";

export default function LiveMonitoringView({ token }) {
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterZone, setFilterZone] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");

  const [inspectingViolation, setInspectingViolation] = useState(null);
  const [auditNotes, setAuditNotes] = useState("");
  const [auditStatus, setAuditStatus] = useState("unresolved");
  const [saveLoading, setSaveLoading] = useState(false);

  // --- 1. File Upload Verification States ---
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLocation, setUploadLocation] = useState("Main Site");
  const [uploadArea, setUploadArea] = useState("Scaffold Zone");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  // --- 2. Live Hardware Camera (USB / Webcam / Phone) States ---
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [videoDevices, setVideoDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [facingMode, setFacingMode] = useState("user");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamLoading, setStreamLoading] = useState(false);
  const [camLocation, setCamLocation] = useState("Live Patrol Feed");
  const [camArea, setCamArea] = useState("Active Inspection Zone");
  const [capturing, setCapturing] = useState(false);
  const [liveResult, setLiveResult] = useState(null);

  // Enumerate connected cameras (USB, Webcams, Phone cameras)
  const enumerateCameras = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter(d => d.kind === "videoinput");
      setVideoDevices(videoInputs);
      if (videoInputs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(videoInputs[0].deviceId);
      }
    } catch (err) {
      console.error("Camera enumeration error:", err);
    }
  };

  useEffect(() => {
    enumerateCameras();
  }, []);

  // Start Live Camera Stream
  const startCameraStream = async (deviceIdToUse = selectedDeviceId, currentFacing = facingMode) => {
    setStreamLoading(true);
    stopCameraStream();

    try {
      const constraints = {
        video: deviceIdToUse
          ? { deviceId: { exact: deviceIdToUse } }
          : { facingMode: currentFacing, width: { ideal: 1280 }, height: { ideal: 720 } }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsStreaming(true);
      enumerateCameras(); // Refresh device names once permission is granted
    } catch (err) {
      console.error("Failed to start camera:", err);
      alert("Could not access camera device. Please grant camera permissions and make sure no other application is using it.");
    } finally {
      setStreamLoading(false);
    }
  };

  // Stop Live Camera Stream
  const stopCameraStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  };

  // Toggle Camera Facing Mode (Front / Rear / USB)
  const toggleFacingMode = () => {
    const nextFacing = facingMode === "user" ? "environment" : "user";
    setFacingMode(nextFacing);
    if (isStreaming) {
      startCameraStream("", nextFacing);
    }
  };

  // Capture Live Frame & Send to AI Detection Backend
  const captureAndAnalyzeLiveFrame = async () => {
    if (!videoRef.current || !isStreaming) {
      alert("Please start the live camera feed first.");
      return;
    }

    setCapturing(true);
    setLiveResult(null);

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current || document.createElement("canvas");
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          alert("Failed to capture frame.");
          setCapturing(false);
          return;
        }

        const formData = new FormData();
        formData.append("image", blob, `live_capture_${Date.now()}.jpg`);
        formData.append("location", camLocation);
        formData.append("area_type", camArea);

        try {
          const res = await axios.post(`${API_URL}/api/detect/upload`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
              "Authorization": `Bearer ${token}`
            }
          });

          setLiveResult(res.data);
          if (res.data.violations_count > 0) {
            alert(`🚨 ${res.data.violations_count} PPE Violation(s) Detected! Alert notification dispatched to Telegram.`);
          } else {
            alert("✓ Frame compliant! No PPE violations detected.");
          }
          fetchViolations();
        } catch (err) {
          console.error("Live detection error:", err);
          alert(err.response?.data?.error || "Failed to analyze live camera frame.");
        } finally {
          setCapturing(false);
        }
      }, "image/jpeg", 0.92);

    } catch (err) {
      console.error(err);
      setCapturing(false);
    }
  };

  useEffect(() => {
    return () => {
      stopCameraStream();
    };
  }, []);

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploadLoading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append("image", uploadFile);
    formData.append("location", uploadLocation);
    formData.append("area_type", uploadArea);

    try {
      const res = await axios.post(`${API_URL}/api/detect/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": `Bearer ${token}`
        }
      });
      setUploadResult(res.data);
      alert(`Upload analyzed: ${res.data.violations_count} violations detected! Alert notifications dispatched to Telegram.`);
      fetchViolations();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Error analyzing uploaded file.");
    } finally {
      setUploadLoading(false);
    }
  };

  const fetchViolations = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/api/violations?limit=50`);
      setViolations(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchViolations();
  }, []);

  // Built-in default camera feeds
  const dynamicCameras = [
    { id: "cam-1", name: "Main Scaffold Zone", location: "Main Site", activeWorkers: 12 },
    { id: "cam-2", name: "Basement Excavation", location: "South Site", activeWorkers: 5 },
    { id: "cam-3", name: "Tech Lab Entry", location: "Tech Park", activeWorkers: 2 },
    { id: "cam-4", name: "Warehouse Loading", location: "North Zone", activeWorkers: 8 },
  ];

  const filteredCameras = dynamicCameras.filter(camera => {
    const match = camera.location.toLowerCase().includes(filterZone.toLowerCase()) ||
                  camera.name.toLowerCase().includes(filterZone.toLowerCase());
    if (!match) return false;
    if (!filterSeverity) return true;
    const cameraViolations = violations.filter(v => v.location.toLowerCase().includes(camera.location.toLowerCase()));
    return cameraViolations.some(v => v.severity?.toLowerCase() === filterSeverity.toLowerCase() && v.status !== "resolved");
  });

  const openCameraDrawer = (camera) => {
    setSelectedCamera(camera);
    const cameraViolations = violations.filter(v => v.location.toLowerCase().includes(camera.location.toLowerCase()));
    if (cameraViolations.length > 0) {
      loadInspectingIncident(cameraViolations[0]);
    } else {
      setInspectingViolation(null);
      setAuditNotes("");
      setAuditStatus("unresolved");
    }
  };

  const loadInspectingIncident = (incident) => {
    setInspectingViolation(incident);
    setAuditNotes(incident.notes || "");
    setAuditStatus(incident.status || "unresolved");
  };

  const handleSaveAudit = async (e) => {
    e.preventDefault();
    if (!inspectingViolation) return;
    setSaveLoading(true);
    try {
      await Promise.all([
        axios.post(`${API_URL}/api/violations/${inspectingViolation.id}/notes`, { notes: auditNotes }),
        axios.post(`${API_URL}/api/violations/${inspectingViolation.id}/status`, { status: auditStatus })
      ]);
      alert("Incident audit committed successfully.");
      setViolations(prev => prev.map(v => v.id === inspectingViolation.id ? { ...v, status: auditStatus, notes: auditNotes } : v));
      fetchViolations();
    } catch (err) {
      console.error(err);
      alert("Failed to commit audit changes.");
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Live Video Monitoring</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>CCTV network streams and live hardware camera compliance feeds</p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <select className="form-control-select" value={filterZone} onChange={e => setFilterZone(e.target.value)}>
            <option value="">All Zones</option>
            {Array.from(new Set(dynamicCameras.map(c => c.location))).map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
          <select className="form-control-select" value={filterSeverity} onChange={e => setFilterSeverity(e.target.value)}>
            <option value="">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* 2.1 MODEL VERIFICATION TEST BENCH (FILE UPLOAD) */}
      <div className="glass-panel tab-fade-container" style={{ padding: "1.25rem", marginBottom: "1.5rem" }}>
        <h4 style={{ fontSize: "0.95rem", fontWeight: "600", color: "#fff", display: "flex", alignItems: "center", gap: "0.5rem", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
          <span>🤖 Model Verification Test Bench (Image Upload)</span>
          <span style={{ fontSize: "0.75rem", fontWeight: "400", color: "var(--text-muted)", marginLeft: "auto" }}>
            Upload a camera frame or site snapshot to analyze YOLOv8 classifications & verify alert notifications
          </span>
        </h4>
        
        <form onSubmit={handleUploadSubmit} style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="form-input-group" style={{ marginBottom: 0, flex: 1, minWidth: "200px" }}>
            <label className="form-label">Test Site Name / Location</label>
            <input 
              type="text" 
              className="form-control-input" 
              value={uploadLocation} 
              onChange={e => setUploadLocation(e.target.value)} 
              placeholder="e.g. West Scaffold Wing"
              required 
            />
          </div>
          
          <div className="form-input-group" style={{ marginBottom: 0, flex: 1, minWidth: "200px" }}>
            <label className="form-label">Zone Area Type</label>
            <input 
              type="text" 
              className="form-control-input" 
              value={uploadArea} 
              onChange={e => setUploadArea(e.target.value)} 
              placeholder="e.g. Restricted Access"
              required 
            />
          </div>

          <div className="form-input-group" style={{ marginBottom: 0, flex: 1.5, minWidth: "250px" }}>
            <label className="form-label">Select Site Snapshot Frame (Image File)</label>
            <input 
              type="file" 
              accept="image/*" 
              className="form-control-input" 
              style={{ padding: "0.5rem" }}
              onChange={e => {
                if (e.target.files && e.target.files[0]) {
                  setUploadFile(e.target.files[0]);
                }
              }}
              required 
            />
          </div>

          <button 
            type="submit" 
            className="btn-premium" 
            style={{ height: "42px", padding: "0 1.5rem" }}
            disabled={uploadLoading || !uploadFile}
          >
            {uploadLoading ? (
              <RefreshCw style={{ animation: "spin 2s linear infinite" }} size={16} />
            ) : (
              <Upload size={16} />
            )}
            {uploadLoading ? "Analysing Frame..." : "Run AI Test Analysis"}
          </button>
        </form>

        {uploadResult && (
          <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(14,165,233,0.05)", border: "1px solid rgba(14,165,233,0.15)", borderRadius: "4px", fontSize: "0.85rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <span>Detections count: <strong>{uploadResult.violations_count} violations</strong></span>
              <span style={{ color: "var(--primary)" }}>Status: Active alerts dispatched to Telegram</span>
            </div>
            {uploadResult.detections.length > 0 ? (
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {uploadResult.detections.map((d, idx) => (
                  <span key={idx} className={`badge-pill ${d.is_violation ? "high" : "resolved"}`}>
                    {d.label} ({Math.round(d.confidence * 100)}%)
                  </span>
                ))}
              </div>
            ) : (
              <span style={{ color: "var(--success)" }}>✓ Frame compliant. No PPE violation detected.</span>
            )}
          </div>
        )}
      </div>

      {/* 2.2 LIVE HARDWARE CAMERA STREAM & CAPTURE SECTION (USB / WEBCAM / PHONE / MOBILE) */}
      <div className="glass-panel tab-fade-container" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.5rem" }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Camera size={20} style={{ color: "var(--primary)" }} />
              Live Hardware Camera Connection (USB / Integrated Webcam)
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", margin: "0.25rem 0 0" }}>
              Connect any external USB camera or integrated laptop webcam for real-time AI PPE analysis
            </p>
          </div>
        </div>

        {/* Camera Selector and Controls */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center", marginBottom: "1rem" }}>
          <div className="form-input-group" style={{ marginBottom: 0, flex: 1, minWidth: "220px" }}>
            <label className="form-label">Select Video Input Device (USB / Webcam)</label>
            <select 
              className="form-control-select" 
              value={selectedDeviceId} 
              onChange={e => {
                setSelectedDeviceId(e.target.value);
                if (isStreaming) startCameraStream(e.target.value);
              }}
            >
              {videoDevices.length > 0 ? (
                videoDevices.map((d, i) => (
                  <option key={d.deviceId || i} value={d.deviceId}>
                    {d.label || `Camera ${i + 1} (${d.deviceId.slice(0, 8)}...)`}
                  </option>
                ))
              ) : (
                <option value="">Default System Camera / Webcam</option>
              )}
            </select>
          </div>

          <div className="form-input-group" style={{ marginBottom: 0, width: "160px" }}>
            <label className="form-label">Inspect Location</label>
            <input 
              type="text" 
              className="form-control-input" 
              value={camLocation} 
              onChange={e => setCamLocation(e.target.value)} 
            />
          </div>

          <div className="form-input-group" style={{ marginBottom: 0, width: "160px" }}>
            <label className="form-label">Inspect Zone</label>
            <input 
              type="text" 
              className="form-control-input" 
              value={camArea} 
              onChange={e => setCamArea(e.target.value)} 
            />
          </div>

          <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-end", height: "42px" }}>
            {!isStreaming ? (
              <button 
                type="button" 
                className="btn-premium" 
                onClick={() => startCameraStream()}
                disabled={streamLoading}
                style={{ height: "42px", padding: "0 1.25rem" }}
              >
                {streamLoading ? <RefreshCw size={15} style={{ animation: "spin 1s linear infinite" }} /> : "▶ Start Live Camera"}
              </button>
            ) : (
              <button 
                type="button" 
                onClick={stopCameraStream}
                style={{ height: "42px", padding: "0 1.25rem", background: "rgba(239,68,68,0.2)", border: "1px solid rgba(239,68,68,0.4)", color: "#f87171", borderRadius: "6px", cursor: "pointer", fontWeight: "600" }}
              >
                ⏹ Stop Camera
              </button>
            )}

            <button 
              type="button"
              onClick={toggleFacingMode}
              disabled={!isStreaming}
              style={{ height: "42px", padding: "0 1rem", background: "transparent", border: "1px solid var(--border-glass)", color: "var(--text-muted)", borderRadius: "6px", cursor: isStreaming ? "pointer" : "not-allowed", fontSize: "0.82rem" }}
            >
              🔄 Switch Camera
            </button>
          </div>
        </div>

        {/* Video HUD Monitor Stream */}
        <div style={{ display: "grid", gridTemplateColumns: isStreaming ? "1.5fr 1fr" : "1fr", gap: "1rem" }}>
          <div className="camera-monitor" style={{ aspectRatio: "16/9", maxHeight: "420px", background: "#000", position: "relative", borderRadius: "8px", overflow: "hidden", border: "1px solid var(--border-glass)" }}>
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              style={{ width: "100%", height: "100%", objectFit: "cover", display: isStreaming ? "block" : "none" }}
            />

            {!isStreaming && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-muted)", gap: "0.75rem", padding: "2rem" }}>
                <Video size={42} style={{ opacity: 0.3 }} />
                <p style={{ margin: 0, fontWeight: "600" }}>Live Hardware Camera Feed Disconnected</p>
                <p style={{ fontSize: "0.8rem", margin: 0, textAlign: "center" }}>
                  Select your USB camera, laptop webcam, or phone camera above and click <strong>"▶ Start Live Camera"</strong>
                </p>
              </div>
            )}

            {isStreaming && (
              <div className="camera-overlay">
                <span className="status-dot active"></span>
                <span style={{ fontSize: "0.75rem", fontWeight: "600" }}>LIVE STREAMING: {camLocation.toUpperCase()}</span>
              </div>
            )}
          </div>

          {/* Real-time Capture Control Panel */}
          {isStreaming && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-glass)", borderRadius: "8px", padding: "1.25rem", justifyContent: "center" }}>
              <div>
                <h4 style={{ margin: "0 0 0.5rem", fontSize: "0.95rem" }}>📸 Live Frame AI Analysis</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", margin: 0 }}>
                  Capture a frame from the live video stream to run YOLOv8 PPE detection model and trigger Telegram alerts.
                </p>
              </div>

              <button 
                type="button" 
                className="btn-premium" 
                onClick={captureAndAnalyzeLiveFrame}
                disabled={capturing}
                style={{ padding: "0.75rem 1.5rem", fontWeight: "700" }}
              >
                {capturing ? (
                  <><RefreshCw size={16} style={{ animation: "spin 1s linear infinite" }} /> Analysing Frame...</>
                ) : (
                  <>📸 Capture & Run AI Detection</>
                )}
              </button>

              {liveResult && (
                <div style={{ padding: "0.85rem", background: "rgba(14,165,233,0.08)", border: "1px solid rgba(14,165,233,0.2)", borderRadius: "6px", fontSize: "0.82rem" }}>
                  <p style={{ fontWeight: "700", color: "#38bdf8", margin: "0 0 0.35rem" }}>
                    Result: {liveResult.violations_count} PPE Violation(s)
                  </p>
                  {liveResult.detections.length > 0 ? (
                    <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                      {liveResult.detections.map((d, idx) => (
                        <span key={idx} className={`badge-pill ${d.is_violation ? "high" : "resolved"}`}>
                          {d.label} ({Math.round(d.confidence * 100)}%)
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: "#4ade80" }}>✓ All workers compliant.</span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div 
        style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", 
          gap: "1.5rem",
          opacity: selectedCamera ? 0.35 : 1,
          filter: selectedCamera ? "blur(3px)" : "none",
          transition: "all 0.3s ease"
        }}
      >
        {filteredCameras.map(camera => {
          const cameraViolations = violations.filter(v => v.location.toLowerCase().includes(camera.location.toLowerCase()));
          const count = cameraViolations.filter(v => v.status !== "resolved").length;

          return (
            <div 
              key={camera.id} 
              className="glass-panel" 
              style={{ padding: "1rem", cursor: "pointer" }}
              onClick={() => openCameraDrawer(camera)}
            >
              <div className="camera-monitor" style={{ aspectRatio: "16 / 10", marginBottom: "0.75rem" }}>
                {cameraViolations.length > 0 ? (
                  <img src={`${API_URL}/api/violations/images/${cameraViolations[0].image_url}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} alt="Camera Feed" />
                ) : (
                  <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center" }}>
                    <Video size={32} style={{ margin: "0 auto 0.5rem", opacity: 0.2 }} />
                    Live CCTV Stream: {camera.name}
                  </div>
                )}
                
                <div className="camera-overlay">
                  <span className="status-dot active"></span>
                  <span style={{ fontSize: "0.75rem", fontWeight: "600" }}>{camera.name.toUpperCase()}</span>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                <div>
                  <p style={{ fontWeight: "600" }}>{camera.location}</p>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>Active Workers: {camera.activeWorkers}</p>
                </div>
                <span className={`badge-pill ${count > 0 ? "high" : "resolved"}`} style={{ alignSelf: "center" }}>
                  {count > 0 ? `${count} Violations` : "Compliant"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* CCTV Timeline Detail Drawer */}
      {selectedCamera && (
        <div 
          className="image-modal-overlay" 
          style={{ justifyContent: "center", alignItems: "center", padding: "1.5rem", backdropFilter: "blur(8px)", transition: "backdrop-filter 0.3s ease" }}
          onClick={() => setSelectedCamera(null)}
        >
          <div 
            className="glass-panel tab-fade-container" 
            style={{ width: "100%", maxWidth: "780px", maxHeight: "90vh", borderRadius: "8px", padding: "2rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.5rem", background: "var(--bg-card)", border: "1px solid var(--border-glass)", boxShadow: "0 10px 30px rgba(0,0,0,0.5)" }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "1rem" }}>
              <div>
                <h3 style={{ fontSize: "1.25rem" }}>CCTV Audit Inspector</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>{selectedCamera.name} - {selectedCamera.location}</p>
              </div>
              <button 
                type="button"
                className="btn-premium" 
                style={{ background: "transparent", border: "1px solid var(--border-glass)", padding: "0.4rem 0.8rem" }}
                onClick={() => setSelectedCamera(null)}
              >
                Close
              </button>
            </div>

            <div className="camera-monitor" style={{ aspectRatio: "16/9" }}>
              {inspectingViolation ? (
                <img src={`${API_URL}/api/violations/images/${inspectingViolation.image_url}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} alt="Evidence" />
              ) : (
                <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No active violation incidents.</div>
              )}
              <div className="camera-overlay">
                <span className="status-dot active"></span>
                <span style={{ fontSize: "0.75rem", fontWeight: "600" }}>EXPANDED HUD VIEW</span>
              </div>
            </div>

            {/* Horizontal Timeline */}
            <div>
              <span className="form-label" style={{ display: "block", marginBottom: "0.5rem" }}>Incident Timeline</span>
              <div style={{ display: "flex", gap: "0.75rem", overflowX: "auto", paddingBottom: "0.5rem" }}>
                {violations
                  .filter(v => v.location.toLowerCase().includes(selectedCamera.location.toLowerCase()))
                  .map(v => (
                    <div 
                      key={v.id} 
                      style={{ 
                        flexShrink: 0, 
                        width: "120px", 
                        background: inspectingViolation?.id === v.id ? "rgba(14,165,233,0.2)" : "rgba(255,255,255,0.03)", 
                        border: inspectingViolation?.id === v.id ? "1px solid var(--primary)" : "1px solid var(--border-glass)", 
                        borderRadius: "6px", 
                        padding: "0.5rem", 
                        cursor: "pointer" 
                      }}
                      onClick={() => loadInspectingIncident(v)}
                    >
                      <div style={{ fontSize: "0.7rem", fontWeight: "600", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {v.equipment_type}
                      </div>
                      <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                        {new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Incident Audit Form */}
            {inspectingViolation && (
              <form onSubmit={handleSaveAudit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  <div className="form-input-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Violation Status</label>
                    <select className="form-control-select" value={auditStatus} onChange={e => setAuditStatus(e.target.value)}>
                      <option value="unresolved">Unresolved (Active Hazard)</option>
                      <option value="in_review">In Review (Investigating)</option>
                      <option value="resolved">Resolved (Compliant)</option>
                    </select>
                  </div>
                  <div className="form-input-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Severity Level</label>
                    <input className="form-control-input" value={inspectingViolation.severity?.toUpperCase()} disabled />
                  </div>
                </div>

                <div className="form-input-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Audit Notes & Actions Taken</label>
                  <textarea 
                    className="form-control-input" 
                    rows={3} 
                    value={auditNotes} 
                    onChange={e => setAuditNotes(e.target.value)} 
                    placeholder="Enter supervisor findings, worker warnings, or corrective actions..."
                  />
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
                  <button type="submit" className="btn-premium" disabled={saveLoading}>
                    {saveLoading ? "Saving Audit..." : "Commit Audit"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

    </>
  );
}
