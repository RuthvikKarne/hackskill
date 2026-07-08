"use client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, LineChart, Line } from "recharts";

const DISTRICT_DATA: any[] = [];
const TREND_DATA: any[] = [];
const RADAR_DATA: any[] = [];

const RISK_COLOR = (score: number) => score >= 50 ? "#ef4444" : score >= 35 ? "#f59e0b" : "#10b981";

export default function SurveillancePage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Disease Surveillance</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>AI-powered outbreak risk monitoring · Multi-signal epidemiological scoring</p>
      </div>

      {/* District risk cards */}
      <div className="animate-fade-in-up stagger-1" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 14, marginBottom: 24 }}>
        {DISTRICT_DATA.map((d, i) => (
          <div key={d.district} className={`glass glass-hover animate-fade-in-up stagger-${i + 1}`} style={{ borderRadius: 14, padding: "18px 20px", borderLeft: `3px solid ${RISK_COLOR(d.risk)}` }}>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 8, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>{d.district}</div>
            <div style={{ fontSize: 36, fontWeight: 800, color: RISK_COLOR(d.risk), letterSpacing: "-0.02em" }}>{d.risk}</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 10 }}>Risk Score</div>
            <div className="progress-bar" style={{ marginBottom: 12 }}>
              <div className="progress-fill" style={{ width: `${d.risk}%`, background: RISK_COLOR(d.risk) }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
              <span style={{ color: "var(--text-muted)" }}>{d.cases} cases</span>
              <span style={{ color: d.growth > 10 ? "#f87171" : "#34d399" }}>+{d.growth}%/day</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="animate-fade-in-up stagger-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
        {/* Case trend */}
        <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Case Trend — 14 Days</h3>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>Daily new cases by district</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={TREND_DATA}>
              <XAxis dataKey="day" tick={{ fill: "#4a5568", fontSize: 10 }} axisLine={false} tickLine={false} interval={2} />
              <YAxis tick={{ fill: "#4a5568", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "#1a2035", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f0f4ff" }} />
              <Line type="monotone" dataKey="kigali" stroke="#3b82f6" strokeWidth={2} dot={false} name="Kigali" />
              <Line type="monotone" dataKey="musanze" stroke="#ef4444" strokeWidth={2} dot={false} name="Musanze" />
              <Line type="monotone" dataKey="huye" stroke="#10b981" strokeWidth={2} dot={false} name="Huye" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* SHAP Radar */}
        <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>SHAP Feature Importance</h3>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>What drives Musanze district risk (score: 55)</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={RADAR_DATA}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#6b7280", fontSize: 11 }} />
              <Radar name="Score" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts table */}
      <div className="animate-fade-in-up stagger-3 glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Active Surveillance Alerts</h3>
        <table className="hrip-table">
          <thead>
            <tr>
              <th>District</th><th>Risk Score</th><th>Incidence (/100k)</th><th>Daily Growth</th><th>Alert</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No surveillance alerts found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
