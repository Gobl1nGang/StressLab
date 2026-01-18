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
            # Try to find the level that contains 'Close'
            if 'Close' in data.columns.get_level_values(0):
                data.columns = data.columns.get_level_values(0)
            elif 'Close' in data.columns.get_level_values(1):
                data.columns = data.columns.get_level_values(1)
            else:
                # Fallback: just take the first level and hope for the best
                data.columns = data.columns.get_level_values(0)
        
        # Ensure 'Close' column exists
        if 'Close' not in data.columns:
            # Some versions of yfinance use 'Adj Close' or 'Price'
            if 'Adj Close' in data.columns:
                data['Close'] = data['Adj Close']
            else:
                raise KeyError(f"DataFrame missing 'Close' column. Available: {data.columns.tolist()}")

        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        # Re-raise so the backend can return a 404/500 with the message
        raise e

def load_macro_data(filepath: str) -> pd.DataFrame:
    """
    Load macro events data from a CSV file.
    """
    # For hackathon, we'll mock this or return empty if file not found
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        return pd.DataFrame()
