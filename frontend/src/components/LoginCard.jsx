import React, { useState } from "react";
import axios from "axios";
import { Mail, Lock, RefreshCw } from "lucide-react";
import { API_URL } from "../config";

export default function LoginCard({ setToken, setUser, switchMode, cancel }) {
  const [email, setEmail] = useState(""); // Supports email address
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Google OAuth Simulation state
  const [showGooglePrompt, setShowGooglePrompt] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, { username: email, password });
      setToken(response.data.token);
      setUser(response.data.user);
      cancel(); // Close the modal
    } catch (err) {
      setError(err.response?.data?.error || "Login credentials verification failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSubmit = async (e) => {
    e.preventDefault();
    if (!googleEmail.toLowerCase().endsWith("@gmail.com")) {
      setError("Only @gmail.com addresses are supported for Google Authentication.");
      return;
    }
    setGoogleLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/auth/google-login`, { 
        email: googleEmail, 
        username: googleName || googleEmail.split("@")[0] 
      });
      setToken(response.data.token);
      setUser(response.data.user);
      cancel();
    } catch (err) {
      setError(err.response?.data?.error || "Google authentication failed.");
    } finally {
      setGoogleLoading(false);
      setShowGooglePrompt(false);
    }
  };

  if (showGooglePrompt) {
    return (
      <form onSubmit={handleGoogleSubmit} className="tab-fade-container">
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <svg style={{ width: "32px", height: "32px", marginBottom: "0.5rem" }} viewBox="0 0 24 24">
            <path fill="#EA4335" d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.47 14.97 1 12 1 7.24 1 3.23 3.92 1.64 8.16l3.92 3.04C6.44 7.64 8.98 5.04 12 5.04z"/>
            <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.36H12v4.51h6.46c-.29 1.48-1.14 2.73-2.42 3.57v2.96h3.92c2.29-2.11 3.53-5.21 3.53-8.68z"/>
            <path fill="#FBBC05" d="M5.56 14.8c-.24-.72-.38-1.49-.38-2.3c0-.81.14-1.58.38-2.3L1.64 8.16C.59 10.26 0 12.59 0 15c0 2.41.59 4.74 1.64 6.84l3.92-3.04z"/>
            <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.92-2.96c-1.1.74-2.52 1.18-4.04 1.18-3.02 0-5.56-2.6-6.44-6.16L1.64 15.16C3.23 19.4 7.24 23 12 23z"/>
          </svg>
          <h4 style={{ fontSize: "1.05rem", fontWeight: "700", color: "#fff" }}>Sign in with Google</h4>
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>Use your @gmail.com account to authenticate</p>
        </div>

        {error && (
          <div style={{ background: "rgba(220,38,38,0.1)", border: "1px solid var(--severity-high)", color: "var(--severity-high)", padding: "0.6rem", borderRadius: "4px", fontSize: "0.8rem", marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        <div className="form-input-group">
          <label className="form-label">Google Email Address</label>
          <input 
            type="email" 
            className="form-control-input" 
            placeholder="example@gmail.com" 
            value={googleEmail}
            onChange={e => setGoogleEmail(e.target.value)}
            required 
          />
        </div>

        <div className="form-input-group">
          <label className="form-label">Profile Full Name (Optional)</label>
          <input 
            type="text" 
            className="form-control-input" 
            placeholder="John Doe" 
            value={googleName}
            onChange={e => setGoogleName(e.target.value)}
          />
        </div>

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
          <button type="button" className="btn-premium" style={{ background: "transparent", border: "1px solid var(--border-glass)", flexGrow: 1 }} onClick={() => setShowGooglePrompt(false)}>
            Back
          </button>
          <button type="submit" className="btn-premium" style={{ flexGrow: 2 }} disabled={googleLoading}>
            {googleLoading ? "Connecting..." : "Continue"}
          </button>
        </div>
      </form>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div style={{ background: "rgba(220,38,38,0.1)", border: "1px solid var(--severity-high)", color: "var(--severity-high)", padding: "0.6rem", borderRadius: "4px", fontSize: "0.8rem", marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      <div className="form-input-group">
        <label className="form-label">Username or Email Address</label>
        <div style={{ position: "relative" }}>
          <Mail size={16} style={{ position: "absolute", left: "0.85rem", top: "0.85rem", color: "var(--text-muted)" }} />
          <input 
            type="text" 
            className="form-control-input" 
            style={{ width: "100%", paddingLeft: "2.5rem" }} 
            placeholder="Username or email" 
            value={email} 
            onChange={e => setEmail(e.target.value)} 
            required 
          />
        </div>
      </div>

      <div className="form-input-group">
        <label className="form-label">Password</label>
        <div style={{ position: "relative" }}>
          <Lock size={16} style={{ position: "absolute", left: "0.85rem", top: "0.85rem", color: "var(--text-muted)" }} />
          <input 
            type="password" 
            className="form-control-input" 
            style={{ width: "100%", paddingLeft: "2.5rem" }} 
            placeholder="••••••••" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
          />
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text-muted)", cursor: "pointer" }}>
          <input type="checkbox" checked={rememberMe} onChange={e => setRememberMe(e.target.checked)} /> Remember me
        </label>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
        <button type="button" className="btn-premium" style={{ background: "transparent", border: "1px solid var(--border-glass)", flexGrow: 1 }} onClick={cancel}>
          Cancel
        </button>
        <button type="submit" className="btn-premium" style={{ flexGrow: 2 }} disabled={loading}>
          {loading ? "Checking..." : "Login"}
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "1rem", borderTop: "1px solid var(--border-glass)", paddingTop: "1rem" }}>
        <button 
          type="button" 
          className="btn-premium" 
          style={{ background: "#fff", color: "#1f2937", border: "1px solid #d1d5db", fontWeight: "600" }}
          onClick={() => { setError(null); setShowGooglePrompt(true); }}
        >
          <svg style={{ width: "18px", height: "18px" }} viewBox="0 0 24 24">
            <path fill="#EA4335" d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.47 14.97 1 12 1 7.24 1 3.23 3.92 1.64 8.16l3.92 3.04C6.44 7.64 8.98 5.04 12 5.04z"/>
            <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.36H12v4.51h6.46c-.29 1.48-1.14 2.73-2.42 3.57v2.96h3.92c2.29-2.11 3.53-5.21 3.53-8.68z"/>
            <path fill="#FBBC05" d="M5.56 14.8c-.24-.72-.38-1.49-.38-2.3c0-.81.14-1.58.38-2.3L1.64 8.16C.59 10.26 0 12.59 0 15c0 2.41.59 4.74 1.64 6.84l3.92-3.04z"/>
            <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.92-2.96c-1.1.74-2.52 1.18-4.04 1.18-3.02 0-5.56-2.6-6.44-6.16L1.64 15.16C3.23 19.4 7.24 23 12 23z"/>
          </svg>
          Sign in with Google
        </button>
      </div>

      <div style={{ marginTop: "1.25rem", textAlign: "center", fontSize: "0.8rem" }}>
        <span style={{ color: "var(--text-muted)" }}>Request supervisor portal access? </span>
        <button type="button" style={{ background: "none", border: "none", color: "var(--primary)", fontWeight: "600", cursor: "pointer" }} onClick={switchMode}>
          Sign Up
        </button>
      </div>
    </form>
  );
}
