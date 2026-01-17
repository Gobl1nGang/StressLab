"use client";
import React from 'react';
import { BacktestResponse, AnalysisResponse } from '../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, History, ShieldAlert, CheckCircle2, Info } from 'lucide-react';

interface DashboardProps {
    backtestResults: BacktestResponse | null;
    analysisResults: AnalysisResponse | null;
}

export default function Dashboard({ backtestResults, analysisResults }: DashboardProps) {
    if (!backtestResults) {
        return (
            <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-[#2b3139] rounded-xl text-[#848e9c]">
                <TrendingUp className="w-12 h-12 mb-4 opacity-20" />
                <p>Configure a strategy and run simulation to see market analytics.</p>
            </div>
        );
    }

    const chartData = backtestResults.equity_curve.map((val, idx) => ({
        index: idx,
        equity: val
    }));

    const isHighRisk = analysisResults && analysisResults.failure_probability > 0.6;
    const isMediumRisk = analysisResults && analysisResults.failure_probability > 0.3 && analysisResults.failure_probability <= 0.6;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="binance-card p-4">
                    <p className="text-sm text-[#848e9c] mb-1">Final Equity</p>
                    <div className="flex items-baseline space-x-2">
                        <span className="text-2xl font-bold text-[#eaecef]">${backtestResults.final_capital.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                        <span className={`text-xs ${backtestResults.final_capital >= 10000 ? 'text-[#0ecb81]' : 'text-[#f6465d]'}`}>
                            {((backtestResults.final_capital - 10000) / 100).toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div className="binance-card p-4">
                    <p className="text-sm text-[#848e9c] mb-1">Total Signals</p>
                    <p className="text-2xl font-bold text-[#eaecef]">{backtestResults.trades.length}</p>
                </div>
                <div className="binance-card p-4">
                    <p className="text-sm text-[#848e9c] mb-1">Win Rate (Est.)</p>
                    <p className="text-2xl font-bold text-[#0ecb81]">--%</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Chart Section */}
                <div className="lg:col-span-2 binance-card p-6 overflow-hidden">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-lg flex items-center space-x-2">
                            <TrendingUp className="w-5 h-5 text-[#f0b90b]" />
                            <span>Equity Performance</span>
                        </h3>
                        <div className="flex space-x-2">
                            <span className="px-2 py-1 bg-[#2b3139] text-[#848e9c] text-[10px] rounded uppercase font-bold">Historical</span>
                        </div>
                    </div>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f0b90b" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#f0b90b" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" vertical={false} />
                                <XAxis
                                    dataKey="index"
                                    stroke="#474d57"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <YAxis
                                    stroke="#474d57"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => `$${val}`}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e2329', border: '1px solid #2b3139', borderRadius: '4px' }}
                                    itemStyle={{ color: '#f0b90b' }}
                                />
                                <Area type="monotone" dataKey="equity" stroke="#f0b90b" strokeWidth={2} fillOpacity={1} fill="url(#colorEquity)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Falsifier Results */}
                <div className="lg:col-span-1 border-l border-[#2b3139] lg:border-l-0">
                    {analysisResults && (
                        <div className={`binance-card p-6 h-full border-l-4 ${isHighRisk ? 'border-[#f6465d]' : isMediumRisk ? 'border-[#f0b90b]' : 'border-[#0ecb81]'}`}>
                            <div className="flex items-center space-x-2 mb-4 text-[#848e9c]">
                                <ShieldAlert className="w-4 h-4" />
                                <span className="text-sm font-bold uppercase tracking-wider">Falsification Report</span>
                            </div>

                            <div className="mb-6">
                                <div className="text-4xl font-bold mb-1">
                                    {(analysisResults.failure_probability * 100).toFixed(1)}%
                                </div>
                                <p className="text-sm text-[#848e9c]">Failure Probability Score</p>
                            </div>

                            <div className="space-y-4">
                                <div className="p-3 bg-black/20 rounded border border-white/5">
                                    <h4 className="text-sm font-bold mb-1 flex items-center space-x-2">
                                        {isHighRisk ? (
                                            <AlertCircle className="w-4 h-4 text-[#f6465d]" />
                                        ) : (
                                            <CheckCircle2 className="w-4 h-4 text-[#0ecb81]" />
                                        )}
                                        <span>Verdict</span>
                                    </h4>
                                    <p className="text-xs text-[#848e9c] leading-relaxed">
                                        {analysisResults.recommendation}
                                    </p>
                                </div>

                                <div className="text-[10px] text-[#474d57] flex items-start space-x-2">
                                    <Info className="w-3 h-3 mt-0.5" />
                                    <span>Analysis based on 10-step lookback LSTM inference.</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Trade Log Section */}
            <div className="binance-card p-6 overflow-hidden">
                <div className="flex items-center space-x-2 mb-6">
                    <History className="w-5 h-5 text-[#f0b90b]" />
                    <h3 className="font-bold text-lg">Execution Log</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="text-[#848e9c] border-b border-[#2b3139]">
                                <th className="pb-3 font-medium">Time / Index</th>
                                <th className="pb-3 font-medium">Type</th>
                                <th className="pb-3 font-medium">Price</th>
                                <th className="pb-3 font-medium text-right">Status</th>
                            </tr>
                        </thead>
                        <tbody className="text-[#eaecef]">
                            {backtestResults.trades.slice(-10).map((trade, idx) => (
                                <tr key={idx} className="border-b border-[#2b3139]/50 hover:bg-[#2b3139]/30 transition-colors">
                                    <td className="py-3 font-mono text-[12px]">{trade.date}</td>
                                    <td className="py-3 capitalize">
                                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${trade.type === 'buy' ? 'bg-[#0ecb81]/10 text-[#0ecb81]' : 'bg-[#f6465d]/10 text-[#f6465d]'}`}>
                                            {trade.type}
                                        </span>
                                    </td>
                                    <td className="py-3 font-mono">${trade.price.toFixed(2)}</td>
                                    <td className="py-3 text-right">
                                        <span className="text-[#0ecb81] text-[10px]">Filled</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {backtestResults.trades.length > 10 && (
                        <p className="mt-4 text-center text-xs text-[#474d57]">Showing last 10 of {backtestResults.trades.length} iterations</p>
                    )}
                </div>
            </div>
        </div>
    );
}

// Internal icons helper (if needed, but using lucide-react)
const AlertCircle = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
);
