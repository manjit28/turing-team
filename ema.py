__all__ = ["exponential_moving_average"]

from typing import List, Optional

def exponential_moving_average(values: List[float], span: int, min_periods: Optional[int] = None) -> List[float]:
    """
    Compute the exponential moving average (EMA) of a list of float values.
    
    Uses the standard EMA formula:
    alpha = 2/(span+1)
    EMA_t = alpha*value_t + (1-alpha)*EMA_{t-1}
    
    For the first EMA value, use the simple mean of the first min_periods data points if provided;
    otherwise use the first value.
    
    Args:
        values: List of float values to compute EMA for
        span: The span parameter for EMA calculation
        min_periods: Minimum number of values required before returning EMA values
        
    Returns:
        List of EMA values with None for positions where insufficient data exists
        
    Example:
        For values=[1,2,3,4,5], span=2, min_periods=3, the expected EMA list is 
        [None, None, 2.0, 3.0, 4.0]
    """
    if not values:
        return []
    
    if span <= 0:
        raise ValueError("Span must be positive")
    
    if min_periods is not None and min_periods <= 0:
        raise ValueError("Min periods must be positive or None")
    
    result = []
    ema = None
    
    for i, value in enumerate(values):
        if i < min_periods if min_periods is not None else i < 1:
            # Not enough data points yet
            result.append(None)
        elif i == min_periods - 1 if min_periods is not None else i == 0:
            # First EMA value - use simple mean of first min_periods values or first value
            if min_periods is not None:
                # Calculate mean of first min_periods values
                ema = sum(values[:min_periods]) / min_periods
            else:
                ema = value
            result.append(ema)
        else:
            # Calculate EMA using standard formula
            alpha = 2.0 / (span + 1)
            ema = alpha * value + (1 - alpha) * ema
            result.append(ema)
    
    return result