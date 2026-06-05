import React, { useState, useMemo } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Sector,
  BarChart, Bar, Legend, RadialBarChart, RadialBar,
  defs, linearGradient, stop,
} from 'recharts';

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────
const formatINR = (v) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v ?? 0);
const fmtPct = (v) => `${(v ?? 0) >= 0 ? '+' : ''}${(v ?? 0).toFixed(2)}%`;
const safeVal = (v) => (v == null || isNaN(v) ? 0 : v);
const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4', '#EC4899'];

// ─────────────────────────────────────────────────────────────
// MOCK DATA
// ─────────────────────────────────────────────────────────────
const ALLOCATION_DATA = [
  { category: 'Large Cap',  invested: 450000,  currentValue: 558000,  color: '#10B981' },
  { category: 'Mid Cap',    invested: 300000,  currentValue: 384000,  color: '#3B82F6' },
  { category: 'Small Cap',  invested: 200000,  currentValue: 268000,  color: '#8B5CF6' },
  { category: 'Sectoral',   invested: 250000,  currentValue: 307500,  color: '#F59E0B' },
  { category: 'Debt',       invested: 180000,  currentValue: 198000,  color: '#06B6D4' },
  { category: 'Gold',       invested: 120000,  currentValue: 148800,  color: '#EC4899' },
];

const LUMPSUM_DATA = {
  summary: { totalInvested: 1500000, currentValue: 1864300, absoluteROI: 24.29 },
  growthTimeline: (() => {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const years  = [2023, 2024];
    let v = 1500000;
    return years.flatMap(y => months.map(m => {
      v = v * (1 + (Math.random() * 0.025 - 0.004));
      return { month: `${m} ${y}`, value: Math.round(v) };
    }));
  })(),
  schemes: [
    { schemeName: 'Mirae Asset Large Cap Fund', purchaseDate: '12 Jan 2023', navAtPurchase: 82.45, currentNAV: 104.32, units: 1820.50, investedAmount: 150000, currentValue: 189918 },
    { schemeName: 'Parag Parikh Flexi Cap Fund', purchaseDate: '05 Mar 2023', navAtPurchase: 54.78, currentNAV: 74.91, units: 5476.46, investedAmount: 300000, currentValue: 410264 },
    { schemeName: 'Axis Bluechip Fund', purchaseDate: '20 Jun 2022', navAtPurchase: 41.20, currentNAV: 51.60, units: 7281.55, investedAmount: 300000, currentValue: 375728 },
    { schemeName: 'ICICI Pru Technology Fund', purchaseDate: '14 Sep 2022', navAtPurchase: 120.10, currentNAV: 145.80, units: 2081.60, investedAmount: 250000, currentValue: 303497 },
    { schemeName: 'SBI Gold Fund', purchaseDate: '02 Nov 2023', navAtPurchase: 18.24, currentNAV: 22.41, units: 6578.95, investedAmount: 120000, currentValue: 147445 },
  ],
};

const SIP_DATA = {
  healthScore: 74,
  healthBreakdown: { regularity: 82, onTimePayment: 91, skipRate: 8 },
  missedOpportunities: [
    { schemeName: 'Mirae Asset Large Cap', missedDate: 'Mar 2024', missedAmount: 5000, navOnMissedDate: 94.20, navToday: 104.32, unitsWouldHaveBought: 53.08, currentValueIfInvested: 5543, opportunityCost: 543 },
    { schemeName: 'Parag Parikh Flexi Cap', missedDate: 'Jun 2024', missedAmount: 10000, navOnMissedDate: 67.50, navToday: 74.91, unitsWouldHaveBought: 148.15, currentValueIfInvested: 11097, opportunityCost: 1097 },
    { schemeName: 'Axis Bluechip Fund', missedDate: 'Aug 2024', missedAmount: 7500, navOnMissedDate: 47.80, navToday: 51.60, unitsWouldHaveBought: 156.90, currentValueIfInvested: 8096, opportunityCost: 596 },
  ],
  overlapAlerts: [
    { alertType: 'DUPLICATE_SIP', severity: 'HIGH', funds: ['Mirae Asset Large Cap Fund', 'Axis Bluechip Fund'], overlapPercent: 78, description: 'Both funds hold >75% overlap in top-10 holdings. You are effectively duplicating exposure.', recommendation: 'Consider consolidating into one large-cap fund to reduce redundancy.' },
    { alertType: 'PORTFOLIO_OVERLAP', severity: 'MEDIUM', funds: ['Parag Parikh Flexi Cap Fund', 'ICICI Pru Nifty 50 Index Fund'], overlapPercent: 42, description: '42% portfolio overlap detected between these two funds by stock holdings.', recommendation: 'Acceptable overlap but monitor — if it exceeds 60%, consider rebalancing.' },
  ],
  monthlySIPs: [
    { schemeName: 'Mirae Large Cap',     monthlyAmount: 5000,  status: 'ACTIVE', totalInstallments: 24, completedInstallments: 21, skippedInstallments: 3 },
    { schemeName: 'Parag Parikh Flexi',  monthlyAmount: 10000, status: 'ACTIVE', totalInstallments: 24, completedInstallments: 23, skippedInstallments: 1 },
    { schemeName: 'Axis Bluechip',       monthlyAmount: 7500,  status: 'ACTIVE', totalInstallments: 24, completedInstallments: 20, skippedInstallments: 4 },
    { schemeName: 'HDFC Mid Cap Opp.',   monthlyAmount: 6000,  status: 'ACTIVE', totalInstallments: 18, completedInstallments: 18, skippedInstallments: 0 },
    { schemeName: 'Nippon Small Cap',    monthlyAmount: 4000,  status: 'PAUSED', totalInstallments: 12, completedInstallments: 9,  skippedInstallments: 3 },
    { schemeName: 'SBI Gold Fund',       monthlyAmount: 2000,  status: 'ACTIVE', totalInstallments: 12, completedInstallments: 12, skippedInstallments: 0 },
  ],
};

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
    { date: '08 Apr 2024', sourceScheme: 'Axis Bluechip Fund', destinationScheme: 'Parag Parikh Flexi Cap', unitsTransferred: 1200.00, navAtSwitch: 49.20, switchValue: 59040, taxType: 'STCG', taxAmount: 1180 },
    { date: '22 Jul 2024', sourceScheme: 'SBI Liquid Fund', destinationScheme: 'Mirae Asset Large Cap', unitsTransferred: 450.75, navAtSwitch: 3421.80, switchValue: 1542797, taxType: 'NIL', taxAmount: 0 },
    { date: '10 Nov 2024', sourceScheme: 'Nippon India Small Cap', destinationScheme: 'HDFC Mid Cap Opp. Fund', unitsTransferred: 600.00, navAtSwitch: 132.40, switchValue: 79440, taxType: 'STCG', taxAmount: 2380 },
  ],
};

const REDEMPTION_DATA = {
  chartData: [
    { schemeName: 'Axis Bluechip',    redeemedAmount: 85000,  lockInRemaining: 0 },
    { schemeName: 'SBI ELSS',         redeemedAmount: 50000,  lockInRemaining: 18000 },
    { schemeName: 'Mirae Large Cap',  redeemedAmount: 120000, lockInRemaining: 0 },
    { schemeName: 'Parag Parikh',     redeemedAmount: 40000,  lockInRemaining: 0 },
    { schemeName: 'HDFC ELSS TaxSvr', redeemedAmount: 60000,  lockInRemaining: 32000 },
    { schemeName: 'ICICI Tech Fund',  redeemedAmount: 95000,  lockInRemaining: 0 },
    { schemeName: 'Nippon Small Cap', redeemedAmount: 30000,  lockInRemaining: 0 },
    { schemeName: 'DSP Midcap',       redeemedAmount: 70000,  lockInRemaining: 0 },
  ],
  transactions: [
    { schemeName: 'Axis Bluechip Fund', redemptionDate: '12 Mar 2024', units: 1650, navAtRedemption: 51.52, investedAmount: 68000, redemptionValue: 85008, realizedGain: 17008, exitLoad: 0, taxType: 'LTCG', bankAccount: 'HDFC ****4521', status: 'COMPLETED' },
    { schemeName: 'SBI Long Term Equity Fund', redemptionDate: '18 Apr 2024', units: 820, navAtRedemption: 61.00, investedAmount: 40000, redemptionValue: 50020, realizedGain: 10020, exitLoad: 0, taxType: 'LTCG', bankAccount: 'SBI ****8834', status: 'COMPLETED' },
    { schemeName: 'Mirae Asset Large Cap', redemptionDate: '02 May 2024', units: 1150, navAtRedemption: 104.32, investedAmount: 100000, redemptionValue: 119968, realizedGain: 19968, exitLoad: 0, taxType: 'LTCG', bankAccount: 'HDFC ****4521', status: 'COMPLETED' },
    { schemeName: 'Parag Parikh Flexi Cap', redemptionDate: '28 Jun 2024', units: 534, navAtRedemption: 74.91, investedAmount: 32000, redemptionValue: 40002, realizedGain: 8002, exitLoad: 0, taxType: 'LTCG', bankAccount: 'ICICI ****2290', status: 'PARTIAL' },
    { schemeName: 'ICICI Pru Technology', redemptionDate: '15 Aug 2024', units: 651, navAtRedemption: 145.80, investedAmount: 80000, redemptionValue: 94937, realizedGain: 14937, exitLoad: 500, taxType: 'STCG', bankAccount: 'SBI ****8834', status: 'COMPLETED' },
    { schemeName: 'Nippon India Small Cap', redemptionDate: '05 Oct 2024', units: 220, navAtRedemption: 136.40, investedAmount: 25000, redemptionValue: 30008, realizedGain: 5008, exitLoad: 0, taxType: 'STCG', bankAccount: 'HDFC ****4521', status: 'COMPLETED' },
  ],
};

// ─────────────────────────────────────────────────────────────
// SHARED STYLES
// ─────────────────────────────────────────────────────────────
const card = { background: '#111111', border: '1px solid #2A2A2A', borderRadius: 12, padding: 20 };
const muted = { color: '#6B7280' };
const secondary = { color: '#9CA3AF' };
const positive = { color: '#10B981' };
const negative = { color: '#EF4444' };

// ─────────────────────────────────────────────────────────────
// TAB A — ASSET ALLOCATION
// ─────────────────────────────────────────────────────────────
function AllocationTab() {
  const [activeIndex, setActiveIndex] = useState(null);

  const totalInvested     = useMemo(() => ALLOCATION_DATA.reduce((s, d) => s + d.invested, 0),     []);
  const totalCurrentValue = useMemo(() => ALLOCATION_DATA.reduce((s, d) => s + d.currentValue, 0), []);

  const tableData = useMemo(() =>
    ALLOCATION_DATA.map(d => ({
      ...d,
      gain: d.currentValue - d.invested,
      allocationPct: (d.currentValue / totalCurrentValue) * 100,
    })), [totalCurrentValue]);

  const renderActiveShape = (props) => {
    const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill } = props;
    return (
      <Sector cx={cx} cy={cy} innerRadius={innerRadius - 4} outerRadius={outerRadius + 8}
        startAngle={startAngle} endAngle={endAngle} fill={fill} />
    );
  };

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div style={{ ...card, padding: 12 }}>
        <p style={{ color: d.color, fontWeight: 700, marginBottom: 4 }}>{d.category}</p>
        <p style={secondary}>Value: {formatINR(d.currentValue)}</p>
        <p style={secondary}>Alloc: {((d.currentValue / totalCurrentValue) * 100).toFixed(2)}%</p>
      </div>
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
      {/* Donut Chart */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Portfolio Allocation</h3>
        <ResponsiveContainer width="100%" height={320}>
          <PieChart>
            <defs>
              {ALLOCATION_DATA.map((d, i) => (
                <radialGradient key={i} id={`ag${i}`} cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor={d.color} stopOpacity={0.9} />
                  <stop offset="100%" stopColor={d.color} stopOpacity={0.6} />
                </radialGradient>
              ))}
            </defs>
            <Pie data={ALLOCATION_DATA} cx="50%" cy="50%" innerRadius={80} outerRadius={130}
              dataKey="currentValue" nameKey="category"
              activeIndex={activeIndex} activeShape={renderActiveShape}
              onMouseEnter={(_, i) => setActiveIndex(i)}
              onMouseLeave={() => setActiveIndex(null)}>
              {ALLOCATION_DATA.map((d, i) => <Cell key={d.category} fill={d.color} />)}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <text x="50%" y="46%" textAnchor="middle" fill="#9CA3AF" fontSize={13}>Portfolio</text>
            <text x="50%" y="55%" textAnchor="middle" fill="#fff" fontSize={15} fontWeight={700}>
              {formatINR(totalCurrentValue)}
            </text>
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Breakdown Table */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Breakdown</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {tableData.map(d => (
            <div key={d.category} style={{ background: '#1A1A1A', borderRadius: 8, padding: '10px 14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: d.color, flexShrink: 0 }} />
                  <span style={{ color: '#fff', fontWeight: 600, fontSize: 13 }}>{d.category}</span>
                </div>
                <span style={{ color: '#fff', fontWeight: 700, fontSize: 13 }}>{d.allocationPct.toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                <span style={secondary}>Inv: {formatINR(d.invested)}</span>
                <span style={secondary}>Now: {formatINR(d.currentValue)}</span>
                <span style={d.gain >= 0 ? positive : negative}>{formatINR(d.gain)}</span>
              </div>
              <div style={{ background: '#2A2A2A', borderRadius: 4, height: 4 }}>
                <div style={{ width: `${d.allocationPct}%`, height: 4, borderRadius: 4, background: d.color }} />
              </div>
            </div>
          ))}
          {/* Totals row */}
          <div style={{ background: '#1E1E1E', border: '1px solid #3A3A3A', borderRadius: 8, padding: '10px 14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#fff', fontWeight: 700 }}>Total</span>
              <div style={{ display: 'flex', gap: 16, fontSize: 13 }}>
                <span style={secondary}>{formatINR(totalInvested)}</span>
                <span style={{ color: '#10B981', fontWeight: 700 }}>{formatINR(totalCurrentValue)}</span>
                <span style={positive}>{formatINR(totalCurrentValue - totalInvested)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// TAB B — LUMPSUM SUMMARY
// ─────────────────────────────────────────────────────────────
function LumpsumTab() {
  const { summary, growthTimeline, schemes } = LUMPSUM_DATA;

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div style={{ ...card, padding: 10 }}>
        <p style={secondary}>{label}</p>
        <p style={{ color: '#10B981', fontWeight: 700 }}>{formatINR(payload[0]?.value)}</p>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        {[
          { label: 'Total Lumpsum Invested', value: formatINR(summary.totalInvested), color: '#9CA3AF' },
          { label: 'Current Value',           value: formatINR(summary.currentValue),  color: '#10B981' },
          { label: 'Absolute ROI',            value: fmtPct(summary.absoluteROI),       color: summary.absoluteROI >= 0 ? '#10B981' : '#EF4444' },
        ].map(s => (
          <div key={s.label} style={card}>
            <p style={{ ...muted, fontSize: 12, marginBottom: 8 }}>{s.label}</p>
            <p style={{ color: s.color, fontSize: 22, fontWeight: 700 }}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Growth chart */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Growth Trajectory</h3>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={growthTimeline} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
            <defs>
              <linearGradient id="lumpsumGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#10B981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
            <XAxis dataKey="month" tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false}
              interval={3} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `₹${(v / 100000).toFixed(1)}L`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2}
              fill="url(#lumpsumGradient)"
              dot={(props) => {
                const isLast = props.index === growthTimeline.length - 1;
                return isLast ? <circle key={props.index} cx={props.cx} cy={props.cy} r={5} fill="#10B981" stroke="#111" strokeWidth={2} /> : <React.Fragment key={props.index} />;
              }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Scheme table */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Scheme Breakdown</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 780 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                {['Scheme Name','Purchase Date','NAV @ Buy','Current NAV','Units','Invested','Current Value','Return %'].map(h => (
                  <th key={h} style={{ ...muted, textAlign: 'left', padding: '8px 10px', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {schemes.map(s => {
                const ret = ((s.currentValue - s.investedAmount) / s.investedAmount) * 100;
                return (
                  <tr key={s.schemeName} style={{ borderBottom: '1px solid #1A1A1A' }}>
                    <td style={{ color: '#fff', padding: '10px', fontWeight: 500 }}>{s.schemeName}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{s.purchaseDate}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>₹{s.navAtPurchase.toFixed(4)}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>₹{s.currentNAV.toFixed(4)}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>{s.units.toFixed(2)}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{formatINR(s.investedAmount)}</td>
                    <td style={{ color: '#10B981', padding: '10px', fontWeight: 600 }}>{formatINR(s.currentValue)}</td>
                    <td style={{ padding: '10px', fontWeight: 700, color: ret >= 0 ? '#10B981' : '#EF4444' }}>{fmtPct(ret)}</td>
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

// ─────────────────────────────────────────────────────────────
// TAB C — SIP HEALTH & ANALYTICS
// ─────────────────────────────────────────────────────────────
function SipTab() {
  const { healthScore, healthBreakdown, missedOpportunities, overlapAlerts, monthlySIPs } = SIP_DATA;
  const scoreColor = healthScore >= 75 ? '#10B981' : healthScore >= 50 ? '#F59E0B' : '#EF4444';
  const totalOpportunityCost = missedOpportunities.reduce((s, m) => s + m.opportunityCost, 0);

  const radialData = [{ name: 'Health', value: healthScore, fill: scoreColor }];

  const CustomRadialTooltip = () => null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Health Score */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 4 }}>SIP Health Score</h3>
        <p style={{ ...muted, fontSize: 12, marginBottom: 16 }}>Based on regularity, on-time payments, and skip rate</p>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 24 }}>
          <div style={{ position: 'relative', width: 200, height: 160, flexShrink: 0 }}>
            <ResponsiveContainer width={200} height={160}>
              <RadialBarChart cx="50%" cy="70%" innerRadius={55} outerRadius={85}
                startAngle={180} endAngle={0} data={radialData} barSize={16}>
                <RadialBar background={{ fill: '#1A1A1A' }} dataKey="value" cornerRadius={8} />
                <text x="50%" y="68%" textAnchor="middle" fill={scoreColor} fontSize={32} fontWeight={800}>{healthScore}</text>
                <text x="50%" y="85%" textAnchor="middle" fill="#6B7280" fontSize={12}>/100</text>
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {[
              { label: 'Regularity', value: healthBreakdown.regularity, color: '#10B981' },
              { label: 'On-Time', value: healthBreakdown.onTimePayment, color: '#3B82F6' },
              { label: 'Skip Rate', value: healthBreakdown.skipRate, color: '#EF4444', suffix: '% skipped' },
            ].map(p => (
              <div key={p.label} style={{ background: '#1A1A1A', borderRadius: 8, padding: '10px 16px', textAlign: 'center', minWidth: 100 }}>
                <p style={{ color: p.color, fontSize: 22, fontWeight: 700 }}>{p.value}{p.suffix ? '' : '%'}</p>
                <p style={{ ...muted, fontSize: 11, marginTop: 2 }}>{p.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SIP Mandate Bar Chart */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Active SIP Mandates</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={monthlySIPs} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
            <XAxis dataKey="schemeName" tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8 }} labelStyle={{ color: '#fff' }} itemStyle={{ color: '#9CA3AF' }} />
            <Legend iconType="square" iconSize={10} wrapperStyle={{ color: '#9CA3AF', fontSize: 12 }} />
            <Bar dataKey="completedInstallments" name="Completed" fill="#10B981" radius={[4, 4, 0, 0]} />
            <Bar dataKey="skippedInstallments"   name="Skipped"   fill="#EF4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Missed Opportunities */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <span style={{ fontSize: 18 }}>⚠️</span>
          <h3 style={{ color: '#fff', fontWeight: 700 }}>Missed SIP Opportunities — Wealth Left on the Table</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {missedOpportunities.map((m, i) => (
            <div key={i} style={{ background: '#1A1A1A', borderRadius: 8, padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
              <div>
                <p style={{ color: '#fff', fontWeight: 600, marginBottom: 2 }}>{m.schemeName}</p>
                <p style={{ ...muted, fontSize: 12 }}>Missed: {m.missedDate} · Skipped: {formatINR(m.missedAmount)}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <p style={{ color: '#10B981', fontWeight: 600 }}>Would be {formatINR(m.currentValueIfInvested)} today</p>
                <p style={{ color: '#EF4444', fontSize: 13 }}>Cost: {formatINR(m.opportunityCost)}</p>
              </div>
            </div>
          ))}
          <div style={{ textAlign: 'right', marginTop: 8 }}>
            <span style={{ ...muted, fontSize: 13 }}>Total Opportunity Cost: </span>
            <span style={{ color: '#EF4444', fontWeight: 800, fontSize: 20 }}>{formatINR(totalOpportunityCost)}</span>
          </div>
        </div>
      </div>

      {/* Overlap Alerts */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Portfolio Overlap &amp; Duplicate Alerts</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {(overlapAlerts || []).map((a, i) => {
            const isHigh   = a.severity === 'HIGH';
            const borderClr = isHigh ? '#EF4444' : '#F59E0B';
            const badgeClr  = isHigh ? { background: 'rgba(239,68,68,0.15)', color: '#EF4444' } : { background: 'rgba(245,158,11,0.15)', color: '#F59E0B' };
            return (
              <div key={i} style={{ borderLeft: `4px solid ${borderClr}`, background: '#1A1A1A', borderRadius: '0 8px 8px 0', padding: '14px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
                  <span style={{ ...badgeClr, borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{a.severity}</span>
                  <span style={{ color: '#9CA3AF', fontSize: 12, fontWeight: 600 }}>{a.alertType.replace(/_/g, ' ')}</span>
                  <span style={{ color: borderClr, fontSize: 22, fontWeight: 800, marginLeft: 'auto' }}>{a.overlapPercent}% overlap</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                  {a.funds.map(f => (
                    <span key={f} style={{ background: '#2A2A2A', color: '#e2e8f0', borderRadius: 4, padding: '2px 8px', fontSize: 12 }}>{f}</span>
                  ))}
                </div>
                <p style={{ color: '#9CA3AF', fontSize: 13, marginBottom: 4 }}>{a.description}</p>
                <p style={{ ...muted, fontSize: 12 }}>💡 {a.recommendation}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// TAB D — SWP & SWITCH
// ─────────────────────────────────────────────────────────────
function SwpTab() {
  const { monthlyWithdrawals, summary, switchLog } = SWP_DATA;

  const taxBadge = (taxType) => {
    const s = taxType === 'STCG'
      ? { background: 'rgba(245,158,11,0.15)', color: '#F59E0B' }
      : taxType === 'LTCG'
      ? { background: 'rgba(59,130,246,0.15)', color: '#3B82F6' }
      : { background: 'rgba(16,185,129,0.15)', color: '#10B981' };
    return (
      <span style={{ ...s, borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 700 }}>{taxType}</span>
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
      {/* SWP Tracker */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={card}>
          <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Monthly Withdrawals</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={monthlyWithdrawals} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
              <XAxis dataKey="month" tick={{ fill: '#6B7280', fontSize: 10 }} tickLine={false}
                tickFormatter={v => v.split(' ')[0]} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} tickLine={false} axisLine={false}
                tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #2A2A2A', borderRadius: 8 }}
                formatter={v => [formatINR(v), 'Withdrawn']} labelStyle={{ color: '#fff' }} />
              <Bar dataKey="amount" fill="#EF4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {[
            { label: 'Total Withdrawn',     value: formatINR(summary.totalWithdrawn),       color: '#EF4444' },
            { label: 'Remaining Principal', value: formatINR(summary.remainingPrincipal),   color: '#10B981' },
            { label: 'Monthly Rate',        value: formatINR(summary.monthlyWithdrawalRate), color: '#9CA3AF' },
            { label: 'Run Rate',            value: `${summary.estimatedRunRateMonths} mo`,  color: '#3B82F6' },
          ].map(s => (
            <div key={s.label} style={{ ...card, padding: 14 }}>
              <p style={{ ...muted, fontSize: 11, marginBottom: 4 }}>{s.label}</p>
              <p style={{ color: s.color, fontWeight: 700, fontSize: 16 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Switch Log */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Fund Switch Log</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {switchLog.map((sw, i) => (
            <div key={i} style={{ borderLeft: '2px dashed #2A2A2A', paddingLeft: 16, paddingBottom: i < switchLog.length - 1 ? 24 : 0, position: 'relative' }}>
              <div style={{ width: 8, height: 8, background: '#3B82F6', borderRadius: '50%', position: 'absolute', left: -5, top: 2 }} />
              <p style={{ ...muted, fontSize: 11, marginBottom: 4 }}>{sw.date}</p>
              <p style={{ color: '#fff', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
                <span style={secondary}>{sw.sourceScheme}</span>
                <span style={{ color: '#6B7280', margin: '0 8px' }}>→</span>
                <span style={{ color: '#10B981' }}>{sw.destinationScheme}</span>
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', fontSize: 12 }}>
                <span style={secondary}>{sw.unitsTransferred.toFixed(2)} units @ ₹{sw.navAtSwitch.toFixed(2)}</span>
                <span style={secondary}>· {formatINR(sw.switchValue)}</span>
                {taxBadge(sw.taxType)}
                <span style={{ color: sw.taxAmount > 0 ? '#EF4444' : '#10B981', fontSize: 12 }}>
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

// ─────────────────────────────────────────────────────────────
// TAB E — REDEMPTIONS
// ─────────────────────────────────────────────────────────────
function RedemptionsTab() {
  const { chartData, transactions } = REDEMPTION_DATA;

  const totals = useMemo(() => ({
    invested:  transactions.reduce((s, t) => s + t.investedAmount,   0),
    redeemed:  transactions.reduce((s, t) => s + t.redemptionValue,  0),
    gainLoss:  transactions.reduce((s, t) => s + (t.redemptionValue - t.investedAmount), 0),
  }), []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const hasLock = payload.find(p => p.dataKey === 'lockInRemaining')?.value > 0;
    return (
      <div style={{ ...card, padding: 10, fontSize: 12 }}>
        <p style={{ color: '#fff', fontWeight: 600, marginBottom: 4 }}>{label}</p>
        {payload.map(p => (
          <p key={p.dataKey} style={{ color: p.fill }}>{p.name}: {formatINR(p.value)}</p>
        ))}
        {hasLock && <p style={{ color: '#F59E0B', marginTop: 4 }}>⚠️ ELSS Lock-in Active</p>}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Stacked bar chart */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Redemptions Overview</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
            <XAxis dataKey="schemeName" tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend iconType="square" iconSize={10} wrapperStyle={{ color: '#9CA3AF', fontSize: 12 }} />
            <Bar dataKey="redeemedAmount"  name="Redeemed"           fill="#10B981" stackId="a" radius={[0, 0, 0, 0]} />
            <Bar dataKey="lockInRemaining" name="Lock-in Remaining"  fill="#F59E0B" stackId="a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Transactions table */}
      <div style={card}>
        <h3 style={{ color: '#fff', fontWeight: 700, marginBottom: 16 }}>Redemption Transactions</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, minWidth: 920 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2A2A2A' }}>
                {['Scheme','Date','Units','NAV','Invested','Redeemed','Gain/Loss','Exit Load','Tax','Bank','Status'].map(h => (
                  <th key={h} style={{ ...muted, textAlign: 'left', padding: '8px 10px', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, i) => {
                const gainLoss = t.redemptionValue - t.investedAmount;
                const statusStyle = t.status === 'COMPLETED'
                  ? { background: 'rgba(16,185,129,0.15)', color: '#10B981' }
                  : { background: 'rgba(245,158,11,0.15)', color: '#F59E0B' };
                return (
                  <tr key={i} style={{ borderBottom: '1px solid #1A1A1A' }}>
                    <td style={{ color: '#fff', padding: '10px', fontWeight: 500, whiteSpace: 'nowrap' }}>{t.schemeName}</td>
                    <td style={{ ...secondary, padding: '10px', whiteSpace: 'nowrap' }}>{t.redemptionDate}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>{t.units.toFixed(0)}</td>
                    <td style={{ ...secondary, padding: '10px', fontFamily: 'monospace' }}>₹{t.navAtRedemption.toFixed(2)}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{formatINR(t.investedAmount)}</td>
                    <td style={{ color: '#10B981', padding: '10px', fontWeight: 600 }}>{formatINR(t.redemptionValue)}</td>
                    <td style={{ padding: '10px', fontWeight: 700, color: gainLoss >= 0 ? '#10B981' : '#EF4444' }}>{formatINR(gainLoss)}</td>
                    <td style={{ ...secondary, padding: '10px' }}>{t.exitLoad > 0 ? formatINR(t.exitLoad) : '—'}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ background: t.taxType === 'STCG' ? 'rgba(245,158,11,0.15)' : 'rgba(59,130,246,0.15)', color: t.taxType === 'STCG' ? '#F59E0B' : '#3B82F6', borderRadius: 4, padding: '2px 6px', fontSize: 11, fontWeight: 700 }}>{t.taxType}</span>
                    </td>
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
                <td style={{ color: '#10B981', padding: '10px', fontWeight: 700 }}>{formatINR(totals.redeemed)}</td>
                <td style={{ padding: '10px', fontWeight: 700, color: totals.gainLoss >= 0 ? '#10B981' : '#EF4444' }}>{formatINR(totals.gainLoss)}</td>
                <td colSpan={4} />
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────
const TABS = [
  { id: 'allocation',  label: 'Asset Allocation' },
  { id: 'lumpsum',     label: 'Lumpsum Summary' },
  { id: 'sip',         label: 'SIP Health & Analytics' },
  { id: 'swp',         label: 'SWP & Switch' },
  { id: 'redemptions', label: 'Redemptions' },
];

export default function MutualFundDashboard() {
  const [activeTab, setActiveTab] = useState('allocation');

  const tabContent = {
    allocation:  <AllocationTab />,
    lumpsum:     <LumpsumTab />,
    sip:         <SipTab />,
    swp:         <SwpTab />,
    redemptions: <RedemptionsTab />,
  };

  return (
    <div style={{ background: '#0A0A0A', minHeight: '100vh', color: '#fff', fontFamily: "'Inter', 'Segoe UI', sans-serif" }}>
      {/* Header */}
      <div style={{ padding: '20px 24px', borderBottom: '1px solid #1A1A1A' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#fff', margin: 0 }}>
          Mutual Fund <span style={{ color: '#10B981' }}>Dashboard</span>
        </h1>
        <p style={{ color: '#6B7280', fontSize: 13, margin: '4px 0 0' }}>Portfolio analytics & insights</p>
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
              color: activeTab === t.id ? '#fff' : '#6B7280',
              borderBottom: activeTab === t.id ? '2px solid #10B981' : '2px solid transparent',
              transition: 'color 0.15s, border-color 0.15s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => { if (activeTab !== t.id) e.target.style.color = '#9CA3AF'; }}
            onMouseLeave={e => { if (activeTab !== t.id) e.target.style.color = '#6B7280'; }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ padding: '24px', maxWidth: 1280, margin: '0 auto' }}>
        {tabContent[activeTab]}
      </div>
    </div>
  );
}
