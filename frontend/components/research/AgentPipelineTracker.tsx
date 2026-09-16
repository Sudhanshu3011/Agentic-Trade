"use client";

import { motion } from "framer-motion";
import {
  Activity,
  Landmark,
  Globe2,
  Newspaper,
  Layers,
  Sparkles,
} from "lucide-react";

interface AgentStatus {
  name: string;
  role: string;
  description: string;
  icon: typeof Activity;
  color: string;
  bg: string;
  border: string;
}

const AGENTS: AgentStatus[] = [
  {
    name: "Technical Analyst",
    role: "Quantitative Indicators",
    description: "Evaluating trend momentum, support/resistance & RSI volatility regimes...",
    icon: Activity,
    color: "text-indigo-600",
    bg: "bg-indigo-50/35",
    border: "border-indigo-200/60",
  },
  {
    name: "Fundamental Analyst",
    role: "Financial Statements",
    description: "Auditing balance sheet leverage, ROCE, and free cash-flow inflections...",
    icon: Landmark,
    color: "text-emerald-600",
    bg: "bg-emerald-50/35",
    border: "border-emerald-200/60",
  },
  {
    name: "Global Market Analyst",
    role: "Macro Regimes",
    description: "Correlating Nifty 50, Sensex, VIX, and global indices...",
    icon: Globe2,
    color: "text-blue-600",
    bg: "bg-blue-50/35",
    border: "border-blue-200/60",
  },
  {
    name: "News & Sentiment Analyst",
    role: "Disclosures & Signals",
    description: "Extracting corporate actions, regulatory filings, and market catalysts...",
    icon: Newspaper,
    color: "text-amber-600",
    bg: "bg-amber-50/35",
    border: "border-amber-200/60",
  },
  {
    name: "Sector Specialist",
    role: "Peer Benchmarking",
    description: "Benchmarking relative valuation multiples & industry tailwinds...",
    icon: Layers,
    color: "text-purple-600",
    bg: "bg-purple-50/35",
    border: "border-purple-200/60",
  },
];

export function AgentPipelineTracker() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4 }}
      className="mt-6 rounded-2xl border border-zinc-200/80 bg-white/95 p-5 sm:p-6 shadow-sm backdrop-blur-sm"
    >
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-zinc-100">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600 border border-amber-500/20">
            <Sparkles className="h-4 w-4 animate-pulse" />
          </div>
          <div>
            <h3 className="font-sans text-[15px] font-semibold text-zinc-900 tracking-tight">
              Institutional Research Squad in Session
            </h3>
            <p className="text-[13px] text-zinc-500">
              5 specialist agents are synthesizing in-depth reports in parallel. Full reports unlock below momentarily.
            </p>
          </div>
        </div>

        {/* Live Pulse Badge */}
        <div className="flex items-center gap-2 self-start sm:self-center px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-800 font-mono text-[11px] font-medium">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          </span>
          <span>5 Agents Active</span>
        </div>
      </div>

      {/* Progress Timeline Indicator */}
      <div className="relative my-4 h-1.5 w-full overflow-hidden rounded-full bg-zinc-100">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-amber-500 via-indigo-600 to-amber-500"
          initial={{ width: "15%" }}
          animate={{ width: ["20%", "65%", "85%"] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* 5 Agent Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-2">
        {AGENTS.map((agent, i) => {
          const Icon = agent.icon;
          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.08 }}
              className={`flex flex-col justify-between rounded-xl border ${agent.border} ${agent.bg} p-3.5 transition-all hover:shadow-sm`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${agent.color}`} />
                    <span className="font-sans text-[13px] font-semibold text-zinc-900 line-clamp-1">
                      {agent.name}
                    </span>
                  </div>
                </div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-zinc-400 mb-1.5">
                  {agent.role}
                </p>
                <p className="text-[12px] leading-relaxed text-zinc-600 line-clamp-3">
                  {agent.description}
                </p>
              </div>

              {/* Status pill */}
              <div className="mt-3 flex items-center gap-1.5 pt-2 border-t border-black/[0.04]">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
                <span className="font-mono text-[10px] text-zinc-500">
                  Synthesizing...
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

