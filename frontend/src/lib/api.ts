const API_URL = 'http://localhost:8000';

export interface IndicatorConfig {
    name: string;
    params: Record<string, any>;
}

export interface StrategyRequest {
    ticker: string;
    indicators: IndicatorConfig[];
    rules: any[];
    initial_capital: number;
}

export interface Trade {
    date: string;
    type: 'buy' | 'sell';
    price: number;
}

export interface BacktestResponse {
    final_capital: number;
    trades: Trade[];
    equity_curve: number[];
}

export interface AnalysisResponse {
    failure_probability: number;
    recommendation: string;
}

export let ACCESS_TOKEN = '';

export function setAccessToken(token: string) {
    ACCESS_TOKEN = token;
}

export async function login(username: string, password: string): Promise<string> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
    });

    if (!response.ok) throw new Error('Login failed');
    const data = await response.json();
    return data.access_token;
}

export async function runBacktest(request: StrategyRequest): Promise<BacktestResponse> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (ACCESS_TOKEN) {
        headers['Authorization'] = `Bearer ${ACCESS_TOKEN}`;
    }

    const response = await fetch(`${API_URL}/backtest`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(request),
    });
    if (response.status === 401) throw new Error('Unauthorized. Please login.');
    if (!response.ok) throw new Error('Backtest failed');
    return response.json();
}

export async function analyzeStrategy(request: StrategyRequest): Promise<AnalysisResponse> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (ACCESS_TOKEN) {
        headers['Authorization'] = `Bearer ${ACCESS_TOKEN}`;
    }

    const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
}
