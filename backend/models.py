from pydantic import BaseModel
from typing import List, Dict, Any, Optional

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
    indicators: List[IndicatorConfig]
    rules: List[Rule]
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
