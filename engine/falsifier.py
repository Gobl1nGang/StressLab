import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple

class FalsifierModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=32, output_size=1):
        super(FalsifierModel, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        out, _ = self.lstm(x)
        # Take the last time step
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

class Falsifier:
    def __init__(self):
        self.model = FalsifierModel()
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)

    def prepare_data(self, returns: List[float], seq_len: int = 10) -> Tuple[torch.Tensor, torch.Tensor]:
        X, y = [], []
        for i in range(len(returns) - seq_len):
            X.append(returns[i:i+seq_len])
            # Target: 1 if next return is negative (failure), 0 otherwise
            y.append(1 if returns[i+seq_len] < 0 else 0)
        
        return torch.tensor(X, dtype=torch.float32).unsqueeze(-1), torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

    def train(self, returns: List[float], epochs: int = 100):
        if len(returns) < 20:
            return # Not enough data
            
        X, y = self.prepare_data(returns)
        
        self.model.train()
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            outputs = self.model(X)
            loss = self.criterion(outputs, y)
            loss.backward()
            self.optimizer.step()
            
    def predict_failure_probability(self, recent_returns: List[float]) -> float:
        self.model.eval()
        if len(recent_returns) < 10:
            return 0.5 # Default uncertainty
            
        # Take last 10 returns
        seq = torch.tensor(recent_returns[-10:], dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
        with torch.no_grad():
            prob = self.model(seq)
        return prob.item()
