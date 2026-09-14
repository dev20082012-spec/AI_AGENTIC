import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import {
  TrendingUp,
  CalendarClock,
  Megaphone,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  Layers,
  Activity,
  Cpu,
  ShieldCheck,
  Copy,
  Check,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const EXAMPLE_QUERIES = [
  {
    label: "Full Weekly Briefing",
    query: "Give me this week's briefing: revenue trend, pending ops items, and how our last campaign performed.",
  },
  {
    label: "Finance Only",
    query: "What is our current revenue trend and 3-month forecast across product lines?",
  },
  {
    label: "Operations Only",
    query: "Which operational tasks are currently blocked or stale and require CTO escalation?",
  },
  {
    label: "Marketing Only",
    query: "How did our last ad campaign perform across regions and age demographics?",
  },
];

const SPECIALIST_CONFIG = [
  {
    key: "finance",
    name: "Finance Specialist",
    icon: TrendingUp,
    role: "Revenue analytics, linear forecasting & 2-sigma anomaly detection",
    accent: "teal",
  },
  {
    key: "ops",
    name: "Operations Specialist",
    icon: CalendarClock,
    role: "Task status tracking, blocked bottleneck escalation & scheduling",
    accent: "cyan",
  },
  {
    key: "marketing",
    name: "Marketing Specialist",
    icon: Megaphone,
    role: "CTR & conversion attribution, demographic segmentation & ROI",
    accent: "emerald",
  },
];

export default function App() {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Staggered reveal state:
  // stage: 'idle' | 'analyzing' | 'revealing' | 'done'
  const [stage, setStage] = useState("idle");
  const [activeSpecialists, setActiveSpecialists] = useState({});
  const [revealedKeys, setRevealedKeys] = useState(new Set());
  const [briefingData, setBriefingData] = useState(null);
  const [showSynthesis, setShowSynthesis] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (overrideQuery) => {
    const q = (overrideQuery || query).trim();
    if (!q || isLoading) return;

    if (overrideQuery) {
      setQuery(overrideQuery);
    }

    setIsLoading(true);
    setError(null);
    setStage("analyzing");
    setRevealedKeys(new Set());
    setShowSynthesis(false);
    setBriefingData(null);
    setCopied(false);

    try {
      const resp = await fetch(`${API_BASE}/api/briefing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${resp.status})`);
      }

      const data = await resp.json();
      setBriefingData(data);
      setActiveSpecialists(data.specialist_results || {});
      setStage("revealing");

      // Staggered reveal logic
      const called = data.specialists_called || [];
      
      called.forEach((key, index) => {
        setTimeout(() => {
          setRevealedKeys((prev) => new Set([...prev, key]));
        }, (index + 1) * 800);
      });

      // Show final synthesis markdown card after all called specialists reveal
      const totalDelay = (called.length + 1) * 850;
      setTimeout(() => {
        setShowSynthesis(true);
        setStage("done");
        setIsLoading(false);
      }, totalDelay);

    } catch (err) {
      setError(err.message || "Unable to reach AGentic Resolve orchestrator.");
      setStage("idle");
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!briefingData?.synthesized_briefing) return;
    navigator.clipboard.writeText(briefingData.synthesized_briefing);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Layers className="w-5 h-5 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-200 to-teal-200">
                  AGentic Resolve
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                  Chief of Staff
                </span>
              </div>
              <p className="text-xs text-slate-400">Autonomous Multi-Agent Enterprise Orchestration</p>
            </div>
          </div>

          {/* Status indicators */}
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              <span>Strands Agents SDK</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span>3 Specialist Agents Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        
        {/* Hero / Query Section */}
        <section className="bg-gradient-to-b from-slate-900/90 to-slate-950/80 rounded-2xl border border-slate-800/80 p-6 md:p-8 shadow-xl shadow-black/40">
          <div className="max-w-3xl">
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">
              Ask your Executive Chief of Staff
            </h1>
            <p className="text-sm md:text-base text-slate-400 mb-6">
              The orchestrator dynamically routes your inquiry to specialized financial, operations, and marketing agents, synthesizing their domain findings into a unified executive briefing.
            </p>
          </div>

          {/* Search bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="flex flex-col sm:flex-row gap-3 items-stretch"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask AGentic Resolve (e.g. Give me this week's briefing on revenue, ops, and campaigns...)"
                disabled={isLoading}
                className="w-full bg-slate-950/90 border border-slate-700/80 rounded-xl px-4 py-3.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 transition-all disabled:opacity-60 shadow-inner"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-6 py-3.5 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-semibold rounded-xl text-sm transition-all shadow-lg shadow-teal-500/20 hover:shadow-teal-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shrink-0"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Orchestrating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Briefing</span>
                </>
              )}
            </button>
          </form>

          {/* Clickable Example Queries */}
          <div className="mt-4 pt-4 border-t border-slate-800/60 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              Try prompt:
            </span>
            {EXAMPLE_QUERIES.map((ex, i) => (
              <button
                key={i}
                type="button"
                disabled={isLoading}
                onClick={() => handleSubmit(ex.query)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-teal-300 border border-slate-700/50 hover:border-teal-500/40 transition-all text-left"
              >
                {ex.label}
              </button>
            ))}
          </div>
        </section>

        {/* Error Card */}
        {error && (
          <div className="bg-rose-950/30 border border-rose-800/60 rounded-xl p-5 flex items-start gap-4 text-rose-200 animate-fade-in shadow-lg">
            <AlertCircle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
            <div className="flex-1">
              <h3 className="font-semibold text-sm text-rose-300">Orchestration Error</h3>
              <p className="text-xs mt-1 text-rose-200/90">{error}</p>
            </div>
            <button
              onClick={() => handleSubmit()}
              className="px-3 py-1.5 bg-rose-900/60 hover:bg-rose-900 border border-rose-700/60 text-rose-100 rounded-lg text-xs font-medium transition-all"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Orchestration Status Banner */}
        {stage === "analyzing" && (
          <div className="flex items-center justify-center gap-3 py-3 px-4 bg-teal-950/20 border border-teal-800/30 rounded-xl text-teal-300 text-sm animate-pulse-subtle">
            <div className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-ping"></div>
            <span>Orchestrator is analysing your request and delegating to specialist sub-agents...</span>
          </div>
        )}

        {/* 3 Specialist Agents Cards Grid */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-teal-400" />
              Specialist Agent Delegation Layer
            </h2>
            <span className="text-xs text-slate-400">
              {stage === "idle"
                ? "Standing by for delegation"
                : stage === "analyzing"
                ? "Evaluating routing decision..."
                : `${briefingData?.specialists_called?.length || 0} specialist(s) dispatched`}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {SPECIALIST_CONFIG.map((spec) => {
              const Icon = spec.icon;
              const isPending = stage === "analyzing";
              const isCalled = briefingData?.specialists_called?.includes(spec.key);
              const isRevealed = revealedKeys.has(spec.key);
              const isDimmed = stage !== "idle" && stage !== "analyzing" && !isCalled;
              const summaryText = activeSpecialists[spec.key]?.summary;

              return (
                <div
                  key={spec.key}
                  className={`relative rounded-xl border p-5 flex flex-col transition-all duration-500 ${
                    isDimmed
                      ? "bg-slate-950/40 border-slate-900 opacity-40 grayscale"
                      : isRevealed
                      ? "bg-slate-900/90 border-teal-500/50 shadow-lg shadow-teal-950/30 ring-1 ring-teal-500/20"
                      : isPending
                      ? "bg-slate-900/50 border-slate-800 animate-pulse-subtle"
                      : "bg-slate-900/60 border-slate-800/80 hover:border-slate-700"
                  }`}
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
                          isRevealed
                            ? "bg-teal-500/20 text-teal-300 border border-teal-500/30"
                            : isPending
                            ? "bg-slate-800 text-slate-400"
                            : "bg-slate-800/80 text-slate-400"
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-sm text-slate-100">{spec.name}</h3>
                        <p className="text-[11px] text-slate-400 line-clamp-1">{spec.role}</p>
                      </div>
                    </div>

                    {/* Status Badge */}
                    {isRevealed && (
                      <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-300 border border-teal-500/30">
                        <CheckCircle2 className="w-3 h-3" />
                        Dispatched
                      </span>
                    )}
                    {isPending && (
                      <span className="flex items-center gap-1 text-[11px] text-slate-400 px-2 py-0.5 rounded-full bg-slate-800">
                        <Clock className="w-3 h-3 animate-spin" />
                        Routing...
                      </span>
                    )}
                    {isDimmed && (
                      <span className="text-[10px] text-slate-400 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        Not Needed
                      </span>
                    )}
                  </div>

                  {/* Card Body */}
                  <div className="flex-1 mt-2 text-xs">
                    {isRevealed && summaryText ? (
                      <div className="text-slate-300 space-y-1.5 animate-fade-in bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                        {summaryText}
                      </div>
                    ) : isPending ? (
                      <div className="space-y-2 py-4">
                        <div className="h-2 bg-slate-800 rounded animate-pulse w-3/4"></div>
                        <div className="h-2 bg-slate-800 rounded animate-pulse w-5/6"></div>
                        <div className="h-2 bg-slate-800 rounded animate-pulse w-1/2"></div>
                      </div>
                    ) : isDimmed ? (
                      <div className="py-4 text-center text-slate-400 text-xs italic">
                        Orchestrator determined this specialist was not required for this query.
                      </div>
                    ) : (
                      <div className="py-3 text-slate-400 text-xs">
                        Ready to process domain-specific telemetry and historical trends upon orchestrator call.
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Synthesized Briefing Card */}
        {showSynthesis && briefingData?.synthesized_briefing && (
          <section className="bg-slate-900/95 border border-teal-500/40 rounded-2xl p-6 md:p-8 shadow-2xl shadow-teal-950/20 animate-fade-in space-y-6 ring-1 ring-teal-500/20">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-teal-500/20 text-teal-300 border border-teal-500/30 flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    Executive Briefing Synthesis
                  </h2>
                  <p className="text-xs text-slate-400">
                    Compiled from {briefingData.specialists_called?.length} specialist agent reports
                  </p>
                </div>
              </div>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-teal-400" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Markdown</span>
                  </>
                )}
              </button>
            </div>

            {/* Markdown Body */}
            <div className="prose prose-invert prose-teal max-w-none text-slate-200 text-sm leading-relaxed space-y-4">
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => (
                    <h1 className="text-xl font-bold text-teal-200 mt-4 mb-2 pb-1 border-b border-slate-800" {...props} />
                  ),
                  h2: ({ node, ...props }) => (
                    <h2 className="text-base font-semibold text-teal-300 mt-4 mb-2 flex items-center gap-2" {...props} />
                  ),
                  h3: ({ node, ...props }) => (
                    <h3 className="text-sm font-semibold text-slate-200 mt-3 mb-1" {...props} />
                  ),
                  ul: ({ node, ...props }) => (
                    <ul className="list-disc list-inside space-y-1 my-2 text-slate-300" {...props} />
                  ),
                  li: ({ node, ...props }) => (
                    <li className="text-slate-300" {...props} />
                  ),
                  strong: ({ node, ...props }) => (
                    <strong className="font-semibold text-white" {...props} />
                  ),
                  p: ({ node, ...props }) => (
                    <p className="my-1.5 leading-relaxed" {...props} />
                  ),
                  hr: () => (
                    <hr className="my-4 border-slate-800" />
                  ),
                }}
              >
                {briefingData.synthesized_briefing}
              </ReactMarkdown>
            </div>
          </section>
        )}
      </main>

      {/* Persistent Footer */}
      <footer className="border-t border-slate-800/60 bg-slate-950 py-4 px-6 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-400"></span>
            <span>Built with <strong>Strands Agents SDK</strong> &middot; Agents for Humans Hackathon</span>
          </div>
          <div>
            <span>Architecture: Multi-Agent Orchestrator (Agents-as-Tools Pattern)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
