from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from .models import StrategyRequest, BacktestResponse, AnalysisResponse
import sys
import os

# Add project root to path to import engine and security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.backtester import Backtester
from engine.strategy import Strategy, SMA, RSI, Indicator
from engine.dataloader import fetch_market_data
# from engine.falsifier import Falsifier 

import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from fastapi.encoders import jsonable_encoder



from security.auth import Token, create_access_token, decode_access_token, verify_password, get_password_hash
from security.validator import process_credentials
import requests

from .database import get_db
from .db_models import DbSimulationResult, User
from .user_models import UserCreate, UserResponse
from sqlalchemy.orm import Session

app = FastAPI(title="Trading Strategy Falsifier API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# falsifier = Falsifier()

SECURITY_SERVICE_URL = "http://localhost:8001"  # Your teammate's security service URL



async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_data = decode_access_token(token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == user_data.username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Step 1: Validate credentials format using teammate's security validator
    result = process_credentials({"username": form_data.username, "password": form_data.password})
    if isinstance(result, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 2: Check credentials against database
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 3: Create and return token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Step 1: Validate credentials using teammate's security validator
    result = process_credentials({"username": user.username, "password": user.password})
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    
    # Step 2: Check if user already exists in DB
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Step 3: Hash password and save to DB
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/")
async def root():
    return {"message": "Trading Strategy Falsifier API is running"}

@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: StrategyRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Fetch Data (Mock or Real)
    try:
        if request.ticker.upper() == "MOCK":
            # Generate Mock Data
            dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
            prices = 100 + np.random.randn(100).cumsum()
            data = pd.DataFrame({
                "Date": dates,
                "Open": prices,
                "High": prices + 1,
                "Low": prices - 1,
                "Close": prices,
                "Volume": 100000
            })
        else:
            data = fetch_market_data(request.ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 2. Build Strategy
    indicators = []
    for ind_config in request.indicators:
        if ind_config.name == "SMA":
            indicators.append(SMA("SMA", ind_config.params))
        elif ind_config.name == "RSI":
            indicators.append(RSI("RSI", ind_config.params))
        # Add more indicators here
    
    strategy = Strategy(indicators, request.rules)

    # 3. Run Backtest
    backtester = Backtester(data, request.initial_capital)
    results = backtester.run(strategy)

    # 4. Train Falsifier (Online learning for hackathon demo)
    # Calculate returns from equity curve
    equity_curve = results['equity_curve']
    if len(equity_curve) > 1:
        returns = [((b - a) / a) for a, b in zip(equity_curve[:-1], equity_curve[1:])]
        # falsifier.train(returns)
        pass

    # Format response
    formatted_trades = [
        {"date": str(t['date']), "type": t['type'], "price": t['price']}
        for t in results['trades']
    ]
    
    # 5. Save to Database
    try:
        db_result = DbSimulationResult(
            simulation_uuid=str(uuid.uuid4()),
            ticker=request.ticker,
            strategy_name="Custom Strategy", # Could be dynamic
            start_date=datetime.now(), # Should be from request/data
            end_date=datetime.now(),
            final_capital=results['final_capital'],
            total_return_pct=(results['final_capital'] - request.initial_capital) / request.initial_capital,
            max_drawdown_pct=0.0, # Backtester needs to return this
            falsification_triggered=False,
            trades_json=jsonable_encoder(formatted_trades),
            equity_curve_json=jsonable_encoder(results['equity_curve']),
            warnings_json=[],
            owner_id=current_user.get("id") # From the auth token
        )
        db.add(db_result)
        db.commit()
    except Exception as e:
        print(f"Failed to save to DB: {e}")
        # Don't fail the request just because DB save failed
    
    return BacktestResponse(
        final_capital=results['final_capital'],
        trades=formatted_trades,
        equity_curve=results['equity_curve']
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_strategy(request: StrategyRequest):
    # For hackathon, we'll just run a quick backtest to get recent returns
    # In production, we'd cache the backtest ID
    
    try:
        data = fetch_market_data(request.ticker)
        # Mock strategy construction (same as above)
        indicators = []
        for ind_config in request.indicators:
            if ind_config.name == "SMA":
                indicators.append(SMA("SMA", ind_config.params))
            elif ind_config.name == "RSI":
                indicators.append(RSI("RSI", ind_config.params))
        strategy = Strategy(indicators, request.rules)
        backtester = Backtester(data, request.initial_capital)
        results = backtester.run(strategy)
        
        equity_curve = results['equity_curve']
        if len(equity_curve) < 10:
             return AnalysisResponse(failure_probability=0.0, recommendation="Not enough data")

        returns = [((b - a) / a) for a, b in zip(equity_curve[:-1], equity_curve[1:])]
        
        # prob = falsifier.predict_failure_probability(returns)
        prob = 0.5 # Default mock value
        
        rec = "Strategy looks stable."
        if prob > 0.7:
            rec = "High risk of failure detected! Consider reducing leverage or adding a stop-loss."
        elif prob > 0.4:
            rec = "Moderate risk. Monitor volatility."
            
        return AnalysisResponse(failure_probability=prob, recommendation=rec)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

