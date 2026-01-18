"use client";
import React, { useState, useEffect, useRef } from 'react';
import { SimulationState, SimulationResults } from '../lib/simulationApi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

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
        return <div className="text-gray-400">Run a simulation to see real-time playback.</div>;
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
                <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-gray-400 text-sm">Current Price</p>
                    <p className="text-2xl font-bold">${latestState?.price.toFixed(2) || '0.00'}</p>
                </div>
                <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-gray-400 text-sm">Current Equity</p>
                    <p className={`text-2xl font-bold ${latestState?.equity >= 10000 ? 'text-green-400' : 'text-red-400'}`}>
                        ${latestState?.equity.toFixed(2) || '0.00'}
                    </p>
                </div>
                <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-gray-400 text-sm">Return</p>
                    <p className={`text-2xl font-bold ${latestState?.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {latestState?.return_pct.toFixed(2) || '0.00'}%
                    </p>
                </div>
                <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-gray-400 text-sm">Trades</p>
                    <p className="text-2xl font-bold">{latestState?.total_trades || 0}</p>
                </div>
            </div>

            {/* Live Chart */}
            <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white border border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Live Performance</h2>
                    {isSimulating && (
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-400">LIVE SIMULATION</span>
                        </div>
                    )}
                </div>
                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="date" stroke="#666" fontSize={12} tickCount={5} />
                            <YAxis yAxisId="left" stroke="#8884d8" fontSize={12} domain={['auto', 'auto']} />
                            <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" fontSize={12} domain={['auto', 'auto']} />
                            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                            <Line yAxisId="left" type="monotone" dataKey="equity" stroke="#8884d8" dot={false} strokeWidth={2} name="Equity" isAnimationActive={false} />
                            <Line yAxisId="right" type="monotone" dataKey="price" stroke="#82ca9d" dot={false} strokeWidth={1} name="Price" isAnimationActive={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Trade Log */}
            <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white border border-gray-700">
                <h2 className="text-xl font-bold mb-4">Trade Log</h2>
                <div ref={scrollRef} className="max-h-60 overflow-y-auto space-y-2 pr-2">
                    {trades.length === 0 ? (
                        <p className="text-gray-500 italic">No trades executed yet...</p>
                    ) : (
                        trades.map((trade, idx) => (
                            <div key={idx} className="flex justify-between items-center p-3 bg-gray-900 rounded border border-gray-700">
                                <div className="flex items-center space-x-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${trade.type === 'BUY' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
                                        {trade.type}
                                    </span>
                                    <span className="text-sm font-mono">{trade.date.split(' ')[0]}</span>
                                </div>
                                <div className="text-sm">
                                    <span className="text-gray-400">Price:</span> ${trade.price.toFixed(2)}
                                    <span className="mx-2 text-gray-600">|</span>
                                    <span className="text-gray-400">Shares:</span> {trade.shares.toFixed(4)}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Final Results Summary */}
            {results && (
                <div className="p-6 bg-gradient-to-br from-indigo-900/40 to-purple-900/40 rounded-lg border border-indigo-500/30">
                    <h2 className="text-2xl font-bold mb-4 text-indigo-300">Simulation Complete</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div>
                            <p className="text-gray-400 text-sm">Total Return</p>
                            <p className={`text-xl font-bold ${results.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                ${results.total_return.toFixed(2)} ({results.return_percentage.toFixed(2)}%)
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-400 text-sm">Max Equity</p>
                            <p className="text-xl font-bold text-blue-400">${results.max_equity.toFixed(2)}</p>
                        </div>
                        <div>
                            <p className="text-gray-400 text-sm">Min Equity</p>
                            <p className="text-xl font-bold text-orange-400">${results.min_equity.toFixed(2)}</p>
                        </div>
                        <div>
                            <p className="text-gray-400 text-sm">Days Simulated</p>
                            <p className="text-xl font-bold">{results.days_simulated}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
