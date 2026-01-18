"""
Training script for Advanced ML Falsifier.

Trains all models:
1. LSTM Predictor (future failures)
2. Complex Pattern Detector (non-linear relationships)
3. Anomaly Detector (unusual patterns)

Usage:
    python engine/train_advanced.py --data_dir ./data/training/processed --epochs 300
"""

import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm
from sklearn.model_selection import train_test_split

from advanced_falsifier import (
    LSTMPredictor, ComplexPatternNet, AnomalyDetector, AdvancedFalsifier
)

def load_all_data(data_dir: str):
    """Load all processed CSV files."""
    data_path = Path(data_dir)
    all_returns = []
    all_labels = []
    
    csv_files = list(data_path.glob("*.csv"))
    print(f"Loading {len(csv_files)} files...")
    
    for csv_file in tqdm(csv_files[:500], desc="Loading data"):  # Limit for memory
        try:
            if csv_file.stat().st_size == 0:
                continue
            
            df = pd.read_csv(csv_file)
            if 'return' not in df.columns or 'label' not in df.columns:
                continue
            
            all_returns.extend(df['return'].values.tolist())
            all_labels.extend(df['label'].values.tolist())
        except:
            continue
    
    return np.array(all_returns), np.array(all_labels)

def prepare_lstm_sequences(returns, labels, seq_len=10):
    """Prepare sequences for LSTM training."""
    X, y = [], []
    
    for i in range(len(returns) - seq_len):
        # Create feature sequence
        seq_features = []
        for j in range(i, i + seq_len):
            features = [
                returns[j],
                np.std(returns[max(0, j-5):j+1]) if j > 0 else 0,  # Volatility
                np.mean(returns[max(0, j-5):j+1]) if j > 0 else 0,  # Trend
                returns[j-1] if j > 0 else 0,  # Previous return
                1 if j > 0 and returns[j] < 0 else 0  # Is negative
            ]
            seq_features.append(features)
        
        X.append(seq_features)
        y.append(labels[i + seq_len])
    
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

def prepare_pattern_features(returns, labels, window=20):
    """Prepare features for pattern detector."""
    X, y = [], []
    
    for i in range(window, len(returns)):
        features = []
        
        # Recent returns
        recent = returns[i-window:i]
        features.extend(recent[:10].tolist() + [0] * max(0, 10 - len(recent)))
        
        # Statistical features
        features.append(np.std(recent))
        features.append(np.mean(recent))
        features.append(recent[-1] if len(recent) > 0 else 0)
        features.append(np.min(recent))
        features.append(np.max(recent))
        
        # Trend features
        if len(recent) > 1:
            features.append(1 if recent[-1] > recent[0] else 0)
        else:
            features.append(0)
        
        # Pad to 20 features
        while len(features) < 20:
            features.append(0)
        
        X.append(features[:20])
        y.append(labels[i])
    
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

def train_lstm(model, X_train, y_train, X_test, y_test, epochs=100, batch_size=64):
    """Train LSTM predictor."""
    print("\n" + "="*60)
    print("Training LSTM Predictor")
    print("="*60)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    dataset = torch.utils.data.TensorDataset(X_train, y_train)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    best_acc = 0
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        # Evaluate
        if (epoch + 1) % 20 == 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test)
                test_loss = criterion(test_outputs, y_test)
                predicted = (test_outputs > 0.5).float()
                accuracy = (predicted == y_test).sum().item() / y_test.size(0) * 100
                
                if accuracy > best_acc:
                    best_acc = accuracy
                
                print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss/len(dataloader):.4f}, "
                      f"Test Acc: {accuracy:.2f}%, Best: {best_acc:.2f}%")
    
    return best_acc

def train_pattern_detector(model, X_train, y_train, X_test, y_test, epochs=100, batch_size=128):
    """Train complex pattern detector."""
    print("\n" + "="*60)
    print("Training Complex Pattern Detector")
    print("="*60)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    dataset = torch.utils.data.TensorDataset(X_train, y_train)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    best_acc = 0
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        if (epoch + 1) % 20 == 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test)
                test_loss = criterion(test_outputs, y_test)
                predicted = (test_outputs > 0.5).float()
                accuracy = (predicted == y_test).sum().item() / y_test.size(0) * 100
                
                if accuracy > best_acc:
                    best_acc = accuracy
                
                print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss/len(dataloader):.4f}, "
                      f"Test Acc: {accuracy:.2f}%, Best: {best_acc:.2f}%")
    
    return best_acc

def train_anomaly_detector(detector, X_train):
    """Train anomaly detector."""
    print("\n" + "="*60)
    print("Training Anomaly Detector")
    print("="*60)
    
    detector.fit(X_train.numpy())
    print("✓ Anomaly detector trained")

def main():
    parser = argparse.ArgumentParser(description='Train Advanced ML Falsifier')
    parser.add_argument('--data_dir', type=str, default='./data/training/processed')
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--model_dir', type=str, default='./data/models')
    
    args = parser.parse_args()
    
    # Load data
    print("Loading training data...")
    returns, labels = load_all_data(args.data_dir)
    print(f"Loaded {len(returns)} samples")
    
    # Prepare LSTM data
    print("\nPreparing LSTM sequences...")
    X_lstm, y_lstm = prepare_lstm_sequences(returns, labels)
    X_lstm_train, X_lstm_test, y_lstm_train, y_lstm_test = train_test_split(
        X_lstm, y_lstm, test_size=0.2, random_state=42
    )
    print(f"LSTM: {len(X_lstm_train)} train, {len(X_lstm_test)} test")
    
    # Prepare pattern detector data
    print("\nPreparing pattern features...")
    X_pattern, y_pattern = prepare_pattern_features(returns, labels)
    X_pattern_train, X_pattern_test, y_pattern_train, y_pattern_test = train_test_split(
        X_pattern, y_pattern, test_size=0.2, random_state=42
    )
    print(f"Pattern: {len(X_pattern_train)} train, {len(X_pattern_test)} test")
    
    # Initialize models
    lstm_model = LSTMPredictor(input_size=5, hidden_size=64, num_layers=2)
    pattern_model = ComplexPatternNet(input_size=20, hidden_sizes=[128, 64, 32])
    anomaly_detector = AnomalyDetector()
    
    # Train LSTM
    lstm_acc = train_lstm(lstm_model, X_lstm_train, y_lstm_train, 
                         X_lstm_test, y_lstm_test, epochs=args.epochs, 
                         batch_size=args.batch_size)
    
    # Train pattern detector
    pattern_acc = train_pattern_detector(pattern_model, X_pattern_train, y_pattern_train,
                                        X_pattern_test, y_pattern_test, epochs=args.epochs,
                                        batch_size=args.batch_size * 2)
    
    # Train anomaly detector
    train_anomaly_detector(anomaly_detector, X_pattern_train)
    
    # Save models
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    torch.save(lstm_model.state_dict(), model_dir / "lstm_predictor.pth")
    torch.save(pattern_model.state_dict(), model_dir / "pattern_detector.pth")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"LSTM Predictor - Best Accuracy: {lstm_acc:.2f}%")
    print(f"Pattern Detector - Best Accuracy: {pattern_acc:.2f}%")
    print(f"Models saved to: {model_dir}")
    print("="*60)

if __name__ == "__main__":
    main()
