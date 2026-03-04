"""Tests for Phase 1: Structured Signals and Indian Market Support."""

import pytest
from datetime import datetime
from chanana_quant.agents.utils.agent_states import TradingSignal
from chanana_quant.graph.signal_processing import SignalProcessor, SignalValidationResult
from chanana_quant.dataflows.indian_market_utils import (
    normalize_indian_ticker,
    is_indian_ticker,
    is_indian_market_open,
    get_next_trading_day,
    get_indian_sector,
    get_sector_peers,
)


class TestTradingSignal:
    """Test TradingSignal schema and validation."""
    
    def test_valid_buy_signal(self):
        """Test creating a valid BUY signal."""
        signal = TradingSignal(
            action="BUY",
            confidence=0.8,
            position_size_pct=10.0,
            stop_loss_pct=5.0,
            take_profit_pct=15.0,
            holding_period_days=30,
            primary_reason="Strong fundamentals and technical breakout",
            supporting_factors=["Revenue growth", "Positive momentum"],
            risk_factors=["Market volatility"],
            ticker="RELIANCE.NS",
            analysis_date="2024-03-01"
        )
        
        assert signal.action == "BUY"
        assert signal.confidence == 0.8
        assert signal.position_size_pct == 10.0
    
    def test_invalid_action(self):
        """Test that invalid action raises error."""
        with pytest.raises(ValueError):
            TradingSignal(
                action="INVALID",
                confidence=0.5,
                position_size_pct=10.0,
                primary_reason="Test",
                ticker="TCS.NS",
                analysis_date="2024-03-01"
            )
    
    def test_confidence_bounds(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            TradingSignal(
                action="BUY",
                confidence=1.5,
                position_size_pct=10.0,
                primary_reason="Test",
                ticker="TCS.NS",
                analysis_date="2024-03-01"
            )
    
    def test_position_size_bounds(self):
        """Test position size must be between 0 and 100."""
        with pytest.raises(ValueError):
            TradingSignal(
                action="BUY",
                confidence=0.5,
                position_size_pct=150.0,
                primary_reason="Test",
                ticker="TCS.NS",
                analysis_date="2024-03-01"
            )


class TestSignalValidation:
    """Test signal validation logic."""
    
    def test_buy_with_zero_position_size_error(self):
        """Test BUY with 0% position size is invalid."""
        signal = TradingSignal(
            action="BUY",
            confidence=0.8,
            position_size_pct=0.0,
            primary_reason="Test",
            ticker="TCS.NS",
            analysis_date="2024-03-01"
        )
        
        # Create a mock LLM for SignalProcessor
        class MockLLM:
            def invoke(self, messages):
                class Response:
                    content = ""
                return Response()
        
        processor = SignalProcessor(MockLLM())
        result = processor.validate_signal(signal)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_high_stop_loss_warning(self):
        """Test warning for stop loss > 20%."""
        signal = TradingSignal(
            action="BUY",
            confidence=0.8,
            position_size_pct=10.0,
            stop_loss_pct=25.0,
            primary_reason="Test",
            ticker="TCS.NS",
            analysis_date="2024-03-01"
        )
        
        class MockLLM:
            def invoke(self, messages):
                class Response:
                    content = ""
                return Response()
        
        processor = SignalProcessor(MockLLM())
        result = processor.validate_signal(signal)
        
        assert result.is_valid  # Still valid, just warning
        assert len(result.warnings) > 0
    
    def test_take_profit_less_than_stop_loss_warning(self):
        """Test warning when take profit < stop loss."""
        signal = TradingSignal(
            action="BUY",
            confidence=0.8,
            position_size_pct=10.0,
            stop_loss_pct=10.0,
            take_profit_pct=5.0,
            primary_reason="Test",
            ticker="TCS.NS",
            analysis_date="2024-03-01"
        )
        
        class MockLLM:
            def invoke(self, messages):
                class Response:
                    content = ""
                return Response()
        
        processor = SignalProcessor(MockLLM())
        result = processor.validate_signal(signal)
        
        assert result.is_valid
        assert len(result.warnings) > 0


class TestTickerNormalization:
    """Test Indian ticker normalization."""
    
    def test_normalize_adds_ns_suffix(self):
        """Test that normalization adds .NS suffix."""
        assert normalize_indian_ticker("RELIANCE") == "RELIANCE.NS"
        assert normalize_indian_ticker("TCS") == "TCS.NS"
    
    def test_normalize_preserves_existing_suffix(self):
        """Test that existing suffixes are preserved."""
        assert normalize_indian_ticker("RELIANCE.NS") == "RELIANCE.NS"
        assert normalize_indian_ticker("TCS.BO") == "TCS.BO"
    
    def test_normalize_idempotence(self):
        """Test that normalizing twice gives same result."""
        ticker = "INFY"
        normalized_once = normalize_indian_ticker(ticker)
        normalized_twice = normalize_indian_ticker(normalized_once)
        assert normalized_once == normalized_twice
    
    def test_is_indian_ticker(self):
        """Test Indian ticker detection."""
        assert is_indian_ticker("RELIANCE.NS") == True
        assert is_indian_ticker("TCS.BO") == True
        assert is_indian_ticker("AAPL") == False
        assert is_indian_ticker("GOOGL") == False


class TestMarketCalendar:
    """Test Indian market calendar functions."""
    
    def test_weekend_closed(self):
        """Test that weekends are not trading days."""
        saturday = datetime(2024, 3, 2)  # Saturday
        sunday = datetime(2024, 3, 3)    # Sunday
        
        assert is_indian_market_open(saturday) == False
        assert is_indian_market_open(sunday) == False
    
    def test_weekday_open(self):
        """Test that regular weekdays are trading days."""
        monday = datetime(2024, 3, 4)  # Monday
        assert is_indian_market_open(monday) == True
    
    def test_holiday_closed(self):
        """Test that holidays are not trading days."""
        republic_day = datetime(2024, 1, 26)  # Republic Day
        assert is_indian_market_open(republic_day) == False
    
    def test_get_next_trading_day_skips_weekend(self):
        """Test that next trading day skips weekends."""
        friday = datetime(2024, 3, 1)  # Friday
        next_day = get_next_trading_day(friday)
        
        # Should skip Saturday and Sunday, land on Monday
        assert next_day.weekday() == 0  # Monday
        assert next_day.day == 4
    
    def test_get_next_trading_day_skips_holiday(self):
        """Test that next trading day skips holidays."""
        day_before_republic_day = datetime(2024, 1, 25)  # Thursday
        next_day = get_next_trading_day(day_before_republic_day)
        
        # Should skip Republic Day (26th, Friday) and weekend, land on Monday 29th
        assert next_day.day == 29


class TestSectorClassification:
    """Test Indian stock sector classification."""
    
    def test_get_sector_for_known_stocks(self):
        """Test sector classification for known stocks."""
        assert get_indian_sector("RELIANCE.NS") == "Energy"
        assert get_indian_sector("TCS") == "IT"
        assert get_indian_sector("HDFCBANK.NS") == "Banking"
    
    def test_get_sector_for_unknown_stock(self):
        """Test that unknown stocks return 'Unknown'."""
        assert get_indian_sector("UNKNOWN") == "Unknown"
    
    def test_get_sector_peers(self):
        """Test getting sector peers."""
        peers = get_sector_peers("TCS.NS", n=3)
        
        assert len(peers) <= 3
        assert "TCS" not in peers  # Should not include itself
        assert "INFY" in peers  # Should include other IT stocks
    
    def test_sector_peer_consistency(self):
        """Test that all peers are in the same sector."""
        ticker = "RELIANCE.NS"
        sector = get_indian_sector(ticker)
        peers = get_sector_peers(ticker, n=5)
        
        for peer in peers:
            peer_sector = get_indian_sector(peer)
            assert peer_sector == sector


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
