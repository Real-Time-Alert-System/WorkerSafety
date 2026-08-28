import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import { 
  RefreshCw, 
  Activity, 
  AlertOctagon, 
  AlertTriangle, 
  CheckSquare 
} from "lucide-react";
import { API_URL } from "../config";
import CountUp from "./CountUp";

// Register Chart.js components
Chart.register(...registerables);

export default function DashboardView() {
  const [stats, setStats] = useState(null);
  const [violations, setViolations] = useState([]);
  const [selectedSite, setSelectedSite] = useState("all");
  const [loading, setLoading] = useState(true);

  const eqRef = useRef(null);
  const trendRef = useRef(null);
  const activeCharts = useRef([]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, violationsRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats`),
        axios.get(`${API_URL}/api/violations?limit=100`)
      ]);
      setStats(statsRes.data);
      setViolations(violationsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      loadData();
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!stats) return;

    activeCharts.current.forEach(c => c.destroy());
    activeCharts.current = [];

    const gridColor = "rgba(255, 255, 255, 0.04)";
    const tickColor = "#9ca3af";

    if (eqRef.current) {
      const chart = new Chart(eqRef.current, {
        type: "bar",
        data: {
          labels: stats.by_equipment.map(x => x.equipment_type),
          datasets: [{
            data: stats.by_equipment.map(x => x.count),
            backgroundColor: "rgba(14, 165, 233, 0.75)",
            borderColor: "var(--primary)",
            borderWidth: 1,
            borderRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: tickColor } },
            y: { grid: { color: gridColor }, ticks: { color: tickColor, stepSize: 1 } }
          }
        }
      });
      activeCharts.current.push(chart);
    }

    if (trendRef.current) {
      const chart = new Chart(trendRef.current, {
        type: "line",
        data: {
          labels: stats.daily_trend.map(x => x.day),
          datasets: [{
            data: stats.daily_trend.map(x => x.count),
            borderColor: "var(--primary)",
            backgroundColor: "rgba(14, 165, 233, 0.08)",
            fill: true,
            tension: 0.25,
            pointRadius: 3,
            pointBackgroundColor: "var(--primary)"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: tickColor } },
            y: { grid: { color: gridColor }, ticks: { color: tickColor, stepSize: 1 } }
          }
        }
      });
      activeCharts.current.push(chart);
    }

  }, [stats]);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh", gap: "1rem" }}>
        <RefreshCw style={{ animation: "spin 2s linear infinite" }} />
        <span>Loading safety dashboard...</span>
      </div>
    );
  }

  const unresolved = violations.filter(v => v.status !== "resolved");
  const weeklyIncidents = violations.filter(v => (Date.now() - new Date(v.timestamp)) < 7 * 24 * 60 * 60 * 1000).length;

  return (
    <>
      <div className="workspace-header">
        <div>
          <h1 className="workspace-title">Safety Control Center</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Multi-site compliance and alerts monitor</p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <select 
            className="form-control-select" 
            value={selectedSite} 
            onChange={e => setSelectedSite(e.target.value)}
          >
            <option value="all">All Active Sites</option>
            <option value="main">Main Construction Site</option>
            <option value="excavation">Basement Excavation Zone</option>
            <option value="cleanroom">Cleanroom Lab</option>
          </select>
          <button type="button" className="btn-premium" onClick={loadData}><RefreshCw size={16} /></button>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="glass-panel metric-card">
          <div className="metric-info">
            <h5>PPE Compliance (Today)</h5>
            <p style={{ color: "var(--success)" }}><CountUp end={98} />.2%</p>
          </div>
          <div className="metric-icon-box success">
            <Activity size={24} />
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div className="metric-info">
            <h5>Active Critical Alerts</h5>
            <p style={{ color: unresolved.length > 0 ? "var(--severity-high)" : "var(--text-main)" }}>
              <CountUp end={unresolved.length} />
            </p>
          </div>
          <div className="metric-icon-box danger">
            <AlertOctagon size={24} />
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div className="metric-info">
            <h5>Incidents This Week</h5>
            <p><CountUp end={weeklyIncidents} /></p>
          </div>
          <div className="metric-icon-box warning">
            <AlertTriangle size={24} />
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div className="metric-info">
            <h5>Avg Acknowledge Time</h5>
            <p><CountUp end={1} />.8 Min</p>
          </div>
          <div className="metric-icon-box primary">
            <CheckSquare size={24} />
          </div>
        </div>
      </div>

      <div className="charts-grid" style={{ gridTemplateColumns: "1.8fr 1fr" }}>
        <div className="glass-panel chart-card" style={{ padding: "1.25rem" }}>
          <span className="chart-title">Active Site Health Monitors</span>
          <div className="table-container" style={{ marginTop: "0.75rem" }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Site Name</th>
                  <th>Location</th>
                  <th>Violations</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: "600" }}>Main Construction Site</td>
                  <td>Sector 4 Building</td>
                  <td>{unresolved.filter(v => v.location.toLowerCase().includes("main")).length}</td>
                  <td><span className="badge-pill high">WARNING</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Cleanroom Lab</td>
                  <td>Level 2 Tech Park</td>
                  <td>{unresolved.filter(v => v.location.toLowerCase().includes("lab")).length}</td>
                  <td><span className="badge-pill resolved">HEALTHY</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: "600" }}>Basement Excavation Zone</td>
                  <td>South Sector Base</td>
                  <td>{unresolved.filter(v => v.location.toLowerCase().includes("excavation")).length}</td>
                  <td><span className="badge-pill medium">WARNING</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-panel chart-card" style={{ padding: "1.25rem" }}>
          <span className="chart-title">Safety "Hot Zones"</span>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ fontWeight: "600", fontSize: "0.9rem" }}>Scaffold Zone A</p>
                <small style={{ color: "var(--text-muted)" }}>Main Site</small>
              </div>
              <span className="badge-pill high" style={{ fontSize: "0.7rem" }}>High Risk</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ fontWeight: "600", fontSize: "0.9rem" }}>Loading Dock</p>
                <small style={{ color: "var(--text-muted)" }}>South Site</small>
              </div>
              <span className="badge-pill medium" style={{ fontSize: "0.7rem" }}>Medium Risk</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ fontWeight: "600", fontSize: "0.9rem" }}>Chemical Storage Room</p>
                <small style={{ color: "var(--text-muted)" }}>Level 2 Tech Park</small>
              </div>
              <span className="badge-pill low" style={{ fontSize: "0.7rem" }}>Low Risk</span>
            </div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="glass-panel chart-card">
          <span className="chart-title">Top Violation Types</span>
          <div className="chart-wrapper">
            <canvas ref={eqRef}></canvas>
          </div>
        </div>

        <div className="glass-panel chart-card">
          <span className="chart-title">Violations Per Day (Last 30 Days)</span>
          <div className="chart-wrapper">
            <canvas ref={trendRef}></canvas>
          </div>
        </div>
      </div>
    </>
  );
}
