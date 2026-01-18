class SimpleStrategy:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_sma(self, prices, window):
        """Calculate Simple Moving Average"""
        if len(prices) < window:
            return [0] * len(prices)
        
        sma = []
        for i in range(len(prices)):
            if i < window - 1:
                sma.append(0)
            else:
                avg = sum(prices[i-window+1:i+1]) / window
                sma.append(avg)
        return sma
    
    def generate_signals(self, data):
        """Generate buy/sell signals based on SMA crossover"""
        prices = [row['Close'] for row in data]
        
        short_sma = self.calculate_sma(prices, self.short_window)
        long_sma = self.calculate_sma(prices, self.long_window)
        
        signals = []
        for i in range(len(data)):
            signal = 0
            if i > 0 and short_sma[i] > 0 and long_sma[i] > 0:
                # Buy when short SMA crosses above long SMA
                if short_sma[i] > long_sma[i] and short_sma[i-1] <= long_sma[i-1]:
                    signal = 1
                # Sell when short SMA crosses below long SMA
                elif short_sma[i] < long_sma[i] and short_sma[i-1] >= long_sma[i-1]:
                    signal = -1
            
            signals.append({
                'date': data[i]['Date'],
                'price': data[i]['Close'],
                'short_sma': short_sma[i],
                'long_sma': long_sma[i],
                'signal': signal
            })
        
        return signals