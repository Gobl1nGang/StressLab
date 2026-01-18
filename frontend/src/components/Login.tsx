"use client";
import React, { useState } from 'react';
import { login, register, setAccessToken } from '../lib/api';
import { motion } from 'framer-motion';
import { LogIn, ShieldCheck, Info } from 'lucide-react';

interface LoginProps {
    onLoginSuccess: () => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
    const [isLoginMode, setIsLoginMode] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            if (isLoginMode) {
                const token = await login(username, password);
                setAccessToken(token);
                onLoginSuccess();
            } else {
                await register(username, password);
                // Auto-login after register or switch to login mode
                setIsLoginMode(true);
                setError('Registration successful! Please login.');
                // Optional: Auto login
                // const token = await login(username, password);
                // setAccessToken(token);
                // onLoginSuccess();
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'System Access Denied';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-full max-w-md p-8 bg-[#1e2329] border border-[#2b3139] rounded-xl shadow-2xl shadow-black/50"
        >
            <div className="flex flex-col items-center mb-8">
                <div className="w-12 h-12 bg-[#f0b90b]/10 rounded-full flex items-center justify-center mb-4">
                    <ShieldCheck className="w-6 h-6 text-[#f0b90b]" />
                </div>
                <h2 className="text-2xl font-bold text-[#eaecef]">
                    {isLoginMode ? 'Authorize Access' : 'Create Account'}
                </h2>
                <p className="text-sm text-[#848e9c] mt-1 text-center">
                    Enter your StressLab credentials to access the Falsification Engine.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                    <label className="text-xs font-bold text-[#848e9c] uppercase tracking-wider">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-2.5 bg-[#2b3139] border border-transparent focus:border-[#f0b90b] outline-none rounded text-[#eaecef] transition-all"
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-xs font-bold text-[#848e9c] uppercase tracking-wider">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-2.5 bg-[#2b3139] border border-transparent focus:border-[#f0b90b] outline-none rounded text-[#eaecef] transition-all"
                    />
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-[#f6465d] text-xs py-2 px-3 bg-[#f6465d]/10 border border-[#f6465d]/20 rounded"
                    >
                        {error}
                    </motion.div>
                )}

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 bg-[#f0b90b] hover:bg-[#fcd535] disabled:opacity-50 text-black font-bold rounded flex items-center justify-center space-x-2 transition-all active:scale-[0.98]"
                >
                    {isLoading ? (
                        <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                    ) : (
                        <>
                            <LogIn className="w-4 h-4" />
                            <span>{isLoginMode ? 'Login to Dashboard' : 'Register Account'}</span>
                        </>
                    )}
                </button>
            </form>

            <div className="mt-6 text-center">
                <button
                    onClick={() => {
                        setIsLoginMode(!isLoginMode);
                        setError('');
                    }}
                    className="text-sm text-[#f0b90b] hover:text-[#fcd535] underline underline-offset-4"
                >
                    {isLoginMode ? "Don't have an account? Register" : "Already have an account? Login"}
                </button>
            </div>

            <div className="mt-8 pt-6 border-t border-[#2b3139] flex items-start space-x-3 text-[#474d57]">
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <p className="text-[10px] leading-relaxed">
                    Default hackathon build: Use <span className="text-[#848e9c]">johndoe</span> / <span className="text-[#848e9c]">secret</span> for administrative access.
                </p>
            </div>
        </motion.div>
    );
}
