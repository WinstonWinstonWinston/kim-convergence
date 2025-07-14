# Mean‑position convergence test (independent of KimConvergence)

import numpy as np
from typing import Sequence, Iterable

def mean_in_bounds(values: Iterable[float], bounds: Sequence[float]) -> bool:
    """
    Return True when the running mean of *values* lies within [lo, hi].

    Parameters
    ----------
    values   : list-like of scalar or 0-D NumPy arrays
    bounds   : (lo, hi) numeric pair

    Notes
    -----
    • If values is empty the function returns False
      (nothing recorded yet).
    """
    if not values:
        return False

    lo, hi = bounds
    return lo <= float(np.mean(values)) <= hi