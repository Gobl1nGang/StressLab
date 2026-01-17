"use client";
import React, { useState } from 'react';
import { login, setAccessToken } from '../lib/api';

interface LoginProps {
    onLoginSuccess: () => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
    const [username, setUsername] = useState('johndoe');
    const [password, setPassword] = useState('secret');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const token = await login(username, password);
            setAccessToken(token);
            onLoginSuccess();
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-10 p-6 bg-gray-800 rounded-lg shadow-lg text-white">
            <h2 className="text-2xl font-bold mb-4 text-center">Login</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-1">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full p-2 bg-gray-700 rounded border border-gray-600"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 bg-gray-700 rounded border border-gray-600"
                    />
                </div>
                {error && <p className="text-red-400 text-sm">{error}</p>}
                <button type="submit" className="w-full py-2 bg-blue-600 rounded font-bold hover:bg-blue-500 transition">
                    Login
                </button>
            </form>
            <p className="mt-4 text-xs text-gray-400 text-center">Default: johndoe / secret</p>
        </div>
    );
}
