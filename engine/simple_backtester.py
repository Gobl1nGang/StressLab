class SimpleBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
    
    def run(self, signals):
        """Run backtest on signals"""
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
        for signal_data in signals:
            price = signal_data['price']
            signal = signal_data['signal']
            date = signal_data['date']
            
            # Execute trades
            if signal == 1 and self.position == 0:  # Buy
                self.position = self.capital / price
                self.capital = 0
                self.trades.append({
                    'date': date,
                    'type': 'BUY',
                    'price': price,
                    'shares': self.position
                })
            elif signal == -1 and self.position > 0:  # Sell
                self.capital = self.position * price
                self.position = 0
                self.trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'value': self.capital
                })
            
            # Calculate current equity
            current_equity = self.capital + (self.position * price)
            self.equity_curve.append({
                'date': date,
                'equity': current_equity,
                'price': price
            })
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': self.equity_curve[-1]['equity'] if self.equity_curve else self.initial_capital,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }