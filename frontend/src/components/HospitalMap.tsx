"use client";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";

interface Hospital {
  id: string; name: string; city: string; lat: number; lng: number;
  occupancy: number; stock: number; risk: number; level: string;
}

const RISK_COLORS: Record<string, string> = {
  critical: "#ef4444", high: "#f59e0b", moderate: "#3b82f6", low: "#10b981",
};

interface Props {
  hospitals: Hospital[];
  selected?: string;
  onSelect: (id: string) => void;
}

export default function HospitalMap({ hospitals, selected, onSelect }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  if (!mounted) return null;

  const center: [number, number] = [28.6139, 77.2090];

  return (
    <div style={{ borderRadius: 16, overflow: "hidden", border: "1px solid var(--border)", height: 420 }}>
      <MapContainer
        center={center}
        zoom={8}
        style={{ height: "100%", width: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution=""
        />
        {hospitals.map((h) => (
          <CircleMarker
            key={h.id}
            center={[h.lat, h.lng]}
            radius={selected === h.id ? 22 : 16}
            fillColor={RISK_COLORS[h.level]}
            color={selected === h.id ? "white" : RISK_COLORS[h.level]}
            weight={selected === h.id ? 3 : 2}
            opacity={1}
            fillOpacity={0.85}
            eventHandlers={{ click: () => onSelect(h.id) }}
          >
            <Tooltip permanent={false} direction="top" offset={[0, -10]}>
              <div style={{ minWidth: 160 }}>
                <strong style={{ fontSize: 13 }}>{h.name}</strong><br />
                <span style={{ color: RISK_COLORS[h.level], fontWeight: 700 }}>
                  {h.level.toUpperCase()} RISK · {(h.risk * 100).toFixed(0)}%
                </span><br />
                <span style={{ fontSize: 12 }}>Beds: {(h.occupancy * 100).toFixed(0)}% occupied</span><br />
                <span style={{ fontSize: 12 }}>Stock: {(h.stock * 100).toFixed(0)}% remaining</span>
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div style={{
        position: "absolute", bottom: 16, left: 16, zIndex: 1000,
        background: "rgba(10,14,26,0.92)", border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 12, padding: "10px 14px",
        backdropFilter: "blur(12px)",
      }}>
        <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Risk Level</p>
        {Object.entries(RISK_COLORS).map(([level, color]) => (
          <div key={level} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: color }} />
            <span style={{ fontSize: 12, color: "var(--text-secondary)", textTransform: "capitalize" }}>{level}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
