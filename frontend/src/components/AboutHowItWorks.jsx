import React, { useState } from "react";
import { HardHat } from "lucide-react";

export default function AboutHowItWorks({ onEnterDashboard, onEnterGuidelines }) {
  const [activePipelineStep, setActivePipelineStep] = useState("camera");
  
  // Interactive Human Action state
  const [incidentStatus, setIncidentStatus] = useState("NEW");

  const pipelineSteps = [
    { id: "camera", num: "01", name: "Camera" },
    { id: "ingestion", num: "02", name: "Ingestion" },
    { id: "vision", num: "03", name: "AI Vision" },
    { id: "detect", num: "04", name: "Detect" },
    { id: "risk", num: "05", name: "Risk Engine" },
    { id: "alert", num: "06", name: "Alert" },
    { id: "evidence", num: "07", name: "Evidence" },
    { id: "human", num: "08", name: "Human Action" },
    { id: "analytics", num: "09", name: "Analytics" }
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "3.5rem", maxWidth: "1100px", margin: "7.5rem auto 4rem", padding: "0 1.5rem" }}>
      
      {/* 1. CINEMATIC HERO SECTION */}
      <section style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "2.5rem", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "3rem" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "var(--primary)", letterSpacing: "1.5px", textTransform: "uppercase" }}>
            About WorkerShield
          </span>
          <h1 style={{ fontSize: "2.85rem", fontWeight: "800", color: "#fff", lineHeight: 1.1 }}>
            From camera feed<br />to safety decision.
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", lineHeight: "1.5", maxWidth: "550px" }}>
            WorkerShield transforms continuous construction-site video into actionable safety intelligence — helping teams identify risks, investigate incidents and respond before unsafe situations become incidents.
          </p>
          <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
            <button className="btn-premium" style={{ fontSize: "0.95rem", padding: "0.75rem 1.5rem" }} onClick={() => {
              const el = document.getElementById("pipeline-section");
              if (el) el.scrollIntoView({ behavior: "smooth" });
            }}>
              Explore How It Works ↓
            </button>
            <button 
              className="btn-premium" 
              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", fontSize: "0.95rem", padding: "0.75rem 1.5rem", color: "#fff" }}
              onClick={onEnterDashboard}
            >
              Open Dashboard →
            </button>
          </div>
        </div>

        {/* Right Hero Video Mockup */}
        <div className="glass-panel" style={{ padding: "0.5rem", position: "relative", borderRadius: "6px", overflow: "hidden" }}>
          <div className="camera-monitor" style={{ aspectRatio: "16 / 10" }}>
            <video autoPlay loop muted playsInline style={{ width: "100%", height: "100%", objectFit: "cover" }}>
              <source src="https://assets.mixkit.co/videos/preview/mixkit-workers-on-a-construction-site-40348-large.mp4" type="video/mp4" />
            </video>
            <div className="camera-overlay">
              <span className="status-dot active"></span>
              <span style={{ fontSize: "0.75rem", fontWeight: "600" }}>CAM-07 • ZONE B</span>
            </div>

            {/* Simulated Bounding Overlays */}
            <div className="cv-bounding-box" style={{ top: "15%", left: "20%", width: "100px", height: "180px" }}>
              <span className="cv-box-label" style={{ fontSize: "0.6rem" }}>worker [97%]</span>
            </div>
            <div className="cv-bounding-box violating" style={{ top: "30%", right: "20%", width: "95px", height: "170px" }}>
              <span className="cv-box-label" style={{ fontSize: "0.6rem" }}>missing hardhat [96%]</span>
            </div>
            
            <span style={{ position: "absolute", bottom: "0.75rem", left: "0.75rem", fontSize: "0.65rem", fontWeight: "700", color: "var(--success)" }}>
              ● AI MONITORING ACTIVE
            </span>
          </div>
        </div>
      </section>

      {/* 2. THE PROBLEM / WHY WE EXIST */}
      <section style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "3rem", alignItems: "center" }}>
        <div>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--severity-high)", textTransform: "uppercase" }}>The Problem</span>
          <h2 style={{ fontSize: "1.75rem", color: "#fff", margin: "0.5rem 0 1rem" }}>
            Construction sites don't stop when the safety team looks away.
          </h2>
          <p style={{ color: "var(--text-main)", fontSize: "0.95rem", lineHeight: "1.6", marginBottom: "1rem" }}>
            Modern construction sites contain dozens of active cameras, multiple complex work zones, heavy vehicles, and hundreds of personnel.
          </p>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
            A safety officer cannot watch every screen continuously. Attention declines by up to 50% after just 20 minutes of screen monitoring. WorkerShield provides continuous, objective computer-vision checks to capture hazards the moment they occur.
          </p>
        </div>

        {/* Traditional vs WorkerShield Ingestion Logic Block */}
        <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div>
            <span style={{ fontSize: "0.7rem", color: "var(--severity-high)", fontWeight: "700" }}>TRADITIONAL AUDITING</span>
            <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginTop: "0.25rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
              <span>24/7 VIDEO</span> ➔ <span>THOUSANDS OF FRAMES</span> ➔ <span>HUMAN FATIGUE</span> ➔ <span>LIMITED FOCUS</span>
            </div>
          </div>
          <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "1rem" }}>
            <span style={{ fontSize: "0.7rem", color: "var(--success)", fontWeight: "700" }}>WORKERSHIELD PIPELINE</span>
            <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginTop: "0.25rem", fontSize: "0.8rem", color: "#fff", fontWeight: "600" }}>
              <span>CONTINUOUS MONITORS</span> + <span>AI TELEMETRY</span> + <span>SUPERVISOR DECISION</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. CORE PHILOSOPHY STATEMENT */}
      <section className="glass-panel" style={{ padding: "2.5rem", textAlign: "center", display: "flex", flexDirection: "column", gap: "1rem", background: "#0b0f19" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "800", color: "#fff" }}>
          WE DON'T REPLACE THE SAFETY TEAM.<br />WE GIVE THEM BETTER VISIBILITY.
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "700px", margin: "0 auto 1.5rem" }}>
          WorkerShield is designed around a simple principle: AI should identify potential risks and surface the evidence. People make the safety decision.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", maxWidth: "600px", margin: "0 auto" }}>
          <div style={{ background: "rgba(255,255,255,0.01)", border: "1px solid var(--border-glass)", padding: "1.25rem", borderRadius: "4px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>AI Scope</span>
            <p style={{ fontSize: "1.1rem", fontWeight: "700", color: "#fff", marginTop: "0.25rem" }}>OBSERVES + DETECTS + PRIORITIZES</p>
          </div>
          <div style={{ background: "rgba(255,255,255,0.01)", border: "1px solid var(--border-glass)", padding: "1.25rem", borderRadius: "4px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--success)", textTransform: "uppercase" }}>Human Scope</span>
            <p style={{ fontSize: "1.1rem", fontWeight: "700", color: "#fff", marginTop: "0.25rem" }}>VERIFIES + RESPONDS + DECIDES</p>
          </div>
        </div>
      </section>

      {/* 4. MAIN INTERACTIVE SYSTEM PIPELINE */}
      <section id="pipeline-section" className="glass-panel" style={{ padding: "2.5rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
        <div>
          <h2 style={{ fontSize: "1.5rem", color: "#fff" }}>HOW WORKERSHIELD WORKS</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>One continuous pipeline from live video to actionable safety intelligence.</p>
        </div>

        {/* Stepper Navigation bar (Horizontal on desktop, scrolls on mobile) */}
        <div style={{ display: "flex", gap: "0.5rem", overflowX: "auto", borderBottom: "1px solid var(--border-glass)", paddingBottom: "1rem" }}>
          {pipelineSteps.map(step => (
            <button
              key={step.id}
              className="btn-premium"
              style={{
                background: activePipelineStep === step.id ? "var(--primary)" : "transparent",
                color: activePipelineStep === step.id ? "#080c14" : "var(--text-muted)",
                border: "1px solid " + (activePipelineStep === step.id ? "var(--primary)" : "transparent"),
                padding: "0.5rem 0.85rem",
                fontSize: "0.8rem",
                fontWeight: "700",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem"
              }}
              onClick={() => setActivePipelineStep(step.id)}
            >
              <span style={{ opacity: 0.6 }}>{step.num}</span>
              <span>{step.name}</span>
            </button>
          ))}
        </div>

        {/* Step Panels */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "2.5rem", alignItems: "center", minHeight: "260px" }}>
          
          {/* Left panel: text descriptions */}
          <div>
            {activePipelineStep === "camera" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 01</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Camera Stream Source</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  WorkerShield interfaces directly with site CCTV security cameras via network RTSP streams or WebRTC integrations to capture live video frames.
                </p>
              </div>
            )}
            {activePipelineStep === "ingestion" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 02</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Stream Ingestion Pipeline</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Incoming high-definition streams are decoded and scheduled into asynchronous worker arrays. Frames are batched dynamically to maintain minimal network latency.
                </p>
              </div>
            )}
            {activePipelineStep === "vision" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 03</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Computer Vision Processing</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Trained deep-learning models evaluate the target frames in milliseconds, localizing bounding coordinates for workers and verifying PPE compliance details.
                </p>
              </div>
            )}
            {activePipelineStep === "detect" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 04</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Safety Event Detection</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Class classifications are processed by configured site zoning rules. Missing safety helmets or vests are registered as safety breach logs.
                </p>
              </div>
            )}
            {activePipelineStep === "risk" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 05</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Risk & Severity Assessment</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Rather than outputting raw object classifications, the system correlates the breach location, duration, and worker proximity markers to assign a weighted severity score (e.g. Critical, High, or Medium).
                </p>
              </div>
            )}
            {activePipelineStep === "alert" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 06</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Proactive Dispatch Alert</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Actions requiring immediate attention bypass standard dashboards and dispatch alerts containing context snapshots directly to Telegram and WhatsApp.
                </p>
              </div>
            )}
            {activePipelineStep === "evidence" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 07</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Audit-Trail Evidence Logs</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Every flagged event is stored in PostgreSQL alongside its target frame snapshot, timestamp, camera index, and detection model tag to build a legal OSHA audit log.
                </p>
              </div>
            )}
            {activePipelineStep === "human" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 08</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Supervisor Audit Verification</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Site safety officers inspect the evidence drawer, modify the incident status to Investigating or Resolved, and type detailed field notes.
                </p>
              </div>
            )}
            {activePipelineStep === "analytics" && (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "700" }}>STEP 09</span>
                <h3 style={{ color: "#fff", fontSize: "1.25rem", margin: "0.25rem 0 0.75rem" }}>Safety Trend Analytics</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  Aggregated logs map recurring hazard zones, calculate compliance averages, and expose safety trend insight rates for management review.
                </p>
              </div>
            )}
          </div>

          {/* Right panel: technical mockup visuals */}
          <div className="glass-panel" style={{ padding: "1.25rem", background: "#05070a", minHeight: "180px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
            {activePipelineStep === "camera" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <span className="badge-pill high" style={{ alignSelf: "flex-start", background: "rgba(14,165,233,0.1)", color: "var(--primary)" }}>RTSP ACTIVE</span>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  <p>STREAM SOURCE: <strong>CAM-07-NORTH</strong></p>
                  <p>TELEMETRY RESOLUTION: <strong>1920 × 1080 @ 30 FPS</strong></p>
                  <p>STATUS: <span style={{ color: "var(--success)" }}>LIVE COMPLIANT</span></p>
                </div>
              </div>
            )}
            {activePipelineStep === "ingestion" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>CONNECTED CHANNELS</span>
                  <span style={{ color: "#fff", fontWeight: "700" }}>24 ONLINE</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>INGESTION LATENCY</span>
                  <span style={{ color: "var(--success)", fontWeight: "700" }}>LOW (45ms)</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>BUFFER STATUS</span>
                  <span style={{ color: "var(--success)", fontWeight: "700" }}>HEALTHY</span>
                </div>
              </div>
            )}
            {activePipelineStep === "vision" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                <span className="badge-pill high" style={{ alignSelf: "flex-start", background: "rgba(22,163,74,0.1)", color: "var(--success)" }}>YOLOv8 INFERENCE</span>
                <p>● worker detected (98.4% confidence)</p>
                <p>● hardhat compliance: <span style={{ color: "var(--success)" }}>✓ COMPLIANT (97.2%)</span></p>
                <p>● high-vis clothing: <span style={{ color: "var(--success)" }}>✓ COMPLIANT (94.8%)</span></p>
              </div>
            )}
            {activePipelineStep === "detect" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.85rem" }}>
                <p>🔎 worker ID: <strong>WORKER #184</strong></p>
                <p>📍 active zone: <strong>ZONE B RESTRICTED</strong></p>
                <p>⏱️ duration track: <span style={{ color: "var(--severity-medium)" }}>00:14 ACTIVE</span></p>
              </div>
            )}
            {activePipelineStep === "risk" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem" }}>
                  <span>RISK ASSESSMENT INDEX</span>
                  <span style={{ color: "var(--severity-high)", fontWeight: "700" }}>92 / 100</span>
                </div>
                {/* Risk Meter */}
                <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.05)", borderRadius: "4px", overflow: "hidden" }}>
                  <div style={{ width: "92%", height: "100%", background: "var(--severity-high)" }}></div>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem", color: "var(--text-muted)" }}>
                  <span>LOW</span>
                  <span>MEDIUM</span>
                  <span>HIGH</span>
                  <span style={{ color: "var(--severity-high)", fontWeight: "700" }}>CRITICAL</span>
                </div>
              </div>
            )}
            {activePipelineStep === "alert" && (
              <div className="glass-panel pulse-warning-card" style={{ padding: "0.75rem", background: "rgba(220,38,38,0.03)", display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.8rem" }}>
                <p style={{ color: "var(--severity-high)", fontWeight: "700" }}>🔴 CRITICAL SAFETY INCIDENT</p>
                <p style={{ fontWeight: "600", color: "#fff" }}>NO HELMET IN RESTRICTED ZONE</p>
                <p style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>Zone B • CAM-07 • detected 14:32:18</p>
                <span style={{ color: "var(--primary)", fontSize: "0.75rem", fontWeight: "700", marginTop: "0.25rem" }}>ALERT DISPATCHED ➔</span>
              </div>
            )}
            {activePipelineStep === "evidence" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                <p>INCIDENT ARCHIVE ID: <strong>#WS-10482</strong></p>
                <p>evidence frame: <span style={{ color: "var(--primary)" }}>evidence_snap_10482.jpg</span></p>
                <p>model tags validation: <strong>Vision Model v2.4</strong></p>
                <p>incident status log: <strong style={{ color: "var(--severity-high)" }}>UNRESOLVED</strong></p>
              </div>
            )}
            {activePipelineStep === "human" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem" }}>
                  <span>INCIDENT STATUS STATE</span>
                  <strong style={{ color: incidentStatus === "RESOLVED" ? "var(--success)" : incidentStatus === "ACKNOWLEDGED" ? "var(--primary)" : "var(--severity-high)" }}>{incidentStatus}</strong>
                </div>
                
                {/* Stepper controls */}
                <div style={{ display: "flex", gap: "0.4rem" }}>
                  <button type="button" className="btn-premium" style={{ padding: "0.35rem 0.5rem", fontSize: "0.7rem", flexGrow: 1 }} onClick={() => setIncidentStatus("ACKNOWLEDGED")}>
                    Acknowledge
                  </button>
                  <button type="button" className="btn-premium" style={{ padding: "0.35rem 0.5rem", fontSize: "0.7rem", flexGrow: 1, background: "var(--success)" }} onClick={() => setIncidentStatus("RESOLVED")}>
                    Resolve
                  </button>
                </div>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textAlign: "center" }}>
                  {incidentStatus === "NEW" && "Awaiting supervisor validation"}
                  {incidentStatus === "ACKNOWLEDGED" && "Acknowledged: Field action taken"}
                  {incidentStatus === "RESOLVED" && "Resolved: Database logs archived"}
                </span>
              </div>
            )}
            {activePipelineStep === "analytics" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                <p>● site compliance average: <strong style={{ color: "var(--success)" }}>91.4%</strong></p>
                <p>● active incidents change: <strong style={{ color: "var(--success)" }}>↓ 18% (weekly)</strong></p>
                <p>● top category flagged: <strong style={{ color: "var(--severity-medium)" }}>no helmet</strong></p>
                <p style={{ color: "var(--primary)", fontSize: "0.7rem", fontWeight: "700" }}>INSIGHT: Zone B logs 34% more breaches than site average.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 5. DYNAMIC FULL-WIDTH PIPELINE SEQUENCE MAP */}
      <section className="glass-panel" style={{ padding: "2.5rem", display: "flex", flexDirection: "column", gap: "2rem", background: "#0b0f19" }}>
        <h3 style={{ fontSize: "1.25rem", color: "#fff", textAlign: "center" }}>FROM CAMERA TO ACTION</h3>
        
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem", position: "relative" }}>
          {[
            { step: "CAMERA", icon: "📹", desc: "Ingest RTSP" },
            { step: "INGEST", icon: "🌐", desc: "Batch frames" },
            { step: "AI VISION", icon: "🤖", desc: "YOLOv8 run" },
            { step: "DETECT", icon: "🔍", desc: "Track coordinates" },
            { step: "RISK ENGINE", icon: "📊", desc: "Weight rules" },
            { step: "ALERT", icon: "🔔", desc: "relays warnings" },
            { step: "EVIDENCE", icon: "📁", desc: "Archive frames" },
            { step: "HUMAN ACTION", icon: "👷", desc: "Acknowledge logs" },
            { step: "ANALYTICS", icon: "📈", desc: "Expose patterns" }
          ].map((item, idx, arr) => (
            <React.Fragment key={item.step}>
              <div 
                className="glass-panel" 
                style={{ 
                  flexGrow: 1, 
                  minWidth: "100px", 
                  padding: "0.75rem", 
                  textAlign: "center", 
                  background: activePipelineStep === item.step.toLowerCase() ? "var(--primary-glow)" : "rgba(255,255,255,0.01)",
                  borderColor: activePipelineStep === item.step.toLowerCase() ? "var(--primary)" : "var(--border-glass)"
                }}
              >
                <span style={{ fontSize: "1.25rem" }}>{item.icon}</span>
                <p style={{ color: "#fff", fontWeight: "700", fontSize: "0.75rem", marginTop: "0.25rem" }}>{item.step}</p>
                <small style={{ color: "var(--text-muted)", fontSize: "0.65rem", display: "block", marginTop: "0.15rem" }}>{item.desc}</small>
              </div>
              {idx < arr.length - 1 && (
                <div style={{ alignSelf: "center", color: "var(--border-glass-active)", fontWeight: "bold" }}>➔</div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* 7. REAL-TIME VS HISTORICAL INTELLIGENCE */}
      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
        <div className="glass-panel" style={{ padding: "2rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--severity-high)", textTransform: "uppercase" }}>Operational Scope</span>
          <h4 style={{ color: "#fff", fontSize: "1.1rem", margin: "0.25rem 0 0.75rem" }}>REAL-TIME SITE TELEMETRY</h4>
          <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <li>● Instant safety helmet & high-visibility vest compliance checks.</li>
            <li>● Restricted controlled zones perimeter gate breaches warning.</li>
            <li>● Worker-heavy equipment safety separation bubble proximity logs.</li>
            <li>● Real-time dispatching to Telegram/WhatsApp alert streams.</li>
          </ul>
        </div>
        
        <div className="glass-panel" style={{ padding: "2rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>Strategic Scope</span>
          <h4 style={{ color: "#fff", fontSize: "1.1rem", margin: "0.25rem 0 0.75rem" }}>HISTORICAL PATTERN INTELLIGENCE</h4>
          <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <li>● Logging historical incident files inside relational databases.</li>
            <li>● Mapping recurring safety "hot hotspots" across site grids.</li>
            <li>● Calculating audit closure response time metrics per foreman.</li>
            <li>● Exporting OSHA-compliant PDF safety summaries for stakeholders.</li>
          </ul>
        </div>
      </section>

      {/* 8. EVIDENCE-FIRST PHILOSOPHY */}
      <section className="glass-panel" style={{ padding: "2.5rem", display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "2.5rem", alignItems: "center" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>Evidence First</span>
          <h3 style={{ fontSize: "1.5rem", color: "#fff", lineHeight: 1.2 }}>
            AN ALERT IS ONLY USEFUL<br />IF YOU CAN ACT ON IT.
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.5" }}>
            Every safety event should be traceable to the visual evidence that triggered it. WorkerShield couples every incident record to its target timestamp, camera ID, zone configurations, classification model version, and raw frame snapshot.
          </p>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", fontSize: "0.75rem", color: "var(--text-muted)" }}>
            <span>DETECTION</span> ➔ <span>EVIDENCE CLIP</span> ➔ <span>ZONE CONTEXT</span> ➔ <span>DECISION</span> ➔ <span>ACTION</span>
          </div>
        </div>

        {/* Mock Evidence incident card */}
        <div className="glass-panel" style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.75rem", background: "#05070a" }}>
          <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.5rem" }}>
            <span style={{ fontWeight: "700", color: "#fff", fontSize: "0.85rem" }}>INCIDENT #WS-10482</span>
            <span className="badge-pill high" style={{ fontSize: "0.65rem" }}>NEW</span>
          </div>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <p>PPE BREACH: <strong>No Helmet Detected</strong></p>
            <p>LOCATION: <strong>CAM-07 • Zone B</strong></p>
            <p>TIMESTAMP: <strong>14:32:18</strong></p>
            <p>CONFIDENCE INDEX: <strong>96.4%</strong></p>
            <p>MODEL VERSION: <strong>Vision Model v2.4</strong></p>
          </div>
        </div>
      </section>

      {/* 9. HUMAN-IN-THE-LOOP SPLIT VISUAL */}
      <section style={{ display: "grid", gridTemplateColumns: "2.5fr 3fr", gap: "2.5rem" }}>
        <div>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>System Boundaries</span>
          <h3 style={{ fontSize: "1.35rem", color: "#fff", margin: "0.25rem 0 1rem" }}>
            AI watches the signals.<br />People make the decisions.
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.5" }}>
            Our tool acts as a support grid for safety teams, scanning video channels continuously so officers can focus their attention on active alerts and resolution steps.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div className="glass-panel" style={{ padding: "1.25rem" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)" }}>AI RESPONSIBILITY</span>
            <ul style={{ paddingLeft: "1.25rem", fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              <li>● Observe streams</li>
              <li>● Detect bounding boxes</li>
              <li>● Prioritize breaches</li>
              <li>● Notify channels</li>
            </ul>
          </div>
          <div className="glass-panel" style={{ padding: "1.25rem" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--success)" }}>HUMAN RESPONSIBILITY</span>
            <ul style={{ paddingLeft: "1.25rem", fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              <li>● Verify evidence</li>
              <li>● Investigate site</li>
              <li>● Respond physically</li>
              <li>● Resolve status</li>
            </ul>
          </div>
        </div>
      </section>

      {/* 10. PRODUCT LIFECYCLE CIRCULAR LOOP */}
      <section className="glass-panel" style={{ padding: "2.5rem", display: "flex", flexDirection: "column", gap: "1.5rem", alignItems: "center", textAlign: "center" }}>
        <h3 style={{ fontSize: "1.25rem", color: "#fff" }}>Continuous Site Safety Loop</h3>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", maxWidth: "600px" }}>
          Every logged incident resolves into Strategic data feedback, helping teams refine hazard requirements and continuously build safer sites.
        </p>

        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center", fontSize: "0.85rem", fontWeight: "700", color: "var(--primary)" }}>
          <span>MONITOR</span> ➔ <span>DETECT</span> ➔ <span>RESPOND</span> ➔ <span>RESOLVE</span> ➔ <span>ANALYZE</span> ➔ <span>IMPROVE</span> ➔ <span>MONITOR</span>
        </div>
      </section>

      {/* 11. WHY THIS ARCHITECTURE MATTERS */}
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem" }}>
        <div className="glass-panel" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Continuous Visibility</h4>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Monitor multiple camera feeds simultaneously without requiring safety officers to sit and manually watch raw screens.
          </p>
        </div>
        <div className="glass-panel" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Actionable Incidents</h4>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Convert raw bounding box detections into prioritized incidents containing timestamps, status tags, and ownership records.
          </p>
        </div>
        <div className="glass-panel" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Measurable Improvement</h4>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Utilize historical database records to locate recurring warning patterns and establish corrective training steps on site.
          </p>
        </div>
      </section>

      {/* 12. FINAL CALL TO ACTION (CTA) */}
      <section style={{ background: "#0b0f19", border: "1px solid var(--border-glass)", borderRadius: "6px", padding: "3rem", display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "2.5rem", alignItems: "center" }}>
        <div>
          <h3 style={{ fontSize: "1.75rem", color: "#fff", marginBottom: "0.5rem" }}>SEE WORKERSHIELD IN ACTION.</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>Move from passive camera feeds to active safety intelligence.</p>
          
          <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
            <button type="button" className="btn-premium" style={{ fontSize: "0.95rem", padding: "0.7rem 1.25rem" }} onClick={onEnterDashboard}>
              Open Live Dashboard →
            </button>
            <button 
              type="button" 
              className="btn-premium" 
              style={{ background: "transparent", border: "1px solid var(--border-glass)", fontSize: "0.95rem", padding: "0.7rem 1.25rem" }}
              onClick={onEnterGuidelines}
            >
              Explore Guidelines →
            </button>
          </div>
        </div>

        {/* System HUD panel */}
        <div className="glass-panel" style={{ padding: "1.25rem", background: "#05070a" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--success)" }}>● SYSTEM OPERATIONAL</span>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginTop: "0.75rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
            <div>
              <p>CAMERAS ACTIVE</p>
              <strong style={{ color: "#fff" }}>24 ONLINE</strong>
            </div>
            <div>
              <p>ACTIVE WORKERS</p>
              <strong style={{ color: "#fff" }}>1,842 MONITORED</strong>
            </div>
            <div>
              <p>UNRESOLVED EVENTS</p>
              <strong style={{ color: "var(--severity-high)" }}>7 ACTIVE</strong>
            </div>
            <div>
              <p>COMPLIANCE INDEX</p>
              <strong style={{ color: "var(--success)" }}>91.4% RATE</strong>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
