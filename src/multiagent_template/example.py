"""Example usage of the multi-agent trading system."""

from src.multiagent_template import TradingSystem


def main():
    """Run a simple example of the trading system."""
    print("Creating Multi-Agent Trading System...")
    trading_system = TradingSystem()
    
    # Example stock tickers to analyze
    tickers = ["AAPL", "TSLA", "MSFT"]
    
    print("\nAnalyzing stocks with multi-agent system...")
    
    for ticker in tickers:
        print(f"\n{'='*50}")
        print(f"Analyzing {ticker}")
        print(f"{'='*50}")
        
        try:
            recommendation = trading_system.analyze_stock(ticker)
            
            print(f"Ticker: {recommendation['ticker']}")
            print(f"Recommendation: {recommendation['recommendation']}")
            print(f"Sentiment Score: {recommendation['sentiment_score']}")
            print(f"Confidence: {recommendation['confidence']}")
            print(f"Summary: {recommendation['summary']}")
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
    
    print("\nMulti-agent trading analysis completed!")


if __name__ == "__main__":
    main()