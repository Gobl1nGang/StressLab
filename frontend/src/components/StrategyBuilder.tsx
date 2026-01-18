"use client";
import React, { useState } from 'react';
import { IndicatorConfig, StrategyRequest, Rule } from '../lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Settings2, Play, Search, ShieldAlert, ArrowRightLeft } from 'lucide-react';

interface StrategyBuilderProps {
    onRunBacktest: (strategy: StrategyRequest) => void;
    isLoading?: boolean;
}

export default function StrategyBuilder({ onRunBacktest, isLoading }: StrategyBuilderProps) {
    const [ticker, setTicker] = useState('BTC-USD');
    const [indicators, setIndicators] = useState<IndicatorConfig[]>([
        { name: 'SMA', params: { window: 20 } },
        { name: 'SMA', params: { window: 50 } },
        { name: 'RSI', params: { window: 14 } }
    ]);
    const [rules, setRules] = useState<Rule[]>([
        { type: 'buy', condition: 'threshold', indicator: 'RSI', operator: '<', value: 30 },
        { type: 'sell', condition: 'threshold', indicator: 'RSI', operator: '>', value: 70 }
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
            rules,
            initial_capital: 10000,
            start_date: "2023-01-01",
            end_date: "2024-01-01"
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

                    <div className="grid grid-cols-3 gap-2">
                        <button type="button" onClick={() => addIndicator('SMA')} className="flex items-center justify-center space-x-1 py-1.5 bg-[#2b3139] hover:bg-[#474d57] rounded text-[10px] transition-colors">
                            <Plus className="w-3 h-3" /> <span>SMA</span>
                        </button>
                        <button type="button" onClick={() => addIndicator('RSI')} className="flex items-center justify-center space-x-1 py-1.5 bg-[#2b3139] hover:bg-[#474d57] rounded text-[10px] transition-colors">
                            <Plus className="w-3 h-3" /> <span>RSI</span>
                        </button>
                        <button type="button" onClick={() => addIndicator('MACD')} className="flex items-center justify-center space-x-1 py-1.5 bg-[#2b3139] hover:bg-[#474d57] rounded text-[10px] transition-colors">
                            <Plus className="w-3 h-3" /> <span>MACD</span>
                        </button>
                    </div>

                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
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
                                        <button type="button" onClick={() => setIndicators(indicators.filter((_, i) => i !== idx))} className="text-[#474d57] hover:text-[#f6465d] transition-colors">
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                    <div className="space-y-2">
                                        {Object.entries(ind.params).map(([key, val]) => (
                                            <div key={key} className="flex items-center space-x-3">
                                                <span className="text-[10px] text-[#848e9c] whitespace-nowrap w-12">{key}:</span>
                                                <input
                                                    type="range"
                                                    min={key === 'slow' ? "20" : "2"}
                                                    max={key === 'slow' ? "250" : "100"}
                                                    value={val as number}
                                                    onChange={(e) => updateIndicatorParam(idx, key, parseInt(e.target.value))}
                                                    className="flex-1 accent-[#f0b90b] h-1"
                                                />
                                                <span className="text-[10px] font-mono text-[#eaecef] w-6">{val as number}</span>
                                            </div>
                                        ))}
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Rules Section */}
                <div className="space-y-3 pt-4 border-t border-[#2b3139]">
                    <label className="text-xs font-bold text-[#848e9c] uppercase tracking-wider flex items-center justify-between">
                        <span>Trading Rules</span>
                        <ArrowRightLeft className="w-3 h-3" />
                    </label>

                    <div className="grid grid-cols-2 gap-2">
                        <button type="button" onClick={() => addRule('buy')} className="py-1.5 bg-[#2b3139] hover:bg-[#02c076]/20 text-[#02c076] hover:text-[#02c076] rounded text-[10px] font-bold border border-transparent hover:border-[#02c076]/30 transition-all">+ BUY RULE</button>
                        <button type="button" onClick={() => addRule('sell')} className="py-1.5 bg-[#2b3139] hover:bg-[#cf304a]/20 text-[#f6465d] rounded text-[10px] font-bold border border-transparent hover:border-[#f6465d]/30 transition-all">+ SELL RULE</button>
                    </div>

                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
                        {rules.map((rule, idx) => (
                            <div key={idx} className={`p-2 rounded border ${rule.type === 'buy' ? 'border-[#02c076]/20 bg-[#02c076]/5' : 'border-[#f6465d]/20 bg-[#f6465d]/5'}`}>
                                <div className="flex justify-between items-center mb-2">
                                    <span className={`text-[10px] font-bold ${rule.type === 'buy' ? 'text-[#02c076]' : 'text-[#f6465d]'}`}>{rule.type.toUpperCase()} SIGNAL</span>
                                    <button type="button" onClick={() => setRules(rules.filter((_, i) => i !== idx))} className="text-[#474d57] hover:text-[#f6465d] transition-colors">
                                        <X className="w-3 h-3" />
                                    </button>
                                </div>
                                <div className="grid grid-cols-1 gap-1.5">
                                    <select
                                        value={rule.condition}
                                        onChange={(e) => {
                                            const newRules = [...rules];
                                            newRules[idx].condition = e.target.value as 'threshold' | 'crossover' | 'crossunder';
                                            setRules(newRules);
                                        }}
                                        className="text-[10px] p-1.5 bg-[#1e2329] border border-[#2b3139] rounded text-[#eaecef] outline-none"
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
                                                className="text-[10px] p-1.5 bg-[#1e2329] border border-[#2b3139] rounded text-[#eaecef] outline-none flex-1"
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
                                                className="text-[10px] p-1.5 bg-[#1e2329] border border-[#2b3139] rounded text-[#eaecef] outline-none w-12"
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
                                                className="text-[10px] p-1.5 bg-[#1e2329] border border-[#2b3139] rounded text-[#eaecef] outline-none flex-1"
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
                                                className="text-[10px] p-1.5 bg-[#1e2329] border border-[#2b3139] rounded text-[#eaecef] outline-none flex-1"
                                                placeholder="Ind 2"
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Submit Action */}
                <div className="pt-4 border-t border-[#2b3139]">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className={`w-full py-3 ${isLoading ? 'bg-[#2b3139] text-[#474d57]' : 'bg-[#f0b90b] hover:bg-[#fcd535] text-black'} font-bold rounded flex items-center justify-center space-x-2 transition-all active:scale-[0.98] transition-colors`}
                    >
                        {isLoading ? (
                            <div className="w-4 h-4 border-2 border-[#474d57] border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <Play className="w-4 h-4 fill-current" />
                        )}
                        <span>{isLoading ? 'Simulation in Progress' : 'Launch Simulation'}</span>
                    </button>
                    <p className="mt-2 text-[10px] text-[#474d57] text-center">
                        Initial Capital: $10,000.00
                    </p>
                </div>
            </form>
        </div>
    );
}
