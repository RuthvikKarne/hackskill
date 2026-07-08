"use client";
const TESTS: any[] = [];
const PRI_C: Record<string,string> = { urgent: "#ef4444", stat: "#f59e0b", routine: "#3b82f6" };
const STA_C: Record<string,string> = { "In Progress": "#8b5cf6", "Complete": "#10b981", "Pending": "#4a5568" };

export default function LaboratoryPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Laboratory</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Test queue management and results tracking</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { l: "In Progress", n: TESTS.filter(t=>t.status==="In Progress").length, c: "#8b5cf6" },
          { l: "Pending", n: TESTS.filter(t=>t.status==="Pending").length, c: "#f59e0b" },
          { l: "Complete", n: TESTS.filter(t=>t.status==="Complete").length, c: "#10b981" },
        ].map(s=>(
          <div key={s.l} className="glass" style={{ borderRadius: 12, padding: "14px 16px", textAlign: "center", borderTop: `3px solid ${s.c}` }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.c }}>{s.n}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>
      <div className="glass animate-fade-in-up stagger-1" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <table className="hrip-table">
          <thead><tr><th>Test ID</th><th>Patient</th><th>Test Type</th><th>Priority</th><th>Status</th><th>ETA</th></tr></thead>
          <tbody>
            {TESTS.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No laboratory data available</td>
              </tr>
            ) : TESTS.map(t => (
              <tr key={t.id}>
                <td><code style={{ fontSize: 12, color: "#60a5fa" }}>{t.id}</code></td>
                <td>{t.patient}</td>
                <td style={{ fontWeight: 600 }}>{t.type}</td>
                <td><span style={{ fontSize: 11, fontWeight: 700, borderRadius: 6, padding: "3px 8px", background: `${PRI_C[t.priority]}22`, color: PRI_C[t.priority] }}>{t.priority.toUpperCase()}</span></td>
                <td><span style={{ fontSize: 12, fontWeight: 600, color: STA_C[t.status] }}>{t.status}</span></td>
                <td style={{ color: t.eta !== "—" ? "#60a5fa" : "var(--text-muted)", fontWeight: t.eta !== "—" ? 700 : 400 }}>{t.eta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
