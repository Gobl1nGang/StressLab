from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IndicatorConfig(BaseModel):
    name: str
    params: Dict[str, Any]

class StrategyRequest(BaseModel):
    ticker: str
    indicators: List[IndicatorConfig]
    rules: List[Dict[str, Any]] # Placeholder for rule definition
    initial_capital: float = 10000.0

class Trade(BaseModel):
    date: str
    type: str
    price: float

class BacktestResponse(BaseModel):
    final_capital: float
    trades: List[Trade]
    equity_curve: List[float]

class AnalysisResponse(BaseModel):
    failure_probability: float
    recommendation: str
