# Mean‑position convergence test (independent of KimConvergence)

import numpy as np
from typing import Sequence, Iterable
import matplotlib.pyplot as plt

def mcr(values: Iterable[float], percent_past_d: float, every: int) -> bool:
    """
    Return True when the step is percent_past_d the d_* mcr statistic.
    For example, if percent_past_d = 2.3 then returns len(values) > d*2.3

    Parameters
    ----------
    values : list-like of scalar or 0-D NumPy arrays
    percent_past_d : how much past d you want to be to be "equilibrated". 
    every : how often to step through attempts at d

    Notes
    -----
    • If values is empty the function returns False
      (nothing recorded yet).
    """
    if not values:
        return False
    
    values = np.array(values)

    n = len(values)

    d_arr = [np.sum((values[d:n] - values[d:n].mean())**2) / (n - d)**2 for d in range(0,int(n*0.9),every)]
    d_star = every*np.argmin(d_arr)

    print(n)
    print(d_star)
    print(n > d_star*percent_past_d)
    print()

    return n > d_star*percent_past_d