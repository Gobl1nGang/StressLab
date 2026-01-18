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
from engine.simple_falsifier import SimpleFalsifier  # Using simple rule-based approach
from security.auth import Token, create_access_token, decode_access_token, verify_password, get_password_hash
from .simulation_routes import router as simulation_router  # Real-time simulation

app = FastAPI(title="Trading Strategy Falsifier API")

# Include simulation router
app.include_router(simulation_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

falsifier = SimpleFalsifier(failure_threshold=0.6)  # Rule-based, no training needed

# Mock User DB
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": get_password_hash("secret"),
        "disabled": False,
    }
}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = decode_access_token(token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = fake_users_db.get(user_data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "Trading Strategy Falsifier API is running"}

@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: StrategyRequest, current_user: dict = Depends(get_current_user)):
    # 1. Fetch Data
    try:
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
    
    # Convert Pydantic rules to dicts for the engine
    rules_dict = [rule.dict() for rule in request.rules]
    strategy = Strategy(indicators, rules_dict)

    # 3. Run Backtest
    backtester = Backtester(data, request.initial_capital)
    results = backtester.run(strategy)

    # No training needed - using rule-based falsifier

    # Format response
    formatted_trades = [
        {"date": str(t['date']), "type": t['type'], "price": t['price']}
        for t in results['trades']
    ]
    
    return BacktestResponse(
        final_capital=results['final_capital'],
        trades=formatted_trades,
        equity_curve=results['equity_curve']
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_strategy(request: StrategyRequest, current_user: dict = Depends(get_current_user)):
    """
    Analyze strategy using rule-based falsifier.
    
    Returns:
    - Failure probability based on volatility
    - Recommendation based on failure patterns
    """
    try:
        data = fetch_market_data(request.ticker)
        
        # Build strategy
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

        # Calculate returns
        returns = [((b - a) / a) for a, b in zip(equity_curve[:-1], equity_curve[1:])]
        
        # Use simple falsifier for analysis
        prob = falsifier.predict_failure_probability(returns)
        
        # Get detailed analysis
        analysis = falsifier.analyze_failures(results['trades'], equity_curve)
        
        # Generate recommendation
        rec = analysis['recommendation']
        if prob > 0.7:
            rec = f"🚨 HIGH RISK (volatility-based): {rec}"
        elif prob > 0.4:
            rec = f"⚡ MODERATE RISK: {rec}"
            
        return AnalysisResponse(failure_probability=prob, recommendation=rec)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

