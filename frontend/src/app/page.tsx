"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { createClient } from "@/utils/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [role, setRole] = useState<"hospital" | "vendor">("hospital");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organization, setOrganization] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    if (mode === "signup") {
      const supabase = createClient();
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { organization_name: organization, role },
        },
      });

      if (error) {
        setError(error.message);
      } else {
        setSuccess("Registration successful! You can now sign in (or check email if confirmation is required).");
        setMode("signin");
      }
    } else {
      const supabase = createClient();
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        setError(error.message);
      } else {
        // Explicitly route the user based on their role metadata to ensure Next.js handles the redirect
        const userRole = data.user?.user_metadata?.role || "hospital";
        if (userRole === "vendor") {
          window.location.href = "/vendor";
        } else {
          window.location.href = "/dashboard";
        }
      }
    }
    setLoading(false);
  };

  const handleGoogleAuth = async () => {
    // Determine redirect based on environment
    const redirectUrl = typeof window !== 'undefined' 
      ? `${window.location.origin}/auth/callback` 
      : 'http://localhost:3000/auth/callback';
      
    const supabase = createClient();
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: redirectUrl,
      },
    });

    if (error) {
      setError(error.message);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0e1a 0%, #0d1528 50%, #0a1520 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Animated background orbs */}
      <div style={{
        position: "absolute", top: "10%", left: "10%", width: 400, height: 400,
        background: "radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)",
        borderRadius: "50%", animation: "float 6s ease-in-out infinite",
      }} />
      <div style={{
        position: "absolute", bottom: "10%", right: "10%", width: 350, height: 350,
        background: "radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)",
        borderRadius: "50%", animation: "float 8s ease-in-out infinite reverse",
      }} />
      <div style={{
        position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)",
        width: 600, height: 600,
        background: "radial-gradient(circle, rgba(16,185,129,0.04) 0%, transparent 70%)",
        borderRadius: "50%",
      }} />

      <div style={{ position: "relative", zIndex: 10, width: "100%", maxWidth: 420, padding: "0 24px" }}>
        {/* Logo + Brand */}
        <div className="animate-fade-in-up" style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{
            width: 64, height: 64, borderRadius: 18,
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 20px", fontSize: 28,
            boxShadow: "0 8px 32px rgba(59,130,246,0.4)",
          }}>
            🏥
          </div>
          <h1 className="gradient-text" style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 8 }}>
            HRIP
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 15 }}>
            Healthcare Resource Intelligence Platform
          </p>
          <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 6 }}>
            Powered by AI · Built for Public Health
          </p>
        </div>

        {/* Login card */}
        <div className="glass animate-fade-in-up stagger-2" style={{ borderRadius: 20, padding: 32 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 6 }}>
            {mode === "signin" ? "Organization Sign In" : "Register Organization"}
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 28 }}>
            {mode === "signin" ? "Access your health district dashboard" : "Create an account for your organization"}
          </p>

          <form onSubmit={handleAuth}>
            {mode === "signup" && (
              <>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Account Type
                  </label>
                  <select
                    className="hrip-input"
                    value={role}
                    onChange={(e) => setRole(e.target.value as "hospital" | "vendor")}
                    required
                  >
                    <option value="hospital">Hospital / Medical Facility</option>
                    <option value="vendor">Supply Chain Vendor</option>
                  </select>
                </div>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Organization Name
                  </label>
                  <input
                    className="hrip-input"
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    placeholder={role === "hospital" ? "e.g. Kigali Health District" : "e.g. MedSupply Co."}
                    required
                  />
                </div>
              </>
            )}

            <div style={{ marginBottom: 16 }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Email Address
              </label>
              <input
                className="hrip-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@hospital.gov"
                required
              />
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Password
              </label>
              <input
                className="hrip-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "10px 14px", marginBottom: 16, color: "#f87171", fontSize: 13 }}>
                {error}
              </div>
            )}
            
            {success && (
              <div style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.3)", borderRadius: 8, padding: "10px 14px", marginBottom: 16, color: "#34d399", fontSize: 13 }}>
                {success}
              </div>
            )}

            <button
              className="btn-primary"
              type="submit"
              disabled={loading}
              style={{ width: "100%", padding: "12px 20px", fontSize: 15, borderRadius: 12, marginBottom: 16 }}
            >
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                  <span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block", animation: "spin-slow 0.8s linear infinite" }} />
                  {mode === "signin" ? "Authenticating…" : "Registering…"}
                </span>
              ) : mode === "signin" ? "Sign In →" : "Sign Up →"}
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
              <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
              <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>OR</div>
              <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
            </div>

            <button
              type="button"
              onClick={handleGoogleAuth}
              style={{ 
                width: "100%", padding: "12px 20px", fontSize: 15, borderRadius: 12,
                background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
                color: "var(--text-primary)", fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
                cursor: "pointer", transition: "all 0.2s"
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.1)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.05)")}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>
          </form>

          {/* Toggle Mode */}
          <div style={{ marginTop: 20, textAlign: "center", fontSize: 13, color: "var(--text-secondary)" }}>
            {mode === "signin" ? (
              <>
                New organization?{" "}
                <button onClick={() => { setMode("signup"); setError(""); setSuccess(""); }} style={{ background: "none", border: "none", color: "#60a5fa", cursor: "pointer", fontWeight: 600 }}>
                  Register here
                </button>
              </>
            ) : (
              <>
                Already registered?{" "}
                <button onClick={() => { setMode("signin"); setError(""); setSuccess(""); }} style={{ background: "none", border: "none", color: "#60a5fa", cursor: "pointer", fontWeight: 600 }}>
                  Sign in
                </button>
              </>
            )}
          </div>
        </div>

        {/* Feature pills */}
        <div className="animate-fade-in-up stagger-3" style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", marginTop: 24 }}>
          {["🤖 Gemini AI", "🗺️ Live Map", "📊 Forecasting", "🚨 Real-time Alerts"].map((f) => (
            <span key={f} style={{
              background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)",
              borderRadius: 20, padding: "4px 12px", fontSize: 12, color: "var(--text-secondary)",
            }}>{f}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
