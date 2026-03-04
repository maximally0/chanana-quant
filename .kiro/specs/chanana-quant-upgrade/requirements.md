# Requirements Document: Chanana Quant System Upgrade

## Introduction

This document specifies the requirements for upgrading the Chanana Quant trading system from a research prototype into a production-grade trading research system. Chanana Quant is an AI-native hedge fund architecture for Indian markets that uses LangGraph to orchestrate specialized AI agents for market analysis, investment research, trading decisions, and risk management.

The upgrade encompasses six phases: structured signal output, Indian market specialization, backtesting infrastructure, experiment tracking, portfolio management, and monitoring dashboard. The system will preserve its existing LangGraph architecture while adding critical capabilities for systematic validation, Indian market focus, and production deployment.

## Glossary

- **Trading_System**: The Chanana Quant multi-agent trading analysis framework
- **Signal_Processor**: Component that extracts trading decisions from agent outputs
- **Trading_Signal**: Structured output containing action, confidence, position size, and risk parameters
- **Backtesting_Engine**: Component that simulates trading decisions on historical data
- **Portfolio_Manager**: Component that tracks and manages multiple stock positions
- **Experiment_Tracker**: Component that logs and compares system configurations and results
- **Macro_Analyst**: Agent that analyzes market-level indicators and trends
- **Risk_Manager**: Agent that evaluates and approves/rejects trading decisions
- **NSE**: National Stock Exchange of India
- **BSE**: Bombay Stock Exchange
- **NIFTY50**: India's benchmark stock market index
- **India_VIX**: India's volatility index
- **FII**: Foreign Institutional Investors
- **DII**: Domestic Institutional Investors
- **LangGraph**: Framework for orchestrating multi-agent workflows
- **Agent_State**: Data structure containing all agent reports and decisions
- **Memory_System**: BM25-based retrieval system for agent learning
- **Sharpe_Ratio**: Risk-adjusted return metric
- **CAGR**: Compound Annual Growth Rate
- **Max_Drawdown**: Maximum peak-to-trough decline in portfolio value
- **Position_Sizing**: Algorithm for determining investment amount per trade
- **Stop_Loss**: Price level at which to exit a losing position
- **Take_Profit**: Price level at which to exit a winning position

## Requirements

### Requirement 1: Structured Trading Signal Output

**User Story:** As a system developer, I want trading decisions to be output in a structured format, so that I can programmatically process signals for backtesting and portfolio management.

#### Acceptance Criteria

1. THE Signal_Processor SHALL define a TradingSignal schema with action, confidence, position_size_pct, stop_loss_pct, take_profit_pct, holding_period_days, primary_reason, supporting_factors, risk_factors, timestamp, ticker, and analysis_date fields
2. WHEN the Risk_Manager generates a decision, THE Trading_System SHALL extract a structured TradingSignal object
3. THE TradingSignal action field SHALL contain exactly one of BUY, SELL, or HOLD
4. THE TradingSignal confidence field SHALL be a float between 0.0 and 1.0 inclusive
5. THE TradingSignal position_size_pct field SHALL be a float between 0.0 and 100.0 inclusive
6. WHERE structured output extraction fails, THE Signal_Processor SHALL fall back to LLM-based text extraction
7. THE Trading_System SHALL maintain backward compatibility by storing both structured and text-based signals in Agent_State


### Requirement 2: Signal Validation and Quality Checks

**User Story:** As a risk manager, I want trading signals to be validated for consistency and reasonableness, so that I can identify potentially problematic decisions before execution.

#### Acceptance Criteria

1. WHEN a TradingSignal is generated, THE Signal_Processor SHALL validate that action matches position_size_pct (BUY with >0%, HOLD with 0%)
2. IF stop_loss_pct exceeds 20%, THEN THE Signal_Processor SHALL log a warning
3. IF take_profit_pct is less than stop_loss_pct, THEN THE Signal_Processor SHALL log a warning
4. IF action is HOLD and confidence exceeds 0.7, THEN THE Signal_Processor SHALL log a warning
5. THE Signal_Processor SHALL return validation results with is_valid boolean and error_messages list
6. THE Trading_System SHALL log validation warnings but SHALL NOT fail signal generation

### Requirement 3: Indian Market Ticker Normalization

**User Story:** As a trader, I want to analyze Indian stocks using standard ticker symbols, so that I can seamlessly work with NSE and BSE listed companies.

#### Acceptance Criteria

1. WHEN a ticker without .NS or .BO suffix is provided, THE Trading_System SHALL append .NS suffix by default
2. THE Trading_System SHALL recognize .NS suffix as NSE ticker format
3. THE Trading_System SHALL recognize .BO suffix as BSE ticker format
4. THE Trading_System SHALL provide an is_indian_ticker function that returns true for tickers ending in .NS or .BO
5. THE Trading_System SHALL normalize tickers before routing to data vendors
6. WHERE a ticker is already suffixed with .NS or .BO, THE Trading_System SHALL preserve the original suffix

### Requirement 4: Indian Market Holiday Calendar

**User Story:** As a system operator, I want the system to recognize Indian market holidays, so that I can avoid attempting analysis on non-trading days.

#### Acceptance Criteria

1. THE Trading_System SHALL maintain a calendar of Indian market holidays including Republic Day, Holi, Diwali, and other NSE holidays
2. THE Trading_System SHALL provide an is_indian_market_open function that checks if a given date is a trading day
3. THE Trading_System SHALL exclude weekends (Saturday and Sunday) from trading days
4. THE Trading_System SHALL provide a get_next_trading_day function that returns the next valid Indian trading day
5. WHEN backtesting, THE Trading_System SHALL skip non-trading days automatically
6. THE Trading_System SHALL validate trade dates in the CLI and reject non-trading days with a descriptive message

### Requirement 5: Macro Market Analysis

**User Story:** As an analyst, I want the system to analyze macro market conditions including NIFTY50 trends and sectoral performance, so that individual stock decisions can be made in proper market context.

#### Acceptance Criteria

1. THE Macro_Analyst SHALL fetch NIFTY50 index data using ticker ^NSEI
2. THE Macro_Analyst SHALL classify NIFTY50 trend as bullish, bearish, or sideways based on price action
3. THE Macro_Analyst SHALL calculate NIFTY50 1-day and 1-week percentage changes
4. THE Macro_Analyst SHALL fetch sectoral index data for NIFTY Bank, NIFTY IT, NIFTY Pharma, and NIFTY Auto
5. THE Macro_Analyst SHALL calculate sector performance as percentage change over analysis period
6. THE Macro_Analyst SHALL determine if the analyzed stock is outperforming or underperforming NIFTY50
7. THE Macro_Analyst SHALL classify sector momentum as strong, weak, or neutral
8. THE Macro_Analyst SHALL generate a macro_report containing nifty50_trend, nifty50_change_1d, nifty50_change_1w, sector_performance, stock_vs_nifty, and sector_momentum fields
9. THE Trading_System SHALL execute the Macro_Analyst as the first node in the LangGraph workflow
10. THE Trading_System SHALL inject macro_report into all downstream analyst prompts


### Requirement 6: India VIX Volatility Analysis

**User Story:** As a risk manager, I want the system to analyze India VIX levels and classify volatility regimes, so that position sizing and risk parameters can be adjusted based on market volatility.

#### Acceptance Criteria

1. THE Macro_Analyst SHALL fetch India VIX data using ticker ^INDIAVIX
2. THE Macro_Analyst SHALL calculate the current India VIX value
3. THE Macro_Analyst SHALL calculate India VIX historical percentile over the past year
4. THE Macro_Analyst SHALL classify volatility regime as low when VIX is below 15
5. THE Macro_Analyst SHALL classify volatility regime as medium when VIX is between 15 and 25
6. THE Macro_Analyst SHALL classify volatility regime as high when VIX exceeds 25
7. THE Macro_Analyst SHALL determine VIX trend as rising, falling, or stable based on recent changes
8. THE Risk_Manager SHALL adjust risk tolerance based on volatility regime in prompts
9. WHERE volatility regime is high, THE Risk_Manager SHALL recommend smaller position sizes and tighter stop losses in prompts

### Requirement 7: FII/DII Flow Data Integration

**User Story:** As a market analyst, I want the system to incorporate Foreign and Domestic Institutional Investor flow data, so that institutional sentiment can inform trading decisions.

#### Acceptance Criteria

1. THE Macro_Analyst SHALL fetch FII net flow data in crores
2. THE Macro_Analyst SHALL fetch DII net flow data in crores
3. THE Macro_Analyst SHALL classify FII trend as buying when net flow is positive, selling when negative
4. THE Macro_Analyst SHALL classify DII trend as buying when net flow is positive, selling when negative
5. THE Macro_Analyst SHALL determine institutional_sentiment as bullish, bearish, or neutral based on combined FII and DII flows
6. WHERE FII/DII data is unavailable, THE Macro_Analyst SHALL continue analysis without institutional flow data
7. THE Macro_Analyst SHALL include FII/DII flow data in the macro_report

### Requirement 8: Indian Stock Sector Classification

**User Story:** As a fundamentals analyst, I want stocks to be classified by sector, so that sector-specific analysis and peer comparison can be performed.

#### Acceptance Criteria

1. THE Trading_System SHALL maintain a mapping of Indian stock tickers to sectors including Energy, IT, Banking, Telecom, Pharma, Auto, and FMCG
2. THE Trading_System SHALL provide a get_indian_sector function that returns the sector for a given ticker
3. THE Trading_System SHALL provide a get_sector_peers function that returns up to 5 peer stocks in the same sector
4. WHERE a ticker is not in the sector mapping, THE Trading_System SHALL return "Unknown" as the sector
5. THE Fundamentals_Analyst SHALL include sector classification in analysis
6. THE Macro_Analyst SHALL enable sector-relative performance analysis

### Requirement 9: Portfolio State Tracking

**User Story:** As a portfolio manager, I want the system to track all open and closed positions with entry prices, quantities, and profit/loss, so that I can monitor portfolio performance over time.

#### Acceptance Criteria

1. THE Portfolio_Manager SHALL maintain a Position dataclass with ticker, quantity, entry_price, entry_date, stop_loss, take_profit, and exit information
2. THE Portfolio_Manager SHALL track current cash balance
3. THE Portfolio_Manager SHALL track all open positions in a positions dictionary keyed by ticker
4. THE Portfolio_Manager SHALL track all closed positions in a closed_positions list
5. THE Portfolio_Manager SHALL calculate position cost_basis as quantity multiplied by entry_price
6. THE Portfolio_Manager SHALL calculate position current_value given a current price
7. THE Portfolio_Manager SHALL calculate position profit/loss as current_value minus cost_basis
8. THE Portfolio_Manager SHALL calculate position profit/loss percentage
9. THE Portfolio_Manager SHALL calculate total_value as cash plus sum of all position values
10. THE Portfolio_Manager SHALL maintain a value_history list tracking portfolio value over time


### Requirement 10: Trade Execution Simulation

**User Story:** As a backtesting engineer, I want the system to simulate trade execution based on structured signals, so that I can evaluate trading strategy performance on historical data.

#### Acceptance Criteria

1. WHEN a TradingSignal with action BUY is received, THE Trade_Simulator SHALL calculate position size as portfolio total_value multiplied by position_size_pct divided by 100
2. WHEN a TradingSignal with action BUY is received, THE Trade_Simulator SHALL calculate quantity as position size divided by execution price, rounded down to integer
3. WHEN executing a BUY order, THE Trade_Simulator SHALL use the next trading day's open price as execution price
4. WHEN executing a BUY order with insufficient cash, THE Trade_Simulator SHALL reduce quantity to maximum affordable amount
5. WHEN a TradingSignal with action SELL is received, THE Trade_Simulator SHALL close the position at the next trading day's open price
6. WHEN a TradingSignal with action HOLD is received and a position exists, THE Trade_Simulator SHALL check stop_loss and take_profit levels
7. IF current price triggers stop_loss, THEN THE Trade_Simulator SHALL execute a SELL order
8. IF current price triggers take_profit, THEN THE Trade_Simulator SHALL execute a SELL order
9. WHERE execution price cannot be obtained, THE Trade_Simulator SHALL skip the trade and return None
10. THE Trade_Simulator SHALL return trade details including action, quantity, price, and execution status

### Requirement 11: Performance Metrics Calculation

**User Story:** As a quantitative analyst, I want the system to calculate comprehensive performance metrics including Sharpe ratio, CAGR, and maximum drawdown, so that I can evaluate and compare trading strategies.

#### Acceptance Criteria

1. THE Backtesting_Engine SHALL calculate total_return as final portfolio value minus initial capital divided by initial capital
2. THE Backtesting_Engine SHALL calculate CAGR as annualized return over the backtest period
3. THE Backtesting_Engine SHALL calculate Sharpe_Ratio assuming 252 trading days per year and 5% risk-free rate
4. THE Backtesting_Engine SHALL calculate Max_Drawdown as maximum peak-to-trough decline in portfolio value
5. THE Backtesting_Engine SHALL calculate win_rate as number of profitable trades divided by total closed trades
6. THE Backtesting_Engine SHALL calculate avg_win_pct as average profit percentage of winning trades
7. THE Backtesting_Engine SHALL calculate avg_loss_pct as average loss percentage of losing trades
8. THE Backtesting_Engine SHALL calculate profit_factor as total profits divided by total losses
9. THE Backtesting_Engine SHALL return metrics dictionary with all calculated values
10. WHERE there are no closed trades, THE Backtesting_Engine SHALL return zero for win_rate and profit_factor

### Requirement 12: Backtesting Engine Orchestration

**User Story:** As a researcher, I want to run the trading system on historical data and receive performance metrics, so that I can validate whether the system generates alpha.

#### Acceptance Criteria

1. THE Backtesting_Engine SHALL accept ticker, start_date, end_date, and initial_capital as inputs
2. THE Backtesting_Engine SHALL generate a list of trading dates between start_date and end_date based on rebalance_frequency
3. FOR EACH trading date, THE Backtesting_Engine SHALL invoke the Trading_System propagate method
4. FOR EACH trading date, THE Backtesting_Engine SHALL simulate trade execution based on the returned signal
5. FOR EACH trading date, THE Backtesting_Engine SHALL update portfolio state
6. FOR EACH trading date, THE Backtesting_Engine SHALL record results including date, signal, trade, and portfolio_value
7. WHEN a position is closed, THE Backtesting_Engine SHALL invoke the Trading_System reflect_and_remember method with actual returns
8. WHEN all dates are processed, THE Backtesting_Engine SHALL calculate final performance metrics
9. THE Backtesting_Engine SHALL return results dictionary containing results list, metrics dictionary, and portfolio state
10. THE Backtesting_Engine SHALL support daily and weekly rebalance frequencies


### Requirement 13: Experiment Configuration Management

**User Story:** As a researcher, I want to define and store experiment configurations including LLM settings, analyst selection, and backtest parameters, so that I can reproduce and compare experiments systematically.

#### Acceptance Criteria

1. THE Experiment_Tracker SHALL define an ExperimentConfig dataclass with experiment_id, name, description, created_at, llm_provider, deep_think_llm, quick_think_llm, max_debate_rounds, max_risk_discuss_rounds, selected_analysts, data_vendors, ticker, start_date, end_date, initial_capital, and custom_params fields
2. THE ExperimentConfig SHALL provide a to_dict method that converts the configuration to a dictionary
3. THE ExperimentConfig SHALL provide a to_json method that serializes the configuration to JSON format
4. THE ExperimentConfig SHALL provide a from_dict class method that creates an ExperimentConfig from a dictionary
5. THE ExperimentConfig SHALL provide a generate_id class method that creates unique experiment IDs in format exp_YYYYMMDD_HHMMSS
6. THE Experiment_Tracker SHALL save experiment configuration to experiments/{experiment_id}/config.json
7. THE Experiment_Tracker SHALL create experiment directory structure when a new experiment is created

### Requirement 14: Experiment Result Logging

**User Story:** As a researcher, I want all experiment results including signals and metrics to be logged automatically, so that I can analyze and compare experiments later.

#### Acceptance Criteria

1. WHEN an experiment is created, THE Experiment_Tracker SHALL create a directory at experiments/{experiment_id}
2. WHEN a signal is generated during an experiment, THE Experiment_Tracker SHALL append the signal to {experiment_id}/signals.jsonl
3. WHEN backtesting completes, THE Experiment_Tracker SHALL save metrics to {experiment_id}/metrics.json
4. THE Experiment_Tracker SHALL provide a log_result method that appends data to result_type.jsonl files
5. THE Experiment_Tracker SHALL provide a log_metrics method that saves metrics dictionary to metrics.json
6. THE Experiment_Tracker SHALL provide a get_results method that loads all results of a given type from JSONL files
7. THE Trading_System SHALL automatically log signals when experiment_id is provided during initialization
8. THE Backtesting_Engine SHALL automatically log metrics when experiment_id is provided

### Requirement 15: Experiment Listing and Retrieval

**User Story:** As a researcher, I want to list all experiments and retrieve their configurations and results, so that I can review past experiments and select ones for comparison.

#### Acceptance Criteria

1. THE Experiment_Tracker SHALL provide a get_experiment method that loads ExperimentConfig from config.json
2. THE Experiment_Tracker SHALL provide a list_experiments method that returns all ExperimentConfig objects sorted by created_at descending
3. WHERE an experiment directory exists but config.json is missing, THE Experiment_Tracker SHALL skip that experiment
4. THE Experiment_Tracker SHALL scan the experiments directory to discover all experiments
5. THE Experiment_Tracker SHALL return empty list when no experiments exist

### Requirement 16: Experiment Comparison and Reporting

**User Story:** As a researcher, I want to compare multiple experiments side-by-side with visualizations and summary statistics, so that I can identify the best-performing configurations.

#### Acceptance Criteria

1. THE Experiment_Tracker SHALL provide a compare_metrics method that accepts a list of experiment_ids and returns a DataFrame with metrics for each experiment
2. THE Experiment_Tracker SHALL provide a compare_signals method that accepts a list of experiment_ids and returns a DataFrame with all signals tagged by experiment_id
3. THE Experiment_Tracker SHALL provide a generate_comparison_report method that creates a markdown report comparing experiments
4. THE comparison report SHALL include a performance metrics table with all experiments
5. THE comparison report SHALL identify the best performer for Sharpe_Ratio, CAGR, Max_Drawdown, and win_rate
6. THE Experiment_Tracker SHALL include experiment name, LLM configuration, and analyst selection in comparison tables
7. WHERE metrics.json does not exist for an experiment, THE Experiment_Tracker SHALL skip that experiment in comparisons


### Requirement 17: Multi-Stock Portfolio Management

**User Story:** As a portfolio manager, I want to manage positions across multiple stocks simultaneously with portfolio-level constraints, so that I can build diversified portfolios rather than single-stock strategies.

#### Acceptance Criteria

1. THE Portfolio_Manager SHALL track positions for multiple tickers simultaneously
2. THE Portfolio_Manager SHALL provide an add_stock method that runs analysis for a new ticker
3. THE Portfolio_Manager SHALL aggregate signals from multiple stock analyses
4. THE Portfolio_Manager SHALL calculate portfolio-level metrics including total value, cash allocation, and equity allocation
5. THE Portfolio_Manager SHALL provide a get_portfolio_summary method that returns current positions, values, and allocations
6. THE Portfolio_Manager SHALL support running analysis for multiple stocks in a single session
7. THE Portfolio_Manager SHALL maintain separate position tracking for each ticker

### Requirement 18: Position Sizing Algorithms

**User Story:** As a risk manager, I want position sizes to be calculated using systematic algorithms like Kelly Criterion or risk-based sizing, so that capital allocation is optimized based on risk and expected returns.

#### Acceptance Criteria

1. THE Portfolio_Manager SHALL provide a calculate_kelly_position_size method that implements the Kelly Criterion formula
2. THE Portfolio_Manager SHALL provide a calculate_risk_based_position_size method that sizes positions based on volatility
3. THE Portfolio_Manager SHALL provide a calculate_equal_weight_position_size method that allocates equal weight to all positions
4. THE Portfolio_Manager SHALL accept position_sizing_method as a configuration parameter with values kelly, risk_based, or equal_weight
5. WHEN position_sizing_method is kelly, THE Portfolio_Manager SHALL use win_rate and avg_win/avg_loss to calculate position size
6. WHEN position_sizing_method is risk_based, THE Portfolio_Manager SHALL use stock volatility to adjust position size inversely
7. THE Portfolio_Manager SHALL apply a maximum position size limit to prevent over-concentration
8. THE Portfolio_Manager SHALL override signal position_size_pct with calculated position size when using systematic sizing

### Requirement 19: Portfolio-Level Risk Controls

**User Story:** As a risk manager, I want portfolio-level risk limits including maximum position size, sector concentration limits, and total exposure limits, so that the portfolio remains diversified and risk-controlled.

#### Acceptance Criteria

1. THE Portfolio_Manager SHALL enforce a max_position_size_pct limit (default 20%) that prevents any single position from exceeding this percentage of portfolio value
2. THE Portfolio_Manager SHALL enforce a max_sector_exposure_pct limit (default 40%) that prevents sector concentration
3. THE Portfolio_Manager SHALL enforce a max_total_exposure_pct limit (default 100%) that prevents over-leveraging
4. WHEN a trade would violate max_position_size_pct, THE Portfolio_Manager SHALL reduce position size to the maximum allowed
5. WHEN a trade would violate max_sector_exposure_pct, THE Portfolio_Manager SHALL reject the trade
6. WHEN a trade would violate max_total_exposure_pct, THE Portfolio_Manager SHALL reject the trade
7. THE Portfolio_Manager SHALL provide a check_risk_limits method that validates a proposed trade against all risk limits
8. THE Portfolio_Manager SHALL log risk limit violations with descriptive messages
9. THE Portfolio_Manager SHALL allow risk limits to be configured via Portfolio_Manager initialization parameters

### Requirement 20: Portfolio Rebalancing Logic

**User Story:** As a portfolio manager, I want the system to rebalance the portfolio periodically or when allocations drift beyond thresholds, so that the portfolio maintains target allocations over time.

#### Acceptance Criteria

1. THE Portfolio_Manager SHALL provide a rebalance_portfolio method that adjusts positions to target allocations
2. THE Portfolio_Manager SHALL support periodic rebalancing with configurable frequency (daily, weekly, monthly)
3. THE Portfolio_Manager SHALL support threshold-based rebalancing when position drift exceeds a configurable percentage
4. WHEN rebalancing, THE Portfolio_Manager SHALL calculate target position sizes based on current portfolio value and target allocations
5. WHEN rebalancing, THE Portfolio_Manager SHALL generate BUY or SELL orders to move current positions toward targets
6. THE Portfolio_Manager SHALL respect risk limits during rebalancing
7. THE Portfolio_Manager SHALL log all rebalancing actions with before and after allocations
8. WHERE target allocations are not specified, THE Portfolio_Manager SHALL use equal-weight allocation


### Requirement 21: CLI Backtesting Command

**User Story:** As a system user, I want to run backtests from the command line with configurable parameters, so that I can easily test strategies on historical data without writing code.

#### Acceptance Criteria

1. THE CLI SHALL provide a backtest command that accepts ticker, start_date, end_date, initial_capital, and frequency parameters
2. WHEN the backtest command is invoked, THE CLI SHALL prompt the user to select LLM provider, analysts, and other configuration options
3. WHEN the backtest command is invoked, THE CLI SHALL initialize the Trading_System with selected configuration
4. WHEN the backtest command is invoked, THE CLI SHALL create a Backtesting_Engine and run the backtest
5. WHEN backtesting completes, THE CLI SHALL display performance metrics in a formatted table
6. THE CLI SHALL display metrics including total_return, CAGR, Sharpe_Ratio, Max_Drawdown, win_rate, profit_factor, and total_trades
7. WHEN backtesting completes, THE CLI SHALL save results to a timestamped directory
8. THE CLI SHALL show progress indicators during backtesting execution
9. THE CLI SHALL handle errors gracefully and display user-friendly error messages

### Requirement 22: CLI Experiment Management Commands

**User Story:** As a researcher, I want to list, compare, and view experiments from the command line, so that I can manage experiments without writing Python code.

#### Acceptance Criteria

1. THE CLI SHALL provide an experiments list command that displays all experiments with ID, name, date, and key metrics
2. THE CLI SHALL provide an experiments compare command that accepts multiple experiment IDs and generates a comparison report
3. THE CLI SHALL provide an experiments show command that displays detailed information for a single experiment
4. WHEN experiments compare is invoked, THE CLI SHALL display a comparison table with metrics for all selected experiments
5. WHEN experiments compare is invoked, THE CLI SHALL highlight the best performer for each metric
6. THE CLI SHALL save comparison reports to a markdown file
7. THE CLI SHALL provide an option to export experiment results to CSV format

### Requirement 23: Streamlit Dashboard Application

**User Story:** As a system operator, I want a web-based dashboard to monitor live analysis, view backtesting results, and compare experiments, so that I can interact with the system through a visual interface.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a Streamlit application with navigation sidebar
2. THE Dashboard SHALL include pages for Live Analysis, Backtesting, Experiments, and Portfolio
3. THE Dashboard SHALL launch when the dashboard CLI command is invoked
4. THE Dashboard SHALL load in less than 5 seconds
5. THE Dashboard SHALL use Plotly for interactive visualizations
6. THE Dashboard SHALL display the Chanana Quant logo and branding
7. THE Dashboard SHALL handle errors gracefully with user-friendly error messages

### Requirement 24: Live Analysis Dashboard Page

**User Story:** As an analyst, I want to run live analysis through the dashboard and view results including signals and agent reports, so that I can analyze stocks interactively.

#### Acceptance Criteria

1. THE Live Analysis page SHALL provide input fields for ticker, analysis_date, llm_provider, and analyst selection
2. WHEN the Run Analysis button is clicked, THE Live Analysis page SHALL initialize the Trading_System and execute propagate
3. WHEN analysis completes, THE Live Analysis page SHALL display the trading signal with action, confidence, and position_size_pct metrics
4. WHEN analysis completes, THE Live Analysis page SHALL display the primary_reason for the decision
5. THE Live Analysis page SHALL provide tabs for Market, Sentiment, News, and Fundamentals reports
6. THE Live Analysis page SHALL display the research team debate with bull and bear arguments
7. THE Live Analysis page SHALL show a spinner with "Running analysis..." message during execution
8. THE Live Analysis page SHALL display a success message when analysis completes


### Requirement 25: Backtesting Dashboard Page

**User Story:** As a researcher, I want to run backtests through the dashboard and visualize portfolio value over time with performance metrics, so that I can evaluate strategies visually.

#### Acceptance Criteria

1. THE Backtesting page SHALL provide input fields for ticker, start_date, end_date, initial_capital, and frequency
2. WHEN the Run Backtest button is clicked, THE Backtesting page SHALL initialize the Backtesting_Engine and execute the backtest
3. WHEN backtesting completes, THE Backtesting page SHALL display performance metrics in a 4-column grid layout
4. THE Backtesting page SHALL display total_return, CAGR, Sharpe_Ratio, Max_Drawdown, win_rate, profit_factor, total_trades, and final_value metrics
5. THE Backtesting page SHALL display a line chart showing portfolio value over time
6. THE portfolio value chart SHALL use Plotly with interactive hover tooltips
7. THE Backtesting page SHALL display a trade history table with all executed trades
8. THE trade history table SHALL include date, action, ticker, quantity, price, and profit/loss columns
9. THE Backtesting page SHALL show a spinner during backtest execution
10. THE Backtesting page SHALL format currency values with rupee symbol and thousand separators

### Requirement 26: Experiments Comparison Dashboard Page

**User Story:** As a researcher, I want to compare multiple experiments in the dashboard with visualizations and identify best performers, so that I can optimize system configuration.

#### Acceptance Criteria

1. THE Experiments page SHALL list all available experiments with name and experiment_id
2. THE Experiments page SHALL provide a multiselect widget to choose experiments for comparison
3. WHEN experiments are selected, THE Experiments page SHALL display a comparison table with metrics for all selected experiments
4. THE Experiments page SHALL display bar charts comparing Sharpe_Ratio and win_rate across experiments
5. THE Experiments page SHALL use Plotly for interactive bar charts
6. WHEN the Generate Comparison Report button is clicked, THE Experiments page SHALL create a markdown report
7. THE Experiments page SHALL provide a download button to save the comparison report
8. WHERE no experiments exist, THE Experiments page SHALL display an info message prompting the user to run analyses first
9. THE Experiments page SHALL default to selecting the 3 most recent experiments

### Requirement 27: Portfolio Dashboard Page

**User Story:** As a portfolio manager, I want to view current portfolio positions, allocations, and performance metrics in the dashboard, so that I can monitor portfolio health.

#### Acceptance Criteria

1. THE Portfolio page SHALL display current cash balance and total portfolio value
2. THE Portfolio page SHALL display a table of all open positions with ticker, quantity, entry_price, current_price, current_value, and profit/loss
3. THE Portfolio page SHALL display a pie chart showing allocation by ticker
4. THE Portfolio page SHALL display a pie chart showing allocation by sector
5. THE Portfolio page SHALL calculate and display portfolio-level metrics including total_return and current_exposure_pct
6. THE Portfolio page SHALL use color coding for profit (green) and loss (red) in the positions table
7. THE Portfolio page SHALL refresh data when the Refresh button is clicked
8. WHERE no positions exist, THE Portfolio page SHALL display a message indicating the portfolio is empty

### Requirement 28: System Integration and Backward Compatibility

**User Story:** As a system maintainer, I want all upgrades to integrate seamlessly with the existing LangGraph architecture without breaking current functionality, so that the system remains stable during incremental deployment.

#### Acceptance Criteria

1. THE Trading_System SHALL preserve the existing LangGraph workflow structure with analyst, researcher, trader, and risk management nodes
2. THE Trading_System SHALL maintain the current Agent_State structure with all existing fields
3. THE Trading_System SHALL continue to support all existing LLM providers including OpenAI, Anthropic, Google, xAI, OpenRouter, and Ollama
4. THE Trading_System SHALL maintain the existing Memory_System using BM25-based retrieval
5. THE Trading_System SHALL preserve the existing data vendor routing system
6. WHEN structured signals are enabled, THE Trading_System SHALL store both structured and text-based signals for backward compatibility
7. WHEN macro analyst is disabled, THE Trading_System SHALL function with the original analyst-only workflow
8. THE Trading_System SHALL maintain the existing CLI interface for single-stock analysis
9. THE Trading_System SHALL continue to save analysis results to eval_results directory in the original format
10. THE Trading_System SHALL support gradual adoption of new features without requiring all-or-nothing deployment


### Requirement 29: Data Caching and Performance Optimization

**User Story:** As a system operator, I want data fetching to be cached and optimized, so that backtesting and repeated analyses run efficiently without redundant API calls.

#### Acceptance Criteria

1. THE Trading_System SHALL cache market data fetched during backtesting to avoid redundant API calls
2. THE Trading_System SHALL reuse cached data when the same ticker and date range are requested
3. THE Trading_System SHALL store cached data in the existing dataflows/data_cache directory
4. THE Trading_System SHALL provide a cache expiration mechanism to refresh stale data
5. WHEN backtesting over long date ranges, THE Trading_System SHALL batch data fetching requests
6. THE Trading_System SHALL display progress indicators during data-intensive operations
7. THE Trading_System SHALL handle rate limiting from data vendors gracefully with retry logic
8. THE Trading_System SHALL log cache hits and misses for performance monitoring

### Requirement 30: Error Handling and Logging

**User Story:** As a system operator, I want comprehensive error handling and logging throughout the system, so that I can diagnose issues and ensure system reliability.

#### Acceptance Criteria

1. WHEN data fetching fails, THE Trading_System SHALL log the error and attempt fallback data sources
2. WHEN LLM API calls fail, THE Trading_System SHALL retry up to 3 times with exponential backoff
3. WHEN structured output extraction fails, THE Trading_System SHALL fall back to text-based extraction and log a warning
4. WHEN backtesting encounters an error on a specific date, THE Trading_System SHALL log the error and continue with remaining dates
5. WHEN portfolio risk limits are violated, THE Trading_System SHALL log the violation with details
6. THE Trading_System SHALL provide configurable log levels (DEBUG, INFO, WARNING, ERROR)
7. THE Trading_System SHALL write logs to both console and file
8. THE Trading_System SHALL include timestamps, component names, and context in all log messages
9. THE Trading_System SHALL provide a --debug flag in CLI commands to enable verbose logging
10. THE Trading_System SHALL capture and log all exceptions with full stack traces

### Requirement 31: Configuration Management and Validation

**User Story:** As a system administrator, I want configuration to be validated and documented, so that users can configure the system correctly without errors.

#### Acceptance Criteria

1. THE Trading_System SHALL validate all configuration parameters on initialization
2. THE Trading_System SHALL provide descriptive error messages for invalid configuration values
3. THE Trading_System SHALL document all configuration parameters in default_config.py with comments
4. THE Trading_System SHALL provide default values for all optional configuration parameters
5. THE Trading_System SHALL validate that selected analysts exist before starting analysis
6. THE Trading_System SHALL validate that selected LLM provider is supported
7. THE Trading_System SHALL validate that required API keys are set for selected providers
8. THE Trading_System SHALL validate date formats (YYYY-MM-DD) for all date inputs
9. THE Trading_System SHALL validate that start_date is before end_date in backtesting
10. THE Trading_System SHALL provide a validate_config function that checks configuration completeness

### Requirement 32: Documentation and Examples

**User Story:** As a new user, I want comprehensive documentation with examples for all new features, so that I can learn to use the upgraded system effectively.

#### Acceptance Criteria

1. THE Trading_System SHALL provide README documentation for structured signals with code examples
2. THE Trading_System SHALL provide README documentation for backtesting with CLI and Python examples
3. THE Trading_System SHALL provide README documentation for experiment tracking with usage examples
4. THE Trading_System SHALL provide README documentation for portfolio management with configuration examples
5. THE Trading_System SHALL provide README documentation for the dashboard with screenshots
6. THE Trading_System SHALL include docstrings for all public classes and methods
7. THE Trading_System SHALL provide example scripts in an examples directory demonstrating key features
8. THE Trading_System SHALL document all configuration parameters with descriptions and default values
9. THE Trading_System SHALL provide a migration guide for users upgrading from the original system
10. THE Trading_System SHALL include a troubleshooting section in documentation for common issues


### Requirement 33: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive tests for all new features, so that I can ensure system reliability and catch regressions early.

#### Acceptance Criteria

1. THE Trading_System SHALL include unit tests for TradingSignal validation logic
2. THE Trading_System SHALL include unit tests for Indian ticker normalization functions
3. THE Trading_System SHALL include unit tests for Portfolio state tracking and calculations
4. THE Trading_System SHALL include unit tests for Trade_Simulator execution logic
5. THE Trading_System SHALL include unit tests for performance metrics calculations
6. THE Trading_System SHALL include integration tests for Backtesting_Engine end-to-end workflow
7. THE Trading_System SHALL include integration tests for Experiment_Tracker storage and retrieval
8. THE Trading_System SHALL include tests for Portfolio_Manager risk limit enforcement
9. THE Trading_System SHALL achieve at least 80% code coverage for new modules
10. THE Trading_System SHALL include tests that verify backward compatibility with existing functionality

### Requirement 34: Deployment and Installation

**User Story:** As a system administrator, I want clear installation instructions and dependency management, so that I can deploy the upgraded system smoothly.

#### Acceptance Criteria

1. THE Trading_System SHALL update requirements.txt with all new dependencies including numpy, streamlit, and plotly
2. THE Trading_System SHALL specify minimum Python version requirement (3.10 or higher)
3. THE Trading_System SHALL provide installation instructions in README for all new dependencies
4. THE Trading_System SHALL ensure all new modules are importable after pip install
5. THE Trading_System SHALL provide a setup verification script that checks all dependencies are installed
6. THE Trading_System SHALL document any system-level dependencies (e.g., for data sources)
7. THE Trading_System SHALL provide Docker configuration for containerized deployment (optional)
8. THE Trading_System SHALL maintain compatibility with existing virtual environment setup
9. THE Trading_System SHALL provide upgrade instructions for users migrating from the original system
10. THE Trading_System SHALL include a changelog documenting all new features and changes

## Requirements Summary

This requirements document specifies 34 high-level requirements organized into 6 phases:

**Phase 1: Foundation (Requirements 1-4)** - Structured signals and Indian market support
**Phase 2: Macro Awareness (Requirements 5-8)** - Macro analysis and Indian market context  
**Phase 3: Backtesting (Requirements 9-12)** - Backtesting infrastructure and metrics
**Phase 4: Experiments (Requirements 13-16)** - Experiment tracking and comparison
**Phase 5: Portfolio (Requirements 17-20)** - Multi-stock portfolio management
**Phase 6: Dashboard (Requirements 23-27)** - Monitoring and visualization interface
**Cross-Cutting (Requirements 21-22, 28-34)** - CLI, integration, quality, and deployment

All requirements follow EARS patterns and INCOSE quality rules to ensure clarity, testability, and completeness. The system will preserve its existing LangGraph architecture while adding critical capabilities for production deployment and systematic validation.

## Implementation Notes

### Phased Deployment Strategy

The requirements are designed for incremental implementation:
- Phase 1 (Requirements 1-4) enables all future work and should be implemented first
- Phase 3 (Requirements 9-12) can be implemented before Phase 2 if backtesting is higher priority
- Phase 6 (Requirements 23-27) is optional and can be deferred or skipped
- Cross-cutting requirements (28-34) should be addressed throughout all phases

### Key Design Principles

1. **Preserve Architecture**: All requirements extend rather than replace the existing LangGraph system
2. **Backward Compatibility**: Structured signals coexist with text-based signals; new features are opt-in
3. **Indian Market Focus**: NSE/BSE support, NIFTY50 context, India VIX, and sector analysis
4. **Data-Driven Validation**: Backtesting enables quantitative validation of system performance
5. **Incremental Value**: Each phase delivers working functionality that can be deployed independently

### Success Criteria

The upgraded system will be considered successful when:
- All trading signals are output in structured format with validation
- Indian stocks can be analyzed with proper NSE/BSE ticker handling
- Backtesting runs successfully on 1+ year of historical data with accurate metrics
- Experiments can be tracked, compared, and reproduced systematically
- Portfolio management supports multi-stock strategies with risk controls
- The system maintains backward compatibility with existing workflows
- Documentation and examples enable new users to adopt all features

### Risk Mitigation

Key risks and mitigations:
- **Structured output failures**: Fallback to LLM-based text extraction
- **Indian data availability**: Use yfinance as reliable primary source with fallbacks
- **Backtesting performance**: Implement caching and progress indicators
- **Breaking changes**: Maintain backward compatibility and gradual feature adoption
- **Complexity**: Comprehensive documentation, examples, and error messages
