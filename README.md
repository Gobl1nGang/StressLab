# Trading Strategy Falsifier

A hackathon project to build, backtest, and falsify trading strategies using PyTorch and Macro Analysis.

## Project Structure

- `frontend/`: Next.js application (UI)
- `backend/`: FastAPI server (API)
- `engine/`: Python module for Backtesting and Falsification (PyTorch)
- `security/`: Authentication and authorization (JWT with Argon2)
- `data/`: Data storage

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+

### Backend Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the server:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```
   API will be available at `http://localhost:8000`.

### Frontend Setup
1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   App will be available at `http://localhost:3000`.

### Default Credentials
- Username: `johndoe`
- Password: `secret`

## Testing Integration

Run the integration test to verify all components are connected:
```bash
python test_integration.py
```

## Features
- **Authentication**: JWT-based auth with Argon2 password hashing
- **Strategy Builder**: Define strategies using indicators (SMA, RSI)
- **Backtester**: Simulate strategy performance on historical data
- **Falsifier**: PyTorch LSTM model that predicts strategy failure probability
- **Dashboard**: Visualize equity curves and risk analysis
