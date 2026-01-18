from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IndicatorConfig(BaseModel):
    name: str
    params: Dict[str, Any]

class Rule(BaseModel):
    type: str  # 'buy' or 'sell'
    condition: str  # 'threshold', 'crossover', 'crossunder'
    indicator: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[float] = None
    ind1: Optional[str] = None
    ind2: Optional[str] = None

class StrategyRequest(BaseModel):
    ticker: str
    start_date: Optional[str] = "2023-01-01"
    end_date: Optional[str] = "2023-04-01"
    initial_capital: float = 10000.0
    indicators: List[IndicatorConfig]
    rules: List[Rule]

class Trade(BaseModel):
    date: str
    type: str
    price: float

class BacktestResponse(BaseModel):
    final_capital: float
    trades: List[Dict[str, Any]]
    equity_curve: List[float]

class AnalysisResponse(BaseModel):
    failure_probability: float
    recommendation: str
