import random
from datetime import datetime, timedelta

def generate_mock_data(days=100):
    """Generate mock stock data for testing"""
    data = []
    price = 100.0
    date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        # Random walk with slight upward bias
        change = random.uniform(-0.03, 0.035)
        price = max(price * (1 + change), 10.0)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Open': price * random.uniform(0.99, 1.01),
            'High': price * random.uniform(1.0, 1.03),
            'Low': price * random.uniform(0.97, 1.0),
            'Close': price,
            'Volume': random.randint(1000000, 5000000)
        })
        date += timedelta(days=1)
    
    return data