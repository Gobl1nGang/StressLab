from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from .models import StrategyRequest, BacktestResponse, AnalysisResponse
import sys
import os

# Add project root to path to import engine and security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.backtester import Backtester
from engine.strategy import Strategy, SMA, RSI, MACD, Indicator
from engine.dataloader import fetch_market_data
from engine.simple_falsifier import SimpleFalsifier
from security.auth import Token, create_access_token, decode_access_token, verify_password, get_password_hash
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import requests

from .database import get_db, Base, engine
from .db_models import DbSimulationResult, User
from .user_models import UserCreate, UserResponse
from sqlalchemy.orm import Session
from .simulation_routes import router as simulation_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading Strategy Falsifier API")

# Include simulation router
app.include_router(simulation_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://128.189.63.209:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

falsifier = SimpleFalsifier(failure_threshold=0.6)

@app.on_event("startup")
def create_default_user():
    db = next(get_db())
    user = db.query(User).filter(User.username == "johndoe").first()
    if not user:
        from security.auth import get_password_hash
        hashed_password = get_password_hash("secret")
        new_user = User(username="johndoe", hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        print("Created default user: johndoe")

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
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
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
        elif ind_config.name == "MACD":
            indicators.append(MACD("MACD", ind_config.params))
    
    rules_dict = [rule.dict() for rule in request.rules]
    strategy = Strategy(indicators, rules_dict)

    # 3. Run Backtest
    backtester = Backtester(data, request.initial_capital)
    results = backtester.run(strategy)

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
            strategy_name="Custom Strategy",
            start_date=datetime.now(),
            end_date=datetime.now(),
            final_capital=results['final_capital'],
            total_return_pct=(results['final_capital'] - request.initial_capital) / request.initial_capital,
            max_drawdown_pct=0.0,
            falsification_triggered=False,
            trades_json=jsonable_encoder(formatted_trades),
            equity_curve_json=jsonable_encoder(results['equity_curve']),
            warnings_json=[],
            owner_id=current_user.id
        )
        db.add(db_result)
        db.commit()
    except Exception as e:
        print(f"Failed to save to DB: {e}")
    
    return BacktestResponse(
        final_capital=results['final_capital'],
        trades=formatted_trades,
        equity_curve=results['equity_curve']
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_strategy(request: StrategyRequest, current_user: dict = Depends(get_current_user)):
    try:
        data = fetch_market_data(request.ticker)
        
        indicators = []
        for ind_config in request.indicators:
            if ind_config.name == "SMA":
                indicators.append(SMA("SMA", ind_config.params))
            elif ind_config.name == "RSI":
                indicators.append(RSI("RSI", ind_config.params))
            elif ind_config.name == "MACD":
                indicators.append(MACD("MACD", ind_config.params))
        
        rules_dict = [rule.dict() for rule in request.rules]
        strategy = Strategy(indicators, rules_dict)
        backtester = Backtester(data, request.initial_capital)
        results = backtester.run(strategy)
        
        equity_curve = results['equity_curve']
        if len(equity_curve) < 10:
             return AnalysisResponse(failure_probability=0.0, recommendation="Not enough data")

        returns = [((b - a) / a) for a, b in zip(equity_curve[:-1], equity_curve[1:])]
        prob = falsifier.predict_failure_probability(returns)
        analysis = falsifier.analyze_failures(results['trades'], equity_curve)
        
        rec = analysis['recommendation']
        if prob > 0.7:
            rec = f"🚨 HIGH RISK: {rec}"
        elif prob > 0.4:
            rec = f"⚡ MODERATE RISK: {rec}"
            
        return AnalysisResponse(failure_probability=prob, recommendation=rec)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
