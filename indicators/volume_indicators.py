"""
Volume Indicators Module
Calculates volume-based metrics and relative volume ratios
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_volume_change_pct(hist_data: pd.DataFrame) -> Optional[float]:
    """
    Calculate day-over-day volume change percentage
    
    Args:
        hist_data: Historical OHLCV data
    
    Returns:
        Volume change percentage or None
    """
    try:
        if len(hist_data) < 2:
            return None
        
        current_volume = hist_data['Volume'].iloc[-1]
        prev_volume = hist_data['Volume'].iloc[-2]
        
        if prev_volume == 0:
            return None
        
        change_pct = ((current_volume - prev_volume) / prev_volume) * 100
        return float(change_pct)
        
    except Exception as e:
        logger.error(f"Error calculating volume change: {e}")
        return None


def calculate_relative_volume(hist_data: pd.DataFrame, current_days: int, 
                              average_days: int) -> Optional[float]:
    """
    Calculate relative volume ratio
    
    Args:
        hist_data: Historical OHLCV data
        current_days: Days for current average (usually 1 or 10)
        average_days: Days for comparison average
    
    Returns:
        Relative volume ratio or None
    """
    try:
        if len(hist_data) < average_days:
            return None
        
        current_avg = hist_data['Volume'].tail(current_days).mean()
        comparison_avg = hist_data['Volume'].tail(average_days).mean()
        
        if comparison_avg == 0:
            return None
        
        rel_vol = current_avg / comparison_avg
        return float(rel_vol)
        
    except Exception as e:
        logger.error(f"Error calculating relative volume: {e}")
        return None


def calculate_all_volume_indicators(hist_data: pd.DataFrame) -> Dict:
    """
    Calculate all volume indicators
    
    Args:
        hist_data: Historical OHLCV data
    
    Returns:
        Dictionary with all calculated volume indicators
    """
    return {
        'VolumeChangePct': calculate_volume_change_pct(hist_data),
        'RelVol_1D_over_10D': calculate_relative_volume(hist_data, 1, 10),
        'RelVol_1D_over_30D': calculate_relative_volume(hist_data, 1, 30),
        'RelVol_10D_over_30D': calculate_relative_volume(hist_data, 10, 30),
        'RelVol_10D_over_60D': calculate_relative_volume(hist_data, 10, 60),
        'RelVol_10D_over_90D': calculate_relative_volume(hist_data, 10, 90)
    }