import React, { useState, useEffect, useRef } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useChat } from "../context/ChatContext";
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
  HelpCircle,
  Copy,
  Check,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SPECIALIST_META = {
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
  const { conversations, addMessage, clearHistory } = useChat();

  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const meta = SPECIALIST_META[specialist];
  const history = (conversations && conversations[specialist]) || [];

  useEffect(() => {
    if (!meta) {
      navigate("/");
    }
  }, [specialist, meta, navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [specialist]);

  if (!meta) return null;

  const Icon = meta.icon;

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputValue).trim();
    if (!text || loading) return;

    setInputValue("");

    const userMsg = { role: "user", content: text };
    addMessage(specialist, userMsg);

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat/${specialist}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: history,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      addMessage(specialist, {
        role: "assistant",
        content: data.response || "No response received.",
      });
    } catch (err) {
      addMessage(specialist, {
        role: "assistant",
        content: `**Error:** Failed to get response from ${meta.name}. (${err.message}). Please try again.`,
      });
    } finally {
      setLoading(false);
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
    <div className="flex flex-col h-screen bg-[#080c14] text-slate-100 font-sans">
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
          {history.length > 0 && (
            <button
              onClick={() => clearHistory(specialist)}
              title="Clear conversation history"
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-400 px-2.5 py-1.5 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Ready</span>
          </div>
        </div>
      </header>

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
                Persistent multi-turn executive intelligence. Your conversation history is maintained even if you navigate away or refresh.
              </p>
            </div>

            {/* Starter prompts */}
            <div className="w-full max-w-lg space-y-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block text-left">
                Suggested Prompts
              </span>
              <div className="grid gap-2">
                {meta.starters.map((starter, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(starter)}
                    className="w-full text-left text-xs text-slate-300 p-3 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/80 transition-all flex items-center justify-between group"
                  >
                    <span>{starter}</span>
                    <Sparkles className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 transition-colors shrink-0 ml-2" />
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
                    <Bot className="w-4 h-4 text-teal-400" />
                  </div>
                )}

                <div
                  className={`relative group max-w-[85%] md:max-w-[75%] rounded-2xl p-4 text-xs md:text-sm leading-relaxed border shadow-md ${
                    isUser ? meta.userBubble : meta.agentBubble
                  }`}
                >
                  {isUser ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <div className="prose prose-invert prose-xs md:prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0.5">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
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

        {/* Loading Thinking Indicator */}
        {loading && (
          <div className="flex gap-3 justify-start items-center">
            <div className={`w-8 h-8 rounded-lg bg-slate-900 border ${meta.borderGlow} flex items-center justify-center shrink-0`}>
              <Bot className="w-4 h-4 text-teal-400" />
            </div>
            <div className="rounded-2xl px-4 py-3 bg-slate-900 border border-slate-800 text-slate-400 text-xs flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "0ms" }}></span>
                <span className="w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "150ms" }}></span>
                <span className="w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "300ms" }}></span>
              </div>
              <span className="text-slate-400 text-xs">{meta.shortName} Specialist is reasoning...</span>
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
                className="w-full resize-none rounded-xl bg-slate-900 border border-slate-800 focus:border-teal-500 focus:ring-1 focus:ring-teal-500 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={!inputValue.trim() || loading}
              className="h-11 px-4 rounded-xl bg-teal-500 hover:bg-teal-400 disabled:opacity-40 disabled:hover:bg-teal-500 text-slate-950 font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-teal-500/20"
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
            <span>Powered by Strands Agents SDK &middot; Groq Llama/Qwen Inference</span>
            <span>History saved to localStorage</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
