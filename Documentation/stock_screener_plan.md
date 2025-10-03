# Stock Screener Project - Design & Planning Document

## Project Overview

**Goal**: Create an integrated stock screener that combines data analysis capabilities with TradingView automation for post-market analysis and chart viewing.

**Use Case**: After market close, fetch comprehensive technical data for all stocks, apply filters to screen for opportunities, and launch selected stocks in TradingView Desktop for detailed chart analysis.

## Core Requirements

### Functional Requirements
- Excel-like sortable/filterable interface displaying 27 technical metrics
- Manual data refresh (no auto-refresh)
- One-click TradingView Desktop integration
- Multiple watchlist management
- Conditional formatting for visual screening
- Data persistence for extended analysis sessions

### Technical Requirements  
- Flask web application
- LocalStorage for data persistence
- Excel-based watchlist management
- Parallel data fetching with rate limiting
- Responsive table interface

## Data Architecture

## Data Storage Strategy

### Data Flow & Storage Locations

**Primary Storage: Browser LocalStorage**
- Final processed metrics (27 per stock)
- Fast access for filtering/sorting
- Persists across browser sessions

**File System Storage**

**data/cache/ (YFinance Raw Data Cache)**
```
data/cache/
├── RELIANCE_NS_2024-01-20.json    # Raw OHLCV historical data
├── TCS_NS_2024-01-20.json          # 5 years daily + weekly data
├── NIFTY_2024-01-20.json           # Nifty index data for relative strength
└── cache_index.json                # Cache metadata & timestamps
```
*Purpose: Cache raw YFinance data to avoid re-fetching on same day*

**data/processed/ (Historical Processed Data)**
```
data/processed/
├── stock_metrics_2024-01-20.json  # All 27 metrics for all stocks
├── stock_metrics_2024-01-19.json  # Previous day's calculations
├── stock_metrics_2024-01-18.json  # Day-by-day historical data
└── processing_log.json            # Calculation logs & errors
```
*Purpose: Historical comparison & trend analysis across multiple days*

**data/exports/ (User Downloaded Files)**
```
data/exports/
├── banking_high_rsi_2024-01-20_15-30.xlsx     # Filtered banking stocks
├── momentum_breakouts_2024-01-20_16-45.csv    # Custom filtered results  
├── all_stocks_screened_2024-01-20.xlsx        # Complete dataset export
└── watchlist_backup_2024-01-20.xlsx           # Watchlist sheets backup
```
*Purpose: User-requested downloads after filtering/sorting operations*

### Data Retention Strategy

**Based on Indicator Requirements:**

**Cache Retention (data/cache/)**
- Raw OHLCV data: 5+ years (needed for 5YearHigh/Low, SMA200, etc.)
- Auto-refresh only current day's data
- Keep historical cache for indicator calculations

**Processed Data Retention (data/processed/)**  
- Daily snapshots: 90 days (for trend comparison)
- Weekly snapshots: 1 year (for longer-term analysis)
- Monthly snapshots: 5 years (for historical perspective)

**Export Retention (data/exports/)**
- User downloads: 30 days (auto-cleanup)
- Important exports: Manual deletion only

### Storage Configuration

**config.json Storage Settings**
```json
{
  "storage": {
    "enable_cache": true,
    "cache_retention_years": 5,
    "processed_retention_days": 90,
    "export_retention_days": 30,
    "auto_cleanup": true,
    "backup_watchlists": true
  },
  "data_requirements": {
    "daily_history_years": 5,
    "weekly_history_years": 5,
    "nifty_cache_years": 5
  }
}
```

### Data Processing Workflow

**Step 1: Cache Check & Fetch**
```python
def fetch_stock_data(ticker, date):
    cache_file = f"data/cache/{ticker}_{date}.json"
    
    if cache_exists(cache_file) and is_current_day(date):
        return load_from_cache(cache_file)
    else:
        # Fetch 5 years of data for all indicators
        data = yf.Ticker(ticker).history(period="5y", interval="1d")
        weekly_data = yf.Ticker(ticker).history(period="5y", interval="1wk")
        save_to_cache(cache_file, data, weekly_data)
        return data, weekly_data
```

**Step 2: Process & Store Historical Snapshots**
```python
def process_and_store(all_stock_data, date):
    processed_metrics = calculate_all_indicators(all_stock_data)
    
    # Store for historical comparison
    processed_file = f"data/processed/stock_metrics_{date}.json"
    save_processed_data(processed_file, processed_metrics)
    
    # Store in LocalStorage for immediate use
    return processed_metrics
```

**Step 3: Export Handler**
```python 
def export_filtered_data(filtered_data, export_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    export_file = f"data/exports/{export_name}_{timestamp}.xlsx"
    
    filtered_data.to_excel(export_file, index=False)
    return export_file
```

## Excel Structure

### Master Sheet (READ-ONLY)
**Sheet: "Master"**
| Stock_Name | YF_Ticker | TV_Ticker | Sector | Industry |
|------------|-----------|-----------|--------|----------|
| Reliance Industries | RELIANCE.NS | NSE:RELIANCE | Oil & Gas | Oil Refining |
| TCS | TCS.NS | NSE:TCS | IT | Software Services |
| HDFC Bank | HDFCBANK.NS | NSE:HDFCBANK | Banking | Private Bank |
| Apple Inc | AAPL | NASDAQ:AAPL | Technology | Consumer Electronics |

**Purpose**: Complete stock universe with all required data - maintained manually by user

### Watchlist Sheets (READ-WRITE) 
**Sheet names = Watchlist names**

Example - Sheet: "Banking"
| Stock_Name | Added_Date | Priority | Target_Price | Stop_Loss | Notes |
|------------|------------|----------|--------------|-----------|-------|
| HDFC Bank | 2024-01-15 | High | 1800 | 1500 | Q4 results strong |

**Purpose**: Dynamic trading watchlists managed by script

## Modular Indicator System

### Indicator Organization

**indicators/price_indicators.py**
- Price, TrailingPE
- 52WeekHigh, 52WeekLow, 5YearHigh, 5YearLow
- Basic price-based calculations

**indicators/trend_indicators.py**
- SuperTrend_1D, SuperTrend_1W
- SMA50_1D, SMA200_1D, SMA200_1W
- SMA50_1D_AwayFromPrice_Pct, SMA200_1D_AwayFromPrice_Pct
- GoldenCross_DeathCross

**indicators/momentum_indicators.py**
- RSI_1D, RSI_1W
- MACD_1D, MACD_Signal_1D, MACD_1W, MACD_Signal_1W

**indicators/money_flow_indicators.py**
- MFI (Money Flow Index) - Volume-weighted RSI (0-100 scale)
- CMF (Chaikin Money Flow) - 20-day buying/selling pressure
- BuySellPressureRatio - Custom: (Up-day volume / Down-day volume) over 10 days

**indicators/strength_indicators.py**
- RelStrength_18d, RelStrength_55D, RelStrength_81d

### Configuration System

**indicators/indicator_config.json**
```json
{
  "active_indicators": {
    "price": ["Price", "TrailingPE", "52WeekHigh", "52WeekLow"],
    "trend": ["SuperTrend_1D", "SMA50_1D", "SMA200_1D"],
    "momentum": ["RSI_1D", "MACD_1D"],
    "volume": ["VolumeChangePct", "RelVol_1D_over_10D"],
    "strength": ["RelStrength_55D"]
  },
  "indicator_settings": {
    "RSI_period": 14,
    "SuperTrend_period": 10,
    "SuperTrend_multiplier": 3.0,
    "MACD_fast": 12,
    "MACD_slow": 26,
    "MACD_signal": 9
  }
}
```

### Indicator Registry System

**indicators/__init__.py**
```python
from .price_indicators import *
from .trend_indicators import *
from .momentum_indicators import *
from .volume_indicators import *
from .strength_indicators import *

def get_all_indicators():
    """Return all available indicator functions"""
    return {
        'price': get_price_indicators(),
        'trend': get_trend_indicators(),
        'momentum': get_momentum_indicators(),
        'volume': get_volume_indicators(),
        'strength': get_strength_indicators()
    }

def calculate_all_metrics(stock_data, config):
    """Calculate all active indicators for a stock"""
    results = {}
    active = config['active_indicators']
    
    for category, indicators in active.items():
        category_results = calculate_category(category, stock_data, indicators, config)
        results.update(category_results)
    
    return results
```

### Easy Modification Benefits

**Adding New Indicator**
1. Create function in appropriate file
2. Add to indicator_config.json
3. Automatically included in calculations

**Removing Indicator** 
1. Remove from indicator_config.json
2. Indicator skipped without code changes

**Changing Parameters**
1. Modify values in indicator_config.json
2. No code modification needed

**Custom Indicators**
1. Create new file: `indicators/custom_indicators.py`
2. Add to __init__.py imports
3. Add to configuration

### Price & Valuation
- Price
- Price_1D_Change_Pct - Day-over-day price change percentage
- Price_5D_Change_Pct - 5-day price change percentage  
- Price_11D_Change_Pct - 11-day price change percentage
- TrailingPE
- 52WeekHigh, 52WeekLow
- 5YearHigh, 5YearLow

### Technical Indicators  
- SuperTrend_1D, SuperTrend_1W
- RSI_1D, RSI_1W
- MACD_1D, MACD_Signal_1D, MACD_1W, MACD_Signal_1W
- MACD_Signal_1D (Buy/Sell/Neutral) - Daily timeframe crossover signal
- MACD_Signal_1W (Buy/Sell/Neutral) - Weekly timeframe crossover signal
- SMA50_1D, SMA200_1D, SMA200_1W
- GoldenCross_DeathCross

### Moving Average Analysis
- SMA50_1D_AwayFromPrice_Pct
- SMA200_1D_AwayFromPrice_Pct

### Volume Analysis
- VolumeChangePct
- RelVol_1D_over_10D, RelVol_1D_over_30D
- RelVol_10D_over_30D, RelVol_10D_over_60D, RelVol_10D_over_90D

### Relative Strength
- RelStrength_18d, RelStrength_55D, RelStrength_81d

## User Interface Design

### Main Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Data from: Jan 20, 2024 (4:15 PM) | [Refresh Data] | 147 stocks │
├─────────────────────────────────────────────────────────────────┤
│ Watchlist: [All Stocks ▼] [+ New] [Delete] [Add Stock]         │
├─────────────────────────────────────────────────────────────────┤
│ Quick Filters:                                                  │
│ [RSI <30] [RSI >70] [Bullish] [Bearish] [High Vol] [Banking]   │
├─────────────────────────────────────────────────────────────────┤
│ Active Filters: [RSI: >60 ×] [Sector: Banking ×] [Clear All]   │
├─────────────────────────────────────────────────────────────────┤
│ Stock Name ↑ | Sector | Price ↓ | RSI | SuperTrend | Volume... │
│ Reliance     | O&G    | 2845   | 65  | Bullish    | +45%   ... │
└─────────────────────────────────────────────────────────────────┘
```

### Filtering System

**Quick Filter Buttons**
- RSI: [<30] [30-70] [>70]
- SuperTrend: [Bullish] [Bearish] 
- Volume: [High >150%] [Normal] [Low <50%]
- Golden Cross: [GC] [DC] [Crossing]

**Range Filters**
- Price: [Min: ___] [Max: ___]
- RSI: [Min: ___] [Max: ___] 
- Volume Change %: [Min: ___] [Max: ___]

**Dropdown Filters**
- Sector: Alphabetically sorted A→Z
- Exchange: NSE, BSE, NASDAQ, NYSE

**Active Filter Display**
- Show filter chips: [Filter Name: Value ×]
- [Clear All] button
- Result counter: "Showing 23 of 150 stocks"

### Conditional Formatting Rules

**RSI Coloring**
- RSI > 70: Light red background (Overbought)
- RSI < 30: Light green background (Oversold)

**SuperTrend Indication** 
- Price > SuperTrend: Green background (Bullish)
- Price < SuperTrend: Red background (Bearish)

**Volume Highlighting**
- RelVol > 2.0: Bold text + blue background
- RelVol > 1.5: Bold text

**MACD Signals**
- MACD > Signal: Green left border
- MACD < Signal: Red left border

**Golden/Death Cross**
- "GC": Green cell with up arrow
- "DC": Red cell with down arrow
- "Crossing": Yellow cell with warning icon

## Watchlist Management

### Web Interface Controls

**Watchlist Operations**
- Create new watchlist (popup dialog)
- Delete watchlist (confirmation required)
- Rename watchlist
- Clone watchlist

**Stock Management**
- Add stock to watchlist (from master list or search)
- Remove selected stocks (checkbox selection)
- Move stocks between watchlists
- Bulk operations

**UI Components**
```html
<select id="watchlistSelect">
    <option value="all">All Stocks (1247)</option>
    <option value="Banking">Banking (15)</option>
    <option value="Tech_Breakouts">Tech Breakouts (8)</option>
</select>

<button onclick="createWatchlist()">+ New Watchlist</button>
<button onclick="addStock()">+ Add Stock</button>
<button onclick="removeSelected()">Remove Selected</button>
```

### Backend API Endpoints

**Watchlist Management**
- GET /api/watchlists - List all watchlists
- POST /api/watchlist/create - Create new watchlist
- DELETE /api/watchlist/delete - Delete watchlist
- PUT /api/watchlist/rename - Rename watchlist

**Stock Management**
- POST /api/watchlist/{name}/add - Add stock to watchlist
- DELETE /api/watchlist/{name}/remove - Remove stock
- GET /api/watchlist/{name}/stocks - Get stocks in watchlist
- PUT /api/stock/move - Move stock between watchlists

## TradingView Integration

### Ticker System
**Direct Excel Mapping**
- Both YFinance and TradingView tickers stored in Excel Master sheet
- No runtime mapping logic needed
- Simple direct lookup from Excel data

### Launch Process
1. User clicks stock name in table
2. Get TV_Ticker directly from Excel data
3. Activate TradingView Desktop window  
4. Type ticker in search box
5. Press Enter to load chart

## File Structure

```
StockScreener/
├── app.py                    # Main Flask application
├── data_processor.py         # Stock data fetching & orchestration
├── tradingview_launcher.py   # TradingView automation
├── watchlist.xlsx            # Excel with Master + watchlist sheets
├── config.json              # Settings & configurations
├── run_screener.bat          # One-click startup script
├── setup_screener.bat        # Environment setup script
├── data/                     # Data storage folder
│   ├── cache/               # Temporary YFinance raw data cache
│   ├── processed/           # Final calculated metrics
│   └── exports/             # User exported files
├── indicators/               # Technical indicators module
│   ├── __init__.py          # Indicator registry & loader
│   ├── price_indicators.py   # Price, PE, 52-week high/low
│   ├── trend_indicators.py   # SuperTrend, SMA, Golden Cross
│   ├── momentum_indicators.py # RSI, MACD calculations
│   ├── volume_indicators.py  # Volume ratios & relative volume
│   ├── money_flow_indicators.py # MFI, CMF, Pressure Ratio (NEW)
│   ├── strength_indicators.py # Relative strength calculations
│   └── indicator_config.json # Active indicators configuration
├── templates/
│   └── screener.html        # Main interface template
├── static/
│   ├── css/
│   │   └── screener.css     # Conditional formatting styles
│   └── js/
│       └── screener.js      # Table functionality & filtering
└── requirements.txt         # Python dependencies
```

## Implementation Phases

### Phase 1: Core Functionality
- Basic table with 27 metrics
- Manual refresh button
- Excel-like sorting (click headers)
- Basic filters (RSI ranges, sector dropdown)
- TradingView clicking integration
- LocalStorage data persistence

### Phase 2: Enhanced Filtering  
- Quick filter buttons
- Active filter display with chips
- Color-based filtering
- Multi-column sorting
- Advanced conditional formatting

### Phase 3: Watchlist Management
- Web interface for create/delete watchlists
- Add/remove stocks functionality
- Bulk operations (move, delete multiple)
- Search and add stocks from master list

### Phase 4: Polish & Optimization
- Loading indicators and error handling
- Export filtered results to Excel
- Performance optimizations
- Better mobile responsiveness

## One-Click Startup System

### Setup Script (setup_screener.bat)
```batch
@echo off
title Stock Screener - Setup
color 0B
echo.
echo ================================
echo   STOCK SCREENER - SETUP
echo ================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✓ Python found

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install packages
echo Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Create data directories
if not exist "data" mkdir data
if not exist "data\cache" mkdir data\cache
if not exist "data\processed" mkdir data\processed
if not exist "data\exports" mkdir data\exports

REM Check for watchlist file
if not exist "watchlist.xlsx" (
    echo.
    echo WARNING: watchlist.xlsx not found!
    echo Please create your Excel file with Master sheet
    echo.
)

echo.
echo ✓ Setup complete!
echo Run "run_screener.bat" to start the application
pause
```

### Run Script (run_screener.bat)
```batch
@echo off
title Stock Screener - Running
color 0A
cls

echo.
echo ================================
echo   STOCK SCREENER - STARTING
echo ================================
echo.

REM Check if setup was run
if not exist "venv" (
    echo ERROR: Setup not complete. Run "setup_screener.bat" first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check for watchlist
if not exist "watchlist.xlsx" (
    echo WARNING: watchlist.xlsx not found!
    echo The app will start but you need to create your Excel file.
    echo.
)

REM Start the application
echo Starting Stock Screener...
echo.
echo 🌐 Web interface will open at: http://localhost:5000
echo 💡 Make sure TradingView Desktop is installed
echo ⏹️  Press Ctrl+C to stop the server
echo.

REM Start Flask app and open browser
start "" "http://localhost:5000"
python app.py

echo.
echo 👋 Stock Screener stopped.
pause
```

## Key Design Decisions

### Filter Behavior
- Filters reset on page refresh (no persistence)
- All filters use AND logic (simple approach)
- Sector dropdown sorted alphabetically A→Z
- Export shows only filtered results

### Data Management
- No duplicate data fetching (unique tickers only)
- Master sheet remains read-only for script
- Watchlist sheets fully managed by web interface
- Data freshness check on app load

### User Experience Priorities
1. Fast screening after data load (client-side filtering)
2. Intuitive Excel-like interface
3. One-click TradingView integration
4. Visual indicators for quick screening
5. Flexible watchlist organization

## Technical Considerations

### Performance
- Parallel data fetching (5 concurrent threads)
- Client-side filtering for responsiveness
- Minimal data storage (processed metrics only)
- Efficient conditional formatting with CSS classes

### Error Handling
- Failed ticker fetches shown as "Error" rows
- Graceful handling of missing TradingView window
- Data freshness warnings
- Fallback to cached data when possible

### Future Enhancements (Post-Phase 4)
- Multiple timeframe analysis
- Custom alert system
- Historical data comparison
- Advanced charting integration
- Mobile app version

---

*This document will be updated as the project evolves and requirements change during development.*