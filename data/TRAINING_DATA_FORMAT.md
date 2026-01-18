# Training Data Format Guide

## Directory Structure
```
data/
├── training/          # Your training datasets go here
│   ├── strategy1.csv
│   ├── strategy2.csv
│   └── ...
└── models/           # Trained model weights saved here
    ├── falsifier_weights.pth
    └── training_history.json
```

## CSV Format

Each CSV file should contain historical strategy returns with labels:

### Required Columns:
- `return`: Float value representing the strategy return at each time step
- `label`: Integer (0 or 1) where:
  - `1` = Strategy failed/lost money in the next period
  - `0` = Strategy succeeded/made money in the next period

### Optional Columns:
- `date`: Timestamp (for reference, not used in training)
- `ticker`: Stock symbol (for reference)
- `strategy_name`: Name of the strategy (for reference)

### Example CSV:
```csv
date,return,label,ticker,strategy_name
2024-01-01,0.02,0,AAPL,SMA_Cross
2024-01-02,-0.01,1,AAPL,SMA_Cross
2024-01-03,0.015,0,AAPL,SMA_Cross
2024-01-04,0.005,0,AAPL,SMA_Cross
2024-01-05,-0.03,1,AAPL,SMA_Cross
```

## How to Prepare Your Data

1. **Run historical backtests** on various strategies
2. **Calculate returns** for each time period
3. **Label each return**:
   - If the NEXT return is negative → label = 1 (failure)
   - If the NEXT return is positive → label = 0 (success)
4. **Save as CSV** in `data/training/` directory

## Training the Model

Once your data is ready:

```bash
# Basic training
python engine/train_model.py --data_dir ./data/training

# Custom parameters
python engine/train_model.py \
  --data_dir ./data/training \
  --epochs 1000 \
  --batch_size 64 \
  --model_path ./data/models/falsifier_weights.pth
```

## Model Architecture

- **Input**: Sequence of 10 consecutive returns
- **LSTM Layer**: 64 hidden units (configurable)
- **Output**: Probability of failure (0.0 to 1.0)
- **Loss**: Binary Cross Entropy
- **Optimizer**: Adam (lr=0.001)

## After Training

The model will automatically be loaded by the Falsifier class when you run backtests through the API.
