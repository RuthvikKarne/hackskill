"use client";
import { useState, useEffect } from "react";
import { createClient } from "@/utils/supabase/client";

const STATUS_COLOR: Record<string, string> = { critical: "#ef4444", low: "#f59e0b", normal: "#10b981" };

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    async function fetchInventory() {
      const supabase = createClient();
      const { data } = await supabase.from("inventory").select("item_name, category, stock_level, min_threshold, unit");
      if (data) {
        // Group by item_name across all hospitals
        const grouped = data.reduce((acc: any, curr: any) => {
          if (!acc[curr.item_name]) {
            acc[curr.item_name] = { 
              name: curr.item_name, 
              category: curr.category, 
              stock: 0, 
              min: 0, 
              unit: curr.unit 
            };
          }
          acc[curr.item_name].stock += curr.stock_level;
          acc[curr.item_name].min += curr.min_threshold;
          return acc;
        }, {});

        const itemsArr = Object.values(grouped).map((item: any) => {
          const ratio = item.stock / (item.min || 1);
          let status = "normal";
          if (ratio < 0.5) status = "critical";
          else if (ratio < 1) status = "low";
          return { ...item, status };
        });
        setItems(itemsArr);
      }
    }
    fetchInventory();
  }, []);

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Inventory Management</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Medicine and supply stock levels · AI-powered demand forecasting</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { l: "Critical", n: items.filter(i=>i.status==="critical").length, c: "#ef4444" },
          { l: "Low Stock", n: items.filter(i=>i.status==="low").length, c: "#f59e0b" },
          { l: "Normal", n: items.filter(i=>i.status==="normal").length, c: "#10b981" },
        ].map(s=>(
          <div key={s.l} className="glass" style={{ borderRadius: 12, padding: "14px 16px", textAlign: "center", borderTop: `3px solid ${s.c}` }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.c }}>{s.n}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>
      <div className="glass" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <table className="hrip-table">
          <thead><tr><th>Medicine</th><th>Category</th><th>Stock vs Min</th><th>Units</th><th>Status</th></tr></thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No inventory data available</td>
              </tr>
            ) : items.map((item: any) => {
              const pct = item.min ? Math.round(item.stock / item.min * 100) : 0;
              return (
                <tr key={item.name}>
                  <td><strong>{item.name}</strong></td>
                  <td style={{ color: "var(--text-secondary)" }}>{item.category}</td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{ width: 80 }}><div className="progress-bar"><div className="progress-fill" style={{ width: `${Math.min(pct,100)}%`, background: STATUS_COLOR[item.status] }} /></div></div>
                      <span style={{ fontSize: 12, fontWeight: 600, color: STATUS_COLOR[item.status] }}>{item.stock}/{item.min}</span>
                    </div>
                  </td>
                  <td style={{ color: "var(--text-muted)", fontSize: 13 }}>{item.unit}</td>
                  <td><span className={`badge-${item.status === "normal" ? "low" : item.status}`} style={{ borderRadius: 6, padding: "3px 8px", fontSize: 11, fontWeight: 600 }}>{item.status.toUpperCase()}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
