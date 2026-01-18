"use client";
import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import StrategyBuilder from '@/components/StrategyBuilder';
import Dashboard from '@/components/Dashboard';
import SimulationDashboard from '@/components/SimulationDashboard';
import Login from '@/components/Login';
import { runBacktest, analyzeStrategy, StrategyRequest, BacktestResponse, AnalysisResponse } from '@/lib/api';
import { streamSimulation, SimulationState, SimulationResults } from '@/lib/simulationApi';
import { LayoutGrid, Loader2, AlertCircle, Activity } from 'lucide-react';

export default function Home() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [backtestResults, setBacktestResults] = useState<BacktestResponse | null>(null);
    const [analysisResults, setAnalysisResults] = useState<AnalysisResponse | null>(null);

    // Simulation state
    const [simulationStates, setSimulationStates] = useState<SimulationState[]>([]);
    const [simulationResults, setSimulationResults] = useState<SimulationResults | null>(null);
    const [isSimulating, setIsSimulating] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    const handleRunBacktest = async (strategy: StrategyRequest) => {
        if (loading || isSimulating) return;

        // Cancel any existing simulation
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();

        setLoading(true);
        setError(null);
        setBacktestResults(null);
        setAnalysisResults(null);
        setSimulationStates([]);
        setSimulationResults(null);

        try {
            // 1. Run Backtest (Static)
            const results = await runBacktest(strategy);
            setBacktestResults(results);
            const analysis = await analyzeStrategy(strategy);
            setAnalysisResults(analysis);

            // 3. Start Real-Time Simulation Playback
            setIsSimulating(true);
            await streamSimulation(
                {
                    ticker: strategy.ticker,
                    indicators: strategy.indicators,
                    rules: strategy.rules,
                    initial_capital: 10000,
                    speed: 2.0 // 2 days per second for demo
                },
                (state) => {
                    setSimulationStates(prev => [...prev, state]);
                },
                (results) => {
                    setSimulationResults(results);
                    setIsSimulating(false);
                },
                (err) => {
                    if (err !== 'The user aborted a request.' && err !== 'signal is aborted without reason') {
                        setError(`Simulation error: ${err}`);
                    }
                    setIsSimulating(false);
                },
                abortControllerRef.current.signal
            );

        } catch (err: any) {
            if (err.name !== 'AbortError') {
                setError(err.message || 'An error occurred during simulation');
            }
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
                    <StrategyBuilder onRunBacktest={handleRunBacktest} isLoading={loading || isSimulating} />
                </div>
            </aside>

            {/* Main Content / Dashboard */}
            <main className="flex-1 overflow-y-auto bg-[#0b0e11] relative">
                <AnimatePresence mode="wait">
                    {loading && !isSimulating ? (
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
                    ) : (
                        <motion.div
                            key="content"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-4 h-full space-y-6"
                        >
                            {/* Error Display */}
                            {error && (
                                <motion.div
                                    initial={{ scale: 0.95, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    className="p-4 bg-[#f6465d]/10 border border-[#f6465d]/30 rounded flex items-start space-x-3"
                                >
                                    <AlertCircle className="w-5 h-5 text-[#f6465d] mt-1 shrink-0" />
                                    <div>
                                        <h4 className="font-bold text-[#f6465d] text-sm">Simulation Error</h4>
                                        <p className="text-xs text-[#848e9c]">{error}</p>
                                        <button
                                            onClick={() => setError(null)}
                                            className="mt-2 text-[10px] text-[#848e9c] hover:text-[#eaecef] underline"
                                        >
                                            Dismiss
                                        </button>
                                    </div>
                                </motion.div>
                            )}

                            {/* Real-Time Simulation Dashboard */}
                            {(isSimulating || simulationStates.length > 0) && (
                                <SimulationDashboard
                                    states={simulationStates}
                                    results={simulationResults}
                                    isSimulating={isSimulating}
                                />
                            )}

                            {/* Static Analysis Results */}
                            {!loading && backtestResults && (
                                <Dashboard backtestResults={backtestResults} analysisResults={analysisResults} />
                            )}

                            {/* Welcome State */}
                            {!loading && !backtestResults && !isSimulating && !error && (
                                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
                                    <div className="w-20 h-20 rounded-full bg-[#1e2329] flex items-center justify-center border border-[#2b3139]">
                                        <Activity className="w-10 h-10 text-[#2b3139]" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-[#eaecef]">Ready for Simulation</h3>
                                        <p className="text-sm text-[#848e9c]">Select a market and build your strategy to begin.</p>
                                    </div>
                                </div>
                            )}
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
