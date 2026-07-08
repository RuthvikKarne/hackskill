"use client";
import { useState } from "react";

import { useRecommendations, useApproveRecommendation, useRejectRecommendation, Recommendation } from "@/lib/queries";

const RISK_COLORS: Record<string, string> = {
  critical: "#ef4444", high: "#f59e0b", moderate: "#3b82f6", low: "#10b981",
};
const CAT_ICONS: Record<string, string> = {
  RISK: "🎯", FORECASTING: "📈", OPTIMIZATION: "⚡", SURVEILLANCE: "🔬",
};

export default function RecommendationsPage() {
  const { data: recs = [], isLoading, isError } = useRecommendations();
  const approveMutation = useApproveRecommendation();
  const rejectMutation = useRejectRecommendation();

  const [expanded, setExpanded] = useState<string | null>(null);
  const [filter, setFilter] = useState<Recommendation["status"] | "ALL">("ALL");

  const handleApprove = async (id: string) => {
    approveMutation.mutate(id);
  };

  const handleReject = async (id: string) => {
    const reason = window.prompt("Reason for rejection (required):");
    if (!reason) return;
    rejectMutation.mutate({ id, reason });
  };

  const shown = filter === "ALL" ? recs : recs.filter(r => r.status === filter);
  const pending = recs.filter(r => r.status === "PENDING").length;

  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>AI Recommendations</h1>
            <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Human-in-the-loop approval workflow · All AI actions require your approval</p>
          </div>
          {pending > 0 && (
            <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: "8px 16px", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ef4444", display: "inline-block", animation: "pulse-ring 1.5s ease-out infinite" }} />
              <span style={{ fontSize: 14, color: "#f87171", fontWeight: 600 }}>{pending} awaiting approval</span>
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-secondary)" }}>
          <div style={{ display: "inline-block", width: 24, height: 24, border: "2px solid rgba(139,92,246,0.3)", borderTopColor: "#8b5cf6", borderRadius: "50%", animation: "spin-slow 0.8s linear infinite", marginBottom: 16 }} />
          <div>Loading AI recommendations...</div>
        </div>
      ) : isError ? (
        <div style={{ padding: "40px", background: "rgba(239,68,68,0.1)", borderRadius: 12, color: "#f87171", textAlign: "center" }}>
          Failed to load recommendations. Please try again.
        </div>
      ) : (
        <>
          {/* Stats row */}
      <div className="animate-fade-in-up stagger-1" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Pending", count: recs.filter(r => r.status === "PENDING").length, color: "#f59e0b" },
          { label: "Approved", count: recs.filter(r => r.status === "APPROVED").length, color: "#10b981" },
          { label: "Rejected", count: recs.filter(r => r.status === "REJECTED").length, color: "#6b7280" },
        ].map(s => (
          <div key={s.label} className="glass" style={{ borderRadius: 12, padding: "14px 16px", textAlign: "center", borderTop: `3px solid ${s.color}` }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.count}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div style={{ display: "flex", gap: 8, marginBottom: 18 }}>
        {(["ALL", "PENDING", "APPROVED", "REJECTED"] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            background: filter === f ? "rgba(59,130,246,0.15)" : "var(--bg-card)",
            border: `1px solid ${filter === f ? "rgba(59,130,246,0.4)" : "var(--border)"}`,
            borderRadius: 20, padding: "5px 14px", fontSize: 12, cursor: "pointer",
            color: filter === f ? "#60a5fa" : "var(--text-secondary)", fontWeight: filter === f ? 600 : 400,
          }}>{f}</button>
        ))}
      </div>

      {/* Recommendation cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {shown.map((rec, i) => (
          <div key={rec.id} className={`glass animate-fade-in-up stagger-${Math.min(i + 1, 5)}`} style={{
            borderRadius: 16, overflow: "hidden",
            borderLeft: `4px solid ${RISK_COLORS[rec.risk_level]}`,
            opacity: rec.status !== "PENDING" ? 0.65 : 1,
          }}>
            {/* Header */}
            <div style={{ padding: "18px 20px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: 18 }}>{CAT_ICONS[rec.category]}</span>
                  <span style={{ fontSize: 11, background: "rgba(255,255,255,0.06)", border: "1px solid var(--border)", borderRadius: 6, padding: "2px 8px", color: "var(--text-secondary)", fontWeight: 600 }}>
                    {rec.category}
                  </span>
                  <span className={`badge-${rec.risk_level}`} style={{ borderRadius: 6, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>
                    {rec.risk_level.toUpperCase()}
                  </span>
                  {rec.status !== "PENDING" && (
                    <span style={{ fontSize: 11, background: rec.status === "APPROVED" ? "rgba(16,185,129,0.15)" : "rgba(107,114,128,0.15)", border: `1px solid ${rec.status === "APPROVED" ? "rgba(16,185,129,0.3)" : "rgba(107,114,128,0.3)"}`, borderRadius: 6, padding: "2px 8px", color: rec.status === "APPROVED" ? "#34d399" : "#9ca3af", fontWeight: 600 }}>
                      {rec.status === "APPROVED" ? "✓ APPROVED" : "✕ REJECTED"}
                    </span>
                  )}
                </div>
                <h3 style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{rec.title}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5, marginBottom: 8 }}>{rec.description}</p>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  🏥 {rec.hospitalName} · Model confidence: <span style={{ color: "#60a5fa", fontWeight: 600 }}>{(rec.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              {rec.status === "PENDING" && (
                <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                  <button
                    className="btn-success"
                    onClick={() => handleApprove(rec.id)}
                    disabled={approveMutation.isPending}
                  >
                    {approveMutation.isPending ? "…" : "✓ Approve"}
                  </button>
                  <button
                    className="btn-danger"
                    onClick={() => handleReject(rec.id)}
                    disabled={rejectMutation.isPending}
                  >
                    ✕ Reject
                  </button>
                </div>
              )}
            </div>

            {/* Action items */}
            <div style={{ padding: "0 20px 14px" }}>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {rec.action_items.map((item, idx) => (
                  <div key={idx} style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)", borderRadius: 8, padding: "6px 10px", fontSize: 12, color: "var(--text-secondary)" }}>
                    {idx + 1}. {item}
                  </div>
                ))}
              </div>
            </div>

            {/* SHAP Explainability panel */}
            {rec.explanation && (
              <div>
                <button
                  onClick={() => setExpanded(expanded === rec.id ? null : rec.id)}
                  style={{ width: "100%", padding: "10px 20px", background: "rgba(255,255,255,0.02)", border: "none", borderTop: "1px solid var(--border)", cursor: "pointer", textAlign: "left", display: "flex", alignItems: "center", gap: 8, color: "var(--text-secondary)", fontSize: 12, fontWeight: 600 }}
                >
                  <span>✨</span>
                  <span>SHAP Explanation · {rec.explanation.model_name}</span>
                  <span style={{ marginLeft: "auto" }}>{expanded === rec.id ? "▲" : "▼"}</span>
                </button>
                {expanded === rec.id && (
                  <div className="animate-fade-in" style={{ padding: "16px 20px", background: "rgba(139,92,246,0.04)", borderTop: "1px solid rgba(139,92,246,0.1)" }}>
                    <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 16 }}>
                      {rec.explanation.summary_text}
                    </p>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {rec.explanation.features.map((f) => (
                        <div key={f.feature_name} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <span style={{ fontSize: 11, color: "var(--text-muted)", width: 20, textAlign: "right" }}>#{f.importance_rank}</span>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>{f.feature_name.replace(/_/g, " ")}</span>
                              <span style={{ fontSize: 12, color: "#a78bfa", fontWeight: 700 }}>SHAP: {f.shap_value.toFixed(3)}</span>
                            </div>
                            <div className="progress-bar">
                              <div className="progress-fill" style={{ width: `${Math.min(f.shap_value / 0.35 * 100, 100)}%`, background: "linear-gradient(90deg,#8b5cf6,#3b82f6)" }} />
                            </div>
                            <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{f.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      </>
      )}
    </div>
  );
}
