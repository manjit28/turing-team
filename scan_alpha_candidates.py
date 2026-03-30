import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def scan_alpha_candidates(tickers, spy_ticker='SPY', time_period='30m'):
    """
    Scan for stocks that are likely to outperform SPY for the remainder of the trading session.
    
    Args:
        tickers (list): List of stock tickers to scan
        spy_ticker (str): Ticker for the benchmark (default: SPY)
        time_period (str): Time period for data fetch (default: '30m')
    
    Returns:
        dict: Top candidate with detailed analysis
    """
    
    # Get current time
    now = datetime.now()
    
    # Create a single fetch for all tickers + SPY
    all_tickers = tickers + [spy_ticker]
    
    try:
        # Fetch 5-minute data for all tickers
        data = yf.download(all_tickers, period='1d', interval='5m')
        
        if data.empty:
            raise ValueError("No data returned from yfinance")
            
        # Get the most recent complete 5-minute bar
        data = data.dropna()
        
        # Calculate performance metrics for each ticker
        candidates = []
        
        for ticker in tickers:
            if ticker not in data.index:
                continue
                
            # Get ticker data
            ticker_data = data.loc[ticker]
            
            if len(ticker_data) == 0:
                continue
                
            # Calculate open and current price
            open_price = ticker_data['Open'].iloc[0]
            current_price = ticker_data['Close'].iloc[-1]
            
            # Calculate percentage change
            pct_change = ((current_price - open_price) / open_price) * 100
            
            # Get volume data
            volume = ticker_data['Volume'].iloc[-1]
            avg_volume = ticker_data['Volume'].mean()
            relative_volume = volume / avg_volume if avg_volume > 0 else 0
            
            # Calculate VWAP (simplified for this example)
            # In a real implementation, we'd calculate VWAP properly
            vwap = ticker_data['Close'].mean()
            
            # Get SPY data
            spy_data = data.loc[spy_ticker]
            if len(spy_data) == 0:
                continue
            spy_open = spy_data['Open'].iloc[0]
            spy_current = spy_data['Close'].iloc[-1]
            spy_pct_change = ((spy_current - spy_open) / spy_open) * 100
            
            # Calculate alpha score (relative strength)
            alpha_score = pct_change - spy_pct_change
            
            # Filter conditions
            above_vwap = current_price > vwap
            high_volume = relative_volume > 1.2
            
            if above_vwap and high_volume:
                candidates.append({
                    'ticker': ticker,
                    'pct_change': pct_change,
                    'spy_pct_change': spy_pct_change,
                    'alpha_score': alpha_score,
                    'current_price': current_price,
                    'vwap': vwap,
                    'volume': volume,
                    'relative_volume': relative_volume,
                    'above_vwap': above_vwap,
                    'high_volume': high_volume
                })
        
        # Sort by alpha score (descending)
        candidates.sort(key=lambda x: x['alpha_score'], reverse=True)
        
        if candidates:
            top_candidate = candidates[0]
            return {
                'top_candidate': top_candidate,
                'all_candidates': candidates,
                'timestamp': now.isoformat()
            }
        else:
            return {
                'top_candidate': None,
                'all_candidates': [],
                'timestamp': now.isoformat()
            }
            
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': now.isoformat()
        }

# Example usage:
if __name__ == "__main__":
    test_tickers = ['NVDA', 'AMD', 'TSLA', 'META', 'AMZN']
    result = scan_alpha_candidates(test_tickers)
    print("Results:")
    print(result)