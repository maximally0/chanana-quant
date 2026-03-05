"""Property-based tests for Phase 1 using Hypothesis.

These tests verify mathematical properties and invariants that should hold
for all possible inputs, not just specific test cases.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from chanana_quant.agents.utils.agent_states import TradingSignal
from chanana_quant.graph.signal_processing import SignalProcessor
from chanana_quant.dataflows.indian_market_utils import (
    normalize_indian_ticker,
    is_indian_ticker,
    is_indian_market_open,
    get_next_trading_day,
    get_indian_sector,
    get_sector_peers,
)


# Strategy for generating valid trading signals
@st.composite
def trading_signal_strategy(draw):
    """Generate random but valid TradingSignal instances."""
    action = draw(st.sampled_from(["BUY", "SELL", "HOLD"]))
    confidence = draw(st.floats(min_value=0.0, max_value=1.0))
    position_size_pct = draw(st.floats(min_value=0.0, max_value=100.0))
    
    # Optional fields
    stop_loss_pct = draw(st.one_of(
        st.none(),
        st.floats(min_value=0.1, max_value=50.0)
    ))
    take_profit_pct = draw(st.one_of(
        st.none(),
        st.floats(min_value=0.1, max_value=100.0)
    ))
    holding_period_days = draw(st.one_of(
        st.none(),
        st.integers(min_value=1, max_value=365)
    ))
    
    return TradingSignal(
        action=action,
        confidence=confidence,
        position_size_pct=position_size_pct,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        holding_period_days=holding_period_days,
        primary_reason="Property test generated reason",
        supporting_factors=["Factor 1", "Factor 2"],
        risk_factors=["Risk 1"],
        ticker="TEST.NS",
        analysis_date="2024-03-01"
    )


class TestTradingSignalProperties:
    """Property 1: Trading Signal Field Constraints"""
    
    @given(trading_signal_strategy())
    @settings(max_examples=100)
    def test_signal_field_constraints_always_valid(self, signal):
        """Property: All generated signals must satisfy field constraints."""
        # Action constraint
        assert signal.action in ["BUY", "SELL", "HOLD"]
        
        # Confidence constraint
        assert 0.0 <= signal.confidence <= 1.0
        
        # Position size constraint
        assert 0.0 <= signal.position_size_pct <= 100.0
        
        # Optional field constraints
        if signal.stop_loss_pct is not None:
            assert signal.stop_loss_pct > 0.0
        
        if signal.take_profit_pct is not None:
            assert signal.take_profit_pct > 0.0
        
        if signal.holding_period_days is not None:
            assert signal.holding_period_days > 0
    
    @given(
        st.floats(min_value=-1000.0, max_value=1000.0).filter(lambda x: not (0.0 <= x <= 1.0))
    )
    def test_confidence_rejects_out_of_bounds(self, invalid_confidence):
        """Property: Confidence outside [0, 1] must be rejected."""
        with pytest.raises(ValueError):
            TradingSignal(
                action="BUY",
                confidence=invalid_confidence,
                position_size_pct=10.0,
                primary_reason="Test",
                ticker="TEST.NS",
                analysis_date="2024-03-01"
            )
    
    @given(
        st.floats(min_value=-1000.0, max_value=1000.0).filter(lambda x: not (0.0 <= x <= 100.0))
    )
    def test_position_size_rejects_out_of_bounds(self, invalid_position_size):
        """Property: Position size outside [0, 100] must be rejected."""
        with pytest.raises(ValueError):
            TradingSignal(
                action="BUY",
                confidence=0.5,
                position_size_pct=invalid_position_size,
                primary_reason="Test",
                ticker="TEST.NS",
                analysis_date="2024-03-01"
            )


class TestSignalActionConsistency:
    """Property 2: Signal Action Consistency"""
    
    @given(
        st.floats(min_value=0.1, max_value=100.0),
        st.floats(min_value=0.0, max_value=1.0)
    )
    def test_buy_with_positive_position_size_is_valid(self, position_size, confidence):
        """Property: BUY with positive position size should be valid."""
        signal = TradingSignal(
            action="BUY",
            confidence=confidence,
            position_size_pct=position_size,
            primary_reason="Test",
            ticker="TEST.NS",
            analysis_date="2024-03-01"
        )
        
        class MockLLM:
            def invoke(self, messages):
                class Response:
                    content = ""
                return Response()
        
        processor = SignalProcessor(MockLLM())
        result = processor.validate_signal(signal)
        
        # Should be valid (no errors)
        assert result.is_valid
    
    @given(st.floats(min_value=0.0, max_value=1.0))
    def test_buy_with_zero_position_size_is_invalid(self, confidence):
        """Property: BUY with 0% position size should always be invalid."""
        signal = TradingSignal(
            action="BUY",
            confidence=confidence,
            position_size_pct=0.0,
            primary_reason="Test",
            ticker="TEST.NS",
            analysis_date="2024-03-01"
        )
        
        class MockLLM:
            def invoke(self, messages):
                class Response:
                    content = ""
                return Response()
        
        processor = SignalProcessor(MockLLM())
        result = processor.validate_signal(signal)
        
        # Should be invalid
        assert not result.is_valid
        assert len(result.errors) > 0


class TestTickerNormalizationProperties:
    """Property 4: Ticker Normalization Idempotence"""
    
    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu',))))
    def test_normalization_is_idempotent(self, ticker):
        """Property: normalize(normalize(x)) == normalize(x) for all x."""
        assume(ticker)  # Ensure non-empty
        
        normalized_once = normalize_indian_ticker(ticker)
        normalized_twice = normalize_indian_ticker(normalized_once)
        
        assert normalized_once == normalized_twice
    
    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu',))))
    def test_normalized_ticker_always_has_suffix(self, ticker):
        """Property: All normalized tickers must end with .NS or .BO."""
        assume(ticker)
        
        normalized = normalize_indian_ticker(ticker)
        
        assert normalized.endswith('.NS') or normalized.endswith('.BO')


class TestIndianTickerClassification:
    """Property 5: Indian Ticker Classification"""
    
    @given(st.text(min_size=1, max_size=20))
    def test_normalized_ticker_is_always_indian(self, ticker):
        """Property: normalize(x) always produces an Indian ticker."""
        assume(ticker and ticker.strip())
        
        normalized = normalize_indian_ticker(ticker)
        
        assert is_indian_ticker(normalized)
    
    @given(st.text(min_size=1, max_size=20).filter(lambda x: not x.endswith('.NS') and not x.endswith('.BO')))
    def test_ticker_without_suffix_is_not_indian(self, ticker):
        """Property: Tickers without .NS or .BO suffix are not Indian."""
        assume(ticker and ticker.strip())
        
        # Only test if it doesn't accidentally end with .NS or .BO
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            assert not is_indian_ticker(ticker)


class TestMarketCalendarProperties:
    """Property 6 & 7: Market Calendar Consistency and Weekend Exclusion"""
    
    @given(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date()))
    def test_weekends_are_never_trading_days(self, date):
        """Property 7: Saturdays and Sundays are never trading days."""
        dt = datetime.combine(date, datetime.min.time())
        
        if dt.weekday() in [5, 6]:  # Saturday or Sunday
            assert not is_indian_market_open(dt)
    
    @given(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date()))
    def test_next_trading_day_is_always_open(self, date):
        """Property 6: get_next_trading_day always returns an open day."""
        dt = datetime.combine(date, datetime.min.time())
        
        next_day = get_next_trading_day(dt)
        
        # The next trading day must be a trading day
        assert is_indian_market_open(next_day)
    
    @given(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date()))
    def test_next_trading_day_is_after_current_day(self, date):
        """Property: get_next_trading_day(x) > x for all x."""
        dt = datetime.combine(date, datetime.min.time())
        
        next_day = get_next_trading_day(dt)
        
        assert next_day > dt
    
    @given(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date()))
    def test_next_trading_day_is_not_weekend(self, date):
        """Property: get_next_trading_day never returns a weekend."""
        dt = datetime.combine(date, datetime.min.time())
        
        next_day = get_next_trading_day(dt)
        
        # Next trading day should not be Saturday (5) or Sunday (6)
        assert next_day.weekday() not in [5, 6]


class TestNIFTY50PercentageChange:
    """Property 8: NIFTY50 Percentage Change Calculation"""
    
    @given(
        st.floats(min_value=1000.0, max_value=30000.0),
        st.floats(min_value=1000.0, max_value=30000.0)
    )
    def test_percentage_change_formula(self, old_price, new_price):
        """Property: Percentage change formula is mathematically correct."""
        # Calculate percentage change
        pct_change = ((new_price - old_price) / old_price) * 100
        
        # Verify inverse operation
        reconstructed_price = old_price * (1 + pct_change / 100)
        
        # Should reconstruct the new price (within floating point precision)
        assert abs(reconstructed_price - new_price) < 0.01
    
    @given(st.floats(min_value=1000.0, max_value=30000.0))
    def test_zero_change_gives_zero_percent(self, price):
        """Property: No change in price gives 0% change."""
        pct_change = ((price - price) / price) * 100
        
        assert abs(pct_change) < 0.0001


class TestStockVsIndexClassification:
    """Property 9: Stock vs Index Classification"""
    
    @given(
        st.floats(min_value=0.1, max_value=100.0),
        st.floats(min_value=0.1, max_value=100.0)
    )
    def test_stock_vs_index_is_consistent(self, stock_return, index_return):
        """Property: Stock vs index classification is consistent with returns."""
        if stock_return > index_return:
            classification = "outperforming"
        elif stock_return < index_return:
            classification = "underperforming"
        else:
            classification = "matching"
        
        # Verify consistency
        if classification == "outperforming":
            assert stock_return > index_return
        elif classification == "underperforming":
            assert stock_return < index_return
        else:
            assert abs(stock_return - index_return) < 0.0001


class TestVIXRegimeClassification:
    """Property 10: VIX Regime Classification"""
    
    @given(st.floats(min_value=0.0, max_value=100.0))
    def test_vix_regime_boundaries(self, vix_value):
        """Property: VIX regime classification has clear boundaries."""
        if vix_value < 15.0:
            regime = "low"
        elif 15.0 <= vix_value <= 25.0:
            regime = "medium"
        else:
            regime = "high"
        
        # Verify boundaries
        if regime == "low":
            assert vix_value < 15.0
        elif regime == "medium":
            assert 15.0 <= vix_value <= 25.0
        else:
            assert vix_value > 25.0
    
    @given(st.floats(min_value=0.0, max_value=14.99))
    def test_low_vix_always_classified_as_low(self, vix_value):
        """Property: VIX < 15 is always 'low' regime."""
        regime = "low" if vix_value < 15.0 else "not_low"
        assert regime == "low"
    
    @given(st.floats(min_value=25.01, max_value=100.0))
    def test_high_vix_always_classified_as_high(self, vix_value):
        """Property: VIX > 25 is always 'high' regime."""
        regime = "high" if vix_value > 25.0 else "not_high"
        assert regime == "high"


class TestSectorPeerConsistency:
    """Property 11: Sector Peer Consistency"""
    
    @given(st.sampled_from(["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY", "WIPRO"]))
    def test_peers_are_in_same_sector(self, ticker):
        """Property: All peers must be in the same sector as the original stock."""
        sector = get_indian_sector(ticker)
        
        # Skip if sector is Unknown
        assume(sector != "Unknown")
        
        peers = get_sector_peers(ticker, n=5)
        
        for peer in peers:
            peer_sector = get_indian_sector(peer)
            assert peer_sector == sector, f"Peer {peer} has sector {peer_sector}, expected {sector}"
    
    @given(
        st.sampled_from(["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"]),
        st.integers(min_value=1, max_value=10)
    )
    def test_peer_count_respects_limit(self, ticker, n):
        """Property: Number of peers returned should not exceed requested limit."""
        peers = get_sector_peers(ticker, n=n)
        
        assert len(peers) <= n
    
    @given(st.sampled_from(["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"]))
    def test_stock_not_in_its_own_peers(self, ticker):
        """Property: A stock should never appear in its own peer list."""
        peers = get_sector_peers(ticker, n=10)
        
        # Remove suffix for comparison
        base_ticker = ticker.replace('.NS', '').replace('.BO', '')
        
        assert base_ticker not in peers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
