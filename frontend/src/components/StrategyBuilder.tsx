"use client";
import React, { useState } from 'react';
import { IndicatorConfig, StrategyRequest } from '../lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Settings2, Play, Search } from 'lucide-react';

interface StrategyBuilderProps {
    onRunBacktest: (strategy: StrategyRequest) => void;
}

export default function StrategyBuilder({ onRunBacktest }: StrategyBuilderProps) {
    const [ticker, setTicker] = useState('BTC-USD');
    const [indicators, setIndicators] = useState<IndicatorConfig[]>([]);

    const addIndicator = (name: string) => {
        setIndicators([...indicators, { name, params: { window: 14 } }]);
    };

    const updateIndicatorParam = (idx: number, key: string, value: number) => {
        const newIndicators = [...indicators];
        newIndicators[idx].params[key] = value;
        setIndicators(newIndicators);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onRunBacktest({
            ticker,
            indicators,
            rules: [],
            initial_capital: 10000
        });
    };

    return (
        <div className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Ticker Input */}
                <div className="space-y-2">
                    <label className="text-xs font-bold text-[#848e9c] uppercase tracking-wider">Market Ticker</label>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#474d57]" />
                        <input
                            type="text"
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            placeholder="e.g. BTC-USD, AAPL"
                            className="w-full pl-10 pr-4 py-2 bg-[#2b3139] border border-transparent focus:border-[#f0b90b] rounded text-sm text-[#eaecef] transition-all outline-none"
                        />
                    </div>
                </div>

                {/* Indicator Selection */}
                <div className="space-y-3">
                    <label className="text-xs font-bold text-[#848e9c] uppercase tracking-wider flex items-center justify-between">
                        <span>Indicators</span>
                        <Settings2 className="w-3 h-3" />
                    </label>

                    <div className="grid grid-cols-2 gap-2">
                        <button
                            type="button"
                            onClick={() => addIndicator('SMA')}
                            className="flex items-center justify-center space-x-1 py-1.5 bg-[#2b3139] hover:bg-[#474d57] rounded text-xs transition-colors"
                        >
                            <Plus className="w-3 h-3" />
                            <span>SMA</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => addIndicator('RSI')}
                            className="flex items-center justify-center space-x-1 py-1.5 bg-[#2b3139] hover:bg-[#474d57] rounded text-xs transition-colors"
                        >
                            <Plus className="w-3 h-3" />
                            <span>RSI</span>
                        </button>
                    </div>

                    <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                        <AnimatePresence>
                            {indicators.map((ind, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    className="p-3 bg-[#2b3139]/40 border border-[#2b3139] rounded group hover:border-[#474d57] transition-all"
                                >
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-xs font-bold text-[#f0b90b]">{ind.name}</span>
                                        <button
                                            type="button"
                                            onClick={() => setIndicators(indicators.filter((_, i) => i !== idx))}
                                            className="text-[#474d57] hover:text-[#f6465d] transition-colors"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                    <div className="flex items-center space-x-3">
                                        <span className="text-[10px] text-[#848e9c] whitespace-nowrap">Window:</span>
                                        <input
                                            type="range"
                                            min="2"
                                            max="200"
                                            value={ind.params.window}
                                            onChange={(e) => updateIndicatorParam(idx, 'window', parseInt(e.target.value))}
                                            className="flex-1 accent-[#f0b90b] h-1"
                                        />
                                        <span className="text-[10px] font-mono text-[#eaecef] w-6">{ind.params.window}</span>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        {indicators.length === 0 && (
                            <div className="text-center py-6 text-[#474d57] text-[10px] italic">
                                No indicators added.
                            </div>
                        )}
                    </div>
                </div>

                {/* Submit Action */}
                <div className="pt-4 border-t border-[#2b3139]">
                    <button
                        type="submit"
                        className="w-full py-3 bg-[#f0b90b] hover:bg-[#fcd535] text-black font-bold rounded flex items-center justify-center space-x-2 transition-all active:scale-[0.98]"
                    >
                        <Play className="w-4 h-4 fill-current" />
                        <span>Execute Strategy</span>
                    </button>
                    <p className="mt-2 text-[10px] text-[#474d57] text-center">
                        Initial Capital: $10,000.00
                    </p>
                </div>
            </form>
        </div>
    );
}
