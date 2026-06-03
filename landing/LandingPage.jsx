import { motion } from "framer-motion";
import {
  BarChart2, RefreshCw, Coins, Activity, Users,
  PieChart, ShieldCheck, Lock, Database, Upload,
} from "lucide-react";

/* ─── animation variants ─── */
const fadeUp = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };
const stagger = { show: { transition: { staggerChildren: 0.12 } } };

/* ─── reusable components ─── */
const GlowPill = ({ children, color = "cyan" }) => (
  <span
    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold
      backdrop-blur-md border
      ${color === "cyan"
        ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-300"
        : color === "green"
        ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
        : "border-purple-500/40 bg-purple-500/10 text-purple-300"
      }`}
  >
    {children}
  </span>
);

const GlassCard = ({ children, className = "", glowColor = "cyan", hover = true }) => (
  <div
    className={`
      relative rounded-2xl border backdrop-blur-xl
      bg-white/[0.03] transition-all duration-300
      ${hover ? "group hover:-translate-y-1" : ""}
      ${glowColor === "cyan"
        ? "border-cyan-500/20 hover:border-cyan-400/50 hover:shadow-[0_0_30px_rgba(0,240,255,0.12)]"
        : glowColor === "purple"
        ? "border-purple-500/20 hover:border-purple-400/50 hover:shadow-[0_0_30px_rgba(176,38,255,0.15)]"
        : "border-emerald-500/20 hover:border-emerald-400/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.15)]"
      }
      ${className}
    `}
  >
    {children}
  </div>
);

/* ─── LEFT / RIGHT HUD PANELS ─── */
const LeftHUD1 = () => (
  <GlassCard className="p-5 w-52" glowColor="cyan">
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <div className="w-14 h-14 rounded-xl bg-cyan-500/10 border border-cyan-500/30
                        flex items-center justify-center
                        shadow-[0_0_20px_rgba(0,240,255,0.2)]">
          <Lock className="w-7 h-7 text-cyan-400" />
        </div>
        <div className="absolute -inset-1 rounded-xl border border-cyan-500/20 animate-pulse" />
      </div>
      <div className="text-center">
        <p className="text-xs font-bold text-white">Zero Storage</p>
        <p className="text-[10px] text-slate-400 mt-0.5">On-device parsing only</p>
      </div>
      {/* circuit lines */}
      <svg width="120" height="40" viewBox="0 0 120 40" className="opacity-40">
        <path d="M10 20 H40 V10 H80 V30 H110" stroke="#00F0FF" strokeWidth="1" fill="none" strokeDasharray="4 3" />
        <circle cx="40" cy="10" r="2" fill="#00F0FF" />
        <circle cx="80" cy="30" r="2" fill="#00F0FF" />
      </svg>
    </div>
  </GlassCard>
);

const LeftHUD2 = () => (
  <GlassCard className="p-5 w-52" glowColor="purple">
    <p className="text-[10px] font-bold text-purple-300 uppercase tracking-widest mb-3">
      SIP Health
    </p>
    <svg width="160" height="50" viewBox="0 0 160 50">
      <polyline
        points="0,25 20,25 30,5 45,45 60,10 75,35 95,15 110,30 130,20 160,20"
        fill="none" stroke="#B026FF" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"
      />
      <polyline
        points="0,25 20,25 30,5 45,45 60,10 75,35 95,15 110,30 130,20 160,20"
        fill="none" stroke="rgba(176,38,255,0.15)" strokeWidth="8"
        strokeLinecap="round" strokeLinejoin="round"
      />
    </svg>
    <div className="flex items-center gap-1.5 mt-2">
      <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
      <p className="text-[10px] text-purple-300">9 active · 0 bounced</p>
    </div>
  </GlassCard>
);

const RightHUD1 = () => (
  <GlassCard className="p-5 w-52" glowColor="cyan">
    <p className="text-[10px] font-bold text-cyan-300 uppercase tracking-widest mb-3">
      Sources
    </p>
    <div className="flex flex-col gap-2">
      {["CAMS", "KFintech"].map((name, i) => (
        <div key={name} className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30
                          flex items-center justify-center">
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <span className="text-xs font-semibold text-white">{name}</span>
        </div>
      ))}
    </div>
    <svg width="80" height="30" viewBox="0 0 80 30" className="mt-3 opacity-50">
      <path d="M10 10 Q40 0 70 10" stroke="#00F0FF" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      <path d="M10 20 Q40 30 70 20" stroke="#00F0FF" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      <circle cx="10" cy="15" r="3" fill="#00F0FF" />
      <circle cx="70" cy="15" r="3" fill="#00F0FF" />
    </svg>
  </GlassCard>
);

const RightHUD2 = () => (
  <GlassCard className="p-5 w-52" glowColor="green">
    <p className="text-[10px] font-bold text-emerald-300 uppercase tracking-widest mb-3">
      Portfolio XIRR
    </p>
    <div className="flex items-end gap-1 h-14">
      {[40, 55, 35, 70, 50, 85, 65].map((h, i) => (
        <div
          key={i}
          className="flex-1 rounded-t"
          style={{
            height: `${h}%`,
            background: i === 5
              ? "linear-gradient(to top, #10b981, #34d399)"
              : "rgba(16,185,129,0.25)",
            boxShadow: i === 5 ? "0 0 12px rgba(16,185,129,0.5)" : "none",
          }}
        />
      ))}
    </div>
    <div className="mt-3 flex items-center gap-1.5">
      <span className="text-emerald-400 font-bold text-sm">▲ XIRR 8.3%</span>
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
    </div>
  </GlassCard>
);

/* ─── UPLOAD PORTAL ─── */
const UploadPortal = () => (
  <div className="relative">
    {/* glow behind the box */}
    <div className="absolute -inset-4 rounded-3xl bg-gradient-to-r from-cyan-500/20 via-purple-500/10 to-cyan-500/20 blur-2xl" />

    <div
      className="relative rounded-2xl p-8 w-80 text-center
        bg-white/[0.04] backdrop-blur-xl
        border-2 border-dashed"
      style={{ borderImage: "linear-gradient(135deg,#00F0FF,#B026FF) 1" }}
    >
      {/* inner glow ring */}
      <div className="absolute inset-0 rounded-2xl
        shadow-[inset_0_0_40px_rgba(0,240,255,0.05)]" />

      <div className="w-14 h-14 mx-auto mb-4 rounded-xl
        bg-gradient-to-br from-cyan-500/20 to-purple-500/20
        border border-cyan-500/30 flex items-center justify-center
        shadow-[0_0_20px_rgba(0,240,255,0.15)]">
        <Upload className="w-6 h-6 text-cyan-400" />
      </div>

      <p className="text-white font-bold text-lg mb-1">Upload your CAS PDF</p>
      <p className="text-slate-400 text-xs mb-6 leading-relaxed">
        Drag and drop or click to browse<br />PDF files only
      </p>

      <button
        className="w-full py-3 px-6 rounded-xl font-semibold text-sm
          bg-gradient-to-r from-cyan-500 to-purple-600
          text-white shadow-[0_0_20px_rgba(0,240,255,0.3)]
          hover:shadow-[0_0_30px_rgba(0,240,255,0.5)]
          hover:scale-[1.02] active:scale-[0.98]
          transition-all duration-200 flex items-center justify-center gap-2"
      >
        <Upload className="w-4 h-4" />
        200MB per file · PDF
      </button>
    </div>
  </div>
);

/* ─── FEATURE CARDS ─── */
const features = [
  {
    icon: <BarChart2 className="w-6 h-6 text-cyan-400" />,
    title: "Live NAV & XIRR",
    desc: "Real-time NAV from MFAPI. Per-scheme XIRR calculated automatically across your entire portfolio history.",
    span: 1, glow: "cyan",
  },
  {
    icon: <RefreshCw className="w-6 h-6 text-purple-400" />,
    title: "360° Portfolio View",
    desc: "Every folio, scheme, and transaction from both CAMS and KFintech — unified in a single clean dashboard.",
    span: 1, glow: "purple",
  },
  {
    icon: <Coins className="w-6 h-6 text-cyan-400" />,
    title: "P&L Analytics",
    desc: "Realised & unrealised gains broken down by scheme, category, and time period — with a visual summary.",
    span: 1, glow: "cyan",
  },
  {
    icon: <Activity className="w-6 h-6 text-white" />,
    title: "SIP Health Monitor",
    desc: "Track every active SIP — next due dates, mandate status, bounce alerts, and historical SIP investment timeline.",
    span: 2, glow: "wide",
    pills: ["Active SIPs", "Bounce Alerts", "Next Due Date"],
  },
  {
    icon: <Users className="w-6 h-6 text-slate-300" />,
    title: "Family View",
    desc: "Analyse multiple CAS files together. Compare portfolios across family members with a consolidated wealth summary.",
    span: 1, glow: "dark",
  },
  {
    icon: <PieChart className="w-6 h-6 text-cyan-400" />,
    title: "Asset Allocation",
    desc: "Equity vs Debt breakdown with interactive charts. Understand your actual risk exposure at a glance.",
    span: 1, glow: "cyan",
  },
  {
    icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
    title: "100% Private by Design",
    desc: "Your CAS PDF is parsed entirely on your device using casparser. No data is uploaded, logged, or stored anywhere.",
    span: 1, glow: "green",
    pills: ["✓ No server storage", "✓ Local processing"],
  },
];

const FeatureCard = ({ card, index }) => {
  const isWide = card.span === 2;
  const isDark = card.glow === "dark";
  const isGreen = card.glow === "green";

  return (
    <motion.div
      variants={fadeUp}
      className={`
        relative rounded-2xl p-6 border backdrop-blur-xl
        transition-all duration-300 group
        ${isWide
          ? "col-span-2 bg-gradient-to-br from-indigo-600/30 via-purple-600/20 to-blue-600/30 border-purple-500/30 hover:border-purple-400/60 hover:shadow-[0_0_40px_rgba(139,92,246,0.2)]"
          : isDark
          ? "bg-slate-900/80 border-blue-900/50 hover:border-blue-700/60 hover:shadow-[0_0_24px_rgba(59,130,246,0.1)]"
          : isGreen
          ? "bg-white/[0.03] border-emerald-500/20 hover:border-emerald-400/50 hover:shadow-[0_0_28px_rgba(16,185,129,0.15)]"
          : "bg-white/[0.03] border-white/[0.07] hover:border-cyan-500/40 hover:shadow-[0_0_24px_rgba(0,240,255,0.1)]"
        }
        hover:-translate-y-1
      `}
    >
      {/* icon bubble */}
      <div className={`
        w-11 h-11 rounded-xl flex items-center justify-center mb-4
        ${isWide
          ? "bg-white/10 border border-white/20"
          : isDark
          ? "bg-blue-900/40 border border-blue-800/50"
          : isGreen
          ? "bg-emerald-500/10 border border-emerald-500/30"
          : "bg-cyan-500/10 border border-cyan-500/20"
        }
      `}>
        {card.icon}
      </div>

      <h3 className={`font-bold text-base mb-2 ${isWide ? "text-white text-xl" : "text-white"}`}>
        {card.title}
      </h3>
      <p className={`text-sm leading-relaxed ${isWide ? "text-white/70 max-w-lg" : "text-slate-400"}`}>
        {card.desc}
      </p>

      {card.pills && (
        <div className="flex flex-wrap gap-2 mt-4">
          {card.pills.map((pill) => (
            <span
              key={pill}
              className={`px-3 py-1 rounded-full text-xs font-semibold border
                ${isWide
                  ? "bg-white/10 border-white/20 text-white"
                  : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                }`}
            >
              {pill}
            </span>
          ))}
        </div>
      )}

      {/* hover accent line */}
      <div className={`
        absolute bottom-0 left-6 right-6 h-px rounded-full opacity-0 group-hover:opacity-100 transition-opacity
        ${isGreen ? "bg-gradient-to-r from-transparent via-emerald-400 to-transparent"
          : isWide ? "bg-gradient-to-r from-transparent via-purple-400 to-transparent"
          : "bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
        }
      `} />
    </motion.div>
  );
};

/* ─── MAIN EXPORT ─── */
export default function LandingPage() {
  return (
    <div
      className="min-h-screen text-white overflow-x-hidden"
      style={{
        background: "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,240,255,0.08) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 50%, rgba(176,38,255,0.07) 0%, transparent 60%), #0B0E14",
      }}
    >
      {/* Tech-grid overlay */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(0,240,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,1) 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      />

      {/* ══════════ HERO ══════════ */}
      <section className="relative pt-16 pb-24 px-4">
        <div className="max-w-6xl mx-auto">

          {/* ── Header ── */}
          <motion.div
            initial="hidden" animate="show" variants={stagger}
            className="text-center mb-16"
          >
            {/* Logo */}
            <motion.div variants={fadeUp} className="mb-5">
              <h2
                className="text-3xl font-black tracking-tight"
                style={{
                  color: "#00F0FF",
                  textShadow: "0 0 30px rgba(0,240,255,0.6), 0 0 60px rgba(0,240,255,0.3)",
                }}
              >
                cas.360 view
              </h2>
            </motion.div>

            {/* Badge */}
            <motion.div variants={fadeUp} className="flex justify-center mb-10">
              <GlowPill color="cyan">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_#00F0FF]" />
                MUTUAL FUND INTELLIGENCE PLATFORM
              </GlowPill>
            </motion.div>

            {/* H1 */}
            <motion.h1
              variants={fadeUp}
              className="text-5xl md:text-7xl font-black tracking-tighter mb-6 leading-none"
              style={{
                background: "linear-gradient(135deg, #00F0FF 0%, #B026FF 60%, #00F0FF 100%)",
                backgroundSize: "200% auto",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
                textShadow: "none",
                filter: "drop-shadow(0 0 30px rgba(0,240,255,0.3))",
                animation: "gradientShift 4s ease infinite",
              }}
            >
              Your Portfolio,<br />Fully Decoded.
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              variants={fadeUp}
              className="text-slate-400 text-lg max-w-xl mx-auto mb-8 leading-relaxed"
            >
              Upload your CAS PDF and instantly unlock a complete 360° view of all
              your mutual fund investments — live NAV, XIRR, SIP health, and more.
            </motion.p>

            {/* Trust pills */}
            <motion.div variants={fadeUp} className="flex flex-wrap justify-center gap-2 mb-16">
              {[
                "🔒 Zero data storage",
                "⚡ Instant analysis",
                "🏦 CAMS + KFintech",
                "📊 Live NAV & XIRR",
              ].map((t) => (
                <GlowPill key={t} color="cyan">{t}</GlowPill>
              ))}
            </motion.div>
          </motion.div>

          {/* ── 3-panel row: HUDs + Upload Portal ── */}
          <motion.div
            initial="hidden" animate="show" variants={stagger}
            className="flex items-center justify-center gap-6 flex-wrap"
          >
            {/* Left HUDs */}
            <motion.div variants={fadeUp} className="flex flex-col gap-4">
              <LeftHUD1 />
              <LeftHUD2 />
            </motion.div>

            {/* Center portal */}
            <motion.div variants={fadeUp}>
              <UploadPortal />
            </motion.div>

            {/* Right HUDs */}
            <motion.div variants={fadeUp} className="flex flex-col gap-4">
              <RightHUD1 />
              <RightHUD2 />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* divider glow */}
      <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent mx-8" />

      {/* ══════════ FEATURES ══════════ */}
      <section className="py-24 px-4">
        <div className="max-w-6xl mx-auto">

          {/* Section header */}
          <motion.div
            initial="hidden" whileInView="show" viewport={{ once: true }} variants={stagger}
            className="text-center mb-14"
          >
            <motion.div variants={fadeUp} className="flex justify-center mb-4">
              <GlowPill color="purple">WHY CAS 360</GlowPill>
            </motion.div>
            <motion.h2
              variants={fadeUp}
              className="text-4xl md:text-5xl font-black text-white tracking-tight mb-4"
            >
              Everything your portfolio<br />needs, in one place.
            </motion.h2>
            <motion.p variants={fadeUp} className="text-slate-400 text-lg">
              Institutional-grade portfolio intelligence for every Indian investor.
            </motion.p>
          </motion.div>

          {/* Bento grid */}
          <motion.div
            initial="hidden" whileInView="show" viewport={{ once: true }} variants={stagger}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            {features.map((card, i) => (
              <FeatureCard key={i} card={card} index={i} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* Footer glow */}
      <div className="h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent mx-8 mb-8" />
      <p className="text-center text-slate-600 text-xs pb-12">
        © 2026 cas.360 view · All data processed locally · Zero server storage
      </p>

      {/* ── gradient keyframes ── */}
      <style>{`
        @keyframes gradientShift {
          0%   { background-position: 0%   50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0%   50%; }
        }
      `}</style>
    </div>
  );
}
