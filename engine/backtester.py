from typing import Dict, Any
import pandas as pd
import numpy as np
from .strategy import Strategy

class Backtester:
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000.0):
        self.data = data
        self.initial_capital = initial_capital
        self.results = {}

    def run(self, strategy: Strategy) -> Dict[str, Any]:
        """
        Run a strategy on the data.
        """
        df = strategy.generate_signals(self.data)
        
        # Simulation
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = []

        for i, row in df.iterrows():
            price = row['Close']
            signal = row.get('Signal', 0)

            if signal == 1 and position == 0: # Buy
                position = capital / price
                capital = 0
                trades.append({'date': i, 'type': 'buy', 'price': price})
            elif signal == -1 and position > 0: # Sell
                capital = position * price
                position = 0
                trades.append({'date': i, 'type': 'sell', 'price': price})
            
            current_value = capital + (position * price)
            equity_curve.append(current_value)

        self.results = {
            'final_capital': capital + (position * df.iloc[-1]['Close']),
            'trades': trades,
            'equity_curve': equity_curve
        }
        return self.results
