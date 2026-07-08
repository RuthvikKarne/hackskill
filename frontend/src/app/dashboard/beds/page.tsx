"use client";
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { createClient } from "@/utils/supabase/client";

const COLOR = (pct: number) => pct >= 90 ? "#ef4444" : pct >= 70 ? "#f59e0b" : "#10b981";

export default function BedsPage() {
  const [beds, setBeds] = useState<any[]>([]);

  useEffect(() => {
    async function fetchBeds() {
      const supabase = createClient();
      const { data } = await supabase.from("beds").select("ward_name, total_beds, occupied_beds");
      if (data) {
        // Group by ward_name across all hospitals
        const grouped = data.reduce((acc: any, bed: any) => {
          if (!acc[bed.ward_name]) {
            acc[bed.ward_name] = { ward: bed.ward_name, total: 0, occupied: 0 };
          }
          acc[bed.ward_name].total += bed.total_beds;
          acc[bed.ward_name].occupied += bed.occupied_beds;
          return acc;
        }, {});
        setBeds(Object.values(grouped));
      }
    }
    fetchBeds();
  }, []);

  const total = beds.reduce((a, b) => a + b.total, 0);
  const occupied = beds.reduce((a, b) => a + b.occupied, 0);
  const pct = total ? Math.round(occupied / total * 100) : 0;

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Beds & Wards</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Real-time bed occupancy across all wards</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14, marginBottom: 24 }}>
        {[
          { label: "Total Beds", value: total, color: "#3b82f6" },
          { label: "Occupied", value: occupied, color: "#f59e0b" },
          { label: "Available", value: total - occupied, color: "#10b981" },
        ].map(s => (
          <div key={s.label} className="glass" style={{ borderRadius: 14, padding: "18px 20px", borderTop: `3px solid ${s.color}` }}>
            <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Occupancy by Ward</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={beds} layout="vertical">
              <XAxis type="number" domain={[0, 100]} tick={{ fill: "#4a5568", fontSize: 11 }} />
              <YAxis type="category" dataKey="ward" tick={{ fill: "#8892aa", fontSize: 12 }} width={80} />
              <Tooltip cursor={{ fill: "rgba(255,255,255,0.02)" }} contentStyle={{ background: "#18181b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f0f4ff" }} formatter={(v: any) => [`${v}%`, "Occupancy"]} />
              <Bar dataKey={(d) => Math.round(d.occupied / d.total * 100)} fill="#3b82f6" radius={[0, 4, 4, 0]} name="Occupancy %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
          <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Ward Details</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {beds.length === 0 ? (
              <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No ward data available</div>
            ) : beds.map(b => {
              const p = b.total ? Math.round(b.occupied / b.total * 100) : 0;
              return (
                <div key={b.ward}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 600 }}>{b.ward}</span>
                    <span style={{ fontSize: 13, color: COLOR(p), fontWeight: 700 }}>{b.occupied}/{b.total} ({p}%)</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${p}%`, background: COLOR(p) }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
