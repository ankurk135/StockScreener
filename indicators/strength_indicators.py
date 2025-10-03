"""
Strength Indicators Module
Calculates relative strength vs market (Nifty)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_relative_strength(stock_data: pd.DataFrame, nifty_data: pd.DataFrame, 
                                days: int) -> Optional[float]:
    """
    Calculate relative strength vs Nifty over specified days
    
    Args:
        stock_data: Stock's historical OHLCV data
        nifty_data: Nifty's historical OHLCV data
        days: Period for calculation
    
    Returns:
        Relative strength ratio or None
    """
    try:
        if len(stock_data) < days + 1 or len(nifty_data) < days + 1:
            return None
        
        # Get current and past prices
        stock_current = stock_data['Close'].iloc[-1]
        stock_past = stock_data['Close'].iloc[-(days + 1)]
        
        nifty_current = nifty_data['Close'].iloc[-1]
        nifty_past = nifty_data['Close'].iloc[-(days + 1)]
        
        if stock_past == 0 or nifty_past == 0:
            return None
        
        # Calculate returns
        stock_return = (stock_current / stock_past) - 1
        nifty_return = (nifty_current / nifty_past) - 1
        
        if nifty_return == 0:
            return None
        
        # Relative strength = stock_return / nifty_return
        rel_strength = stock_return / nifty_return
        
        return float(rel_strength)
        
    except Exception as e:
        logger.error(f"Error calculating relative strength: {e}")
        return None


def calculate_all_strength_indicators(stock_data: pd.DataFrame, 
                                      nifty_data: pd.DataFrame) -> Dict:
    """
    Calculate all relative strength indicators
    
    Args:
        stock_data: Stock's historical OHLCV data
        nifty_data: Nifty's historical OHLCV data
    
    Returns:
        Dictionary with all calculated strength indicators
    """
    return {
        'RelStrength_18d': calculate_relative_strength(stock_data, nifty_data, 18),
        'RelStrength_55D': calculate_relative_strength(stock_data, nifty_data, 55),
        'RelStrength_81d': calculate_relative_strength(stock_data, nifty_data, 81)
    }