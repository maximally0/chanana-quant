# Implementation Plan: Chanana Quant System Upgrade

## Overview

This implementation plan converts the Chanana Quant system upgrade design into actionable coding tasks. The upgrade transforms the system from a research prototype into a production-grade trading research platform with structured signals, Indian market specialization, backtesting infrastructure, experiment tracking, portfolio management, and monitoring dashboard.

The implementation follows a phased approach across 6 major phases with clear dependencies and checkpoints. Each task references specific requirements for traceability.

## Tasks

### Phase 1: Foundation - Structured Signals and Indian Market Support

- [ ] 1. Set up structured signal schema and validation
  - [ ] 1.1 Create TradingSignal Pydantic model in agent_states.py
    - Define TradingSignal schema with action, confidence, position_size_pct, stop_loss_pct, take_profit_pct, holding_period_days, primary_reason, supporting_factors, risk_factors, timestamp, ticker, and analysis_date fields
    - Add field validators for constraints (action in BUY/SELL/HOLD, confidence 0-1, position_size_pct 0-100)
    - _Requirements: 1.1, 1.3, 1.4, 1.5_
  
  - [ ]* 1.2 Write property test for TradingSignal field constraints
    - **Property 1: Trading Signal Field Constraints**
    - **Validates: Requirements 1.3, 1.4, 1.5**
    - Use hypothesis to generate random TradingSignal instances and verify all field constraints
    - _Requirements: 1.3, 1.4, 1.5_
  
  - [ ] 1.3 Create SignalProcessor class for structured extraction
    - Implement process_signal method with structured output parsing using PydanticOutputParser
    - Implement LLM-based fallback extraction when structured output fails
    - Add logging for fallback occurrences
    - _Requirements: 1.2, 1.6_
  
  - [ ]* 1.4 Write property test for signal extraction round-trip
    - **Property 3: Signal Extraction Round-Trip**
    - **Validates: Requirements 1.2, 1.6**
    - _Requirements: 1.2, 1.6_


  - [ ] 1.5 Implement signal validation logic
    - Create validate_signal method checking action-position_size consistency
    - Add warnings for stop_loss > 20%, take_profit < stop_loss, HOLD with high confidence
    - Return validation results with is_valid boolean and error_messages list
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 1.6 Write property test for signal action consistency
    - **Property 2: Signal Action Consistency**
    - **Validates: Requirements 2.1**
    - _Requirements: 2.1_
  
  - [ ] 1.7 Update Risk Manager to output structured signals
    - Modify risk_manager.py to use with_structured_output() for TradingSignal
    - Store both structured signal and text decision in AgentState for backward compatibility
    - Update prompts to include all required signal fields
    - _Requirements: 1.2, 1.7_
  
  - [ ]* 1.8 Write unit tests for signal validation edge cases
    - Test boundary values (confidence 0.0, 1.0, position_size 0%, 100%)
    - Test warning triggers (stop_loss 20%, 25%, take_profit < stop_loss)
    - Test action-position consistency violations
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 2. Implement Indian market ticker normalization and calendar
  - [ ] 2.1 Create indian_market_utils.py module
    - Implement normalize_indian_ticker function (append .NS by default, preserve existing suffixes)
    - Implement is_indian_ticker function (check for .NS or .BO suffix)
    - Define INDIAN_MARKET_HOLIDAYS list with 2024-2025 holidays
    - Define INDIAN_SECTOR_MAPPING dictionary for major stocks
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 8.1_
  
  - [ ]* 2.2 Write property test for ticker normalization idempotence
    - **Property 4: Ticker Normalization Idempotence**
    - **Validates: Requirements 3.1, 3.6**
    - Verify normalize(normalize(ticker)) == normalize(ticker) for all inputs
    - _Requirements: 3.1, 3.6_
  
  - [ ]* 2.3 Write property test for Indian ticker classification
    - **Property 5: Indian Ticker Classification**
    - **Validates: Requirements 3.4**
    - _Requirements: 3.4_
  
  - [ ] 2.4 Implement market calendar functions
    - Implement is_indian_market_open function (check weekends and holidays)
    - Implement get_next_trading_day function (skip non-trading days)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 2.5 Write property test for market calendar consistency
    - **Property 6: Market Calendar Consistency**
    - **Validates: Requirements 4.2, 4.3, 4.4**
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [ ]* 2.6 Write property test for weekend exclusion
    - **Property 7: Weekend Exclusion**
    - **Validates: Requirements 4.3**
    - _Requirements: 4.3_
  
  - [ ] 2.7 Implement sector classification functions
    - Implement get_indian_sector function (return sector or "Unknown")
    - Implement get_sector_peers function (return up to 5 peers in same sector)
    - _Requirements: 8.2, 8.3, 8.4_
  
  - [ ]* 2.8 Write property test for sector peer consistency
    - **Property 11: Sector Peer Consistency**
    - **Validates: Requirements 8.3**
    - _Requirements: 8.3_
  
  - [ ] 2.9 Integrate ticker normalization into data routing layer
    - Update dataflows/interface.py to normalize tickers before vendor routing
    - Ensure backward compatibility with existing ticker formats
    - _Requirements: 3.5_
  
  - [ ]* 2.10 Write unit tests for ticker normalization edge cases
    - Test empty strings, special characters, mixed case
    - Test tickers with and without suffixes
    - Test BSE vs NSE suffix handling
    - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [ ] 3. Checkpoint - Phase 1 foundation complete
  - Ensure all tests pass, verify structured signals work end-to-end, ask the user if questions arise.



### Phase 2: Macro Awareness - Indian Market Context

- [ ] 4. Create macro data fetching tools
  - [ ] 4.1 Create macro_data_tools.py with data fetching functions
    - Implement get_nifty50_data tool (fetch ^NSEI from yfinance)
    - Implement get_india_vix_data tool (fetch ^INDIAVIX from yfinance)
    - Implement get_sectoral_indices tool (fetch ^NSEBANK, ^CNXIT, ^CNXPHARMA, ^CNXAUTO)
    - Implement get_fii_dii_flows tool (with fallback for unavailable data)
    - Add error handling and fallback logic for data unavailability
    - _Requirements: 5.1, 6.1, 7.1, 7.2_
  
  - [ ]* 4.2 Write unit tests for macro data fetching
    - Test with mocked API responses
    - Test error handling and fallbacks
    - Test data structure validation
    - _Requirements: 5.1, 6.1, 7.1, 7.2, 7.6_

- [ ] 5. Implement MacroReport schema and analysis logic
  - [ ] 5.1 Create MacroReport Pydantic model
    - Define schema with nifty50_trend, nifty50_change_1d, nifty50_change_1w, india_vix_current, volatility_regime, fii_net_flow, dii_net_flow, institutional_sentiment, sector_performance, stock_sector, stock_vs_nifty, sector_momentum fields
    - Add field validators for enums and ranges
    - _Requirements: 5.8, 6.3, 7.5_
  
  - [ ]* 5.2 Write property test for NIFTY50 percentage change calculation
    - **Property 8: NIFTY50 Percentage Change Calculation**
    - **Validates: Requirements 5.3**
    - _Requirements: 5.3_
  
  - [ ]* 5.3 Write property test for stock vs index classification
    - **Property 9: Stock vs Index Classification**
    - **Validates: Requirements 5.6**
    - _Requirements: 5.6_
  
  - [ ]* 5.4 Write property test for VIX regime classification
    - **Property 10: VIX Regime Classification**
    - **Validates: Requirements 6.4, 6.5, 6.6**
    - _Requirements: 6.4, 6.5, 6.6_
  
  - [ ] 5.5 Create macro_analyst.py agent
    - Implement macro_analyst_node function that analyzes NIFTY50, India VIX, FII/DII flows, and sectors
    - Classify NIFTY50 trend as bullish/bearish/sideways based on price action
    - Calculate NIFTY50 1-day and 1-week percentage changes
    - Classify volatility regime based on VIX thresholds (low <15, medium 15-25, high >25)
    - Determine VIX trend (rising/falling/stable)
    - Classify FII/DII trends and determine institutional sentiment
    - Calculate sector performance and identify top/worst performers
    - Determine stock vs NIFTY performance and sector momentum
    - Return MacroReport in AgentState
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.3, 7.4, 7.5, 7.7_
  
  - [ ]* 5.6 Write unit tests for macro analyst logic
    - Test NIFTY50 trend classification with sample data
    - Test VIX regime classification at boundary values
    - Test institutional sentiment determination
    - Test sector performance calculations
    - _Requirements: 5.2, 5.7, 6.4, 6.5, 6.6, 7.5_

- [ ] 6. Integrate macro analyst into LangGraph workflow
  - [ ] 6.1 Add macro analyst node to graph setup
    - Update graph/setup.py to add macro_analyst as first node in workflow
    - Add MacroReport field to AgentState
    - Wire macro analyst to execute before existing analysts
    - _Requirements: 5.9_
  
  - [ ] 6.2 Inject macro context into downstream agent prompts
    - Update all analyst prompts to include macro_report context
    - Update Risk Manager prompt to adjust recommendations based on volatility regime
    - Ensure macro context is optional (backward compatibility when disabled)
    - _Requirements: 5.10, 6.8, 6.9_
  
  - [ ]* 6.3 Write integration test for macro context flow
    - Test end-to-end analysis with macro analyst enabled
    - Verify MacroReport is generated and passed to downstream agents
    - Test with macro analyst disabled (backward compatibility)
    - _Requirements: 5.9, 5.10, 28.7_

- [ ] 7. Checkpoint - Phase 2 macro awareness complete
  - Ensure all tests pass, verify macro context enriches analysis, ask the user if questions arise.



### Phase 3: Backtesting - Historical Simulation and Performance Metrics

- [ ] 8. Implement portfolio state tracking
  - [ ] 8.1 Create Position dataclass in portfolio.py
    - Define Position with ticker, quantity, entry_price, entry_date, stop_loss, take_profit, exit_price, exit_date fields
    - Implement cost_basis property (quantity * entry_price)
    - Implement current_value method (quantity * current_price)
    - Implement pnl and pnl_pct methods
    - Implement is_closed property
    - _Requirements: 9.1, 9.5, 9.6, 9.7, 9.8_
  
  - [ ]* 8.2 Write property test for position cost basis invariant
    - **Property 12: Position Cost Basis Invariant**
    - **Validates: Requirements 9.5**
    - _Requirements: 9.5_
  
  - [ ]* 8.3 Write property test for position P&L calculation
    - **Property 13: Position P&L Calculation**
    - **Validates: Requirements 9.7, 9.8**
    - _Requirements: 9.7, 9.8_
  
  - [ ] 8.4 Create Portfolio class for state management
    - Implement __init__ with initial_capital parameter
    - Track cash, positions dict, closed_positions list, trades list, value_history list
    - Implement total_value property (cash + sum of position values)
    - Implement buy method (create position, deduct cash, record trade)
    - Implement sell method (close position, add cash, record trade)
    - Implement update_value method (record portfolio value at date)
    - Implement to_dict method for serialization
    - _Requirements: 9.2, 9.3, 9.4, 9.9, 9.10_
  
  - [ ]* 8.5 Write property test for portfolio value conservation
    - **Property 14: Portfolio Value Conservation**
    - **Validates: Requirements 9.9**
    - _Requirements: 9.9_
  
  - [ ]* 8.6 Write unit tests for portfolio state transitions
    - Test buy order execution (sufficient funds, insufficient funds)
    - Test sell order execution (position exists, position doesn't exist)
    - Test value history tracking
    - _Requirements: 9.2, 9.3, 9.4, 9.10_

- [ ] 9. Implement trade execution simulator
  - [ ] 9.1 Create TradeSimulator class in simulator.py
    - Implement execute_signal method that processes TradingSignal and executes trades
    - Implement _get_execution_price method (fetch next trading day's open price)
    - Implement _check_stop_loss method (check if stop loss triggered)
    - Implement _check_take_profit method (check if take profit triggered)
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.7, 10.8, 10.9_
  
  - [ ] 9.2 Implement BUY signal execution logic
    - Calculate position size as portfolio.total_value * signal.position_size_pct / 100
    - Get execution price (next trading day's open)
    - Calculate quantity as position_size / execution_price (rounded down)
    - Check sufficient cash, reduce quantity if needed
    - Execute buy order with stop_loss and take_profit levels
    - Return trade details
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 9.3 Write property test for trade execution price consistency
    - **Property 15: Trade Execution Price Consistency**
    - **Validates: Requirements 10.3, 10.5**
    - _Requirements: 10.3, 10.5_
  
  - [ ]* 9.4 Write property test for insufficient funds handling
    - **Property 16: Insufficient Funds Handling**
    - **Validates: Requirements 10.4**
    - _Requirements: 10.4_
  
  - [ ] 9.5 Implement SELL signal execution logic
    - Check if position exists
    - Get execution price (next trading day's open)
    - Execute sell order
    - Record P&L
    - _Requirements: 10.5_
  
  - [ ] 9.6 Implement HOLD signal processing with stop loss/take profit checks
    - Check existing positions for stop_loss trigger
    - Check existing positions for take_profit trigger
    - Execute automatic exits if triggered
    - _Requirements: 10.6, 10.7, 10.8_
  
  - [ ]* 9.7 Write property test for stop loss trigger
    - **Property 17: Stop Loss Trigger**
    - **Validates: Requirements 10.7**
    - _Requirements: 10.7_
  
  - [ ]* 9.8 Write unit tests for trade simulator edge cases
    - Test execution price unavailable (skip trade)
    - Test position doesn't exist for SELL
    - Test stop loss and take profit boundary conditions
    - _Requirements: 10.9_

- [ ] 10. Implement performance metrics calculator
  - [ ] 10.1 Create PerformanceMetrics class in metrics.py
    - Implement calculate method that computes all metrics from results and portfolio
    - Implement _calculate_returns helper (convert portfolio values to returns)
    - Implement _calculate_sharpe_ratio (annualized, 252 trading days, 5% risk-free rate)
    - Implement _calculate_max_drawdown (maximum peak-to-trough decline)
    - Implement _calculate_cagr (annualized return over period)
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ]* 10.2 Write property test for Sharpe ratio calculation
    - **Property 18: Sharpe Ratio Calculation**
    - **Validates: Requirements 11.3**
    - _Requirements: 11.3_
  
  - [ ]* 10.3 Write property test for maximum drawdown calculation
    - **Property 19: Maximum Drawdown Calculation**
    - **Validates: Requirements 11.4**
    - _Requirements: 11.4_
  
  - [ ] 10.4 Implement trade-level metrics
    - Calculate win_rate (profitable trades / total trades)
    - Calculate avg_win_pct (average profit % of winning trades)
    - Calculate avg_loss_pct (average loss % of losing trades)
    - Calculate profit_factor (total profits / total losses)
    - Handle edge cases (no trades, all wins, all losses)
    - _Requirements: 11.5, 11.6, 11.7, 11.8, 11.10_
  
  - [ ]* 10.5 Write property test for win rate calculation
    - **Property 20: Win Rate Calculation**
    - **Validates: Requirements 11.5**
    - _Requirements: 11.5_
  
  - [ ]* 10.6 Write unit tests for metrics edge cases
    - Test with zero closed trades
    - Test with all winning trades
    - Test with all losing trades
    - Test CAGR calculation with various time periods
    - _Requirements: 11.10_

- [ ] 11. Implement backtesting engine orchestration
  - [ ] 11.1 Create BacktestEngine class in engine.py
    - Implement __init__ with graph and initial_capital parameters
    - Initialize Portfolio, TradeSimulator, and PerformanceMetrics instances
    - _Requirements: 12.1_
  
  - [ ] 11.2 Implement run method for backtest execution
    - Accept ticker, start_date, end_date, rebalance_frequency parameters
    - Generate trading dates using _generate_trading_dates helper
    - Loop through each trading date
    - Call graph.propagate(ticker, date) to get signal
    - Call simulator.execute_signal to simulate trade
    - Update portfolio state
    - Record results (date, signal, trade, portfolio_value)
    - Call graph.reflect_and_remember when position closed
    - Calculate final performance metrics
    - Return results dict with results list, metrics dict, and portfolio state
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9_
  
  - [ ] 11.3 Implement _generate_trading_dates helper
    - Generate dates between start_date and end_date based on rebalance_frequency
    - Support daily and weekly frequencies
    - Filter out non-trading days using is_indian_market_open
    - _Requirements: 12.2, 12.10_
  
  - [ ]* 11.4 Write integration test for backtesting workflow
    - Test end-to-end backtest over 1 month period
    - Verify all components interact correctly
    - Verify results structure is complete
    - Verify metrics are calculated
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9_

- [ ] 12. Checkpoint - Phase 3 backtesting complete
  - Ensure all tests pass, run sample backtest and verify metrics, ask the user if questions arise.



### Phase 4: Experiments - Configuration and Result Tracking

- [ ] 13. Implement experiment configuration management
  - [ ] 13.1 Create ExperimentConfig dataclass in config.py
    - Define dataclass with experiment_id, name, description, created_at, llm_provider, deep_think_llm, quick_think_llm, max_debate_rounds, max_risk_discuss_rounds, selected_analysts, data_vendors, ticker, start_date, end_date, initial_capital, rebalance_frequency, custom_params fields
    - Implement to_dict method for serialization
    - Implement to_json method for JSON serialization
    - Implement from_dict classmethod for deserialization
    - Implement generate_id classmethod (format: exp_YYYYMMDD_HHMMSS)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 13.2 Write property test for config serialization round-trip
    - **Property 21: Experiment Configuration Serialization Round-Trip**
    - **Validates: Requirements 13.2, 13.3, 13.4**
    - _Requirements: 13.2, 13.3, 13.4_
  
  - [ ] 13.3 Implement configuration validation
    - Validate LLM provider is supported
    - Validate analysts exist in system
    - Validate date formats and ranges
    - Validate numeric parameters are within bounds
    - _Requirements: 31.1, 31.2, 31.5, 31.6, 31.8, 31.9_
  
  - [ ]* 13.4 Write unit tests for config validation
    - Test with invalid LLM provider
    - Test with unknown analysts
    - Test with invalid date formats
    - Test with start_date after end_date
    - _Requirements: 31.1, 31.2, 31.5, 31.6, 31.8, 31.9_

- [ ] 14. Implement experiment result tracking
  - [ ] 14.1 Create ExperimentTracker class in tracker.py
    - Implement __init__ with experiments_dir parameter
    - Create experiments directory if it doesn't exist
    - _Requirements: 14.1_
  
  - [ ] 14.2 Implement experiment creation and storage
    - Implement create_experiment method (create directory, save config.json)
    - Create directory structure: experiments/{experiment_id}/
    - Save config.json, create empty signals.jsonl, metrics.json, logs.txt
    - _Requirements: 13.6, 13.7, 14.1_
  
  - [ ] 14.3 Implement result logging methods
    - Implement log_result method (append to result_type.jsonl files)
    - Implement log_metrics method (save metrics dict to metrics.json)
    - Use JSONL format for streaming results (one JSON object per line)
    - _Requirements: 14.2, 14.3, 14.4_
  
  - [ ] 14.4 Implement experiment retrieval methods
    - Implement get_experiment method (load ExperimentConfig from config.json)
    - Implement list_experiments method (scan directory, return all configs sorted by created_at)
    - Implement get_results method (load results from JSONL file)
    - Handle missing or corrupted files gracefully
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 14.5 Write unit tests for experiment tracking
    - Test experiment creation and directory structure
    - Test result logging (signals, metrics)
    - Test experiment retrieval
    - Test listing with empty directory
    - Test handling of corrupted files
    - _Requirements: 13.6, 13.7, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3_

- [ ] 15. Implement experiment comparison engine
  - [ ] 15.1 Create ExperimentComparison class in comparison.py
    - Implement __init__ with ExperimentTracker instance
    - _Requirements: 16.1_
  
  - [ ] 15.2 Implement comparison methods
    - Implement compare_metrics method (return DataFrame with metrics for all experiments)
    - Implement compare_signals method (return DataFrame with all signals tagged by experiment_id)
    - Load metrics from each experiment and combine into comparison table
    - _Requirements: 16.1, 16.2_
  
  - [ ] 15.3 Implement comparison report generation
    - Implement generate_comparison_report method (create markdown report)
    - Include performance metrics table
    - Identify best performers for each metric (Sharpe, CAGR, Max Drawdown, win_rate)
    - Include experiment configurations in comparison
    - _Requirements: 16.3, 16.4, 16.5, 16.6_
  
  - [ ] 15.4 Handle missing experiment data
    - Skip experiments without metrics.json
    - Log warnings for incomplete experiments
    - _Requirements: 16.7_
  
  - [ ]* 15.5 Write unit tests for experiment comparison
    - Test compare_metrics with multiple experiments
    - Test report generation
    - Test handling of missing metrics
    - Test best performer identification
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.7_

- [ ] 16. Integrate experiment tracking into system
  - [ ] 16.1 Add experiment tracking to TradingSystem
    - Update graph initialization to accept experiment_id parameter
    - Auto-log signals when experiment_id is provided
    - Store experiment_id in AgentState
    - _Requirements: 14.7_
  
  - [ ] 16.2 Add experiment tracking to BacktestEngine
    - Accept experiment_id parameter in run method
    - Auto-log metrics when experiment_id is provided
    - _Requirements: 14.8_
  
  - [ ]* 16.3 Write integration test for experiment workflow
    - Create experiment configuration
    - Run analysis with experiment tracking
    - Verify results are logged
    - Retrieve and compare experiments
    - Verify report generation
    - _Requirements: 13.6, 13.7, 14.2, 14.3, 14.7, 14.8, 16.1, 16.2, 16.3_

- [ ] 17. Checkpoint - Phase 4 experiments complete
  - Ensure all tests pass, create and compare sample experiments, ask the user if questions arise.



### Phase 5: Portfolio - Multi-Stock Management and Risk Controls

- [ ] 18. Implement position sizing algorithms
  - [ ] 18.1 Create position_sizing.py module
    - Implement calculate_signal_based_size function (use signal.position_size_pct directly)
    - Implement calculate_kelly_size function (Kelly Criterion: f = (p*b - q)/b)
    - Implement calculate_risk_based_size function (inverse volatility weighting)
    - Implement calculate_equal_weight_size function (equal allocation)
    - _Requirements: 18.1, 18.2, 18.3, 18.4_
  
  - [ ]* 18.2 Write property test for Kelly criterion position sizing
    - **Property 24: Kelly Criterion Position Sizing**
    - **Validates: Requirements 18.5**
    - _Requirements: 18.5_
  
  - [ ]* 18.3 Write property test for risk-based sizing inverse relationship
    - **Property 25: Risk-Based Position Sizing Inverse Relationship**
    - **Validates: Requirements 18.6**
    - _Requirements: 18.6_
  
  - [ ]* 18.4 Write unit tests for position sizing edge cases
    - Test Kelly with win_rate 0, 1, 0.5
    - Test risk-based with very high/low volatility
    - Test equal weight with various portfolio sizes
    - Test max_kelly_fraction capping
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7_

- [ ] 19. Implement portfolio-level risk controls
  - [ ] 19.1 Create RiskControls class in risk_controls.py
    - Implement __init__ with max_position_size_pct, max_sector_exposure_pct, max_total_exposure_pct parameters
    - _Requirements: 19.1, 19.2, 19.3_
  
  - [ ] 19.2 Implement risk limit checking methods
    - Implement check_position_size_limit (verify position <= max_position_size_pct)
    - Implement check_sector_exposure_limit (verify sector total <= max_sector_exposure_pct)
    - Implement check_total_exposure_limit (verify total equity <= max_total_exposure_pct)
    - Return (is_valid, error_message) tuples
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_
  
  - [ ] 19.3 Implement position size adjustment
    - Implement adjust_position_size method (reduce size to comply with all limits)
    - Apply limits in order: position size, sector exposure, total exposure
    - _Requirements: 19.4, 19.7_
  
  - [ ] 19.4 Add risk limit violation logging
    - Log all violations with descriptive messages
    - Include ticker, requested size, limit, and violation type
    - _Requirements: 19.8_
  
  - [ ]* 19.5 Write property test for position size limit enforcement
    - **Property 22: Position Size Limit Enforcement**
    - **Validates: Requirements 19.1, 19.4**
    - _Requirements: 19.1, 19.4_
  
  - [ ]* 19.6 Write property test for sector exposure limit enforcement
    - **Property 23: Sector Exposure Limit Enforcement**
    - **Validates: Requirements 19.2, 19.5**
    - _Requirements: 19.2, 19.5_
  
  - [ ]* 19.7 Write unit tests for risk controls
    - Test position size limit at boundary
    - Test sector exposure with multiple positions
    - Test total exposure limit
    - Test position size adjustment
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_

- [ ] 20. Implement portfolio manager
  - [ ] 20.1 Create PortfolioManager class in manager.py
    - Implement __init__ with graph, initial_capital, risk limits, and position_sizing_method parameters
    - Initialize Portfolio, RiskControls, and position sizing configuration
    - _Requirements: 17.1, 19.9_
  
  - [ ] 20.2 Implement single stock analysis
    - Implement analyze_stock method (run graph.propagate for one ticker)
    - Return TradingSignal
    - _Requirements: 17.2_
  
  - [ ] 20.3 Implement multi-stock analysis
    - Implement analyze_portfolio method (run analysis for multiple tickers)
    - Return dict mapping ticker to TradingSignal
    - Support parallel execution for multiple stocks
    - _Requirements: 17.3, 17.6_
  
  - [ ] 20.4 Implement signal execution with risk controls
    - Implement execute_signals method (process signals with risk checks)
    - Call check_risk_limits for each signal
    - Apply position sizing algorithm based on configuration
    - Execute trades that pass risk checks
    - Log rejected trades with reasons
    - Return list of executed trades
    - _Requirements: 18.4, 18.5, 18.6, 18.8, 19.4, 19.5, 19.6, 19.7, 19.8_
  
  - [ ] 20.5 Implement portfolio summary
    - Implement get_portfolio_summary method (return current state and metrics)
    - Include positions, values, allocations, cash, total value
    - Calculate portfolio-level metrics (total_return, exposure_pct)
    - _Requirements: 17.4, 17.5_
  
  - [ ]* 20.6 Write unit tests for portfolio manager
    - Test single stock analysis
    - Test multi-stock analysis
    - Test signal execution with risk controls
    - Test portfolio summary generation
    - _Requirements: 17.2, 17.3, 17.4, 17.5, 18.8, 19.4, 19.5, 19.6_

- [ ] 21. Implement portfolio rebalancing
  - [ ] 21.1 Create rebalancing.py module
    - Implement rebalance_portfolio method in PortfolioManager
    - Accept target_allocations dict (ticker -> target_pct)
    - Calculate current allocations
    - Generate BUY/SELL orders to move toward targets
    - Respect risk limits during rebalancing
    - _Requirements: 20.1, 20.4, 20.5, 20.6_
  
  - [ ] 21.2 Implement rebalancing triggers
    - Support periodic rebalancing (daily, weekly, monthly)
    - Support threshold-based rebalancing (when drift exceeds threshold)
    - _Requirements: 20.2, 20.3_
  
  - [ ] 21.3 Add rebalancing logging
    - Log all rebalancing actions with before/after allocations
    - _Requirements: 20.7_
  
  - [ ] 21.4 Handle missing target allocations
    - Default to equal-weight allocation when targets not specified
    - _Requirements: 20.8_
  
  - [ ]* 21.5 Write unit tests for rebalancing
    - Test rebalancing to target allocations
    - Test periodic rebalancing
    - Test threshold-based rebalancing
    - Test equal-weight default
    - Test risk limit compliance during rebalancing
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8_

- [ ] 22. Checkpoint - Phase 5 portfolio management complete
  - Ensure all tests pass, test multi-stock portfolio with risk controls, ask the user if questions arise.



### Phase 6: Dashboard - Web-Based Monitoring and Visualization

- [ ] 23. Set up Streamlit dashboard application
  - [ ] 23.1 Create dashboard directory structure
    - Create dashboard/app.py (main application)
    - Create dashboard/pages/ directory for page modules
    - Create dashboard/components/ directory for reusable components
    - Create dashboard/utils/ directory for utilities
    - _Requirements: 23.1, 23.2_
  
  - [ ] 23.2 Implement main dashboard app
    - Create app.py with Streamlit page configuration
    - Add navigation sidebar with page selection
    - Add Chanana Quant branding and logo
    - Configure theme (light/dark support)
    - Add error handling with user-friendly messages
    - _Requirements: 23.1, 23.2, 23.3, 23.6, 23.7_
  
  - [ ] 23.3 Create reusable chart components
    - Create components/charts.py with Plotly chart functions
    - Implement create_portfolio_value_chart (line chart with hover tooltips)
    - Implement create_allocation_pie_chart (pie chart for allocations)
    - Implement create_performance_bar_chart (bar chart for metrics comparison)
    - _Requirements: 23.5_
  
  - [ ] 23.4 Create formatting utilities
    - Create utils/formatting.py with data formatting functions
    - Implement format_currency (rupee symbol, thousand separators)
    - Implement format_percentage (with sign and decimals)
    - Implement format_date (consistent date display)
    - _Requirements: 25.10_

- [ ] 24. Implement Live Analysis dashboard page
  - [ ] 24.1 Create pages/live_analysis.py
    - Add page title and description
    - Create input form with ticker, analysis_date, llm_provider, analyst selection
    - Add "Run Analysis" button
    - _Requirements: 24.1, 24.2_
  
  - [ ] 24.2 Implement analysis execution
    - Initialize TradingSystem with selected configuration on button click
    - Execute graph.propagate() with spinner ("Running analysis...")
    - Handle errors gracefully with error messages
    - _Requirements: 24.2, 24.7, 24.8_
  
  - [ ] 24.3 Display analysis results
    - Display trading signal with action, confidence, position_size_pct in metric cards
    - Display primary_reason in highlighted box
    - Create tabs for Market, Sentiment, News, Fundamentals reports
    - Display research team debate with bull/bear arguments
    - _Requirements: 24.3, 24.4, 24.5, 24.6_
  
  - [ ]* 24.4 Write unit tests for live analysis page components
    - Test input validation
    - Test result display formatting
    - Test error handling
    - _Requirements: 24.1, 24.2, 24.3, 24.7_

- [ ] 25. Implement Backtesting dashboard page
  - [ ] 25.1 Create pages/backtesting.py
    - Add page title and description
    - Create input form with ticker, start_date, end_date, initial_capital, frequency
    - Add "Run Backtest" button
    - _Requirements: 25.1, 25.2_
  
  - [ ] 25.2 Implement backtest execution
    - Initialize BacktestEngine with configuration on button click
    - Execute backtest with spinner ("Running backtest...")
    - Handle errors gracefully
    - _Requirements: 25.2, 25.9_
  
  - [ ] 25.3 Display performance metrics
    - Display metrics in 4-column grid layout
    - Show total_return, CAGR, Sharpe_Ratio, Max_Drawdown, win_rate, profit_factor, total_trades, final_value
    - Format currency and percentage values
    - _Requirements: 25.3, 25.4, 25.10_
  
  - [ ] 25.4 Display portfolio value chart
    - Create interactive Plotly line chart of portfolio value over time
    - Add hover tooltips with date and value
    - _Requirements: 25.5, 25.6_
  
  - [ ] 25.5 Display trade history table
    - Create table with date, action, ticker, quantity, price, profit/loss columns
    - Format currency values with rupee symbol
    - Color code profit (green) and loss (red)
    - _Requirements: 25.7, 25.8_
  
  - [ ]* 25.6 Write unit tests for backtesting page components
    - Test input validation
    - Test metrics display formatting
    - Test chart generation
    - Test trade history table
    - _Requirements: 25.1, 25.3, 25.4, 25.7, 25.10_

- [ ] 26. Implement Experiments dashboard page
  - [ ] 26.1 Create pages/experiments.py
    - Add page title and description
    - List all available experiments with name and experiment_id
    - Add multiselect widget to choose experiments for comparison
    - Default to selecting 3 most recent experiments
    - _Requirements: 26.1, 26.2, 26.9_
  
  - [ ] 26.2 Display experiment comparison
    - Display comparison table with metrics for all selected experiments when experiments are selected
    - Create interactive Plotly bar charts comparing Sharpe_Ratio and win_rate
    - Highlight best performers for each metric
    - _Requirements: 26.3, 26.4, 26.5_
  
  - [ ] 26.3 Implement comparison report generation
    - Add "Generate Comparison Report" button
    - Create markdown report using ExperimentComparison.generate_comparison_report
    - Add download button to save report
    - _Requirements: 26.6, 26.7_
  
  - [ ] 26.4 Handle empty experiments
    - Display info message when no experiments exist
    - Prompt user to run analyses first
    - _Requirements: 26.8_
  
  - [ ]* 26.5 Write unit tests for experiments page components
    - Test experiment listing
    - Test comparison table generation
    - Test report generation
    - Test empty state handling
    - _Requirements: 26.1, 26.2, 26.3, 26.8_

- [ ] 27. Implement Portfolio dashboard page
  - [ ] 27.1 Create pages/portfolio.py
    - Add page title and description
    - Display current cash balance and total portfolio value in metric cards
    - Add "Refresh" button to reload data
    - _Requirements: 27.1, 27.7_
  
  - [ ] 27.2 Display positions table
    - Create table with ticker, quantity, entry_price, current_price, current_value, profit/loss columns
    - Color code profit (green) and loss (red)
    - _Requirements: 27.2, 27.6_
  
  - [ ] 27.3 Display allocation charts
    - Create pie chart showing allocation by ticker
    - Create pie chart showing allocation by sector
    - Use Plotly for interactive charts
    - _Requirements: 27.3, 27.4_
  
  - [ ] 27.4 Display portfolio-level metrics
    - Calculate and display total_return and current_exposure_pct
    - _Requirements: 27.5_
  
  - [ ] 27.5 Handle empty portfolio
    - Display message when no positions exist
    - _Requirements: 27.8_
  
  - [ ]* 27.6 Write unit tests for portfolio page components
    - Test positions table display
    - Test allocation chart generation
    - Test metrics calculation
    - Test empty state handling
    - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5, 27.8_

- [ ] 28. Integrate dashboard with CLI
  - [ ] 28.1 Add dashboard command to CLI
    - Update cli/main.py with dashboard command
    - Launch Streamlit app when command is invoked
    - Pass configuration parameters (port, theme)
    - _Requirements: 23.3_
  
  - [ ] 28.2 Verify dashboard performance
    - Test dashboard loads in less than 5 seconds
    - Test all pages are accessible
    - Test navigation works correctly
    - _Requirements: 23.4_

- [ ] 29. Checkpoint - Phase 6 dashboard complete
  - Ensure all pages work correctly, test end-to-end user flows, ask the user if questions arise.



### Cross-Cutting: CLI, Integration, and Quality

- [ ] 30. Implement CLI commands for backtesting and experiments
  - [ ] 30.1 Add backtest CLI command
    - Create backtest command in cli/main.py
    - Accept ticker, start_date, end_date, initial_capital, frequency parameters
    - Prompt user to select LLM provider, analysts, and configuration
    - Initialize TradingSystem and BacktestEngine
    - Run backtest with progress indicators
    - Display performance metrics in formatted table
    - Save results to timestamped directory
    - Handle errors with user-friendly messages
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9_
  
  - [ ] 30.2 Add experiment management CLI commands
    - Create experiments list command (display all experiments with ID, name, date, key metrics)
    - Create experiments compare command (accept multiple IDs, generate comparison report)
    - Create experiments show command (display detailed info for single experiment)
    - Highlight best performers in comparison table
    - Save comparison reports to markdown file
    - Provide option to export results to CSV
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7_
  
  - [ ]* 30.3 Write integration tests for CLI commands
    - Test backtest command end-to-end
    - Test experiment commands
    - Test error handling
    - _Requirements: 21.1, 21.9, 22.1, 22.2, 22.3_

- [ ] 31. Ensure backward compatibility and system integration
  - [ ] 31.1 Verify LangGraph workflow preservation
    - Ensure existing analyst, researcher, trader, risk management nodes unchanged
    - Ensure Agent_State structure preserved with all existing fields
    - Ensure Memory_System using BM25 retrieval still functions
    - Ensure data vendor routing system unchanged
    - _Requirements: 28.1, 28.2, 28.4, 28.5_
  
  - [ ] 31.2 Verify LLM provider support
    - Test with OpenAI, Anthropic, Google, xAI, OpenRouter, Ollama
    - Ensure all providers work with new features
    - _Requirements: 28.3_
  
  - [ ] 31.3 Implement dual signal storage
    - Store both structured and text-based signals in AgentState
    - Ensure backward compatibility with existing code expecting text signals
    - _Requirements: 28.6_
  
  - [ ] 31.4 Make macro analyst optional
    - Add enable_macro_analyst configuration flag
    - Ensure system functions with original workflow when disabled
    - _Requirements: 28.7_
  
  - [ ] 31.5 Preserve existing CLI and output formats
    - Ensure existing CLI interface for single-stock analysis unchanged
    - Ensure eval_results directory structure preserved
    - _Requirements: 28.8, 28.9_
  
  - [ ]* 31.6 Write backward compatibility integration tests
    - Test existing single-stock analysis workflow
    - Verify output format unchanged
    - Verify eval_results structure preserved
    - Test with macro analyst disabled
    - Test memory system functionality
    - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.5, 28.6, 28.7, 28.8, 28.9, 28.10_

- [ ] 32. Implement data caching and performance optimization
  - [ ] 32.1 Implement market data caching
    - Cache market data in dataflows/data_cache/ directory
    - Reuse cached data for same ticker and date range
    - Implement cache expiration (24 hours for daily data)
    - _Requirements: 29.1, 29.2, 29.3, 29.4_
  
  - [ ] 32.2 Optimize backtesting data fetching
    - Batch data fetching requests for long date ranges
    - Display progress indicators during data-intensive operations
    - _Requirements: 29.5, 29.6_
  
  - [ ] 32.3 Implement rate limiting and retry logic
    - Handle rate limiting from data vendors gracefully
    - Implement exponential backoff retry logic
    - _Requirements: 29.7_
  
  - [ ] 32.4 Add cache monitoring
    - Log cache hits and misses for performance monitoring
    - _Requirements: 29.8_
  
  - [ ]* 32.5 Write unit tests for caching
    - Test cache storage and retrieval
    - Test cache expiration
    - Test batch fetching
    - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

- [ ] 33. Implement comprehensive error handling and logging
  - [ ] 33.1 Implement data fetching error handling
    - Add try-except blocks for data fetching with fallback sources
    - Log errors and attempt fallback data sources
    - _Requirements: 30.1_
  
  - [ ] 33.2 Implement LLM API error handling
    - Add retry logic with exponential backoff (up to 3 retries)
    - Handle rate limiting and timeout errors
    - _Requirements: 30.2_
  
  - [ ] 33.3 Implement structured output fallback
    - Fall back to text-based extraction when structured output fails
    - Log warnings for fallback occurrences
    - _Requirements: 30.3_
  
  - [ ] 33.4 Implement backtesting error handling
    - Continue with remaining dates when error occurs on specific date
    - Log errors with full context
    - _Requirements: 30.4_
  
  - [ ] 33.5 Implement risk limit violation logging
    - Log all risk limit violations with details (ticker, size, limit, violation type)
    - _Requirements: 30.5_
  
  - [ ] 33.6 Configure logging system
    - Support configurable log levels (DEBUG, INFO, WARNING, ERROR)
    - Write logs to both console and file
    - Include timestamps, component names, and context in log messages
    - Add --debug flag to CLI commands for verbose logging
    - Capture and log all exceptions with full stack traces
    - _Requirements: 30.6, 30.7, 30.8, 30.9, 30.10_
  
  - [ ]* 33.7 Write unit tests for error handling
    - Test data fetching fallback
    - Test LLM retry logic
    - Test structured output fallback
    - Test backtesting error recovery
    - _Requirements: 30.1, 30.2, 30.3, 30.4_

- [ ] 34. Implement configuration management and validation
  - [ ] 34.1 Update default_config.py with new parameters
    - Add all Phase 1-6 configuration parameters
    - Document each parameter with comments
    - Provide default values for all optional parameters
    - _Requirements: 31.3, 31.4_
  
  - [ ] 34.2 Implement configuration validation
    - Create validate_config function
    - Validate all parameters on initialization
    - Validate selected analysts exist
    - Validate LLM provider is supported
    - Validate required API keys are set
    - Validate date formats (YYYY-MM-DD)
    - Validate start_date is before end_date
    - Provide descriptive error messages for invalid values
    - _Requirements: 31.1, 31.2, 31.5, 31.6, 31.7, 31.8, 31.9, 31.10_
  
  - [ ]* 34.3 Write unit tests for configuration validation
    - Test with invalid LLM provider
    - Test with unknown analysts
    - Test with missing API keys
    - Test with invalid date formats
    - Test with start_date after end_date
    - _Requirements: 31.1, 31.2, 31.5, 31.6, 31.7, 31.8, 31.9_

- [ ] 35. Create comprehensive documentation
  - [ ] 35.1 Write README for structured signals
    - Document TradingSignal schema
    - Provide code examples for signal processing
    - Explain validation rules
    - _Requirements: 32.1_
  
  - [ ] 35.2 Write README for backtesting
    - Document CLI usage with examples
    - Document Python API usage
    - Explain performance metrics
    - _Requirements: 32.2_
  
  - [ ] 35.3 Write README for experiment tracking
    - Document experiment creation and configuration
    - Provide usage examples
    - Explain comparison features
    - _Requirements: 32.3_
  
  - [ ] 35.4 Write README for portfolio management
    - Document portfolio manager configuration
    - Explain position sizing methods
    - Explain risk controls
    - Provide configuration examples
    - _Requirements: 32.4_
  
  - [ ] 35.5 Write README for dashboard
    - Document dashboard launch and usage
    - Include screenshots of each page
    - Explain features and navigation
    - _Requirements: 32.5_
  
  - [ ] 35.6 Add docstrings to all public classes and methods
    - Follow Google docstring format
    - Include parameter descriptions and return types
    - Add usage examples where helpful
    - _Requirements: 32.6_
  
  - [ ] 35.7 Create example scripts
    - Create examples/ directory
    - Add example for backtesting
    - Add example for experiment tracking
    - Add example for portfolio management
    - _Requirements: 32.7_
  
  - [ ] 35.8 Document configuration parameters
    - Create configuration reference document
    - List all parameters with descriptions and defaults
    - _Requirements: 32.8_
  
  - [ ] 35.9 Create migration guide
    - Document upgrade process for existing users
    - Explain backward compatibility features
    - Provide step-by-step migration instructions
    - _Requirements: 32.9_
  
  - [ ] 35.10 Add troubleshooting section
    - Document common issues and solutions
    - Include debugging tips
    - _Requirements: 32.10_

- [ ] 36. Update dependencies and installation
  - [ ] 36.1 Update requirements.txt
    - Add numpy, streamlit, plotly, hypothesis
    - Specify minimum versions
    - Document Python 3.10+ requirement
    - _Requirements: 34.1, 34.2_
  
  - [ ] 36.2 Create setup verification script
    - Create chanana_quant/verify_setup.py
    - Check Python version
    - Check required packages
    - Check API keys
    - Check directories
    - Test data fetching
    - Test LLM connection
    - Display verification results
    - _Requirements: 34.5_
  
  - [ ] 36.3 Update installation instructions
    - Document installation steps in README
    - Document system-level dependencies
    - Provide Docker configuration (optional)
    - _Requirements: 34.3, 34.6, 34.7_
  
  - [ ] 36.4 Ensure importability
    - Verify all new modules are importable after pip install
    - Test in fresh virtual environment
    - _Requirements: 34.4_
  
  - [ ] 36.5 Create changelog
    - Document all new features and changes
    - Organize by phase
    - Include migration notes
    - _Requirements: 34.10_

- [ ] 37. Final checkpoint - System integration and testing
  - Run full test suite (unit, property, integration tests)
  - Verify all 34 requirements are satisfied
  - Test backward compatibility with existing workflows
  - Run end-to-end scenarios for all 6 phases
  - Verify documentation is complete and accurate
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability (format: _Requirements: X.Y_)
- Checkpoints ensure incremental validation at the end of each phase
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a phased approach: Foundation → Macro → Backtesting → Experiments → Portfolio → Dashboard → Cross-Cutting
- Backward compatibility is maintained throughout all phases
- Each phase delivers independent value and can be deployed separately

## Implementation Timeline Estimate

- Phase 1 (Foundation): 2-3 days
- Phase 2 (Macro Awareness): 3-4 days
- Phase 3 (Backtesting): 4-5 days
- Phase 4 (Experiments): 2-3 days
- Phase 5 (Portfolio): 4-5 days
- Phase 6 (Dashboard): 5-6 days
- Cross-Cutting (CLI, Integration, Quality): 4-5 days

**Total: 24-31 days**

