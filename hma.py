import pandas as pd
import numpy as np

def wma(prices: pd.Series, window: int) -> pd.Series:
    """Calculate Weighted Moving Average."""
    weights = np.arange(1, window + 1)
    return prices.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate Hull Moving Average (HMA).
    
    The HMA is a weighted moving average that reduces lag while maintaining smoothness.
    
    Args:
        prices: pandas Series of price values
        window: The period for the HMA calculation
        
    Returns:
        pandas Series of HMA values with same index as input, NaN where insufficient data
    """
    # Step 1: Compute WMA over window periods
    wma_window = wma(prices, window)
    
    # Step 2: Compute WMA over window/2 periods, double it, subtract WMA from step 1
    wma_half = wma(prices, window // 2)
    half_wma_doubled = wma_half * 2
    diff = half_wma_doubled - wma_window
    
    # Step 3: Compute WMA of the result over sqrt(window) periods
    sqrt_window = int(np.sqrt(window))
    hma_result = wma(diff, sqrt_window)
    
    return hma_result

if __name__ == "__main__":
    # Create a simple price series
    prices = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print("Input prices:")
    print(prices)
    print("\nHMA with window=5:")
    result = hma(prices, 5)
    print(result)