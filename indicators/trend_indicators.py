"""
Trend Indicators Module
Calculates moving averages, SuperTrend, and trend-following indicators
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_sma(hist_data: pd.DataFrame, period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average
    
    Args:
        hist_data: Historical OHLCV data
        period: Number of periods for SMA
    
    Returns:
        SMA value or None if insufficient data
    """
    try:
        if len(hist_data) < period:
            return None
        
        sma = hist_data['Close'].rolling(window=period).mean().iloc[-1]
        
        if pd.isna(sma):
            return None
        
        return float(sma)
        
    except Exception as e:
        logger.error(f"Error calculating SMA{period}: {e}")
        return None


def calculate_sma_distance_pct(price: float, sma: float) -> Optional[float]:
    """
    Calculate percentage distance of price from SMA
    
    Args:
        price: Current stock price
        sma: SMA value
    
    Returns:
        Percentage distance or None
    """
    try:
        if price is None or sma is None or price == 0:
            return None
        
        distance_pct = ((price - sma) / price) * 100
        return float(distance_pct)
        
    except Exception as e:
        logger.error(f"Error calculating SMA distance: {e}")
        return None


def calculate_golden_death_cross(hist_data: pd.DataFrame) -> Optional[str]:
    """
    Detect Golden Cross (SMA50 > SMA200) or Death Cross (SMA50 < SMA200)
    
    Args:
        hist_data: Historical OHLCV data
    
    Returns:
        "GC" for Golden Cross, "DC" for Death Cross, None otherwise
    """
    try:
        if len(hist_data) < 200:
            return None
        
        sma_50 = hist_data['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = hist_data['Close'].rolling(window=200).mean().iloc[-1]
        
        if pd.isna(sma_50) or pd.isna(sma_200):
            return None
        
        # Check for crossing (within 0.5%)
        diff_pct = abs(sma_50 - sma_200) / sma_200 * 100
        
        if diff_pct < 0.5:
            return "Crossing"
        elif sma_50 > sma_200:
            return "GC"
        else:
            return "DC"
            
    except Exception as e:
        logger.error(f"Error calculating Golden/Death Cross: {e}")
        return None


def calculate_supertrend(hist_data: pd.DataFrame, period: int = 10, 
                        multiplier: float = 3.0) -> Optional[float]:
    """
    Calculate SuperTrend indicator
    
    Args:
        hist_data: Historical OHLCV data
        period: ATR period (default 10)
        multiplier: ATR multiplier (default 3.0)
    
    Returns:
        SuperTrend value or None
    """
    try:
        if len(hist_data) < period:
            return None
        
        high = hist_data['High'].values
        low = hist_data['Low'].values
        close = hist_data['Close'].values
        
        # Calculate True Range
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        tr[0] = high[0] - low[0]
        
        # Calculate ATR
        atr = pd.Series(tr).rolling(window=period).mean().values
        
        # Calculate basic bands
        hl2 = (high + low) / 2
        upper_basic = hl2 + (multiplier * atr)
        lower_basic = hl2 - (multiplier * atr)
        
        # Calculate final bands and SuperTrend
        upper_final = np.full_like(upper_basic, np.nan)
        lower_final = np.full_like(lower_basic, np.nan)
        supertrend = np.full_like(close, np.nan)
        trend = np.full_like(close, np.nan)
        
        for i in range(period, len(close)):
            # Upper band
            if np.isnan(upper_final[i-1]) or upper_basic[i] < upper_final[i-1] or close[i-1] > upper_final[i-1]:
                upper_final[i] = upper_basic[i]
            else:
                upper_final[i] = upper_final[i-1]
            
            # Lower band
            if np.isnan(lower_final[i-1]) or lower_basic[i] > lower_final[i-1] or close[i-1] < lower_final[i-1]:
                lower_final[i] = lower_basic[i]
            else:
                lower_final[i] = lower_final[i-1]
            
            # Determine trend and SuperTrend
            if i == period:
                if close[i] <= upper_final[i]:
                    supertrend[i] = upper_final[i]
                    trend[i] = -1
                else:
                    supertrend[i] = lower_final[i]
                    trend[i] = 1
            else:
                if trend[i-1] == 1 and close[i] < lower_final[i]:
                    supertrend[i] = upper_final[i]
                    trend[i] = -1
                elif trend[i-1] == -1 and close[i] > upper_final[i]:
                    supertrend[i] = lower_final[i]
                    trend[i] = 1
                else:
                    supertrend[i] = supertrend[i-1]
                    trend[i] = trend[i-1]
        
        # Return last value
        if np.isnan(supertrend[-1]):
            return None
        
        return float(supertrend[-1])
        
    except Exception as e:
        logger.error(f"Error calculating SuperTrend: {e}")
        return None


def calculate_all_trend_indicators(daily_data: pd.DataFrame, weekly_data: pd.DataFrame, 
                                   price: float) -> Dict:
    """
    Calculate all trend indicators
    
    Args:
        daily_data: Daily historical OHLCV data
        weekly_data: Weekly historical OHLCV data
        price: Current stock price
    
    Returns:
        Dictionary with all calculated trend indicators
    """
    # Calculate SMAs
    sma50_1d = calculate_sma(daily_data, 50)
    sma200_1d = calculate_sma(daily_data, 200)
    sma200_1w = calculate_sma(weekly_data, 200)
    
    return {
        'SMA50_1D': sma50_1d,
        'SMA200_1D': sma200_1d,
        'SMA200_1W': sma200_1w,
        'SMA50_1D_AwayFromPrice_Pct': calculate_sma_distance_pct(price, sma50_1d),
        'SMA200_1D_AwayFromPrice_Pct': calculate_sma_distance_pct(price, sma200_1d),
        'GoldenCross_DeathCross': calculate_golden_death_cross(daily_data),
        'SuperTrend_1D': calculate_supertrend(daily_data, period=10, multiplier=3.0),
        'SuperTrend_1W': calculate_supertrend(weekly_data, period=10, multiplier=3.0)
    }