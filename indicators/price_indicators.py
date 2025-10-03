"""
Price Indicators Module
Calculates price-based metrics and valuation ratios
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_price(hist_data: pd.DataFrame) -> Optional[float]:
    """Get current price (latest close)"""
    try:
        if hist_data.empty:
            return None
        return float(hist_data['Close'].iloc[-1])
    except Exception as e:
        logger.error(f"Error calculating price: {e}")
        return None


def calculate_price_change_pct(hist_data: pd.DataFrame, days: int) -> Optional[float]:
    """
    Calculate price change percentage over N days
    
    Args:
        hist_data: Historical OHLCV data
        days: Number of days to look back
    
    Returns:
        Percentage change or None if insufficient data
    """
    try:
        if len(hist_data) < days + 1:
            return None
        
        current_price = hist_data['Close'].iloc[-1]
        past_price = hist_data['Close'].iloc[-(days + 1)]
        
        if past_price == 0:
            return None
        
        change_pct = ((current_price - past_price) / past_price) * 100
        return float(change_pct)
        
    except Exception as e:
        logger.error(f"Error calculating {days}D price change: {e}")
        return None


def calculate_52_week_high(hist_data: pd.DataFrame) -> Optional[float]:
    """Calculate 52-week high (252 trading days)"""
    try:
        if len(hist_data) < 252:
            # Use available data if less than 252 days
            return float(hist_data['High'].max())
        
        week_52_data = hist_data.tail(252)
        return float(week_52_data['High'].max())
        
    except Exception as e:
        logger.error(f"Error calculating 52-week high: {e}")
        return None


def calculate_52_week_low(hist_data: pd.DataFrame) -> Optional[float]:
    """Calculate 52-week low (252 trading days)"""
    try:
        if len(hist_data) < 252:
            return float(hist_data['Low'].min())
        
        week_52_data = hist_data.tail(252)
        return float(week_52_data['Low'].min())
        
    except Exception as e:
        logger.error(f"Error calculating 52-week low: {e}")
        return None


def calculate_5_year_high(hist_data: pd.DataFrame) -> Optional[float]:
    """Calculate 5-year high"""
    try:
        if hist_data.empty:
            return None
        return float(hist_data['High'].max())
    except Exception as e:
        logger.error(f"Error calculating 5-year high: {e}")
        return None


def calculate_5_year_low(hist_data: pd.DataFrame) -> Optional[float]:
    """Calculate 5-year low"""
    try:
        if hist_data.empty:
            return None
        return float(hist_data['Low'].min())
    except Exception as e:
        logger.error(f"Error calculating 5-year low: {e}")
        return None


def calculate_trailing_pe(info: Dict) -> Optional[float]:
    """Extract trailing PE ratio from stock info"""
    try:
        pe = info.get('trailingPE')
        if pe and not np.isnan(pe):
            return float(pe)
        return None
    except Exception as e:
        logger.error(f"Error extracting trailing PE: {e}")
        return None


def calculate_all_price_indicators(hist_data: pd.DataFrame, info: Dict) -> Dict:
    """
    Calculate all price indicators
    
    Args:
        hist_data: Historical OHLCV data
        info: Stock info dictionary from yfinance
    
    Returns:
        Dictionary with all calculated price indicators
    """
    return {
        'Price': calculate_price(hist_data),
        'Price_1D_Change_Pct': calculate_price_change_pct(hist_data, 1),
        'Price_5D_Change_Pct': calculate_price_change_pct(hist_data, 5),
        'Price_11D_Change_Pct': calculate_price_change_pct(hist_data, 11),
        'TrailingPE': calculate_trailing_pe(info),
        '52WeekHigh': calculate_52_week_high(hist_data),
        '52WeekLow': calculate_52_week_low(hist_data),
        '5YearHigh': calculate_5_year_high(hist_data),
        '5YearLow': calculate_5_year_low(hist_data)
    }