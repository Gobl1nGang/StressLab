from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IndicatorConfig(BaseModel):
    name: str
    params: Dict[str, Any]

class StrategyRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float
    indicators: List[IndicatorConfig]
    rules: Dict[str, Any]

class BacktestResponse(BaseModel):
    final_capital: float
    trades: List[Dict[str, Any]]
    equity_curve: List[float]

class AnalysisResponse(BaseModel):
    failure_probability: float
    recommendation: str
