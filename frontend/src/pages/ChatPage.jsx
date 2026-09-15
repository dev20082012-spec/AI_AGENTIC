import React, { useState, useEffect, useRef } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useChat } from "../context/ChatContext";
import { API_BASE } from "../config";
import {
  ArrowLeft,
  Send,
  Loader2,
  TrendingUp,
  CalendarClock,
  Megaphone,
  Trash2,
  Bot,
  User,
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  Square,
  Activity,
  CheckCircle2,
  History,
  BarChart3,
  X,
  Server,
  Zap,
} from "lucide-react";

const SPECIALIST_META = {
  executive: {
    name: "Chief of Staff",
    shortName: "Executive AI",
    role: "Conversational Executive Chief of Staff & Multi-Agent Coordinator",
    icon: Sparkles,
    accent: "indigo",
    borderGlow: "border-indigo-500/40",
    bgBadge: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
    userBubble: "bg-indigo-950/40 border-indigo-700/50 text-indigo-100",
    agentBubble: "bg-slate-900 border-slate-800 text-slate-100",
    starters: [
      "How are sales performing across our products?",
      "Why is BetaSuite growing while AlphaApp dominates volume?",
      "Which operational tasks are currently blocked or stale?",
      "Could operations be contributing to any product bottlenecks?",
      "What should I focus on this week across all departments?",
    ],
  },
  finance: {
    name: "Finance Specialist",
    shortName: "Finance",
    role: "Financial Analyst & Revenue Strategist",
    icon: TrendingUp,
    accent: "teal",
    borderGlow: "border-teal-500/30",
    bgBadge: "bg-teal-500/10 text-teal-400 border-teal-500/20",
    userBubble: "bg-teal-950/40 border-teal-700/50 text-teal-100",
    agentBubble: "bg-slate-900 border-slate-800 text-slate-100",
    starters: [
      "What's our revenue trend across product lines?",
      "Are there any financial anomalies or spikes I should know about?",
      "What is the 3-month forecast for AlphaApp vs BetaSuite?",
    ],
  },
  ops: {
    name: "Operations Specialist",
    shortName: "Operations",
    role: "Chief Operating Analyst & Workflow Coordinator",
    icon: CalendarClock,
    accent: "cyan",
    borderGlow: "border-cyan-500/30",
    bgBadge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    userBubble: "bg-cyan-950/40 border-cyan-700/50 text-cyan-100",
    agentBubble: "bg-slate-900 border-slate-800 text-slate-100",
    starters: [
      "Which operational tasks are currently blocked or stale?",
      "What are the high-priority items requiring escalation?",
      "Draft a sync email to Priya Patel regarding the board roadmap.",
    ],
  },
  marketing: {
    name: "Marketing Specialist",
    shortName: "Marketing",
    role: "Growth Marketer & Campaign Attribution Lead",
    icon: Megaphone,
    accent: "emerald",
    borderGlow: "border-emerald-500/30",
    bgBadge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    userBubble: "bg-emerald-950/40 border-emerald-700/50 text-emerald-100",
    agentBubble: "bg-slate-900 border-slate-800 text-slate-100",
    starters: [
      "How did our last ad campaign perform overall?",
      "Which age demographic and region had the highest conversion ROI?",
      "What recommendations do you have for reallocating our ad budget?",
    ],
  },
};

export default function ChatPage() {
  const { specialist } = useParams();
  const navigate = useNavigate();
  const {
    conversations,
    addMessage,
    clearHistory,
    threads,
    activeThreadId,
    switchThread,
    newThread,
  } = useChat();

  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamStatus, setStreamStatus] = useState("");
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingSpecialists, setStreamingSpecialists] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const [diagnosticsOpen, setDiagnosticsOpen] = useState(false);
  const [diagnosticsData, setDiagnosticsData] = useState(null);
  const [threadsOpen, setThreadsOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const requestIdRef = useRef(0);
  const abortControllerRef = useRef(null);

  const meta = SPECIALIST_META[specialist];
  const history = (conversations && conversations[specialist]) || [];

  useEffect(() => {
    if (!meta) {
      navigate("/");
    }
  }, [specialist, meta, navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading, streamingContent, streamStatus]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [specialist]);

  if (!meta) return null;

  const Icon = meta.icon;

  const formatTimestamp = () => {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const loadDiagnostics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/observability`);
      if (res.ok) {
        const d = await res.json();
        setDiagnosticsData(d);
      }
    } catch (e) {}
    setDiagnosticsOpen(true);
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (streamingContent.trim()) {
      addMessage(specialist, {
        role: "assistant",
        content: streamingContent + " *(generation stopped)*",
        timestamp: formatTimestamp(),
        specialists_used: streamingSpecialists,
      });
    }
    setLoading(false);
    setStreamingContent("");
    setStreamStatus("");
  };

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputValue).trim();
    if (!text || loading) return;

    const currentRequestId = ++requestIdRef.current;
    setInputValue("");
    setStreamingContent("");
    setStreamStatus("Analyzing inquiry...");
    setStreamingSpecialists([]);

    const timestamp = formatTimestamp();
    const historySnapshot = [...history];

    const userMsg = { role: "user", content: text, timestamp };
    addMessage(specialist, userMsg);
    setLoading(true);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    if (specialist === "executive") {
      try {
        const response = await fetch(`${API_BASE}/api/chat/executive/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            history: historySnapshot,
          }),
          signal: abortController.signal,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || `Server error (${response.status})`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulated = "";
        let usedSpecs = [];
        let finalMeta = {};

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const parsed = JSON.parse(line.slice(6));
                if (parsed.event === "status") {
                  setStreamStatus(parsed.text || "");
                } else if (parsed.event === "specialist") {
                  usedSpecs = parsed.specialists || [];
                  setStreamingSpecialists(usedSpecs);
                } else if (parsed.event === "token") {
                  accumulated += parsed.delta;
                  setStreamingContent(accumulated);
                } else if (parsed.event === "done") {
                  usedSpecs = parsed.specialists_used || usedSpecs;
                  finalMeta = parsed.metadata || {};
                }
              } catch (e) {
                // Ignore chunk parse errors
              }
            }
          }
        }

        if (currentRequestId === requestIdRef.current && accumulated.trim()) {
          addMessage(specialist, {
            role: "assistant",
            content: accumulated,
            timestamp: formatTimestamp(),
            specialists_used: usedSpecs,
            metadata: finalMeta,
          });
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        if (currentRequestId === requestIdRef.current) {
          addMessage(specialist, {
            role: "assistant",
            isError: true,
            failedQuery: text,
            content: `**Error:** Failed to connect with ${meta.name}. (${err.message}).`,
            timestamp: formatTimestamp(),
          });
        }
      } finally {
        if (currentRequestId === requestIdRef.current) {
          setLoading(false);
          setStreamingContent("");
          setStreamStatus("");
          abortControllerRef.current = null;
        }
      }
    } else {
      try {
        const response = await fetch(`${API_BASE}/api/chat/${specialist}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            history: historySnapshot,
          }),
          signal: abortController.signal,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || `Server error (${response.status})`);
        }

        const data = await response.json();

        if (currentRequestId === requestIdRef.current) {
          addMessage(specialist, {
            role: "assistant",
            content: data.response || "No response received.",
            timestamp: formatTimestamp(),
            specialists_used: data.specialists_used || [],
            metadata: data.metadata || {},
          });
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        if (currentRequestId === requestIdRef.current) {
          addMessage(specialist, {
            role: "assistant",
            isError: true,
            failedQuery: text,
            content: `**Error:** Failed to receive response from ${meta.name}. (${err.message}).`,
            timestamp: formatTimestamp(),
          });
        }
      } finally {
        if (currentRequestId === requestIdRef.current) {
          setLoading(false);
          abortControllerRef.current = null;
        }
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="flex flex-col h-screen bg-[#080c14] text-slate-100 font-sans relative">
      {/* Top Header */}
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-4">
          <Link
            to="/"
            className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800 text-slate-300 hover:text-white transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Executive Hub</span>
          </Link>

          <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

          <div className="flex items-center gap-3">
            <div className={`w-9 h-9 rounded-xl bg-slate-900 border ${meta.borderGlow} flex items-center justify-center`}>
              <Icon className="w-5 h-5 text-current" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold text-white">{meta.name}</h1>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${meta.bgBadge}`}>
                  {meta.shortName}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{meta.role}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Threads Toggle */}
          {specialist === "executive" && (
            <button
              onClick={() => setThreadsOpen(!threadsOpen)}
              className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
            >
              <History className="w-3.5 h-3.5 text-indigo-400" />
              <span className="hidden sm:inline">Threads ({threads.length})</span>
            </button>
          )}

          {/* System Diagnostics Button */}
          <button
            onClick={loadDiagnostics}
            title="System Diagnostics & Observability"
            className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            <Activity className="w-3.5 h-3.5 text-teal-400" />
            <span className="hidden sm:inline">Diagnostics</span>
          </button>

          {history.length > 0 && (
            <button
              onClick={() => newThread(specialist)}
              title="Reset and start new conversation"
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-400 px-2.5 py-1.5 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Thread</span>
            </button>
          )}

          <div className="flex items-center gap-1.5 text-xs text-emerald-400 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Active</span>
          </div>
        </div>
      </header>

      {/* Threads Drawer / Dropdown */}
      {threadsOpen && (
        <div className="absolute top-16 right-6 w-80 max-h-96 rounded-2xl bg-slate-950 border border-slate-800 p-4 shadow-2xl z-40 overflow-y-auto space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
            <span className="font-bold text-white flex items-center gap-1.5">
              <History className="w-3.5 h-3.5 text-indigo-400" />
              Saved Threads
            </span>
            <button
              onClick={() => setThreadsOpen(false)}
              className="text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {threads.length === 0 ? (
            <p className="text-xs text-slate-500 italic text-center py-4">
              No previous threads saved yet.
            </p>
          ) : (
            <div className="space-y-2">
              {threads.map((t) => (
                <button
                  key={t.thread_id}
                  onClick={() => {
                    switchThread(t.thread_id, specialist);
                    setThreadsOpen(false);
                  }}
                  className={`w-full text-left p-2.5 rounded-xl border text-xs transition-all ${
                    activeThreadId === t.thread_id
                      ? "bg-indigo-950/50 border-indigo-500/40 text-indigo-200"
                      : "bg-slate-900/60 border-slate-800/80 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <div className="font-semibold truncate">{t.title}</div>
                  <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                    <span>{t.message_count} messages</span>
                    <span>{new Date(t.updated_at).toLocaleDateString()}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Diagnostics Modal */}
      {diagnosticsOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 max-w-2xl w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-teal-400" />
                <h3 className="text-sm font-bold text-white">System Observability & Telemetry</h3>
              </div>
              <button
                onClick={() => setDiagnosticsOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {diagnosticsData ? (
              <div className="space-y-4 text-xs">
                {/* 4 Stat Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Requests</span>
                    <span className="text-lg font-black text-white">{diagnosticsData.summary?.total_requests || 0}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Success Rate</span>
                    <span className="text-lg font-black text-emerald-400">{diagnosticsData.summary?.success_rate_pct || 100}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Avg Latency</span>
                    <span className="text-lg font-black text-teal-400">{diagnosticsData.summary?.avg_latency_ms || 0} ms</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Failovers</span>
                    <span className="text-lg font-black text-amber-400">{diagnosticsData.summary?.fallback_invocations || 0}</span>
                  </div>
                </div>

                {/* Specialist & Provider Distribution */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Specialist Invocations</span>
                    <div className="flex justify-between text-slate-300">
                      <span>Finance:</span>
                      <span className="font-bold text-teal-400">{diagnosticsData.specialist_distribution?.finance || 0}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Operations:</span>
                      <span className="font-bold text-cyan-400">{diagnosticsData.specialist_distribution?.ops || 0}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Marketing:</span>
                      <span className="font-bold text-emerald-400">{diagnosticsData.specialist_distribution?.marketing || 0}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Active Providers</span>
                    <div className="flex justify-between text-slate-300">
                      <span>Groq Cloud (Primary):</span>
                      <span className="font-bold text-indigo-400">{diagnosticsData.provider_distribution?.groq || 0}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>OpenRouter (Fallback):</span>
                      <span className="font-bold text-amber-400">{diagnosticsData.provider_distribution?.openrouter || 0}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Rule-Based / Direct:</span>
                      <span className="font-bold text-slate-400">{diagnosticsData.provider_distribution?.direct || 0}</span>
                    </div>
                  </div>
                </div>

                {/* Recent Traces Table */}
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">Recent Execution Traces</span>
                  <div className="max-h-44 overflow-y-auto rounded-xl border border-slate-800 bg-slate-950">
                    <table className="w-full text-left text-[11px] text-slate-300">
                      <thead className="bg-slate-900/80 border-b border-slate-800 text-[10px] uppercase text-slate-400">
                        <tr>
                          <th className="p-2">Endpoint</th>
                          <th className="p-2">Intent</th>
                          <th className="p-2">Provider</th>
                          <th className="p-2">Latency</th>
                          <th className="p-2">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {(diagnosticsData.recent_traces || []).map((t, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/40">
                            <td className="p-2 font-mono text-slate-400">{t.endpoint}</td>
                            <td className="p-2 truncate max-w-[120px]">{t.intent}</td>
                            <td className="p-2">{t.provider}</td>
                            <td className="p-2">{t.latency_ms} ms</td>
                            <td className="p-2">
                              {t.success ? (
                                <span className="text-emerald-400 font-semibold">OK</span>
                              ) : (
                                <span className="text-rose-400 font-semibold">ERR</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6 text-slate-400 text-xs">
                <Loader2 className="w-6 h-6 animate-spin mx-auto text-teal-400 mb-2" />
                <span>Loading observability telemetry...</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chat Messages Area */}
      <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 max-w-4xl w-full mx-auto">
        {history.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6 my-auto">
            <div className={`w-16 h-16 rounded-2xl bg-slate-900/80 border ${meta.borderGlow} flex items-center justify-center shadow-xl`}>
              <Icon className="w-8 h-8 text-white" />
            </div>
            <div className="max-w-md">
              <h2 className="text-xl font-bold text-white mb-2">
                Consult with {meta.name}
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Persistent multi-turn conversational AI. State is preserved automatically across sessions with semantic context resolution.
              </p>
            </div>

            {/* Starter prompts */}
            <div className="w-full max-w-lg space-y-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block text-left">
                Suggested Inquiries:
              </span>
              <div className="grid gap-2">
                {meta.starters.map((starter, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(starter)}
                    className="w-full text-left text-xs text-slate-300 p-3 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/80 transition-all flex items-center justify-between group"
                  >
                    <span>{starter}</span>
                    <Sparkles className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 transition-colors shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          history.map((msg, idx) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={idx}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className={`w-8 h-8 rounded-lg bg-slate-900 border ${meta.borderGlow} flex items-center justify-center shrink-0 mt-0.5`}>
                    <Bot className="w-4 h-4 text-indigo-400" />
                  </div>
                )}

                <div
                  className={`relative group max-w-[85%] md:max-w-[75%] rounded-2xl p-4 text-xs md:text-sm leading-relaxed border shadow-md ${
                    isUser ? meta.userBubble : meta.agentBubble
                  }`}
                >
                  {/* Timestamp header */}
                  <div className="flex items-center justify-between gap-2 mb-1.5 text-[10px] text-slate-400">
                    <span className="font-semibold">{isUser ? "You" : meta.name}</span>
                    {msg.timestamp && <span>{msg.timestamp}</span>}
                  </div>

                  {isUser ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <>
                      {/* Safe Specialist Activity Badges */}
                      {msg.specialists_used && msg.specialists_used.length > 0 && (
                        <div className="flex items-center gap-1.5 mb-2.5 flex-wrap">
                          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Consulted:</span>
                          {msg.specialists_used.map((s) => {
                            const badgeStyle =
                              s === "finance" ? "bg-teal-500/15 text-teal-300 border-teal-500/30" :
                              s === "ops" ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30" :
                              s === "benchmarks" ? "bg-purple-500/15 text-purple-300 border-purple-500/30" :
                              "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
                            const label =
                              s === "finance" ? "Finance" :
                              s === "ops" ? "Operations" :
                              s === "benchmarks" ? "SaaS Benchmarks" : "Marketing";
                            return (
                              <span key={s} className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                                {label}
                              </span>
                            );
                          })}
                          {msg.metadata?.steps > 0 && (
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                              {msg.metadata.steps}-step analysis
                            </span>
                          )}
                        </div>
                      )}

                      <div className="prose prose-invert prose-xs md:prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0.5">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>

                      {/* Error Retry Option */}
                      {msg.isError && msg.failedQuery && (
                        <div className="mt-3 pt-2 border-t border-slate-800">
                          <button
                            onClick={() => handleSendMessage(msg.failedQuery)}
                            className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 px-3 py-1.5 rounded-lg transition-colors"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                            <span>Retry Request</span>
                          </button>
                        </div>
                      )}
                    </>
                  )}

                  {/* Copy button on hover */}
                  <button
                    onClick={() => handleCopy(msg.content, idx)}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white"
                    title="Copy message"
                  >
                    {copiedIndex === idx ? (
                      <Check className="w-3 h-3 text-emerald-400" />
                    ) : (
                      <Copy className="w-3 h-3" />
                    )}
                  </button>
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>
                )}
              </div>
            );
          })
        )}

        {/* Streaming / Loading Indicator Bubble */}
        {loading && (
          <div className="flex gap-3 justify-start items-start">
            <div className={`w-8 h-8 rounded-lg bg-slate-900 border ${meta.borderGlow} flex items-center justify-center shrink-0 mt-0.5`}>
              <Bot className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="rounded-2xl p-4 bg-slate-900 border border-slate-800 text-slate-200 text-xs md:text-sm max-w-[85%] md:max-w-[75%] space-y-3">
              {/* Status Header */}
              <div className="flex items-center gap-2 text-slate-400 text-xs">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                <span>{streamStatus || `${meta.shortName} is analyzing...`}</span>
              </div>

              {/* Streaming Content */}
              {streamingContent ? (
                <div className="prose prose-invert prose-xs md:prose-sm max-w-none">
                  <ReactMarkdown>{streamingContent}</ReactMarkdown>
                </div>
              ) : null}

              {/* Stop Generation Button */}
              <div className="pt-2">
                <button
                  onClick={handleStopStreaming}
                  className="inline-flex items-center gap-1.5 text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 px-3 py-1 rounded-lg transition-colors"
                >
                  <Square className="w-3 h-3 fill-current" />
                  <span>Stop Generation</span>
                </button>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Bottom Message Input Bar */}
      <footer className="border-t border-slate-800/80 bg-slate-950/90 p-4 backdrop-blur-md">
        <div className="max-w-4xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-end gap-3"
          >
            <div className="relative flex-1">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder={`Ask ${meta.name} anything... (Shift+Enter for newline)`}
                className="w-full resize-none rounded-xl bg-slate-900 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={!inputValue.trim() || loading}
              className="h-11 px-4 rounded-xl bg-indigo-500 hover:bg-indigo-400 disabled:opacity-40 disabled:hover:bg-indigo-500 text-slate-950 font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <span className="hidden sm:inline text-xs font-bold">Send</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
          <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 px-1">
            <span>Powered by Strands Agents &middot; Groq/OpenRouter Failover</span>
            <span>Server-synchronized & persisted</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
