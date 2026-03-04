from typing import Annotated, Sequence, Literal
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI
from chanana_quant.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# Structured Trading Signal Schema (Phase 1 upgrade)
class TradingSignal(BaseModel):
    """Structured trading signal output with validation."""
    
    # Core decision
    action: Literal["BUY", "SELL", "HOLD"] = Field(
        description="Trading action recommendation"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0 and 1"
    )
    
    # Position sizing
    position_size_pct: float = Field(
        ge=0.0, le=100.0,
        description="Recommended position size as % of portfolio"
    )
    
    # Risk management
    stop_loss_pct: Optional[float] = Field(
        default=None,
        description="Stop loss as % below entry price"
    )
    take_profit_pct: Optional[float] = Field(
        default=None,
        description="Take profit as % above entry price"
    )
    
    # Time horizon
    holding_period_days: Optional[int] = Field(
        default=None,
        description="Expected holding period in days"
    )
    
    # Reasoning
    primary_reason: str = Field(
        description="Main reason for the decision"
    )
    supporting_factors: list[str] = Field(
        default_factory=list,
        description="Additional supporting factors"
    )
    risk_factors: list[str] = Field(
        default_factory=list,
        description="Key risk factors to monitor"
    )
    
    # Metadata
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Signal generation timestamp"
    )
    ticker: str = Field(
        description="Stock ticker symbol"
    )
    analysis_date: str = Field(
        description="Date of analysis (YYYY-MM-DD)"
    )
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        """Ensure action is one of the allowed values."""
        if v not in ["BUY", "SELL", "HOLD"]:
            raise ValueError(f"Action must be BUY, SELL, or HOLD, got {v}")
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v
    
    @field_validator('position_size_pct')
    @classmethod
    def validate_position_size(cls, v):
        """Ensure position size is between 0 and 100."""
        if not 0.0 <= v <= 100.0:
            raise ValueError(f"Position size must be between 0.0 and 100.0, got {v}")
        return v


# Researcher team state
class InvestDebateState(TypedDict):
    bull_history: Annotated[
        str, "Bullish Conversation history"
    ]  # Bullish Conversation history
    bear_history: Annotated[
        str, "Bearish Conversation history"
    ]  # Bullish Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    current_response: Annotated[str, "Latest response"]  # Last response
    judge_decision: Annotated[str, "Final judge decision"]  # Last response
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


# Risk management team state
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[
        str, "Aggressive Agent's Conversation history"
    ]  # Conversation history
    conservative_history: Annotated[
        str, "Conservative Agent's Conversation history"
    ]  # Conversation history
    neutral_history: Annotated[
        str, "Neutral Agent's Conversation history"
    ]  # Conversation history
    history: Annotated[str, "Conversation history"]  # Conversation history
    latest_speaker: Annotated[str, "Analyst that spoke last"]
    current_aggressive_response: Annotated[
        str, "Latest response by the aggressive analyst"
    ]  # Last response
    current_conservative_response: Annotated[
        str, "Latest response by the conservative analyst"
    ]  # Last response
    current_neutral_response: Annotated[
        str, "Latest response by the neutral analyst"
    ]  # Last response
    judge_decision: Annotated[str, "Judge's decision"]
    count: Annotated[int, "Length of the current conversation"]  # Conversation length


class AgentState(MessagesState):
    company_of_interest: Annotated[str, "Company that we are interested in trading"]
    trade_date: Annotated[str, "What date we are trading at"]

    sender: Annotated[str, "Agent that sent this message"]

    # research step
    market_report: Annotated[str, "Report from the Market Analyst"]
    sentiment_report: Annotated[str, "Report from the Social Media Analyst"]
    news_report: Annotated[
        str, "Report from the News Researcher of current world affairs"
    ]
    fundamentals_report: Annotated[str, "Report from the Fundamentals Researcher"]

    # researcher team discussion step
    investment_debate_state: Annotated[
        InvestDebateState, "Current state of the debate on if to invest or not"
    ]
    investment_plan: Annotated[str, "Plan generated by the Analyst"]

    trader_investment_plan: Annotated[str, "Plan generated by the Trader"]

    # risk management team discussion step
    risk_debate_state: Annotated[
        RiskDebateState, "Current state of the debate on evaluating risk"
    ]
    final_trade_decision: Annotated[str, "Final decision made by the Risk Analysts"]
    
    # structured signal (Phase 1 upgrade)
    trading_signal: Annotated[Optional[TradingSignal], "Structured trading signal output"]
