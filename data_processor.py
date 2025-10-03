"""
Data Processor Module
Main orchestrator that connects all components together
Excel → Fetch → Cache → Calculate → Store
"""

import numpy as np
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from excel_manager import ExcelManager
from data_fetcher import DataFetcher
from cache_manager import CacheManager
from indicators import (
    price_indicators,
    trend_indicators,
    momentum_indicators,
    volume_indicators,
    money_flow_indicators,
    strength_indicators
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/screener.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Main data processing orchestrator"""
    
    def __init__(self):
        """Initialize all components"""
        self.excel_mgr = ExcelManager()
        self.data_fetcher = DataFetcher()
        self.cache_mgr = CacheManager()
        
        # Ensure processed data directory exists
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        logger.info("Data Processor initialized")
    
    def process_single_stock(self, ticker: str, yf_ticker: str, tv_ticker: str,
                            sector: str, industry: str) -> Optional[Dict]:
        """
        Process a single stock: fetch data, calculate indicators
        
        Args:
            ticker: Stock name
            yf_ticker: YFinance ticker
            tv_ticker: TradingView ticker
            sector: Stock sector
            industry: Stock industry
        
        Returns:
            Dictionary with all calculated metrics or None if failed
        """
        try:
            logger.info(f"Processing {ticker} ({yf_ticker})")
            
            # Try to load from cache first
            cached_data = self.cache_mgr.load_from_cache(yf_ticker)
            
            if cached_data:
                logger.info(f"Using cached data for {yf_ticker}")
                data = cached_data
            else:
                # Fetch fresh data
                data = self.data_fetcher.fetch_single_stock(yf_ticker)
                
                if not data:
                    logger.error(f"Failed to fetch data for {yf_ticker}")
                    return None
                
                # Cache the fetched data
                self.cache_mgr.save_to_cache(yf_ticker, data)
            
            # Extract data components
            daily_data = data['daily_data']
            weekly_data = data['weekly_data']
            info = data.get('info', {})
            
            # Calculate all indicators
            result = {
                'Stock_Name': ticker,
                'YF_Ticker': yf_ticker,
                'TV_Ticker': tv_ticker,
                'Sector': sector,
                'Industry': industry,
                'LastUpdate': datetime.now().isoformat()
            }
            
            # Price indicators
            price_results = price_indicators.calculate_all_price_indicators(daily_data, info)
            result.update(price_results)
            
            # Trend indicators
            current_price = price_results.get('Price')
            trend_results = trend_indicators.calculate_all_trend_indicators(
                daily_data, weekly_data, current_price
            )
            result.update(trend_results)
            
            # Momentum indicators
            momentum_results = momentum_indicators.calculate_all_momentum_indicators(
                daily_data, weekly_data
            )
            result.update(momentum_results)
            
            # Volume indicators
            volume_results = volume_indicators.calculate_all_volume_indicators(daily_data)
            result.update(volume_results)
            
            # Money flow indicators
            money_flow_results = money_flow_indicators.calculate_all_money_flow_indicators(daily_data)
            result.update(money_flow_results)
            
            # Relative strength (fetch Nifty if not already available)
            try:
                nifty_cached = self.cache_mgr.load_from_cache("^NSEI")
                if nifty_cached:
                    nifty_data = nifty_cached['daily_data']
                else:
                    nifty_fetch = self.data_fetcher.fetch_single_stock("^NSEI")
                    if nifty_fetch:
                        nifty_data = nifty_fetch['daily_data']
                        self.cache_mgr.save_to_cache("^NSEI", nifty_fetch)
                    else:
                        nifty_data = pd.DataFrame()
                
                if not nifty_data.empty:
                    strength_results = strength_indicators.calculate_all_strength_indicators(
                        daily_data, nifty_data
                    )
                    result.update(strength_results)
            except Exception as e:
                logger.warning(f"Could not calculate relative strength: {e}")
            
            logger.info(f"Successfully processed {ticker}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            return None
    
    def process_all_stocks(self, progress_callback=None) -> pd.DataFrame:
        """
        Process all stocks from Master sheet
        
        Args:
            progress_callback: Optional function to call with progress updates
        
        Returns:
            DataFrame with all calculated metrics
        """
        try:
            # Read master sheet
            master_df = self.excel_mgr.read_master_sheet()
            
            if master_df is None or master_df.empty:
                logger.error("No stocks found in Master sheet")
                return pd.DataFrame()
            
            total_stocks = len(master_df)
            logger.info(f"Processing {total_stocks} stocks from Master sheet")
            
            results = []
            successful = 0
            failed = 0
            
            for index, row in master_df.iterrows():
                # Progress update
                if progress_callback:
                    progress_callback(index + 1, total_stocks, row['Stock_Name'])
                
                # Process stock
                result = self.process_single_stock(
                    ticker=row['Stock_Name'],
                    yf_ticker=row['YF_Ticker'],
                    tv_ticker=row['TV_Ticker'],
                    sector=row.get('Sector', 'Unknown'),
                    industry=row.get('Industry', 'Unknown')
                )
                
                if result:
                    results.append(result)
                    successful += 1
                else:
                    failed += 1
                    # Add error row
                    results.append({
                        'Stock_Name': row['Stock_Name'],
                        'YF_Ticker': row['YF_Ticker'],
                        'TV_Ticker': row['TV_Ticker'],
                        'Error': 'Failed to process'
                    })
            
            logger.info(f"Processing complete: {successful} successful, {failed} failed")
            
            # Convert to DataFrame
            results_df = pd.DataFrame(results)
            return results_df
            
        except Exception as e:
            logger.error(f"Error in process_all_stocks: {e}")
            return pd.DataFrame()
    
    def save_processed_data(self, data_df: pd.DataFrame) -> str:
        """Save processed data to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/processed/stock_data_{timestamp}.json"
            
            # Replace NaN/Inf with None for valid JSON
            data_df = data_df.replace([np.nan, np.inf, -np.inf], None)
            
            # Convert DataFrame to JSON
            data_df.to_json(filename, orient='records', indent=2)
            
            logger.info(f"Saved processed data to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            return ""


def test_data_processor():
    """Test the Data Processor"""
    print("\n" + "="*60)
    print("Testing Data Processor - Full Pipeline")
    print("="*60 + "\n")
    
    try:
        # Initialize processor
        processor = DataProcessor()
        print("✓ Data Processor initialized\n")
        
        # Process all stocks
        print("Processing all stocks from Master sheet...")
        print("This may take several minutes...\n")
        
        def progress_callback(current, total, stock_name):
            pct = (current / total) * 100
            print(f"[{current}/{total}] ({pct:.1f}%) Processing: {stock_name}")
        
        results_df = processor.process_all_stocks(progress_callback=progress_callback)
        
        if results_df.empty:
            print("\n✗ No data processed")
            return
        
        print(f"\n✓ Processed {len(results_df)} stocks")
        
        # Show summary - fixed indexing
        if 'Error' in results_df.columns:
            failed = results_df[results_df['Error'].notna()]
            successful = results_df[results_df['Error'].isna()]
        else:
            successful = results_df
            failed = pd.DataFrame()
        
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        # Save processed data
        filename = processor.save_processed_data(results_df)
        if filename:
            print(f"\n✓ Data saved to: {filename}")
        
        # Show sample results
        if len(successful) > 0:
            print("\nSample Results (first stock):")
            print("-" * 60)
            first_stock = successful.iloc[0]
            print(f"Stock: {first_stock.get('Stock_Name')}")
            print(f"Price: ₹{first_stock.get('Price', 0):.2f}")
            print(f"RSI: {first_stock.get('RSI_1D', 0):.2f}")
            print(f"SuperTrend: ₹{first_stock.get('SuperTrend_1D', 0):.2f}")
            print(f"MACD Signal: {first_stock.get('MACD_Crossover_Signal_1D', 'N/A')}")
        
        print("\n" + "="*60)
        print("Data Processor Test Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_data_processor()