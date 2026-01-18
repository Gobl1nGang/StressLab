"use client";
import React, { useState } from 'react';
import { IndicatorConfig, StrategyRequest } from '../lib/api';

interface Rule {
    type: 'buy' | 'sell';
    condition: 'threshold' | 'crossover' | 'crossunder';
    indicator?: string;
    operator?: string;
    value?: number;
    ind1?: string;
    ind2?: string;
}

interface StrategyBuilderProps {
    onRunBacktest: (strategy: StrategyRequest) => void;
}

export default function StrategyBuilder({ onRunBacktest }: StrategyBuilderProps) {
    const [ticker, setTicker] = useState('AAPL');
    const [indicators, setIndicators] = useState<IndicatorConfig[]>([
        { name: 'SMA', params: { window: 20 } },
        { name: 'SMA', params: { window: 50 } },
        { name: 'RSI', params: { window: 14 } },
        { name: 'MACD', params: { fast: 12, slow: 26, signal: 9 } }
    ]);
    const [rules, setRules] = useState<Rule[]>([
        { type: 'buy', condition: 'crossover', ind1: 'MACD_12_26', ind2: 'MACD_Signal_9' },
        { type: 'sell', condition: 'crossunder', ind1: 'MACD_12_26', ind2: 'MACD_Signal_9' }
    ]);

    const addIndicator = (name: string) => {
        if (name === 'MACD') {
            setIndicators([...indicators, { name, params: { fast: 12, slow: 26, signal: 9 } }]);
        } else {
            setIndicators([...indicators, { name, params: { window: 14 } }]);
        }
    };

    const addRule = (type: 'buy' | 'sell') => {
        setRules([...rules, { type, condition: 'threshold', indicator: 'RSI', operator: '<', value: 30 }]);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onRunBacktest({
            ticker,
            indicators,
            rules,
            initial_capital: 10000
        });
    };

    return (
        <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white border border-gray-700">
            <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                Strategy Builder
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Ticker Input */}
                <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-400 uppercase tracking-wider">Asset Ticker</label>
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value.toUpperCase())}
                        className="w-full p-3 bg-gray-900 rounded-lg border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
                        placeholder="e.g. BTC-USD, AAPL"
                    />
                </div>

                {/* Indicators Section */}
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Indicators</h3>
                        <div className="flex gap-2">
                            <button type="button" onClick={() => addIndicator('SMA')} className="text-xs px-2 py-1 bg-blue-900/50 text-blue-400 border border-blue-500/30 rounded hover:bg-blue-900 transition">Add SMA</button>
                            <button type="button" onClick={() => addIndicator('RSI')} className="text-xs px-2 py-1 bg-green-900/50 text-green-400 border border-green-500/30 rounded hover:bg-green-900 transition">Add RSI</button>
                            <button type="button" onClick={() => addIndicator('MACD')} className="text-xs px-2 py-1 bg-purple-900/50 text-purple-400 border border-purple-500/30 rounded hover:bg-purple-900 transition">Add MACD</button>
                        </div>
                    </div>

                    <div className="space-y-2">
                        {indicators.map((ind, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                                <div className="flex items-center gap-3">
                                    <span className="font-bold text-blue-400">{ind.name}</span>
                                    <span className="text-xs text-gray-500">
                                        {Object.entries(ind.params).map(([k, v]) => `${k}:${v}`).join(', ')}
                                    </span>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setIndicators(indicators.filter((_, i) => i !== idx))}
                                    className="text-gray-500 hover:text-red-400 transition"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Rules Section */}
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Trading Rules</h3>
                        <div className="flex gap-2">
                            <button type="button" onClick={() => addRule('buy')} className="text-xs px-2 py-1 bg-green-900/50 text-green-400 border border-green-500/30 rounded hover:bg-green-900 transition">+ Buy Rule</button>
                            <button type="button" onClick={() => addRule('sell')} className="text-xs px-2 py-1 bg-red-900/50 text-red-400 border border-red-500/30 rounded hover:bg-red-900 transition">+ Sell Rule</button>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {rules.map((rule, idx) => (
                            <div key={idx} className={`p-3 rounded-lg border ${rule.type === 'buy' ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
                                <div className="flex items-center justify-between mb-2">
                                    <span className={`text-xs font-bold uppercase ${rule.type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                        {rule.type} Signal
                                    </span>
                                    <button
                                        type="button"
                                        onClick={() => setRules(rules.filter((_, i) => i !== idx))}
                                        className="text-gray-500 hover:text-red-400 transition"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                </div>

                                <div className="grid grid-cols-2 gap-2">
                                    <select
                                        value={rule.condition}
                                        onChange={(e) => {
                                            const newRules = [...rules];
                                            newRules[idx].condition = e.target.value as any;
                                            setRules(newRules);
                                        }}
                                        className="text-xs p-2 bg-gray-900 border border-gray-700 rounded outline-none"
                                    >
                                        <option value="threshold">Threshold</option>
                                        <option value="crossover">Crossover</option>
                                        <option value="crossunder">Crossunder</option>
                                    </select>

                                    {rule.condition === 'threshold' ? (
                                        <div className="flex gap-1">
                                            <select
                                                value={rule.indicator}
                                                onChange={(e) => {
                                                    const newRules = [...rules];
                                                    newRules[idx].indicator = e.target.value;
                                                    setRules(newRules);
                                                }}
                                                className="text-xs p-2 bg-gray-900 border border-gray-700 rounded outline-none flex-1"
                                            >
                                                <option value="RSI">RSI</option>
                                                <option value="SMA">SMA</option>
                                            </select>
                                            <input
                                                type="number"
                                                value={rule.value}
                                                onChange={(e) => {
                                                    const newRules = [...rules];
                                                    newRules[idx].value = parseFloat(e.target.value);
                                                    setRules(newRules);
                                                }}
                                                className="text-xs p-2 bg-gray-900 border border-gray-700 rounded outline-none w-16"
                                            />
                                        </div>
                                    ) : (
                                        <div className="flex gap-1">
                                            <input
                                                type="text"
                                                value={rule.ind1}
                                                onChange={(e) => {
                                                    const newRules = [...rules];
                                                    newRules[idx].ind1 = e.target.value;
                                                    setRules(newRules);
                                                }}
                                                className="text-xs p-2 bg-gray-900 border border-gray-700 rounded outline-none flex-1"
                                                placeholder="Ind 1"
                                            />
                                            <input
                                                type="text"
                                                value={rule.ind2}
                                                onChange={(e) => {
                                                    const newRules = [...rules];
                                                    newRules[idx].ind2 = e.target.value;
                                                    setRules(newRules);
                                                }}
                                                className="text-xs p-2 bg-gray-900 border border-gray-700 rounded outline-none flex-1"
                                                placeholder="Ind 2"
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <button
                    type="submit"
                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-bold text-lg shadow-lg shadow-purple-900/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
                >
                    Launch Simulation
                </button>
            </form>
        </div>
    );
}
