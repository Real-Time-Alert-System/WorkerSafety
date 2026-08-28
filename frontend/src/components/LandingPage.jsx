import React, { useState, useEffect } from "react";
import axios from "axios";
import { HardHat } from "lucide-react";
import { API_URL } from "../config";
import CountUp from "./CountUp";
import AboutHowItWorks from "./AboutHowItWorks";
import GuidelinesKnowledgeCenter from "./GuidelinesKnowledgeCenter";
import LoginCard from "./LoginCard";
import RegisterCard from "./RegisterCard";

export default function LandingPage({ 
  token, 
  user, 
  authMode, 
  setAuthMode, 
  showAuthModal, 
  setShowAuthModal, 
  setToken, 
  setUser, 
  onEnterDashboard, 
  handleLogout,
  onOpenProfile
}) {
  const [isSolidNav, setIsSolidNav] = useState(false);
  const [activeTab, setActiveTab] = useState("home");
  const [liveTimestamp, setLiveTimestamp] = useState(new Date().toLocaleTimeString());

  // Handle Navbar styling on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 40) {
        setIsSolidNav(true);
      } else {
        setIsSolidNav(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Live Timestamp clock for CV overlays
  useEffect(() => {
    const timer = setInterval(() => {
      setLiveTimestamp(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const tabs = ["home", "dashboard", "about", "guidelines"];
  const tabWidth = 92; // px allocation for sliding links
  const indicatorLeft = tabs.indexOf(activeTab) * tabWidth + 8;

  const handleTabClick = (tab) => {
    if (tab === "dashboard") {
      onEnterDashboard();
      if (!token) return;
    }
    setActiveTab(tab);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "#080c14" }}>
      
      {/* Sticky Fixed Navbar */}
      <nav className={`sticky-navbar ${isSolidNav ? "solid" : ""}`}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <HardHat size={28} style={{ color: "var(--primary)" }} />
          <span style={{ fontSize: "1.2rem", fontWeight: "700", letterSpacing: "-0.5px" }}>WorkerShield AI</span>
        </div>

        {/* Center Links with smooth sliding border indicator */}
        <div className="nav-links-wrapper">
          {tabs.map((tab) => (
            <button 
              key={tab}
              type="button"
              className={`nav-link-item ${activeTab === tab ? "active" : ""}`}
              onClick={() => handleTabClick(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          <div 
            className="nav-indicator-line"
            style={{ left: `${indicatorLeft}px`, width: "76px" }}
          ></div>
        </div>

        {/* Right Auth controls */}
        <div>
          {token ? (
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <div 
                style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}
                onClick={onOpenProfile}
                title="Click to open user profile"
              >
                {user?.avatar ? (
                  user.avatar.startsWith("data:image") ? (
                    <img 
                      src={user.avatar} 
                      alt="User" 
                      style={{ width: "32px", height: "32px", borderRadius: "50%", objectFit: "cover", border: "1px solid var(--primary)" }}
                    />
                  ) : (
                    <div className="metric-icon-box" style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--primary-glow)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <span style={{ fontSize: "1.1rem" }}>{user.avatar}</span>
                    </div>
                  )
                ) : (
                  <div className="metric-icon-box" style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--primary-glow)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: "700" }}>
                      {user?.username ? user.username[0].toUpperCase() : "U"}
                    </span>
                  </div>
                )}
                <span style={{ fontSize: "0.9rem", fontWeight: "600" }}>{user?.username}</span>
              </div>
              <button 
                type="button"
                className="btn-premium" 
                style={{ background: "transparent", border: "1px solid var(--border-glass)", padding: "0.4rem 0.8rem", color: "#ef4444" }}
                onClick={handleLogout}
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              type="button"
              className="btn-premium" 
              onClick={() => { setAuthMode("login"); setShowAuthModal(true); }}
            >
              Portal Login
            </button>
          )}
        </div>
      </nav>

      {/* ---------------- 1. HOME TAB ---------------- */}
      {activeTab === "home" && (
        <>
          {/* Hero Container with Camera Stream or Stock Video Background */}
          <section id="home" className="hero-video-container tab-fade-container">
            
            <video className="hero-video-player" autoPlay loop muted playsInline>
              <source src="https://assets.mixkit.co/videos/preview/mixkit-workers-on-a-construction-site-40348-large.mp4" type="video/mp4" />
            </video>

            {/* Dark Cinematic Tint Overlay */}
            <div className="hero-video-overlay"></div>

            {/* Hero Content */}
            <div className="hero-content-wrapper">
              <div className="badge-pill low" style={{ background: "rgba(14,165,233,0.1)", color: "var(--primary)", border: "1px solid rgba(14,165,233,0.2)" }}>
                ⚡ LIVE AI SAFETY MONITORING
              </div>
              
              <h1 className="landing-title">See risks before they become incidents.</h1>
              
              <p style={{ color: "var(--text-muted)", fontSize: "1.15rem", maxWidth: "640px", margin: "0 auto 1.5rem" }}>
                Monitor construction sites continuously with computer vision that detects PPE violations, unsafe behavior, and high-risk areas in real time.
              </p>

              <div style={{ display: "flex", gap: "1rem" }}>
                <button type="button" className="btn-premium" style={{ fontSize: "1rem", padding: "0.8rem 1.75rem" }} onClick={onEnterDashboard}>
                  Open Dashboard →
                </button>
                <button 
                  type="button" 
                  className="btn-premium" 
                  style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", fontSize: "1rem", padding: "0.8rem 1.75rem", color: "#fff" }}
                  onClick={() => setActiveTab("about")}
                >
                  Explore WorkerShield AI
                </button>
              </div>

              {/* Operational Status Footer HUD */}
              <div style={{ display: "flex", gap: "1.5rem", marginTop: "2rem", fontSize: "0.8rem", fontWeight: "600", color: "var(--text-muted)", background: "rgba(0,0,0,0.4)", padding: "0.5rem 1rem", borderRadius: "4px" }}>
                <span style={{ color: "var(--success)" }}>● SYSTEM OPERATIONAL</span>
                <span><CountUp end={24} /> CAMERAS</span>
                <span><CountUp end={1842} /> WORKERS MONITORED</span>
              </div>
            </div>
          </section>
        </>
      )}
      {activeTab === "about" && (
        <div className="tab-fade-container">
          <AboutHowItWorks 
            onEnterDashboard={onEnterDashboard}
            onEnterGuidelines={() => setActiveTab("guidelines")}
          />
        </div>
      )}

      {/* ---------------- 3. GUIDELINES TAB ---------------- */}
      {activeTab === "guidelines" && (
        <div className="tab-fade-container">
          <GuidelinesKnowledgeCenter 
            token={token} 
            user={user} 
            onEnterDashboard={onEnterDashboard}
          />
        </div>
      )}

      <footer style={{ textAlign: "center", padding: "1.5rem", borderTop: "1px solid var(--border-glass)", fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "auto" }}>
        © {new Date().getFullYear()} WorkerShield AI Safety Systems. All rights reserved.
      </footer>

      {/* ---------------- AUTHENTICATION MODAL ---------------- */}
      {showAuthModal && (
        <div className="image-modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="glass-panel" style={{ width: "100%", maxWidth: "420px", padding: "2.5rem" }} onClick={e => e.stopPropagation()}>
            <div style={{ textAlign: "center", marginBottom: "2rem" }}>
              <HardHat size={42} style={{ color: "var(--primary)", marginBottom: "0.5rem" }} />
              <h2 style={{ fontSize: "1.5rem", fontWeight: "700" }}>
                {authMode === "login" ? "PPE Monitor Log In" : "Register Supervisor"}
              </h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                {authMode === "login" ? "Enter credentials to access safety controls" : "Create supervisor account"}
              </p>
            </div>

            {authMode === "login" ? (
              <LoginCard 
                setToken={setToken} 
                setUser={setUser} 
                switchMode={() => setAuthMode("register")} 
                cancel={() => setShowAuthModal(false)} 
              />
            ) : (
              <RegisterCard 
                switchMode={() => setAuthMode("login")} 
                cancel={() => setShowAuthModal(false)} 
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
