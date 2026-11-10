import pytest
from moving_average import moving_average, weighted_moving_average


def test_weighted_moving_average_known_values():
    values = [1, 2, 3, 4, 5]
    weights = [0.1, 0.3, 0.6]
    result = weighted_moving_average(values, weights)
    assert result[0] is None
    assert result[1] is None
    assert result[2] == pytest.approx(2.5)
    assert result[3] == pytest.approx(3.5)
    assert result[4] == pytest.approx(4.5)


def test_weighted_moving_average_output_length_and_padding():
    values = [10, 20, 30, 40, 50]
    weights = [1, 1, 1]
    result = weighted_moving_average(values, weights)
    assert len(result) == len(values)
    # First len(weights)-1 entries are None
    assert result[0] is None
    assert result[1] is None
    assert result[2] is not None
    assert result[3] is not None
    assert result[4] is not None
    # With equal weights, result should be simple average
    assert result[2] == pytest.approx(20.0)
    assert result[3] == pytest.approx(30.0)
    assert result[4] == pytest.approx(40.0)


def test_weighted_moving_average_empty_weights():
    with pytest.raises(ValueError):
        weighted_moving_average([1, 2, 3], [])


def test_weighted_moving_average_zero_sum_weights():
    with pytest.raises(ValueError):
        weighted_moving_average([1, 2, 3], [1, -1, 0])


def test_weighted_moving_average_normalization():
    values = [1, 2, 3, 4]
    weights = [1, 2, 3]  # sum = 6
    result = weighted_moving_average(values, weights)
    assert result[0] is None
    assert result[1] is None
    # (1*1 + 2*2 + 3*3)/6 = 14/6
    assert result[2] == pytest.approx(14/6)
    # (2*1 + 3*2 + 4*3)/6 = 20/6
    assert result[3] == pytest.approx(20/6)


def test_moving_average_unchanged():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = moving_average(data, 3)
    assert result[0] is None
    assert result[1] is None
    assert result[2] == pytest.approx(2.0)
    assert result[9] == pytest.approx(9.0)
