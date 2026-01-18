"""
Simple rule-based falsifier - no ML training required.

This approach:
1. Identifies failure periods from backtest results
2. Cross-references with macro events/news data
3. Counts trigger occurrences
4. Returns recommendations based on thresholds
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta

class SimpleFalsifier:
    def __init__(self, failure_threshold: float = 0.6):
        """
        Initialize rule-based falsifier.
        
        Args:
            failure_threshold: Percentage of failures that triggers a warning (0.0 to 1.0)
        """
        self.failure_threshold = failure_threshold
        self.macro_events = []  # Will be loaded from your dataset
    
    def load_macro_events(self, events_data: List[Dict]):
        """
        Load macro events/financial reports data.
        
        Expected format:
        [
            {'date': '2024-01-15', 'event': 'Fed Rate Hike', 'category': 'monetary_policy'},
            {'date': '2024-02-01', 'event': 'Earnings Report', 'category': 'earnings'},
            ...
        ]
        """
        self.macro_events = events_data
    
    def analyze_failures(self, trades: List[Dict], equity_curve: List[float]) -> Dict[str, Any]:
        """
        Analyze strategy failures and cross-reference with macro events.
        
        Args:
            trades: List of trades from backtest
            equity_curve: Equity curve from backtest
            
        Returns:
            Analysis results with failure patterns and recommendations
        """
        # 1. Identify failure periods (where equity drops)
        failure_periods = self._identify_failure_periods(equity_curve)
        
        # 2. Cross-reference with macro events
        correlated_events = self._cross_reference_events(failure_periods, trades)
        
        # 3. Count triggers and calculate metrics
        trigger_counts = self._count_triggers(correlated_events)
        
        # 4. Generate recommendations
        recommendation = self._generate_recommendation(trigger_counts, failure_periods)
        
        return {
            'failure_rate': len(failure_periods) / len(equity_curve) if equity_curve else 0,
            'correlated_events': correlated_events,
            'trigger_counts': trigger_counts,
            'recommendation': recommendation,
            'failure_periods': failure_periods
        }
    
    def _identify_failure_periods(self, equity_curve: List[float]) -> List[Dict]:
        """Identify periods where equity decreased."""
        failures = []
        
        for i in range(1, len(equity_curve)):
            if equity_curve[i] < equity_curve[i-1]:
                failures.append({
                    'index': i,
                    'drop_amount': equity_curve[i-1] - equity_curve[i],
                    'drop_percentage': (equity_curve[i-1] - equity_curve[i]) / equity_curve[i-1]
                })
        
        return failures
    
    def _cross_reference_events(self, failure_periods: List[Dict], trades: List[Dict]) -> List[Dict]:
        """Cross-reference failure periods with macro events."""
        correlated = []
        
        for failure in failure_periods:
            # Find trades around this failure
            failure_idx = failure['index']
            
            # Check if any macro events occurred around this time
            # (In real implementation, you'd match dates from trades to events)
            for event in self.macro_events:
                correlated.append({
                    'failure': failure,
                    'event': event,
                    'correlation_strength': 'high'  # Could be calculated based on timing
                })
        
        return correlated
    
    def _count_triggers(self, correlated_events: List[Dict]) -> Dict[str, int]:
        """Count occurrences of different event types during failures."""
        trigger_counts = {}
        
        for item in correlated_events:
            event_category = item['event'].get('category', 'unknown')
            trigger_counts[event_category] = trigger_counts.get(event_category, 0) + 1
        
        return trigger_counts
    
    def _generate_recommendation(self, trigger_counts: Dict[str, int], 
                                 failure_periods: List[Dict]) -> str:
        """Generate recommendation based on trigger analysis."""
        total_failures = len(failure_periods)
        
        if total_failures == 0:
            return "Strategy shows no significant failures. Continue monitoring."
        
        # Find most common trigger
        if trigger_counts:
            most_common_trigger = max(trigger_counts.items(), key=lambda x: x[1])
            trigger_name, count = most_common_trigger
            
            trigger_rate = count / total_failures
            
            if trigger_rate > self.failure_threshold:
                return (f"⚠️ HIGH RISK: Strategy fails {trigger_rate:.1%} of the time during "
                       f"'{trigger_name}' events. Avoid trading during these conditions.")
            elif trigger_rate > 0.3:
                return (f"⚡ MODERATE RISK: Strategy shows weakness during '{trigger_name}' events "
                       f"({trigger_rate:.1%} failure rate). Use caution.")
            else:
                return f"✓ Strategy is relatively stable. Minor correlation with '{trigger_name}' events."
        
        return "Strategy shows failures but no clear correlation with macro events."
    
    def predict_failure_probability(self, recent_returns: List[float]) -> float:
        """
        Simple heuristic: calculate failure probability based on recent volatility.
        No ML needed - just statistical analysis.
        """
        if len(recent_returns) < 5:
            return 0.5
        
        # Calculate volatility (standard deviation)
        import numpy as np
        volatility = np.std(recent_returns)
        
        # High volatility = higher failure probability
        # This is a simple heuristic, adjust thresholds as needed
        if volatility > 0.05:
            return 0.8
        elif volatility > 0.03:
            return 0.5
        else:
            return 0.2
