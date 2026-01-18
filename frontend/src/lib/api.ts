const API_URL = 'http://localhost:8000';
const USE_MOCK = true; // Set to false to connect to the real backend

export interface Rule {
    type: string;  // 'buy' or 'sell'
    condition: string;  // 'threshold', 'crossover', 'crossunder'
    indicator?: string;
    operator?: string;
    value?: number;
    ind1?: string;
    ind2?: string;
}

export interface IndicatorConfig {
    name: string;
    params: Record<string, number>;
}

export interface StrategyRequest {
    ticker: string;
    indicators: IndicatorConfig[];
    rules: Rule[];
    initial_capital: number;
    start_date?: string;
    end_date?: string;
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
    if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 800));
        if (username === 'johndoe' && password === 'secret') return 'mock-jwt-token';
        throw new Error('Invalid credentials');
    }

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

export async function register(username: string, password: string): Promise<void> {
    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Registration failed');
    }
}

export async function runBacktest(request: StrategyRequest): Promise<BacktestResponse> {
    if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        // Generate mock equity curve
        const curve = [10000];
        for (let i = 0; i < 50; i++) {
            curve.push(curve[i] * (1 + (Math.random() * 0.04 - 0.01)));
        }
        return {
            final_capital: curve[curve.length - 1],
            trades: [
                { date: '2023-01-01', type: 'buy', price: 16500 },
                { date: '2023-01-05', type: 'sell', price: 17200 },
                { date: '2023-01-10', type: 'buy', price: 16800 },
            ],
            equity_curve: curve
        };
    }

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
    if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
            failure_probability: Math.random() * 0.8,
            recommendation: "Mock Recommendation: Strategy shows high sensitivity to volatility. Consider dynamic hedging."
        };
    }

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
