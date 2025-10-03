"""
Stock Screener Flask Application
Main web application serving the screener interface
"""

from flask import Flask, render_template, jsonify, request
import json
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

from data_processor import DataProcessor
from excel_manager import ExcelManager

# Setup Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/screener.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global data storage (will be replaced by LocalStorage on frontend)
current_stock_data = None
last_update_time = None


@app.route('/')
def index():
    """Main screener interface"""
    return render_template('screener.html')


@app.route('/api/stocks')
def get_stocks():
    """Get all stock data"""
    global current_stock_data, last_update_time
    
    try:
        if current_stock_data is None:
            return jsonify({
                'success': False,
                'message': 'No data loaded. Click Refresh Data to fetch stocks.',
                'data': []
            })
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(current_stock_data)} stocks',
            'last_update': last_update_time,
            'data': current_stock_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_stocks: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': []
        }), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh stock data by processing all stocks"""
    global current_stock_data, last_update_time
    
    try:
        logger.info("Starting data refresh...")
        
        processor = DataProcessor()
        results_df = processor.process_all_stocks()
        
        if results_df.empty:
            return jsonify({
                'success': False,
                'message': 'No stocks processed'
            }), 500
        
        # Convert DataFrame to list of dicts, replacing NaN/Inf with None
        current_stock_data = results_df.replace([np.nan, np.inf, -np.inf], None).to_dict('records')
        last_update_time = datetime.now().isoformat()
        
        # Save to processed folder
        processor.save_processed_data(results_df)
        
        successful = len([s for s in current_stock_data if 'Error' not in s or s['Error'] is None])
        
        logger.info(f"Data refresh complete: {successful} stocks processed")
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {successful} stocks',
            'last_update': last_update_time,
            'total_stocks': len(current_stock_data),
            'successful': successful
        })
        
    except Exception as e:
        logger.error(f"Error in refresh_data: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/status')
def get_status():
    """Get system status"""
    global current_stock_data, last_update_time
    
    try:
        excel_mgr = ExcelManager()
        
        status = {
            'data_loaded': current_stock_data is not None,
            'stocks_count': len(current_stock_data) if current_stock_data else 0,
            'last_update': last_update_time,
            'excel_file_exists': excel_mgr.validate_excel_file(),
            'cache_stats': {}
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("STOCK SCREENER - Web Application")
    print("="*60)
    print("\nStarting Flask server...")
    print("Web interface: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)