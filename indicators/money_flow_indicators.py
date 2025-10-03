"""
Money Flow Indicators Module
Calculates MFI, CMF, VPT, and buying/selling pressure metrics
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_mfi(hist_data: pd.DataFrame, period: int = 14) -> Optional[float]:
    """
    Calculate Money Flow Index (MFI)
    
    Args:
        hist_data: Historical OHLCV data
        period: MFI period (default 14)
    
    Returns:
        MFI value (0-100) or None
    """
    try:
        if len(hist_data) < period + 1:
            return None
        
        # Calculate typical price
        typical_price = (hist_data['High'] + hist_data['Low'] + hist_data['Close']) / 3
        
        # Calculate raw money flow
        money_flow = typical_price * hist_data['Volume']
        
        # Separate positive and negative money flow
        price_diff = typical_price.diff()
        positive_flow = money_flow.where(price_diff > 0, 0)
        negative_flow = money_flow.where(price_diff < 0, 0)
        
        # Calculate money flow ratio
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        money_ratio = positive_mf / negative_mf
        
        # Calculate MFI
        mfi = 100 - (100 / (1 + money_ratio))
        
        mfi_value = mfi.iloc[-1]
        
        if pd.isna(mfi_value) or np.isinf(mfi_value):
            return None
        
        return float(mfi_value)
        
    except Exception as e:
        logger.error(f"Error calculating MFI: {e}")
        return None


def calculate_cmf(hist_data: pd.DataFrame, period: int = 20) -> Optional[float]:
    """
    Calculate Chaikin Money Flow (CMF)
    
    Args:
        hist_data: Historical OHLCV data
        period: CMF period (default 20)
    
    Returns:
        CMF value (positive or negative) or None
    """
    try:
        if len(hist_data) < period:
            return None
        
        # Money Flow Multiplier
        mf_multiplier = ((hist_data['Close'] - hist_data['Low']) - 
                        (hist_data['High'] - hist_data['Close'])) / (hist_data['High'] - hist_data['Low'])
        
        # Handle division by zero (when high == low)
        mf_multiplier = mf_multiplier.fillna(0)
        
        # Money Flow Volume
        mf_volume = mf_multiplier * hist_data['Volume']
        
        # CMF
        cmf = mf_volume.rolling(window=period).sum() / hist_data['Volume'].rolling(window=period).sum()
        
        cmf_value = cmf.iloc[-1]
        
        if pd.isna(cmf_value) or np.isinf(cmf_value):
            return None
        
        return float(cmf_value)
        
    except Exception as e:
        logger.error(f"Error calculating CMF: {e}")
        return None


def calculate_buy_sell_pressure_ratio(hist_data: pd.DataFrame, period: int = 10) -> Optional[float]:
    """
    Calculate buying vs selling pressure ratio
    
    Args:
        hist_data: Historical OHLCV data
        period: Period for calculation (default 10)
    
    Returns:
        Pressure ratio (>1 means buying dominates) or None
    """
    try:
        if len(hist_data) < period:
            return None
        
        recent_data = hist_data.tail(period)
        
        # Calculate price changes
        price_changes = recent_data['Close'].diff()
        
        # Buying volume (up days)
        buying_volume = recent_data['Volume'].where(price_changes > 0, 0).sum()
        
        # Selling volume (down days)
        selling_volume = recent_data['Volume'].where(price_changes < 0, 0).sum()
        
        if selling_volume == 0:
            return None
        
        pressure_ratio = buying_volume / selling_volume
        
        return float(pressure_ratio)
        
    except Exception as e:
        logger.error(f"Error calculating buy/sell pressure: {e}")
        return None


def calculate_vpt_change(hist_data: pd.DataFrame, period: int = 11) -> Optional[float]:
    """
    Calculate Volume-Price Trend (VPT) percentage change
    
    Args:
        hist_data: Historical OHLCV data
        period: Period for change calculation (default 11)
    
    Returns:
        VPT percentage change over period or None
    """
    try:
        if len(hist_data) < period + 1:
            return None
        
        # Calculate VPT (cumulative)
        price_change_pct = hist_data['Close'].pct_change()
        vpt = (price_change_pct * hist_data['Volume']).cumsum()
        
        # Calculate percentage change over period
        current_vpt = vpt.iloc[-1]
        past_vpt = vpt.iloc[-(period + 1)]
        
        if past_vpt == 0:
            return None
        
        vpt_change_pct = ((current_vpt - past_vpt) / abs(past_vpt)) * 100
        
        return float(vpt_change_pct)
        
    except Exception as e:
        logger.error(f"Error calculating VPT change: {e}")
        return None


def calculate_all_money_flow_indicators(hist_data: pd.DataFrame) -> Dict:
    """
    Calculate all money flow indicators
    
    Args:
        hist_data: Historical OHLCV data
    
    Returns:
        Dictionary with all calculated money flow indicators
    """
    return {
        'MFI': calculate_mfi(hist_data, period=14),
        'CMF': calculate_cmf(hist_data, period=20),
        'BuySellPressureRatio': calculate_buy_sell_pressure_ratio(hist_data, period=10),
        'VPT_11D_Change': calculate_vpt_change(hist_data, period=11)
    }