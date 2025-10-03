"""
Data Fetcher Module
Handles fetching stock data from YFinance with error handling and retries
"""

import yfinance as yf
import time
import logging
import pandas as pd
from typing import Optional, Dict, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock data from YFinance with robust error handling"""
    
    def __init__(self, config: dict = None):
        """Initialize Data Fetcher with configuration"""
        if config is None:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.api_delay = config['api']['yfinance_delay']
        self.max_retries = config['api']['max_retries']
        self.timeout = config['api']['timeout']
        self.daily_history_years = config['data_requirements']['daily_history_years']
        self.weekly_history_years = config['data_requirements']['weekly_history_years']
    
    def fetch_single_stock(self, ticker: str, target_date: Optional[datetime] = None) -> Optional[Dict]:
        """
        Fetch data for a single stock with retry logic
        
        Args:
            ticker: YFinance ticker symbol (e.g., "RELIANCE.NS")
            target_date: Optional specific date to fetch data for
            
        Returns:
            Dictionary with daily_data, weekly_data, and info, or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {ticker} (attempt {attempt + 1}/{self.max_retries})")
                
                # Create ticker object
                stock = yf.Ticker(ticker)
                
                # Fetch daily historical data
                daily_data = stock.history(
                    period=f"{self.daily_history_years}y",
                    interval="1d"
                )
                
                # Fetch weekly historical data
                weekly_data = stock.history(
                    period=f"{self.weekly_history_years}y",
                    interval="1wk"
                )
                
                # Check if data is empty
                if daily_data.empty:
                    logger.warning(f"{ticker}: No daily data returned")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                
                # Fetch company info (may not be available for all stocks)
                try:
                    info = stock.info
                except Exception as e:
                    logger.warning(f"{ticker}: Could not fetch info: {e}")
                    info = {}
                
                # Filter by target date if specified
                if target_date:
                    daily_data = daily_data[daily_data.index <= target_date]
                    weekly_data = weekly_data[weekly_data.index <= target_date]
                
                logger.info(f"{ticker}: Successfully fetched {len(daily_data)} daily, {len(weekly_data)} weekly records")
                
                return {
                    'ticker': ticker,
                    'daily_data': daily_data,
                    'weekly_data': weekly_data,
                    'info': info,
                    'fetch_time': datetime.now()
                }
                
            except Exception as e:
                logger.error(f"{ticker}: Error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"{ticker}: Failed after {self.max_retries} attempts")
                    return None
        
        return None
    
    def fetch_multiple_stocks(self, tickers: list, progress_callback=None) -> Dict[str, Dict]:
        """
        Fetch data for multiple stocks with progress tracking
        
        Args:
            tickers: List of ticker symbols
            progress_callback: Optional function to call with progress updates
            
        Returns:
            Dictionary mapping tickers to their data
        """
        results = {}
        total = len(tickers)
        
        logger.info(f"Starting batch fetch for {total} stocks")
        
        for index, ticker in enumerate(tickers, 1):
            # Progress update
            if progress_callback:
                progress_callback(index, total, ticker)
            else:
                logger.info(f"Progress: {index}/{total} ({(index/total)*100:.1f}%)")
            
            # Fetch data
            data = self.fetch_single_stock(ticker)
            
            if data:
                results[ticker] = data
            else:
                results[ticker] = {'error': 'Failed to fetch data'}
            
            # Rate limiting
            if index < total:  # Don't delay after last stock
                time.sleep(self.api_delay)
        
        successful = sum(1 for v in results.values() if 'error' not in v)
        failed = total - successful
        
        logger.info(f"Batch fetch complete: {successful} successful, {failed} failed")
        
        return results
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Quick validation check if ticker exists
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            True if ticker appears valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got meaningful info back
            if info and len(info) > 5:
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Ticker validation failed for {ticker}: {e}")
            return False


def test_data_fetcher():
    """Test the Data Fetcher functionality"""
    print("\n" + "="*60)
    print("Testing Data Fetcher")
    print("="*60 + "\n")
    
    try:
        # Initialize fetcher
        fetcher = DataFetcher()
        print("✓ Data Fetcher initialized\n")
        
        # Test single stock fetch
        test_ticker = "RELIANCE.NS"
        print(f"Testing single stock fetch: {test_ticker}")
        
        data = fetcher.fetch_single_stock(test_ticker)
        
        if data:
            print(f"✓ Successfully fetched {test_ticker}")
            print(f"  Daily records: {len(data['daily_data'])}")
            print(f"  Weekly records: {len(data['weekly_data'])}")
            print(f"  Latest close: ₹{data['daily_data']['Close'].iloc[-1]:.2f}")
            
            if data['info']:
                print(f"  Company: {data['info'].get('longName', 'N/A')}")
                print(f"  Sector: {data['info'].get('sector', 'N/A')}")
        else:
            print(f"✗ Failed to fetch {test_ticker}")
            return
        
        # Test with invalid ticker
        print(f"\nTesting invalid ticker: INVALID.NS")
        invalid_data = fetcher.fetch_single_stock("INVALID.NS")
        if invalid_data is None:
            print("✓ Correctly handled invalid ticker")
        
        # Test batch fetch with small sample
        print(f"\nTesting batch fetch with 3 stocks")
        test_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        
        results = fetcher.fetch_multiple_stocks(test_tickers)
        
        successful = sum(1 for v in results.values() if 'error' not in v)
        print(f"\n✓ Batch fetch complete: {successful}/{len(test_tickers)} successful")
        
        for ticker, data in results.items():
            if 'error' in data:
                print(f"  ✗ {ticker}: {data['error']}")
            else:
                latest_price = data['daily_data']['Close'].iloc[-1]
                print(f"  ✓ {ticker}: ₹{latest_price:.2f}")
        
        print("\n" + "="*60)
        print("Data Fetcher Test Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run test when file is executed directly
    test_data_fetcher()