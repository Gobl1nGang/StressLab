#!/usr/bin/env python3
"""
Minimal working simulation demo
"""

import sys
import time
sys.path.append('.')

from engine.mock_data import generate_mock_data
from engine.simple_strategy import SimpleStrategy
from engine.simple_backtester import SimpleBacktester

def run_simulation():
    print("🎬 Starting Trading Strategy Simulation")
    print("=" * 50)
    
    # Generate mock data
    print("📊 Generating mock market data...")
    data = generate_mock_data(days=60)
    print(f"✓ Generated {len(data)} days of data")
    
    # Create strategy
    print("🧠 Creating SMA crossover strategy (5/20)...")
    strategy = SimpleStrategy(short_window=5, long_window=20)
    
    # Generate signals
    print("📈 Generating trading signals...")
    signals = strategy.generate_signals(data)
    
    # Count signals
    buy_signals = sum(1 for s in signals if s['signal'] == 1)
    sell_signals = sum(1 for s in signals if s['signal'] == -1)
    print(f"✓ Generated {buy_signals} BUY and {sell_signals} SELL signals")
    
    # Run backtest
    print("💰 Running backtest...")
    backtester = SimpleBacktester(initial_capital=10000)
    results = backtester.run(signals)
    
    # Show results
    print("\n" + "=" * 50)
    print("📊 SIMULATION RESULTS")
    print("=" * 50)
    
    final_equity = results['final_equity']
    initial_capital = results['initial_capital']
    total_return = final_equity - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Equity:   ${final_equity:,.2f}")
    print(f"Total Return:   ${total_return:,.2f} ({return_pct:+.2f}%)")
    print(f"Total Trades:   {len(results['trades'])}")
    
    if results['trades']:
        print("\n📋 Trade History:")
        for trade in results['trades'][:5]:  # Show first 5 trades
            print(f"  {trade['date']}: {trade['type']} @ ${trade['price']:.2f}")
        if len(results['trades']) > 5:
            print(f"  ... and {len(results['trades']) - 5} more trades")
    
    # Show equity progression
    print("\n📈 Equity Curve (last 10 days):")
    for equity_point in results['equity_curve'][-10:]:
        date = equity_point['date']
        equity = equity_point['equity']
        price = equity_point['price']
        print(f"  {date}: ${equity:,.2f} (Price: ${price:.2f})")
    
    return results

if __name__ == "__main__":
    try:
        results = run_simulation()
        print("\n✅ Simulation completed successfully!")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()