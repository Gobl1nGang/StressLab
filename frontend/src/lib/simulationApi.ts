// Frontend API client for real-time simulation

const SIMULATION_API_BASE = 'http://localhost:8000/simulation';

export interface SimulationRequest {
    ticker: string;
    indicators: Array<{
        name: string;
        params: Record<string, number>;
    }>;
    rules: any[];
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
    trades: any[];
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
    onError: (error: string) => void
): Promise<void> {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${SIMULATION_API_BASE}/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
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
    } catch (error: any) {
        onError(error.message || 'Connection error');
    }
}

/**
 * Run full simulation and get all results at once (non-streaming)
 */
export async function runSimulation(
    request: SimulationRequest
): Promise<{
    info: any;
    states: SimulationState[];
    results: SimulationResults;
}> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${SIMULATION_API_BASE}/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
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
): Promise<any> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${SIMULATION_API_BASE}/info`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        throw new Error('Failed to get simulation info');
    }

    return response.json();
}
