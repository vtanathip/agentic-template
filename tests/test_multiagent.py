"""Unit tests for the multi-agent trading system."""

import pytest
from unittest.mock import Mock, patch
from src.multiagent_template import TradingSystem, TradingState
from src.multiagent_template.agents import NewsAgent, SocialAgent, TechnicalAgent


class TestTradingSystem:
    """Test cases for the TradingSystem class."""

    def test_trading_system_initialization(self):
        """Test that TradingSystem initializes correctly."""
        trading_system = TradingSystem()
        assert trading_system is not None
        assert trading_system.graph is not None

    def test_analyze_stock_returns_recommendation(self):
        """Test that analyze_stock returns a valid recommendation."""
        trading_system = TradingSystem()
        result = trading_system.analyze_stock("AAPL")

        assert isinstance(result, dict)
        assert "ticker" in result
        assert "recommendation" in result
        assert "sentiment_score" in result
        assert "confidence" in result
        assert "summary" in result

        assert result["ticker"] == "AAPL"
        assert result["recommendation"] in ["BUY", "SELL", "HOLD"]
        assert isinstance(result["sentiment_score"], (int, float))
        assert isinstance(result["confidence"], (int, float))
        assert isinstance(result["summary"], str)

    def test_analyze_stock_with_different_tickers(self):
        """Test analysis with different stock tickers."""
        trading_system = TradingSystem()

        tickers = ["AAPL", "TSLA", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = trading_system.analyze_stock(ticker)
            assert result["ticker"] == ticker
            assert result["recommendation"] in ["BUY", "SELL", "HOLD"]


class TestNewsAgent:
    """Test cases for the NewsAgent class."""

    def test_news_agent_initialization(self):
        """Test that NewsAgent initializes correctly."""
        agent = NewsAgent()
        assert agent.name == "NewsAgent"

    def test_news_agent_analyze(self):
        """Test NewsAgent analysis functionality."""
        agent = NewsAgent()
        state = {"ticker": "AAPL", "messages": []}

        result = agent.analyze(state)

        assert "news_analysis" in result
        news_data = result["news_analysis"]

        assert news_data["agent"] == "NewsAgent"
        assert news_data["ticker"] == "AAPL"
        assert "sentiment" in news_data
        assert "confidence" in news_data
        assert "key_topics" in news_data
        assert "timestamp" in news_data
        assert "summary" in news_data

        assert isinstance(news_data["sentiment"], (int, float))
        assert isinstance(news_data["confidence"], (int, float))
        assert isinstance(news_data["key_topics"], list)

    def test_news_agent_sentiment_range(self):
        """Test that NewsAgent sentiment is within expected range."""
        agent = NewsAgent()
        state = {"ticker": "TEST", "messages": []}

        # Run multiple times to check range
        for _ in range(10):
            result = agent.analyze(state)
            sentiment = result["news_analysis"]["sentiment"]
            assert -1 <= sentiment <= 1


class TestSocialAgent:
    """Test cases for the SocialAgent class."""

    def test_social_agent_initialization(self):
        """Test that SocialAgent initializes correctly."""
        agent = SocialAgent()
        assert agent.name == "SocialAgent"

    def test_social_agent_analyze(self):
        """Test SocialAgent analysis functionality."""
        agent = SocialAgent()
        state = {"ticker": "TSLA", "messages": []}

        result = agent.analyze(state)

        assert "social_analysis" in result
        social_data = result["social_analysis"]

        assert social_data["agent"] == "SocialAgent"
        assert social_data["ticker"] == "TSLA"
        assert "sentiment" in social_data
        assert "confidence" in social_data
        assert "platforms" in social_data
        assert "volume" in social_data
        assert "timestamp" in social_data
        assert "summary" in social_data

        assert isinstance(social_data["sentiment"], (int, float))
        assert isinstance(social_data["confidence"], (int, float))
        assert isinstance(social_data["platforms"], list)
        assert isinstance(social_data["volume"], int)


class TestTechnicalAgent:
    """Test cases for the TechnicalAgent class."""

    def test_technical_agent_initialization(self):
        """Test that TechnicalAgent initializes correctly."""
        agent = TechnicalAgent()
        assert agent.name == "TechnicalAgent"

    def test_technical_agent_analyze(self):
        """Test TechnicalAgent analysis functionality."""
        agent = TechnicalAgent()
        state = {"ticker": "MSFT", "messages": []}

        result = agent.analyze(state)

        assert "technical_analysis" in result
        tech_data = result["technical_analysis"]

        assert tech_data["agent"] == "TechnicalAgent"
        assert tech_data["ticker"] == "MSFT"
        assert "signal" in tech_data
        assert "confidence" in tech_data
        assert "indicators" in tech_data
        assert "timestamp" in tech_data
        assert "summary" in tech_data

        assert isinstance(tech_data["signal"], (int, float))
        assert isinstance(tech_data["confidence"], (int, float))
        assert isinstance(tech_data["indicators"], dict)

        # Check indicators structure
        indicators = tech_data["indicators"]
        assert "RSI" in indicators
        assert "MACD" in indicators
        assert "trend" in indicators
        assert indicators["trend"] in ["bullish", "bearish", "sideways"]


class TestTradingSystemIntegration:
    """Integration tests for the complete trading system."""

    def test_full_analysis_workflow(self):
        """Test the complete analysis workflow."""
        trading_system = TradingSystem()
        ticker = "AAPL"

        result = trading_system.analyze_stock(ticker)

        # Verify final recommendation structure
        assert result["ticker"] == ticker
        assert result["recommendation"] in ["BUY", "SELL", "HOLD"]
        assert -1 <= result["sentiment_score"] <= 1
        assert 0 <= result["confidence"] <= 1
        assert ticker in result["summary"]
        assert result["recommendation"] in result["summary"]

    def test_multiple_stock_analysis(self):
        """Test analyzing multiple stocks in sequence."""
        trading_system = TradingSystem()
        tickers = ["AAPL", "GOOGL", "AMZN"]

        results = []
        for ticker in tickers:
            result = trading_system.analyze_stock(ticker)
            results.append(result)

        # Verify each result is independent
        for i, result in enumerate(results):
            assert result["ticker"] == tickers[i]
            assert result["recommendation"] in ["BUY", "SELL", "HOLD"]

    def test_synthesis_logic(self):
        """Test the synthesis logic produces consistent results."""
        trading_system = TradingSystem()

        # Mock state with known values
        mock_state = {
            "ticker": "TEST",
            "messages": [],
            "news_analysis": {"sentiment": 0.8, "confidence": 0.9},
            "social_analysis": {"sentiment": 0.6, "confidence": 0.8},
            "technical_analysis": {"signal": 0.7, "confidence": 0.85}
        }

        result = trading_system._synthesize_results(mock_state)

        assert "final_recommendation" in result
        final_rec = result["final_recommendation"]

        # With all positive signals, should be BUY
        assert final_rec["recommendation"] == "BUY"
        assert final_rec["sentiment_score"] > 0
        assert final_rec["confidence"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
