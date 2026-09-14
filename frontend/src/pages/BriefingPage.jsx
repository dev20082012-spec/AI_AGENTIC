import React, { useState } from "react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  ArrowLeft,
  Sparkles,
  TrendingUp,
  CalendarClock,
  Megaphone,
  Send,
  Loader2,
  Copy,
  Check,
  Layers,
  Activity,
  CheckCircle2,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const PRESET_QUERIES = [
  "Give me this week's briefing: revenue trend, pending ops items, and how our last campaign performed.",
  "Executive sync: Analyze 3-month sales forecast, critical operational blockers, and ad conversion ROI.",
];

export default function BriefingPage() {
  const [query, setQuery] = useState(PRESET_QUERIES[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleRunBriefing = async (queryToRun) => {
    const q = queryToRun || query;
    if (!q.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

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
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result?.synthesized_briefing) return;
    navigator.clipboard.writeText(result.synthesized_briefing);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
              <p className="text-[11px] text-slate-400">Chief of Staff Orchestrator (Multi-Agent Synthesis)</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 space-y-6">
        {/* Search / Run Controls */}
        <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 shadow-xl space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Briefing Query
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
            <span className="text-[11px] text-slate-500 self-center mr-1">Preset:</span>
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
          <div className="rounded-xl p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading Spinner / Progress */}
        {loading && (
          <div className="rounded-2xl bg-slate-900/50 border border-slate-800/80 p-8 text-center space-y-4">
            <div className="inline-flex p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 animate-pulse">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Chief of Staff Orchestrator Running</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Analyzing request, dispatching to Finance, Operations, and Marketing specialist agents, and synthesizing final actions...
              </p>
            </div>
          </div>
        )}

        {/* Results view */}
        {result && (
          <div className="space-y-6">
            {/* 3 Specialist Cards Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Finance */}
              <div className="rounded-xl p-4 bg-slate-900/70 border border-teal-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-teal-400 font-semibold text-xs">
                    <TrendingUp className="w-4 h-4" />
                    <span>Finance Specialist</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                    {result.specialist_results?.finance?.called ? "Consulted" : "Skipped"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.finance?.summary || "No data reported."}
                </p>
              </div>

              {/* Ops */}
              <div className="rounded-xl p-4 bg-slate-900/70 border border-cyan-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs">
                    <CalendarClock className="w-4 h-4" />
                    <span>Operations Specialist</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {result.specialist_results?.ops?.called ? "Consulted" : "Skipped"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.ops?.summary || "No data reported."}
                </p>
              </div>

              {/* Marketing */}
              <div className="rounded-xl p-4 bg-slate-900/70 border border-emerald-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                    <Megaphone className="w-4 h-4" />
                    <span>Marketing Specialist</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {result.specialist_results?.marketing?.called ? "Consulted" : "Skipped"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-3">
                  {result.specialist_results?.marketing?.summary || "No data reported."}
                </p>
              </div>
            </div>

            {/* Synthesized Briefing */}
            <div className="rounded-2xl bg-slate-900 border border-amber-500/30 p-6 shadow-2xl relative">
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-bold text-white">Synthesized Executive Briefing</h2>
                </div>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copied" : "Copy Briefing"}</span>
                </button>
              </div>

              <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed">
                <ReactMarkdown>{result.synthesized_briefing}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
