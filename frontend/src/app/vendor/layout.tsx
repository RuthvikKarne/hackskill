"use client";
import { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { createBrowserClient } from "@supabase/ssr";

export default function VendorLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  // A simple client-side logout just to be able to reset state easily
  const handleSignOut = async () => {
    const supabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
    await supabase.auth.signOut();
    window.location.href = "/";
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Vendor Sidebar */}
      <aside style={{ width: 260, borderRight: "1px solid var(--border)", background: "var(--bg-card)", display: "flex", flexDirection: "column", padding: "24px 20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 40, paddingLeft: 8 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #10b981, #059669)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800 }}>V</div>
          <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: "-0.03em" }}>Vendor Portal</div>
        </div>

        <nav style={{ display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
          {[
            { href: "/vendor", label: "📦 Orders & Supply" },
            { href: "/vendor/inventory", label: "💊 Vendor Inventory" },
            { href: "/vendor/routes", label: "🚚 Distribution Routes" },
          ].map((link) => {
            const active = pathname === link.href;
            return (
              <Link 
                key={link.href} 
                href={link.href} 
                style={{ 
                  display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", borderRadius: 10, textDecoration: "none", 
                  color: active ? "var(--text-primary)" : "var(--text-secondary)", 
                  background: active ? "var(--bg-card-hover)" : "transparent", 
                  fontWeight: active ? 600 : 500,
                  transition: "all 0.2s ease"
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <button onClick={handleSignOut} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", borderRadius: 10, color: "#f87171", background: "none", border: "none", cursor: "pointer", fontWeight: 600, textAlign: "left", marginTop: "auto" }}>
          🚪 Sign Out
        </button>
      </aside>

      {/* Main Vendor Content */}
      <main style={{ flex: 1, padding: "40px 48px", overflowY: "auto", position: "relative" }}>
        <div className="ambient-glow" style={{ top: -100, left: 200, opacity: 0.3, background: "#10b981" }} />
        {children}
      </main>
    </div>
  );
}
