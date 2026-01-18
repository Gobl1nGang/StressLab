"""
Training script for the Falsifier PyTorch model.

This script pre-trains the model on historical trading data and saves the weights.
The trained model will be loaded by the Falsifier class for inference.

Usage:
    python engine/train_model.py --data_dir ./data/training --epochs 500
"""

import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import List, Tuple
import json

from falsifier import FalsifierModel

class ModelTrainer:
    def __init__(self, model_save_path: str = "./data/models/falsifier_weights.pth"):
        self.model = FalsifierModel(input_size=1, hidden_size=64, output_size=1)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.model_save_path = model_save_path
        self.training_history = []
        
    def load_training_data(self, data_dir: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Load training data from CSV files in the specified directory.
        
        Expected format:
        - CSV files with columns: ['date', 'return', 'label']
        - 'return': strategy returns (float)
        - 'label': 1 if failure, 0 if success (int)
        
        Or provide your own format and modify this function.
        """
        data_path = Path(data_dir)
        all_sequences = []
        all_labels = []
        
        print(f"Loading training data from {data_dir}...")
        
        # Load all CSV files
        csv_files = list(data_path.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in {data_dir}")
        
        for csv_file in csv_files:
            print(f"  Loading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            
            # Validate columns
            if 'return' not in df.columns or 'label' not in df.columns:
                print(f"  Warning: Skipping {csv_file.name} - missing 'return' or 'label' columns")
                continue
            
            returns = df['return'].values
            labels = df['label'].values
            
            # Create sequences (sliding window of 10)
            seq_len = 10
            for i in range(len(returns) - seq_len):
                all_sequences.append(returns[i:i+seq_len])
                all_labels.append(labels[i+seq_len])
        
        if not all_sequences:
            raise ValueError("No valid training data found!")
        
        print(f"Loaded {len(all_sequences)} training sequences from {len(csv_files)} files")
        
        X = torch.tensor(all_sequences, dtype=torch.float32).unsqueeze(-1)
        y = torch.tensor(all_labels, dtype=torch.float32).unsqueeze(-1)
        
        return X, y
    
    def train(self, X: torch.Tensor, y: torch.Tensor, epochs: int = 500, batch_size: int = 32):
        """
        Train the model on the provided data.
        """
        print(f"\nStarting training for {epochs} epochs...")
        print(f"Training samples: {len(X)}")
        print(f"Model architecture: {self.model}")
        
        dataset = torch.utils.data.TensorDataset(X, y)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            correct = 0
            total = 0
            
            for batch_X, batch_y in dataloader:
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
                
                # Calculate accuracy
                predicted = (outputs > 0.5).float()
                correct += (predicted == batch_y).sum().item()
                total += batch_y.size(0)
            
            avg_loss = epoch_loss / len(dataloader)
            accuracy = 100 * correct / total
            
            self.training_history.append({
                'epoch': epoch + 1,
                'loss': avg_loss,
                'accuracy': accuracy
            })
            
            if (epoch + 1) % 50 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
        
        print("\nTraining complete!")
        print(f"Final Loss: {self.training_history[-1]['loss']:.4f}")
        print(f"Final Accuracy: {self.training_history[-1]['accuracy']:.2f}%")
    
    def save_model(self):
        """
        Save the trained model weights and training history.
        """
        save_path = Path(self.model_save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model state dict
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_config': {
                'input_size': 1,
                'hidden_size': self.model.hidden_size,
                'output_size': 1
            },
            'training_history': self.training_history
        }, save_path)
        
        print(f"\nModel saved to {save_path}")
        
        # Save training history as JSON
        history_path = save_path.parent / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        print(f"Training history saved to {history_path}")
    
    def evaluate(self, X: torch.Tensor, y: torch.Tensor):
        """
        Evaluate the model on test data.
        """
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X)
            loss = self.criterion(outputs, y)
            predicted = (outputs > 0.5).float()
            accuracy = 100 * (predicted == y).sum().item() / y.size(0)
        
        print(f"\nEvaluation Results:")
        print(f"  Loss: {loss.item():.4f}")
        print(f"  Accuracy: {accuracy:.2f}%")
        
        return loss.item(), accuracy


def main():
    parser = argparse.ArgumentParser(description='Train the Falsifier model')
    parser.add_argument('--data_dir', type=str, default='./data/training',
                        help='Directory containing training CSV files')
    parser.add_argument('--epochs', type=int, default=500,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size for training')
    parser.add_argument('--model_path', type=str, default='./data/models/falsifier_weights.pth',
                        help='Path to save the trained model')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ModelTrainer(model_save_path=args.model_path)
    
    # Load data
    try:
        X, y = trainer.load_training_data(args.data_dir)
    except Exception as e:
        print(f"Error loading data: {e}")
        print("\nPlease ensure your training data is in the correct format:")
        print("  - CSV files in the data directory")
        print("  - Columns: 'return' (float) and 'label' (0 or 1)")
        return
    
    # Split into train/test (80/20)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Train set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train
    trainer.train(X_train, y_train, epochs=args.epochs, batch_size=args.batch_size)
    
    # Evaluate
    trainer.evaluate(X_test, y_test)
    
    # Save
    trainer.save_model()
    
    print("\n" + "="*60)
    print("Training complete! Model is ready to use.")
    print("="*60)


if __name__ == "__main__":
    main()
