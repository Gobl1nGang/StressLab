from typing import List, Dict, Any
import pandas as pd

class Indicator:
    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name
        self.params = params

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

class SMA(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        window = self.params.get('window', 14)
        return df['Close'].rolling(window=window).mean()

class RSI(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        window = self.params.get('window', 14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class Strategy:
    def __init__(self, indicators: List[Indicator], rules: List[Dict]):
        self.indicators = indicators
        self.rules = rules

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for ind in self.indicators:
            df[f"{ind.name}_{ind.params.get('window')}"] = ind.calculate(df)
        
        df['Signal'] = 0
        # Simple rule engine: if all conditions met, Buy (1), else Sell (-1) or Hold (0)
        # For hackathon, let's assume simple "Buy when Condition A, Sell when Condition B"
        # This is a placeholder for the complex rule logic
        return df
