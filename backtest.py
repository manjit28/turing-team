from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

Signal = int | None
SignalFunction = Callable[[Sequence[float]], Sequence[Signal]]

@dataclass(frozen=True)
class BacktestResult:
    equity_curve: list[float]
    total_return: float
    max_drawdown: float
    trade_count: int


def backtest_daily_closes(
    closes: Sequence[float],
    signal_fn: SignalFunction,
) -> BacktestResult:
    # Validate closes
    if not closes:
        raise ValueError("closes must be non-empty")
    # Validate closes values
    import math
    closes_list = list(closes)
    for c in closes_list:
        # bool is subclass of int, reject bool explicitly
        if isinstance(c, bool) or not isinstance(c, (int, float)):
            raise ValueError("closes must contain only real numeric values")
        if not math.isfinite(c):
            raise ValueError("closes must be finite")
        if c <= 0:
            raise ValueError("closes must be strictly positive")

    # Call signal function, propagate exceptions
    signals = signal_fn(closes_list)

    # Validate signal output
    try:
        signal_len = len(signals)  # type: ignore
    except TypeError:
        raise ValueError("signal_fn must return a sequence")
    if signal_len != len(closes_list):
        raise ValueError("signal output length must match closes length")
    # Validate each signal value
    allowed = {-1, 0, 1, None}
    # Build list to avoid mutation issues
    signal_vals = []
    for s in signals:
        if s is None:
            signal_vals.append(None)
        elif s in (-1, 0, 1):
            signal_vals.append(int(s))
        else:
            raise ValueError("signal values must be None, -1, 0, or +1")
    # Do not mutate inputs

    n = len(closes_list)
    equity_curve = [1.0]
    # executed position p[0] = 0
    prev_position = 0
    trade_count = 0

    # For t >= 1
    for t in range(1, n):
        # executed position for t is signal[t-1]
        sig = signal_vals[t - 1]
        pos = 0 if sig is None else sig
        # trade count: compare with previous executed position
        if pos != prev_position:
            trade_count += 1
        # return
        prev_close = closes_list[t - 1]
        curr_close = closes_list[t]
        r = curr_close / prev_close - 1.0
        equity_prev = equity_curve[-1]
        equity_curr = equity_prev * (1.0 + pos * r)
        equity_curve.append(equity_curr)
        prev_position = pos

    # If n == 1, equity_curve is [1.0], trade_count stays 0
    total_return = equity_curve[-1] - 1.0

    # Max drawdown
    peak = 1.0
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        if peak != 0:
            dd = (peak - eq) / peak
            if dd > max_dd:
                max_dd = dd

    return BacktestResult(
        equity_curve=equity_curve,
        total_return=total_return,
        max_drawdown=max_dd,
        trade_count=trade_count,
    )
