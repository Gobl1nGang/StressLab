"use client";
import React, { useState } from 'react';
import { IndicatorConfig, StrategyRequest } from '../lib/api';

interface StrategyBuilderProps {
    onRunBacktest: (strategy: StrategyRequest) => void;
}

export default function StrategyBuilder({ onRunBacktest }: StrategyBuilderProps) {
    const [ticker, setTicker] = useState('AAPL');
    const [indicators, setIndicators] = useState<IndicatorConfig[]>([]);

    const addIndicator = (name: string) => {
        setIndicators([...indicators, { name, params: { window: 14 } }]);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onRunBacktest({
            ticker,
            indicators,
            rules: [], // Placeholder
            initial_capital: 10000
        });
    };

    return (
        <div className="p-6 bg-gray-800 rounded-lg shadow-lg text-white">
            <h2 className="text-2xl font-bold mb-4">Strategy Builder</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-1">Ticker</label>
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        className="w-full p-2 bg-gray-700 rounded border border-gray-600"
                    />
                </div>

                <div>
                    <h3 className="text-lg font-semibold mb-2">Indicators</h3>
                    <div className="flex space-x-2 mb-2">
                        <button type="button" onClick={() => addIndicator('SMA')} className="px-3 py-1 bg-blue-600 rounded hover:bg-blue-500">Add SMA</button>
                        <button type="button" onClick={() => addIndicator('RSI')} className="px-3 py-1 bg-green-600 rounded hover:bg-green-500">Add RSI</button>
                    </div>
                    <ul className="space-y-2">
                        {indicators.map((ind, idx) => (
                            <li key={idx} className="flex justify-between items-center bg-gray-700 p-2 rounded">
                                <span>{ind.name} (Window: {ind.params.window})</span>
                                <button type="button" onClick={() => setIndicators(indicators.filter((_, i) => i !== idx))} className="text-red-400 hover:text-red-300">Remove</button>
                            </li>
                        ))}
                    </ul>
                </div>

                <button type="submit" className="w-full py-2 bg-purple-600 rounded font-bold hover:bg-purple-500 transition">
                    Run Backtest
                </button>
            </form>
        </div>
    );
}
