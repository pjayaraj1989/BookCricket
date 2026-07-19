"""
Duckworth-Lewis (Standard Edition) calculations for rain-affected
limited-overs matches.

Based on the published condensed D/L resource table (percentage of a
side's run-scoring resources remaining, given whole overs left and
wickets lost), with bilinear interpolation between table entries. The
table is absolute in overs, so shorter formats work naturally: a T20
innings simply starts with 20-overs-left resources (58.9%).
"""

# rows: overs left, columns: resources % remaining at 0/2/5/7/9 wickets lost
_OVERS_ROWS = [0, 5, 10, 20, 25, 30, 40, 50]
_WKTS_COLS = [0, 2, 5, 7, 9]
_TABLE = {
    50: [100.0, 83.8, 49.5, 26.5, 7.6],
    40: [90.3, 77.6, 48.3, 26.4, 7.6],
    30: [77.1, 68.2, 45.7, 26.2, 7.6],
    25: [68.7, 61.8, 43.4, 25.9, 7.6],
    20: [58.9, 54.0, 40.0, 25.2, 7.6],
    10: [34.1, 32.5, 27.5, 20.6, 7.5],
    5: [18.4, 17.9, 16.4, 14.0, 7.0],
    0: [0.0, 0.0, 0.0, 0.0, 0.0],
}

# average score of a full 50-over innings, used when the side batting
# second ends up with more resources than the side batting first
G50 = 245.0


def _interp(x, x0, x1, y0, y1):
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (x - x0) / float(x1 - x0)


def ResourcesRemaining(overs_left, wickets_lost):
    """
    Percentage of run-scoring resources a batting side still has.

    Args:
        overs_left: Whole/fractional overs still available (clamped 0-50).
        wickets_lost: Wickets already fallen (clamped 0-10).

    Returns:
        float: resources remaining, 0.0-100.0
    """
    overs_left = max(0.0, min(50.0, float(overs_left)))
    wickets_lost = max(0, min(10, int(wickets_lost)))
    if wickets_lost == 10 or overs_left == 0:
        return 0.0

    # bracket overs
    o_lo = max(r for r in _OVERS_ROWS if r <= overs_left)
    o_hi = min(r for r in _OVERS_ROWS if r >= overs_left)

    def row_at(wkts, overs_row):
        vals = _TABLE[overs_row]
        if wkts >= _WKTS_COLS[-1]:
            # between 9 wickets and all out (0 resources)
            return _interp(wkts, _WKTS_COLS[-1], 10, vals[-1], 0.0)
        w_lo = max(c for c in _WKTS_COLS if c <= wkts)
        w_hi = min(c for c in _WKTS_COLS if c >= wkts)
        return _interp(
            wkts,
            w_lo,
            w_hi,
            vals[_WKTS_COLS.index(w_lo)],
            vals[_WKTS_COLS.index(w_hi)],
        )

    return round(
        _interp(
            overs_left,
            o_lo,
            o_hi,
            row_at(wickets_lost, o_lo),
            row_at(wickets_lost, o_hi),
        ),
        1,
    )


def RevisedTarget(first_innings_score, r1, r2, g=G50):
    """
    D/L Standard Edition revised target for the side batting second.

    Args:
        first_innings_score: Runs made by the side batting first.
        r1: Resources (%) that were available to the side batting first.
        r2: Resources (%) available to the side batting second.
        g: Average full-innings score for the format (G50 scaled).

    Returns:
        int: runs needed to win.
    """
    if r1 <= 0:
        return first_innings_score + 1
    if r2 <= r1:
        par = first_innings_score * r2 / r1
    else:
        par = first_innings_score + g * (r2 - r1) / 100.0
    return int(par) + 1


def ParScore(first_innings_score, r1, r2_used, g=G50):
    """
    D/L par score for the chasing side at a stoppage: the score they must
    be AHEAD of to be winning, given the resources they have used so far.

    Returns:
        int
    """
    if r1 <= 0:
        return first_innings_score
    if r2_used <= r1:
        par = first_innings_score * r2_used / r1
    else:
        par = first_innings_score + g * (r2_used - r1) / 100.0
    return int(par)
