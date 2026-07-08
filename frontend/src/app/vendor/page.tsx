"use client";
import { useState, useEffect } from "react";
import { createClient } from "@/utils/supabase/client";

export default function VendorDashboard() {
  const [orders, setOrders] = useState<any[]>([]);
  
  useEffect(() => {
    async function fetchOrders() {
      const supabase = createClient();
      const { data } = await supabase
        .from("vendor_orders")
        .select(`id, item_name, quantity, priority, status, hospitals(name)`)
        .order("order_date", { ascending: false });

      if (data) {
        setOrders(data.map(o => ({
          id: `ORD-${o.id.split('-')[0].toUpperCase()}`,
          hospital: (o.hospitals as any)?.name || "Unknown",
          item: `${o.quantity}x ${o.item_name}`,
          priority: o.priority,
          status: o.status
        })));
      }
    }
    fetchOrders();
  }, []);

  const pending = orders.filter(o => o.status === "Pending").length;
  const enRoute = orders.filter(o => o.status === "Dispatched").length;
  // Simulating low stock alerts from the network
  const lowStock = 1;

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Vendor Supply Dashboard</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Manage hospital orders, dispatch logistics, and track inventory stock</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 30 }}>
        <div className="glass animate-fade-in-up stagger-1" style={{ borderRadius: 14, padding: "20px 22px", borderTop: "3px solid #10b981" }}>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", marginBottom: 8 }}>Pending Orders</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#10b981" }}>{pending}</div>
        </div>
        <div className="glass animate-fade-in-up stagger-2" style={{ borderRadius: 14, padding: "20px 22px", borderTop: "3px solid #3b82f6" }}>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", marginBottom: 8 }}>En-Route Deliveries</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#3b82f6" }}>{enRoute}</div>
        </div>
        <div className="glass animate-fade-in-up stagger-3" style={{ borderRadius: 14, padding: "20px 22px", borderTop: "3px solid #f59e0b" }}>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", marginBottom: 8 }}>Low Stock Alerts</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: "#f59e0b" }}>{lowStock}</div>
        </div>
      </div>

      <div className="glass animate-fade-in-up stagger-4" style={{ borderRadius: 16, padding: "20px 22px" }}>
        <h3 style={{ fontWeight: 700, fontSize: 16, marginBottom: 16 }}>Active Hospital Orders</h3>
        <table className="hrip-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Hospital</th>
              <th>Items</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "20px 0" }}>No pending orders from hospitals</td>
              </tr>
            ) : orders.map(o => (
              <tr key={o.id}>
                <td><strong>{o.id}</strong></td>
                <td>{o.hospital}</td>
                <td>{o.item}</td>
                <td>
                  <span style={{ color: o.priority === "Critical" ? "#ef4444" : o.priority === "Urgent" ? "#f59e0b" : "#3b82f6", fontWeight: 700 }}>
                    {o.priority}
                  </span>
                </td>
                <td>
                  <span style={{
                    fontSize: 12, fontWeight: 600, borderRadius: 6, padding: "3px 8px",
                    background: o.status === "Pending" ? "rgba(245,158,11,0.15)" : o.status === "Dispatched" ? "rgba(59,130,246,0.15)" : "rgba(16,185,129,0.15)",
                    color: o.status === "Pending" ? "#f59e0b" : o.status === "Dispatched" ? "#60a5fa" : "#34d399",
                  }}>{o.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
