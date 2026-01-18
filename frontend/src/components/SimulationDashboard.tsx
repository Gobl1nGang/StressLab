"use client";
import React, { useEffect, useRef } from 'react';
import { SimulationState, SimulationResults } from '../lib/simulationApi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, TrendingUp, DollarSign, History, CheckCircle2, Zap } from 'lucide-react';

interface SimulationDashboardProps {
    states: SimulationState[];
    results: SimulationResults | null;
    isSimulating: boolean;
}

export default function SimulationDashboard({ states, results, isSimulating }: SimulationDashboardProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [states]);

    if (states.length === 0 && !isSimulating) {
        return <div className="text-[#474d57] italic text-sm">Run a simulation to see real-time playback.</div>;
    }

    const latestState = states[states.length - 1];

    const chartData = states.map((s, idx) => ({
        index: idx,
        price: s.price,
        equity: s.equity,
        date: s.date.split(' ')[0]
    }));

    const trades = states.filter(s => s.trade !== null).map(s => s.trade!);

    return (
        <div className="space-y-6">
            {/* Real-Time Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { label: 'Current Price', value: `$${latestState?.price.toFixed(2) || '0.00'}`, icon: DollarSign, color: 'text-[#eaecef]' },
                    { label: 'Live Equity', value: `$${latestState?.equity.toFixed(2) || '0.00'}`, icon: Activity, color: latestState?.equity >= 10000 ? 'text-[#02c076]' : 'text-[#f6465d]' },
                    { label: 'Return', value: `${latestState?.return_pct.toFixed(2) || '0.00'}%`, icon: TrendingUp, color: latestState?.return_pct >= 0 ? 'text-[#02c076]' : 'text-[#f6465d]' },
                    { label: 'Trade Count', value: latestState?.total_trades || 0, icon: History, color: 'text-[#f0b90b]' },
                ].map((stat, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-4 bg-[#1e2329] border border-[#2b3139] rounded shadow-sm hover:border-[#474d57] transition-all"
                    >
                        <div className="flex items-center space-x-2 mb-2">
                            <stat.icon className="w-3.5 h-3.5 text-[#848e9c]" />
                            <p className="text-[#848e9c] text-[10px] font-bold uppercase tracking-wider">{stat.label}</p>
                        </div>
                        <p className={`text-xl font-mono font-bold ${stat.color}`}>{stat.value}</p>
                    </motion.div>
                ))}
            </div>

            {/* Live Chart */}
            <div className="p-6 bg-[#1e2329] rounded border border-[#2b3139] relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[#f0b90b]"></div>
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-[#f0b90b]" />
                        <h2 className="text-sm font-bold text-[#eaecef]">LIVE EXECUTION ENGINE</h2>
                    </div>
                    {isSimulating && (
                        <div className="flex items-center space-x-2 bg-[#f6465d]/10 px-2 py-1 rounded border border-[#f6465d]/20">
                            <div className="w-2 h-2 bg-[#f6465d] rounded-full animate-pulse"></div>
                            <span className="text-[10px] font-bold text-[#f6465d] uppercase tracking-tighter">Streaming Data</span>
                        </div>
                    )}
                </div>
                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#f0b90b" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#f0b90b" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" vertical={false} />
                            <XAxis dataKey="date" stroke="#474d57" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#474d57" fontSize={10} tickLine={false} axisLine={false} domain={['auto', 'auto']} tickFormatter={(v) => `$${v}`} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e2329', border: '1px solid #2b3139', borderRadius: '4px', fontSize: '12px' }}
                                itemStyle={{ color: '#f0b90b' }}
                            />
                            <Area type="monotone" dataKey="equity" stroke="#f0b90b" fillOpacity={1} fill="url(#colorEquity)" strokeWidth={2} isAnimationActive={false} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Trade Log */}
                <div className="lg:col-span-2 p-4 bg-[#1e2329] rounded border border-[#2b3139]">
                    <h2 className="text-xs font-bold text-[#eaecef] mb-4 uppercase tracking-widest border-b border-[#2b3139] pb-2">Execution Log</h2>
                    <div ref={scrollRef} className="max-h-60 overflow-y-auto space-y-1.5 pr-2 custom-scrollbar">
                        <AnimatePresence>
                            {trades.length === 0 ? (
                                <p className="text-[#474d57] text-[10px] italic py-4">Scanning for entry signals...</p>
                            ) : (
                                trades.map((trade, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -5 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="flex justify-between items-center p-2.5 bg-[#0b0e11]/50 rounded border border-[#2b3139] hover:border-[#474d57] transition-all"
                                    >
                                        <div className="flex items-center space-x-4">
                                            <span className={`text-[10px] font-bold w-12 text-center py-0.5 rounded ${trade.type === 'BUY' ? 'bg-[#02c076]/10 text-[#02c076]' : 'bg-[#f6465d]/10 text-[#f6465d]'}`}>
                                                {trade.type}
                                            </span>
                                            <span className="text-[10px] font-mono text-[#848e9c]">{trade.date}</span>
                                        </div>
                                        <div className="text-[10px] font-mono">
                                            <span className="text-[#848e9c]">Price:</span> <span className="text-[#eaecef]">${trade.price.toFixed(2)}</span>
                                            <span className="mx-2 text-[#2b3139]">|</span>
                                            <span className="text-[#848e9c]">Size:</span> <span className="text-[#eaecef]">{trade.shares.toFixed(4)}</span>
                                        </div>
                                    </motion.div>
                                ))
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Final Results Summary */}
                <div className="lg:col-span-1">
                    {results ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="p-5 bg-gradient-to-br from-[#1e2329] to-[#0b0e11] rounded border border-[#f0b90b]/30 relative overflow-hidden h-full"
                        >
                            <div className="absolute top-0 right-0 p-2">
                                <CheckCircle2 className="w-8 h-8 text-[#02c076]/20" />
                            </div>
                            <h2 className="text-xs font-bold text-[#f0b90b] mb-4 uppercase tracking-widest">Session Summary</h2>
                            <div className="space-y-4">
                                <div>
                                    <p className="text-[#848e9c] text-[10px] uppercase">Final Return</p>
                                    <p className={`text-lg font-bold ${results.total_return >= 0 ? 'text-[#02c076]' : 'text-[#f6465d]'}`}>
                                        ${results.total_return.toFixed(2)}
                                        <span className="ml-2 text-xs font-normal">({results.return_percentage.toFixed(2)}%)</span>
                                    </p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-[#848e9c] text-[10px] uppercase">Peak Equity</p>
                                        <p className="text-sm font-bold text-[#eaecef] font-mono">${results.max_equity.toFixed(2)}</p>
                                    </div>
                                    <div>
                                        <p className="text-[#848e9c] text-[10px] uppercase">Drawdown</p>
                                        <p className="text-sm font-bold text-[#f6465d] font-mono">${(results.max_equity - results.min_equity).toFixed(2)}</p>
                                    </div>
                                </div>
                                <div className="pt-4 border-t border-[#2b3139]">
                                    <p className="text-[#848e9c] text-[10px]">DURATION: {results.days_simulated} MARKET DAYS</p>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="p-5 bg-[#1e2329] rounded border border-[#2b3139] border-dashed h-full flex flex-col items-center justify-center text-center">
                            <Activity className="w-8 h-8 text-[#2b3139] mb-2" />
                            <p className="text-[10px] text-[#474d57] uppercase font-bold">Simulator Standby</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
