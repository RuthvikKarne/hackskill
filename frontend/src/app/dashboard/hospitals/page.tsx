"use client";
import dynamic from "next/dynamic";
import { useState } from "react";

// Dynamically import map to avoid SSR issues with Leaflet
const HospitalMap = dynamic(() => import("@/components/HospitalMap"), {
  ssr: false,
  loading: () => (
    <div className="skeleton" style={{ height: 420, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "var(--text-muted)" }}>Loading map…</p>
    </div>
  ),
});

import { useHospitals, Hospital } from "@/lib/queries";

const RISK_COLORS: Record<string, string> = {
  critical: "#ef4444", high: "#f59e0b", moderate: "#3b82f6", low: "#10b981",
};

export default function HospitalsPage() {
  const { data: HOSPITALS = [], isLoading, isError } = useHospitals();
  const [selected, setSelected] = useState<Hospital | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const filtered = filter === "all" ? HOSPITALS : HOSPITALS.filter(h => h.level === filter);

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Hospital Network</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Live risk map · Click any hospital for details</p>
      </div>

      {/* Filter pills */}
      <div className="animate-fade-in-up stagger-1" style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {["all", "critical", "high", "moderate", "low"].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            background: filter === f ? (f === "all" ? "rgba(59,130,246,0.2)" : `${RISK_COLORS[f]}22`) : "var(--bg-card)",
            border: `1px solid ${filter === f ? (f === "all" ? "rgba(59,130,246,0.4)" : `${RISK_COLORS[f]}55`) : "var(--border)"}`,
            borderRadius: 20, padding: "6px 16px", fontSize: 13, cursor: "pointer",
            color: filter === f ? (f === "all" ? "#60a5fa" : RISK_COLORS[f]) : "var(--text-secondary)",
            fontWeight: filter === f ? 600 : 400, transition: "all 0.15s",
          }}>
            {f === "all" ? "All Hospitals" : f.charAt(0).toUpperCase() + f.slice(1)}
            <span style={{ marginLeft: 6, opacity: 0.7 }}>
              {f === "all" ? HOSPITALS.length : HOSPITALS.filter(h => h.level === f).length}
            </span>
          </button>
        ))}
      </div>

      {isLoading ? (
        <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-secondary)" }}>
          <div style={{ display: "inline-block", width: 24, height: 24, border: "2px solid rgba(59,130,246,0.3)", borderTopColor: "#3b82f6", borderRadius: "50%", animation: "spin-slow 0.8s linear infinite", marginBottom: 16 }} />
          <div>Loading hospitals data...</div>
        </div>
      ) : isError ? (
        <div style={{ padding: "40px", background: "rgba(239,68,68,0.1)", borderRadius: 12, color: "#f87171", textAlign: "center" }}>
          Failed to load hospitals. Please try again.
        </div>
      ) : (
        <>
          {/* Map + Detail panel */}
          <div className="animate-fade-in-up stagger-2" style={{ display: "grid", gridTemplateColumns: selected ? "1fr 320px" : "1fr", gap: 16, marginBottom: 20, transition: "all 0.3s" }}>
        <div>
          <HospitalMap hospitals={HOSPITALS} selected={selected?.id} onSelect={(id) => setSelected(HOSPITALS.find(h => h.id === id) || null)} />
        </div>

        {selected && (
          <div className="glass animate-fade-in" style={{ borderRadius: 16, padding: 20, borderLeft: `3px solid ${RISK_COLORS[selected.level]}`, height: "fit-content" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <h3 style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{selected.name}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{selected.city}</p>
              </div>
              <button onClick={() => setSelected(null)} className="btn-ghost" style={{ padding: "3px 8px" }}>✕</button>
            </div>

            <span className={`badge-${selected.level}`} style={{ borderRadius: 6, padding: "4px 12px", fontSize: 12, fontWeight: 700, display: "inline-block", marginBottom: 16 }}>
              {selected.level.toUpperCase()} RISK · {(selected.risk * 100).toFixed(0)}%
            </span>

            {[
              { label: "Bed Occupancy", value: `${(selected.occupancy * 100).toFixed(0)}%`, color: selected.occupancy > 0.8 ? "#f87171" : "#34d399" },
              { label: "Stock Level", value: `${(selected.stock * 100).toFixed(0)}%`, color: selected.stock < 0.3 ? "#f87171" : "#34d399" },
              { label: "Avg Wait Time", value: `${selected.waitTime} min`, color: selected.waitTime > 60 ? "#fbbf24" : "#34d399" },
              { label: "Total Beds", value: `${selected.beds}`, color: "var(--text-primary)" },
              { label: "ICU Beds", value: `${selected.icu}`, color: "var(--text-primary)" },
            ].map(item => (
              <div key={item.label} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{item.label}</span>
                <span style={{ fontSize: 13, fontWeight: 600, color: item.color }}>{item.value}</span>
              </div>
            ))}

            <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 8 }}>
              <a href="/dashboard/recommendations" style={{ display: "block" }}>
                <button className="btn-primary" style={{ width: "100%", fontSize: 13 }}>View AI Recommendations</button>
              </a>
              <button className="btn-ghost" style={{ width: "100%", fontSize: 13 }}>📞 {selected.phone}</button>
            </div>
          </div>
        )}
      </div>

      {/* Hospital cards grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
        {filtered.map((h, i) => (
          <div
            key={h.id}
            className={`glass glass-hover animate-fade-in-up stagger-${Math.min(i + 2, 5)}`}
            onClick={() => setSelected(h)}
            style={{ borderRadius: 14, padding: "18px 20px", cursor: "pointer", borderLeft: `3px solid ${RISK_COLORS[h.level]}` }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 2 }}>{h.name}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{h.city} · {h.beds} beds</div>
              </div>
              <span className={`badge-${h.level}`} style={{ borderRadius: 6, padding: "3px 8px", fontSize: 11, fontWeight: 700 }}>
                {h.level.toUpperCase()}
              </span>
            </div>

            <div style={{ display: "flex", gap: 12 }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Beds</div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${h.occupancy * 100}%`, background: h.occupancy > 0.8 ? "#ef4444" : h.occupancy > 0.6 ? "#f59e0b" : "#10b981" }} />
                </div>
                <div style={{ fontSize: 12, marginTop: 3, fontWeight: 600, color: h.occupancy > 0.8 ? "#f87171" : "var(--text-primary)" }}>{(h.occupancy * 100).toFixed(0)}%</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Stock</div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${h.stock * 100}%`, background: h.stock < 0.3 ? "#ef4444" : h.stock < 0.5 ? "#f59e0b" : "#10b981" }} />
                </div>
                <div style={{ fontSize: 12, marginTop: 3, fontWeight: 600, color: h.stock < 0.3 ? "#f87171" : "var(--text-primary)" }}>{(h.stock * 100).toFixed(0)}%</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 2 }}>Risk</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: RISK_COLORS[h.level] }}>{(h.risk * 100).toFixed(0)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      </>
      )}
    </div>
  );
}
