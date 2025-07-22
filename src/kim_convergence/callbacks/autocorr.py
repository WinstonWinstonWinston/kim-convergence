import numpy as np
from typing import Sequence, Iterable
# import matplotlib.pyplot as plt
import logging
from scipy.stats import norm
from kim_convergence.core import KimConvergence
from kim_convergence.utils import autcorr_function_1d,auto_window

def autocorr(values: Iterable[float], tol: int, c: int, key: str, kc: KimConvergence, log: logging.Logger) -> bool:
    """
    Return True when the chain is tol*autocorr steps long. Nearly a verbatim copy of the emcee implementation.
    See https://github.com/dfm/emcee/blob/main/src/emcee/autocorr.py. 

    Parameters
    ----------
    tol : The minimum number of autocorrelation times needed to trust the estimate.
    c  :  The step size for the window search.
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

    # max_b = int(n/100)  
    # block_sizes = [e for e in range(1, max_b)]
    # block_data = [
    #     values[:n - n % b].reshape(-1, b).mean(axis=1)
    #     for b in block_sizes
    # ]
    # run_mean = np.mean(values)
    # block_stds = np.array([
    #     np.sum((block_series - run_mean)**2)/(len(block_series) - 1) for block_series in block_data
    # ])
    # s = block_sizes*block_stds/block_stds[0]

    rho = autcorr_function_1d(values)
    taus = 2.0 * np.cumsum(rho) - 1.0
    window = auto_window(taus, c)
    tau_est = taus[window]
    condition = tol * tau_est < n
    run_mean = np.mean(values)
    
    log.info(
    "[autocorr] "
    f"key = {key} | " 
    f"n = {n*kc.cfg.stepFn.substeps:,d} | "
    f"run_mean = {run_mean:.6f} | "
    f"tau_est = {tau_est*kc.cfg.stepFn.substeps} | "
    f"condition = {condition}"
    )

    if condition:
        object.__setattr__(kc,"tau_est_" + str(key), tau_est*kc.cfg.stepFn.substeps)

        #   plt.figure(figsize=(8, 4), dpi=150)

        #   # full even‐extension
        #   x = np.concatenate((-np.arange(len(rho))[::-1], np.arange(len(rho))))
        #   y = np.concatenate((rho[::-1], rho))

        #   # plot the entire curve
        #   plt.plot(x, y, lw=1.5, label=r'$\rho(\ell)$')

        #   # fill only between -window and +window
        #   plt.fill_between(
        #       x, y,
        #       where=np.abs(x) <= window,
        #       alpha=0.3
        #   )

        #   plt.axvline(tau_est,  color='C1', linestyle='--', lw=2,
        #               label=fr'$\tau_{{\rm est}}={tau_est:.1f}$')
        #   plt.axvline(-tau_est, color='C1', linestyle='--', lw=2)
        #   plt.axvline(window,   color='C2', linestyle='-.', lw=2, label=fr'$M={window}$')
        #   plt.axvline(-window,  color='C2', linestyle='-.', lw=2)

        #   plt.xlabel('Lag $\ell$')
        #   plt.ylabel(r'Autocorrelation $\rho$')
        #   plt.legend(loc='best', frameon=True)
        #   plt.xlim(-1.5 * window, 1.5 * window)

        #   plt.tight_layout()
        #   plt.show() 

    return condition 