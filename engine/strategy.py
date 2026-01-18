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

class MACD(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.params.get('fast', 12)
        slow = self.params.get('slow', 26)
        signal = self.params.get('signal', 9)
        
        exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return pd.DataFrame({
            f"MACD_{fast}_{slow}": macd,
            f"MACD_Signal_{signal}": signal_line,
            f"MACD_Hist": histogram
        })

class Strategy:
    def __init__(self, indicators: List[Indicator], rules: List[Dict]):
        self.indicators = indicators
        self.rules = rules

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # 1. Calculate all indicators
        for ind in self.indicators:
            result = ind.calculate(df)
            if isinstance(result, pd.Series):
                df[ind.name] = result
            else:
                for col in result.columns:
                    df[col] = result[col]
        
        # 2. Initialize Signal column
        df['Signal'] = 0
        
        # 3. Apply Rules
        # Rules format: {"type": "buy/sell", "condition": "indicator > value", "indicator": "RSI", "operator": ">", "value": 70}
        # Or crossover: {"type": "buy", "condition": "crossover", "ind1": "MACD", "ind2": "MACD_Signal"}
        
        for i in range(1, len(df)):
            buy_conditions = [r for r in self.rules if r['type'] == 'buy']
            sell_conditions = [r for r in self.rules if r['type'] == 'sell']
            
            # Check Buy Rules
            buy_triggered = False
            if buy_conditions:
                buy_triggered = True
                for rule in buy_conditions:
                    if not self._check_rule(df, i, rule):
                        buy_triggered = False
                        break
            
            # Check Sell Rules
            sell_triggered = False
            if sell_conditions:
                sell_triggered = True
                for rule in sell_conditions:
                    if not self._check_rule(df, i, rule):
                        sell_triggered = False
                        break
            
            if buy_triggered:
                df.iloc[i, df.columns.get_loc('Signal')] = 1
            elif sell_triggered:
                df.iloc[i, df.columns.get_loc('Signal')] = -1
                
        return df

    def _check_rule(self, df: pd.DataFrame, i: int, rule: Dict) -> bool:
        try:
            op = rule.get('operator')
            ind = rule.get('indicator')
            val = rule.get('value')
            
            if rule.get('condition') == 'crossover':
                ind1 = rule.get('ind1')
                ind2 = rule.get('ind2')
                # Cross above: prev ind1 < prev ind2 AND curr ind1 > curr ind2
                return (df[ind1].iloc[i-1] < df[ind2].iloc[i-1] and 
                        df[ind1].iloc[i] > df[ind2].iloc[i])
            
            if rule.get('condition') == 'crossunder':
                ind1 = rule.get('ind1')
                ind2 = rule.get('ind2')
                return (df[ind1].iloc[i-1] > df[ind2].iloc[i-1] and 
                        df[ind1].iloc[i] < df[ind2].iloc[i])

            # Simple threshold rules
            curr_val = df[ind].iloc[i]
            if op == '>': return curr_val > val
            if op == '<': return curr_val < val
            if op == '>=': return curr_val >= val
            if op == '<=': return curr_val <= val
            
        except Exception as e:
            return False
        return False
