"use client";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { useHospital, useHospitalInventory, useAddInventoryItem } from "@/lib/queries";

const STATUS_COLOR: Record<string, string> = { critical: "#ef4444", low: "#f59e0b", normal: "#10b981" };

const EMPTY_ITEM = { item_name: "", category: "", stock_level: "", min_threshold: "", unit: "" };
type ItemForm = typeof EMPTY_ITEM;

export default function HospitalInventoryPage() {
  const params = useParams<{ id: string }>();
  const hospitalId = params.id;
  const router = useRouter();

  const { data: hospital, isLoading: hospitalLoading } = useHospital(hospitalId);
  const { data: rawItems = [], isLoading: itemsLoading, isError } = useHospitalInventory(hospitalId);
  const addItem = useAddInventoryItem();

  const [showAddModal, setShowAddModal] = useState(false);
  const [form, setForm] = useState<ItemForm>(EMPTY_ITEM);
  const [formError, setFormError] = useState<string | null>(null);

  const items = rawItems.map((item) => {
    const ratio = item.stock_level / (item.min_threshold || 1);
    let status = "normal";
    if (ratio < 0.5) status = "critical";
    else if (ratio < 1) status = "low";
    return { ...item, status };
  });

  function updateField(key: keyof ItemForm, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function closeModal() {
    setShowAddModal(false);
    setForm(EMPTY_ITEM);
    setFormError(null);
  }

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);

    if (!form.item_name.trim() || !form.category.trim() || !form.unit.trim()) {
      setFormError("Item name, category, and unit are required.");
      return;
    }
    const stock = parseInt(form.stock_level, 10);
    const min = parseInt(form.min_threshold, 10);
    if (Number.isNaN(stock) || Number.isNaN(min)) {
      setFormError("Stock level and minimum threshold must be numbers.");
      return;
    }

    try {
      await addItem.mutateAsync({
        hospital_id: hospitalId,
        item_name: form.item_name.trim(),
        category: form.category.trim(),
        stock_level: stock,
        min_threshold: min,
        unit: form.unit.trim(),
      });
      closeModal();
    } catch (err: any) {
      setFormError(err?.message || "Failed to add item. Please try again.");
    }
  }

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <button onClick={() => router.push("/dashboard/hospitals")} className="btn-ghost" style={{ fontSize: 13, marginBottom: 8 }}>
            ← Back to Hospitals
          </button>
          <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>
            {hospitalLoading ? "Loading…" : hospital?.name || "Inventory"}
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Stock levels for this hospital{hospital?.district ? ` · ${hospital.district}` : ""}
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowAddModal(true)} style={{ fontSize: 13, padding: "8px 16px" }}>
          + Add Inventory Item
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { l: "Critical", n: items.filter((i) => i.status === "critical").length, c: "#ef4444" },
          { l: "Low Stock", n: items.filter((i) => i.status === "low").length, c: "#f59e0b" },
          { l: "Normal", n: items.filter((i) => i.status === "normal").length, c: "#10b981" },
        ].map((s) => (
          <div key={s.l} className="glass" style={{ borderRadius: 12, padding: "14px 16px", textAlign: "center", borderTop: `3px solid ${s.c}` }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.c }}>{s.n}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>

      <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
        {itemsLoading ? (
          <div style={{ textAlign: "center", color: "var(--text-secondary)", padding: "20px 0" }}>Loading inventory...</div>
        ) : isError ? (
          <div style={{ textAlign: "center", color: "#f87171", padding: "20px 0" }}>Failed to load inventory.</div>
        ) : (
          <table className="hrip-table">
            <thead><tr><th>Medicine</th><th>Category</th><th>Stock vs Min</th><th>Units</th><th>Status</th></tr></thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>
                    No inventory data for this hospital yet. Add the first item to get started.
                  </td>
                </tr>
              ) : items.map((item) => {
                const pct = item.min_threshold ? Math.round((item.stock_level / item.min_threshold) * 100) : 0;
                return (
                  <tr key={item.id}>
                    <td><strong>{item.item_name}</strong></td>
                    <td style={{ color: "var(--text-secondary)" }}>{item.category}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ width: 80 }}>
                          <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${Math.min(pct, 100)}%`, background: STATUS_COLOR[item.status] }} />
                          </div>
                        </div>
                        <span style={{ fontSize: 12, fontWeight: 600, color: STATUS_COLOR[item.status] }}>{item.stock_level}/{item.min_threshold}</span>
                      </div>
                    </td>
                    <td style={{ color: "var(--text-muted)", fontSize: 13 }}>{item.unit}</td>
                    <td><span className={`badge-${item.status === "normal" ? "low" : item.status}`} style={{ borderRadius: 6, padding: "3px 8px", fontSize: 11, fontWeight: 600 }}>{item.status.toUpperCase()}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Add Inventory Item modal */}
      {showAddModal && (
        <div
          onClick={closeModal}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.55)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
        >
          <div
            className="glass animate-fade-in"
            onClick={(e) => e.stopPropagation()}
            style={{ borderRadius: 16, padding: 24, width: 420, maxWidth: "90vw", maxHeight: "85vh", overflowY: "auto" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontWeight: 700, fontSize: 18 }}>Add Inventory Item</h3>
              <button onClick={closeModal} className="btn-ghost" style={{ padding: "3px 8px" }}>✕</button>
            </div>

            <form onSubmit={handleAddItem} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <Field label="Item Name *" value={form.item_name} onChange={(v) => updateField("item_name", v)} placeholder="e.g. Paracetamol 500mg" />
              <Field label="Category *" value={form.category} onChange={(v) => updateField("category", v)} placeholder="e.g. Medicine, PPE, Equipment" />
              <div style={{ display: "flex", gap: 12 }}>
                <Field label="Stock Level *" value={form.stock_level} onChange={(v) => updateField("stock_level", v)} placeholder="e.g. 500" />
                <Field label="Min Threshold *" value={form.min_threshold} onChange={(v) => updateField("min_threshold", v)} placeholder="e.g. 100" />
              </div>
              <Field label="Unit *" value={form.unit} onChange={(v) => updateField("unit", v)} placeholder="e.g. tablets, boxes, units" />

              {formError && (
                <div style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", borderRadius: 8, padding: "8px 12px", fontSize: 13 }}>
                  {formError}
                </div>
              )}

              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <button type="button" onClick={closeModal} className="btn-ghost" style={{ flex: 1, fontSize: 13 }}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={addItem.isPending} style={{ flex: 1, fontSize: 13 }}>
                  {addItem.isPending ? "Adding..." : "Add Item"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1, fontSize: 12, color: "var(--text-secondary)" }}>
      {label}
      <input
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        style={{
          background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8,
          padding: "8px 10px", fontSize: 13, color: "var(--text-primary)", outline: "none",
        }}
      />
    </label>
  );
}