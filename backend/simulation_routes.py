"""
Backend endpoints for real-time simulation playback.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.realtime_simulator import RealtimeSimulator
from engine.strategy import Strategy, SMA, RSI, MACD
from backend.models import IndicatorConfig, Rule

router = APIRouter(prefix="/simulation", tags=["Real-Time Simulation"])

class SimulationRequest(BaseModel):
    ticker: str
    indicators: List[IndicatorConfig]
    rules: List[Rule]
    initial_capital: float = 10000.0
    speed: float = 1.0  # Days per second

@router.post("/info")
async def get_simulation_info(request: SimulationRequest):
    """Get information about the simulation period."""
    try:
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
        simulator = RealtimeSimulator(request.ticker, strategy, request.initial_capital)
        
        return simulator.get_simulation_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_simulation(request: SimulationRequest):
    """
    Stream real-time simulation updates.
    Returns Server-Sent Events (SSE) with day-by-day updates.
    """
    async def event_generator():
        try:
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
            simulator = RealtimeSimulator(request.ticker, strategy, request.initial_capital)
            
            # Send initial info
            info = simulator.get_simulation_info()
            yield f"data: {json.dumps({'type': 'info', 'data': info})}\n\n"
            
            # Stream simulation updates
            for state in simulator.run_full_simulation():
                yield f"data: {json.dumps({'type': 'update', 'data': state})}\n\n"
                await asyncio.sleep(1 / request.speed)
            
            # Send final results
            results = simulator.get_final_results()
            yield f"data: {json.dumps({'type': 'complete', 'data': results})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/run")
async def run_simulation(request: SimulationRequest):
    """
    Run full simulation and return all results at once.
    Use this for non-streaming mode.
    """
    try:
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
        simulator = RealtimeSimulator(request.ticker, strategy, request.initial_capital)
        
        # Run full simulation
        states = []
        for state in simulator.run_full_simulation():
            states.append(state)
        
        # Get final results
        results = simulator.get_final_results()
        
        return {
            'info': simulator.get_simulation_info(),
            'states': states,
            'results': results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
