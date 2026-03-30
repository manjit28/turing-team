import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_vwap(df):
    """Calculate Volume Weighted Average Price"""
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['TP'] * df['Volume']
    vwap = df['TPV'].sum() / df['Volume'].sum()
    return vwap

def scan_alpha_candidates(tickers, spy_ticker='SPY'):
    """
    Scan for stocks that are likely to outperform SPY for the rest of the trading session.
    
    Args:
        tickers (list): List of stock tickers to scan
        spy_ticker (str): Ticker for SPY (default: 'SPY')
        
    Returns:
        list: Ranked list of candidates with alpha scores and analysis
    """
    # Get current time and calculate start time (e.g., 30 minutes ago)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    # Fetch 5-minute data for all tickers plus SPY
    data = yf.download(tickers + [spy_ticker], period="1d", interval="5m")
    
    if data.empty:
        return "No data available"
    
    # Get the last 30 minutes of data
    if len(data) < 10:
        return "Insufficient data"
    
    # Get the last complete 5-minute bars (at least 6 bars for VWAP calculation)
    recent_data = data.tail(30)  # Get last 30 bars (2.5 hours of data)
    
    # Calculate open prices and current prices for all tickers
    open_prices = {}
    current_prices = {}
    volumes = {}
    avg_volumes = {}
    
    # Process each ticker
    for ticker in tickers + [spy_ticker]:
        ticker_data = recent_data[ticker]
        if len(ticker_data) < 10:
            continue
            
        open_prices[ticker] = ticker_data['Open'].iloc[0]
        current_prices[ticker] = ticker_data['Close'].iloc[-1]
        volumes[ticker] = ticker_data['Volume'].iloc[-1]
        avg_volumes[ticker] = ticker_data['Volume'].mean()
    
    # Calculate percentage changes from open
    stock_changes = {}
    spy_change = 0
    
    for ticker in tickers:
        if ticker in open_prices and ticker in current_prices:
            stock_changes[ticker] = ((current_prices[ticker] - open_prices[ticker]) / open_prices[ticker]) * 100
    
    if spy_ticker in open_prices and spy_ticker in current_prices:
        spy_change = ((current_prices[spy_ticker] - open_prices[spy_ticker]) / open_prices[spy_ticker]) * 100
    
    # Calculate VWAP for each stock
    vwap_values = {}
    for ticker in tickers:
        if ticker in recent_data:
            ticker_data = recent_data[ticker]
            vwap_values[ticker] = calculate_vwap(ticker_data)
    
    # Calculate alpha scores and filter
    candidates = []
    for ticker in tickers:
        if ticker not in stock_changes or ticker not in vwap_values:
            continue
            
        # Get current price and VWAP
        current_price = current_prices[ticker]
        vwap = vwap_values[ticker]
        
        # Get current volume and average volume
        current_vol = volumes[ticker]
        avg_vol = avg_volumes[ticker]
        
        # Calculate relative volume (RVOL)
        rvol = current_vol / avg_vol if avg_vol > 0 else 0
        
        # Calculate alpha score (relative strength)
        alpha_score = stock_changes[ticker] - spy_change
        
        # Apply filters
        if current_price > vwap and rvol > 1.2:
            candidates.append({
                'ticker': ticker,
                'alpha_score': alpha_score,
                'stock_change': stock_changes[ticker],
                'spy_change': spy_change,
                'current_price': current_price,
                'vwap': vwap,
                'volume': current_vol,
                'avg_volume': avg_vol,
                'rvol': rvol
            })
    
    # Sort by alpha score (descending)
    candidates.sort(key=lambda x: x['alpha_score'], reverse=True)
    
    return candidates