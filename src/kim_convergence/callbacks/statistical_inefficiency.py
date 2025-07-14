import numpy as np
from typing import Sequence, Iterable
import matplotlib.pyplot as plt
import logging
from scipy.stats import norm

def statistical_inefficiency(values: Iterable[float], limit: int, ci_half_width_desired: float, log: logging.Logger) -> bool:
    """
    Return True when the ci_half_width meets desired value. Computes this with
    the statistical inefficiency. 

    Parameters
    ----------
    values : list-like of scalar or 0-D NumPy arrays
    limit  : how many blocks sizes to average over
    ci_half_width_desired : the confidence you want in units of values

    Notes
    -----
    • If values is empty the function returns False
      (nothing recorded yet).
    """
    if not values or len(values) < 10:
        return False

    values = np.array(values)

    n = len(values)

    max_b = 16384  # maximum allowed block size

    block_sizes = [
        2**e for e in range(0, int(np.log2(n)) + 1)
        if n // (2**e) >= 2 and 2**e <= max_b
    ]

    block_data = [
        values[:n - n % b].reshape(-1, b).mean(axis=1)
        for b in block_sizes
    ]

    run_mean = np.mean(block_data[0])

    block_stds = np.array([
        np.sum((block_series - run_mean)**2)/(len(block_series) - 1) for block_series in block_data
    ])

    s = block_sizes*block_stds/block_stds[0]

    tail = s[-limit:]
    limit_s = np.mean(tail)
    plateu_conditon = (np.max(tail) - np.min(tail)) / limit_s < 0.1

    alpha = 0.05  # for 95% CI
    z = norm.ppf(1 - alpha / 2)

    N = len(values)

    ci_half_width = z * block_stds[0] * np.sqrt(limit_s) / np.sqrt(N)
    ci = (run_mean - ci_half_width, run_mean + ci_half_width)
    
    CI_condition = ci_half_width <= ci_half_width_desired

    log.info(
    "[statistical_inefficiency] "
    f"n = {n:,d} | "
    f"run_mean = {run_mean:.6f} | "
    f"ci_half_width = {ci_half_width:.6f} | "
    f"CI_condition = {CI_condition} | "
    f"plateu_conditon = {plateu_conditon} | "
    f"limit_s = {limit_s:.2f}"
    )

    if n == 500001:
        plt.plot(block_sizes,s)
        plt.scatter(block_sizes,s)
        plt.show()

    return CI_condition and plateu_conditon