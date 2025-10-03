"""
Excel Manager Module
Handles reading and writing Excel files for watchlist management
"""

import os
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExcelManager:
    """Manages Excel file operations for stock watchlist"""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize Excel Manager with configuration"""
        self.config = self.load_config(config_path)
        self.excel_file = self.config['excel']['watchlist_file']
        self.master_sheet = self.config['excel']['master_sheet']
        self.required_columns = self.config['excel']['required_columns']
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def validate_excel_file(self) -> bool:
        """Check if Excel file exists and is accessible"""
        if not os.path.exists(self.excel_file):
            logger.error(f"Excel file not found: {self.excel_file}")
            return False
        
        # Check if file is locked (open in Excel)
        try:
            with open(self.excel_file, 'a'):
                pass
            return True
        except PermissionError:
            logger.warning(f"Excel file is locked (may be open in Excel): {self.excel_file}")
            return True  # File exists but locked - still return True
    
    def read_master_sheet(self) -> Optional[pd.DataFrame]:
        """
        Read the Master sheet containing all stocks
        
        Returns:
            DataFrame with stock data or None if error
        """
        try:
            # Validate file exists
            if not self.validate_excel_file():
                return None
            
            # Read Excel file
            logger.info(f"Reading Master sheet from {self.excel_file}")
            df = pd.read_excel(self.excel_file, sheet_name=self.master_sheet)
            
            # Validate required columns exist
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                logger.error(f"Available columns: {list(df.columns)}")
                raise ValueError(f"Missing columns: {missing_columns}")
            
            # Clean data
            df = df.dropna(subset=['Stock_Name', 'YF_Ticker', 'TV_Ticker'])  # Remove rows with missing critical data
            df['Stock_Name'] = df['Stock_Name'].str.strip()
            df['YF_Ticker'] = df['YF_Ticker'].str.strip().str.upper()
            df['TV_Ticker'] = df['TV_Ticker'].str.strip()
            
            logger.info(f"Successfully loaded {len(df)} stocks from Master sheet")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {self.excel_file}")
            return None
        except ValueError as e:
            logger.error(f"Excel validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading Excel: {e}")
            return None
    
    def get_all_sheet_names(self) -> List[str]:
        """Get all sheet names from Excel file"""
        try:
            excel_file = pd.ExcelFile(self.excel_file)
            sheet_names = excel_file.sheet_names
            logger.info(f"Found {len(sheet_names)} sheets: {sheet_names}")
            return sheet_names
        except Exception as e:
            logger.error(f"Error reading sheet names: {e}")
            return []
    
    def get_watchlist_sheets(self) -> List[str]:
        """Get all watchlist sheet names (excluding Master)"""
        all_sheets = self.get_all_sheet_names()
        watchlist_sheets = [s for s in all_sheets if s != self.master_sheet]
        logger.info(f"Found {len(watchlist_sheets)} watchlist sheets")
        return watchlist_sheets
    
    def read_watchlist_sheet(self, sheet_name: str) -> Optional[pd.DataFrame]:
        """
        Read a specific watchlist sheet
        
        Args:
            sheet_name: Name of the watchlist sheet
            
        Returns:
            DataFrame with stock names from that watchlist
        """
        try:
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
            logger.info(f"Read {len(df)} stocks from watchlist '{sheet_name}'")
            return df
        except Exception as e:
            logger.error(f"Error reading watchlist sheet '{sheet_name}': {e}")
            return None
    
    def get_stocks_by_watchlist(self, watchlist_name: str) -> Optional[List[str]]:
        """
        Get list of stock names in a specific watchlist
        
        Args:
            watchlist_name: Name of the watchlist
            
        Returns:
            List of stock names
        """
        watchlist_df = self.read_watchlist_sheet(watchlist_name)
        if watchlist_df is None:
            return None
        
        if 'Stock_Name' not in watchlist_df.columns:
            logger.error(f"Watchlist '{watchlist_name}' missing 'Stock_Name' column")
            return None
        
        stock_names = watchlist_df['Stock_Name'].dropna().tolist()
        return stock_names


# Test function
def test_excel_manager():
    """Test the Excel Manager functionality"""
    print("\n" + "="*60)
    print("Testing Excel Manager")
    print("="*60 + "\n")
    
    try:
        # Initialize manager
        manager = ExcelManager()
        print("✓ Excel Manager initialized")
        
        # Test file validation
        if manager.validate_excel_file():
            print("✓ Excel file exists and is accessible")
        else:
            print("✗ Excel file validation failed")
            return
        
        # Read Master sheet
        master_df = manager.read_master_sheet()
        if master_df is not None:
            print(f"✓ Master sheet loaded: {len(master_df)} stocks")
            print("\nFirst 5 stocks:")
            print(master_df[['Stock_Name', 'YF_Ticker', 'TV_Ticker', 'Sector']].head())
        else:
            print("✗ Failed to read Master sheet")
            return
        
        # Get all sheets
        all_sheets = manager.get_all_sheet_names()
        print(f"\n✓ Found {len(all_sheets)} total sheets: {all_sheets}")
        
        # Get watchlist sheets
        watchlist_sheets = manager.get_watchlist_sheets()
        if watchlist_sheets:
            print(f"✓ Found {len(watchlist_sheets)} watchlist sheets: {watchlist_sheets}")
        else:
            print("ℹ No additional watchlist sheets found (only Master sheet)")
        
        print("\n" + "="*60)
        print("Excel Manager Test Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run test when file is executed directly
    test_excel_manager()