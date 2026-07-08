"use client";

import { useState, useEffect } from "react";
import { createClient } from "@/utils/supabase/client";

const SEV: Record<string, string> = { critical: "#ef4444", high: "#f59e0b", moderate: "#3b82f6" };

export default function EmergencyPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [ambulances, setAmbulances] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      const supabase = createClient();
      
      const { data: incData } = await supabase
        .from("incidents")
        .select(`id, type, severity, status, patients_involved, ambulances_dispatched, reported_at, hospitals(name)`);
        
      if (incData) {
        setIncidents(incData.map(i => ({
          id: `INC-${i.id.split('-')[0].toUpperCase()}`,
          type: i.type,
          severity: i.severity,
          status: i.status,
          patients: i.patients_involved,
          ambulances: i.ambulances_dispatched,
          hospital: i.hospitals?.name || 'Unknown',
          time: new Date(i.reported_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        })));
      }

      const { data: ambData } = await supabase
        .from("ambulances")
        .select(`id, driver_name, status, eta, hospitals(name)`);
        
      if (ambData) {
        setAmbulances(ambData.map(a => ({
          id: `AMB-${a.id.split('-')[0].toUpperCase()}`,
          driver: a.driver_name,
          status: a.status,
          hospital: a.hospitals?.name || 'Unknown',
          eta: a.eta
        })));
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <div className="animate-fade-in-up" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Emergency Response</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Real-time incident tracking · Ambulance coordination · Resource allocation</p>
        </div>
        <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: "10px 18px", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#ef4444", display: "inline-block", animation: incidents.length > 0 ? "pulse-ring 1.5s ease-out infinite" : "none" }} />
          <span style={{ fontSize: 14, color: "#f87171", fontWeight: 700 }}>{incidents.length} ACTIVE INCIDENT{incidents.length !== 1 ? 'S' : ''}</span>
        </div>
      </div>

      {/* Incident cards */}
      <div className="animate-fade-in-up stagger-1" style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 24 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 4 }}>Active Incidents</h2>
        {incidents.length === 0 ? (
          <div className="glass" style={{ borderRadius: 14, padding: "30px 20px", textAlign: "center", color: "var(--text-muted)" }}>No active incidents</div>
        ) : incidents.map((inc, i) => (
          <div key={inc.id} className={`glass glass-hover animate-fade-in-up stagger-${i + 1}`} style={{ borderRadius: 14, padding: "18px 20px", borderLeft: `4px solid ${SEV[inc.severity] || "#666"}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ fontWeight: 800, fontSize: 14 }}>{inc.id}</span>
                  <span className={`badge-${inc.severity}`} style={{ borderRadius: 6, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>{inc.severity.toUpperCase()}</span>
                  <span style={{ fontSize: 12, color: inc.status === "Active" ? "#f87171" : inc.status === "Contained" ? "#fbbf24" : "#34d399", fontWeight: 600 }}>
                    {inc.status === "Active" ? "🔴" : inc.status === "Contained" ? "🟡" : "🟢"} {inc.status}
                  </span>
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>{inc.type}</div>
                <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>🏥 {inc.hospital} · {inc.time}</div>
              </div>
              <div style={{ display: "flex", gap: 16, textAlign: "right" }}>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{inc.patients}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Patients</div>
                </div>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{inc.ambulances}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Ambulances</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Ambulance tracker */}
      <div className="animate-fade-in-up stagger-3 glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>🚑 Ambulance Fleet Status</h3>
        <table className="hrip-table">
          <thead>
            <tr><th>Unit</th><th>Driver</th><th>Status</th><th>Assigned Hospital</th><th>ETA</th></tr>
          </thead>
          <tbody>
            {ambulances.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No ambulance data available</td>
              </tr>
            ) : ambulances.map(a => (
              <tr key={a.id}>
                <td><strong>{a.id}</strong></td>
                <td>{a.driver}</td>
                <td>
                  <span style={{
                    fontSize: 12, fontWeight: 600, borderRadius: 6, padding: "3px 8px",
                    background: a.status === "En Route" ? "rgba(59,130,246,0.15)" : a.status === "On Scene" ? "rgba(239,68,68,0.15)" : "rgba(16,185,129,0.15)",
                    color: a.status === "En Route" ? "#60a5fa" : a.status === "On Scene" ? "#f87171" : "#34d399",
                  }}>{a.status}</span>
                </td>
                <td>{a.hospital}</td>
                <td style={{ color: a.eta !== "—" ? "#60a5fa" : "var(--text-muted)", fontWeight: a.eta !== "—" ? 700 : 400 }}>{a.eta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
