import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  HardHat, 
  LayoutDashboard, 
  Video, 
  MapPin, 
  AlertTriangle, 
  BarChart2, 
  FileText, 
  Settings, 
  User, 
  LogOut 
} from "lucide-react";

import { API_URL } from "./config";
import LandingPage from "./components/LandingPage";
import DashboardView from "./components/DashboardView";
import LiveMonitoringView from "./components/LiveMonitoringView";
import { 
  SitesCamerasView, 
  AlertsIncidentsView, 
  AnalyticsView, 
  ReportsView, 
  SettingsView 
} from "./components/SubViews";

const loadToken = () => localStorage.getItem("token") || null;
const loadUser = () => JSON.parse(localStorage.getItem("user")) || null;

const canAccessPage = (pageName, user) => {
  if (!user) return false;
  const role = (user.role || (user.isAdmin ? "manager" : "supervisor")).toLowerCase();
  if (role === "manager") return true;
  if (role === "supervisor") {
    return ["dashboard", "live_monitoring", "alerts_incidents", "analytics", "reports", "settings"].includes(pageName);
  }
  if (role === "worker") {
    return ["dashboard"].includes(pageName);
  }
  return false;
};

export default function App() {
  const [token, setToken] = useState(loadToken());
  const [user, setUser] = useState(loadUser());
  const [showLanding, setShowLanding] = useState(true); // Always start on the Landing Page first
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState("login"); // login or register
  
  // Profile settings editor modal states
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [editUsername, setEditUsername] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editAvatar, setEditAvatar] = useState("");

  useEffect(() => {
    if (showProfileModal && user) {
      setEditUsername(user.username || "");
      setEditEmail(user.email || "");
      setEditAvatar(user.avatar || "");
    }
  }, [showProfileModal, user]);
  
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      localStorage.setItem("token", token);
      if (user) {
        localStorage.setItem("user", JSON.stringify(user));
      }
    } else {
      delete axios.defaults.headers.common["Authorization"];
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
  }, [token, user]);


  const handleLogout = () => {
    setToken(null);
    setUser(null);
    setShowLanding(true);
  };

  // Render Landing Page if showLanding is true
  if (showLanding) {
    return (
      <LandingPage 
        token={token}
        user={user}
        authMode={authMode}
        setAuthMode={setAuthMode}
        showAuthModal={showAuthModal}
        setShowAuthModal={setShowAuthModal}
        setToken={setToken}
        setUser={setUser}
        onEnterDashboard={() => {
          if (token) {
            setShowLanding(false);
            setCurrentPage("dashboard");
          } else {
            setAuthMode("register");
            setShowAuthModal(true);
          }
        }}
        handleLogout={handleLogout}
        onOpenProfile={() => setShowProfileModal(true)}
      />
    );
  }

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="logo-container" style={{ cursor: "pointer" }} onClick={() => setShowLanding(true)}>
          <HardHat size={32} className="logo-icon" />
          <span className="logo-text">WorkerShield AI</span>
        </div>
        
        <ul className="nav-list">
          {canAccessPage("dashboard", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "dashboard" ? "active" : ""}`}
                onClick={() => setCurrentPage("dashboard")}
              >
                <LayoutDashboard size={20} />
                Dashboard
              </button>
            </li>
          )}
          {canAccessPage("live_monitoring", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "live_monitoring" ? "active" : ""}`}
                onClick={() => setCurrentPage("live_monitoring")}
              >
                <Video size={20} />
                Live Monitoring
              </button>
            </li>
          )}
          {canAccessPage("sites_cameras", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "sites_cameras" ? "active" : ""}`}
                onClick={() => setCurrentPage("sites_cameras")}
              >
                <MapPin size={20} />
                Sites & Cameras
              </button>
            </li>
          )}
          {canAccessPage("alerts_incidents", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "alerts_incidents" ? "active" : ""}`}
                onClick={() => setCurrentPage("alerts_incidents")}
              >
                <AlertTriangle size={20} />
                Alerts & Incidents
              </button>
            </li>
          )}
          {canAccessPage("analytics", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "analytics" ? "active" : ""}`}
                onClick={() => setCurrentPage("analytics")}
              >
                <BarChart2 size={20} />
                Analytics
              </button>
            </li>
          )}
          {canAccessPage("reports", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "reports" ? "active" : ""}`}
                onClick={() => setCurrentPage("reports")}
              >
                <FileText size={20} />
                Reports
              </button>
            </li>
          )}
          {canAccessPage("settings", user) && (
            <li>
              <button 
                type="button"
                className={`nav-item-btn ${currentPage === "settings" ? "active" : ""}`}
                onClick={() => setCurrentPage("settings")}
              >
                <Settings size={20} />
                Settings
              </button>
            </li>
          )}
        </ul>

        <div className="profile-footer" style={{ marginTop: "auto", borderTop: "1px solid var(--border-glass)", paddingTop: "1rem" }}>
          <div 
            className="profile-details" 
            style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem", cursor: "pointer" }}
            onClick={() => setShowProfileModal(true)}
            title="Click to edit account settings"
          >
            <div className="metric-icon-box" style={{ width: 40, height: 40, overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.3rem" }}>
              {user?.avatar ? (
                user.avatar.startsWith("data:image") ? (
                  <img src={user.avatar} style={{ width: "100%", height: "100%", objectFit: "cover" }} alt="User" />
                ) : (
                  user.avatar
                )
              ) : (
                <User size={18} />
              )}
            </div>
            <div>
              <p style={{ fontSize: "0.9rem", fontWeight: "600" }}>{user?.username}</p>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "capitalize" }}>
                {user?.role || (user?.isAdmin ? "manager" : "supervisor")}
              </p>
            </div>
          </div>
          <button type="button" className="nav-item-btn signout-btn" style={{ color: "#ef4444" }} onClick={handleLogout}>
            <LogOut size={20} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Workspace Router */}
      <main className="main-workspace tab-fade-container" key={currentPage}>
        {currentPage === "dashboard" && canAccessPage("dashboard", user) && <DashboardView />}
        {currentPage === "live_monitoring" && canAccessPage("live_monitoring", user) && <LiveMonitoringView token={token} />}
        {currentPage === "sites_cameras" && canAccessPage("sites_cameras", user) && <SitesCamerasView />}
        {currentPage === "alerts_incidents" && canAccessPage("alerts_incidents", user) && <AlertsIncidentsView />}
        {currentPage === "analytics" && canAccessPage("analytics", user) && <AnalyticsView />}
        {currentPage === "reports" && canAccessPage("reports", user) && <ReportsView />}
        {currentPage === "settings" && canAccessPage("settings", user) && <SettingsView />}
      </main>

      {/* User Profile Settings Modal */}
      {showProfileModal && (
        <div className="image-modal-overlay" onClick={() => setShowProfileModal(false)}>
          <div 
            className="glass-panel tab-fade-container" 
            style={{ width: "100%", maxWidth: "420px", padding: "2.5rem", background: "var(--bg-card)", border: "1px solid var(--border-glass)" }} 
            onClick={e => e.stopPropagation()}
          >
            <div style={{ textAlign: "center", marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#fff" }}>Safety Profile Settings</h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "0.25rem" }}>Manage safety account details and dashboard avatars</p>
            </div>

            <form onSubmit={async (e) => {
              e.preventDefault();
              try {
                const res = await axios.post(`${API_URL}/api/auth/profile`, {
                  username: editUsername,
                  email: editEmail,
                  avatar: editAvatar
                });
                setToken(res.data.token);
                setUser(res.data.user);
                alert("Account profile updated successfully.");
                setShowProfileModal(false);
              } catch (err) {
                console.error(err);
                alert(err.response?.data?.error || "Failed to update profile settings.");
              }
            }} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              
              {/* Profile Photo Upload / Emoji picker */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
                <div 
                  style={{
                    width: "80px",
                    height: "80px",
                    borderRadius: "50%",
                    border: "2px solid var(--primary)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "rgba(255,255,255,0.02)",
                    overflow: "hidden",
                    fontSize: "2.5rem",
                    cursor: "pointer"
                  }}
                  onClick={() => document.getElementById("profile-editor-file-upload").click()}
                  title="Click to upload custom picture"
                >
                  {editAvatar ? (
                    editAvatar.startsWith("data:image") ? (
                      <img src={editAvatar} style={{ width: "100%", height: "100%", objectFit: "cover" }} alt="Avatar" />
                    ) : (
                      editAvatar
                    )
                  ) : (
                    <User size={36} style={{ color: "var(--text-muted)" }} />
                  )}
                </div>
                
                <input 
                  type="file" 
                  accept="image/*" 
                  id="profile-editor-file-upload" 
                  style={{ display: "none" }} 
                  onChange={e => {
                    const file = e.target.files[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onloadend = () => setEditAvatar(reader.result);
                      reader.readAsDataURL(file);
                    }
                  }}
                />

                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Click photo to upload or pick safety badge:</span>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  {["👷", "🛡️", "🤖", "📈"].map(icon => (
                    <button 
                      key={icon}
                      type="button"
                      style={{
                        fontSize: "1.2rem",
                        width: "36px",
                        height: "36px",
                        borderRadius: "50%",
                        border: editAvatar === icon ? "2px solid var(--primary)" : "1px solid var(--border-glass)",
                        background: editAvatar === icon ? "rgba(14,165,233,0.15)" : "transparent",
                        cursor: "pointer"
                      }}
                      onClick={() => setEditAvatar(icon)}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-input-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Username</label>
                <input 
                  type="text" 
                  className="form-control-input" 
                  value={editUsername} 
                  onChange={e => setEditUsername(e.target.value)} 
                  required 
                />
              </div>

              <div className="form-input-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  className="form-control-input" 
                  value={editEmail} 
                  onChange={e => setEditEmail(e.target.value)} 
                  required 
                />
              </div>

              <div className="form-input-group" style={{ marginBottom: 0 }}>
                <label className="form-label">System Security Role</label>
                <input 
                  type="text" 
                  className="form-control-input" 
                  style={{ textTransform: "capitalize", opacity: 0.6 }} 
                  value={user?.role || (user?.isAdmin ? "manager" : "supervisor")} 
                  disabled 
                />
              </div>

              <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
                <button 
                  type="button" 
                  className="btn-premium" 
                  style={{ background: "transparent", border: "1px solid var(--border-glass)", flexGrow: 1 }} 
                  onClick={() => setShowProfileModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-premium" style={{ flexGrow: 2 }}>
                  Save Changes
                </button>
              </div>

            </form>
          </div>
        </div>
      )}
    </div>
  );
}
