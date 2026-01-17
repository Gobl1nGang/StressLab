"use client";
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import StrategyBuilder from '@/components/StrategyBuilder';
import Dashboard from '@/components/Dashboard';
import Login from '@/components/Login';
import { runBacktest, analyzeStrategy, StrategyRequest, BacktestResponse, AnalysisResponse } from '@/lib/api';
import { LayoutGrid, Loader2, AlertCircle } from 'lucide-react';

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
            const results = await runBacktest(strategy);
            setBacktestResults(results);
            const analysis = await analyzeStrategy(strategy);
            setAnalysisResults(analysis);
        } catch (err: any) {
            setError(err.message || 'An error occurred during simulation');
        } finally {
            setLoading(false);
        }
    };

    if (!isLoggedIn) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-center min-h-[calc(100vh-3.5rem)] bg-[#0b0e11]"
            >
                <Login onLoginSuccess={() => setIsLoggedIn(true)} />
            </motion.div>
        );
    }

    return (
        <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
            {/* Sidebar / Strategy Builder */}
            <aside className="w-80 border-r border-[#2b3139] bg-[#1e2329] overflow-y-auto hidden lg:block">
                <div className="p-4 border-b border-[#2b3139]">
                    <div className="flex items-center space-x-2 text-[#eaecef]">
                        <LayoutGrid className="w-4 h-4 text-[#f0b90b]" />
                        <span className="font-semibold">Strategy Entry</span>
                    </div>
                </div>
                <div className="p-4">
                    <StrategyBuilder onRunBacktest={handleRunBacktest} />
                </div>
            </aside>

            {/* Main Content / Dashboard */}
            <main className="flex-1 overflow-y-auto bg-[#0b0e11] relative">
                <AnimatePresence mode="wait">
                    {loading ? (
                        <motion.div
                            key="loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0b0e11]/80 backdrop-blur-sm"
                        >
                            <Loader2 className="w-12 h-12 text-[#f0b90b] animate-spin mb-4" />
                            <h3 className="text-xl font-bold">Simulating Market Edge</h3>
                            <p className="text-sm text-[#848e9c]">Falsification engine running neural analysis...</p>
                        </motion.div>
                    ) : error ? (
                        <motion.div
                            key="error"
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="p-8 m-4 bg-[#f6465d]/10 border border-[#f6465d]/30 rounded-lg flex items-start space-x-3"
                        >
                            <AlertCircle className="w-5 h-5 text-[#f6465d] mt-1" />
                            <div>
                                <h4 className="font-bold text-[#f6465d]">Simulation Error</h4>
                                <p className="text-sm text-[#848e9c]">{error}</p>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="dashboard"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-4 h-full"
                        >
                            <Dashboard backtestResults={backtestResults} analysisResults={analysisResults} />
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Mobile version toggle/notice if needed */}
                <div className="lg:hidden p-4 text-center text-[#848e9c] italic text-sm">
                    Strategy entry is available on desktop view.
                </div>
            </main>
        </div>
    );
}
