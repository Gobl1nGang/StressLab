"""
Demo script for real-time simulation playback.

Run this to see the simulation in action!
"""

import sys
sys.path.append('.')

from engine.realtime_simulator import simulate_with_playback
from engine.strategy import Strategy, SMA, RSI

# Create a simple SMA crossover strategy
sma_short = SMA("SMA", {"window": 20})
sma_long = SMA("SMA", {"window": 50})
strategy = Strategy([sma_short, sma_long], [])

# Run simulation with playback
print("\n🎬 Starting Real-Time Simulation Demo\n")
results = simulate_with_playback(
    ticker="AAPL",
    strategy=strategy,
    initial_capital=10000.0,
    speed=2.0  # 2 days per second for faster demo
)

print("\n✅ Simulation complete! Check the results above.")
