"use client";
import { useState, useRef, useEffect } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";

interface Message {
  role: "user" | "model";
  text: string;
}

// Context fed to Gemini about the current system state
const HEAL_CONTEXT = `
You are HEAL AI Assistant — an intelligent healthcare resource management copilot powered by Google Gemini.
You have real-time access to the following healthcare district data:

HOSPITALS:
- Aster General Hospital (Kigali): Bed occupancy 92% [CRITICAL], Stock shortage 20%, Wait time 85min, Risk Score 0.74
- Cedar Community Clinic (Kigali): Bed occupancy 55% [NORMAL], Stock shortage 8%, Wait time 22min, Risk Score 0.22
- Moringa Teaching Hospital (Butare): Bed occupancy 83% [HIGH], Stock shortage 35%, Wait time 64min, Risk Score 0.51

ACTIVE AI RECOMMENDATIONS (awaiting human approval):
1. [CRITICAL] Aster General: Open emergency overflow ward — 92% occupancy
2. [HIGH] Moringa Teaching: Medicine redistribution — Paracetamol stock at 12%
3. [MODERATE] District-wide: Patient surge forecast +35% in 72 hours

DISEASE SURVEILLANCE:
- Kigali district: Moderate risk (score 0.41), 127 confirmed cases, 8% daily growth
- Huye district: Low risk (score 0.19), 23 confirmed cases

FORECASTS:
- Patient load next 7 days: avg 138/day (+15% vs last week)
- Medicine demand next 30 days: Paracetamol 2,400 units needed

SYSTEM STATUS: All services online. Last updated: ${new Date().toLocaleTimeString()}

You help healthcare administrators make decisions, understand AI recommendations, and manage resources efficiently.
Be concise, actionable, and empathetic to healthcare context. Use bullet points for lists.
`;

interface Props {
  onClose: () => void;
}

export default function AskHRIP({ onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "model",
      text: "👋 Hi! I'm your HEAL AI Assistant powered by Gemini.\n\nI have real-time access to your hospital data, AI recommendations, and health surveillance. What would you like to know?\n\nTry asking:\n• *\"What should I prioritize today?\"*\n• *\"Why is Aster hospital at critical risk?\"*\n• *\"Summarize the disease situation\"*",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState(process.env.NEXT_PUBLIC_GEMINI_API_KEY || "");
  const [showKeyInput, setShowKeyInput] = useState(!process.env.NEXT_PUBLIC_GEMINI_API_KEY);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    if (!apiKey) { setShowKeyInput(true); return; }

    const userMsg: Message = { role: "user", text: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const genAI = new GoogleGenerativeAI(apiKey);
      const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

      const chat = model.startChat({
        history: [
          { role: "user", parts: [{ text: HEAL_CONTEXT }] },
          { role: "model", parts: [{ text: "I understand the HEAL system context. I'm ready to assist with healthcare resource management queries." }] },
          ...messages.map((m) => ({
            role: m.role,
            parts: [{ text: m.text }],
          })),
        ],
        generationConfig: {
          temperature: 0.1, // Highly deterministic for factual healthcare data
          topK: 40,
        },
      });

      const result = await chat.sendMessageStream(userMsg.text);
      
      // Add empty model message to be populated by stream
      setMessages((prev) => [...prev, { role: "model", text: "" }]);
      
      let streamedText = "";
      for await (const chunk of result.stream) {
        streamedText += chunk.text();
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "model", text: streamedText };
          return updated;
        });
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [...prev, {
        role: "model",
        text: `⚠️ Error connecting to Gemini: ${errorMsg}. Please check your API key.`,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "What should I prioritize today?",
    "Summarize hospital risks",
    "Explain the AI recommendations",
    "Disease surveillance update",
  ];

  return (
    <div className="glass" style={{
      height: "100%", borderRadius: 20, display: "flex", flexDirection: "column",
      border: "1px solid rgba(139,92,246,0.3)",
      boxShadow: "0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(139,92,246,0.1)",
    }}>
      {/* Header */}
      <div style={{
        padding: "16px 18px", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "linear-gradient(90deg, rgba(139,92,246,0.1), rgba(59,130,246,0.05))",
        borderRadius: "20px 20px 0 0",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg, #8b5cf6, #3b82f6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18, boxShadow: "0 4px 12px rgba(139,92,246,0.4)",
          }}>✨</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 15 }}>Ask HEAL</div>
            <div style={{ fontSize: 11, color: "#a78bfa" }}>Powered by Google Gemini</div>
          </div>
        </div>
        <button onClick={onClose} className="btn-ghost" style={{ padding: "4px 10px", fontSize: 16 }}>✕</button>
      </div>

      {/* API key setup */}
      {showKeyInput && (
        <div style={{ padding: "12px 16px", background: "rgba(59,130,246,0.08)", borderBottom: "1px solid var(--border)" }}>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8 }}>
            Enter your Gemini API key (get free at <a href="https://aistudio.google.com" target="_blank" rel="noreferrer" style={{ color: "#60a5fa" }}>aistudio.google.com</a>):
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              className="hrip-input"
              type="password"
              placeholder="AIza..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              style={{ fontSize: 13 }}
            />
            <button className="btn-primary" onClick={() => setShowKeyInput(false)} style={{ whiteSpace: "nowrap", fontSize: 13 }}>
              Save
            </button>
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "16px", display: "flex", flexDirection: "column", gap: 10 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
            {msg.role === "model" && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <div style={{ width: 20, height: 20, borderRadius: 6, background: "linear-gradient(135deg,#8b5cf6,#3b82f6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10 }}>✨</div>
                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>HEAL AI</span>
              </div>
            )}
            <div className={msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}>
              <p style={{ whiteSpace: "pre-wrap", lineHeight: 1.6, margin: 0 }}>{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: 4, padding: "10px 14px", background: "rgba(255,255,255,0.04)", borderRadius: 12, width: "fit-content" }}>
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick prompts */}
      <div style={{ padding: "0 12px 8px", display: "flex", gap: 6, flexWrap: "wrap" }}>
        {quickPrompts.map((p) => (
          <button key={p} onClick={() => { setInput(p); }} style={{
            background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)",
            borderRadius: 12, padding: "4px 10px", fontSize: 11, color: "var(--text-secondary)", cursor: "pointer",
            transition: "all 0.15s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.borderColor = "rgba(139,92,246,0.4)")}
          onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
          >{p}</button>
        ))}
      </div>

      {/* Input */}
      <div style={{ padding: "8px 12px 12px", display: "flex", gap: 8 }}>
        <input
          className="hrip-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder="Ask about hospitals, risks, forecasts…"
          style={{ fontSize: 13, borderRadius: 12 }}
        />
        <button
          className="btn-primary"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{ padding: "10px 16px", borderRadius: 12, fontSize: 16, minWidth: 44 }}
        >
          ↑
        </button>
      </div>
    </div>
  );
}
