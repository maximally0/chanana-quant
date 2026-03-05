import time
import json
from typing import Optional
from chanana_quant.agents.utils.agent_states import TradingSignal


def create_risk_manager(llm, memory, use_structured_output: bool = False):
    """Create risk manager node.
    
    Args:
        llm: Language model for generating decisions
        memory: Memory system for past decisions
        use_structured_output: If True, output structured TradingSignal (Phase 1 upgrade)
    """
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Aggressive, Neutral, and Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

Deliverables:
- A clear and actionable recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the debate and past reflections.

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes."""

        # Generate response
        if use_structured_output:
            # Phase 1 upgrade: Use structured output
            try:
                structured_llm = llm.with_structured_output(TradingSignal)
                
                # Enhanced prompt for structured output
                structured_prompt = prompt + f"""

---

**IMPORTANT**: Provide your decision in the following structured format:
- action: BUY, SELL, or HOLD
- confidence: 0.0 to 1.0 (how confident are you in this decision)
- position_size_pct: 0 to 100 (recommended position size as % of portfolio, 0 for HOLD/SELL)
- stop_loss_pct: optional, % below entry to exit (e.g., 5.0 for 5%)
- take_profit_pct: optional, % above entry to exit (e.g., 10.0 for 10%)
- holding_period_days: optional, expected holding period in days
- primary_reason: main reason for your decision (one sentence)
- supporting_factors: list of 2-3 key supporting factors
- risk_factors: list of 2-3 key risks to monitor

Ticker: {company_name}
Analysis Date: {state['trade_date']}
"""
                
                trading_signal = structured_llm.invoke(structured_prompt)
                response_content = f"**Decision: {trading_signal.action}** (Confidence: {trading_signal.confidence:.1%})\n\n"
                response_content += f"**Position Size**: {trading_signal.position_size_pct}% of portfolio\n\n"
                response_content += f"**Primary Reason**: {trading_signal.primary_reason}\n\n"
                
                if trading_signal.supporting_factors:
                    response_content += "**Supporting Factors**:\n"
                    for factor in trading_signal.supporting_factors:
                        response_content += f"- {factor}\n"
                    response_content += "\n"
                
                if trading_signal.risk_factors:
                    response_content += "**Risk Factors**:\n"
                    for risk in trading_signal.risk_factors:
                        response_content += f"- {risk}\n"
                    response_content += "\n"
                
                if trading_signal.stop_loss_pct:
                    response_content += f"**Stop Loss**: {trading_signal.stop_loss_pct}%\n"
                if trading_signal.take_profit_pct:
                    response_content += f"**Take Profit**: {trading_signal.take_profit_pct}%\n"
                
            except Exception as e:
                # Fallback to text-based output if structured output fails
                print(f"Warning: Structured output failed, falling back to text: {e}")
                response = llm.invoke(prompt)
                response_content = response.content
                trading_signal = None
        else:
            # Original behavior: text-based output
            response = llm.invoke(prompt)
            response_content = response.content
            trading_signal = None

        new_risk_debate_state = {
            "judge_decision": response_content,
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        result = {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response_content,
        }
        
        # Add structured signal if Phase 1 upgrade is active
        if use_structured_output and trading_signal is not None:
            result["trading_signal"] = trading_signal
        
        return result

    return risk_manager_node
