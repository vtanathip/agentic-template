"""Main entry point for multiagent trading system."""

import argparse
from src.multiagent_template import TradingSystem


def main():
    """Main entry point for the trading system CLI."""
    parser = argparse.ArgumentParser(description="Multi-Agent Trading System")
    parser.add_argument(
        "tickers",
        nargs="+",
        help="Stock tickers to analyze (e.g., AAPL TSLA MSFT)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    args = parser.parse_args()

    print("🤖 Multi-Agent Trading System")
    print("=" * 40)

    trading_system = TradingSystem()

    results = []
    for ticker in args.tickers:
        print(f"\n📊 Analyzing {ticker}...")
        try:
            recommendation = trading_system.analyze_stock(ticker)
            results.append(recommendation)

            if args.json:
                import json
                print(json.dumps(recommendation, indent=2))
            else:
                print(f"  Recommendation: {recommendation['recommendation']}")
                print(
                    f"  Sentiment Score: {recommendation['sentiment_score']}")
                print(f"  Confidence: {recommendation['confidence']:.0%}")
                print(f"  Summary: {recommendation['summary']}")

        except Exception as e:
            print(f"  ❌ Error analyzing {ticker}: {e}")

    if args.json and len(results) > 1:
        import json
        print("\n" + "=" * 40)
        print("All Results:")
        print(json.dumps(results, indent=2))

    print(f"\n✅ Analysis complete for {len(results)} ticker(s)!")


if __name__ == "__main__":
    main()
