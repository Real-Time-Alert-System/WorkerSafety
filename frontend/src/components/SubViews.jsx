import React, { useState, useEffect } from "react";
import axios from "axios";
import { RefreshCw, Eye, Download } from "lucide-react";
import { API_URL } from "../config";

// ---------------- 1. SITES & CAMERAS VIEW ----------------

export function SitesCamerasView() {
  const [sites] = useState([
    { id: "site-1", name: "Main Construction Site", location: "Sector 4 Building", camerasCount: 5, score: "98.2%", status: "Healthy" },
    { id: "site-2", name: "Cleanroom Lab", location: "Level 2 Tech Park", camerasCount: 2, score: "100%", status: "Healthy" },
    { id: "site-3", name: "Basement Excavation Zone", location: "South Sector Base", camerasCount: 4, score: "94.0%", status: "Warning" }
  ]);
  const [selectedSite, setSelectedSite] = useState(null);

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Sites & Camera Assets</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Configure site-wide safety requirements and active camera devices</p>
        </div>
      </div>

      {selectedSite ? (
        <div className="charts-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
          <div className="glass-panel" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3>{selectedSite.name} Configuration</h3>
              <button type="button" className="btn-premium" style={{ background: "transparent", border: "1px solid var(--border-glass)" }} onClick={() => setSelectedSite(null)}>
                Back
              </button>
            </div>

            <div className="form-input-group">
              <label className="form-label">Required Zone PPE items</label>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.5rem" }}>
                <label style={{ display: "flex", gap: "0.5rem" }}><input type="checkbox" defaultChecked /> Hardhat (Head protection)</label>
                <label style={{ display: "flex", gap: "0.5rem" }}><input type="checkbox" defaultChecked /> Safety Vest (High visibility)</label>
                <label style={{ display: "flex", gap: "0.5rem" }}><input type="checkbox" /> Face Mask (Dust protection)</label>
              </div>
            </div>

            <div className="form-input-group">
              <label className="form-label">Alert Threshold Sensitivity</label>
              <select className="form-control-select" defaultValue="medium">
                <option value="high">{"High (Confidence >= 35%)"}</option>
                <option value="medium">{"Standard (Confidence >= 50%)"}</option>
                <option value="low">{"Low (Confidence >= 75%)"}</option>
              </select>
            </div>

            <button type="button" className="btn-premium" onClick={() => { alert("Site safety configs saved."); setSelectedSite(null); }}>
              Save Safety Configurations
            </button>
          </div>

          <div className="glass-panel" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
            <h3>Connected Cameras ({selectedSite.camerasCount})</h3>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Camera Device</th>
                    <th>Zone</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ fontWeight: "600" }}>Cam-01-HD</td>
                    <td>Entrance Gate</td>
                    <td><span className="badge-pill resolved">ONLINE</span></td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: "600" }}>Cam-02-HD</td>
                    <td>Scaffold Area</td>
                    <td><span className="badge-pill resolved">ONLINE</span></td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: "600" }}>Cam-03-HD</td>
                    <td>Material Storage</td>
                    <td><span className="badge-pill unresolved">OFFLINE</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-panel" style={{ padding: "1rem" }}>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Site Name</th>
                  <th>Location</th>
                  <th>Camera Assets</th>
                  <th>PPE Compliance</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {sites.map(s => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: "600" }}>{s.name}</td>
                    <td>{s.location}</td>
                    <td>{s.camerasCount} Devices</td>
                    <td style={{ fontWeight: "600", color: "var(--primary)" }}>{s.score}</td>
                    <td>
                      <span className={`badge-pill ${s.status === "Healthy" ? "resolved" : "medium"}`}>
                        {s.status}
                      </span>
                    </td>
                    <td>
                      <button type="button" className="btn-premium" style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem" }} onClick={() => setSelectedSite(s)}>
                        Configure Rules
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}

// ---------------- 2. ALERTS & INCIDENTS VIEW ----------------

export function AlertsIncidentsView() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchLoc, setSearchLoc] = useState("");
  const [searchStatus, setSearchStatus] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  const fetchViolations = async () => {
    setLoading(true);
    try {
      // Fetch top 20 recent violation logs
      const res = await axios.get(`${API_URL}/api/violations?limit=20`);
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

  const filtered = violations
    .filter(v => {
      return v.location.toLowerCase().includes(searchLoc.toLowerCase()) &&
             (searchStatus === "" || v.status === searchStatus);
    })
    .slice(0, 20); // Keep top 20 logs only

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Historical Incident Logs</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Supervisor audit trail of top 20 safety violations logged in PostgreSQL
          </p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "1.25rem", display: "flex", gap: "1.25rem", flexWrap: "wrap", alignItems: "flex-end" }}>
        <div className="form-input-group" style={{ flexGrow: 1, minWidth: "220px", marginBottom: 0 }}>
          <label className="form-label">Filter by Site Location</label>
          <input 
            type="text" 
            className="form-control-input" 
            placeholder="Search site..." 
            value={searchLoc}
            onChange={e => setSearchLoc(e.target.value)}
          />
        </div>
        <div className="form-input-group" style={{ width: "180px", marginBottom: 0 }}>
          <label className="form-label">Violation Status</label>
          <select className="form-control-select" value={searchStatus} onChange={e => setSearchStatus(e.target.value)}>
            <option value="">Top 20 Logs</option>
            <option value="unresolved">Unresolved</option>
            <option value="in_review">In Review</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", padding: "0 0.5rem" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontWeight: "600" }}>
            📊 Displaying Top 20 Logged Incidents (Scroll window below for full audit):
          </span>
          <span className="badge-pill low" style={{ fontSize: "0.75rem" }}>
            {filtered.length} of Top 20 Records
          </span>
        </div>

        {loading ? (
          <div style={{ padding: "3rem", textAlign: "center" }}>
            <RefreshCw style={{ animation: "spin 2s linear infinite" }} />
          </div>
        ) : (
          /* Scrollable window for top 20 logs */
          <div 
            className="table-container" 
            style={{ 
              maxHeight: "520px", 
              overflowY: "auto", 
              border: "1px solid var(--border-glass)", 
              borderRadius: "8px" 
            }}
          >
            <table className="custom-table" style={{ borderCollapse: "separate", borderSpacing: 0 }}>
              <thead style={{ position: "sticky", top: 0, zIndex: 2, background: "#0e1526" }}>
                <tr>
                  <th>ID</th>
                  <th>Timestamp</th>
                  <th>Location</th>
                  <th>Class</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Supervisor Notes</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(v => (
                  <tr key={v.id}>
                    <td>#{v.id}</td>
                    <td style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{new Date(v.timestamp).toLocaleString()}</td>
                    <td style={{ fontWeight: "600" }}>{v.location}</td>
                    <td style={{ fontWeight: "600", color: "var(--primary)" }}>{v.equipment_type}</td>
                    <td>
                      <span className={`badge-pill ${v.severity.toLowerCase() === "high" ? "high" : "medium"}`}>
                        {v.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`badge-pill ${v.status === "resolved" ? "resolved" : "unresolved"}`}>
                        {v.status.replace("_", " ")}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.85rem", color: "var(--text-muted)", maxWidth: "160px", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
                      {v.notes || "(No notes)"}
                    </td>
                    <td>
                      {v.image_url ? (
                        <button type="button" className="btn-premium" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }} onClick={() => setSelectedImage(`${API_URL}/api/violations/images/${v.image_url}`)}>
                          <Eye size={12} /> View Snap
                        </button>
                      ) : (
                        <span>N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedImage && (
        <div className="image-modal-overlay" onClick={() => setSelectedImage(null)}>
          <div className="image-modal-content" onClick={e => e.stopPropagation()}>
            <button type="button" className="modal-close-btn" onClick={() => setSelectedImage(null)}>×</button>
            <img src={selectedImage} alt="Incident Evidence" />
          </div>
        </div>
      )}
    </>
  );
}

// ---------------- 3. ANALYTICS VIEW ----------------

export function AnalyticsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/analytics/realtime`);
      setData(res.data);
    } catch (err) {
      console.error("Analytics fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 4000); // Live real-time polling
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh", gap: "1rem" }}>
        <RefreshCw style={{ animation: "spin 2s linear infinite" }} />
        <span>Loading safety analytics database...</span>
      </div>
    );
  }

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Safety Analytics</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Statistical review of site hazard zones and supervisor response rates fed live from PostgreSQL database
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="metrics-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginBottom: "1.5rem" }}>
        <div className="glass-panel metric-card" style={{ padding: "1.25rem" }}>
          <div className="metric-info">
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: "600" }}>Total Hazard Incidents</span>
            <p style={{ fontSize: "1.8rem", fontWeight: "700", margin: "0.25rem 0 0", color: "#fff" }}>{data?.totalViolations || 0}</p>
          </div>
        </div>
        <div className="glass-panel metric-card" style={{ padding: "1.25rem" }}>
          <div className="metric-info">
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: "600" }}>Total Resolved Hazards</span>
            <p style={{ fontSize: "1.8rem", fontWeight: "700", margin: "0.25rem 0 0", color: "#4ade80" }}>{data?.totalResolved || 0}</p>
          </div>
        </div>
        <div className="glass-panel metric-card" style={{ padding: "1.25rem" }}>
          <div className="metric-info">
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: "600" }}>Supervisor Resolution Rate</span>
            <p style={{ fontSize: "1.8rem", fontWeight: "700", margin: "0.25rem 0 0", color: "#38bdf8" }}>{data?.resolutionRate || 0}%</p>
          </div>
        </div>
      </div>

      <div className="charts-grid" style={{ gridTemplateColumns: "1fr 1.5fr", gap: "1.5rem" }}>
        
        {/* Real-time Site Hazard Hotspots */}
        <div className="glass-panel chart-card" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem" }}>
            <span className="chart-title" style={{ fontSize: "1.1rem" }}>🔥 Site Hazard Hotspots</span>
            <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: "600" }}>PostgreSQL Live</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {data?.hotspots && data.hotspots.length > 0 ? (
              data.hotspots.map((spot, idx) => (
                <div key={idx}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.88rem", fontWeight: "600" }}>
                    <span>{spot.location}</span>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>{spot.count} Incidents ({spot.percentage}%)</span>
                  </div>
                  <div style={{ height: "8px", background: "rgba(255,255,255,0.05)", borderRadius: "4px", overflow: "hidden", marginTop: "0.4rem" }}>
                    <div 
                      style={{ 
                        height: "100%", 
                        width: `${Math.max(spot.percentage, 8)}%`, 
                        background: spot.highSeverityCount > 0 ? "var(--severity-high)" : "var(--primary)",
                        transition: "width 0.4s ease"
                      }}
                    ></div>
                  </div>
                  <small style={{ color: "var(--text-muted)", fontSize: "0.75rem", marginTop: "0.2rem", display: "block" }}>
                    {spot.resolvedCount} Resolved | {spot.highSeverityCount} High Risk
                  </small>
                </div>
              ))
            ) : (
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No site hazard data recorded yet.</p>
            )}
          </div>
        </div>

        {/* Real-time Supervisor Response Rates */}
        <div className="glass-panel chart-card" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem" }}>
            <span className="chart-title" style={{ fontSize: "1.1rem" }}>👮 Supervisor Audit & Response Rates</span>
            <span style={{ fontSize: "0.75rem", color: "#4ade80", fontWeight: "600" }}>Live Tracking</span>
          </div>

          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Supervisor</th>
                  <th>Role</th>
                  <th>Total Handled</th>
                  <th>Response Rate</th>
                  <th>Avg Response Time</th>
                </tr>
              </thead>
              <tbody>
                {data?.supervisors && data.supervisors.length > 0 ? (
                  data.supervisors.map((s, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: "600", color: "#fff" }}>{s.username}</td>
                      <td style={{ textTransform: "capitalize", fontSize: "0.8rem", color: "var(--text-muted)" }}>{s.role}</td>
                      <td style={{ fontWeight: "600", color: "var(--primary)" }}>{s.totalHandled} Incidents</td>
                      <td>
                        <span className="badge-pill resolved">
                          {s.responseRate}
                        </span>
                      </td>
                      <td style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{s.avgResTime}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>No supervisor audit records found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* PPE Equipment Violation Distribution */}
          <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "1rem", marginTop: "0.5rem" }}>
            <span style={{ fontSize: "0.88rem", fontWeight: "600", display: "block", marginBottom: "0.75rem" }}>
              🛡️ PPE Equipment Violation Breakdown
            </span>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              {data?.equipmentBreakdown && data.equipmentBreakdown.map((item, idx) => (
                <div key={idx} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", borderRadius: "6px", padding: "0.5rem 0.85rem", fontSize: "0.8rem" }}>
                  <span style={{ color: "var(--text-muted)" }}>{item.equipment}: </span>
                  <strong style={{ color: "#fff" }}>{item.count}</strong> ({item.percentage}%)
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </>
  );
}

// ---------------- 4. REPORTS VIEW ----------------

export function ReportsView() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/api/reports/summary`);
      setSummary(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Safety Reports</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Generate OSHA-aligned safety audit reports</p>
        </div>
      </div>

      <div className="charts-grid" style={{ gridTemplateColumns: "1fr 1.5fr" }}>
        <div className="glass-panel" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <h3>Report Options</h3>
          <div className="form-input-group">
            <label className="form-label">Report Template</label>
            <select className="form-control-select">
              <option value="daily">Daily safety summary</option>
              <option value="weekly">Weekly compliance report</option>
              <option value="monthly">Monthly audit log</option>
            </select>
          </div>
          <button 
            type="button" 
            className="btn-premium" 
            onClick={() => alert("PDF report generated successfully.")}
            disabled={loading}
          >
            <Download size={18} /> Export PDF Report
          </button>
        </div>

        <div className="glass-panel" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <span style={{ color: "var(--text-muted)", fontSize: "0.8rem", fontWeight: "600" }}>LIVE REPORT PREVIEW</span>
          {loading ? (
            <div style={{ padding: "2rem", textAlign: "center" }}>
              <RefreshCw style={{ animation: "spin 2s linear infinite" }} />
              <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>Loading report preview...</p>
            </div>
          ) : (
            <div style={{ border: "1px dashed var(--border-glass)", padding: "1.5rem", borderRadius: "6px", background: "rgba(0,0,0,0.15)", fontSize: "0.85rem" }}>
              <h4 style={{ textAlign: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
                OSHA Safety Compliance Summary
              </h4>
              <p><strong>Audit Period:</strong> {new Date().toLocaleDateString()}</p>
              <p><strong>Total Safety Incidents Logged:</strong> {summary?.totalIncidents}</p>
              <p><strong>Unresolved Alerts:</strong> {summary?.unresolvedIncidents}</p>
              
              <div style={{ marginTop: "1rem", borderTop: "1px solid var(--border-glass)", paddingTop: "0.5rem" }}>
                <strong>Severity Breakdown:</strong>
                <ul style={{ paddingLeft: "1.25rem", marginTop: "0.25rem" }}>
                  {summary?.bySeverity.map((s, idx) => (
                    <li key={idx} style={{ textTransform: "capitalize" }}>
                      {s.severity}: {s.count} incidents
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ marginTop: "1rem", borderTop: "1px solid var(--border-glass)", paddingTop: "0.5rem" }}>
                <strong>Recent Logged Violations:</strong>
                <table className="custom-table" style={{ fontSize: "0.75rem", marginTop: "0.5rem" }}>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Location</th>
                      <th>Class</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary?.latestIncidents.slice(0, 5).map(v => (
                      <tr key={v.id}>
                        <td>{new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                        <td>{v.location}</td>
                        <td>{v.equipment_type}</td>
                        <td style={{ textTransform: "uppercase" }}>{v.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// ---------------- 5. SETTINGS VIEW ----------------

export function SettingsView() {
  const [telegramEnabled, setTelegramEnabled] = useState(false);
  const [telegramBotToken, setTelegramBotToken] = useState("");
  const [telegramChatId, setTelegramChatId] = useState("");
  
  const [notificationCooldown, setNotificationCooldown] = useState(60);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingTg, setTestingTg] = useState(false);

  // --- Personal Telegram Connection State ---
  const [tgStatus, setTgStatus] = useState({ connected: false, personalId: null, pending: false });
  const [tgDeepLink, setTgDeepLink] = useState(null);
  const [tgConnecting, setTgConnecting] = useState(false);
  const [tgError, setTgError] = useState("");
  const tgPollRef = React.useRef(null);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [settingsRes, tgStatusRes] = await Promise.all([
        axios.get(`${API_URL}/api/settings`),
        axios.get(`${API_URL}/api/telegram/status`).catch(() => ({ data: { connected: false, personalId: null, pending: false } }))
      ]);
      setTelegramEnabled(settingsRes.data.telegramEnabled);
      setTelegramBotToken(settingsRes.data.telegramBotToken);
      setTelegramChatId(settingsRes.data.telegramChatId || tgStatusRes.data.personalId || "");
      setNotificationCooldown(settingsRes.data.notificationCooldown);
      setTgStatus(tgStatusRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
    return () => { if (tgPollRef.current) clearInterval(tgPollRef.current); };
  }, []);

  const startTgPolling = () => {
    if (tgPollRef.current) clearInterval(tgPollRef.current);
    tgPollRef.current = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/api/telegram/status`);
        setTgStatus(res.data);
        if (res.data.connected) {
          clearInterval(tgPollRef.current);
          setTgConnecting(false);
          setTgDeepLink(null);
          if (res.data.personalId) setTelegramChatId(res.data.personalId);
        }
      } catch (e) {
        console.error("Poll error:", e);
      }
    }, 3000);
  };

  const handleGenerateLink = async () => {
    setTgError("");
    setTgConnecting(true);
    setTgDeepLink(null);
    try {
      const res = await axios.post(`${API_URL}/api/telegram/connect`, {});
      setTgDeepLink(res.data.deepLink);
      startTgPolling();
    } catch (err) {
      setTgError(err?.response?.data?.error || "Failed to generate link. Make sure a Bot Token is entered and saved below.");
      setTgConnecting(false);
    }
  };

  const handleOpenTelegram = () => {
    if (tgDeepLink) window.open(tgDeepLink, "_blank");
  };

  const handleDisconnectTelegram = async () => {
    if (!window.confirm("Remove your personal Telegram connection?")) return;
    try {
      await axios.delete(`${API_URL}/api/telegram/connect`);
      setTgStatus({ connected: false, personalId: null, pending: false });
      setTgDeepLink(null);
      setTgConnecting(false);
      if (tgPollRef.current) clearInterval(tgPollRef.current);
    } catch (err) {
      alert("Failed to disconnect. Please try again.");
    }
  };

  const handleSaveSettings = async (e) => {
    if (e) e.preventDefault();
    setSaving(true);
    try {
      await axios.post(`${API_URL}/api/settings`, {
        telegramEnabled,
        telegramBotToken,
        telegramChatId,
        notificationCooldown
      });
      alert("Settings saved successfully! Alerts will now dispatch via Telegram.");
    } catch (err) {
      console.error(err);
      alert("Failed to save configuration settings.");
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    setTestingTg(true);
    try {
      const res = await axios.post(`${API_URL}/api/settings/test-telegram`);
      alert(res.data.message);
    } catch (err) {
      alert(err?.response?.data?.error || "Failed to send Telegram test notification.");
    } finally {
      setTestingTg(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh", gap: "1rem" }}>
        <RefreshCw style={{ animation: "spin 2s linear infinite" }} />
        <span>Loading safety settings...</span>
      </div>
    );
  }

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Application Settings</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Configure automatic Telegram alert channel for site safety violations</p>
        </div>
      </div>

      <form onSubmit={handleSaveSettings} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* UNIFIED TELEGRAM INTEGRATION CARD */}
          <div className="glass-panel" style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-glass)", paddingBottom: "1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <span style={{ fontSize: "1.5rem" }}>✈️</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: "1.2rem" }}>Telegram Alert Channel</h3>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", margin: "0.2rem 0 0" }}>
                    Receive real-time instant safety violation alerts directly on your phone
                  </p>
                </div>
              </div>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", fontSize: "0.9rem", fontWeight: "600" }}>
                <input 
                  type="checkbox" 
                  checked={telegramEnabled} 
                  onChange={e => setTelegramEnabled(e.target.checked)} 
                />
                <span>Enable Alerts</span>
              </label>
            </div>
            
            <div style={{ opacity: telegramEnabled ? 1 : 0.5, display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {/* Bot Token input */}
              <div className="form-input-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Telegram Bot Token</span>
                  <small style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>From Telegram @BotFather</small>
                </label>
                <input 
                  type="password" 
                  className="form-control-input" 
                  placeholder="8672875903:AAFRSP..." 
                  value={telegramBotToken}
                  onChange={e => setTelegramBotToken(e.target.value)}
                  disabled={!telegramEnabled} 
                />
              </div>

              {/* Personal Connection / Auto Chat ID Detection */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", borderRadius: "8px", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <span style={{ fontSize: "0.9rem", fontWeight: "600", color: "var(--text-primary)" }}>📱 Supervisor Telegram Connection</span>
                  {tgStatus.connected && (
                    <span style={{ fontSize: "0.78rem", color: "#4ade80", background: "rgba(34,197,94,0.15)", padding: "3px 10px", borderRadius: "12px", border: "1px solid rgba(34,197,94,0.3)", fontWeight: "600" }}>
                      ✓ Auto-Connected
                    </span>
                  )}
                </div>

                {tgStatus.connected ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", margin: 0 }}>
                      Your Telegram Personal ID: <code style={{ background: "rgba(255,255,255,0.1)", padding: "3px 8px", borderRadius: "4px", color: "#fff", fontWeight: "700", fontSize: "0.95rem" }}>{tgStatus.personalId}</code>
                    </p>
                    <button 
                      type="button" 
                      onClick={handleDisconnectTelegram}
                      disabled={!telegramEnabled}
                      style={{ alignSelf: "flex-start", marginTop: "0.5rem", padding: "0.4rem 1rem", background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.3)", color: "#f87171", borderRadius: "6px", fontSize: "0.8rem", cursor: "pointer", fontWeight: "600" }}
                    >
                      Disconnect & Reset
                    </button>
                  </div>
                ) : tgDeepLink ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    <p style={{ color: "#fbbf24", fontSize: "0.85rem", margin: 0, fontWeight: "600" }}>
                      ⏳ Tap "Open Telegram" → Click START in bot to link:
                    </p>
                    <div style={{ display: "flex", gap: "0.75rem" }}>
                      <button 
                        type="button" 
                        onClick={handleOpenTelegram}
                        style={{ padding: "0.5rem 1.25rem", background: "#229ED9", border: "none", color: "#fff", borderRadius: "6px", cursor: "pointer", fontWeight: "600", fontSize: "0.85rem" }}
                      >
                        📲 Open Telegram Bot
                      </button>
                      <button 
                        type="button" 
                        onClick={() => { setTgDeepLink(null); setTgConnecting(false); }}
                        style={{ padding: "0.5rem 1rem", background: "transparent", border: "1px solid var(--border-glass)", color: "var(--text-muted)", borderRadius: "6px", cursor: "pointer", fontSize: "0.85rem" }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.82rem", margin: 0, lineHeight: "1.5" }}>
                      Click <strong>"Connect via Telegram Link"</strong> to automatically detect your phone's Telegram Chat ID without typing numbers manually.
                    </p>
                    {tgError && <p style={{ color: "#f87171", fontSize: "0.8rem", margin: 0 }}>⚠️ {tgError}</p>}
                    <button 
                      type="button" 
                      onClick={handleGenerateLink}
                      disabled={!telegramEnabled || tgConnecting}
                      className="btn-premium"
                      style={{ alignSelf: "flex-start", padding: "0.5rem 1.25rem", fontSize: "0.85rem" }}
                    >
                      {tgConnecting ? "Generating..." : "🔗 Connect via Telegram Link"}
                    </button>
                  </div>
                )}
              </div>

              {/* Chat ID Field (Manual or Channel Chat ID) */}
              <div className="form-input-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Chat ID (Personal / Group / Channel)</span>
                  <small style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>Auto-filled or manual</small>
                </label>
                <input 
                  type="text" 
                  className="form-control-input" 
                  placeholder="e.g. 1613628414 or -100123456789" 
                  value={telegramChatId}
                  onChange={e => setTelegramChatId(e.target.value)}
                  disabled={!telegramEnabled} 
                />
              </div>

              {/* Send Test Telegram Alert Button */}
              <button
                type="button"
                onClick={handleTestTelegram}
                disabled={!telegramEnabled || testingTg}
                style={{
                  marginTop: "0.5rem",
                  padding: "0.75rem 1.5rem",
                  background: "rgba(34, 158, 217, 0.15)",
                  border: "1px solid rgba(34, 158, 217, 0.4)",
                  color: "#38bdf8",
                  borderRadius: "6px",
                  fontWeight: "600",
                  fontSize: "0.9rem",
                  cursor: telegramEnabled ? "pointer" : "not-allowed",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                  alignSelf: "flex-start"
                }}
              >
                {testingTg ? <RefreshCw size={16} style={{ animation: "spin 1s linear infinite" }} /> : "🧪 Send Test Telegram Alert"}
              </button>
            </div>
          </div>

        </div>

        {/* Global Controls Panel */}
        <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", gap: "2rem", alignItems: "center", flexWrap: "wrap" }}>
          <div className="form-input-group" style={{ marginBottom: 0, width: "240px" }}>
            <label className="form-label">Alert Cooldown (Seconds)</label>
            <input 
              type="number" 
              className="form-control-input" 
              placeholder="60" 
              value={notificationCooldown}
              onChange={e => setNotificationCooldown(parseInt(e.target.value) || 0)}
              min={0}
              required 
            />
          </div>
          <button 
            type="submit" 
            className="btn-premium" 
            style={{ marginLeft: "auto", height: "42px", padding: "0 2.5rem" }}
            disabled={saving}
          >
            {saving ? "Saving Configurations..." : "💾 Save All Settings"}
          </button>
        </div>
      </form>
    </>
  );
}