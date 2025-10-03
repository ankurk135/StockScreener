"""
Cache Manager Module
Handles file-based caching of YFinance data to improve performance
"""

import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages file-based caching for stock data"""
    
    def __init__(self, config: dict = None):
        """Initialize Cache Manager with configuration"""
        if config is None:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.cache_dir = Path('data/cache')
        self.cache_enabled = config['storage']['enable_cache']
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cache Manager initialized (enabled: {self.cache_enabled})")
    
    def get_cache_filename(self, ticker: str, fetch_date: date = None) -> str:
        """
        Generate cache filename for a ticker
        
        Args:
            ticker: Stock ticker symbol
            fetch_date: Date of data fetch (defaults to today)
            
        Returns:
            Filename for cache file
        """
        if fetch_date is None:
            fetch_date = date.today()
        
        # Sanitize ticker for filename (replace : with _)
        safe_ticker = ticker.replace(':', '_').replace('/', '_')
        filename = f"{safe_ticker}_{fetch_date.strftime('%Y-%m-%d')}.json"
        
        return filename
    
    def get_cache_path(self, ticker: str, fetch_date: date = None) -> Path:
        """Get full path to cache file"""
        filename = self.get_cache_filename(ticker, fetch_date)
        return self.cache_dir / filename
    
    def cache_exists(self, ticker: str, fetch_date: date = None) -> bool:
        """
        Check if cache file exists for ticker and date
        
        Args:
            ticker: Stock ticker symbol
            fetch_date: Date to check (defaults to today)
            
        Returns:
            True if cache exists, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        cache_path = self.get_cache_path(ticker, fetch_date)
        exists = cache_path.exists()
        
        if exists:
            logger.debug(f"Cache hit for {ticker}")
        else:
            logger.debug(f"Cache miss for {ticker}")
        
        return exists
    
    def save_to_cache(self, ticker: str, data: Dict, fetch_date: date = None) -> bool:
        """
        Save stock data to cache
        
        Args:
            ticker: Stock ticker symbol
            data: Dictionary containing stock data
            fetch_date: Date of fetch (defaults to today)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            logger.debug("Caching disabled, skipping save")
            return False
        
        try:
            cache_path = self.get_cache_path(ticker, fetch_date)
            
            # Prepare data for JSON serialization
            cache_data = {
                'ticker': ticker,
                'fetch_time': datetime.now().isoformat(),
                'fetch_date': (fetch_date or date.today()).isoformat(),
                'daily_data': data['daily_data'].to_json() if isinstance(data.get('daily_data'), pd.DataFrame) else None,
                'weekly_data': data['weekly_data'].to_json() if isinstance(data.get('weekly_data'), pd.DataFrame) else None,
                'info': data.get('info', {})
            }
            
            # Write to file
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached data for {ticker} to {cache_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache data for {ticker}: {e}")
            return False
    
    def load_from_cache(self, ticker: str, fetch_date: date = None) -> Optional[Dict]:
        """
        Load stock data from cache
        
        Args:
            ticker: Stock ticker symbol
            fetch_date: Date of cached data (defaults to today)
            
        Returns:
            Dictionary with stock data or None if not found/error
        """
        if not self.cache_enabled:
            return None
        
        try:
            cache_path = self.get_cache_path(ticker, fetch_date)
            
            if not cache_path.exists():
                return None
            
            # Read from file
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Reconstruct DataFrames
            result = {
                'ticker': cache_data['ticker'],
                'fetch_time': datetime.fromisoformat(cache_data['fetch_time']),
                'daily_data': pd.read_json(cache_data['daily_data']) if cache_data['daily_data'] else pd.DataFrame(),
                'weekly_data': pd.read_json(cache_data['weekly_data']) if cache_data['weekly_data'] else pd.DataFrame(),
                'info': cache_data.get('info', {})
            }
            
            logger.info(f"Loaded {ticker} from cache")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load cache for {ticker}: {e}")
            return None
    
    def is_cache_valid(self, ticker: str, max_age_hours: int = 24) -> bool:
        """
        Check if cache is still valid (not too old)
        
        Args:
            ticker: Stock ticker symbol
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            True if cache exists and is recent enough
        """
        cache_path = self.get_cache_path(ticker)
        
        if not cache_path.exists():
            return False
        
        # Check file modification time
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age_hours = (datetime.now() - file_time).total_seconds() / 3600
        
        is_valid = age_hours < max_age_hours
        
        if not is_valid:
            logger.debug(f"Cache for {ticker} is {age_hours:.1f}h old (max: {max_age_hours}h)")
        
        return is_valid
    
    def cleanup_old_cache(self, days_to_keep: int = 7) -> int:
        """
        Remove cache files older than specified days
        
        Args:
            days_to_keep: Number of days to keep cache files
            
        Returns:
            Number of files deleted
        """
        if not self.cache_enabled:
            return 0
        
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 86400)
            deleted_count = 0
            
            for cache_file in self.cache_dir.glob('*.json'):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old cache file: {cache_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old cache files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cache usage
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob('*.json'))
            total_files = len(cache_files)
            
            if total_files == 0:
                return {
                    'total_files': 0,
                    'total_size_mb': 0,
                    'oldest_file': None,
                    'newest_file': None
                }
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in cache_files)
            total_size_mb = total_size / (1024 * 1024)
            
            # Find oldest and newest
            file_times = [(f, f.stat().st_mtime) for f in cache_files]
            oldest = min(file_times, key=lambda x: x[1])
            newest = max(file_times, key=lambda x: x[1])
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size_mb, 2),
                'oldest_file': oldest[0].name,
                'oldest_date': datetime.fromtimestamp(oldest[1]).strftime('%Y-%m-%d'),
                'newest_file': newest[0].name,
                'newest_date': datetime.fromtimestamp(newest[1]).strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


def test_cache_manager():
    """Test the Cache Manager functionality"""
    print("\n" + "="*60)
    print("Testing Cache Manager")
    print("="*60 + "\n")
    
    try:
        # Initialize manager
        cache_mgr = CacheManager()
        print("✓ Cache Manager initialized\n")
        
        # Test cache with sample data
        test_ticker = "TEST.NS"
        sample_data = {
            'ticker': test_ticker,
            'daily_data': pd.DataFrame({
                'Close': [100, 101, 102],
                'Volume': [1000, 1100, 1200]
            }),
            'weekly_data': pd.DataFrame({
                'Close': [100, 105],
                'Volume': [5000, 6000]
            }),
            'info': {'longName': 'Test Company', 'sector': 'Technology'}
        }
        
        # Save to cache
        print(f"Saving {test_ticker} to cache...")
        success = cache_mgr.save_to_cache(test_ticker, sample_data)
        if success:
            print("✓ Data saved to cache")
        else:
            print("✗ Failed to save to cache")
            return
        
        # Check if cache exists
        print(f"\nChecking if cache exists for {test_ticker}...")
        exists = cache_mgr.cache_exists(test_ticker)
        if exists:
            print("✓ Cache file found")
        else:
            print("✗ Cache file not found")
            return
        
        # Load from cache
        print(f"\nLoading {test_ticker} from cache...")
        cached_data = cache_mgr.load_from_cache(test_ticker)
        
        if cached_data:
            print("✓ Data loaded from cache")
            print(f"  Daily records: {len(cached_data['daily_data'])}")
            print(f"  Weekly records: {len(cached_data['weekly_data'])}")
            print(f"  Company: {cached_data['info'].get('longName', 'N/A')}")
        else:
            print("✗ Failed to load from cache")
            return
        
        # Get cache stats
        print("\nCache Statistics:")
        stats = cache_mgr.get_cache_stats()
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total size: {stats['total_size_mb']} MB")
        if stats['total_files'] > 0:
            print(f"  Newest: {stats['newest_file']}")
        
        # Test cleanup (with 0 days to force cleanup of test file)
        print("\nTesting cache cleanup...")
        deleted = cache_mgr.cleanup_old_cache(days_to_keep=0)
        print(f"✓ Cleaned up {deleted} cache file(s)")
        
        print("\n" + "="*60)
        print("Cache Manager Test Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run test when file is executed directly
    test_cache_manager()