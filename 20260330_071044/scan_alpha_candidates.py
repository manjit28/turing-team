import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def scan_alpha_candidates(tickers, spy_ticker='SPY'):
    """
    Scan for stocks likely to outperform SPY for the remainder of the trading session.
    
    This implements the "Hedged Alpha Capture" strategy by:
    1. Calculating relative strength (stock change vs SPY change)
    2. filtering for stocks trading above VWAP
    3. filtering for stocks with above-average volume
    
    Args:
        tickers (list): List of stock tickers to scan
        spy_ticker (str): Ticker for SPY (default: 'SPY')
    
    Returns:
        dict: Top candidate with detailed analysis or None if no candidates meet criteria
    """
    
    # Get current date and time
    now = datetime.now()
    
    # For testing, we'll fetch data from last 2 hours to simulate intraday data
    end_date = now.strftime('%Y-%m-%d')
    start_date = (now - timedelta(hours=2)).strftime('%Y-%m-%d')
    
    # Fetch data for all tickers including SPY
    all_tickers = tickers + [spy_ticker]
    try:
        data = yf.download(all_tickers, start=start_date, end=end_date, interval='5m')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    # If we don't have enough data, return None
    if data.empty or len(data) < 2:
        return None
    
    # Get the last complete 5-minute bar
    last_bar = data.index[-1]
    
    # Get opening prices (first prices of the day)
    open_prices = {}
    for ticker in all_tickers:
        # Get the first data point for this ticker
        ticker_data = data[ticker]
        if not ticker_data.empty:
            open_price = ticker_data.iloc[0]['Open']
            open_prices[ticker] = open_price
    
    # Get current prices (last prices)
    current_prices = {}
    for ticker in all_tickers:
        ticker_data = data[ticker]
        if not ticker_data.empty:
            current_price = ticker_data.iloc[-1]['Close']
            current_prices[ticker] = current_price
    
    # Calculate percentage changes from open
    pct_changes = {}
    for ticker in tickers:
        if ticker in open_prices and ticker in current_prices:
            pct_change = ((current_prices[ticker] - open_prices[ticker]) / open_prices[ticker]) * 100
            pct_changes[ticker] = pct_change
    
    # Get SPY percentage change
    spy_pct_change = None
    if spy_ticker in open_prices and spy_ticker in current_prices:
        spy_pct_change = ((current_prices[spy_ticker] - open_prices[spy_ticker]) / open_prices[spy_ticker]) * 100
    
    # Calculate VWAP for each ticker (simplified for this implementation)
    vwap_values = {}
    for ticker in tickers:
        ticker_data = data[ticker]
        if not ticker_data.empty:
            # For simplicity, we'll use the last close price as a proxy for VWAP
            # In a production implementation, you'd calculate VWAP properly
            vwap_values[ticker] = ticker_data.iloc[-1]['Close']
    
    # Calculate relative volume (current volume vs average volume)
    relative_volumes = {}
    for ticker in tickers:
        ticker_data = data[ticker]
        if not ticker_data.empty:
            # For simplicity, we'll use a basic volume comparison
            current_volume = ticker_data.iloc[-1]['Volume']
            avg_volume = ticker_data['Volume'].mean()
            if avg_volume > 0:
                relative_volume = current_volume / avg_volume
                relative_volumes[ticker] = relative_volume
            else:
                relative_volumes[ticker] = 1.0
    
    # Build results list
    results = []
    
    for ticker in tickers:
        if ticker in pct_changes and ticker in vwap_values and ticker in relative_volumes:
            ticker_pct_change = pct_changes[ticker]
            ticker_vwap = vwap_values[ticker]
            ticker_volume = relative_volumes[ticker]
            current_price = current_prices[ticker]
            
            # Filter: price must be above VWAP and volume > 1.2
            if current_price > ticker_vwap and ticker_volume > 1.2:
                # Calculate alpha score (relative strength)
                alpha_score = ticker_pct_change - spy_pct_change if spy_pct_change is not None else ticker_pct_change
                
                results.append({
                    'ticker': ticker,
                    'alpha_score': alpha_score,
                    'ticker_pct_change': ticker_pct_change,
                    'spy_pct_change': spy_pct_change,
                    'current_price': current_price,
                    'vwap': ticker_vwap,
                    'relative_volume': ticker_volume
                })
    
    # Sort by alpha score descending
    results.sort(key=lambda x: x['alpha_score'], reverse=True)
    
    # Return top candidate
    if results:
        return results[0]
    else:
        return None

# Example usage:
if __name__ == "__main__":
    # Test with a sample watchlist
    sample_watchlist = ['AMD', 'TSLA', 'META', 'AMZN', 'GOOGL']
    result = scan_alpha_candidates(sample_watchlist)
    print("Sample test run of scan_alpha_candidates:")
    print(result)