"""
Preprocessing script to convert NASDAQ OHLCV CSV files into training data format.

This script:
1. Reads OHLCV data from NASDAQ ticker CSVs
2. Calculates daily returns
3. Generates labels (1 = next return is negative, 0 = positive)
4. Saves processed data ready for model training

Usage:
    python engine/preprocess_data.py --input_dir ./data/training/nasdaq/csv --output_dir ./data/training/processed
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm

def calculate_returns(df: pd.DataFrame, price_col: str = 'Close') -> pd.Series:
    """Calculate daily returns from price data."""
    return df[price_col].pct_change()

def generate_labels(returns: pd.Series) -> pd.Series:
    """
    Generate labels for training:
    - 1 if next return is negative (failure)
    - 0 if next return is positive (success)
    """
    # Shift returns by -1 to get "next" return
    next_returns = returns.shift(-1)
    labels = (next_returns < 0).astype(int)
    return labels

def preprocess_ticker(csv_path: Path, output_dir: Path) -> bool:
    """
    Preprocess a single ticker CSV file.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Check for required columns
        if 'Close' not in df.columns and 'Adjusted Close' not in df.columns:
            print(f"  Warning: {csv_path.name} missing Close/Adjusted Close column")
            return False
        
        # Use Adjusted Close if available, otherwise Close
        price_col = 'Adjusted Close' if 'Adjusted Close' in df.columns else 'Close'
        
        # Calculate returns
        df['return'] = calculate_returns(df, price_col)
        
        # Generate labels
        df['label'] = generate_labels(df['return'])
        
        # Drop NaN values (first row has NaN return, last row has NaN label)
        df = df.dropna(subset=['return', 'label'])
        
        # Keep only necessary columns
        if 'Date' in df.columns:
            output_df = df[['Date', 'return', 'label']].copy()
        else:
            output_df = df[['return', 'label']].copy()
        
        # Add ticker name
        ticker = csv_path.stem
        output_df['ticker'] = ticker
        
        # Save processed data
        output_path = output_dir / f"{ticker}.csv"
        output_df.to_csv(output_path, index=False)
        
        return True
        
    except Exception as e:
        print(f"  Error processing {csv_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Preprocess NASDAQ OHLCV data for training')
    parser.add_argument('--input_dir', type=str, default='./data/training/nasdaq/csv',
                        help='Directory containing NASDAQ ticker CSV files')
    parser.add_argument('--output_dir', type=str, default='./data/training/processed',
                        help='Directory to save processed training data')
    parser.add_argument('--combine', action='store_true',
                        help='Combine all tickers into a single CSV file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files
    csv_files = list(input_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_path}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Output directory: {output_path}")
    print()
    
    # Process each file
    successful = 0
    failed = 0
    all_data = []
    
    for csv_file in tqdm(csv_files, desc="Processing tickers"):
        if preprocess_ticker(csv_file, output_path):
            successful += 1
            
            # If combining, read the processed file
            if args.combine:
                processed_df = pd.read_csv(output_path / f"{csv_file.stem}.csv")
                all_data.append(processed_df)
        else:
            failed += 1
    
    print()
    print("="*60)
    print(f"Processing complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Output: {output_path}")
    
    # Combine all data if requested
    if args.combine and all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_path = output_path / "combined_training_data.csv"
        combined_df.to_csv(combined_path, index=False)
        print(f"\nCombined data saved to: {combined_path}")
        print(f"Total samples: {len(combined_df)}")
    
    print("="*60)
    print()
    print("Next steps:")
    print(f"  1. Review processed data in {output_path}")
    print(f"  2. Run training: python engine/train_model.py --data_dir {output_path}")


if __name__ == "__main__":
    main()
