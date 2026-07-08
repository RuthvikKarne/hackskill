"use client";
const DOCTORS: any[] = [];
const STATUS_C: Record<string,string> = { "On Duty": "#10b981", "On Call": "#f59e0b", "In Theatre": "#8b5cf6", "Off Duty": "#4a5568" };

export default function DoctorsPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Doctors & Staff</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Medical staff tracking and shift management</p>
      </div>
      <div className="glass animate-fade-in-up stagger-1" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <table className="hrip-table">
          <thead><tr><th>Doctor</th><th>Specialty</th><th>Hospital</th><th>Current Patients</th><th>Status</th><th>Shift</th></tr></thead>
          <tbody>
            {DOCTORS.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No doctors data available</td>
              </tr>
            ) : DOCTORS.map(d => (
              <tr key={d.id}>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 34, height: 34, borderRadius: "50%", background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700 }}>{d.name.split(" ")[1][0]}</div>
                    <div><div style={{ fontWeight: 600, fontSize: 14 }}>{d.name}</div><div style={{ fontSize: 12, color: "var(--text-muted)" }}>{d.id}</div></div>
                  </div>
                </td>
                <td style={{ color: "var(--text-secondary)" }}>{d.specialty}</td>
                <td style={{ fontSize: 13 }}>{d.hospital}</td>
                <td><span style={{ fontWeight: 700, color: d.patients > 10 ? "#f59e0b" : "var(--text-primary)" }}>{d.patients}</span></td>
                <td><span style={{ fontSize: 12, fontWeight: 600, borderRadius: 6, padding: "3px 10px", background: `${STATUS_C[d.status]}22`, color: STATUS_C[d.status] }}>{d.status}</span></td>
                <td style={{ color: "var(--text-secondary)", fontSize: 13 }}>{d.shift}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
