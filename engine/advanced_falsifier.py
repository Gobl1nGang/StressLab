"""
Advanced ML-based Falsifier with comprehensive capabilities:
1. Future failure prediction (LSTM)
2. Complex non-linear relationships (Neural Network)
3. Adaptive learning (Online learning)
4. Anomaly detection (Isolation Forest)
5. NLP for news sentiment (Transformer-based)
6. Hybrid rule-based + ML approach
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. FUTURE PREDICTION MODEL (LSTM)
# ============================================================================

class LSTMPredictor(nn.Module):
    """LSTM model for predicting future failures."""
    def __init__(self, input_size=5, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(32, output_size)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Take last time step
        out = lstm_out[:, -1, :]
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return self.sigmoid(out)


# ============================================================================
# 2. COMPLEX PATTERN DETECTOR (Deep Neural Network)
# ============================================================================

class ComplexPatternNet(nn.Module):
    """Deep network for detecting complex non-linear relationships."""
    def __init__(self, input_size=20, hidden_sizes=[128, 64, 32], output_size=1):
        super(ComplexPatternNet, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        layers.append(nn.Sigmoid())
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


# ============================================================================
# 3. ANOMALY DETECTOR
# ============================================================================

class AnomalyDetector:
    """Isolation Forest for detecting unusual failure patterns."""
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, data: np.ndarray):
        """Train on normal patterns."""
        scaled_data = self.scaler.fit_transform(data)
        self.model.fit(scaled_data)
        self.is_fitted = True
    
    def detect_anomaly(self, data: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if pattern is anomalous.
        Returns: (is_anomaly, anomaly_score)
        """
        if not self.is_fitted:
            return False, 0.0
        
        scaled_data = self.scaler.transform(data.reshape(1, -1))
        prediction = self.model.predict(scaled_data)[0]
        score = self.model.score_samples(scaled_data)[0]
        
        is_anomaly = prediction == -1
        return is_anomaly, abs(score)


# ============================================================================
# 4. NLP SENTIMENT ANALYZER (Simplified - would use transformers in production)
# ============================================================================

class NewsSentimentAnalyzer:
    """Analyze news sentiment to predict market impact."""
    def __init__(self):
        # In production, would use: transformers.pipeline("sentiment-analysis")
        # For hackathon, using simple keyword-based approach
        self.negative_keywords = [
            'crash', 'decline', 'fall', 'drop', 'recession', 'crisis',
            'concern', 'worry', 'risk', 'threat', 'volatility', 'uncertainty'
        ]
        self.positive_keywords = [
            'growth', 'rise', 'gain', 'rally', 'surge', 'optimism',
            'confidence', 'strong', 'robust', 'recovery'
        ]
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of news text.
        Returns: {'sentiment': score, 'confidence': conf}
        """
        text_lower = text.lower()
        
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        
        total = negative_count + positive_count
        if total == 0:
            return {'sentiment': 0.0, 'confidence': 0.0}
        
        # -1 (very negative) to +1 (very positive)
        sentiment = (positive_count - negative_count) / total
        confidence = min(total / 10.0, 1.0)  # More keywords = higher confidence
        
        return {'sentiment': sentiment, 'confidence': confidence}


# ============================================================================
# 5. ADAPTIVE LEARNER (Online Learning)
# ============================================================================

class AdaptiveLearner:
    """Continuously learns from new data."""
    def __init__(self, model: nn.Module, lr=0.001):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=lr)
        self.criterion = nn.BCELoss()
        self.update_count = 0
    
    def update(self, X: torch.Tensor, y: torch.Tensor):
        """Update model with new data point."""
        self.model.train()
        self.optimizer.zero_grad()
        
        output = self.model(X)
        loss = self.criterion(output, y)
        loss.backward()
        self.optimizer.step()
        
        self.update_count += 1
        return loss.item()
    
    def should_retrain(self, threshold=100):
        """Check if full retraining is needed."""
        return self.update_count >= threshold


# ============================================================================
# 6. HYBRID FALSIFIER (Combines All Approaches)
# ============================================================================

class AdvancedFalsifier:
    """
    Comprehensive falsifier combining:
    - Rule-based logic (fast, interpretable)
    - LSTM prediction (future failures)
    - Complex pattern detection (non-linear relationships)
    - Anomaly detection (unusual patterns)
    - NLP sentiment (news analysis)
    - Adaptive learning (continuous improvement)
    """
    
    def __init__(self, model_dir: str = "./data/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all components
        self.lstm_predictor = LSTMPredictor()
        self.pattern_detector = ComplexPatternNet()
        self.anomaly_detector = AnomalyDetector()
        self.sentiment_analyzer = NewsSentimentAnalyzer()
        
        # Adaptive learners
        self.lstm_learner = AdaptiveLearner(self.lstm_predictor)
        self.pattern_learner = AdaptiveLearner(self.pattern_detector)
        
        # Load pre-trained weights if available
        self._load_models()
        
        # Rule-based thresholds
        self.failure_threshold = 0.6
        self.anomaly_threshold = 0.7
    
    def _load_models(self):
        """Load pre-trained model weights."""
        lstm_path = self.model_dir / "lstm_predictor.pth"
        pattern_path = self.model_dir / "pattern_detector.pth"
        
        if lstm_path.exists():
            self.lstm_predictor.load_state_dict(
                torch.load(lstm_path, map_location='cpu', weights_only=True)
            )
            print("✓ Loaded LSTM predictor")
        
        if pattern_path.exists():
            self.pattern_detector.load_state_dict(
                torch.load(pattern_path, map_location='cpu', weights_only=True)
            )
            print("✓ Loaded pattern detector")
    
    def save_models(self):
        """Save trained models."""
        torch.save(self.lstm_predictor.state_dict(), 
                  self.model_dir / "lstm_predictor.pth")
        torch.save(self.pattern_detector.state_dict(),
                  self.model_dir / "pattern_detector.pth")
        print("✓ Models saved")
    
    def prepare_features(self, returns: List[float], 
                        macro_indicators: Dict[str, float] = None) -> np.ndarray:
        """
        Prepare feature vector from returns and macro indicators.
        
        Features include:
        - Recent returns (last 10)
        - Volatility
        - Trend
        - Macro indicators (VIX, interest rates, etc.)
        """
        features = []
        
        # Returns-based features
        recent_returns = returns[-10:] if len(returns) >= 10 else returns
        features.extend(recent_returns + [0] * (10 - len(recent_returns)))
        
        # Statistical features
        if len(returns) > 1:
            features.append(np.std(returns))  # Volatility
            features.append(np.mean(returns))  # Average return
            features.append(returns[-1] if returns else 0)  # Latest return
        else:
            features.extend([0, 0, 0])
        
        # Macro indicators (if provided)
        if macro_indicators:
            features.append(macro_indicators.get('vix', 0))
            features.append(macro_indicators.get('interest_rate', 0))
            features.append(macro_indicators.get('unemployment', 0))
        else:
            features.extend([0, 0, 0])
        
        # Pad to 20 features
        while len(features) < 20:
            features.append(0)
        
        return np.array(features[:20], dtype=np.float32)
    
    def predict_future_failure(self, returns: List[float], 
                              macro_indicators: Dict[str, float] = None) -> float:
        """
        Predict probability of failure in next period using LSTM.
        """
        if len(returns) < 10:
            return 0.5
        
        # Prepare sequence
        features = []
        for i in range(len(returns) - 10, len(returns)):
            feat = self.prepare_features(returns[:i+1], macro_indicators)
            features.append(feat[:5])  # Use first 5 features for LSTM
        
        X = torch.tensor([features], dtype=torch.float32)
        
        self.lstm_predictor.eval()
        with torch.no_grad():
            prob = self.lstm_predictor(X)
        
        return prob.item()
    
    def detect_complex_patterns(self, returns: List[float],
                               macro_indicators: Dict[str, float] = None) -> float:
        """
        Detect complex non-linear failure patterns.
        """
        features = self.prepare_features(returns, macro_indicators)
        X = torch.tensor([features], dtype=torch.float32)
        
        self.pattern_detector.eval()
        with torch.no_grad():
            prob = self.pattern_detector(X)
        
        return prob.item()
    
    def check_anomaly(self, returns: List[float]) -> Tuple[bool, float, str]:
        """
        Check if current pattern is anomalous.
        Returns: (is_anomaly, score, description)
        """
        if len(returns) < 10:
            return False, 0.0, "Insufficient data"
        
        features = self.prepare_features(returns)
        is_anomaly, score = self.anomaly_detector.detect_anomaly(features)
        
        if is_anomaly:
            desc = f"Unusual pattern detected (anomaly score: {score:.2f})"
        else:
            desc = "Pattern within normal range"
        
        return is_anomaly, score, desc
    
    def analyze_news_impact(self, news_texts: List[str]) -> Dict[str, Any]:
        """
        Analyze news sentiment and predict market impact.
        """
        sentiments = [self.sentiment_analyzer.analyze_sentiment(text) 
                     for text in news_texts]
        
        if not sentiments:
            return {'avg_sentiment': 0.0, 'confidence': 0.0, 'impact': 'neutral'}
        
        avg_sentiment = np.mean([s['sentiment'] for s in sentiments])
        avg_confidence = np.mean([s['confidence'] for s in sentiments])
        
        if avg_sentiment < -0.3:
            impact = 'negative'
        elif avg_sentiment > 0.3:
            impact = 'positive'
        else:
            impact = 'neutral'
        
        return {
            'avg_sentiment': avg_sentiment,
            'confidence': avg_confidence,
            'impact': impact,
            'num_articles': len(news_texts)
        }
    
    def comprehensive_analysis(self, 
                              returns: List[float],
                              macro_indicators: Dict[str, float] = None,
                              news_texts: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using all methods.
        """
        results = {}
        
        # 1. Future prediction (LSTM)
        results['future_failure_prob'] = self.predict_future_failure(returns, macro_indicators)
        
        # 2. Complex patterns
        results['complex_pattern_prob'] = self.detect_complex_patterns(returns, macro_indicators)
        
        # 3. Anomaly detection
        is_anomaly, anomaly_score, anomaly_desc = self.check_anomaly(returns)
        results['anomaly'] = {
            'detected': is_anomaly,
            'score': anomaly_score,
            'description': anomaly_desc
        }
        
        # 4. News sentiment (if provided)
        if news_texts:
            results['news_sentiment'] = self.analyze_news_impact(news_texts)
        
        # 5. Combined risk score (weighted average)
        weights = {
            'future': 0.4,
            'pattern': 0.3,
            'anomaly': 0.2,
            'sentiment': 0.1
        }
        
        risk_score = (
            weights['future'] * results['future_failure_prob'] +
            weights['pattern'] * results['complex_pattern_prob'] +
            weights['anomaly'] * (anomaly_score if is_anomaly else 0)
        )
        
        if news_texts and results.get('news_sentiment'):
            sentiment_risk = max(0, -results['news_sentiment']['avg_sentiment'])
            risk_score += weights['sentiment'] * sentiment_risk
        
        results['combined_risk_score'] = risk_score
        
        # 6. Generate recommendation
        results['recommendation'] = self._generate_recommendation(results)
        
        return results
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate actionable recommendation."""
        risk = analysis['combined_risk_score']
        
        if risk > 0.7:
            return ("🚨 CRITICAL RISK: Multiple indicators suggest high failure probability. "
                   "Consider halting strategy or implementing strict stop-losses.")
        elif risk > 0.5:
            return ("⚠️ HIGH RISK: Strategy shows concerning patterns. "
                   "Reduce position size and monitor closely.")
        elif risk > 0.3:
            return ("⚡ MODERATE RISK: Some warning signs detected. "
                   "Proceed with caution and review risk parameters.")
        else:
            return "✓ LOW RISK: Strategy appears stable under current conditions."
    
    def adaptive_update(self, returns: List[float], actual_failure: bool):
        """
        Update models with new data (online learning).
        """
        if len(returns) < 10:
            return
        
        # Prepare data
        features = self.prepare_features(returns)
        X_pattern = torch.tensor([features], dtype=torch.float32)
        y = torch.tensor([[1.0 if actual_failure else 0.0]], dtype=torch.float32)
        
        # Update pattern detector
        loss = self.pattern_learner.update(X_pattern, y)
        
        # Check if full retraining needed
        if self.pattern_learner.should_retrain():
            print("⚠️ Adaptive learning threshold reached. Consider full retraining.")
            self.save_models()
