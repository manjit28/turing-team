def moving_average(data, window, min_periods=None):
    """
    Calculate the moving average of a list of numbers.
    
    Args:
        data: List of numbers
        window: Size of the moving window
        min_periods: Minimum number of observations required to have a value (default: window)
        
    Returns:
        List of moving averages with the same length as data, padded with None for insufficient data
    """
    if min_periods is None:
        min_periods = window
    
    if window <= 0:
        raise ValueError("Window must be positive")
    
    if min_periods < 0:
        raise ValueError("min_periods must be non-negative")
        
    if min_periods > window:
        raise ValueError("min_periods cannot exceed window")
    
    result = []
    
    for i in range(len(data)):
        # Calculate start index for the window
        start = max(0, i - window + 1)
        
        # Get the window of data
        window_data = data[start:i+1]
        
        # Check if we have enough data points
        if len(window_data) < min_periods:
            result.append(None)
        else:
            # Calculate the average
            avg = sum(window_data) / len(window_data)
            result.append(avg)
    
    return result


def weighted_moving_average(values, weights):
    """
    Calculate rolling weighted moving average.
    
    Args:
        values: List of numbers
        weights: List of weights in chronological order
        
    Returns:
        List of weighted moving averages with same length as values, padded with None for insufficient data
    """
    if not weights:
        raise ValueError("weights must be non-empty")
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise ValueError("sum of weights must be non-zero")
    window = len(weights)
    result = []
    for i in range(len(values)):
        if i + 1 < window:
            result.append(None)
        else:
            window_values = values[i - window + 1:i + 1]
            weighted_sum = sum(v * w for v, w in zip(window_values, weights))
            result.append(weighted_sum / weight_sum)
    return result


if __name__ == "__main__":
    # Test example
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    window_size = 3
    ma_result = moving_average(test_data, window_size)
    print(f"Data: {test_data}")
    print(f"Moving average (window={window_size}): {ma_result}")
