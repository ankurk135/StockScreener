"""
Test script for all technical indicators (Basic + Advanced)
"""

import pandas as pd
from data_fetcher import DataFetcher
from indicators import (
    price_indicators, 
    trend_indicators, 
    momentum_indicators,
    volume_indicators,
    money_flow_indicators,
    strength_indicators
)


def test_all_indicators():
    print("\n" + "="*60)
    print("Testing ALL Technical Indicators (40 metrics)")
    print("="*60 + "\n")
    
    # Fetch sample data
    print("Fetching data for RELIANCE.NS and Nifty...")
    fetcher = DataFetcher()
    
    stock_data = fetcher.fetch_single_stock("RELIANCE.NS")
    nifty_data = fetcher.fetch_single_stock("^NSEI")  # Nifty 50 index
    
    if not stock_data or not nifty_data:
        print("Failed to fetch data")
        return
    
    daily_data = stock_data['daily_data']
    weekly_data = stock_data['weekly_data']
    info = stock_data['info']
    nifty_daily = nifty_data['daily_data']
    
    print(f"Data fetched: {len(daily_data)} daily, {len(weekly_data)} weekly records\n")
    
    # Test Price Indicators
    print("1. PRICE INDICATORS (9 metrics)")
    print("-" * 60)
    price_results = price_indicators.calculate_all_price_indicators(daily_data, info)
    
    for indicator, value in price_results.items():
        if value is not None:
            if 'Pct' in indicator:
                print(f"  ✓ {indicator}: {value:.2f}%")
            elif 'PE' in indicator:
                print(f"  ✓ {indicator}: {value:.2f}x")
            else:
                print(f"  ✓ {indicator}: ₹{value:.2f}")
        else:
            print(f"  ✗ {indicator}: N/A")
    
    # Test Trend Indicators (including SuperTrend)
    print("\n2. TREND INDICATORS (8 metrics)")
    print("-" * 60)
    current_price = price_results['Price']
    trend_results = trend_indicators.calculate_all_trend_indicators(
        daily_data, weekly_data, current_price
    )
    
    for indicator, value in trend_results.items():
        if value is not None:
            if 'Pct' in indicator:
                print(f"  ✓ {indicator}: {value:.2f}%")
            elif indicator in ['GoldenCross_DeathCross']:
                print(f"  ✓ {indicator}: {value}")
            else:
                print(f"  ✓ {indicator}: ₹{value:.2f}")
        else:
            print(f"  ✗ {indicator}: N/A")
    
   # Test Momentum Indicators (including complete MACD)
    print("\n3. MOMENTUM INDICATORS (8 metrics)")
    print("-" * 60)
    momentum_results = momentum_indicators.calculate_all_momentum_indicators(
        daily_data, weekly_data
    )
    
    for indicator, value in momentum_results.items():
        if value is not None:
            if 'Crossover_Signal' in indicator:  # These are strings
                print(f"  ✓ {indicator}: {value}")
            else:  # These are numbers
                print(f"  ✓ {indicator}: {value:.2f}")
        else:
            print(f"  ✗ {indicator}: N/A")
    # Test Volume Indicators
    print("\n4. VOLUME INDICATORS (6 metrics)")
    print("-" * 60)
    volume_results = volume_indicators.calculate_all_volume_indicators(daily_data)
    
    for indicator, value in volume_results.items():
        if value is not None:
            if 'Pct' in indicator:
                print(f"  ✓ {indicator}: {value:.2f}%")
            else:
                print(f"  ✓ {indicator}: {value:.2f}x")
        else:
            print(f"  ✗ {indicator}: N/A")
    
    # Test Money Flow Indicators
    print("\n5. MONEY FLOW INDICATORS (4 metrics)")
    print("-" * 60)
    money_flow_results = money_flow_indicators.calculate_all_money_flow_indicators(daily_data)
    
    for indicator, value in money_flow_results.items():
        if value is not None:
            if 'Pct' in indicator or 'Change' in indicator:
                print(f"  ✓ {indicator}: {value:.2f}%")
            else:
                print(f"  ✓ {indicator}: {value:.2f}")
        else:
            print(f"  ✗ {indicator}: N/A")
    
    # Test Relative Strength Indicators
    print("\n6. RELATIVE STRENGTH INDICATORS (3 metrics)")
    print("-" * 60)
    strength_results = strength_indicators.calculate_all_strength_indicators(
        daily_data, nifty_daily
    )
    
    for indicator, value in strength_results.items():
        if value is not None:
            print(f"  ✓ {indicator}: {value:.2f}x")
        else:
            print(f"  ✗ {indicator}: N/A")
    
    # Summary
    print("\n" + "="*60)
    all_results = {**price_results, **trend_results, **momentum_results, 
                   **volume_results, **money_flow_results, **strength_results}
    
    total_indicators = len(all_results)
    calculated = sum(1 for v in all_results.values() if v is not None)
    
    print(f"SUMMARY: {calculated}/{total_indicators} indicators calculated successfully")
    print("="*60)


if __name__ == '__main__':
    test_all_indicators()