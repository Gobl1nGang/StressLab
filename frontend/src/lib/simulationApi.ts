// Frontend API client for real-time simulation
import { ACCESS_TOKEN, Rule, IndicatorConfig } from './api';

const API_URL = 'http://localhost:8000';
const SIMULATION_API_BASE = `${API_URL}/simulation`;

export interface SimulationRequest {
    ticker: string;
    indicators: IndicatorConfig[];
    rules: Rule[];
    initial_capital?: number;
    speed?: number; // Days per second
}

export interface SimulationState {
    day: number;
    total_days: number;
    date: string;
    price: number;
    open: number;
    high: number;
    low: number;
    volume: number;
    indicators: Record<string, number>;
    signal: number;
    position: number;
    capital: number;
    equity: number;
    trade: {
        date: string;
        type: string;
        price: number;
        shares: number;
    } | null;
    total_trades: number;
    return_pct: number;
}

export interface SimulationResults {
    initial_capital: number;
    final_equity: number;
    total_return: number;
    return_percentage: number;
    total_trades: number;
    trades: Array<{ date: string; type: string; price: number; type_label: string }>;
    equity_curve: number[];
    max_equity: number;
    min_equity: number;
    days_simulated: number;
}

/**
 * Stream real-time simulation updates using fetch and readable stream
 */
export async function streamSimulation(
    request: SimulationRequest,
    onUpdate: (state: SimulationState) => void,
    onComplete: (results: SimulationResults) => void,
    onError: (error: string) => void,
    signal?: AbortSignal
): Promise<void> {
    try {
        const response = await fetch(`${SIMULATION_API_BASE}/stream`, {
            method: 'POST',
            signal,
            headers: {
                'Content-Type': 'application/json',
                ...(ACCESS_TOKEN && { 'Authorization': `Bearer ${ACCESS_TOKEN}` })
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(`Simulation stream failed: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('Response body is not readable');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const message = JSON.parse(line.slice(6));
                    switch (message.type) {
                        case 'info':
                            console.log('Simulation info:', message.data);
                            break;
                        case 'update':
                            onUpdate(message.data);
                            break;
                        case 'complete':
                            onComplete(message.data);
                            return;
                        case 'error':
                            onError(message.message);
                            return;
                    }
                }
            }
        }
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Connection error';
        onError(errorMessage);
    }
}

/**
 * Run full simulation and get all results at once (non-streaming)
 */
export async function runSimulation(
    request: SimulationRequest
): Promise<{
    info: { training_period: [string, string], simulation_period: [string, string] };
    states: SimulationState[];
    results: SimulationResults;
}> {
    const response = await fetch(`${SIMULATION_API_BASE}/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(ACCESS_TOKEN && { 'Authorization': `Bearer ${ACCESS_TOKEN}` })
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        throw new Error('Simulation failed');
    }

    return response.json();
}

/**
 * Get simulation info (training/simulation periods)
 */
export async function getSimulationInfo(
    request: SimulationRequest
): Promise<{ training_period: [string, string], simulation_period: [string, string] }> {
    const response = await fetch(`${SIMULATION_API_BASE}/info`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(ACCESS_TOKEN && { 'Authorization': `Bearer ${ACCESS_TOKEN}` })
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        throw new Error('Failed to get simulation info');
    }

    return response.json();
}
