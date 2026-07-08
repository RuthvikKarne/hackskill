export default function VendorInventoryPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>Vendor Inventory</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Manage your internal warehouse stock levels before dispatch</p>
      </div>
      
      <div className="glass animate-fade-in-up stagger-1" style={{ borderRadius: 16, padding: "40px 22px", textAlign: "center" }}>
        <div style={{ fontSize: 40, marginBottom: 16 }}>📦</div>
        <h3 style={{ fontWeight: 700, fontSize: 16, marginBottom: 8 }}>Warehouse Inventory Module</h3>
        <p style={{ color: "var(--text-secondary)", fontSize: 14, maxWidth: 400, margin: "0 auto" }}>
          This module tracks your internal supply stock levels. It is currently in development for the next phase of the hackathon.
        </p>
      </div>
    </div>
  );
}
