import math
import pytest
from backtest import BacktestResult, backtest_daily_closes
from moving_average import moving_average, weighted_moving_average
from ema import exponential_moving_average


def test_hand_calculated_timing_metrics():
    closes = [100, 110, 99, 132]
    signals = [1, 1, -1, 0]
    result = backtest_daily_closes(closes, lambda c: signals)
    assert result.equity_curve == pytest.approx([1.0, 1.1, 0.99, 0.66], rel=1e-9)
    assert result.total_return == pytest.approx(-0.34, rel=1e-9)
    assert result.max_drawdown == pytest.approx(0.40, rel=1e-9)
    assert result.trade_count == 2


def test_warmup_flat_no_return_no_trades():
    closes = [100, 101, 102, 103]
    # signals start with None, then flat, then long
    signals = [None, None, 1, 1]
    result = backtest_daily_closes(closes, lambda c: signals)
    # p[1]=None->0, p[2]=None->0, p[3]=1
    # equity: 1.0, 1.0, 1.0, 1.0 * (1 + 1*(103/102-1)) ≈ 1.0098
    assert result.equity_curve[0] == pytest.approx(1.0)
    assert result.equity_curve[1] == pytest.approx(1.0)
    assert result.equity_curve[2] == pytest.approx(1.0)
    assert result.equity_curve[3] > 1.0
    # trades: 0->0 no, 0->0 no, 0->1 yes => 1 trade
    assert result.trade_count == 1


def test_trade_count_entry_exit_unchanged_reversal():
    # entry
    closes = [100, 110]
    signals = [1, 0]
    res = backtest_daily_closes(closes, lambda c: signals)
    assert res.trade_count == 1  # 0 ->1

    # exit
    closes = [100, 110, 100]
    signals = [1, 1, 0]
    res = backtest_daily_closes(closes, lambda c: signals)
    # p1=1, p2=1, p3? Wait n=3, p1=1, p2=1 -> trades: 0->1 =1, 1->1=0 => total 1
    # final signal 0 not executed
    assert res.trade_count == 1

    # unchanged
    closes = [100, 110, 120]
    signals = [1, 1, 1]
    res = backtest_daily_closes(closes, lambda c: signals)
    assert res.trade_count == 1

    # direct reversal +1 to -1
    closes = [100, 110, 100]
    signals = [1, -1, 0]
    res = backtest_daily_closes(closes, lambda c: signals)
    # p1=1, p2=-1 => trade 0->1, 1->-1 => 2 trades
    assert res.trade_count == 2

    # reversal -1 to +1
    closes = [100, 90, 100]
    signals = [-1, 1, 0]
    res = backtest_daily_closes(closes, lambda c: signals)
    assert res.trade_count == 2


def test_single_close():
    closes = [100]
    signals = [1]
    result = backtest_daily_closes(closes, lambda c: signals)
    assert result.equity_curve == [1.0]
    assert result.total_return == pytest.approx(0.0)
    assert result.max_drawdown == pytest.approx(0.0)
    assert result.trade_count == 0


def test_invalid_closes():
    with pytest.raises(ValueError):
        backtest_daily_closes([], lambda c: [])
    with pytest.raises(ValueError):
        backtest_daily_closes([0, 1], lambda c: [0, 0])
    with pytest.raises(ValueError):
        backtest_daily_closes([-1, 1], lambda c: [0, 0])
    with pytest.raises(ValueError):
        backtest_daily_closes([1, math.nan], lambda c: [0, 0])
    with pytest.raises(ValueError):
        backtest_daily_closes([1, math.inf], lambda c: [0, 0])
    with pytest.raises(ValueError):
        backtest_daily_closes([1, "a"], lambda c: [0, 0])


def test_invalid_signals():
    closes = [100, 110]
    with pytest.raises(ValueError):
        backtest_daily_closes(closes, lambda c: [1])  # length mismatch
    with pytest.raises(ValueError):
        backtest_daily_closes(closes, lambda c: [1, 2])  # invalid value
    with pytest.raises(ValueError):
        backtest_daily_closes(closes, lambda c: [1, "x"])


def test_callback_exception_propagates():
    closes = [100, 110]
    def bad(c):
        raise RuntimeError("boom")
    with pytest.raises(RuntimeError, match="boom"):
        backtest_daily_closes(closes, bad)


def test_input_not_mutated():
    closes = [100, 110, 120]
    signals = [1, None, 0]
    closes_copy = closes[:]
    signals_copy = signals[:]
    backtest_daily_closes(closes, lambda c: signals)
    assert closes == closes_copy
    assert signals == signals_copy


def test_final_signal_not_executed():
    closes = [100, 110, 120]
    signals = [0, 0, 1]
    result = backtest_daily_closes(closes, lambda c: signals)
    # executed positions: p1=0, p2=0 => equity flat
    assert result.equity_curve == pytest.approx([1.0, 1.0, 1.0])
    assert result.trade_count == 0


def test_short_exposure():
    closes = [100, 90, 80]
    signals = [-1, -1, 0]
    result = backtest_daily_closes(closes, lambda c: signals)
    # t1: r=-0.1, pos=-1 => 1*(1+0.1)=1.1
    # t2: r=-0.111..., pos=-1 => 1.1*(1+0.111...)=1.222...
    assert result.equity_curve[1] == pytest.approx(1.1)
    assert result.equity_curve[2] > 1.1
    assert result.trade_count == 1


def test_moving_average_integration():
    # Simple moving average crossover: signal long when price > MA, flat otherwise, warm-up None
    closes = [10, 12, 11, 13, 14, 13, 15]
    window = 3
    ma = moving_average(closes, window)
    # map to signal
    def signal_fn(c):
        m = moving_average(c, window)
        sig = []
        for price, avg in zip(c, m):
            if avg is None:
                sig.append(None)
            else:
                sig.append(1 if price > avg else 0)
        return sig
    result = backtest_daily_closes(closes, signal_fn)
    # Should have equity length 7
    assert len(result.equity_curve) == len(closes)
    # First two are warm-up flat
    assert result.equity_curve[0] == pytest.approx(1.0)
    assert result.equity_curve[1] == pytest.approx(1.0)
    # No exception


def test_ema_integration():
    closes = [10, 11, 12, 13, 14, 15]
    span = 3
    min_periods = 3
    def signal_fn(c):
        ema_vals = exponential_moving_average(c, span=span, min_periods=min_periods)
        sig = []
        for price, e in zip(c, ema_vals):
            if e is None:
                sig.append(None)
            else:
                sig.append(1 if price > e else 0)
        return sig
    result = backtest_daily_closes(closes, signal_fn)
    assert len(result.equity_curve) == len(closes)
    # Warm-up first 2 None -> flat
    assert result.equity_curve[1] == pytest.approx(1.0)


def test_weighted_moving_average_integration():
    closes = [100, 102, 101, 105, 107, 106]
    weights = [0.2, 0.3, 0.5]
    def signal_fn(c):
        wma = weighted_moving_average(c, weights)
        sig = []
        for price, avg in zip(c, wma):
            if avg is None:
                sig.append(None)
            else:
                sig.append(1 if price > avg else 0)
        return sig
    result = backtest_daily_closes(closes, signal_fn)
    assert len(result.equity_curve) == len(closes)
    # First len(weights)-1 =2 entries warm-up flat
    assert result.equity_curve[0] == pytest.approx(1.0)
    assert result.equity_curve[1] == pytest.approx(1.0)


def test_max_drawdown_computation():
    closes = [100, 120, 80, 90]
    signals = [1, 1, 1, 0]
    result = backtest_daily_closes(closes, lambda c: signals)
    # equity: 1, 1.2, 0.8, 0.9
    assert result.equity_curve == pytest.approx([1.0, 1.2, 0.8, 0.9], rel=1e-9)
    # peak 1.2, max dd (1.2-0.8)/1.2 = 0.333...
    assert result.max_drawdown == pytest.approx(0.3333333333, rel=1e-9)
    assert result.total_return == pytest.approx(-0.1, rel=1e-9)
