import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_market_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical market data using yfinance.
    """
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            raise ValueError(f"No data found for {ticker}")
        
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def load_macro_data(filepath: str) -> pd.DataFrame:
    """
    Load macro events data from a CSV file.
    """
    # For hackathon, we'll mock this or return empty if file not found
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        return pd.DataFrame()
