"""Trading system orchestrator for multi-agent market analysis."""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class TradingState(TypedDict):
    """State for the trading multi-agent system."""
    ticker: str
    messages: List[BaseMessage]
    news_analysis: Dict[str, Any]
    social_analysis: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    final_recommendation: Dict[str, Any]


class TradingSystem:
    """Multi-agent trading system coordinator."""

    def __init__(self):
        """Initialize the trading system."""
        self.graph = self._create_graph()

    def _create_graph(self):
        """Create the state graph for the trading system."""
        from .agents import NewsAgent, SocialAgent, TechnicalAgent

        # Initialize agents
        news_agent = NewsAgent()
        social_agent = SocialAgent()
        technical_agent = TechnicalAgent()

        # Create workflow
        workflow = StateGraph(TradingState)

        # Add nodes
        workflow.add_node("news_analysis", news_agent.analyze)
        workflow.add_node("social_analysis", social_agent.analyze)
        workflow.add_node("technical_analysis", technical_agent.analyze)
        workflow.add_node("synthesize", self._synthesize_results)

        # Add edges - sequential to avoid concurrent updates
        workflow.add_edge(START, "news_analysis")
        workflow.add_edge("news_analysis", "social_analysis")
        workflow.add_edge("social_analysis", "technical_analysis")
        workflow.add_edge("technical_analysis", "synthesize")

        workflow.add_edge("synthesize", END)

        return workflow.compile()

    def _synthesize_results(self, state: TradingState) -> TradingState:
        """Synthesize results from all agents into a final recommendation."""
        ticker = state["ticker"]
        news = state.get("news_analysis", {})
        social = state.get("social_analysis", {})
        technical = state.get("technical_analysis", {})

        # Simple synthesis logic
        sentiment_score = 0
        confidence = 0

        if news:
            sentiment_score += news.get("sentiment", 0) * 0.4
            confidence += news.get("confidence", 0) * 0.4

        if social:
            sentiment_score += social.get("sentiment", 0) * 0.3
            confidence += social.get("confidence", 0) * 0.3

        if technical:
            sentiment_score += technical.get("signal", 0) * 0.3
            confidence += technical.get("confidence", 0) * 0.3

        # Determine recommendation
        if sentiment_score > 0.6:
            recommendation = "BUY"
        elif sentiment_score < -0.6:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"

        final_recommendation = {
            "ticker": ticker,
            "recommendation": recommendation,
            "sentiment_score": round(sentiment_score, 2),
            "confidence": round(confidence, 2),
            "summary": f"Based on multi-agent analysis of {ticker}: {recommendation} with {round(confidence*100)}% confidence"
        }

        # Create new state with final recommendation
        new_state = state.copy()
        new_state["final_recommendation"] = final_recommendation
        new_messages = state["messages"].copy()
        new_messages.append(
            AIMessage(
                content=f"Analysis complete for {ticker}: {final_recommendation['summary']}")
        )
        new_state["messages"] = new_messages

        return new_state

    def analyze_stock(self, ticker: str) -> Dict[str, Any]:
        """Analyze a stock ticker using all agents."""
        initial_state: TradingState = {
            "ticker": ticker,
            "messages": [HumanMessage(content=f"Analyze {ticker}")],
            "news_analysis": {},
            "social_analysis": {},
            "technical_analysis": {},
            "final_recommendation": {}
        }

        result = self.graph.invoke(initial_state)
        return result["final_recommendation"]


def create_trading_system() -> TradingSystem:
    """Create and return a new trading system instance."""
    return TradingSystem()
