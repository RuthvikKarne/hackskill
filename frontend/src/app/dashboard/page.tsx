"use client";
import { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

import { createClient } from "@/utils/supabase/client";

// ── Mock data (connects to AI engine in production) ───────────────────────
const FORECAST_DATA: any[] = [];
const ALERTS: any[] = [];

const RISK_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f59e0b",
  moderate: "#3b82f6",
  low: "#10b981",
};

function KPICard({ title, value, sub, icon, color, delta }: { title: string; value: string; sub?: string; icon: string; color: string; delta?: string }) {
  const [animated, setAnimated] = useState(false);
  useEffect(() => { setTimeout(() => setAnimated(true), 100); }, []);
  return (
    <div className="glass glass-hover" style={{ borderRadius: 16, padding: "20px 22px", borderLeft: `3px solid ${color}`, transition: "all 0.3s" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>{title}</span>
        <span style={{ fontSize: 22 }}>{icon}</span>
      </div>
      <div style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", lineHeight: 1 }}>{animated ? value : "—"}</div>
      {sub && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>{sub}</div>}
      {delta && <div style={{ fontSize: 12, color: delta.startsWith("+") ? "#f87171" : "#34d399", marginTop: 4, fontWeight: 600 }}>{delta} vs last week</div>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; name: string; color: string }>; label?: string }) => {
  if (active && payload?.length) {
    return (
      <div className="glass" style={{ borderRadius: 10, padding: "10px 14px", border: "1px solid var(--border)" }}>
        <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ fontSize: 14, fontWeight: 600, color: p.color }}>
            {p.name}: {p.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function DashboardPage() {
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [activeHospital, setActiveHospital] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      const supabase = createClient();
      const { data, error } = await supabase
        .from("hospitals")
        .select(`
          id, name, district,
          beds (total_beds, occupied_beds),
          inventory (stock_level, min_threshold),
          incidents (severity, status)
        `);
      
      if (data) {
        // Transform the nested data into the shape our table expects
        const transformed = data.map(h => {
          const totalBeds = h.beds?.reduce((a: number, b: any) => a + b.total_beds, 0) || 0;
          const occupiedBeds = h.beds?.reduce((a: number, b: any) => a + b.occupied_beds, 0) || 0;
          const occupancy = totalBeds ? occupiedBeds / totalBeds : 0;
          
          const totalStock = h.inventory?.reduce((a: number, b: any) => a + b.stock_level, 0) || 0;
          const totalMin = h.inventory?.reduce((a: number, b: any) => a + b.min_threshold, 0) || 1;
          const stockRatio = totalStock / totalMin; // just a rough metric
          const stockScore = stockRatio > 1.5 ? 0.9 : stockRatio > 1 ? 0.6 : 0.3;

          const activeIncidents = h.incidents?.filter((i: any) => i.status === "Active") || [];
          const hasCritical = activeIncidents.some((i: any) => i.severity === "critical");
          const hasHigh = activeIncidents.some((i: any) => i.severity === "high");

          // Basic Risk logic
          let risk = (occupancy * 0.6) + ((1 - stockScore) * 0.4);
          let level = "low";
          if (hasCritical || risk > 0.8) {
            level = "critical";
            risk = Math.max(risk, 0.9);
          } else if (hasHigh || risk > 0.6) {
            level = "high";
            risk = Math.max(risk, 0.7);
          } else if (risk > 0.4) {
            level = "moderate";
          }

          return {
            id: h.id,
            name: h.name,
            city: h.district,
            occupancy,
            stock: stockScore,
            waitTime: level === "critical" ? 85 : level === "high" ? 45 : 15,
            risk,
            level
          };
        });
        setHospitals(transformed);
      }
    }
    fetchData();
  }, []);

  const critical = hospitals.filter(h => h.level === "critical").length;
  const high = hospitals.filter(h => h.level === "high").length;
  const avgOccupancy = hospitals.length ? Math.round(hospitals.reduce((a, h) => a + h.occupancy, 0) / hospitals.length * 100) : 0;

  return (
    <div>
      {/* Page header */}
      <div className="animate-fade-in-up" style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>
          District Overview
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
          Real-time health resource intelligence · {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="animate-fade-in-up stagger-1" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
        <KPICard title="Critical Hospitals" value={`${critical}`} sub="Require immediate action" icon="🚨" color="#ef4444" delta="+1" />
        <KPICard title="Avg Bed Occupancy" value={`${avgOccupancy}%`} sub="Across 4 hospitals" icon="🛏️" color="#f59e0b" delta="+8%" />
        <KPICard title="AI Recommendations" value="3" sub="Pending human approval" icon="🤖" color="#8b5cf6" />
        <KPICard title="Active Emergencies" value="1" sub="District-wide" icon="🚑" color="#ef4444" />
        <KPICard title="Forecast (7-day avg)" value="138" sub="Patients per day" icon="📈" color="#3b82f6" delta="+15%" />
      </div>

      {/* Main grid: Chart + Alerts */}
      <div className="animate-fade-in-up stagger-2" style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 16, marginBottom: 24 }}>
        {/* Patient load forecast chart */}
        <div className="glass" style={{ borderRadius: 16, padding: "22px 24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <h3 style={{ fontWeight: 700, fontSize: 16 }}>Patient Load Forecast</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: 12, marginTop: 2 }}>7-day AI forecast with confidence bands</p>
            </div>
            <span style={{ fontSize: 11, background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.2)", borderRadius: 20, padding: "3px 10px", color: "#60a5fa" }}>
              EMA + Seasonal Model
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={FORECAST_DATA}>
              <defs>
                <linearGradient id="patientGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" tick={{ fill: "#4a5568", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#4a5568", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="patients" stroke="#3b82f6" strokeWidth={2} fill="url(#patientGrad)" name="Actual" />
              <Area type="monotone" dataKey="forecast" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" fill="url(#forecastGrad)" name="Forecast" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts feed */}
        <div className="glass" style={{ borderRadius: 16, padding: "22px 20px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>Live Alerts</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: 12, marginBottom: 16 }}>Real-time system notifications</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {ALERTS.length === 0 ? (
              <div style={{ textAlign: "center", padding: "20px 0", color: "var(--text-muted)", fontSize: 13 }}>No active alerts</div>
            ) : ALERTS.map((alert) => (
              <div key={alert.id} style={{
                background: "var(--bg-card-hover)",
                border: `1px solid ${RISK_COLORS[alert.type]}22`,
                borderLeft: `3px solid ${RISK_COLORS[alert.type]}`,
                borderRadius: 10, padding: "10px 12px",
              }}>
                <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span style={{ fontSize: 16 }}>{alert.icon}</span>
                  <div>
                    <p style={{ fontSize: 12, lineHeight: 1.5 }}>{alert.msg}</p>
                    <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>{alert.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Hospital table */}
      <div className="animate-fade-in-up stagger-3 glass" style={{ borderRadius: 16, padding: "22px 24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div>
            <h3 style={{ fontWeight: 700, fontSize: 16 }}>Hospital Risk Dashboard</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: 12, marginTop: 2 }}>Live AI risk scores with feature breakdown</p>
          </div>
          <a href="/dashboard/hospitals" style={{ fontSize: 13, color: "#60a5fa", textDecoration: "none" }}>View on Map →</a>
        </div>
        <table className="hrip-table">
          <thead>
            <tr>
              <th>Hospital</th>
              <th>Risk Score</th>
              <th>Bed Occupancy</th>
              <th>Stock Level</th>
              <th>Wait Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {hospitals.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No hospital data available</td>
              </tr>
            ) : hospitals.map((h) => (
              <tr key={h.id} onClick={() => setActiveHospital(h.id === activeHospital ? null : h.id)} style={{ cursor: "pointer" }}>
                <td>
                  <div style={{ fontWeight: 600 }}>{h.name}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{h.city}</div>
                </td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 60 }}>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${h.risk * 100}%`, background: RISK_COLORS[h.level] }} />
                      </div>
                    </div>
                    <span style={{ fontWeight: 700, color: RISK_COLORS[h.level] }}>{(h.risk * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 50 }}>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${h.occupancy * 100}%`, background: h.occupancy > 0.8 ? "#ef4444" : h.occupancy > 0.6 ? "#f59e0b" : "#10b981" }} />
                      </div>
                    </div>
                    <span>{(h.occupancy * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td>
                  <span style={{ color: h.stock < 0.3 ? "#f87171" : h.stock < 0.5 ? "#fbbf24" : "#34d399" }}>
                    {(h.stock * 100).toFixed(0)}%
                  </span>
                </td>
                <td><span style={{ color: h.waitTime > 60 ? "#f59e0b" : "var(--text-primary)" }}>{h.waitTime} min</span></td>
                <td>
                  <span className={`badge-${h.level}`} style={{ borderRadius: 6, padding: "3px 10px", fontSize: 12, fontWeight: 600 }}>
                    {h.level.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
