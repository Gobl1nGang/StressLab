import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_mock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Generate high-quality synthetic market data for demos."""
    days = 365 if period == "1y" else 730
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    
    # Base price based on common tickers
    base_price = 100.0
    if "BTC" in ticker.upper(): base_price = 40000.0
    elif "ETH" in ticker.upper(): base_price = 2000.0
    elif "AAPL" in ticker.upper(): base_price = 150.0
    
    # Random walk
    returns = np.random.normal(0.0005, 0.02, days)
    prices = base_price * (1 + returns).cumprod()
    
    data = pd.DataFrame({
        "Open": prices * (1 - 0.002),
        "High": prices * (1 + 0.005),
        "Low": prices * (1 - 0.005),
        "Close": prices,
        "Volume": np.random.randint(1000, 10000, days) * 1000
    }, index=dates)
    data.index.name = "Date"
    return data

def fetch_market_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    STRICT MODE: Fetch market data ONLY from local Nasdaq CSV library.
    No Yahoo Finance fallback, no synthetic fallback.
    """
    
    local_path = os.path.join("data", "training", "nasdaq", "csv", f"{ticker.upper()}.csv")
    
    if os.path.exists(local_path):
        try:
            print(f"Loading strict Nasdaq data for {ticker} from {local_path}...")
            data = pd.read_csv(local_path)
            
            # Normalize column names
            data.columns = [str(col).strip() for col in data.columns]
            
            # Handle Date column (Nasdaq CSVs use DD-MM-YYYY)
            if 'Date' in data.columns:
                try:
                    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
                except:
                    data['Date'] = pd.to_datetime(data['Date'])
                data.set_index('Date', inplace=True)
            
            # Map Adjusted Close to Close if Close is missing
            if 'Close' not in data.columns and 'Adjusted Close' in data.columns:
                data['Close'] = data['Adjusted Close']
                
            # Ensure basic columns exist
            if 'Close' in data.columns:
                if 'Open' not in data.columns: data['Open'] = data['Close'] * 0.998
                if 'High' not in data.columns: data['High'] = data['Close'] * 1.005
                if 'Low' not in data.columns: data['Low'] = data['Close'] * 0.995
                if 'Volume' not in data.columns: data['Volume'] = 100000
                
            # STRICT FILTER: Only numeric financial columns passed to engine
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            data = data[[col for col in expected_cols if col in data.columns]]
            
            # Final numeric validation
            data = data.apply(pd.to_numeric, errors='coerce').dropna()
            
            if data.empty:
                raise ValueError(f"Data file for {ticker} is empty or corrupted.")
                
            return data
        except Exception as e:
            raise RuntimeError(f"Error reading Nasdaq CSV for {ticker}: {e}")
    else:
        raise FileNotFoundError(f"Ticker '{ticker}' not found in limited Nasdaq CSV database.")

def load_macro_data(filepath: str) -> pd.DataFrame:
    """
    Load macro events data from a CSV file.
    """
    # For hackathon, we'll mock this or return empty if file not found
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        return pd.DataFrame()
