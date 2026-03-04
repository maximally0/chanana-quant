# Chanana Quant: System Upgrade Plan

**Project Vision:** Chanana Quant — AI-native hedge fund architecture for Indian markets

**Document Purpose:** This upgrade plan provides a precise, code-level roadmap to evolve the current multi-agent trading analysis framework into a production-grade trading research system while preserving its existing LangGraph architecture.

---

## Table of Contents

1. [Current System Analysis](#1-current-system-analysis)
2. [Code-Level Architecture Map](#2-code-level-architecture-map)
3. [Structural Limitations](#3-structural-limitations)
4. [High-Leverage Upgrade Points](#4-high-leverage-upgrade-points)
5. [Indian Market Specialization](#5-indian-market-specialization)
6. [Structured Signal Design](#6-structured-signal-design)
7. [Minimal Backtesting Integration](#7-minimal-backtesting-integration)
8. [Experiment Framework](#8-experiment-framework)
9. [Optional Monitoring Dashboard](#9-optional-monitoring-dashboard)
10. [Incremental Implementation Roadmap](#10-incremental-implementation-roadmap)

---

## 1. Current System Analysis

### 1.1 System Overview

Chanana Quant implements a multi-agent trading analysis framework using LangGraph to orchestrate specialized AI agents. The system simulates a real-world trading firm structure with distinct teams performing analysis, research, trading decisions, and risk management.

### 1.2 Execution Pipeline

The complete execution flow follows this sequence:

```
User Input (ticker, date)
    ↓
[ANALYST TEAM] - Parallel/Sequential Analysis
    ├─ Market Analyst → Technical indicators (MACD, RSI, Bollinger Bands, etc.)
    ├─ Social Media Analyst → Sentiment analysis from news/social data
    ├─ News Analyst → Global news and insider transactions
    └─ Fundamentals Analyst → Financial statements, balance sheet, cash flow
    ↓
[RESEARCH TEAM] - Debate-Based Synthesis
    ├─ Bull Researcher → Argues for investment (uses memory for past lessons)
    ├─ Bear Researcher → Argues against investment (uses memory for past lessons)
    └─ Research Manager → Synthesizes debate into investment plan
    ↓
[TRADER AGENT] - Trading Decision
    └─ Trader → Creates trading plan based on research (uses memory)
    ↓
[RISK MANAGEMENT TEAM] - Risk Assessment Debate
    ├─ Aggressive Analyst → High-risk, high-reward perspective
    ├─ Conservative Analyst → Risk-averse perspective
    ├─ Neutral Analyst → Balanced perspective
    └─ Risk Manager → Final risk assessment
    ↓
[PORTFOLIO MANAGER] - Final Decision
    └─ Portfolio Manager (Risk Judge) → Approves/rejects with BUY/SELL/HOLD
    ↓
Output: Free-form text decision + extracted signal (BUY/SELL/HOLD)
```


### 1.3 LangGraph Orchestration Details

**Graph Construction** (`chanana_quant/graph/setup.py`):
- Uses `StateGraph(AgentState)` to manage state flow
- Nodes represent agents (analysts, researchers, trader, risk managers)
- Tool nodes handle data fetching (market data, news, fundamentals)
- Conditional edges control flow based on tool calls and debate rounds

**State Management** (`chanana_quant/agents/utils/agent_states.py`):
- `AgentState`: Main state container inheriting from `MessagesState`
- `InvestDebateState`: Tracks bull/bear debate history and rounds
- `RiskDebateState`: Tracks three-way risk debate (aggressive/conservative/neutral)
- State flows through graph, accumulating reports at each stage

**Conditional Logic** (`chanana_quant/graph/conditional_logic.py`):
- `should_continue_*`: Determines if analyst needs more tool calls
- `should_continue_debate`: Controls research debate rounds (max_debate_rounds)
- `should_continue_risk_analysis`: Controls risk debate rounds (max_risk_discuss_rounds)

**Key Files Responsible for Each Step:**

1. **Analyst Agents** → `chanana_quant/agents/analysts/*.py`
   - Each analyst uses LLM + tools to generate domain-specific reports
   - Reports stored in state: `market_report`, `sentiment_report`, `news_report`, `fundamentals_report`

2. **Research Debate** → `chanana_quant/agents/researchers/*.py`
   - Bull/Bear researchers debate using past memories (BM25-based retrieval)
   - Research Manager synthesizes into `investment_plan`

3. **Trader Decision** → `chanana_quant/agents/trader/trader.py`
   - Receives investment plan, generates `trader_investment_plan`
   - Uses memory to learn from past mistakes

4. **Risk Debate** → `chanana_quant/agents/risk_mgmt/*.py`
   - Three analysts debate risk from different perspectives
   - Risk Manager produces `final_trade_decision`

5. **Signal Extraction** → `chanana_quant/graph/signal_processing.py`
   - Uses LLM to extract BUY/SELL/HOLD from free-form text
   - Simple prompt-based extraction, no structured output


### 1.4 Data Flow Architecture

**Data Sources** (`chanana_quant/dataflows/`):
- Abstraction layer supports multiple vendors: yfinance, Alpha Vantage
- Routing system with fallback: `interface.py` routes to vendor implementations
- Configuration-driven: category-level and tool-level vendor selection
- Caching: Data stored in `dataflows/data_cache/`

**Tool Execution**:
- Tools defined in `chanana_quant/agents/utils/*_tools.py`
- Tools call `route_to_vendor()` which selects appropriate data source
- LangGraph's `ToolNode` handles tool invocation within agent nodes

**Memory System** (`chanana_quant/agents/utils/memory.py`):
- BM25-based lexical similarity matching (no API calls, offline)
- Each agent (bull, bear, trader, judges) has separate memory
- Stores (situation, recommendation) pairs
- Retrieves top-N similar past situations for context

### 1.5 Current Output Format

**Final State Structure**:
```python
{
    "company_of_interest": "NVDA",
    "trade_date": "2024-05-10",
    "market_report": "...",           # Free-form text
    "sentiment_report": "...",         # Free-form text
    "news_report": "...",              # Free-form text
    "fundamentals_report": "...",      # Free-form text
    "investment_plan": "...",          # Free-form text
    "trader_investment_plan": "...",   # Free-form text
    "final_trade_decision": "...",     # Free-form text with BUY/SELL/HOLD
}
```

**Signal Extraction**:
- LLM parses `final_trade_decision` to extract BUY/SELL/HOLD
- No confidence scores, no structured reasoning
- No quantitative metrics (position size, stop loss, etc.)


---

## 2. Code-Level Architecture Map

### 2.1 Module Breakdown

#### `chanana_quant/graph/` - LangGraph Orchestration Layer
**Purpose**: Manages agent workflow, state transitions, and execution flow

- `trading_graph.py` (Main Entry Point)
  - `ChananaQuantGraph` class: Initializes system, manages LLMs, memories, tools
  - `propagate()`: Executes graph for a ticker/date, returns final state + signal
  - `reflect_and_remember()`: Updates memories based on trading outcomes
  - `process_signal()`: Extracts BUY/SELL/HOLD from text

- `setup.py` (Graph Construction)
  - `GraphSetup.setup_graph()`: Builds LangGraph workflow
  - Connects analyst nodes → research debate → trader → risk debate → end
  - Configures conditional edges for tool calls and debate rounds

- `conditional_logic.py` (Flow Control)
  - Determines when to continue tool calls vs. move to next agent
  - Controls debate round limits
  - Routes between bull/bear researchers and risk analysts

- `propagation.py` (State Initialization)
  - `create_initial_state()`: Sets up empty state with ticker/date
  - `get_graph_args()`: Configures recursion limits and callbacks

- `signal_processing.py` (Signal Extraction)
  - `process_signal()`: LLM-based extraction of BUY/SELL/HOLD
  - Currently simple prompt-based, no structured output

- `reflection.py` (Memory Updates)
  - Reflects on each agent's decisions given actual returns
  - Updates BM25 memory with lessons learned


#### `chanana_quant/agents/` - Agent Implementations
**Purpose**: Individual agent logic and prompts

- `analysts/` - Data Analysis Agents
  - `market_analyst.py`: Technical indicators (SMA, EMA, MACD, RSI, Bollinger, ATR, VWMA)
  - `social_media_analyst.py`: Sentiment analysis from news
  - `news_analyst.py`: Global news, insider transactions
  - `fundamentals_analyst.py`: Financial statements, balance sheet, cash flow
  - Each returns free-form markdown report

- `researchers/` - Investment Debate Agents
  - `bull_researcher.py`: Argues for investment, uses memory
  - `bear_researcher.py`: Argues against investment, uses memory
  - Engage in multi-round debate

- `managers/` - Decision Synthesis Agents
  - `research_manager.py`: Synthesizes bull/bear debate into investment plan
  - `risk_manager.py`: Synthesizes risk debate into final decision

- `trader/` - Trading Decision Agent
  - `trader.py`: Creates trading plan from research, uses memory

- `risk_mgmt/` - Risk Assessment Agents
  - `aggressive_debator.py`: High-risk perspective
  - `conservative_debator.py`: Risk-averse perspective
  - `neutral_debator.py`: Balanced perspective

- `utils/` - Shared Utilities
  - `agent_states.py`: State type definitions
  - `agent_utils.py`: Tool wrapper functions
  - `memory.py`: BM25-based memory system
  - `*_tools.py`: LangChain tool definitions for data fetching


#### `chanana_quant/dataflows/` - Data Acquisition Layer
**Purpose**: Fetch and cache market data from multiple vendors

- `interface.py` (Routing Layer)
  - `route_to_vendor()`: Routes tool calls to configured vendor
  - Supports fallback: tries primary vendor, falls back to alternatives
  - Category-based and tool-based configuration

- `config.py` (Configuration Management)
  - Global config singleton for data vendor selection
  - Integrates with `default_config.py`

- `y_finance.py` (Yahoo Finance Implementation)
  - `get_YFin_data_online()`: OHLCV data
  - `get_stock_stats_indicators_window()`: Technical indicators via stockstats
  - `get_fundamentals()`, `get_balance_sheet()`, etc.: Fundamental data

- `alpha_vantage*.py` (Alpha Vantage Implementation)
  - Alternative data source requiring API key
  - Similar interface to yfinance
  - Rate limiting and error handling

- `stockstats_utils.py` (Technical Indicators)
  - Wrapper around stockstats library
  - Calculates indicators from OHLCV data

- `utils.py` (Data Processing)
  - Date handling, data formatting utilities

#### `chanana_quant/llm_clients/` - LLM Provider Abstraction
**Purpose**: Support multiple LLM providers with unified interface

- `factory.py`: Creates LLM clients based on provider
- `base_client.py`: Abstract base class
- `openai_client.py`: OpenAI, xAI, Ollama, OpenRouter
- `anthropic_client.py`: Anthropic Claude
- `google_client.py`: Google Gemini
- `validators.py`: Input validation


#### `cli/` - Command-Line Interface
**Purpose**: User interaction and result visualization

- `main.py` (Main CLI Application)
  - Interactive questionnaire for user selections
  - Real-time display of agent progress using Rich library
  - Message buffer tracks agent status, reports, tool calls
  - Saves reports to disk in organized folder structure
  - Displays complete analysis after execution

- `config.py`: CLI-specific configuration
- `models.py`: Pydantic models for analyst types
- `utils.py`: Helper functions for user input
- `stats_handler.py`: Callback handler for LLM/tool statistics
- `announcements.py`: Fetches system announcements

#### `chanana_quant/default_config.py` - System Configuration
**Purpose**: Central configuration for all system parameters

```python
DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",      # Complex reasoning
    "quick_think_llm": "gpt-5-mini",  # Quick tasks
    "max_debate_rounds": 1,            # Research debate rounds
    "max_risk_discuss_rounds": 1,      # Risk debate rounds
    "data_vendors": {...},             # Data source configuration
    "tool_vendors": {...},             # Tool-specific overrides
}
```

### 2.2 Key Integration Points

1. **Entry Point**: `main.py` or `cli/main.py`
2. **Graph Execution**: `ChananaQuantGraph.propagate(ticker, date)`
3. **State Flow**: Through LangGraph nodes, accumulated in `AgentState`
4. **Data Fetching**: Tools → `route_to_vendor()` → vendor implementation
5. **Memory**: Each agent queries BM25 memory for similar past situations
6. **Output**: Final state dict + extracted signal string


---

## 3. Structural Limitations

### 3.1 Unstructured Decision Output

**Problem**: All agent outputs are free-form text with no structured schema.

**Impact**:
- Cannot programmatically extract confidence scores, position sizes, or risk metrics
- Signal extraction relies on LLM parsing, which is unreliable
- No quantitative metrics for backtesting or portfolio management
- Difficult to aggregate signals across multiple stocks
- Cannot build systematic trading strategies

**Evidence**:
- `final_trade_decision` is a text paragraph
- `process_signal()` uses LLM to extract BUY/SELL/HOLD
- No confidence, no position size, no stop loss, no target price

### 3.2 Absence of Backtesting Infrastructure

**Problem**: No way to test agent decisions on historical data.

**Impact**:
- Cannot validate if the system actually generates alpha
- No performance metrics (Sharpe ratio, CAGR, max drawdown)
- Cannot compare different configurations or LLM models
- No way to optimize debate rounds, analyst selection, or prompts
- Cannot demonstrate system value to stakeholders

**Evidence**:
- No backtesting module in codebase
- `reflect_and_remember()` exists but requires manual return input
- No historical simulation capability


### 3.3 Lack of Indian Market Specialization

**Problem**: System is generic, not optimized for Indian markets.

**Impact**:
- Uses US ticker format (NVDA, SPY) without NSE/BSE support
- No NIFTY50 or sectoral index context
- Missing India-specific macro indicators (India VIX, FII/DII flows)
- No awareness of Indian market hours, holidays, or regulations
- Cannot analyze Indian stocks effectively

**Evidence**:
- No NSE ticker normalization (e.g., RELIANCE.NS)
- No Indian market data sources
- No India-specific prompts or context
- README mentions "Indian markets" but implementation is US-focused

### 3.4 Missing Macro Context

**Problem**: Agents analyze stocks in isolation without macro awareness.

**Impact**:
- Cannot factor in market regime (bull/bear/sideways)
- No volatility regime detection (VIX levels)
- Missing sector rotation signals
- No correlation with broader indices
- Decisions may contradict overall market conditions

**Evidence**:
- No macro data fetching tools
- Agents only see company-specific data
- No market regime classification


### 3.5 Limited Portfolio Management Logic

**Problem**: System analyzes one stock at a time with no portfolio context.

**Impact**:
- Cannot manage position sizing across multiple stocks
- No portfolio-level risk management
- Cannot rebalance or optimize allocations
- No correlation analysis between holdings
- Cannot implement diversification strategies

**Evidence**:
- Single-stock analysis only
- No portfolio state tracking
- Risk manager evaluates individual trades, not portfolio impact

### 3.6 No Experiment Tracking

**Problem**: No systematic way to track experiments and compare results.

**Impact**:
- Cannot compare different LLM models or configurations
- No A/B testing capability
- Difficult to reproduce results
- Cannot track performance over time
- No audit trail for decisions

**Evidence**:
- Results saved to `eval_results/` but no structured tracking
- No experiment metadata (config, timestamp, performance)
- No comparison tools

### 3.7 Lack of Real-Time Monitoring

**Problem**: No dashboard or monitoring interface for production use.

**Impact**:
- Cannot monitor system health in production
- No visibility into agent performance
- Difficult to debug issues
- Cannot track signal quality over time
- No alerting for anomalies

**Evidence**:
- CLI provides real-time display during execution only
- No persistent monitoring or visualization
- No web interface


---

## 4. High-Leverage Upgrade Points

### 4.1 Structured Signal Extraction

**Target**: `chanana_quant/graph/signal_processing.py`

**Current State**:
```python
def process_signal(self, full_signal: str) -> str:
    # LLM extracts BUY/SELL/HOLD from text
    return self.quick_thinking_llm.invoke(messages).content
```

**Upgrade**:
- Replace with structured output using LangChain's `with_structured_output()`
- Define Pydantic schema for trading signals
- Extract confidence, position size, reasoning, risk metrics

**Integration**:
- Modify `ChananaQuantGraph.process_signal()` to return structured dict
- Update `trader.py` and `risk_manager.py` to output structured format
- Preserve backward compatibility by keeping text in state

**Files to Modify**:
- `chanana_quant/graph/signal_processing.py` (main logic)
- `chanana_quant/agents/trader/trader.py` (structured output)
- `chanana_quant/agents/managers/risk_manager.py` (structured output)
- `chanana_quant/agents/utils/agent_states.py` (add signal schema)


### 4.2 Indian Market Data Integration

**Target**: `chanana_quant/dataflows/`

**Current State**:
- yfinance and Alpha Vantage support US markets
- No NSE/BSE ticker normalization

**Upgrade**:
- Add NSE ticker normalization (RELIANCE → RELIANCE.NS)
- Create `nse_data.py` for NSE-specific data sources
- Add Indian market hours and holiday calendar
- Integrate NSE India API or similar

**Integration**:
- Add to `interface.py` routing system
- Create new vendor option: "nse_india"
- Update `core_stock_tools.py` to handle .NS/.BO suffixes

**Files to Create**:
- `chanana_quant/dataflows/nse_data.py` (NSE data fetching)
- `chanana_quant/dataflows/indian_market_utils.py` (ticker normalization, holidays)

**Files to Modify**:
- `chanana_quant/dataflows/interface.py` (add NSE vendor)
- `chanana_quant/dataflows/config.py` (NSE configuration)
- `chanana_quant/default_config.py` (add NSE as vendor option)


### 4.3 Macro Context Integration

**Target**: `chanana_quant/agents/analysts/` and `chanana_quant/dataflows/`

**Current State**:
- Analysts only see company-specific data
- No market regime awareness

**Upgrade**:
- Create `macro_analyst.py` for market-level analysis
- Add macro data tools (index data, VIX, sector performance)
- Inject macro context into existing analysts

**Integration**:
- Add macro analyst as optional node in graph setup
- Macro report flows to all downstream agents
- Update analyst prompts to consider macro context

**Files to Create**:
- `chanana_quant/agents/analysts/macro_analyst.py` (new analyst)
- `chanana_quant/agents/utils/macro_data_tools.py` (macro data tools)
- `chanana_quant/dataflows/macro_data.py` (macro data fetching)

**Files to Modify**:
- `chanana_quant/graph/setup.py` (add macro analyst node)
- `chanana_quant/agents/utils/agent_states.py` (add macro_report field)
- `chanana_quant/agents/researchers/*.py` (use macro context in prompts)
- `chanana_quant/agents/trader/trader.py` (use macro context)


### 4.4 Backtesting Engine

**Target**: New module `chanana_quant/backtesting/`

**Current State**:
- No backtesting capability
- Manual reflection with `reflect_and_remember()`

**Upgrade**:
- Create backtesting engine that runs graph on historical dates
- Simulate trades and track portfolio value
- Calculate performance metrics
- Integrate with existing reflection system

**Integration**:
- Reuse existing `ChananaQuantGraph.propagate()` for each date
- Track simulated portfolio state
- Call `reflect_and_remember()` after each trade
- Generate performance report

**Files to Create**:
- `chanana_quant/backtesting/engine.py` (main backtesting logic)
- `chanana_quant/backtesting/portfolio.py` (portfolio state tracking)
- `chanana_quant/backtesting/metrics.py` (performance calculations)
- `chanana_quant/backtesting/simulator.py` (trade execution simulation)

**Files to Modify**:
- `chanana_quant/graph/trading_graph.py` (add backtesting mode flag)
- `cli/main.py` (add backtesting command)


### 4.5 Experiment Tracking System

**Target**: New module `chanana_quant/experiments/`

**Current State**:
- Results saved to `eval_results/` with no metadata
- No experiment comparison

**Upgrade**:
- Create experiment tracking system with metadata
- Store configuration, results, and metrics
- Enable comparison across experiments

**Integration**:
- Wrap `ChananaQuantGraph.propagate()` with experiment context
- Log all configuration and results
- Provide comparison utilities

**Files to Create**:
- `chanana_quant/experiments/tracker.py` (experiment logging)
- `chanana_quant/experiments/storage.py` (result storage)
- `chanana_quant/experiments/comparison.py` (experiment comparison)
- `chanana_quant/experiments/config.py` (experiment configuration)

**Files to Modify**:
- `chanana_quant/graph/trading_graph.py` (add experiment tracking hooks)
- `cli/main.py` (add experiment ID to runs)


### 4.6 Portfolio Management Layer

**Target**: New module `chanana_quant/portfolio/`

**Current State**:
- Single-stock analysis only
- No portfolio context

**Upgrade**:
- Create portfolio manager that tracks multiple positions
- Implement position sizing logic
- Add portfolio-level risk management

**Integration**:
- Wrap multiple `propagate()` calls for different stocks
- Aggregate signals into portfolio decisions
- Apply portfolio constraints (max position size, sector limits)

**Files to Create**:
- `chanana_quant/portfolio/manager.py` (portfolio management)
- `chanana_quant/portfolio/position_sizing.py` (position sizing logic)
- `chanana_quant/portfolio/risk_controls.py` (portfolio risk limits)
- `chanana_quant/portfolio/rebalancing.py` (rebalancing logic)

**Files to Modify**:
- `chanana_quant/agents/managers/risk_manager.py` (add portfolio context)
- `chanana_quant/graph/trading_graph.py` (add portfolio mode)

---

## 5. Indian Market Specialization

### 5.1 NSE/BSE Ticker Normalization

**Implementation Location**: `chanana_quant/dataflows/indian_market_utils.py`

**Functionality**:
```python
def normalize_indian_ticker(symbol: str) -> str:
    """Convert Indian ticker to yfinance format.
    
    Examples:
        RELIANCE → RELIANCE.NS
        TCS → TCS.NS
        INFY → INFY.NS
        HDFCBANK → HDFCBANK.NS
    """
    if not symbol.endswith(('.NS', '.BO')):
        return f"{symbol}.NS"  # Default to NSE
    return symbol

def is_indian_ticker(symbol: str) -> bool:
    """Check if ticker is Indian market."""
    return symbol.endswith(('.NS', '.BO'))
```

**Integration Points**:
- `chanana_quant/dataflows/interface.py`: Auto-normalize before routing
- `chanana_quant/agents/utils/core_stock_tools.py`: Normalize in tool calls
- `cli/main.py`: Suggest .NS suffix in ticker input


### 5.2 NIFTY50 and Sectoral Context

**Implementation Location**: `chanana_quant/agents/analysts/macro_analyst.py`

**Functionality**:
- Fetch NIFTY50 index data (^NSEI)
- Fetch sectoral indices (NIFTY Bank, IT, Pharma, Auto, etc.)
- Calculate relative strength vs. index
- Identify sector rotation signals

**Macro Context Structure**:
```python
{
    "nifty50_trend": "bullish/bearish/sideways",
    "nifty50_change_1d": -0.5,
    "nifty50_change_1w": 2.3,
    "sector_performance": {
        "NIFTY Bank": 1.2,
        "NIFTY IT": -0.8,
        "NIFTY Pharma": 0.5,
    },
    "stock_vs_nifty": "outperforming/underperforming",
    "sector_momentum": "strong/weak/neutral"
}
```

**Integration**:
- Add macro analyst as first node in graph (before other analysts)
- Inject macro context into all analyst prompts
- Update researcher prompts to consider market regime

**Prompt Enhancement Example**:
```python
# In bull_researcher.py
prompt = f"""You are a Bull Analyst...

MACRO CONTEXT:
- NIFTY50 Trend: {macro_report['nifty50_trend']}
- Sector Performance: {macro_report['sector_performance']}
- Stock vs Index: {macro_report['stock_vs_nifty']}

Consider the broader market context when making your argument...
"""
```


### 5.3 India VIX Integration

**Implementation Location**: `chanana_quant/dataflows/macro_data.py`

**Functionality**:
```python
def get_india_vix(start_date: str, end_date: str) -> dict:
    """Fetch India VIX data and classify volatility regime.
    
    Returns:
        {
            "current_vix": 15.2,
            "vix_percentile": 45,  # Historical percentile
            "regime": "low/medium/high",
            "trend": "rising/falling/stable"
        }
    """
    # Fetch ^INDIAVIX from yfinance
    # Calculate percentile vs. historical range
    # Classify regime: <15 = low, 15-25 = medium, >25 = high
```

**Integration**:
- Add to macro analyst report
- Adjust risk manager's risk tolerance based on VIX
- Update position sizing based on volatility regime

**Risk Manager Prompt Enhancement**:
```python
# In risk_manager.py
prompt = f"""As the Risk Management Judge...

VOLATILITY CONTEXT:
- India VIX: {macro_report['india_vix']['current_vix']}
- Volatility Regime: {macro_report['india_vix']['regime']}
- VIX Trend: {macro_report['india_vix']['trend']}

In high volatility regimes, recommend smaller position sizes and tighter stop losses...
"""
```


### 5.4 FII/DII Flow Data

**Implementation Location**: `chanana_quant/dataflows/indian_market_data.py`

**Functionality**:
- Fetch Foreign Institutional Investor (FII) flow data
- Fetch Domestic Institutional Investor (DII) flow data
- Analyze net buying/selling pressure

**Data Structure**:
```python
{
    "fii_net_flow": 1250.5,  # Crores
    "dii_net_flow": -850.2,
    "fii_trend": "buying/selling",
    "dii_trend": "buying/selling",
    "institutional_sentiment": "bullish/bearish/neutral"
}
```

**Data Sources**:
- NSE India website (requires scraping or API)
- MoneyControl API
- Alternative: Use proxy indicators from index flows

**Integration**:
- Add to macro analyst report
- Consider in sentiment analyst's analysis
- Factor into research manager's decision

### 5.5 Indian Market Hours and Holidays

**Implementation Location**: `chanana_quant/dataflows/indian_market_utils.py`

**Functionality**:
```python
def is_indian_market_open(date: datetime) -> bool:
    """Check if Indian market is open on given date."""
    # Check if weekday (Mon-Fri)
    # Check against Indian market holiday calendar
    # Check market hours (9:15 AM - 3:30 PM IST)

def get_next_trading_day(date: datetime) -> datetime:
    """Get next Indian trading day."""
    # Skip weekends and holidays

INDIAN_MARKET_HOLIDAYS_2024 = [
    "2024-01-26",  # Republic Day
    "2024-03-08",  # Maha Shivaratri
    "2024-03-25",  # Holi
    # ... complete list
]
```

**Integration**:
- Validate trade dates in CLI
- Skip holidays in backtesting
- Adjust data fetching logic


### 5.6 Sector Classification for Indian Stocks

**Implementation Location**: `chanana_quant/dataflows/indian_market_utils.py`

**Functionality**:
```python
INDIAN_SECTOR_MAPPING = {
    "RELIANCE": "Energy",
    "TCS": "IT",
    "INFY": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "BHARTIARTL": "Telecom",
    # ... complete mapping
}

def get_indian_sector(symbol: str) -> str:
    """Get sector for Indian stock."""
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    return INDIAN_SECTOR_MAPPING.get(base_symbol, "Unknown")

def get_sector_peers(symbol: str, n: int = 5) -> list:
    """Get peer stocks in same sector."""
    sector = get_indian_sector(symbol)
    peers = [s for s, sec in INDIAN_SECTOR_MAPPING.items() if sec == sector]
    return peers[:n]
```

**Integration**:
- Add sector context to fundamentals analyst
- Enable sector rotation analysis in macro analyst
- Support sector-relative performance metrics

---

## 6. Structured Signal Design

### 6.1 Signal Schema Definition

**Implementation Location**: `chanana_quant/agents/utils/agent_states.py`

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TradingSignal(BaseModel):
    """Structured trading signal output."""
    
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
```


### 6.2 Structured Output Implementation

**Implementation Location**: `chanana_quant/graph/signal_processing.py`

**Updated Signal Processor**:
```python
from langchain_core.output_parsers import PydanticOutputParser
from chanana_quant.agents.utils.agent_states import TradingSignal

class SignalProcessor:
    def __init__(self, quick_thinking_llm):
        self.quick_thinking_llm = quick_thinking_llm
        self.parser = PydanticOutputParser(pydantic_object=TradingSignal)
    
    def process_signal(self, full_signal: str, ticker: str, analysis_date: str) -> TradingSignal:
        """Extract structured signal from text decision."""
        
        prompt = f"""Extract a structured trading signal from the following decision.

Decision Text:
{full_signal}

{self.parser.get_format_instructions()}

Ensure all fields are filled with reasonable values based on the decision text.
"""
        
        # Use structured output
        structured_llm = self.quick_thinking_llm.with_structured_output(TradingSignal)
        signal = structured_llm.invoke(prompt)
        
        # Set metadata
        signal.ticker = ticker
        signal.analysis_date = analysis_date
        
        return signal
```

**Alternative: Direct Structured Output from Risk Manager**:
```python
# In risk_manager.py
def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:
        # ... existing logic ...
        
        # Use structured output directly
        structured_llm = llm.with_structured_output(TradingSignal)
        signal = structured_llm.invoke(prompt)
        
        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": signal.model_dump_json(),  # Store as JSON
            "structured_signal": signal  # Store structured object
        }
```


### 6.3 Integration with Existing Pipeline

**Files to Modify**:

1. **`chanana_quant/agents/utils/agent_states.py`**
   - Add `TradingSignal` Pydantic model
   - Add `structured_signal: Optional[TradingSignal]` to `AgentState`

2. **`chanana_quant/agents/managers/risk_manager.py`**
   - Update prompt to request structured output
   - Use `with_structured_output(TradingSignal)`
   - Store both text and structured signal in state

3. **`chanana_quant/graph/signal_processing.py`**
   - Update `process_signal()` to return `TradingSignal` object
   - Add fallback to LLM extraction if structured output fails

4. **`chanana_quant/graph/trading_graph.py`**
   - Update `propagate()` to return structured signal
   - Maintain backward compatibility with text signal

**Backward Compatibility**:
```python
# In trading_graph.py
def propagate(self, company_name, trade_date):
    # ... existing logic ...
    
    # Extract structured signal
    structured_signal = self.process_signal(
        final_state["final_trade_decision"],
        company_name,
        trade_date
    )
    
    # Return both formats
    return final_state, {
        "text": structured_signal.action,  # Backward compatible
        "structured": structured_signal     # New format
    }
```


### 6.4 Signal Validation and Quality Checks

**Implementation Location**: `chanana_quant/graph/signal_processing.py`

**Validation Logic**:
```python
class SignalProcessor:
    def validate_signal(self, signal: TradingSignal) -> tuple[bool, list[str]]:
        """Validate signal for consistency and reasonableness.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Check confidence matches action
        if signal.action == "HOLD" and signal.confidence > 0.7:
            errors.append("High confidence with HOLD action is unusual")
        
        # Check position size is reasonable
        if signal.action == "BUY" and signal.position_size_pct == 0:
            errors.append("BUY action with 0% position size")
        if signal.action == "HOLD" and signal.position_size_pct > 0:
            errors.append("HOLD action should have 0% position size")
        
        # Check stop loss is reasonable
        if signal.stop_loss_pct and signal.stop_loss_pct > 20:
            errors.append("Stop loss >20% is very wide")
        
        # Check take profit is reasonable
        if signal.take_profit_pct and signal.take_profit_pct < signal.stop_loss_pct:
            errors.append("Take profit should be larger than stop loss")
        
        return len(errors) == 0, errors
    
    def process_signal(self, full_signal: str, ticker: str, analysis_date: str) -> TradingSignal:
        signal = self._extract_signal(full_signal, ticker, analysis_date)
        
        # Validate
        is_valid, errors = self.validate_signal(signal)
        if not is_valid:
            # Log warnings but don't fail
            print(f"Signal validation warnings: {errors}")
        
        return signal
```

---

## 7. Minimal Backtesting Integration

### 7.1 Backtesting Architecture

**Design Principle**: Reuse existing pipeline, don't duplicate logic.

**Approach**:
1. Run `ChananaQuantGraph.propagate()` for each historical date
2. Simulate trade execution based on signals
3. Track portfolio value over time
4. Calculate performance metrics
5. Integrate with reflection system

**Module Structure**:
```
chanana_quant/backtesting/
├── engine.py          # Main backtesting orchestration
├── portfolio.py       # Portfolio state tracking
├── simulator.py       # Trade execution simulation
├── metrics.py         # Performance calculations
└── config.py          # Backtesting configuration
```

### 7.2 Backtesting Engine Implementation

**File**: `chanana_quant/backtesting/engine.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict
from chanana_quant.graph.trading_graph import ChananaQuantGraph
from .portfolio import Portfolio
from .simulator import TradeSimulator
from .metrics import PerformanceMetrics

class BacktestEngine:
    """Runs agent decisions on historical data."""
    
    def __init__(self, graph: ChananaQuantGraph, initial_capital: float = 100000):
        self.graph = graph
        self.portfolio = Portfolio(initial_capital)
        self.simulator = TradeSimulator()
        self.metrics = PerformanceMetrics()
        self.results = []
    
    def run(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        rebalance_frequency: str = "daily"
    ) -> Dict:
        """Run backtest over date range.
        
        Args:
            ticker: Stock ticker to trade
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rebalance_frequency: How often to run analysis (daily/weekly)
        
        Returns:
            Backtest results with metrics
        """
        dates = self._generate_trading_dates(start_date, end_date, rebalance_frequency)
        
        for date in dates:
            # Run agent analysis
            final_state, signal = self.graph.propagate(ticker, date)
            
            # Simulate trade execution
            trade = self.simulator.execute_signal(
                signal["structured"],
                self.portfolio,
                date
            )
            
            # Update portfolio
            if trade:
                self.portfolio.add_trade(trade)
            
            # Update portfolio value
            self.portfolio.update_value(date)
            
            # Store result
            self.results.append({
                "date": date,
                "signal": signal,
                "trade": trade,
                "portfolio_value": self.portfolio.total_value,
                "state": final_state
            })
            
            # Reflect on trade (if position closed)
            if trade and trade.is_closed:
                returns = trade.pnl_pct
                self.graph.reflect_and_remember(returns)
        
        # Calculate final metrics
        metrics = self.metrics.calculate(self.results, self.portfolio)
        
        return {
            "results": self.results,
            "metrics": metrics,
            "portfolio": self.portfolio.to_dict()
        }
```


### 7.3 Portfolio State Tracking

**File**: `chanana_quant/backtesting/portfolio.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Position:
    """Represents a stock position."""
    ticker: str
    quantity: int
    entry_price: float
    entry_date: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.entry_price
    
    def current_value(self, current_price: float) -> float:
        return self.quantity * current_price
    
    def pnl(self, current_price: float) -> float:
        return self.current_value(current_price) - self.cost_basis
    
    def pnl_pct(self, current_price: float) -> float:
        return (self.pnl(current_price) / self.cost_basis) * 100

class Portfolio:
    """Tracks portfolio state during backtesting."""
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.trades: List[Dict] = []
        self.value_history: List[Dict] = []
    
    @property
    def total_value(self) -> float:
        """Current portfolio value (cash + positions)."""
        positions_value = sum(
            pos.current_value(self._get_current_price(pos.ticker))
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def buy(self, ticker: str, quantity: int, price: float, date: str, **kwargs):
        """Execute buy order."""
        cost = quantity * price
        if cost > self.cash:
            # Insufficient funds, adjust quantity
            quantity = int(self.cash / price)
            cost = quantity * price
        
        if quantity > 0:
            self.cash -= cost
            self.positions[ticker] = Position(
                ticker=ticker,
                quantity=quantity,
                entry_price=price,
                entry_date=date,
                **kwargs
            )
            self.trades.append({
                "date": date,
                "action": "BUY",
                "ticker": ticker,
                "quantity": quantity,
                "price": price,
                "cost": cost
            })
    
    def sell(self, ticker: str, price: float, date: str):
        """Execute sell order."""
        if ticker not in self.positions:
            return
        
        position = self.positions.pop(ticker)
        proceeds = position.quantity * price
        self.cash += proceeds
        
        position.exit_price = price
        position.exit_date = date
        self.closed_positions.append(position)
        
        self.trades.append({
            "date": date,
            "action": "SELL",
            "ticker": ticker,
            "quantity": position.quantity,
            "price": price,
            "proceeds": proceeds,
            "pnl": position.pnl(price),
            "pnl_pct": position.pnl_pct(price)
        })
    
    def update_value(self, date: str):
        """Update portfolio value for given date."""
        self.value_history.append({
            "date": date,
            "total_value": self.total_value,
            "cash": self.cash,
            "positions_value": self.total_value - self.cash
        })
```


### 7.4 Trade Execution Simulator

**File**: `chanana_quant/backtesting/simulator.py`

```python
from chanana_quant.agents.utils.agent_states import TradingSignal
from .portfolio import Portfolio
import yfinance as yf

class TradeSimulator:
    """Simulates trade execution based on signals."""
    
    def execute_signal(
        self,
        signal: TradingSignal,
        portfolio: Portfolio,
        date: str
    ) -> Optional[Dict]:
        """Execute trade based on signal.
        
        Args:
            signal: Structured trading signal
            portfolio: Current portfolio state
            date: Execution date
        
        Returns:
            Trade details or None if no trade
        """
        # Get execution price (use next day's open)
        execution_price = self._get_execution_price(signal.ticker, date)
        if not execution_price:
            return None
        
        if signal.action == "BUY":
            # Calculate position size
            position_value = portfolio.total_value * (signal.position_size_pct / 100)
            quantity = int(position_value / execution_price)
            
            if quantity > 0:
                portfolio.buy(
                    ticker=signal.ticker,
                    quantity=quantity,
                    price=execution_price,
                    date=date,
                    stop_loss=signal.stop_loss_pct,
                    take_profit=signal.take_profit_pct
                )
                return {"action": "BUY", "quantity": quantity, "price": execution_price}
        
        elif signal.action == "SELL":
            if signal.ticker in portfolio.positions:
                portfolio.sell(
                    ticker=signal.ticker,
                    price=execution_price,
                    date=date
                )
                return {"action": "SELL", "price": execution_price}
        
        elif signal.action == "HOLD":
            # Check stop loss / take profit
            if signal.ticker in portfolio.positions:
                position = portfolio.positions[signal.ticker]
                current_pnl_pct = position.pnl_pct(execution_price)
                
                # Check stop loss
                if position.stop_loss and current_pnl_pct <= -position.stop_loss:
                    portfolio.sell(signal.ticker, execution_price, date)
                    return {"action": "STOP_LOSS", "price": execution_price}
                
                # Check take profit
                if position.take_profit and current_pnl_pct >= position.take_profit:
                    portfolio.sell(signal.ticker, execution_price, date)
                    return {"action": "TAKE_PROFIT", "price": execution_price}
        
        return None
    
    def _get_execution_price(self, ticker: str, date: str) -> Optional[float]:
        """Get execution price (next day's open)."""
        try:
            # Fetch next day's data
            next_date = self._get_next_trading_day(date)
            data = yf.download(ticker, start=next_date, end=next_date, progress=False)
            if not data.empty:
                return data['Open'].iloc[0]
        except:
            pass
        return None
```


### 7.5 Performance Metrics Calculation

**File**: `chanana_quant/backtesting/metrics.py`

```python
import numpy as np
from typing import List, Dict

class PerformanceMetrics:
    """Calculate backtesting performance metrics."""
    
    def calculate(self, results: List[Dict], portfolio) -> Dict:
        """Calculate comprehensive performance metrics."""
        
        # Extract portfolio values
        values = [r["portfolio_value"] for r in results]
        dates = [r["date"] for r in results]
        
        # Calculate returns
        returns = np.diff(values) / values[:-1]
        
        # Total return
        total_return = (values[-1] - portfolio.initial_capital) / portfolio.initial_capital
        
        # CAGR (annualized return)
        days = (pd.to_datetime(dates[-1]) - pd.to_datetime(dates[0])).days
        years = days / 365.25
        cagr = (values[-1] / portfolio.initial_capital) ** (1 / years) - 1 if years > 0 else 0
        
        # Sharpe Ratio (assuming 252 trading days, 5% risk-free rate)
        risk_free_rate = 0.05
        excess_returns = returns - (risk_free_rate / 252)
        sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(returns) if len(returns) > 0 else 0
        
        # Maximum Drawdown
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Win Rate
        closed_trades = [t for t in portfolio.trades if t["action"] == "SELL"]
        winning_trades = [t for t in closed_trades if t.get("pnl", 0) > 0]
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        # Average Win/Loss
        wins = [t["pnl_pct"] for t in closed_trades if t.get("pnl", 0) > 0]
        losses = [t["pnl_pct"] for t in closed_trades if t.get("pnl", 0) < 0]
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        
        # Profit Factor
        total_wins = sum([t["pnl"] for t in closed_trades if t.get("pnl", 0) > 0])
        total_losses = abs(sum([t["pnl"] for t in closed_trades if t.get("pnl", 0) < 0]))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            "total_return": total_return,
            "cagr": cagr,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "avg_win_pct": avg_win,
            "avg_loss_pct": avg_loss,
            "profit_factor": profit_factor,
            "total_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(closed_trades) - len(winning_trades),
            "final_value": values[-1],
            "initial_capital": portfolio.initial_capital
        }
```


### 7.6 CLI Integration

**File**: `cli/main.py`

**Add Backtesting Command**:
```python
@app.command()
def backtest(
    ticker: str = typer.Option(..., help="Stock ticker to backtest"),
    start_date: str = typer.Option(..., help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., help="End date (YYYY-MM-DD)"),
    initial_capital: float = typer.Option(100000, help="Initial capital"),
    frequency: str = typer.Option("daily", help="Rebalance frequency (daily/weekly)")
):
    """Run backtest on historical data."""
    
    # Get user selections (LLM, analysts, etc.)
    selections = get_backtest_selections()
    
    # Create config
    config = DEFAULT_CONFIG.copy()
    config.update(selections)
    
    # Initialize graph
    graph = ChananaQuantGraph(
        selected_analysts=selections["analysts"],
        config=config,
        debug=False
    )
    
    # Create backtesting engine
    from chanana_quant.backtesting.engine import BacktestEngine
    engine = BacktestEngine(graph, initial_capital)
    
    # Run backtest
    console.print(f"[cyan]Running backtest for {ticker}...[/cyan]")
    results = engine.run(ticker, start_date, end_date, frequency)
    
    # Display results
    display_backtest_results(results)
    
    # Save results
    save_backtest_results(results, ticker, start_date, end_date)
```

**Display Results**:
```python
def display_backtest_results(results: Dict):
    """Display backtest metrics in formatted table."""
    metrics = results["metrics"]
    
    table = Table(title="Backtest Performance Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Return", f"{metrics['total_return']:.2%}")
    table.add_row("CAGR", f"{metrics['cagr']:.2%}")
    table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    table.add_row("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
    table.add_row("Win Rate", f"{metrics['win_rate']:.2%}")
    table.add_row("Profit Factor", f"{metrics['profit_factor']:.2f}")
    table.add_row("Total Trades", str(metrics['total_trades']))
    
    console.print(table)
```

---

## 8. Experiment Framework

### 8.1 Experiment Configuration

**File**: `chanana_quant/experiments/config.py`

```python
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
import json

@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    
    # Experiment metadata
    experiment_id: str
    name: str
    description: str
    created_at: str
    
    # System configuration
    llm_provider: str
    deep_think_llm: str
    quick_think_llm: str
    max_debate_rounds: int
    max_risk_discuss_rounds: int
    
    # Analyst selection
    selected_analysts: List[str]
    
    # Data configuration
    data_vendors: Dict[str, str]
    
    # Backtesting parameters (if applicable)
    ticker: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: Optional[float] = None
    
    # Custom parameters
    custom_params: Dict = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)
    
    @classmethod
    def generate_id(cls) -> str:
        """Generate unique experiment ID."""
        return f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
```


### 8.2 Experiment Tracker

**File**: `chanana_quant/experiments/tracker.py`

```python
from pathlib import Path
import json
from typing import Dict, List, Optional
from .config import ExperimentConfig

class ExperimentTracker:
    """Tracks experiments and their results."""
    
    def __init__(self, experiments_dir: str = "./experiments"):
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
    
    def create_experiment(self, config: ExperimentConfig) -> str:
        """Create new experiment and return ID."""
        exp_dir = self.experiments_dir / config.experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save config
        config_path = exp_dir / "config.json"
        config_path.write_text(config.to_json())
        
        return config.experiment_id
    
    def log_result(
        self,
        experiment_id: str,
        result_type: str,
        data: Dict
    ):
        """Log experiment result."""
        exp_dir = self.experiments_dir / experiment_id
        
        # Append to results file
        results_path = exp_dir / f"{result_type}.jsonl"
        with results_path.open("a") as f:
            f.write(json.dumps(data) + "\n")
    
    def log_metrics(self, experiment_id: str, metrics: Dict):
        """Log performance metrics."""
        exp_dir = self.experiments_dir / experiment_id
        metrics_path = exp_dir / "metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2))
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """Load experiment configuration."""
        config_path = self.experiments_dir / experiment_id / "config.json"
        if config_path.exists():
            data = json.loads(config_path.read_text())
            return ExperimentConfig.from_dict(data)
        return None
    
    def list_experiments(self) -> List[ExperimentConfig]:
        """List all experiments."""
        experiments = []
        for exp_dir in self.experiments_dir.iterdir():
            if exp_dir.is_dir():
                config = self.get_experiment(exp_dir.name)
                if config:
                    experiments.append(config)
        return sorted(experiments, key=lambda x: x.created_at, reverse=True)
    
    def get_results(self, experiment_id: str, result_type: str = "signals") -> List[Dict]:
        """Load experiment results."""
        results_path = self.experiments_dir / experiment_id / f"{result_type}.jsonl"
        if not results_path.exists():
            return []
        
        results = []
        with results_path.open("r") as f:
            for line in f:
                results.append(json.loads(line))
        return results
```


### 8.3 Experiment Comparison

**File**: `chanana_quant/experiments/comparison.py`

```python
import pandas as pd
from typing import List, Dict
from .tracker import ExperimentTracker

class ExperimentComparison:
    """Compare multiple experiments."""
    
    def __init__(self, tracker: ExperimentTracker):
        self.tracker = tracker
    
    def compare_metrics(self, experiment_ids: List[str]) -> pd.DataFrame:
        """Compare metrics across experiments."""
        data = []
        
        for exp_id in experiment_ids:
            config = self.tracker.get_experiment(exp_id)
            metrics_path = self.tracker.experiments_dir / exp_id / "metrics.json"
            
            if metrics_path.exists():
                import json
                metrics = json.loads(metrics_path.read_text())
                
                row = {
                    "experiment_id": exp_id,
                    "name": config.name,
                    "llm_provider": config.llm_provider,
                    "deep_think_llm": config.deep_think_llm,
                    "analysts": ",".join(config.selected_analysts),
                    **metrics
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def compare_signals(self, experiment_ids: List[str]) -> pd.DataFrame:
        """Compare signals across experiments."""
        all_signals = []
        
        for exp_id in experiment_ids:
            signals = self.tracker.get_results(exp_id, "signals")
            for signal in signals:
                signal["experiment_id"] = exp_id
                all_signals.append(signal)
        
        return pd.DataFrame(all_signals)
    
    def generate_comparison_report(self, experiment_ids: List[str]) -> str:
        """Generate markdown comparison report."""
        metrics_df = self.compare_metrics(experiment_ids)
        
        report = "# Experiment Comparison Report\n\n"
        report += "## Performance Metrics\n\n"
        report += metrics_df.to_markdown(index=False)
        report += "\n\n"
        
        # Best performers
        report += "## Best Performers\n\n"
        report += f"- Highest Sharpe Ratio: {metrics_df.loc[metrics_df['sharpe_ratio'].idxmax(), 'name']}\n"
        report += f"- Highest CAGR: {metrics_df.loc[metrics_df['cagr'].idxmax(), 'name']}\n"
        report += f"- Lowest Drawdown: {metrics_df.loc[metrics_df['max_drawdown'].idxmax(), 'name']}\n"
        report += f"- Highest Win Rate: {metrics_df.loc[metrics_df['win_rate'].idxmax(), 'name']}\n"
        
        return report
```


### 8.4 Integration with Trading Graph

**File**: `chanana_quant/graph/trading_graph.py`

**Add Experiment Context**:
```python
class ChananaQuantGraph:
    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
        callbacks: Optional[List] = None,
        experiment_id: Optional[str] = None,  # NEW
    ):
        # ... existing initialization ...
        
        # Experiment tracking
        self.experiment_id = experiment_id
        if experiment_id:
            from chanana_quant.experiments.tracker import ExperimentTracker
            self.experiment_tracker = ExperimentTracker()
        else:
            self.experiment_tracker = None
    
    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""
        # ... existing logic ...
        
        # Log to experiment if tracking
        if self.experiment_tracker and self.experiment_id:
            self.experiment_tracker.log_result(
                self.experiment_id,
                "signals",
                {
                    "ticker": company_name,
                    "date": trade_date,
                    "signal": final_state["final_trade_decision"],
                    "structured_signal": signal["structured"].dict() if "structured" in signal else None
                }
            )
        
        return final_state, signal
```

**CLI Integration**:
```python
# In cli/main.py
def run_analysis():
    selections = get_user_selections()
    
    # Create experiment
    from chanana_quant.experiments.config import ExperimentConfig
    from chanana_quant.experiments.tracker import ExperimentTracker
    
    exp_config = ExperimentConfig(
        experiment_id=ExperimentConfig.generate_id(),
        name=f"Analysis_{selections['ticker']}_{selections['analysis_date']}",
        description="Single stock analysis",
        created_at=datetime.now().isoformat(),
        **selections
    )
    
    tracker = ExperimentTracker()
    exp_id = tracker.create_experiment(exp_config)
    
    # Initialize graph with experiment tracking
    graph = ChananaQuantGraph(
        selected_analyst_keys,
        config=config,
        debug=True,
        callbacks=[stats_handler],
        experiment_id=exp_id  # NEW
    )
    
    # ... run analysis ...
    
    # Log final metrics
    tracker.log_metrics(exp_id, {
        "llm_calls": stats_handler.get_stats()["llm_calls"],
        "tool_calls": stats_handler.get_stats()["tool_calls"],
        "elapsed_time": time.time() - start_time
    })
```

---

## 9. Optional Monitoring Dashboard

### 9.1 Dashboard Architecture

**Technology**: Streamlit (lightweight, Python-native)

**Purpose**:
- Visualize agent outputs and signals
- Monitor portfolio performance
- Display backtest results
- Compare experiments

**Module Structure**:
```
chanana_quant/dashboard/
├── app.py              # Main Streamlit app
├── pages/
│   ├── live_analysis.py    # Real-time analysis monitoring
│   ├── backtest.py         # Backtest visualization
│   ├── experiments.py      # Experiment comparison
│   └── portfolio.py        # Portfolio tracking
└── components/
    ├── charts.py           # Reusable chart components
    ├── tables.py           # Data table components
    └── metrics.py          # Metrics display components
```

### 9.2 Main Dashboard Implementation

**File**: `chanana_quant/dashboard/app.py`

```python
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="Chanana Quant Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Chanana Quant Dashboard")
st.markdown("AI-native hedge fund architecture for Indian markets")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Live Analysis", "Backtesting", "Experiments", "Portfolio"]
)

# Load selected page
if page == "Live Analysis":
    from pages import live_analysis
    live_analysis.show()
elif page == "Backtesting":
    from pages import backtest
    backtest.show()
elif page == "Experiments":
    from pages import experiments
    experiments.show()
elif page == "Portfolio":
    from pages import portfolio
    portfolio.show()
```


### 9.3 Live Analysis Page

**File**: `chanana_quant/dashboard/pages/live_analysis.py`

```python
import streamlit as st
from chanana_quant.graph.trading_graph import ChananaQuantGraph
from chanana_quant.default_config import DEFAULT_CONFIG
import json

def show():
    st.header("Live Analysis")
    
    # Input form
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol", value="RELIANCE.NS")
        analysis_date = st.date_input("Analysis Date")
    
    with col2:
        llm_provider = st.selectbox("LLM Provider", ["openai", "anthropic", "google"])
        analysts = st.multiselect(
            "Select Analysts",
            ["market", "social", "news", "fundamentals"],
            default=["market", "news", "fundamentals"]
        )
    
    if st.button("Run Analysis", type="primary"):
        with st.spinner("Running analysis..."):
            # Create config
            config = DEFAULT_CONFIG.copy()
            config["llm_provider"] = llm_provider
            
            # Initialize graph
            graph = ChananaQuantGraph(
                selected_analysts=analysts,
                config=config,
                debug=False
            )
            
            # Run analysis
            final_state, signal = graph.propagate(ticker, str(analysis_date))
            
            # Display results
            st.success("Analysis Complete!")
            
            # Signal summary
            st.subheader("Trading Signal")
            if "structured" in signal:
                sig = signal["structured"]
                col1, col2, col3 = st.columns(3)
                col1.metric("Action", sig.action)
                col2.metric("Confidence", f"{sig.confidence:.2%}")
                col3.metric("Position Size", f"{sig.position_size_pct:.1f}%")
                
                st.markdown(f"**Primary Reason:** {sig.primary_reason}")
            else:
                st.write(signal["text"])
            
            # Analyst reports
            st.subheader("Analyst Reports")
            tabs = st.tabs(["Market", "Sentiment", "News", "Fundamentals"])
            
            with tabs[0]:
                if final_state.get("market_report"):
                    st.markdown(final_state["market_report"])
            with tabs[1]:
                if final_state.get("sentiment_report"):
                    st.markdown(final_state["sentiment_report"])
            with tabs[2]:
                if final_state.get("news_report"):
                    st.markdown(final_state["news_report"])
            with tabs[3]:
                if final_state.get("fundamentals_report"):
                    st.markdown(final_state["fundamentals_report"])
            
            # Research debate
            st.subheader("Research Team Debate")
            if final_state.get("investment_debate_state"):
                debate = final_state["investment_debate_state"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Bull Researcher**")
                    st.markdown(debate.get("bull_history", ""))
                with col2:
                    st.markdown("**Bear Researcher**")
                    st.markdown(debate.get("bear_history", ""))
```


### 9.4 Backtesting Page

**File**: `chanana_quant/dashboard/pages/backtest.py`

```python
import streamlit as st
import plotly.graph_objects as go
from chanana_quant.backtesting.engine import BacktestEngine
from chanana_quant.graph.trading_graph import ChananaQuantGraph
from chanana_quant.default_config import DEFAULT_CONFIG

def show():
    st.header("Backtesting")
    
    # Input form
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker", value="RELIANCE.NS")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    
    with col2:
        initial_capital = st.number_input("Initial Capital", value=100000)
        frequency = st.selectbox("Frequency", ["daily", "weekly"])
    
    if st.button("Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            # Initialize
            config = DEFAULT_CONFIG.copy()
            graph = ChananaQuantGraph(config=config, debug=False)
            engine = BacktestEngine(graph, initial_capital)
            
            # Run backtest
            results = engine.run(ticker, str(start_date), str(end_date), frequency)
            
            # Display metrics
            st.subheader("Performance Metrics")
            metrics = results["metrics"]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Return", f"{metrics['total_return']:.2%}")
            col2.metric("CAGR", f"{metrics['cagr']:.2%}")
            col3.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            col4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Win Rate", f"{metrics['win_rate']:.2%}")
            col2.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
            col3.metric("Total Trades", metrics['total_trades'])
            col4.metric("Final Value", f"₹{metrics['final_value']:,.0f}")
            
            # Portfolio value chart
            st.subheader("Portfolio Value Over Time")
            dates = [r["date"] for r in results["results"]]
            values = [r["portfolio_value"] for r in results["results"]]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='green', width=2)
            ))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Portfolio Value (₹)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Trades table
            st.subheader("Trade History")
            trades_df = pd.DataFrame(results["portfolio"]["trades"])
            st.dataframe(trades_df, use_container_width=True)
```


### 9.5 Experiments Comparison Page

**File**: `chanana_quant/dashboard/pages/experiments.py`

```python
import streamlit as st
import pandas as pd
from chanana_quant.experiments.tracker import ExperimentTracker
from chanana_quant.experiments.comparison import ExperimentComparison

def show():
    st.header("Experiment Comparison")
    
    tracker = ExperimentTracker()
    comparison = ExperimentComparison(tracker)
    
    # List experiments
    experiments = tracker.list_experiments()
    
    if not experiments:
        st.info("No experiments found. Run some analyses first!")
        return
    
    # Select experiments to compare
    exp_options = {f"{exp.name} ({exp.experiment_id})": exp.experiment_id for exp in experiments}
    selected = st.multiselect(
        "Select Experiments to Compare",
        options=list(exp_options.keys()),
        default=list(exp_options.keys())[:3]
    )
    
    if selected:
        selected_ids = [exp_options[name] for name in selected]
        
        # Compare metrics
        st.subheader("Performance Comparison")
        metrics_df = comparison.compare_metrics(selected_ids)
        
        # Display as table
        st.dataframe(metrics_df, use_container_width=True)
        
        # Visualize key metrics
        st.subheader("Metric Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sharpe ratio comparison
            fig = go.Figure(data=[
                go.Bar(x=metrics_df['name'], y=metrics_df['sharpe_ratio'])
            ])
            fig.update_layout(title="Sharpe Ratio Comparison", yaxis_title="Sharpe Ratio")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Win rate comparison
            fig = go.Figure(data=[
                go.Bar(x=metrics_df['name'], y=metrics_df['win_rate'])
            ])
            fig.update_layout(title="Win Rate Comparison", yaxis_title="Win Rate")
            st.plotly_chart(fig, use_container_width=True)
        
        # Generate report
        if st.button("Generate Comparison Report"):
            report = comparison.generate_comparison_report(selected_ids)
            st.markdown(report)
            
            # Download button
            st.download_button(
                "Download Report",
                report,
                file_name="experiment_comparison.md",
                mime="text/markdown"
            )
```

### 9.6 Running the Dashboard

**Command**:
```bash
streamlit run chanana_quant/dashboard/app.py
```

**Add to CLI**:
```python
# In cli/main.py
@app.command()
def dashboard():
    """Launch the monitoring dashboard."""
    import subprocess
    dashboard_path = Path(__file__).parent.parent / "chanana_quant" / "dashboard" / "app.py"
    subprocess.run(["streamlit", "run", str(dashboard_path)])
```

---

## 10. Incremental Implementation Roadmap

### Phase 1: Foundation - Structured Signals & Indian Market Support (2-3 weeks)

**Objective**: Enable structured decision output and basic Indian market support

**Tasks**:
1. **Structured Signal Schema** (3 days)
   - Create `TradingSignal` Pydantic model in `agent_states.py`
   - Update `signal_processing.py` with structured extraction
   - Add validation logic
   - Test with existing pipeline

2. **Risk Manager Structured Output** (2 days)
   - Modify `risk_manager.py` to use `with_structured_output()`
   - Update prompts to request structured format
   - Ensure backward compatibility

3. **NSE Ticker Normalization** (2 days)
   - Create `indian_market_utils.py`
   - Implement ticker normalization functions
   - Add Indian market holiday calendar
   - Integrate with data fetching tools

4. **Testing & Validation** (3 days)
   - Test structured signals on multiple stocks
   - Validate Indian ticker handling
   - Fix edge cases

**Deliverables**:
- Structured `TradingSignal` output with confidence, position size, risk metrics
- Support for NSE/BSE tickers (RELIANCE.NS, TCS.NS, etc.)
- Backward compatible with existing text-based output

**Files Modified**:
- `chanana_quant/agents/utils/agent_states.py`
- `chanana_quant/graph/signal_processing.py`
- `chanana_quant/agents/managers/risk_manager.py`
- `chanana_quant/dataflows/indian_market_utils.py` (new)
- `chanana_quant/dataflows/interface.py`


### Phase 2: Macro Awareness & Indian Market Context (2-3 weeks)

**Objective**: Add macro-level analysis and Indian market specialization

**Tasks**:
1. **Macro Analyst Agent** (4 days)
   - Create `macro_analyst.py`
   - Implement NIFTY50 data fetching
   - Add sectoral indices analysis
   - Create macro context structure

2. **India VIX Integration** (2 days)
   - Add India VIX data fetching in `macro_data.py`
   - Implement volatility regime classification
   - Integrate with risk manager prompts

3. **FII/DII Flow Data** (3 days)
   - Research data sources (NSE, MoneyControl)
   - Implement data fetching (may require scraping)
   - Add to macro analyst report

4. **Graph Integration** (2 days)
   - Add macro analyst as first node in graph
   - Update `setup.py` to include macro node
   - Inject macro context into all analyst prompts

5. **Sector Classification** (2 days)
   - Create Indian sector mapping
   - Implement sector peer identification
   - Add sector context to fundamentals analyst

6. **Testing** (2 days)
   - Test macro analyst on multiple dates
   - Validate context propagation
   - Verify improved decision quality

**Deliverables**:
- Macro analyst providing NIFTY50, sector, and VIX context
- FII/DII flow integration (if data source available)
- Sector-aware analysis for Indian stocks
- All agents receive macro context in prompts

**Files Created**:
- `chanana_quant/agents/analysts/macro_analyst.py`
- `chanana_quant/agents/utils/macro_data_tools.py`
- `chanana_quant/dataflows/macro_data.py`
- `chanana_quant/dataflows/indian_market_data.py`

**Files Modified**:
- `chanana_quant/graph/setup.py`
- `chanana_quant/agents/utils/agent_states.py`
- `chanana_quant/agents/researchers/*.py`
- `chanana_quant/agents/trader/trader.py`
- `chanana_quant/agents/managers/risk_manager.py`


### Phase 3: Backtesting Infrastructure (3-4 weeks)

**Objective**: Enable historical testing and performance validation

**Tasks**:
1. **Portfolio State Tracking** (3 days)
   - Create `portfolio.py` with `Position` and `Portfolio` classes
   - Implement buy/sell/hold logic
   - Add position tracking and value calculation

2. **Trade Simulator** (3 days)
   - Create `simulator.py`
   - Implement signal-to-trade conversion
   - Add execution price logic (next day open)
   - Handle stop loss and take profit

3. **Performance Metrics** (3 days)
   - Create `metrics.py`
   - Implement Sharpe ratio, CAGR, max drawdown
   - Add win rate, profit factor, average win/loss
   - Create metrics report generation

4. **Backtesting Engine** (4 days)
   - Create `engine.py`
   - Implement date iteration logic
   - Integrate with existing graph
   - Add reflection integration

5. **CLI Integration** (2 days)
   - Add `backtest` command to CLI
   - Create backtest configuration UI
   - Add results display

6. **Testing & Validation** (3 days)
   - Run backtests on multiple stocks
   - Validate metrics calculations
   - Compare with buy-and-hold baseline
   - Fix bugs and edge cases

**Deliverables**:
- Fully functional backtesting engine
- Performance metrics (Sharpe, CAGR, drawdown, win rate)
- CLI command for running backtests
- Automatic reflection and memory updates

**Files Created**:
- `chanana_quant/backtesting/engine.py`
- `chanana_quant/backtesting/portfolio.py`
- `chanana_quant/backtesting/simulator.py`
- `chanana_quant/backtesting/metrics.py`
- `chanana_quant/backtesting/config.py`

**Files Modified**:
- `chanana_quant/graph/trading_graph.py`
- `cli/main.py`


### Phase 4: Experiment Tracking & Comparison (2 weeks)

**Objective**: Enable systematic experiment management and comparison

**Tasks**:
1. **Experiment Configuration** (2 days)
   - Create `ExperimentConfig` dataclass in `config.py`
   - Implement serialization/deserialization
   - Add experiment ID generation

2. **Experiment Tracker** (3 days)
   - Create `tracker.py`
   - Implement experiment creation and logging
   - Add result storage (JSONL format)
   - Create experiment listing and loading

3. **Experiment Comparison** (3 days)
   - Create `comparison.py`
   - Implement metrics comparison
   - Add signal comparison
   - Create comparison report generation

4. **Graph Integration** (2 days)
   - Add experiment tracking to `ChananaQuantGraph`
   - Integrate with `propagate()` method
   - Add automatic logging

5. **CLI Integration** (2 days)
   - Update CLI to create experiments
   - Add experiment comparison command
   - Display experiment results

6. **Testing** (2 days)
   - Run multiple experiments with different configs
   - Test comparison functionality
   - Validate report generation

**Deliverables**:
- Experiment tracking system with metadata
- Experiment comparison tools
- CLI commands for experiment management
- Comparison reports (markdown format)

**Files Created**:
- `chanana_quant/experiments/config.py`
- `chanana_quant/experiments/tracker.py`
- `chanana_quant/experiments/comparison.py`
- `chanana_quant/experiments/storage.py`

**Files Modified**:
- `chanana_quant/graph/trading_graph.py`
- `cli/main.py`


### Phase 5: Portfolio Management (2-3 weeks)

**Objective**: Enable multi-stock portfolio management

**Tasks**:
1. **Portfolio Manager** (4 days)
   - Create `manager.py` in portfolio module
   - Implement multi-stock tracking
   - Add portfolio-level risk management
   - Create rebalancing logic

2. **Position Sizing** (3 days)
   - Create `position_sizing.py`
   - Implement Kelly criterion
   - Add risk-based sizing
   - Create volatility-adjusted sizing

3. **Risk Controls** (3 days)
   - Create `risk_controls.py`
   - Implement portfolio-level limits (max position, sector limits)
   - Add correlation analysis
   - Create diversification checks

4. **Rebalancing Logic** (2 days)
   - Create `rebalancing.py`
   - Implement periodic rebalancing
   - Add threshold-based rebalancing

5. **Integration** (3 days)
   - Update risk manager to consider portfolio context
   - Modify backtesting engine for multi-stock
   - Add portfolio mode to CLI

6. **Testing** (2 days)
   - Test with multiple stocks
   - Validate risk controls
   - Compare single-stock vs. portfolio mode

**Deliverables**:
- Portfolio manager for multi-stock tracking
- Position sizing algorithms
- Portfolio-level risk controls
- Rebalancing capabilities

**Files Created**:
- `chanana_quant/portfolio/manager.py`
- `chanana_quant/portfolio/position_sizing.py`
- `chanana_quant/portfolio/risk_controls.py`
- `chanana_quant/portfolio/rebalancing.py`

**Files Modified**:
- `chanana_quant/agents/managers/risk_manager.py`
- `chanana_quant/backtesting/engine.py`
- `chanana_quant/graph/trading_graph.py`
- `cli/main.py`


### Phase 6: Monitoring Dashboard (Optional, 2-3 weeks)

**Objective**: Provide visual interface for monitoring and analysis

**Tasks**:
1. **Dashboard Setup** (2 days)
   - Create dashboard module structure
   - Set up Streamlit app
   - Create navigation and layout

2. **Live Analysis Page** (3 days)
   - Create `live_analysis.py`
   - Implement real-time analysis UI
   - Add signal visualization
   - Display agent reports

3. **Backtesting Page** (3 days)
   - Create `backtest.py`
   - Add backtest configuration UI
   - Implement portfolio value chart
   - Display metrics and trades

4. **Experiments Page** (3 days)
   - Create `experiments.py`
   - Add experiment selection UI
   - Implement comparison visualizations
   - Add report generation

5. **Portfolio Page** (2 days)
   - Create `portfolio.py`
   - Display current positions
   - Show portfolio metrics
   - Add performance charts

6. **Chart Components** (2 days)
   - Create reusable chart components
   - Implement Plotly visualizations
   - Add interactive features

7. **Testing & Polish** (2 days)
   - Test all pages
   - Fix UI issues
   - Add documentation

**Deliverables**:
- Streamlit dashboard with 4 pages
- Real-time analysis monitoring
- Backtest visualization
- Experiment comparison UI
- Portfolio tracking interface

**Files Created**:
- `chanana_quant/dashboard/app.py`
- `chanana_quant/dashboard/pages/live_analysis.py`
- `chanana_quant/dashboard/pages/backtest.py`
- `chanana_quant/dashboard/pages/experiments.py`
- `chanana_quant/dashboard/pages/portfolio.py`
- `chanana_quant/dashboard/components/charts.py`
- `chanana_quant/dashboard/components/tables.py`
- `chanana_quant/dashboard/components/metrics.py`

**Files Modified**:
- `cli/main.py` (add dashboard command)
- `requirements.txt` (add streamlit, plotly)


### Implementation Timeline Summary

| Phase | Duration | Key Deliverables | Priority |
|-------|----------|------------------|----------|
| Phase 1: Foundation | 2-3 weeks | Structured signals, NSE support | Critical |
| Phase 2: Macro Awareness | 2-3 weeks | Macro analyst, India VIX, sectors | High |
| Phase 3: Backtesting | 3-4 weeks | Backtesting engine, metrics | Critical |
| Phase 4: Experiments | 2 weeks | Experiment tracking, comparison | High |
| Phase 5: Portfolio | 2-3 weeks | Multi-stock management | Medium |
| Phase 6: Dashboard | 2-3 weeks | Streamlit monitoring UI | Optional |

**Total Timeline**: 13-18 weeks (3-4.5 months) for full implementation

**Minimum Viable Product (MVP)**: Phases 1-3 (7-10 weeks)
- Structured signals
- Indian market support
- Backtesting capability

**Recommended Approach**:
1. Start with Phase 1 (foundation) - enables all future work
2. Proceed to Phase 3 (backtesting) - validates system effectiveness
3. Add Phase 2 (macro awareness) - improves decision quality
4. Implement Phase 4 (experiments) - enables systematic improvement
5. Consider Phase 5 (portfolio) if multi-stock management needed
6. Add Phase 6 (dashboard) for production monitoring

---

## Appendix A: Key Design Principles

### 1. Preserve Existing Architecture
- Do not rewrite the LangGraph orchestration
- Maintain current agent structure and debate mechanisms
- Keep existing memory system (BM25-based)
- Preserve multi-LLM provider support

### 2. Minimal Code Changes
- Add new modules rather than modifying existing ones extensively
- Use composition over modification
- Maintain backward compatibility where possible
- Extend rather than replace

### 3. Incremental Deployment
- Each phase delivers working functionality
- Can deploy phases independently
- Early phases enable later phases
- No "big bang" releases

### 4. Data-Driven Validation
- Use backtesting to validate improvements
- Track metrics for every change
- Compare experiments systematically
- Make decisions based on performance data

### 5. Indian Market Focus
- Prioritize NSE/BSE support
- Add India-specific macro indicators
- Consider Indian market hours and holidays
- Use Indian market terminology

---

## Appendix B: Risk Mitigation Strategies

### Technical Risks

**Risk**: Structured output may fail with some LLM providers
**Mitigation**: 
- Implement fallback to text-based extraction
- Test with all supported providers
- Add validation and error handling

**Risk**: Backtesting may be slow for long date ranges
**Mitigation**:
- Implement caching for data fetching
- Add progress indicators
- Support parallel execution for multiple stocks

**Risk**: Indian market data may be unavailable or unreliable
**Mitigation**:
- Use yfinance as primary source (reliable for NSE)
- Implement fallback data sources
- Add data quality checks

### Operational Risks

**Risk**: Memory system may not scale with many experiments
**Mitigation**:
- Use efficient BM25 implementation
- Limit memory size per agent
- Implement memory pruning

**Risk**: Dashboard may have performance issues with large datasets
**Mitigation**:
- Implement data pagination
- Use caching for expensive computations
- Optimize chart rendering

---

## Appendix C: Success Metrics

### Phase 1 Success Criteria
- [ ] 100% of signals have structured format with all required fields
- [ ] NSE tickers (*.NS) work correctly with all data sources
- [ ] Backward compatibility maintained (existing code still works)
- [ ] Signal validation catches >90% of inconsistencies

### Phase 2 Success Criteria
- [ ] Macro analyst provides NIFTY50 context for all analyses
- [ ] India VIX regime correctly classified (low/medium/high)
- [ ] Sector context included in fundamentals analysis
- [ ] Agent decisions show awareness of macro conditions

### Phase 3 Success Criteria
- [ ] Backtesting runs successfully on 1+ year of data
- [ ] All metrics calculated correctly (Sharpe, CAGR, drawdown)
- [ ] Reflection system updates memories after each trade
- [ ] Backtest results reproducible across runs

### Phase 4 Success Criteria
- [ ] Experiments tracked with complete metadata
- [ ] Comparison reports generated successfully
- [ ] Can identify best-performing configurations
- [ ] Experiment results stored efficiently

### Phase 5 Success Criteria
- [ ] Portfolio manager tracks multiple positions correctly
- [ ] Position sizing respects portfolio constraints
- [ ] Risk controls prevent over-concentration
- [ ] Rebalancing logic works as expected

### Phase 6 Success Criteria
- [ ] Dashboard loads in <5 seconds
- [ ] All visualizations render correctly
- [ ] Real-time analysis completes in <2 minutes
- [ ] Backtest results display accurately

---

## Appendix D: File Structure After Upgrades

```
chanana_quant/
├── agents/
│   ├── analysts/
│   │   ├── fundamentals_analyst.py
│   │   ├── market_analyst.py
│   │   ├── news_analyst.py
│   │   ├── social_media_analyst.py
│   │   └── macro_analyst.py              # NEW - Phase 2
│   ├── managers/
│   │   ├── research_manager.py
│   │   └── risk_manager.py               # MODIFIED - Phase 1
│   ├── researchers/
│   │   ├── bear_researcher.py
│   │   └── bull_researcher.py
│   ├── risk_mgmt/
│   │   ├── aggressive_debator.py
│   │   ├── conservative_debator.py
│   │   └── neutral_debator.py
│   ├── trader/
│   │   └── trader.py
│   └── utils/
│       ├── agent_states.py               # MODIFIED - Phase 1
│       ├── agent_utils.py
│       ├── core_stock_tools.py
│       ├── fundamental_data_tools.py
│       ├── macro_data_tools.py           # NEW - Phase 2
│       ├── memory.py
│       ├── news_data_tools.py
│       └── technical_indicators_tools.py
├── backtesting/                          # NEW - Phase 3
│   ├── __init__.py
│   ├── config.py
│   ├── engine.py
│   ├── metrics.py
│   ├── portfolio.py
│   └── simulator.py
├── dashboard/                            # NEW - Phase 6
│   ├── app.py
│   ├── components/
│   │   ├── charts.py
│   │   ├── metrics.py
│   │   └── tables.py
│   └── pages/
│       ├── backtest.py
│       ├── experiments.py
│       ├── live_analysis.py
│       └── portfolio.py
├── dataflows/
│   ├── alpha_vantage.py
│   ├── alpha_vantage_common.py
│   ├── alpha_vantage_fundamentals.py
│   ├── alpha_vantage_indicator.py
│   ├── alpha_vantage_news.py
│   ├── alpha_vantage_stock.py
│   ├── config.py
│   ├── indian_market_data.py             # NEW - Phase 2
│   ├── indian_market_utils.py            # NEW - Phase 1
│   ├── interface.py                      # MODIFIED - Phase 1
│   ├── macro_data.py                     # NEW - Phase 2
│   ├── stockstats_utils.py
│   ├── utils.py
│   ├── yfinance_news.py
│   └── y_finance.py
├── experiments/                          # NEW - Phase 4
│   ├── __init__.py
│   ├── comparison.py
│   ├── config.py
│   ├── storage.py
│   └── tracker.py
├── graph/
│   ├── conditional_logic.py
│   ├── propagation.py
│   ├── reflection.py
│   ├── setup.py                          # MODIFIED - Phase 2
│   ├── signal_processing.py              # MODIFIED - Phase 1
│   └── trading_graph.py                  # MODIFIED - Phases 1,4
├── llm_clients/
│   ├── anthropic_client.py
│   ├── base_client.py
│   ├── factory.py
│   ├── google_client.py
│   ├── openai_client.py
│   └── validators.py
├── portfolio/                            # NEW - Phase 5
│   ├── __init__.py
│   ├── manager.py
│   ├── position_sizing.py
│   ├── rebalancing.py
│   └── risk_controls.py
└── default_config.py
```

---

## Appendix E: Dependencies to Add

### Phase 1 Dependencies
```
# No new dependencies required
# Uses existing: pydantic, langchain-core
```

### Phase 2 Dependencies
```
# No new dependencies required
# Uses existing: yfinance, pandas
```

### Phase 3 Dependencies
```
# requirements.txt additions
pandas>=2.3.0  # Already included
numpy>=1.24.0  # For metrics calculations
```

### Phase 4 Dependencies
```
# No new dependencies required
# Uses existing: pandas, json (stdlib)
```

### Phase 5 Dependencies
```
# No new dependencies required
# Uses existing: pandas, numpy
```

### Phase 6 Dependencies
```
# requirements.txt additions
streamlit>=1.28.0
plotly>=5.17.0
```

### Updated requirements.txt
```txt
# Existing dependencies
typing-extensions
langchain-core
langchain-openai
langchain-experimental
pandas
yfinance
stockstats
langgraph
rank-bm25
setuptools
backtrader
parsel
requests
tqdm
pytz
redis
chainlit
rich
typer
questionary
langchain_anthropic
langchain-google-genai

# New dependencies
numpy>=1.24.0
streamlit>=1.28.0
plotly>=5.17.0
```

---

## Conclusion

This upgrade plan provides a comprehensive, code-level roadmap to evolve Chanana Quant from a research prototype into a production-grade trading research system. The plan is designed to:

1. **Preserve the existing architecture**: All upgrades build on the current LangGraph-based multi-agent system without requiring rewrites.

2. **Enable systematic validation**: Backtesting infrastructure allows quantitative validation of system performance.

3. **Specialize for Indian markets**: NSE/BSE support, NIFTY50 context, India VIX, and sector analysis make the system truly Indian market-native.

4. **Provide structured outputs**: Structured signals enable programmatic decision-making, portfolio management, and systematic trading.

5. **Support experimentation**: Experiment tracking enables systematic improvement through A/B testing and configuration optimization.

6. **Scale incrementally**: Each phase delivers working functionality that can be deployed independently.

### Next Steps

1. **Review and approve** this upgrade plan with stakeholders
2. **Set up development environment** with required dependencies
3. **Begin Phase 1 implementation** (structured signals + NSE support)
4. **Establish testing protocols** for each phase
5. **Create project tracking** (GitHub issues, project board)
6. **Schedule regular reviews** to assess progress and adjust priorities

### Expected Outcomes

After completing all phases, Chanana Quant will be:
- A validated trading research system with proven performance metrics
- Specialized for Indian markets with NSE/BSE support and macro awareness
- Capable of systematic backtesting and experiment comparison
- Production-ready with monitoring and portfolio management capabilities
- Positioned as a leading AI-native hedge fund architecture for Indian markets

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-04  
**Status**: Ready for Implementation
