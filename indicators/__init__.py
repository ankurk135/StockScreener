"""
Technical Indicators Module
Modular system for calculating stock technical indicators
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Import indicator modules (will add as we create them)
from . import price_indicators
from . import trend_indicators
from . import momentum_indicators

__all__ = ['price_indicators', 'trend_indicators', 'momentum_indicators']

def load_indicator_config():
    """Load indicator configuration from JSON file"""
    config_path = Path(__file__).parent / 'indicator_config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Indicator config not found, using defaults")
        return {}

def get_active_indicators():
    """Get list of active indicators from config"""
    config = load_indicator_config()
    return config.get('active_indicators', {})