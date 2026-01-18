"""
Real-time playback simulator for trading strategies.

Plays back historical data day-by-day (1 day per second) showing:
- Live indicator progression
- Trade execution in real-time
- Equity curve updates
- Strategy credibility under market conditions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Generator
from datetime import datetime
import time
from engine.strategy import Strategy
from engine.dataloader import fetch_market_data

class RealtimeSimulator:
    def __init__(self, ticker: str, strategy: Strategy, initial_capital: float = 10000.0):
        """
        Initialize real-time simulator.
        
        Args:
            ticker: Stock ticker symbol
            strategy: Trading strategy to simulate
            initial_capital: Starting capital
        """
        self.ticker = ticker
        self.strategy = strategy
        self.initial_capital = initial_capital
        
        # Load dataset (Mock or Real)
        if self.ticker.upper() == "MOCK":
            dates = pd.date_range(end=datetime.now(), periods=500, freq="D")
            prices = 100 + np.random.randn(500).cumsum()
            self.data = pd.DataFrame({
                "Open": prices,
                "High": prices + 1,
                "Low": prices - 1,
                "Close": prices,
                "Volume": 100000
            }, index=dates)
        else:
            self.data = fetch_market_data(ticker, period="2y")
        
        # Split into training and simulation periods
        split_point = int(len(self.data) * 0.7)  # 70% train, 30% simulate
        self.training_data = self.data.iloc[:split_point]
        self.simulation_data = self.data.iloc[split_point:]
        
        # State
        self.current_index = 0
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_history = []
        self.indicator_history = []
        
    def get_simulation_info(self) -> Dict[str, Any]:
        """Get information about the simulation period."""
        return {
            'ticker': self.ticker,
            'training_period': {
                'start': str(self.training_data.index[0]),
                'end': str(self.training_data.index[-1]),
                'days': len(self.training_data)
            },
            'simulation_period': {
                'start': str(self.simulation_data.index[0]),
                'end': str(self.simulation_data.index[-1]),
                'days': len(self.simulation_data)
            },
            'initial_capital': self.initial_capital
        }
    
    def step(self) -> Dict[str, Any]:
        """
        Execute one day of simulation.
        
        Returns:
            Current state including price, indicators, position, equity
        """
        if self.current_index >= len(self.simulation_data):
            return None  # Simulation complete
        
        # Get current data point
        current_date = self.simulation_data.index[self.current_index]
        current_row = self.simulation_data.iloc[self.current_index]
        
        # Calculate indicators using data up to current point
        historical_data = pd.concat([
            self.training_data,
            self.simulation_data.iloc[:self.current_index + 1]
        ])
        
        # Generate signals
        df_with_signals = self.strategy.generate_signals(historical_data)
        current_signal = df_with_signals.iloc[-1]['Signal']
        
        # Get indicator values
        indicator_values = {}
        for col in df_with_signals.columns:
            if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Signal']:
                indicator_values[col] = float(df_with_signals.iloc[-1][col])
        
        # Execute trade based on signal
        price = float(current_row['Close'])
        trade_executed = None
        
        if current_signal == 1 and self.position == 0:  # Buy signal
            self.position = self.capital / price
            self.capital = 0
            trade_executed = {
                'date': str(current_date),
                'type': 'BUY',
                'price': price,
                'shares': self.position
            }
            self.trades.append(trade_executed)
            
        elif current_signal == -1 and self.position > 0:  # Sell signal
            self.capital = self.position * price
            self.position = 0
            trade_executed = {
                'date': str(current_date),
                'type': 'SELL',
                'price': price,
                'shares': self.position
            }
            self.trades.append(trade_executed)
        
        # Calculate current equity
        current_equity = self.capital + (self.position * price)
        self.equity_history.append(current_equity)
        
        # Store indicator values
        self.indicator_history.append({
            'date': str(current_date),
            'indicators': indicator_values
        })
        
        # Prepare state
        state = {
            'day': self.current_index + 1,
            'total_days': len(self.simulation_data),
            'date': str(current_date),
            'price': price,
            'open': float(current_row['Open']),
            'high': float(current_row['High']),
            'low': float(current_row['Low']),
            'volume': int(current_row['Volume']),
            'indicators': indicator_values,
            'signal': int(current_signal),
            'position': self.position,
            'capital': self.capital,
            'equity': current_equity,
            'trade': trade_executed,
            'total_trades': len(self.trades),
            'return_pct': ((current_equity - self.initial_capital) / self.initial_capital) * 100
        }
        
        self.current_index += 1
        return state
    
    def run_full_simulation(self) -> Generator[Dict[str, Any], None, None]:
        """
        Generator that yields each day's state.
        Use this for streaming real-time updates.
        """
        while True:
            state = self.step()
            if state is None:
                break
            yield state
    
    def get_final_results(self) -> Dict[str, Any]:
        """Get final simulation results."""
        final_equity = self.equity_history[-1] if self.equity_history else self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': final_equity - self.initial_capital,
            'return_percentage': ((final_equity - self.initial_capital) / self.initial_capital) * 100,
            'total_trades': len(self.trades),
            'trades': self.trades,
            'equity_curve': self.equity_history,
            'max_equity': max(self.equity_history) if self.equity_history else self.initial_capital,
            'min_equity': min(self.equity_history) if self.equity_history else self.initial_capital,
            'days_simulated': len(self.equity_history)
        }
    
    def reset(self):
        """Reset simulation to beginning."""
        self.current_index = 0
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.equity_history = []
        self.indicator_history = []


def simulate_with_playback(ticker: str, strategy: Strategy, 
                           initial_capital: float = 10000.0,
                           speed: float = 1.0) -> Dict[str, Any]:
    """
    Run simulation with real-time playback (for terminal demo).
    
    Args:
        ticker: Stock ticker
        strategy: Trading strategy
        initial_capital: Starting capital
        speed: Playback speed (1.0 = 1 day per second)
    """
    simulator = RealtimeSimulator(ticker, strategy, initial_capital)
    
    print("="*60)
    print(f"REAL-TIME SIMULATION: {ticker}")
    print("="*60)
    
    info = simulator.get_simulation_info()
    print(f"\nTraining Period: {info['training_period']['start']} to {info['training_period']['end']}")
    print(f"Simulation Period: {info['simulation_period']['start']} to {info['simulation_period']['end']}")
    print(f"Initial Capital: ${info['initial_capital']:,.2f}")
    print(f"\nStarting playback (1 day per {1/speed:.1f} seconds)...\n")
    
    time.sleep(2)
    
    for state in simulator.run_full_simulation():
        # Print current state
        print(f"\r[Day {state['day']}/{state['total_days']}] "
              f"{state['date']} | "
              f"Price: ${state['price']:.2f} | "
              f"Equity: ${state['equity']:,.2f} | "
              f"Return: {state['return_pct']:+.2f}%", 
              end='', flush=True)
        
        # Show trade execution
        if state['trade']:
            print(f"\n>>> {state['trade']['type']} @ ${state['trade']['price']:.2f}")
        
        # Wait for next day
        time.sleep(1 / speed)
    
    print("\n\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    
    results = simulator.get_final_results()
    print(f"\nFinal Equity: ${results['final_equity']:,.2f}")
    print(f"Total Return: ${results['total_return']:,.2f} ({results['return_percentage']:+.2f}%)")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Max Equity: ${results['max_equity']:,.2f}")
    print(f"Min Equity: ${results['min_equity']:,.2f}")
    
    return results
