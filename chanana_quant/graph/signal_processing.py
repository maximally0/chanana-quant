"""Signal processing and validation for trading signals."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chanana_quant.agents.utils.agent_states import TradingSignal

logger = logging.getLogger(__name__)


class SignalValidationResult:
    """Result of signal validation."""
    
    def __init__(self, is_valid: bool, warnings: list[str] = None, errors: list[str] = None):
        self.is_valid = is_valid
        self.warnings = warnings or []
        self.errors = errors or []
    
    def __repr__(self):
        return f"SignalValidationResult(is_valid={self.is_valid}, warnings={len(self.warnings)}, errors={len(self.errors)})"


class SignalProcessor:
    """Processes and validates trading signals."""
    
    def __init__(self, llm):
        """Initialize signal processor with LLM for fallback extraction.
        
        Args:
            llm: Language model for fallback text extraction
        """
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=TradingSignal)
    
    def process_signal(
        self, 
        final_decision_text: str, 
        ticker: str, 
        analysis_date: str,
        structured_signal: Optional[TradingSignal] = None
    ) -> TradingSignal:
        """Process and extract trading signal from text or structured output.
        
        Args:
            final_decision_text: Text-based trading decision
            ticker: Stock ticker symbol
            analysis_date: Date of analysis
            structured_signal: Pre-extracted structured signal (if available)
        
        Returns:
            TradingSignal object
        """
        # If structured signal already provided, use it
        if structured_signal:
            logger.info("Using pre-extracted structured signal")
            return structured_signal
        
        # Try to extract structured signal from text using LLM
        logger.info("Attempting LLM-based signal extraction from text")
        try:
            signal = self._extract_signal_from_text(final_decision_text, ticker, analysis_date)
            logger.info(f"Successfully extracted signal: {signal.action} with confidence {signal.confidence}")
            return signal
        except Exception as e:
            logger.error(f"Failed to extract structured signal: {e}")
            # Return a default HOLD signal as fallback
            return TradingSignal(
                action="HOLD",
                confidence=0.0,
                position_size_pct=0.0,
                primary_reason="Failed to extract signal from text",
                ticker=ticker,
                analysis_date=analysis_date,
                supporting_factors=[],
                risk_factors=["Signal extraction failed"]
            )
    
    def _extract_signal_from_text(self, text: str, ticker: str, analysis_date: str) -> TradingSignal:
        """Extract structured signal from free-form text using LLM.
        
        Args:
            text: Free-form trading decision text
            ticker: Stock ticker symbol
            analysis_date: Date of analysis
        
        Returns:
            TradingSignal object
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a trading signal extraction expert. Extract structured trading information from the given text.
            
{format_instructions}

Extract the following:
- action: BUY, SELL, or HOLD
- confidence: 0.0 to 1.0 (how confident is the decision)
- position_size_pct: 0 to 100 (recommended position size as % of portfolio)
- stop_loss_pct: optional, % below entry to exit (e.g., 5.0 for 5%)
- take_profit_pct: optional, % above entry to exit (e.g., 10.0 for 10%)
- holding_period_days: optional, expected holding period
- primary_reason: main reason for the decision
- supporting_factors: list of supporting factors
- risk_factors: list of key risks

Be conservative with confidence and position sizing if not explicitly stated."""),
            ("user", "Trading Decision Text:\n{text}\n\nTicker: {ticker}\nAnalysis Date: {analysis_date}")
        ])
        
        formatted_prompt = prompt.format_messages(
            format_instructions=self.parser.get_format_instructions(),
            text=text,
            ticker=ticker,
            analysis_date=analysis_date
        )
        
        response = self.llm.invoke(formatted_prompt)
        signal = self.parser.parse(response.content)
        
        # Ensure metadata is set
        signal.ticker = ticker
        signal.analysis_date = analysis_date
        signal.timestamp = datetime.now()
        
        return signal
    
    def validate_signal(self, signal: TradingSignal) -> SignalValidationResult:
        """Validate trading signal for consistency and reasonableness.
        
        Args:
            signal: TradingSignal to validate
        
        Returns:
            SignalValidationResult with validation status and messages
        """
        warnings = []
        errors = []
        
        # Check action-position_size consistency
        if signal.action == "BUY" and signal.position_size_pct == 0.0:
            errors.append("BUY action with 0% position size is inconsistent")
        
        if signal.action == "SELL" and signal.position_size_pct > 0.0:
            warnings.append("SELL action typically should have 0% position size (closing position)")
        
        if signal.action == "HOLD" and signal.position_size_pct > 0.0:
            warnings.append("HOLD action with non-zero position size is unusual")
        
        # Check stop loss reasonableness
        if signal.stop_loss_pct is not None:
            if signal.stop_loss_pct > 20.0:
                warnings.append(f"Stop loss of {signal.stop_loss_pct}% is very wide (>20%)")
            if signal.stop_loss_pct < 0.0:
                errors.append(f"Stop loss cannot be negative: {signal.stop_loss_pct}%")
        
        # Check take profit vs stop loss
        if signal.stop_loss_pct is not None and signal.take_profit_pct is not None:
            if signal.take_profit_pct < signal.stop_loss_pct:
                warnings.append(
                    f"Take profit ({signal.take_profit_pct}%) is less than stop loss ({signal.stop_loss_pct}%), "
                    "resulting in poor risk/reward ratio"
                )
        
        # Check HOLD with high confidence
        if signal.action == "HOLD" and signal.confidence > 0.7:
            warnings.append(
                f"HOLD action with high confidence ({signal.confidence}) is unusual - "
                "consider BUY or SELL if conviction is strong"
            )
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"Signal validation warning: {warning}")
        
        for error in errors:
            logger.error(f"Signal validation error: {error}")
        
        is_valid = len(errors) == 0
        return SignalValidationResult(is_valid=is_valid, warnings=warnings, errors=errors)
