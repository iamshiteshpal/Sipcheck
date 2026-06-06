import React, { useState, useMemo } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  BarChart, Bar, Legend, RadialBarChart, RadialBar,
  ScatterChart, Scatter, ZAxis, LineChart, Line,
} from 'recharts';

// ── Semantic color constants ─────────────────────────────────
const EMERALD = '#10B981';
const RED     = '#EF4444';
const AMBER   = '#F59E0B';
const BLUE    = '#3B82F6';
const MUTED   = '#6B7280';

// ── Helpers ──────────────────────────────────────────────────
const formatINR = (v) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v ?? 0);
const fmtPct    = (v) => `${(v ?? 0) >= 0 ? '+' : ''}${(v ?? 0).toFixed(2)}%`;
const safeVal   = (v) => (v == null || isNaN(v) ? 0 : v);
const cleanName = (n) => (n ?? '').replace(/--+$/, '').trim();
const pnlColor  = (v) => (v ?? 0) >= 0 ? EMERALD : RED;

// Section label — 11px, 500, muted, 0.08em spacing, no uppercase
const SL = { fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', color: MUTED, marginBottom: 12 };

// ── Shared styles ─────────────────────────────────────────────
const card      = { background: '#111111', border: '1px solid #2A2A2A', borderRadius: 12, padding: 20 };
const muted     = { color: MUTED };
const secondary = { color: '#9CA3AF' };
const positive  = { color: EMERALD };
const negative  = { color: RED };

// ── Mock data ─────────────────────────────────────────────────

const TOTAL_INVESTED = 1500000;
const TOTAL_VALUE    = 1706800;
const TOTAL_PNL      = TOTAL_VALUE - TOTAL_INVESTED;
const XIRR_PCT       = 8.28;

const PERF_DONUT_DATA = [
  { name: 'Equity', value: 1360000, color: BLUE   },
  { name: 'Gold',   value: 148800,  color: AMBER  },
  { name: 'Debt',   value: 198000,  color: '#06B6D4' },
];

const TOP_GAINERS = [
  { name: 'Parag Parikh Flexi',  invested: 300000, value: 410264, pnl: 110264, xirr: 24.3, nav: [54,58,62,67,71,74] },
  { name: 'Mirae Large Cap',     invested: 150000, value: 189918, pnl: 39918,  xirr: 18.2, nav: [82,88,92,97,101,104] },
  { name: 'HDFC Mid Cap Opp.',   invested: 108000, value: 135000, pnl: 27000,  xirr: 16.5, nav: [45,48,52,56,60,63] },
  { name: 'Nippon Small Cap',    invested: 48000,  value: 58000,  pnl: 10000,  xirr: 14.1, nav: [90,95,100,108,118,124] },
  { name: 'DSP Midcap',          invested: 70000,  value: 82000,  pnl: 12000,  xirr: 12.8, nav: [30,32,35,38,40,42] },
];

const CAPITAL_CONC = [
  { name: 'Parag Parikh Flexi', invested: 300000, pct: 20.0 },
  { name: 'Axis Bluechip',      invested: 300000, pct: 20.0 },
  { name: 'ICICI Pru Tech',     invested: 250000, pct: 16.7 },
  { name: 'Mirae Large Cap',    invested: 150000, pct: 10.0 },
  { name: 'SBI Gold Fund',      invested: 120000, pct:  8.0 },
];
const CAPITAL_MAX = 300000;

const RECENT_REDEEM = [
  { name: 'Mirae Large Cap', amount: 120000 },
  { name: 'ICICI Tech',      amount: 95000  },
  { name: 'Axis Bluechip',   amount: 85000  },
  { name: 'HDFC ELSS',       amount: 60000  },
  { name: 'SBI ELSS',        amount: 50000  },
];
const TOTAL_REDEEMED = RECENT_REDEEM.reduce((s, r) => s + r.amount, 0);

const SIP_COUNTDOWN = [
  { name: 'Parag Parikh Flexi', amount: 10000, day: 5,  nextDate: '05 Jun', daysLeft: 2  },
  { name: 'Axis Bluechip',      amount: 7500,  day: 10, nextDate: '10 Jun', daysLeft: 7  },
  { name: 'HDFC Mid Cap',       amount: 6000,  day: 15, nextDate: '15 Jun', daysLeft: 12 },
  { name: 'Mirae Large Cap',    amount: 5000,  day: 20, nextDate: '20 Jun', daysLeft: 17 },
  { name: 'SBI Gold Fund',      amount: 2000,  day: 25, nextDate: '25 Jun', daysLeft: 22 },
];

const HOLDINGS = [
  { scheme: 'Mirae Asset Large Cap Fund',  category: 'Equity', invested: 150000, value: 189918, pnl: 39918,  xirr: 18.2 },
  { scheme: 'Parag Parikh Flexi Cap Fund', category: 'Equity', invested: 300000, value: 410264, pnl: 110264, xirr: 24.3 },
  { scheme: 'Axis Bluechip Fund',          category: 'Equity', invested: 300000, value: 375728, pnl: 75728,  xirr: 11.4 },
  { scheme: 'ICICI Pru Technology Fund',   category: 'Equity', invested: 250000, value: 303497, pnl: 53497,  xirr: 10.8 },
  { scheme: 'HDFC Mid Cap Opp. Fund',      category: 'Equity', invested: 108000, value: 135000, pnl: 27000,  xirr: 16.5 },
  { scheme: 'SBI Gold Fund--',             category: 'Gold',   invested: 120000, value: 148800, pnl: 28800,  xirr: 12.1 },
];

const MAX_INVESTED = Math.max(...HOLDINGS.map(h => h.invested));
const MIN_R = 8, MAX_R = 40;
const BUBBLE_DATA = HOLDINGS.map(h => ({
  name: h.scheme,
  xirr: h.xirr,
  value: h.value,
  invested: h.invested,
  z: Math.max(MIN_R * MIN_R, (h.invested / MAX_INVESTED) * MAX_R * MAX_R),
}));

const REALIZED_PNL = { equity: 75935, gold: 28800 };
REALIZED_PNL.total = REALIZED_PNL.equity + REALIZED_PNL.gold;

const SIP_MANDATES = [
  { scheme: 'Mirae Asset Large Cap--', amount: 5000,  status: 'ACTIVE',   day: 20, nextDue: '20 Jun 2026' },
  { scheme: 'Parag Parikh Flexi Cap',  amount: 10000, status: 'ACTIVE',   day: 5,  nextDue: '05 Jun 2026' },
  { scheme: 'Axis Bluechip Fund',      amount: 7500,  status: 'ACTIVE',   day: 10, nextDue: '10 Jun 2026' },
  { scheme: 'HDFC Mid Cap Opp. Fund',  amount: 6000,  status: 'ACTIVE',   day: 15, nextDue: '15 Jun 2026' },
  { scheme: 'Nippon India Small Cap',  amount: 4000,  status: 'INACTIVE', day: 1,  nextDue: '01 Jun 2026' },
  { scheme: 'SBI Gold Fund',           amount: 2000,  status: 'ACTIVE',   day: 25, nextDue: '25 Jun 2026' },
  { scheme: 'ICICI Pru Nifty 50',      amount: 3000,  status: 'ACTIVE',   day: 7,  nextDue: '07 Jun 2026' },
  { scheme: 'DSP Midcap Fund',         amount: 5000,  status: 'ACTIVE',   day: 12, nextDue: '12 Jun 2026' },
  { scheme: 'Kotak Flexicap Fund',     amount: 4000,  status: 'ACTIVE',   day: 18, nextDue: '18 Jun 2026' },
  { scheme: 'Quant Small Cap Fund',    amount: 2499,  status: 'ACTIVE',   day: 22, nextDue: '22 Jun 2026' },
];
const MONTHLY_TOTAL = SIP_MANDATES.reduce((s, m) => s + m.amount, 0);
const ANNUAL_COMMIT = MONTHLY_TOTAL * 12;

const ALLOCATION_DATA = [
  { category: 'Large Cap', invested: 450000, currentValue: 558000,  color: EMERALD     },
  { category: 'Mid Cap',   invested: 300000, currentValue: 384000,  color: BLUE        },
  { category: 'Small Cap', invested: 200000, currentValue: 268000,  color: '#8B5CF6'   },
  { category: 'Sectoral',  invested: 250000, currentValue: 307500,  color: AMBER       },
  { category: 'Debt',      invested: 180000, currentValue: 198000,  color: '#06B6D4'   },
  { category: 'Gold',      invested: 120000, currentValue: 148800,  color: '#EC4899'   },
];

const SWP_DATA = {
  monthlyWithdrawals: [
    { month: 'Jan 2024', amount: 15000 }, { month: 'Feb 2024', amount: 15000 },
    { month: 'Mar 2024', amount: 15000 }, { month: 'Apr 2024', amount: 18000 },
    { month: 'May 2024', amount: 15000 }, { month: 'Jun 2024', amount: 15000 },
    { month: 'Jul 2024', amount: 20000 }, { month: 'Aug 2024', amount: 15000 },
    { month: 'Sep 2024', amount: 15000 }, { month: 'Oct 2024', amount: 15000 },
    { month: 'Nov 2024', amount: 22000 }, { month: 'Dec 2024', amount: 15000 },
  ],
  summary: { totalWithdrawn: 195000, remainingPrincipal: 1305000, monthlyWithdrawalRate: 15000, estimatedRunRateMonths: 87 },
  switchLog: [
    { date: '15 Jan 2024', sourceScheme: 'HDFC Balanced Adv. Fund', destinationScheme: 'ICICI Pru Liquid Fund', unitsTransferred: 842.50, navAtSwitch: 284.60, switchValue: 239880, taxType: 'LTCG', taxAmount: 4200 },
    { date: '08 Apr 2024', sourceScheme: 'Axis Bluechip Fund',       destinationScheme: 'Parag Parikh Flexi Cap', unitsTransferred: 1200.00, navAtSwitch: 49.20, switchValue: 59040, taxType: 'STCG', taxAmount: 1180 },
    { date: '22 Jul 2024', sourceScheme: 'SBI Liquid Fund',          destinationScheme: 'Mirae Asset Large Cap', unitsTransferred: 450.75, navAtSwitch: 3421.80, switchValue: 1542797, taxType: 'NIL', taxAmount: 0 },
    { date: '10 Nov 2024', sourceScheme: 'Nippon India Small Cap',   destinationScheme: 'HDFC Mid Cap Opp. Fund', unitsTransferred: 600.00, navAtSwitch: 132.40, switchValue: 79440, taxType: 'STCG', taxAmount: 2380 },
  ],
};

const REDEMPTION_DATA = {
  chartData: [
    { schemeName: 'Axis Bluechip',    redeemedAmount: 85000,  lockInRemaining: 0     },
    { schemeName: 'SBI ELSS',         redeemedAmount: 50000,  lockInRemaining: 18000 },
    { schemeName: 'Mirae Large Cap',  redeemedAmount: 120000, lockInRemaining: 0     },
    { schemeName: 'Parag Parikh',     redeemedAmount: 40000,  lockInRemaining: 0     },
    { schemeName: 'HDFC ELSS TaxSvr', redeemedAmount: 60000,  lockInRemaining: 32000 },
    { schemeName: 'ICICI Tech Fund',  redeemedAmount: 95000,  lockInRemaining: 0     },
    { schemeName: 'Nippon Small Cap', redeemedAmount: 30000,  lockInRemaining: 0     },
    { schemeName: 'DSP Midcap',       redeemedAmount: 70000,  lockInRemaining: 0     },
  ],
  transactions: [
    { schemeName: 'Axis Bluechip Fund',         redemptionDate: '12 Mar 2024', units: 1650, navAtRedemption: 51.52,  investedAmount: 68000,  redemptionValue: 85008,  realizedGain: 17008, exitLoad: 0,   taxType: 'LTCG', bankAccount: 'HDFC ****4521',  status: 'COMPLETED' },
    { schemeName: 'SBI Long Term Equity Fund',  redemptionDate: '18 Apr 2024', units: 820,  navAtRedemption: 61.00,  investedAmount: 40000,  redemptionValue: 50020,  realizedGain: 10020, exitLoad: 0,   taxType: 'LTCG', bankAccount: 'SBI ****8834',   status: 'COMPLETED' },
    { schemeName: 'Mirae Asset Large Cap',      redemptionDate: '02 May 2024', units: 1150, navAtRedemption: 104.32, investedAmount: 100000, redemptionValue: 119968, realizedGain: 19968, exitLoad: 0,   taxType: 'LTCG', bankAccount: 'HDFC ****4521',  status: 'COMPLETED' },
    { schemeName: 'Parag Parikh Flexi Cap',     redemptionDate: '28 Jun 2024', units: 534,  navAtRedemption: 74.91,  investedAmount: 32000,  redemptionValue: 40002,  realizedGain: 8002,  exitLoad: 0,   taxType: 'LTCG', bankAccount: 'ICICI ****2290', status: 'PARTIAL'   },
    { schemeName: 'ICICI Pru Technology',       redemptionDate: '15 Aug 2024', units: 651,  navAtRedemption: 145.80, investedAmount: 80000,  redemptionValue: 94937,  realizedGain: 14937, exitLoad: 500, taxType: 'STCG', bankAccount: 'SBI ****8834',   status: 'COMPLETED' },
    { schemeName: 'Nippon India Small Cap',     redemptionDate: '05 Oct 2024', units: 220,  navAtRedemption: 136.40, investedAmount: 25000,  redemptionValue: 30008,  realizedGain: 5008,  exitLoad: 0,   taxType: 'STCG', bankAccount: 'HDFC ****4521',  status: 'COMPLETED' },
  ],
};

// ── Utility components ────────────────────────────────────────

function Sparkline({ data }) {
  const d = data.map((v, i) => ({ v, i }));
  return (
    <ResponsiveContainer width={60} height={32}>
      <LineChart data={d} margin={{ top: 4, right: 2, left: 2, bottom: 4 }}>
        <Line type="monotone" dataKey="v" dot={false} stroke={EMERALD} strokeWidth={1.5} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function StatusBadge({ status }) {
  const isActive = status === 'ACTIVE';
  return (
    <span style={{
      background: isActive ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
      color:      isActive ? EMERALD : RED,
      border:     `1px solid ${isActive ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
      borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
    }}>
      {isActive ? 'Live' : 'Paused'}
    </span>
  );
}

function TaxBadge({ taxType }) {
  const s = taxType === 'STCG'
    ? { background: 'rgba(245,158,11,0.15)', color: AMBER }
    : taxType === 'LTCG'
    ? { background: 'rgba(59,130,246,0.15)',  color: BLUE  }
    : { background: 'rgba(16,185,129,0.15)', color: EMERALD };
  return <span style={{ ...s, borderRadius: 4, padding: '2px 6px', fontSize: 11, fontWeight: 700 }}>{taxType}</span>;
}

// ── TAB: Dashboard ────────────────────────────────────────────
function DashboardTab() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Row 1: Performance donut + Top Gainers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px,380px) 1fr', gap: 20, flexWrap: 'wrap' }}>

        {/* Performance donut with center P&L label */}
        <div style={card}>
          <p style={SL}>Performance breakdown</p>
          <div style={{ position: 'relative' }}>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={PERF_DONUT_DATA} cx="50%" cy="50%" innerRadius={70} outerRadius={110}
                  dataKey="value" nameKey="name" paddingAngle={3}>
                  {PERF_DONUT_DATA.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8, fontSize: 12 }}
                  formatter={(v, n) => [formatINR(v), n]}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center label absolutely positioned */}
            <div style={{
              position: 'absolute', top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none',
            }}>
              <div style={{ fontSize: 11, color: MUTED }}>Total P&amp;L</div>
              <div style={{ fontSize: 18, fontWeight: 500, color: pnlColor(TOTAL_PNL) }}>{formatINR(TOTAL_PNL)}</div>
              <div style={{ fontSize: 12, color: EMERALD }}>{fmtPct(XIRR_PCT)} all-time</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 4 }}>
            {PERF_DONUT_DATA.map(d => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} />
                <span style={{ fontSize: 11, color: MUTED }}>{d.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Gainers table — top 5, P&L emerald, XIRR with ▲, sparkline */}
        <div style={card}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <p style={{ ...SL, marginBottom: 0 }}>Top gainers</p>
            <span style={{ fontSize: 11, color: BLUE, cursor: 'pointer' }}>See all →</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                  {['Fund', 'P&L', 'XIRR', 'Trend'].map(h => (
                    <th key={h} style={{ ...muted, textAlign: h === 'Trend' ? 'center' : 'left', padding: '6px 8px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TOP_GAINERS.map((g, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #1A1A1A' }}>
                    <td style={{ color: '#fff', padding: '8px', fontWeight: 500, fontSize: 13 }}>{g.name}</td>
                    <td style={{ color: EMERALD, padding: '8px', fontWeight: 600, fontSize: 13 }}>{formatINR(g.pnl)}</td>
                    <td style={{ color: EMERALD, padding: '8px', fontWeight: 600, fontSize: 13 }}>▲ {g.xirr.toFixed(1)}%</td>
                    <td style={{ padding: '8px', textAlign: 'center' }}><Sparkline data={g.nav} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 2: Capital Concentration + Recent Redemptions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>

        {/* Capital Concentration horizontal bars with blue gradient hierarchy */}
        <div style={card}>
          <p style={SL}>Capital concentration</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {CAPITAL_CONC.map((c, i) => {
              const ratio = c.invested / CAPITAL_MAX;
              // Blue gradient: most invested = #1D4ED8, least = #93C5FD
              const t = i / (CAPITAL_CONC.length - 1);
              const barColor = `rgb(${Math.round(29 + t * (147 - 29))},${Math.round(78 + t * (197 - 78))},${Math.round(216 + t * (253 - 216))})`;
              return (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <span style={{ fontSize: 11, color: MUTED, width: 36 }}>{c.pct.toFixed(0)}%</span>
                      <span style={{ fontSize: 13, color: '#fff' }}>{c.name}</span>
                    </div>
                    <span style={{ fontSize: 12, color: secondary.color }}>{formatINR(c.invested)}</span>
                  </div>
                  <div style={{ background: '#1A1A1A', borderRadius: 4, height: 8, position: 'relative' }}>
                    <div style={{ width: `${ratio * 100}%`, height: 8, borderRadius: 4, background: barColor }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Redemptions — red bars, ₹ label, total card */}
        <div style={card}>
          <p style={SL}>Recent redemptions</p>
          {/* Total redeemed card */}
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '8px 14px', marginBottom: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, color: MUTED }}>Total redeemed</span>
            <span style={{ fontSize: 15, fontWeight: 700, color: RED }}>{formatINR(TOTAL_REDEEMED)}</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={RECENT_REDEEM} layout="vertical" margin={{ top: 0, right: 60, left: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" tick={{ fill: MUTED, fontSize: 11 }} tickLine={false} axisLine={false} width={100} />
              <Tooltip
                contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8, fontSize: 12 }}
                formatter={v => [formatINR(v), 'Redeemed']}
              />
              <Bar dataKey="amount" fill={RED} radius={[0, 4, 4, 0]}
                label={{ position: 'right', fontSize: 11, fill: MUTED, formatter: (v) => formatINR(v) }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3: SIP Countdown */}
      <div style={card}>
        <p style={SL}>SIP countdown</p>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                {['Fund', 'Amount', 'Day', 'Next due', 'Due in'].map(h => (
                  <th key={h} style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SIP_COUNTDOWN.map((s, i) => {
                const nextColor = s.daysLeft <= 7 ? EMERALD : s.daysLeft <= 14 ? AMBER : '#fff';
                const barPct = Math.max(4, ((30 - s.daysLeft) / 30) * 100);
                return (
                  <tr key={i} style={{ borderBottom: '1px solid #1A1A1A' }}>
                    <td style={{ color: '#fff', padding: '10px', fontWeight: 500 }}>{s.name}</td>
                    <td style={{ color: '#9CA3AF', padding: '10px' }}>{formatINR(s.amount)}</td>
                    <td style={{ color: '#9CA3AF', padding: '10px' }}>{s.day}</td>
                    <td style={{ color: nextColor, padding: '10px', fontWeight: 600 }}>{s.nextDate}</td>
                    <td style={{ padding: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ flex: 1, height: 6, background: '#1A1A1A', borderRadius: 3, minWidth: 60 }}>
                          <div style={{ width: `${barPct}%`, height: 6, borderRadius: 3, background: nextColor }} />
                        </div>
                        <span style={{ fontSize: 11, color: nextColor, whiteSpace: 'nowrap' }}>{s.daysLeft}d</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}

// ── TAB: My Portfolio ─────────────────────────────────────────
function PortfolioTab() {
  const [refreshing, setRefreshing] = useState(false);

  const equity = HOLDINGS.filter(h => h.category === 'Equity');
  const gold    = HOLDINGS.filter(h => h.category === 'Gold');

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1200);
  };

  const HoldingSection = ({ title, items, dotColor }) => (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: dotColor }} />
        <p style={{ ...SL, marginBottom: 0 }}>{title}</p>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 700 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
              <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>Fund</th>
              <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>Invested</th>
              <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>Current P&amp;L</th>
              <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>XIRR</th>
              <th style={{ padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', color: MUTED }}>
                CAS Value (Live)
                <button onClick={handleRefresh} style={{ background: 'none', border: 'none', cursor: 'pointer', color: BLUE, fontSize: 12, marginLeft: 6, padding: 0 }}>
                  {refreshing ? '⟳' : '↻'}
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((h, i) => {
              const isPos = h.pnl >= 0;
              return (
                <tr key={i} style={{ borderBottom: '1px solid #1A1A1A' }}>
                  <td style={{ color: '#fff', padding: '10px', fontWeight: 500 }}>{cleanName(h.scheme)}</td>
                  <td style={{ color: '#9CA3AF', padding: '10px' }}>{formatINR(h.invested)}</td>
                  {/* Current P&L — full cell colored */}
                  <td style={{ padding: '10px', color: pnlColor(h.pnl), fontWeight: 600 }}>
                    <span style={{ color: pnlColor(h.pnl) }}>{isPos ? '▲' : '▼'}</span>{' '}
                    {formatINR(Math.abs(h.pnl))}
                  </td>
                  <td style={{ color: pnlColor(h.xirr), padding: '10px', fontWeight: 600 }}>{fmtPct(h.xirr)}</td>
                  <td style={{ color: '#9CA3AF', padding: '10px', fontStyle: 'italic', fontSize: 12 }}>
                    {refreshing ? 'Fetching…' : formatINR(h.value)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Portfolio Ledger heading — 24px, weight 500 */}
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 500, color: '#fff', margin: 0 }}>Portfolio ledger</h1>
        <p style={{ ...muted, fontSize: 13, marginTop: 4 }}>Live holdings across all fund categories</p>
      </div>

      {/* Holdings by category */}
      <div style={card}>
        <HoldingSection title="Equity funds" items={equity} dotColor={BLUE} />
        <HoldingSection title="Gold & commodities" items={gold} dotColor={AMBER} />
      </div>

      {/* Bubble Map — Invested vs XIRR scatter with sqrt radius fix */}
      <div style={card}>
        <p style={SL}>Invested vs XIRR (bubble size = investment amount)</p>
        <ResponsiveContainer width="100%" height={280}>
          <ScatterChart margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
            <XAxis type="number" dataKey="xirr" name="XIRR"
              tick={{ fill: MUTED, fontSize: 11 }} tickLine={false}
              label={{ value: 'XIRR %', position: 'insideBottom', offset: -4, fill: MUTED, fontSize: 11 }} />
            <YAxis type="number" dataKey="value" name="Current Value"
              tick={{ fill: MUTED, fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `₹${(v/100000).toFixed(0)}L`} />
            <ZAxis type="number" dataKey="z" range={[MIN_R * MIN_R, MAX_R * MAX_R]} />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0].payload;
                return (
                  <div style={{ ...card, padding: 10, fontSize: 12 }}>
                    <p style={{ color: '#fff', fontWeight: 600, marginBottom: 4 }}>{cleanName(d.name)}</p>
                    <p style={secondary}>XIRR: <span style={{ color: pnlColor(d.xirr) }}>{fmtPct(d.xirr)}</span></p>
                    <p style={secondary}>Invested: {formatINR(d.invested)}</p>
                    <p style={secondary}>Current: {formatINR(d.value)}</p>
                  </div>
                );
              }}
            />
            <Scatter data={BUBBLE_DATA} fill={BLUE} fillOpacity={0.7} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Total Realized P&L card */}
      <div style={{ ...card, padding: 20, display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 180 }}>
          <p style={SL}>Total realized P&amp;L</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 28, fontWeight: 700, color: EMERALD }}>{formatINR(REALIZED_PNL.total)}</span>
            <span style={{ fontSize: 18, color: EMERALD }}>↑</span>
          </div>
          <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 4 }}>
            <p style={{ fontSize: 12, color: MUTED }}>Equity: <span style={{ color: EMERALD }}>{formatINR(REALIZED_PNL.equity)}</span></p>
            <p style={{ fontSize: 12, color: MUTED }}>Gold: <span style={{ color: AMBER }}>{formatINR(REALIZED_PNL.gold)}</span></p>
          </div>
        </div>
        <div style={{ background: '#1A1A1A', borderRadius: 8, padding: '10px 16px', minWidth: 160 }}>
          <p style={{ fontSize: 11, color: MUTED, marginBottom: 4 }}>Fully exited schemes</p>
          <p style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>6</p>
        </div>
      </div>

    </div>
  );
}

// ── TAB: SIP Center ───────────────────────────────────────────
function SipCenterTab() {
  const [activeFilter, setActiveFilter]   = useState('ACTIVE');
  const [sortCol, setSortCol]             = useState('amount');
  const [sortDir, setSortDir]             = useState('desc');

  const live     = SIP_MANDATES.filter(m => m.status === 'ACTIVE');
  const inactive = SIP_MANDATES.filter(m => m.status === 'INACTIVE');
  const displayed = activeFilter === 'ACTIVE' ? live : inactive;

  const sorted = useMemo(() => {
    return [...displayed].sort((a, b) => {
      let av = a[sortCol], bv = b[sortCol];
      if (typeof av === 'string') av = av.toLowerCase(), bv = bv.toLowerCase();
      return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
  }, [displayed, sortCol, sortDir]);

  const toggleSort = (col) => {
    if (sortCol === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortCol(col); setSortDir('desc'); }
  };

  const SortIcon = ({ col }) => {
    if (sortCol !== col) return <span style={{ color: '#2A2A2A' }}> ↕</span>;
    return <span style={{ color: BLUE }}> {sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  // Mini donut data for the SIP allocation
  const donutData = SIP_MANDATES.map(m => ({ name: cleanName(m.scheme).slice(0, 18), value: m.amount }));
  const DONUT_COLORS = [EMERALD, BLUE, AMBER, '#8B5CF6', '#06B6D4', '#EC4899', '#F97316', '#84CC16', '#A78BFA', RED];

  // Horizontal bar chart data
  const barData = [...SIP_MANDATES]
    .sort((a, b) => b.amount - a.amount)
    .map(m => ({ name: cleanName(m.scheme).slice(0, 22), amount: m.amount, status: m.status }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Total Monthly Outflow — 3-stat grid + mini donut */}
      <div style={{ ...card, display: 'flex', gap: 24, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, minWidth: 300 }}>
          <div>
            <p style={{ ...SL, marginBottom: 4 }}>Monthly</p>
            <p style={{ fontSize: 22, fontWeight: 700, color: EMERALD }}>{formatINR(MONTHLY_TOTAL)}</p>
          </div>
          <div>
            <p style={{ ...SL, marginBottom: 4 }}>Annual commitment</p>
            <p style={{ fontSize: 18, fontWeight: 600, color: '#fff' }}>{formatINR(ANNUAL_COMMIT)}</p>
          </div>
          <div>
            <p style={{ ...SL, marginBottom: 4 }}>Next debit</p>
            <p style={{ fontSize: 16, fontWeight: 600, color: AMBER }}>10 Jun 2026</p>
          </div>
        </div>
        {/* Mini donut */}
        <div style={{ flexShrink: 0 }}>
          <PieChart width={120} height={120}>
            <Pie data={donutData} cx="50%" cy="50%" innerRadius={36} outerRadius={54}
              dataKey="value" nameKey="name" paddingAngle={2}>
              {donutData.map((_, i) => <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />)}
            </Pie>
            <Tooltip
              contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 6, fontSize: 11 }}
              formatter={v => [formatINR(v)]}
            />
          </PieChart>
        </div>
      </div>

      {/* SIP Allocation horizontal bar chart */}
      <div style={card}>
        <p style={SL}>SIP allocation by fund</p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={barData} layout="vertical" margin={{ top: 0, right: 80, left: 0, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" tick={{ fill: MUTED, fontSize: 11 }} tickLine={false} axisLine={false} width={140} />
            <Tooltip
              contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8, fontSize: 12 }}
              formatter={v => [formatINR(v), 'Monthly SIP']}
            />
            <Bar dataKey="amount" radius={[0, 4, 4, 0]}
              label={{ position: 'right', fontSize: 11, fill: MUTED, formatter: v => formatINR(v) }}>
              {barData.map((d, i) => (
                <Cell key={i} fill={d.status === 'ACTIVE' ? EMERALD : RED} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Live / Inactive tabs */}
      <div>
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          {[
            { key: 'ACTIVE',   label: `Live (${live.length})`,     ac: EMERALD, bg: '#064E3B', border: EMERALD },
            { key: 'INACTIVE', label: `Inactive (${inactive.length})`, ac: RED, bg: '#450A0A', border: RED },
          ].map(tab => {
            const isActive = activeFilter === tab.key;
            return (
              <button key={tab.key} onClick={() => setActiveFilter(tab.key)}
                style={{
                  background: isActive ? tab.bg : 'transparent',
                  color:      isActive ? tab.ac : MUTED,
                  border:     `1px solid ${isActive ? tab.border : '#2A2A2A'}`,
                  borderRadius: 6, padding: '6px 14px', fontSize: 12, fontWeight: 600, cursor: 'pointer',
                  transition: 'all 0.15s',
                }}>
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* SIP table with sorting + badges + row tinting */}
        <div style={card}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                  <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>Fund</th>
                  <th onClick={() => toggleSort('amount')} style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', cursor: 'pointer', userSelect: 'none' }}>
                    Amount<SortIcon col="amount" />
                  </th>
                  <th onClick={() => toggleSort('day')} style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', cursor: 'pointer', userSelect: 'none' }}>
                    Day<SortIcon col="day" />
                  </th>
                  <th onClick={() => toggleSort('nextDue')} style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', cursor: 'pointer', userSelect: 'none' }}>
                    Next due<SortIcon col="nextDue" />
                  </th>
                  <th style={{ ...muted, textAlign: 'left', padding: '6px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((m, i) => {
                  const isInactive = m.status === 'INACTIVE';
                  return (
                    <tr key={i} style={{
                      borderBottom: '1px solid #1A1A1A',
                      background: isInactive ? 'rgba(239,68,68,0.06)' : 'transparent',
                    }}>
                      <td style={{ color: '#fff', padding: '10px', fontWeight: 500 }}>{cleanName(m.scheme)}</td>
                      <td style={{ color: '#9CA3AF', padding: '10px' }}>{formatINR(m.amount)}</td>
                      <td style={{ color: '#9CA3AF', padding: '10px' }}>{m.day}</td>
                      <td style={{ color: '#9CA3AF', padding: '10px' }}>{m.nextDue}</td>
                      <td style={{ padding: '10px' }}><StatusBadge status={m.status} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── TAB: SWP & Switch ─────────────────────────────────────────
function SwpTab() {
  const { monthlyWithdrawals, summary, switchLog } = SWP_DATA;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={card}>
          <p style={SL}>Monthly withdrawals</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={monthlyWithdrawals} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
              <XAxis dataKey="month" tick={{ fill: MUTED, fontSize: 10 }} tickLine={false}
                tickFormatter={v => v.split(' ')[0]} />
              <YAxis tick={{ fill: MUTED, fontSize: 10 }} tickLine={false} axisLine={false}
                tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8 }}
                formatter={v => [formatINR(v), 'Withdrawn']} labelStyle={{ color: '#fff' }} />
              <Bar dataKey="amount" fill={RED} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {[
            { label: 'Total withdrawn',     value: formatINR(summary.totalWithdrawn),        color: RED     },
            { label: 'Remaining principal', value: formatINR(summary.remainingPrincipal),    color: EMERALD },
            { label: 'Monthly rate',        value: formatINR(summary.monthlyWithdrawalRate), color: '#9CA3AF' },
            { label: 'Run rate',            value: `${summary.estimatedRunRateMonths} mo`,   color: BLUE    },
          ].map(s => (
            <div key={s.label} style={{ ...card, padding: 14 }}>
              <p style={{ fontSize: 11, color: MUTED, marginBottom: 4 }}>{s.label}</p>
              <p style={{ color: s.color, fontWeight: 700, fontSize: 16 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={card}>
        <p style={SL}>Fund switch log</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {switchLog.map((sw, i) => (
            <div key={i} style={{ borderLeft: '2px dashed #2A2A2A', paddingLeft: 16, paddingBottom: i < switchLog.length - 1 ? 24 : 0, position: 'relative' }}>
              <div style={{ width: 8, height: 8, background: BLUE, borderRadius: '50%', position: 'absolute', left: -5, top: 2 }} />
              <p style={{ fontSize: 11, color: MUTED, marginBottom: 4 }}>{sw.date}</p>
              <p style={{ color: '#fff', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
                <span style={secondary}>{sw.sourceScheme}</span>
                <span style={{ color: MUTED, margin: '0 8px' }}>→</span>
                <span style={{ color: EMERALD }}>{sw.destinationScheme}</span>
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', fontSize: 12 }}>
                <span style={secondary}>{sw.unitsTransferred.toFixed(2)} units @ ₹{sw.navAtSwitch.toFixed(2)}</span>
                <span style={secondary}>· {formatINR(sw.switchValue)}</span>
                <TaxBadge taxType={sw.taxType} />
                <span style={{ color: sw.taxAmount > 0 ? RED : EMERALD, fontSize: 12 }}>
                  {sw.taxAmount > 0 ? `Tax: ${formatINR(sw.taxAmount)}` : 'No tax liability'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── TAB: Redemptions ──────────────────────────────────────────
function RedemptionsTab() {
  const { chartData, transactions } = REDEMPTION_DATA;

  const totals = useMemo(() => ({
    invested: transactions.reduce((s, t) => s + t.investedAmount,  0),
    redeemed: transactions.reduce((s, t) => s + t.redemptionValue, 0),
    gainLoss: transactions.reduce((s, t) => s + (t.redemptionValue - t.investedAmount), 0),
  }), []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={card}>
        <p style={SL}>Redemptions overview</p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
            <XAxis dataKey="schemeName" tick={{ fill: MUTED, fontSize: 11 }} tickLine={false} />
            <YAxis tick={{ fill: MUTED, fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
            <Tooltip contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8, fontSize: 12 }} />
            <Legend iconType="square" iconSize={10} wrapperStyle={{ color: '#9CA3AF', fontSize: 12 }} />
            <Bar dataKey="redeemedAmount"  name="Redeemed"          fill={RED}   stackId="a" radius={[0,0,0,0]} />
            <Bar dataKey="lockInRemaining" name="Lock-in remaining" fill={AMBER} stackId="a" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={card}>
        <p style={SL}>Redemption transactions</p>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, minWidth: 920 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                {['Scheme','Date','Units','NAV','Invested','Redeemed','Gain/Loss','Exit load','Tax','Bank','Status'].map(h => (
                  <th key={h} style={{ ...muted, textAlign: 'left', padding: '8px 10px', fontSize: 11, fontWeight: 500, letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, i) => {
                const gl = t.redemptionValue - t.investedAmount;
                const statusStyle = t.status === 'COMPLETED'
                  ? { background: 'rgba(16,185,129,0.15)', color: EMERALD }
                  : { background: 'rgba(245,158,11,0.15)',  color: AMBER  };
                return (
                  <tr key={i} style={{ borderBottom: '1px solid #1A1A1A' }}>
                    <td style={{ color: '#fff', padding: '10px', fontWeight: 500, whiteSpace: 'nowrap' }}>{t.schemeName}</td>
                    <td style={{ ...secondary, padding: '10px', whiteSpace: 'nowrap' }}>{t.redemptionDate}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>{t.units.toFixed(0)}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>₹{t.navAtRedemption.toFixed(2)}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{formatINR(t.investedAmount)}</td>
                    <td style={{ color: EMERALD, padding: '10px', fontWeight: 600 }}>{formatINR(t.redemptionValue)}</td>
                    <td style={{ padding: '10px', fontWeight: 700, color: pnlColor(gl) }}>{formatINR(gl)}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{t.exitLoad > 0 ? formatINR(t.exitLoad) : '—'}</td>
                    <td style={{ padding: '10px' }}><TaxBadge taxType={t.taxType} /></td>
                    <td style={{ ...muted, padding: '10px', whiteSpace: 'nowrap', fontSize: 11 }}>{t.bankAccount}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ ...statusStyle, borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{t.status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr style={{ borderTop: '1px solid #2A2A2A', background: '#1A1A1A' }}>
                <td colSpan={4} style={{ color: '#9CA3AF', padding: '10px', fontWeight: 700 }}>Totals</td>
                <td style={{ ...secondary, padding: '10px', fontWeight: 700 }}>{formatINR(totals.invested)}</td>
                <td style={{ color: EMERALD, padding: '10px', fontWeight: 700 }}>{formatINR(totals.redeemed)}</td>
                <td style={{ padding: '10px', fontWeight: 700, color: pnlColor(totals.gainLoss) }}>{formatINR(totals.gainLoss)}</td>
                <td colSpan={4} />
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────
const TABS = [
  { id: 'dashboard',   label: 'Dashboard'       },
  { id: 'portfolio',   label: 'My Portfolio'     },
  { id: 'sip',         label: 'SIP Center'       },
  { id: 'swp',         label: 'SWP & Switch'     },
  { id: 'redemptions', label: 'Redemptions'      },
];

export default function MutualFundDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabContent = {
    dashboard:   <DashboardTab />,
    portfolio:   <PortfolioTab />,
    sip:         <SipCenterTab />,
    swp:         <SwpTab />,
    redemptions: <RedemptionsTab />,
  };

  return (
    <div style={{ background: '#0A0A0A', minHeight: '100vh', color: '#fff', fontFamily: "'Inter','Segoe UI',sans-serif" }}>
      {/* Header */}
      <div style={{ padding: '20px 24px', borderBottom: '1px solid #1A1A1A' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#fff', margin: 0 }}>
          Mutual Fund <span style={{ color: EMERALD }}>Dashboard</span>
        </h1>
        <p style={{ color: MUTED, fontSize: 13, margin: '4px 0 0' }}>Portfolio analytics &amp; insights</p>
      </div>

      {/* Tab bar */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: '#111111', borderBottom: '1px solid #2A2A2A',
        overflowX: 'auto', whiteSpace: 'nowrap', WebkitOverflowScrolling: 'touch',
        display: 'flex',
      }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '14px 20px', fontSize: 13, fontWeight: 600,
              color: activeTab === t.id ? '#fff' : MUTED,
              borderBottom: activeTab === t.id ? `2px solid ${EMERALD}` : '2px solid transparent',
              transition: 'color 0.15s, border-color 0.15s',
              whiteSpace: 'nowrap',
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ padding: '24px', maxWidth: 1280, margin: '0 auto' }}>
        {tabContent[activeTab]}
      </div>
    </div>
  );
}
