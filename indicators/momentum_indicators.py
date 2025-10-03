"""
Momentum Indicators Module
Calculates RSI, MACD and other momentum indicators
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def calculate_rsi(hist_data: pd.DataFrame, period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        hist_data: Historical OHLCV data
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    try:
        if len(hist_data) < period + 1:
            return None
        
        # Calculate price changes
        delta = hist_data['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_value = rsi.iloc[-1]
        
        if pd.isna(rsi_value) or np.isinf(rsi_value):
            return None
        
        return float(rsi_value)
        
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return None


def calculate_macd(hist_data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate MACD line and Signal line
    
    Args:
        hist_data: Historical OHLCV data
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line EMA period (default 9)
    
    Returns:
        Tuple of (MACD line, Signal line) or (None, None) if insufficient data
    """
    try:
        if len(hist_data) < slow + signal:
            return None, None
        
        close_prices = hist_data['Close']
        
        # Calculate EMAs
        ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
        ema_slow = close_prices.ewm(span=slow, adjust=False).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD line)
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        macd_value = macd_line.iloc[-1]
        signal_value = signal_line.iloc[-1]
        
        if pd.isna(macd_value) or pd.isna(signal_value):
            return None, None
        
        return float(macd_value), float(signal_value)
        
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return None, None


def calculate_macd_crossover_signal(hist_data: pd.DataFrame, fast: int = 12, 
                                    slow: int = 26, signal: int = 9) -> Optional[str]:
    """
    Detect MACD crossover signals
    
    Args:
        hist_data: Historical OHLCV data
        fast, slow, signal: MACD parameters
    
    Returns:
        "BUY", "SELL", "BULLISH", "BEARISH", or None
    """
    try:
        if len(hist_data) < slow + signal + 1:
            return None
        
        close_prices = hist_data['Close']
        
        # Calculate MACD and Signal
        ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
        ema_slow = close_prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Current and previous values
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        
        # Check for crossover
        if prev_macd <= prev_signal and current_macd > current_signal:
            return "BUY"  # Bullish crossover
        elif prev_macd >= prev_signal and current_macd < current_signal:
            return "SELL"  # Bearish crossover
        elif current_macd > current_signal:
            return "BULLISH"  # Above signal, no fresh cross
        elif current_macd < current_signal:
            return "BEARISH"  # Below signal, no fresh cross
        else:
            return "NEUTRAL"
            
    except Exception as e:
        logger.error(f"Error calculating MACD crossover signal: {e}")
        return None


def calculate_all_momentum_indicators(daily_data: pd.DataFrame, weekly_data: pd.DataFrame) -> Dict:
    """
    Calculate all momentum indicators
    
    Args:
        daily_data: Daily historical OHLCV data
        weekly_data: Weekly historical OHLCV data
    
    Returns:
        Dictionary with all calculated momentum indicators
    """
    # Calculate MACD for daily
    macd_1d, macd_signal_1d = calculate_macd(daily_data)
    macd_crossover_1d = calculate_macd_crossover_signal(daily_data)
    
    # Calculate MACD for weekly
    macd_1w, macd_signal_1w = calculate_macd(weekly_data)
    macd_crossover_1w = calculate_macd_crossover_signal(weekly_data)
    
    return {
        'RSI_1D': calculate_rsi(daily_data, period=14),
        'RSI_1W': calculate_rsi(weekly_data, period=14),
        'MACD_1D': macd_1d,
        'MACD_Signal_1D': macd_signal_1d,
        'MACD_Crossover_Signal_1D': macd_crossover_1d,
        'MACD_1W': macd_1w,
        'MACD_Signal_1W': macd_signal_1w,
        'MACD_Crossover_Signal_1W': macd_crossover_1w
    }