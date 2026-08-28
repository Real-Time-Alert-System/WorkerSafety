import React, { useState, useEffect } from "react";
import { Mail, CheckCircle, RefreshCw, Eye, Download } from "lucide-react";
import { guidelinesData } from "../data/guidelines";
import { API_URL } from "../config";

export default function GuidelinesKnowledgeCenter({ token, user, onEnterDashboard }) {
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [selectedGuideline, setSelectedGuideline] = useState(null);
  
  const [checklist, setChecklist] = useState([
    { label: "Required PPE available & verified", checked: true },
    { label: "PPE correctly fitted and worn secure", checked: true },
    { label: "Work area inspected for hazards", checked: false },
    { label: "Access routes clear of debris/materials", checked: true },
    { label: "Fall hazards controlled (guardrails/PFAS)", checked: false },
    { label: "Equipment inspected with warning tags", checked: true },
    { label: "Restricted zones identified & barricaded", checked: false },
    { label: "Emergency route known & exit signs lit", checked: true },
    { label: "Emergency contacts available and posted", checked: false },
    { label: "Environmental weather conditions reviewed", checked: true }
  ]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") setSelectedGuideline(null);
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  const handleToggleCheck = (index) => {
    setChecklist(prev => prev.map((item, idx) => idx === index ? { ...item, checked: !item.checked } : item));
  };

  const completeCount = checklist.filter(c => c.checked).length;
  const readinessPercent = Math.round((completeCount / checklist.length) * 100);

  // Filter & Search Logic
  const filtered = guidelinesData.filter(g => {
    let matchesFilter = true;
    if (activeFilter === "CRITICAL") matchesFilter = (g.severity === "critical");
    else if (activeFilter === "PPE") matchesFilter = (g.category === "ppe");
    else if (activeFilter === "SITE HAZARDS") matchesFilter = (g.category === "site_hazards");
    else if (activeFilter === "HEALTH") matchesFilter = (g.category === "health");
    else if (activeFilter === "EMERGENCY") matchesFilter = (g.category === "emergency");
    else if (activeFilter === "AI MONITORED") matchesFilter = (g.aiCoverage === "monitored");

    let matchesSearch = true;
    if (search.trim() !== "") {
      const q = search.toLowerCase();
      matchesSearch = g.title.toLowerCase().includes(q) ||
                      g.description.toLowerCase().includes(q) ||
                      g.risks.some(r => r.toLowerCase().includes(q)) ||
                      g.prevention.some(p => p.toLowerCase().includes(q)) ||
                      g.recommendedAction.some(a => a.toLowerCase().includes(q)) ||
                      g.aiCoverage.toLowerCase().includes(q);
    }
    return matchesFilter && matchesSearch;
  });

  const isSearchingOrFiltering = search.trim() !== "" || activeFilter !== "ALL";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem", maxWidth: "1100px", margin: "7.5rem auto 4rem", padding: "0 1.5rem" }}>
      
      {/* Editorial Hero Banner */}
      <div style={{ borderBottom: "1px solid var(--border-glass)", paddingBottom: "2rem" }}>
        <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "var(--primary)", letterSpacing: "1px", textTransform: "uppercase" }}>
          WorkerShield Safety Knowledge Center
        </span>
        <h1 style={{ fontSize: "2.5rem", fontWeight: "800", color: "#fff", lineHeight: 1.1, margin: "0.5rem 0 1rem" }}>
          Build safer.<br />Know the risk before you enter the zone.
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", maxWidth: "700px", lineHeight: "1.5" }}>
          Practical construction-safety guidance covering the hazards WorkerShield helps teams identify, monitor, and respond to — from PPE violations to falls, electrical hazards, and restricted zones.
        </p>

        {/* Statistics Widgets */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1.25rem", marginTop: "1.75rem" }}>
          <div className="glass-panel" style={{ padding: "1rem 1.25rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontSize: "1.75rem", fontWeight: "800", color: "var(--primary)" }}>12</span>
            <span style={{ fontSize: "0.75rem", fontWeight: "600", color: "var(--text-muted)", textTransform: "uppercase" }}>Safety Categories</span>
          </div>
          <div className="glass-panel" style={{ padding: "1rem 1.25rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontSize: "1.75rem", fontWeight: "800", color: "var(--severity-high)" }}>FOCUS FOUR</span>
            <span style={{ fontSize: "0.75rem", fontWeight: "600", color: "var(--text-muted)", textTransform: "uppercase" }}>Fully Covered</span>
          </div>
          <div className="glass-panel" style={{ padding: "1rem 1.25rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontSize: "1.75rem", fontWeight: "800", color: "var(--success)" }}>AI-ASSISTED</span>
            <span style={{ fontSize: "0.75rem", fontWeight: "600", color: "var(--text-muted)", textTransform: "uppercase" }}>Proactive Monitoring</span>
          </div>
        </div>
      </div>

      {/* Real-time Search and Filter HUD */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input 
          type="text" 
          className="form-control-input"
          style={{ width: "100%", padding: "0.9rem 1.25rem", fontSize: "1.05rem" }}
          placeholder="🔍 Search safety guidelines (e.g. helmet, fall, excavation, forklift, silica)..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />

        {/* Filter Chips Bar */}
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", overflowX: "auto", paddingBottom: "0.25rem" }}>
          {["ALL", "CRITICAL", "PPE", "SITE HAZARDS", "HEALTH", "EMERGENCY", "AI MONITORED"].map(f => (
            <button
              key={f}
              type="button"
              className="btn-premium"
              style={{
                background: activeFilter === f ? "var(--primary)" : "transparent",
                color: activeFilter === f ? "#080c14" : "var(--text-muted)",
                border: "1px solid " + (activeFilter === f ? "var(--primary)" : "var(--border-glass)"),
                padding: "0.4rem 0.85rem",
                fontSize: "0.75rem",
                fontWeight: "700"
              }}
              onClick={() => setActiveFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Guidelines Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
        
        {/* Conditional Search Headers */}
        {isSearchingOrFiltering && (
          <div>
            <h4 style={{ color: "#fff", fontSize: "1.1rem" }}>
              Search results matching filters ({filtered.length} found)
            </h4>
          </div>
        )}

        {/* SECTION 1: FOCUS FOUR INDEX */}
        {(!isSearchingOrFiltering || filtered.some(g => g.category === "focus_four")) && (
          <div>
            <h3 style={{ fontSize: "1.25rem", color: "#fff", borderLeft: "3px solid var(--severity-high)", paddingLeft: "0.5rem", marginBottom: "0.25rem" }}>
              OSHA FOCUS FOUR REGULATORY COMPLIANCE
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
              Surfacing continuous telemetry markers for construction's top fatal accident sectors.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
              {filtered.filter(g => g.category === "focus_four").map(g => (
                <div 
                  key={g.id} 
                  className="glass-panel" 
                  style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }}
                  onClick={() => setSelectedGuideline(g)}
                >
                  <span className="badge-pill high" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>CRITICAL</span>
                  <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>{g.title}</h4>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>{g.description}</p>
                  <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "0.5rem", display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    <span>AI telemetry:</span>
                    <strong style={{ color: g.aiCoverage === "monitored" ? "var(--success)" : "var(--primary)" }}>
                      {g.aiCoverage.toUpperCase()}
                    </strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 2: PERSONAL PROTECTIVE WEAR */}
        {(!isSearchingOrFiltering || filtered.some(g => g.category === "ppe")) && (
          <div>
            <h3 style={{ fontSize: "1.25rem", color: "#fff", borderLeft: "3px solid var(--success)", paddingLeft: "0.5rem", marginBottom: "0.25rem" }}>
              PERSONAL PROTECTIVE EQUIPMENT (PPE)
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
              Real-time computer vision verification of worker safety configurations.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
              {filtered.filter(g => g.category === "ppe").map(g => (
                <div 
                  key={g.id} 
                  className="glass-panel" 
                  style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }}
                  onClick={() => setSelectedGuideline(g)}
                >
                  <span className="badge-pill resolved" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>COMPLIANCE</span>
                  <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>{g.title}</h4>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>{g.description}</p>
                  <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "0.5rem", display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    <span>AI check:</span>
                    <strong style={{ color: g.aiCoverage === "monitored" ? "var(--success)" : "var(--primary)" }}>
                      {g.aiCoverage.toUpperCase()}
                    </strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 3: ACCESS & SITE HAZARDS */}
        {(!isSearchingOrFiltering || filtered.some(g => g.category === "site_hazards")) && (
          <div>
            <h3 style={{ fontSize: "1.25rem", color: "#fff", borderLeft: "3px solid var(--primary)", paddingLeft: "0.5rem", marginBottom: "0.25rem" }}>
              SITES HAZARDS & CONTROLLED ZONES
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
              Access structures, boundary enforcement, and heavy machinery interfaces.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
              
              {/* Card A: Scaffolding */}
              <div 
                className="glass-panel" 
                style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }} 
                onClick={() => setSelectedGuideline(guidelinesData.find(x => x.id === "ladders_scaffolds"))}
              >
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>HIGH HAZARD</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Ladders & Scaffolding</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>Setup, inspections, base plates footing, and guardrails capacity audits.</p>
                <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "0.5rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  <strong>LADDER SAFETY / SCAFFOLD SAFETY</strong>
                </div>
              </div>

              {/* Card B: Restricted Zone (Visual HUD mockup card) */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", borderLeft: "3px solid var(--severity-high)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span className="badge-pill high" style={{ fontSize: "0.65rem" }}>CRITICAL</span>
                  <span style={{ fontSize: "0.7rem", color: "var(--success)", fontWeight: "700" }}>AI MONITORED</span>
                </div>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Controlled Zones Check</h4>
                
                {/* Visual HUD Mockup */}
                <div style={{ background: "#05070a", border: "1px solid var(--severity-high)", padding: "0.5rem", borderRadius: "4px", position: "relative", minHeight: "90px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
                  <span style={{ fontSize: "0.65rem", position: "absolute", top: "0.25rem", left: "0.5rem", color: "var(--text-muted)" }}>ZONE B MONITOR</span>
                  <div style={{ textAlign: "center" }}>
                    <p style={{ color: "var(--severity-high)", fontWeight: "700", fontSize: "0.8rem" }}>🔴 UNAUTHORIZED ENTRY</p>
                    <p style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Worker detected inside swing path</p>
                  </div>
                </div>
                
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Safety teams can configure restricted areas and trigger sirens for unauthorized breaches.</p>
              </div>

              {/* Card C: Equipment Safety */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }} onClick={() => setSelectedGuideline(guidelinesData.find(x => x.id === "equipment_safety"))}>
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>HIGH HAZARD</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Equipment & Pedestrian Safety</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>Maintain bubble separation rules between workers and reversing machinery.</p>
                <div style={{ background: "rgba(0,0,0,0.15)", padding: "0.35rem", borderRadius: "4px", fontSize: "0.7rem", textAlign: "center" }}>
                  <strong>WORKER ↔ SAFE SEPARATION ↔ VEHICLE</strong>
                </div>
              </div>

              {/* Card D: Excavation safety */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }} onClick={() => setSelectedGuideline(guidelinesData.find(x => x.id === "excavation_trenching"))}>
                <span className="badge-pill high" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>CRITICAL</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Excavation & Trenching</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>cave-in protection via sloping, shoring, shielding and spoils placements.</p>
                <span style={{ fontSize: "0.7rem", color: "var(--severity-medium)" }}>⚠️ AI CANNOT INSPECT SHORING INTEGRITY</span>
              </div>

            </div>
          </div>
        )}

        {/* SECTION 4: OCCUPATIONAL HEALTH */}
        {(!isSearchingOrFiltering || filtered.some(g => g.category === "health")) && (
          <div>
            <h3 style={{ fontSize: "1.25rem", color: "#fff", borderLeft: "3px solid var(--primary)", paddingLeft: "0.5rem", marginBottom: "0.25rem" }}>
              HAZARDS YOU CAN'T ALWAYS SEE
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
              Not every safety risk can be solved with a camera.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
              
              {/* Silica Dust */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>HEALTH</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Silica & Dust</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>Grinding concrete particles require water-suppression HEPA shrouds.</p>
                <div style={{ background: "rgba(220,38,38,0.08)", border: "1px solid var(--severity-high)", padding: "0.4rem", borderRadius: "4px", fontSize: "0.7rem", textAlign: "center" }}>
                  <span>CAMERA ≠ EXPOSURE METER</span>
                </div>
              </div>

              {/* Respirators */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }} onClick={() => setSelectedGuideline(guidelinesData.find(x => x.id === "respiratory_protection"))}>
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>HEALTH</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Respiratory Protection</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>Qualitative fit tests, cartridge swap checks, organic vapors filters.</p>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>STATUS: HUMAN CONTROL</span>
              </div>

              {/* Heat warning Alert box */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", borderLeft: "3px solid var(--severity-medium)" }}>
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>ENVIRONMENT</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Heat Alert HUD</h4>
                
                {/* Warning HUD Mock */}
                <div style={{ background: "rgba(217,119,6,0.06)", border: "1px solid var(--severity-medium)", padding: "0.5rem", borderRadius: "4px", fontSize: "0.75rem" }}>
                  <p style={{ fontWeight: "700", color: "var(--severity-medium)" }}>ENVIRONMENTAL RISK WARNING</p>
                  <p style={{ color: "var(--text-muted)", marginTop: "0.15rem" }}>Heat index elevated. Recommended break frequency: 15min/hr. Rest & Hydrate.</p>
                </div>
              </div>

              {/* Noise */}
              <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem", cursor: "pointer" }} onClick={() => setSelectedGuideline(guidelinesData.find(x => x.id === "noise_exposure"))}>
                <span className="badge-pill medium" style={{ alignSelf: "flex-start", fontSize: "0.65rem" }}>HEALTH</span>
                <h4 style={{ color: "#fff", fontSize: "1.05rem" }}>Noise Exposure</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", flexGrow: 1 }}>Hearing protection fit, noise reduction limits, sound damping generators.</p>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>AUDITS: HUMAN / SENSOR</span>
              </div>

            </div>
          </div>
        )}

        {/* SECTION 5: EMERGENCY & RESPONSE */}
        {(!isSearchingOrFiltering || filtered.some(g => g.category === "emergency")) && (
          <div style={{ background: "#0b0f19", border: "1px solid var(--border-glass)", borderRadius: "6px", padding: "2.25rem" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--severity-high)", textTransform: "uppercase" }}>Critical Preparedness</span>
            <h3 style={{ fontSize: "1.25rem", color: "#fff", margin: "0.25rem 0 1rem" }}>
              WHEN SOMETHING GOES WRONG, EVERYONE NEEDS TO KNOW WHAT HAPPENS NEXT.
            </h3>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <h5 style={{ color: "#fff", fontSize: "0.95rem" }}>Fire Safety</h5>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Monthly extinguisher tags checks, fire watch, flammable cabinets.</p>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <h5 style={{ color: "#fff", fontSize: "0.95rem" }}>Action Plan</h5>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Evacuation layouts, muster gates, emergency response sirens.</p>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <h5 style={{ color: "#fff", fontSize: "0.95rem" }}>Evacuation Route</h5>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Clear lanes to assemble zones.</p>
                <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "600" }}>WORK AREA ➔ EXIT ➔ MUSTER ASSEMBLY</span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <h5 style={{ color: "#fff", fontSize: "0.95rem" }}>First Response</h5>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Buddy incident warnings, first aid checks, site doctor routing.</p>
              </div>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", borderTop: "1px solid var(--border-glass)", paddingTop: "1rem", marginTop: "1rem" }}>
              * WorkerShield can trigger alerts and archive video files, but emergency response plans remain under qualified site rescue squads.
            </p>
          </div>
        )}

        {/* SECTION 6: WORKERSHIELD AI COVERAGE MATRIX */}
        <div className="glass-panel" style={{ padding: "2rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>Coverage Matrix</span>
          <h3 style={{ fontSize: "1.25rem", color: "#fff", margin: "0.25rem 0 1rem" }}>WHAT WORKERSHIELD CAN SEE</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            WorkerShield is designed to augment safety teams — not replace them. Different hazards require different levels of computer-vision support.
          </p>

          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Site Hazard / PPE Class</th>
                  <th>WorkerShield AI Coverage</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: "600" }}>Helmet compliance (Hardhats)</td>
                  <td><span className="badge-pill resolved">🟢 AI MONITORED</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>High-visibility vest compliance</td>
                  <td><span className="badge-pill resolved">🟢 AI MONITORED</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Restricted-zone perimeter breach</td>
                  <td><span className="badge-pill resolved">🟢 AI MONITORED</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Worker-heavy equipment proximity bubble</td>
                  <td><span className="badge-pill resolved">🟢 AI MONITORED</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Worker operating inside swing paths</td>
                  <td><span className="badge-pill resolved">🟢 AI MONITORED</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Fall-risk area proximity entry</td>
                  <td><span className="badge-pill medium">🟡 PARTIAL COVERAGE</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Excavation cave-in protection check</td>
                  <td><span className="badge-pill medium">🟡 PARTIAL COVERAGE</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Fumes / Silica dust exposure measurement</td>
                  <td><span className="badge-pill low" style={{ background: "rgba(255,255,255,0.05)", color: "var(--text-muted)", border: "1px solid var(--border-glass)" }}>⚪ HUMAN / SENSOR</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Emergency route drill audits</td>
                  <td><span className="badge-pill low" style={{ background: "rgba(255,255,255,0.05)", color: "var(--text-muted)", border: "1px solid var(--border-glass)" }}>⚪ HUMAN CONTROL</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* SECTION 7: INTERACTIVE CHECKLIST */}
        <div className="glass-panel" style={{ padding: "2rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>Audit Checklist</span>
          <h3 style={{ fontSize: "1.25rem", color: "#fff", margin: "0.25rem 0 1rem" }}>BEFORE YOU START WORK</h3>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              {checklist.map((item, idx) => (
                <label key={idx} style={{ display: "flex", gap: "0.6rem", alignItems: "center", fontSize: "0.9rem", color: "var(--text-main)", cursor: "pointer" }}>
                  <input type="checkbox" checked={item.checked} onChange={() => handleToggleCheck(idx)} />
                  <span style={{ textDecoration: item.checked ? "line-through" : "none", color: item.checked ? "var(--text-muted)" : "var(--text-main)" }}>
                    {item.label}
                  </span>
                </label>
              ))}
            </div>

            <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", background: "rgba(0,0,0,0.15)", padding: "2rem", borderRadius: "4px" }}>
              <span style={{ fontSize: "2.5rem", fontWeight: "800", color: "var(--primary)" }}>{completeCount} / {checklist.length}</span>
              <span style={{ fontSize: "0.8rem", fontWeight: "600", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginTop: "0.25rem" }}>
                Items Verified
              </span>
              
              {/* Progress bar */}
              <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.05)", borderRadius: "4px", overflow: "hidden", marginTop: "1rem" }}>
                <div style={{ width: `${readinessPercent}%`, height: "100%", background: readinessPercent > 70 ? "var(--success)" : "var(--primary)", transition: "width 0.3s ease" }}></div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: "700", marginTop: "0.5rem", color: "#fff" }}>
                SAFETY READINESS: {readinessPercent}%
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 8: OFFICIAL RESOURCES */}
        <div>
          <h3 style={{ fontSize: "1.1rem", color: "#fff", marginBottom: "0.25rem" }}>OFFICIAL SAFETY RESOURCES</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Guidance should always be interpreted according to applicable regulations, site conditions, task requirements, and qualified safety personnel.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            {[
              { title: "OSHA Construction safety", url: "https://www.osha.gov/construction" },
              { title: "OSHA Personal Protective Wear", url: "https://www.osha.gov/personal-protective-equipment" },
              { title: "OSHA Fall Protection limits", url: "https://www.osha.gov/fall-protection" },
              { title: "OSHA Silica Exposures guidelines", url: "https://www.osha.gov/silica-crystalline" },
              { title: "OSHA Electrical Safety rules", url: "https://www.osha.gov/electrical" }
            ].map((res, i) => (
              <a 
                key={i} 
                href={res.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="glass-panel"
                style={{ padding: "1rem", display: "flex", flexDirection: "column", gap: "0.25rem", textDecoration: "none" }}
              >
                <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--primary)" }}>OSHA STANDARD</span>
                <p style={{ fontSize: "0.85rem", fontWeight: "600", color: "#fff" }}>{res.title}</p>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Open Resource ➔</span>
              </a>
            ))}
          </div>
        </div>

        {/* SECTION 9: SAFETY DISCLAIMER */}
        <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "1.5rem", marginTop: "1rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-muted)", display: "block", marginBottom: "0.25rem" }}>
            WORKERSHIELD SAFETY NOTICE
          </span>
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", lineHeight: "1.5" }}>
            WorkerShield provides AI-assisted monitoring and safety information intended to support construction safety teams. It does not replace qualified safety professionals, site-specific hazard assessments, worker training, engineering controls, inspections, emergency plans, or applicable laws and regulations. Always follow the requirements applicable to your jurisdiction, employer, task, and worksite.
          </p>
        </div>
      </div>

      {/* ---------------- DETAILS DRAWER PANEL ---------------- */}
      {selectedGuideline && (
        <div 
          className="image-modal-overlay" 
          style={{ justifyContent: "flex-end", padding: 0 }}
          onClick={() => setSelectedGuideline(null)}
        >
          <div 
            className="glass-panel" 
            style={{ width: "100%", maxWidth: "520px", height: "100vh", borderTopRightRadius: 0, borderBottomRightRadius: 0, padding: "2rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "1rem" }}>
              <div>
                <span className="badge-pill high" style={{ fontSize: "0.65rem", display: "inline-block", marginBottom: "0.25rem" }}>
                  {selectedGuideline.severity.toUpperCase()} HAZARD
                </span>
                <h3 style={{ fontSize: "1.25rem", color: "#fff" }}>{selectedGuideline.title}</h3>
              </div>
              <button 
                type="button"
                className="btn-premium" 
                style={{ background: "transparent", border: "1px solid var(--border-glass)", padding: "0.4rem 0.8rem" }}
                onClick={() => setSelectedGuideline(null)}
              >
                Close
              </button>
            </div>

            <div>
              <h5 style={{ color: "var(--primary)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.25rem" }}>Why It Matters</h5>
              <p style={{ fontSize: "0.9rem", color: "var(--text-main)", lineHeight: "1.5" }}>{selectedGuideline.description}</p>
            </div>

            <div>
              <h5 style={{ color: "var(--severity-high)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.4rem" }}>Common Risks</h5>
              <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {selectedGuideline.risks.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>

            <div>
              <h5 style={{ color: "var(--success)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.4rem" }}>Prevention & Controls</h5>
              <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {selectedGuideline.prevention.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>

            <div>
              <h5 style={{ color: "var(--primary)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.4rem" }}>WorkerShield AI Telemetry</h5>
              <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.75rem", borderRadius: "4px", borderLeft: "3px solid var(--primary)" }}>
                <span style={{ fontSize: "0.8rem", fontWeight: "700" }}>
                  Coverage: {selectedGuideline.aiCoverage === "monitored" ? "🟢 AI MONITORED" : selectedGuideline.aiCoverage === "partial" ? "🟡 PARTIAL AI COVERAGE" : "⚪ HUMAN CONTROL"}
                </span>
                <ul style={{ paddingLeft: "1.25rem", fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.35rem", display: "flex", flexDirection: "column", gap: "0.15rem" }}>
                  {selectedGuideline.aiDetections?.map((d, i) => <li key={i}>{d}</li>)}
                  {(!selectedGuideline.aiDetections || selectedGuideline.aiDetections.length === 0) && (
                    <li>No direct computer vision automation. Relies on human checks.</li>
                  )}
                </ul>
              </div>
            </div>

            <div>
              <h5 style={{ color: "var(--primary)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.4rem" }}>Recommended Action</h5>
              <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {selectedGuideline.recommendedAction.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </div>

            <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "1rem", marginTop: "auto" }}>
              <h5 style={{ color: "#fff", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.4rem" }}>Official OSHA Standard</h5>
              {selectedGuideline.resources.map((res, i) => (
                <a 
                  key={i} 
                  href={res.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={{ color: "var(--primary)", fontSize: "0.85rem", textDecoration: "none", fontWeight: "600" }}
                >
                  {res.title} ➔
                </a>
              ))}
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
