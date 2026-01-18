"use client";
import React, { useState } from 'react';
import StrategyBuilder from '@/components/StrategyBuilder';
import Dashboard from '@/components/Dashboard';
import SimulationDashboard from '@/components/SimulationDashboard';
import Login from '@/components/Login';
import { runBacktest, analyzeStrategy, StrategyRequest, BacktestResponse, AnalysisResponse } from '@/lib/api';
import { streamSimulation, SimulationState, SimulationResults } from '@/lib/simulationApi';

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

    const handleRunBacktest = async (strategy: StrategyRequest) => {
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

            // 2. Analyze Strategy
            const analysis = await analyzeStrategy(strategy);
            setAnalysisResults(analysis);

            // 3. Start Real-Time Simulation Playback
            setIsSimulating(true);
            await streamSimulation(
                {
                    ticker: strategy.ticker,
                    indicators: strategy.indicators,
                    rules: strategy.rules,
                    initial_capital: strategy.initial_capital,
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
                    setError(`Simulation error: ${err}`);
                    setIsSimulating(false);
                }
            );

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

                <div className="lg:col-span-2 space-y-8">
                    {loading && !isSimulating && (
                        <div className="text-center py-10 text-xl animate-pulse">
                            Initializing Simulation & Falsification Engine...
                        </div>
                    )}

                    {error && (
                        <div className="text-center py-10 text-red-500 bg-red-900/20 rounded-lg border border-red-500">
                            {error}
                        </div>
                    )}

                    {/* Real-Time Simulation Dashboard */}
                    {(isSimulating || simulationStates.length > 0) && (
                        <SimulationDashboard
                            states={simulationStates}
                            results={simulationResults}
                            isSimulating={isSimulating}
                        />
                    )}

                    {/* Static Analysis Results (shown after simulation starts/completes) */}
                    {!loading && !error && backtestResults && (
                        <Dashboard backtestResults={backtestResults} analysisResults={analysisResults} />
                    )}
                </div>
            </div>
        </main>
    );
}
