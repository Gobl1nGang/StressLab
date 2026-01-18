// Frontend API client for Advanced ML endpoints

const ADVANCED_API_BASE = 'http://localhost:8000/advanced';

export interface MacroIndicators {
    vix?: number;
    interest_rate?: number;
    unemployment?: number;
}

export interface ComprehensiveAnalysisRequest {
    returns: number[];
    macro_indicators?: MacroIndicators;
    news_texts?: string[];
}

export interface AnomalyResult {
    detected: boolean;
    score: number;
    description: string;
}

export interface NewsSentiment {
    avg_sentiment: number;
    confidence: number;
    impact: string;
    num_articles: number;
}

export interface ComprehensiveAnalysisResponse {
    future_failure_prob: number;
    complex_pattern_prob: number;
    anomaly: AnomalyResult;
    news_sentiment?: NewsSentiment;
    combined_risk_score: number;
    recommendation: string;
}

/**
 * Get comprehensive analysis using all ML models
 */
export async function getComprehensiveAnalysis(
    request: ComprehensiveAnalysisRequest
): Promise<ComprehensiveAnalysisResponse> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${ADVANCED_API_BASE}/comprehensive`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        throw new Error('Comprehensive analysis failed');
    }

    return response.json();
}

/**
 * Predict future failure probability (LSTM only)
 */
export async function predictFutureFailure(
    returns: number[],
    macroIndicators?: MacroIndicators
): Promise<number> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${ADVANCED_API_BASE}/predict-future`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ returns, macro_indicators: macroIndicators })
    });

    if (!response.ok) {
        throw new Error('Future prediction failed');
    }

    const data = await response.json();
    return data.future_failure_probability;
}

/**
 * Detect if pattern is anomalous
 */
export async function detectAnomaly(returns: number[]): Promise<AnomalyResult> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${ADVANCED_API_BASE}/detect-anomaly`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(returns)
    });

    if (!response.ok) {
        throw new Error('Anomaly detection failed');
    }

    return response.json();
}

/**
 * Analyze news sentiment
 */
export async function analyzeNews(newsTexts: string[]): Promise<NewsSentiment> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${ADVANCED_API_BASE}/analyze-news`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(newsTexts)
    });

    if (!response.ok) {
        throw new Error('News analysis failed');
    }

    return response.json();
}

/**
 * Update models with new data (adaptive learning)
 */
export async function adaptiveUpdate(
    returns: number[],
    actualFailure: boolean
): Promise<void> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${ADVANCED_API_BASE}/adaptive-update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ returns, actual_failure: actualFailure })
    });

    if (!response.ok) {
        throw new Error('Adaptive update failed');
    }
}

/**
 * Get ML system status
 */
export async function getMLStatus(): Promise<any> {
    const response = await fetch(`${ADVANCED_API_BASE}/status`);

    if (!response.ok) {
        throw new Error('Status check failed');
    }

    return response.json();
}
