import yfinance as yf
import pandas as pd

ticker = "AAPL"
data = yf.download(ticker, period="1mo", progress=False)
print(f"Columns: {data.columns}")
print(f"Is MultiIndex: {isinstance(data.columns, pd.MultiIndex)}")
if isinstance(data.columns, pd.MultiIndex):
    print(f"Level 0: {data.columns.get_level_values(0)}")
    print(f"Level 1: {data.columns.get_level_values(1)}")
