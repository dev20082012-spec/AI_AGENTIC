import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useChat } from "../context/ChatContext";
import { API_BASE } from "../config";
import {
  ArrowLeft,
  Sparkles,
  TrendingUp,
  CalendarClock,
  Megaphone,
  Loader2,
  Copy,
  Check,
  ShieldAlert,
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  FileDown,
  MessageSquare,
  Clock,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

const PRESET_QUERIES = [
  "Give me this week's executive briefing: revenue trend, pending ops items, and how our last campaign performed.",
  "Executive sync: Analyze 3-month sales forecast, critical operational blockers, and ad conversion ROI.",
];

export default function BriefingPage() {
  const navigate = useNavigate();
  const { addMessage } = useChat();

  const [query, setQuery] = useState(PRESET_QUERIES[0]);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [expandedEvidence, setExpandedEvidence] = useState({});

  const toggleEvidence = (spec) => {
    setExpandedEvidence((prev) => ({ ...prev, [spec]: !prev[spec] }));
  };

  const handleRunBriefing = async (queryToRun) => {
    const q = queryToRun || query;
    if (!q.trim() || loading) return;

    setLoading(true);
    setLoadingStep(1);
    setError(null);
    setResult(null);

    // Simulated progressive loading steps for executive feedback
    const t1 = setTimeout(() => setLoadingStep(2), 1200);
    const t2 = setTimeout(() => setLoadingStep(3), 3200);

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
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to execute executive briefing.");
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result?.synthesized_briefing) return;
    navigator.clipboard.writeText(result.synthesized_briefing);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `executive-briefing-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAskFollowUp = () => {
    if (!result) return;
    // Add briefing summary into executive chat context
    addMessage("executive", {
      role: "assistant",
      content: `### Executive Briefing Context (${new Date().toLocaleDateString()})\n\n${result.synthesized_briefing}\n\n*What specific follow-up questions or tactical decisions would you like to explore regarding this briefing?*`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      specialists_used: result.specialists_called || ["finance", "ops", "marketing"],
    });
    navigate("/chat/executive");
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 font-sans flex flex-col">
      {/* Top Header */}
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <Link
            to="/"
            className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800 text-slate-300 hover:text-white transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Executive Hub</span>
          </Link>

          <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white">Full Business Briefing</h1>
              <p className="text-[11px] text-slate-400">Multi-Agent Executive Synthesis & Cross-Department Audit</p>
            </div>
          </div>
        </div>

        {result && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleAskFollowUp}
              className="hidden sm:flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/25"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Discuss in Chat</span>
            </button>
          </div>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 space-y-6">
        {/* Purpose Explanation Banner */}
        <div className="rounded-2xl p-4 bg-gradient-to-r from-amber-500/10 via-slate-900 to-indigo-950/40 border border-amber-500/25 text-xs text-slate-300 flex items-start gap-3">
          <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-slate-100">Executive Report Workflow:</span>
            <p className="leading-relaxed text-slate-300">
              The Full Business Briefing simultaneously queries Finance (sales trajectories), Operations (blocked team milestones), and Marketing (campaign ROI). The top-level orchestrator analyzes cross-department correlations, surfaces vulnerabilities, and delivers prioritized executive recommendations.
            </p>
          </div>
        </div>

        {/* Search / Run Controls */}
        <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 shadow-xl space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Briefing Inquest Prompt
            </label>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRunBriefing()}
                placeholder="Enter executive briefing prompt..."
                className="flex-1 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
              />
              <button
                onClick={() => handleRunBriefing()}
                disabled={loading || !query.trim()}
                className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:hover:bg-amber-500 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-500/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Orchestrating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Run Briefing</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick presets */}
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/60">
            <span className="text-[11px] text-slate-500 self-center mr-1">Suggested Inquests:</span>
            {PRESET_QUERIES.map((preset, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(preset);
                  handleRunBriefing(preset);
                }}
                className="text-xs text-slate-400 hover:text-amber-300 px-3 py-1 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-all text-left"
              >
                {preset.slice(0, 50)}...
              </button>
            ))}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="rounded-xl p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <strong className="block font-semibold">Orchestration Alert:</strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Loading Steps Indicator */}
        {loading && (
          <div className="rounded-2xl bg-slate-900/70 border border-slate-800 p-8 text-center space-y-6">
            <div className="inline-flex p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 animate-pulse">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Chief of Staff Orchestrator Running</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Executing multi-specialist investigation and cross-departmental synthesis.
              </p>
            </div>

            {/* Step Progress Timeline */}
            <div className="max-w-md mx-auto grid grid-cols-3 gap-2 text-xs">
              <div className={`p-2.5 rounded-xl border ${loadingStep >= 1 ? "bg-amber-500/10 border-amber-500/30 text-amber-300" : "bg-slate-950 border-slate-800 text-slate-500"}`}>
                <span className="block font-bold">1. Query Validation</span>
                <span className="text-[10px]">Context bound</span>
              </div>
              <div className={`p-2.5 rounded-xl border ${loadingStep >= 2 ? "bg-amber-500/10 border-amber-500/30 text-amber-300" : "bg-slate-950 border-slate-800 text-slate-500"}`}>
                <span className="block font-bold">2. Specialist Agents</span>
                <span className="text-[10px]">Finance, Ops, Mktg</span>
              </div>
              <div className={`p-2.5 rounded-xl border ${loadingStep >= 3 ? "bg-amber-500/10 border-amber-500/30 text-amber-300" : "bg-slate-950 border-slate-800 text-slate-500"}`}>
                <span className="block font-bold">3. Cross-Synthesis</span>
                <span className="text-[10px]">Actions synthesized</span>
              </div>
            </div>
          </div>
        )}

        {/* Results view: Full Executive Intelligence Report */}
        {result && (
          <div className="space-y-6">
            {/* Report Header Metadata */}
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Executive Intelligence Report
                  </span>
                  {result.generated_at && (
                    <div className="flex items-center gap-1 text-[11px] text-slate-400">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{new Date(result.generated_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>
                <h2 className="text-lg font-bold text-white">
                  "{result.query}"
                </h2>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copied" : "Copy"}</span>
                </button>
                <button
                  onClick={handleExportJSON}
                  className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
              </div>
            </div>

            {/* Specialist Status Timeline Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Finance */}
              <div className="rounded-xl p-4 bg-slate-900/80 border border-teal-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-teal-400 font-semibold text-xs">
                    <TrendingUp className="w-4 h-4" />
                    <span>Finance Specialist</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                    result.specialist_results?.finance?.status === "consulted"
                      ? "bg-teal-500/15 text-teal-300 border-teal-500/30"
                      : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                  }`}>
                    {result.specialist_results?.finance?.status === "consulted" ? "Consulted" : "Unavailable"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.finance?.summary || "Data offline"}
                </p>
                <button
                  onClick={() => toggleEvidence("finance")}
                  className="text-[11px] font-semibold text-teal-400 hover:text-teal-300 flex items-center gap-1 pt-1"
                >
                  <span>{expandedEvidence.finance ? "Hide Evidence" : "View Evidence"}</span>
                  {expandedEvidence.finance ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
                {expandedEvidence.finance && (
                  <div className="mt-2 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 space-y-1">
                    {result.specialist_results?.finance?.findings?.map((f, i) => (
                      <div key={i}>&bull; {f}</div>
                    ))}
                  </div>
                )}
              </div>

              {/* Operations */}
              <div className="rounded-xl p-4 bg-slate-900/80 border border-cyan-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs">
                    <CalendarClock className="w-4 h-4" />
                    <span>Operations Specialist</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                    result.specialist_results?.ops?.status === "consulted"
                      ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
                      : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                  }`}>
                    {result.specialist_results?.ops?.status === "consulted" ? "Consulted" : "Unavailable"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.ops?.summary || "Data offline"}
                </p>
                <button
                  onClick={() => toggleEvidence("ops")}
                  className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 pt-1"
                >
                  <span>{expandedEvidence.ops ? "Hide Evidence" : "View Evidence"}</span>
                  {expandedEvidence.ops ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
                {expandedEvidence.ops && (
                  <div className="mt-2 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 space-y-1">
                    {result.specialist_results?.ops?.findings?.map((f, i) => (
                      <div key={i}>&bull; {f}</div>
                    ))}
                  </div>
                )}
              </div>

              {/* Marketing */}
              <div className="rounded-xl p-4 bg-slate-900/80 border border-emerald-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                    <Megaphone className="w-4 h-4" />
                    <span>Marketing Specialist</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                    result.specialist_results?.marketing?.status === "consulted"
                      ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                  }`}>
                    {result.specialist_results?.marketing?.status === "consulted" ? "Consulted" : "Unavailable"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.marketing?.summary || "Data offline"}
                </p>
                <button
                  onClick={() => toggleEvidence("marketing")}
                  className="text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 pt-1"
                >
                  <span>{expandedEvidence.marketing ? "Hide Evidence" : "View Evidence"}</span>
                  {expandedEvidence.marketing ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
                {expandedEvidence.marketing && (
                  <div className="mt-2 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 space-y-1">
                    {result.specialist_results?.marketing?.findings?.map((f, i) => (
                      <div key={i}>&bull; {f}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* 3 Dedicated Structured Sections: Risks, Opportunities, Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Key Risks */}
              <div className="rounded-xl p-4 bg-rose-950/30 border border-rose-500/30 space-y-2">
                <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Critical Risks</span>
                </div>
                <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
                  {(result.key_risks || []).length > 0 ? (
                    result.key_risks.map((r, i) => <li key={i}>{r}</li>)
                  ) : (
                    <li className="text-slate-500 italic">No critical risks flagged.</li>
                  )}
                </ul>
              </div>

              {/* Strategic Opportunities */}
              <div className="rounded-xl p-4 bg-teal-950/30 border border-teal-500/30 space-y-2">
                <div className="flex items-center gap-2 text-teal-400 font-bold text-xs uppercase tracking-wider">
                  <Lightbulb className="w-4 h-4" />
                  <span>Opportunities</span>
                </div>
                <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
                  {(result.key_opportunities || []).length > 0 ? (
                    result.key_opportunities.map((o, i) => <li key={i}>{o}</li>)
                  ) : (
                    <li className="text-slate-500 italic">No opportunities flagged.</li>
                  )}
                </ul>
              </div>

              {/* Top Actions */}
              <div className="rounded-xl p-4 bg-indigo-950/30 border border-indigo-500/30 space-y-2">
                <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Top Actions</span>
                </div>
                <ol className="text-xs text-slate-300 space-y-1.5 list-decimal list-inside">
                  {(result.top_actions || []).length > 0 ? (
                    result.top_actions.map((a, i) => <li key={i}>{a}</li>)
                  ) : (
                    <li className="text-slate-500 italic">No immediate actions required.</li>
                  )}
                </ol>
              </div>
            </div>

            {/* Synthesized Briefing Document */}
            <div className="rounded-2xl bg-slate-900 border border-amber-500/30 p-6 shadow-2xl relative space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  <h3 className="text-base font-bold text-white">Synthesized Executive Briefing</h3>
                </div>
                <span className="text-[11px] text-slate-400">
                  Synthesized via {result.metadata?.provider || "Groq"} ({result.metadata?.model || "qwen3.8-27b"})
                </span>
              </div>

              <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed">
                <ReactMarkdown>{result.synthesized_briefing}</ReactMarkdown>
              </div>

              {/* Follow-up CTA */}
              <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <p className="text-xs text-slate-400">
                  Need to drill deeper into these metrics or explore scenarios with the Chief of Staff?
                </p>
                <button
                  onClick={handleAskFollowUp}
                  className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-teal-500 hover:from-indigo-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Ask Follow-Up in Executive Chat</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
