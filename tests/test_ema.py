import sys
sys.path.insert(0, '/opt/agent-system-scratch/workspaces/SE-0004')

from ema import exponential_moving_average

def test_empty_input():
    assert exponential_moving_average([], span=2) == []

def test_span_positive():
    try:
        exponential_moving_average([1,2], span=0)
        assert False, "Should raise"
    except ValueError:
        pass

def test_min_periods_positive():
    try:
        exponential_moving_average([1,2], span=2, min_periods=0)
        assert False
    except ValueError:
        pass

def test_type_error_bug_fixed():
    # This used to raise TypeError due to ema being None
    result = exponential_moving_average([1, 2, 3, 4, 5], span=2, min_periods=3)
    # Should not raise
    assert len(result) == 5
    # First two should be None
    assert result[0] is None
    assert result[1] is None
    # First EMA is mean of first 3
    assert result[2] == 2.0
    # Subsequent values should be computed, not None, and not raise TypeError
    assert result[3] is not None
    assert result[4] is not None

def test_min_periods_none_first_value():
    result = exponential_moving_average([1,2,3], span=2, min_periods=None)
    # First value should be first element, not None
    assert result[0] == 1
    # No None values
    assert None not in result

def test_min_periods_one():
    result = exponential_moving_average([10,20,30], span=2, min_periods=1)
    # First EMA is mean of first 1 = 10
    assert result[0] == 10
    # Subsequent computed
    assert result[1] is not None
    assert result[2] is not None

def test_insufficient_data_all_none():
    result = exponential_moving_average([1,2], span=2, min_periods=5)
    assert result == [None, None]

if __name__ == "__main__":
    test_empty_input()
    test_span_positive()
    test_min_periods_positive()
    test_type_error_bug_fixed()
    test_min_periods_none_first_value()
    test_min_periods_one()
    test_insufficient_data_all_none()
    print("All tests passed")
