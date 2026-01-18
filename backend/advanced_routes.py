"""
Backend integration for Advanced ML Falsifier.

Provides endpoints for:
- Comprehensive analysis (all ML models)
- Future failure prediction
- Anomaly detection
- News sentiment analysis
- Adaptive learning updates
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.advanced_falsifier import AdvancedFalsifier

# Initialize router
router = APIRouter(prefix="/advanced", tags=["Advanced ML"])

# Initialize advanced falsifier
advanced_falsifier = AdvancedFalsifier()

# ============================================================================
# Request/Response Models
# ============================================================================

class ComprehensiveAnalysisRequest(BaseModel):
    returns: List[float]
    macro_indicators: Optional[Dict[str, float]] = None
    news_texts: Optional[List[str]] = None

class ComprehensiveAnalysisResponse(BaseModel):
    future_failure_prob: float
    complex_pattern_prob: float
    anomaly: Dict[str, Any]
    news_sentiment: Optional[Dict[str, Any]] = None
    combined_risk_score: float
    recommendation: str

class AdaptiveUpdateRequest(BaseModel):
    returns: List[float]
    actual_failure: bool

# ============================================================================
# Endpoints
# ============================================================================

@router.post("/comprehensive", response_model=ComprehensiveAnalysisResponse)
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    """
    Perform comprehensive analysis using all ML models.
    
    Returns:
    - Future failure probability (LSTM)
    - Complex pattern detection (Deep NN)
    - Anomaly detection
    - News sentiment (if provided)
    - Combined risk score
    - Actionable recommendation
    """
    try:
        results = advanced_falsifier.comprehensive_analysis(
            returns=request.returns,
            macro_indicators=request.macro_indicators,
            news_texts=request.news_texts
        )
        
        return ComprehensiveAnalysisResponse(
            future_failure_prob=results['future_failure_prob'],
            complex_pattern_prob=results['complex_pattern_prob'],
            anomaly=results['anomaly'],
            news_sentiment=results.get('news_sentiment'),
            combined_risk_score=results['combined_risk_score'],
            recommendation=results['recommendation']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-future")
async def predict_future_failure(request: ComprehensiveAnalysisRequest):
    """Predict future failure probability using LSTM."""
    try:
        prob = advanced_falsifier.predict_future_failure(
            returns=request.returns,
            macro_indicators=request.macro_indicators
        )
        return {"future_failure_probability": prob}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-anomaly")
async def detect_anomaly(returns: List[float]):
    """Detect if current pattern is anomalous."""
    try:
        is_anomaly, score, description = advanced_falsifier.check_anomaly(returns)
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": score,
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-news")
async def analyze_news(news_texts: List[str]):
    """Analyze news sentiment and market impact."""
    try:
        results = advanced_falsifier.analyze_news_impact(news_texts)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adaptive-update")
async def adaptive_update(request: AdaptiveUpdateRequest):
    """Update models with new data (online learning)."""
    try:
        advanced_falsifier.adaptive_update(
            returns=request.returns,
            actual_failure=request.actual_failure
        )
        return {"status": "updated", "message": "Models updated with new data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get status of all ML models."""
    return {
        "lstm_loaded": hasattr(advanced_falsifier.lstm_predictor, 'lstm'),
        "pattern_detector_loaded": hasattr(advanced_falsifier.pattern_detector, 'network'),
        "anomaly_detector_fitted": advanced_falsifier.anomaly_detector.is_fitted,
        "model_dir": str(advanced_falsifier.model_dir),
        "status": "operational"
    }
