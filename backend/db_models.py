from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    simulations = relationship("DbSimulationResult", back_populates="owner")

class DbSimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    simulation_uuid = Column(String, index=True)
    ticker = Column(String, index=True)
    strategy_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    final_capital = Column(Float)
    total_return_pct = Column(Float)
    max_drawdown_pct = Column(Float)
    falsification_triggered = Column(Boolean, default=False)
    falsification_reason = Column(String, nullable=True)
    
    # Store complex nested data as JSON
    trades_json = Column(JSON)
    equity_curve_json = Column(JSON)
    warnings_json = Column(JSON)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="simulations")
    
    created_at = Column(DateTime, default=datetime.utcnow)
