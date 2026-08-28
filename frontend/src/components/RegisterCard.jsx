import React, { useState } from "react";
import axios from "axios";
import { User, Mail, Lock } from "lucide-react";
import { API_URL } from "../config";

export default function RegisterCard({ switchMode, cancel }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("worker");
  const [avatar, setAvatar] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API_URL}/api/auth/register`, { username, email, password, role, avatar });
      setSuccess(true);
      setTimeout(switchMode, 2000);
    } catch (err) {
      setError(err.response?.data?.error || "Supervisor registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {success && (
        <div style={{ background: "rgba(22,163,74,0.1)", border: "1px solid var(--success)", color: "var(--success)", padding: "0.6rem", borderRadius: "4px", fontSize: "0.8rem", marginBottom: "1rem", textAlign: "center" }}>
          Registered! Loading login view...
        </div>
      )}

      {error && (
        <div style={{ background: "rgba(220,38,38,0.1)", border: "1px solid var(--severity-high)", color: "var(--severity-high)", padding: "0.6rem", borderRadius: "4px", fontSize: "0.8rem", marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      <div className="form-input-group">
        <label className="form-label">Username</label>
        <div style={{ position: "relative" }}>
          <User size={16} style={{ position: "absolute", left: "0.85rem", top: "0.85rem", color: "var(--text-muted)" }} />
          <input 
            type="text" 
            className="form-control-input" 
            style={{ width: "100%", paddingLeft: "2.5rem" }} 
            placeholder="Username" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            required 
          />
        </div>
      </div>

      <div className="form-input-group">
        <label className="form-label">Email Address</label>
        <div style={{ position: "relative" }}>
          <Mail size={16} style={{ position: "absolute", left: "0.85rem", top: "0.85rem", color: "var(--text-muted)" }} />
          <input 
            type="email" 
            className="form-control-input" 
            style={{ width: "100%", paddingLeft: "2.5rem" }} 
            placeholder="supervisor@gmail.com" 
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
            minLength={8}
            required 
          />
        </div>
      </div>

      <div className="form-input-group">
        <label className="form-label">Authorized Role</label>
        <div style={{ position: "relative" }}>
          <select 
            className="form-control-select" 
            style={{ width: "100%", height: "42px", background: "rgba(0,0,0,0.25)" }} 
            value={role} 
            onChange={e => setRole(e.target.value)}
          >
            <option value="supervisor">Supervisor</option>
            <option value="manager">Manager</option>
            <option value="worker">Worker</option>
          </select>
        </div>
      </div>

      <div className="form-input-group">
        <label className="form-label">Profile Image / Safety Avatar (Optional)</label>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginTop: "0.5rem" }}>
          <input 
            type="file" 
            accept="image/*" 
            style={{ display: "none" }} 
            id="register-avatar-upload"
            onChange={e => {
              const file = e.target.files[0];
              if (file) {
                const reader = new FileReader();
                reader.onloadend = () => setAvatar(reader.result);
                reader.readAsDataURL(file);
              }
            }}
          />
          <button 
            type="button" 
            className="btn-premium" 
            style={{ fontSize: "0.8rem", padding: "0.5rem 1.25rem", background: "transparent", border: "1px solid var(--border-glass)" }}
            onClick={() => document.getElementById("register-avatar-upload").click()}
          >
            Upload Photo
          </button>
          
          <div style={{ display: "flex", gap: "0.4rem", marginLeft: "auto" }}>
            {["👷", "🛡️", "🤖", "📈"].map(icon => (
              <button 
                key={icon}
                type="button"
                style={{
                  fontSize: "1.2rem",
                  width: "36px",
                  height: "36px",
                  borderRadius: "50%",
                  border: avatar === icon ? "2px solid var(--primary)" : "1px solid var(--border-glass)",
                  background: avatar === icon ? "rgba(14,165,233,0.15)" : "transparent",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s"
                }}
                onClick={() => setAvatar(icon)}
              >
                {icon}
              </button>
            ))}
          </div>
        </div>

        {avatar && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.75rem", padding: "0.4rem", background: "rgba(255,255,255,0.03)", borderRadius: "4px" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Selected Preview:</span>
            {avatar.startsWith("data:image") ? (
              <img 
                src={avatar} 
                alt="Preview" 
                style={{ width: "32px", height: "32px", borderRadius: "50%", objectFit: "cover", border: "1px solid var(--primary)" }} 
              />
            ) : (
              <span style={{ fontSize: "1.4rem" }}>{avatar}</span>
            )}
            <button 
              type="button" 
              style={{ marginLeft: "auto", background: "none", border: "none", color: "#ef4444", fontSize: "0.75rem", cursor: "pointer" }}
              onClick={() => setAvatar("")}
            >
              Clear
            </button>
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
        <button type="button" className="btn-premium" style={{ background: "transparent", border: "1px solid var(--border-glass)", flexGrow: 1 }} onClick={cancel}>
          Cancel
        </button>
        <button type="submit" className="btn-premium" style={{ flexGrow: 2 }} disabled={loading || success}>
          {loading ? "Registering..." : "Submit"}
        </button>
      </div>

      <div style={{ marginTop: "1.25rem", textAlign: "center", fontSize: "0.8rem" }}>
        <span style={{ color: "var(--text-muted)" }}>Already registered? </span>
        <button type="button" style={{ background: "none", border: "none", color: "var(--primary)", fontWeight: "600", cursor: "pointer" }} onClick={switchMode}>
          Log In
        </button>
      </div>
    </form>
  );
}
