"use client";
import { useState, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useWards, useAddWard, Ward, NewWardInput } from "@/lib/queries";

// ── Helpers ───────────────────────────────────────────────────────────────────

const OCC_COLOR = (pct: number) =>
  pct >= 90 ? "#ef4444" : pct >= 70 ? "#f59e0b" : "#10b981";

type WardFormState = {
  ward_name: string;
  total_beds: string;
  occupied_beds: string;
};

const EMPTY_FORM: WardFormState = { ward_name: "", total_beds: "", occupied_beds: "" };

// ── Component ─────────────────────────────────────────────────────────────────

export default function BedsPage() {
  // ── Data ──
  const { data: rawWards = [], isLoading, isError } = useWards();
  const addWard = useAddWard();

  // ── Aggregate ward rows (group identical ward_name across hospitals) ──
  const beds = useMemo(() => {
    const grouped: Record<string, { ward: string; total: number; occupied: number }> = {};
    rawWards.forEach((w: Ward) => {
      if (!grouped[w.ward_name]) {
        grouped[w.ward_name] = { ward: w.ward_name, total: 0, occupied: 0 };
      }
      grouped[w.ward_name].total += w.total_beds;
      grouped[w.ward_name].occupied += w.occupied_beds;
    });
    return Object.values(grouped);
  }, [rawWards]);

  const totalBeds = beds.reduce((a, b) => a + b.total, 0);
  const totalOccupied = beds.reduce((a, b) => a + b.occupied, 0);
  const overallPct = totalBeds ? Math.round((totalOccupied / totalBeds) * 100) : 0;

  // ── Modal state ──
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<WardFormState>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);

  function updateField(key: keyof WardFormState, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setFormError(null);
  }

  function closeModal() {
    setShowModal(false);
    setForm(EMPTY_FORM);
    setFormError(null);
  }

  async function handleAddWard(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    // ── Validation ──
    const trimmedName = form.ward_name.trim();
    if (!trimmedName) {
      setFormError("Ward name is required.");
      return;
    }

    const totalNum = parseInt(form.total_beds, 10);
    if (!form.total_beds || isNaN(totalNum) || totalNum <= 0) {
      setFormError("Total beds must be a positive number.");
      return;
    }

    const occupiedNum = parseInt(form.occupied_beds, 10);
    if (form.occupied_beds === "" || isNaN(occupiedNum) || occupiedNum < 0) {
      setFormError("Occupied beds must be 0 or a positive number.");
      return;
    }

    if (occupiedNum > totalNum) {
      setFormError("Occupied beds cannot exceed total beds.");
      return;
    }

    const payload: NewWardInput = {
      ward_name: trimmedName,
      total_beds: totalNum,
      occupied_beds: occupiedNum,
    };

    try {
      await addWard.mutateAsync(payload);
      closeModal();
    } catch (err: any) {
      setFormError(err?.message || "Failed to add ward. Please try again.");
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div>
      {/* ── Header ── */}
      <div className="animate-fade-in-up" style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>
            Beds &amp; Wards
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Real-time bed occupancy across all wards
          </p>
        </div>
        <button
          id="add-ward-btn"
          className="btn-primary"
          onClick={() => setShowModal(true)}
          style={{ fontSize: 13, padding: "8px 16px" }}
        >
          + Add Ward
        </button>
      </div>

      {/* ── Loading / Error ── */}
      {isLoading ? (
        <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-secondary)" }}>
          <div style={{ display: "inline-block", width: 24, height: 24, border: "2px solid rgba(59,130,246,0.3)", borderTopColor: "#3b82f6", borderRadius: "50%", animation: "spin-slow 0.8s linear infinite", marginBottom: 16 }} />
          <div>Loading ward data…</div>
        </div>
      ) : isError ? (
        <div style={{ padding: 40, background: "rgba(239,68,68,0.1)", borderRadius: 12, color: "#f87171", textAlign: "center" }}>
          Failed to load ward data. Please try again.
        </div>
      ) : (
        <>
          {/* ── KPI cards ── */}
          <div className="animate-fade-in-up stagger-1" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 14, marginBottom: 24 }}>
            {[
              { label: "Total Beds", value: totalBeds, color: "#3b82f6" },
              { label: "Occupied", value: totalOccupied, color: OCC_COLOR(overallPct) },
              { label: "Available", value: totalBeds - totalOccupied, color: "#10b981" },
              { label: "Occupancy Rate", value: `${overallPct}%`, color: OCC_COLOR(overallPct) },
            ].map((s) => (
              <div key={s.label} className="glass" style={{ borderRadius: 14, padding: "18px 20px", borderTop: `3px solid ${s.color}` }}>
                <div style={{ fontSize: 30, fontWeight: 800, color: s.color }}>{s.value}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* ── Charts + Table ── */}
          <div className="animate-fade-in-up stagger-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {/* Bar chart */}
            <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
              <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Occupancy by Ward</h3>
              {beds.length === 0 ? (
                <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "40px 0", fontSize: 13 }}>
                  No wards yet. Add one to get started.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={Math.max(220, beds.length * 42)}>
                  <BarChart data={beds} layout="vertical">
                    <XAxis type="number" domain={[0, 100]} tick={{ fill: "#4a5568", fontSize: 11 }} />
                    <YAxis type="category" dataKey="ward" tick={{ fill: "#8892aa", fontSize: 12 }} width={90} />
                    <Tooltip
                      cursor={{ fill: "rgba(255,255,255,0.02)" }}
                      contentStyle={{ background: "#18181b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f0f4ff" }}
                      formatter={(v: any) => [`${v}%`, "Occupancy"]}
                    />
                    <Bar
                      dataKey={(d) => (d.total ? Math.round((d.occupied / d.total) * 100) : 0)}
                      fill="#3b82f6"
                      radius={[0, 4, 4, 0]}
                      name="Occupancy %"
                    />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Ward details list */}
            <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
              <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Ward Details</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {beds.length === 0 ? (
                  <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0", fontSize: 13 }}>
                    No ward data available
                  </div>
                ) : (
                  beds.map((b) => {
                    const p = b.total ? Math.round((b.occupied / b.total) * 100) : 0;
                    const color = OCC_COLOR(p);
                    return (
                      <div key={b.ward}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                          <span style={{ fontSize: 13, fontWeight: 600 }}>{b.ward}</span>
                          <span style={{ fontSize: 13, color, fontWeight: 700 }}>
                            {b.occupied}/{b.total} ({p}%)
                          </span>
                        </div>
                        <div className="progress-bar">
                          <div className="progress-fill" style={{ width: `${p}%`, background: color }} />
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* ── Full ward table ── */}
          {beds.length > 0 && (
            <div className="animate-fade-in-up stagger-3 glass" style={{ borderRadius: 16, padding: "20px 22px", marginTop: 16 }}>
              <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>All Wards</h3>
              <table className="hrip-table">
                <thead>
                  <tr>
                    <th>Ward Name</th>
                    <th>Total Beds</th>
                    <th>Occupied</th>
                    <th>Available</th>
                    <th>Occupancy</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {beds.map((b) => {
                    const p = b.total ? Math.round((b.occupied / b.total) * 100) : 0;
                    const color = OCC_COLOR(p);
                    const statusLabel = p >= 90 ? "CRITICAL" : p >= 70 ? "HIGH" : "NORMAL";
                    const badgeClass = p >= 90 ? "badge-critical" : p >= 70 ? "badge-high" : "badge-low";
                    return (
                      <tr key={b.ward}>
                        <td><strong>{b.ward}</strong></td>
                        <td>{b.total}</td>
                        <td style={{ color }}>{b.occupied}</td>
                        <td style={{ color: "#10b981" }}>{b.total - b.occupied}</td>
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <div style={{ width: 70 }}>
                              <div className="progress-bar">
                                <div className="progress-fill" style={{ width: `${p}%`, background: color }} />
                              </div>
                            </div>
                            <span style={{ fontSize: 12, fontWeight: 700, color }}>{p}%</span>
                          </div>
                        </td>
                        <td>
                          <span className={badgeClass} style={{ borderRadius: 6, padding: "3px 8px", fontSize: 11, fontWeight: 600 }}>
                            {statusLabel}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ── Add Ward Modal ─────────────────────────────────────────────────────── */}
      {showModal && (
        <div
          id="add-ward-modal-overlay"
          onClick={closeModal}
          style={{
            position: "fixed", inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            id="add-ward-modal"
            className="glass animate-fade-in"
            onClick={(e) => e.stopPropagation()}
            style={{ borderRadius: 16, padding: 28, width: 420, maxWidth: "92vw" }}
          >
            {/* Modal header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <h3 style={{ fontWeight: 700, fontSize: 18 }}>Add New Ward</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 2 }}>
                  Enter ward details below
                </p>
              </div>
              <button
                id="close-ward-modal-btn"
                onClick={closeModal}
                className="btn-ghost"
                style={{ padding: "3px 8px" }}
              >
                ✕
              </button>
            </div>

            <form id="add-ward-form" onSubmit={handleAddWard} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {/* Ward Name */}
              <WardField
                id="ward-name-input"
                label="Ward Name *"
                value={form.ward_name}
                onChange={(v) => updateField("ward_name", v)}
                placeholder="e.g. General Ward, ICU, Paediatrics"
              />

              {/* Total & Occupied beds side-by-side */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <WardField
                  id="total-beds-input"
                  label="Total Beds *"
                  type="number"
                  value={form.total_beds}
                  onChange={(v) => updateField("total_beds", v)}
                  placeholder="e.g. 50"
                  min={1}
                />
                <WardField
                  id="occupied-beds-input"
                  label="Occupied Beds *"
                  type="number"
                  value={form.occupied_beds}
                  onChange={(v) => updateField("occupied_beds", v)}
                  placeholder="e.g. 32"
                  min={0}
                />
              </div>

              {/* Real-time cross-field hint */}
              {form.total_beds && form.occupied_beds && (() => {
                const t = parseInt(form.total_beds, 10);
                const o = parseInt(form.occupied_beds, 10);
                if (!isNaN(t) && !isNaN(o) && t > 0 && o >= 0 && o <= t) {
                  const pct = Math.round((o / t) * 100);
                  const color = OCC_COLOR(pct);
                  return (
                    <div style={{ display: "flex", alignItems: "center", gap: 12, background: "var(--bg-secondary)", borderRadius: 10, padding: "10px 14px" }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 5 }}>Live preview</div>
                        <div className="progress-bar">
                          <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
                        </div>
                      </div>
                      <span style={{ fontSize: 14, fontWeight: 800, color }}>{pct}%</span>
                    </div>
                  );
                }
                return null;
              })()}

              {/* Validation error */}
              {formError && (
                <div style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", borderRadius: 8, padding: "10px 14px", fontSize: 13, display: "flex", alignItems: "center", gap: 8 }}>
                  <span>⚠</span>
                  <span>{formError}</span>
                </div>
              )}

              {/* Actions */}
              <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                <button
                  type="button"
                  id="cancel-ward-btn"
                  onClick={closeModal}
                  className="btn-ghost"
                  style={{ flex: 1, fontSize: 13 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  id="submit-ward-btn"
                  className="btn-primary"
                  disabled={addWard.isPending}
                  style={{ flex: 1, fontSize: 13 }}
                >
                  {addWard.isPending ? "Adding…" : "Add Ward"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Field sub-component ───────────────────────────────────────────────────────

function WardField({
  id,
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  min,
}: {
  id?: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: "text" | "number";
  min?: number;
}) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12, color: "var(--text-secondary)" }}>
      {label}
      <input
        id={id}
        type={type}
        value={value}
        placeholder={placeholder}
        min={min}
        onChange={(e) => onChange(e.target.value)}
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "9px 11px",
          fontSize: 13,
          color: "var(--text-primary)",
          outline: "none",
          transition: "border-color 0.15s",
          width: "100%",
        }}
        onFocus={(e) => (e.target.style.borderColor = "var(--border-active)")}
        onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
      />
    </label>
  );
}
