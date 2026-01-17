"use client";
import React, { useState } from 'react';
import StrategyBuilder from '@/components/StrategyBuilder';
import Dashboard from '@/components/Dashboard';
import Login from '@/components/Login';
import { runBacktest, analyzeStrategy, StrategyRequest, BacktestResponse, AnalysisResponse } from '@/lib/api';

export default function Home() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [backtestResults, setBacktestResults] = useState<BacktestResponse | null>(null);
    const [analysisResults, setAnalysisResults] = useState<AnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRunBacktest = async (strategy: StrategyRequest) => {
        setLoading(true);
        setError(null);
        try {
            // 1. Run Backtest
            const results = await runBacktest(strategy);
            setBacktestResults(results);

            // 2. Analyze Strategy
            const analysis = await analyzeStrategy(strategy);
            setAnalysisResults(analysis);
        } catch (err: any) {
            setError(err.message || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    if (!isLoggedIn) {
        return (
            <main className="min-h-screen bg-gray-900 text-white p-8">
                <header className="mb-8 text-center">
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                        Trading Strategy Falsifier
                    </h1>
                </header>
                <Login onLoginSuccess={() => setIsLoggedIn(true)} />
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-gray-900 text-white p-8">
            <header className="mb-8 text-center">
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                    Trading Strategy Falsifier
                </h1>
                <p className="text-gray-400 mt-2">Build, Backtest, and Falsify your strategies.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1">
                    <StrategyBuilder onRunBacktest={handleRunBacktest} />
                </div>

                <div className="lg:col-span-2">
                    {loading && <div className="text-center py-10 text-xl animate-pulse">Running Simulation & Falsification Engine...</div>}
                    {error && <div className="text-center py-10 text-red-500 bg-red-900/20 rounded-lg border border-red-500">{error}</div>}
                    {!loading && !error && (
                        <Dashboard backtestResults={backtestResults} analysisResults={analysisResults} />
                    )}
                </div>
            </div>
        </main>
    );
}
