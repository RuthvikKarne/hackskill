"use client";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

const MONTHLY: any[] = [];

const DISEASE_MIX: any[] = [];

export default function AnalyticsPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Analytics & Reports</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>District-wide health intelligence and trend analysis</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div className="glass animate-fade-in-up stagger-1" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Monthly Patient Volume</h3>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>Outpatient visits, admissions, discharges</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={MONTHLY}>
              <defs>
                <linearGradient id="pGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" tick={{ fill: "#4a5568", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#4a5568", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "#1a2035", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f0f4ff" }} />
              <Area type="monotone" dataKey="patients" stroke="#3b82f6" fill="url(#pGrad)" strokeWidth={2} name="Outpatient" />
              <Area type="monotone" dataKey="admissions" stroke="#8b5cf6" fill="transparent" strokeWidth={1.5} strokeDasharray="4 4" name="Admissions" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass animate-fade-in-up stagger-2" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Disease Distribution</h3>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>Case mix by diagnosis category (July 2026)</p>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={DISEASE_MIX} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={3}>
                  {DISEASE_MIX.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1 }}>
              {DISEASE_MIX.map(d => (
                <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: d.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, flex: 1 }}>{d.name}</span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: d.color }}>{d.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="glass animate-fade-in-up stagger-3" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Hospital Admissions Comparison</h3>
        <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>Monthly admissions across all facilities</p>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={MONTHLY}>
            <XAxis dataKey="month" tick={{ fill: "#4a5568", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#4a5568", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "#1a2035", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f0f4ff" }} />
            <Bar dataKey="admissions" fill="#3b82f6" radius={[4,4,0,0]} name="Admissions" />
            <Bar dataKey="discharged" fill="#10b981" radius={[4,4,0,0]} name="Discharged" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
