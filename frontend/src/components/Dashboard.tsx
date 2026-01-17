"use client";
import React from 'react';
import { BacktestResponse, AnalysisResponse } from '../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardProps {
    backtestResults: BacktestResponse | null;
    analysisResults: AnalysisResponse | null;
}

export default function Dashboard({ backtestResults, analysisResults }: DashboardProps) {
    if (!backtestResults) return <div className="text-gray-400">Run a strategy to see results.</div>;

    const chartData = backtestResults.equity_curve.map((val, idx) => ({
        index: idx,
        equity: val
    }));

    return (
        <div className="space-y-6">
            <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white">
                <h2 className="text-2xl font-bold mb-4">Backtest Results</h2>
                <div className="mb-4">
                    <p className="text-lg">Final Capital: <span className="font-mono text-green-400">${backtestResults.final_capital.toFixed(2)}</span></p>
                    <p className="text-sm text-gray-400">Total Trades: {backtestResults.trades.length}</p>
                </div>

                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                            <XAxis dataKey="index" stroke="#888" />
                            <YAxis stroke="#888" />
                            <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
                            <Line type="monotone" dataKey="equity" stroke="#8884d8" dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {analysisResults && (
                <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white border-l-4 border-red-500">
                    <h2 className="text-2xl font-bold mb-2">Falsifier Analysis</h2>
                    <div className="flex items-center space-x-4">
                        <div className="text-4xl font-bold text-red-400">{(analysisResults.failure_probability * 100).toFixed(1)}%</div>
                        <div className="text-lg">Failure Probability</div>
                    </div>
                    <p className="mt-2 text-gray-300">{analysisResults.recommendation}</p>
                </div>
            )}
        </div>
    );
}
