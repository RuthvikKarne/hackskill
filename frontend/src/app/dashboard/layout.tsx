"use client";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import AskHRIP from "@/components/AskHRIP";

import { LayoutDashboard, Building2, BedDouble, Sparkles, Ambulance, PackageOpen, Stethoscope, FlaskConical, BarChart3, Activity } from "lucide-react";

const NAV_ITEMS = [
  { icon: <LayoutDashboard size={18} />, label: "Overview", href: "/dashboard" },
  { icon: <Building2 size={18} />, label: "Hospitals", href: "/dashboard/hospitals" },
  { icon: <BedDouble size={18} />, label: "Beds & Wards", href: "/dashboard/beds" },
  { icon: <Sparkles size={18} />, label: "AI Recommendations", href: "/dashboard/recommendations" },
  { icon: <Ambulance size={18} />, label: "Emergency", href: "/dashboard/emergency" },
  { icon: <PackageOpen size={18} />, label: "Inventory", href: "/dashboard/inventory" },
  { icon: <Stethoscope size={18} />, label: "Doctors", href: "/dashboard/doctors" },
  { icon: <FlaskConical size={18} />, label: "Laboratory", href: "/dashboard/laboratory" },
  { icon: <BarChart3 size={18} />, label: "Analytics", href: "/dashboard/analytics" },
  { icon: <Activity size={18} />, label: "Surveillance", href: "/dashboard/surveillance" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [chatOpen, setChatOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  const handleSignOut = async () => {
    const { createBrowserClient } = await import("@supabase/ssr");
    const supabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
    await supabase.auth.signOut();
    window.location.href = "/";
  };

  const SIDEBAR_W = sidebarCollapsed ? 68 : 240;

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-primary)" }}>
      {/* ── Sidebar ─────────────────────────────────────── */}
      <aside style={{
        width: SIDEBAR_W,
        minWidth: SIDEBAR_W,
        background: "var(--bg-secondary)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        position: "fixed",
        top: 0, left: 0, bottom: 0,
        zIndex: 50,
        transition: "width 0.25s cubic-bezier(0.4,0,0.2,1)",
        overflow: "hidden",
      }}>
        {/* Brand */}
        <div style={{ padding: "20px 16px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36, minWidth: 36, borderRadius: 10,
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18, boxShadow: "0 4px 12px rgba(59,130,246,0.35)",
          }}>🏥</div>
          {!sidebarCollapsed && (
            <div>
              <div style={{ fontWeight: 800, fontSize: 16, letterSpacing: "-0.02em" }}>HRIP</div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 1 }}>AI Health Platform</div>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "12px 8px", overflowY: "auto" }}>
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <button
                key={item.href}
                onClick={() => router.push(item.href)}
                className={`nav-item ${active ? "active" : ""}`}
                style={{ width: "100%", justifyContent: sidebarCollapsed ? "center" : "flex-start", marginBottom: 2 }}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <span style={{ minWidth: 20, display: "flex", justifyContent: "center" }} aria-hidden="true">{item.icon}</span>
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            );
          })}

          <div style={{ borderTop: "1px solid var(--border)", margin: "12px 4px" }} />

          {/* Ask HRIP button */}
          <button
            onClick={() => setChatOpen(!chatOpen)}
            className="nav-item"
            style={{
              width: "100%", justifyContent: sidebarCollapsed ? "center" : "flex-start",
              background: chatOpen ? "rgba(139,92,246,0.12)" : undefined,
              borderColor: chatOpen ? "rgba(139,92,246,0.3)" : undefined,
              color: chatOpen ? "#c4b5fd" : undefined,
            }}
          >
            <span style={{ fontSize: 18, minWidth: 20, textAlign: "center" }}>✨</span>
            {!sidebarCollapsed && <span>Ask HRIP (Gemini)</span>}
          </button>
        </nav>

        {/* Bottom: collapse + user */}
        <div style={{ padding: "12px 8px", borderTop: "1px solid var(--border)" }}>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="nav-item"
            style={{ width: "100%", justifyContent: sidebarCollapsed ? "center" : "flex-start", marginBottom: 8 }}
          >
            <span style={{ fontSize: 16 }}>{sidebarCollapsed ? "→" : "←"}</span>
            {!sidebarCollapsed && <span>Collapse</span>}
          </button>

          {!sidebarCollapsed && (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 10px", background: "var(--bg-card)", borderRadius: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 700 }}>H</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>Hospital</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Facility Admin</div>
                </div>
              </div>
              <button onClick={handleSignOut} style={{ background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: 12 }} title="Sign Out">🚪</button>
            </div>
          )}
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────── */}
      <main style={{ marginLeft: SIDEBAR_W, flex: 1, display: "flex", flexDirection: "column", minHeight: "100vh", transition: "margin-left 0.25s cubic-bezier(0.4,0,0.2,1)" }}>
        {/* Top bar */}
        <header style={{
          position: "sticky", top: 0, zIndex: 40,
          background: "rgba(10,14,26,0.85)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid var(--border)",
          padding: "0 28px",
          height: 60, display: "flex", alignItems: "center", justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "var(--text-muted)", fontSize: 14 }}>
              {NAV_ITEMS.find(n => pathname.startsWith(n.href) && n.href !== "/dashboard")?.label
                || (pathname === "/dashboard" ? "Overview" : "")}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {/* Live indicator */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 20, padding: "4px 12px" }}>
              <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#10b981", display: "inline-block", animation: "pulse-ring 2s ease-out infinite" }} />
              <span style={{ fontSize: 12, color: "#34d399", fontWeight: 600 }}>LIVE</span>
            </div>
            {/* Ask HRIP inline */}
            <button
              className="btn-ghost"
              onClick={() => setChatOpen(!chatOpen)}
              style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
            >
              ✨ Ask HRIP
            </button>
          </div>
        </header>

        {/* Page content */}
        <div style={{ flex: 1, padding: "24px 28px" }}>
          {children}
        </div>
      </main>

      {/* ── Ask HRIP Chat Overlay ────────────────────────── */}
      {chatOpen && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 100,
          width: 380, height: 540,
          animation: "fadeInUp 0.3s ease",
        }}>
          <AskHRIP onClose={() => setChatOpen(false)} />
        </div>
      )}
    </div>
  );
}
