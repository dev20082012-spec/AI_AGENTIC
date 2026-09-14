import React from "react";
import { Link } from "react-router-dom";
import { useChat } from "../context/ChatContext";
import {
  TrendingUp,
  CalendarClock,
  Megaphone,
  Layers,
  Sparkles,
  ArrowRight,
  MessageSquare,
  Cpu,
  ChevronRight,
} from "lucide-react";

const SPECIALISTS = [
  {
    id: "finance",
    name: "Finance Agent",
    icon: TrendingUp,
    color: "from-teal-500/20 to-teal-600/10 border-teal-500/30 text-teal-400 hover:border-teal-400/60",
    badgeColor: "bg-teal-500/15 text-teal-300 border-teal-500/30",
    description: "Revenue trend analytics, 3-month forecasting & anomaly detection across products.",
    path: "/chat/finance",
    sampleQuery: "What's our revenue trend across product lines?",
  },
  {
    id: "ops",
    name: "Operations Agent",
    icon: CalendarClock,
    color: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/30 text-cyan-400 hover:border-cyan-400/60",
    badgeColor: "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
    description: "Day-to-day operations, blocked bottleneck resolution, team tasks & scheduling.",
    path: "/chat/ops",
    sampleQuery: "Which operational tasks are blocked or stale?",
  },
  {
    id: "marketing",
    name: "Marketing Agent",
    icon: Megaphone,
    color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-400 hover:border-emerald-400/60",
    badgeColor: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    description: "Advertising campaign attribution, demographic targeting, CTR & conversion ROI.",
    path: "/chat/marketing",
    sampleQuery: "How did our last ad campaign perform by region?",
  },
];

export default function LandingPage() {
  const { conversations } = useChat();

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      {/* Top Bar */}
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

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              <span>Strands Agents SDK</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span>Multi-Agent Network Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 flex flex-col justify-center">
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white mb-3">
            Select an Executive Specialist
          </h1>
          <p className="text-slate-400 text-sm md:text-base leading-relaxed">
            Engage in persistent multi-turn conversations with domain specialists, or execute a comprehensive full-business executive briefing with the top-level orchestrator.
          </p>
        </div>

        {/* 4 Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* 3 Specialist Cards */}
          {SPECIALISTS.map((spec) => {
            const Icon = spec.icon;
            const history = conversations[spec.id] || [];
            const msgCount = history.length;
            const lastMsg = msgCount > 0 ? history[msgCount - 1] : null;

            return (
              <Link
                key={spec.id}
                to={spec.path}
                className={`group relative rounded-2xl bg-gradient-to-b ${spec.color} border p-6 flex flex-col justify-between transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl shadow-lg bg-slate-900/60`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-center text-current group-hover:scale-110 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    {msgCount > 0 ? (
                      <span className={`flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${spec.badgeColor}`}>
                        <MessageSquare className="w-3 h-3" />
                        {msgCount} message{msgCount > 1 ? "s" : ""}
                      </span>
                    ) : (
                      <span className="text-[11px] text-slate-400 px-2 py-0.5 rounded bg-slate-950/60 border border-slate-800">
                        New Thread
                      </span>
                    )}
                  </div>

                  <h2 className="text-lg font-bold text-white mb-1 group-hover:text-teal-300 transition-colors">
                    {spec.name}
                  </h2>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4">
                    {spec.description}
                  </p>
                </div>

                {/* History preview or quick prompt */}
                <div className="mt-4 pt-4 border-t border-slate-800/80">
                  {lastMsg ? (
                    <div>
                      <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block mb-1">
                        Last message:
                      </span>
                      <p className="text-xs text-slate-300 line-clamp-2 italic bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
                        "{lastMsg.content.slice(0, 85)}..."
                      </p>
                    </div>
                  ) : (
                    <div>
                      <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block mb-1">
                        Starter:
                      </span>
                      <p className="text-xs text-slate-400 line-clamp-2">
                        {spec.sampleQuery}
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-4 text-xs font-semibold text-slate-200 group-hover:text-white">
                    <span>Open Chat</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            );
          })}

          {/* 4th Card: Full Briefing (Orchestrator) */}
          <Link
            to="/briefing"
            className="group relative rounded-2xl bg-gradient-to-b from-amber-500/20 to-amber-600/10 border border-amber-500/30 hover:border-amber-400/60 p-6 flex flex-col justify-between transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl shadow-lg bg-slate-900/60"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6" />
                </div>
                <span className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border bg-amber-500/15 text-amber-300 border-amber-500/30">
                  Orchestrator
                </span>
              </div>

              <h2 className="text-lg font-bold text-white mb-1 group-hover:text-amber-300 transition-colors">
                Full Business Briefing
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Executes the top-level orchestrator agent across Finance, Ops, and Marketing simultaneously.
              </p>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800/80">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-amber-400/80 block mb-1">
                Executive View
              </span>
              <p className="text-xs text-slate-400 line-clamp-2">
                Unified cross-domain intelligence with synthesized 3 Key Actions.
              </p>

              <div className="flex items-center justify-between mt-4 text-xs font-semibold text-amber-300 group-hover:text-amber-200">
                <span>Run Orchestrator</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>
        </div>
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
