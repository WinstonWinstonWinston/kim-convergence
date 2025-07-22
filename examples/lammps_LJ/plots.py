import numpy as np
import matplotlib.pyplot as plt
from kim_convergence.utils import autcorr_function_1d,auto_window

# Load columns: step, T, P, E into separate arrays
# load all columns
data = np.loadtxt('vars.dump')

# find first index of each unique step
_, first_idx = np.unique(data[:,0], return_index=True)

# sort the indices to restore ascending‐step order
first_idx = np.sort(first_idx)

# select only those rows
uniq = data[first_idx]

# unpack back into arrays
step, T, P, E = uniq.T

# now step contains no duplicates
eq_step = 65100
stepsize = 100

# Autocorrelation Calculation

tol = 500
c = 5
n = len(step[step >= eq_step]) 
rhos = dict()
tau_ests= dict()
windows= dict()

for values,name in zip([T,P,E],["T","P","E"]):

    values = values[step >= eq_step]
    n = len(values)

    rho = autcorr_function_1d(values)
    taus = 2.0 * np.cumsum(rho) - 1.0
    window = auto_window(taus, c)
    tau_est = taus[window]
    condition = tol * tau_est < n
    run_mean = np.mean(values)
    
    rhos[name] = rho
    tau_ests[name] = stepsize*tau_est
    windows[name] = stepsize*window

    print(
    "[autocorr] "
    f"key = {name} | " 
    f"n = {n*stepsize:,d} | "
    f"run_mean = {run_mean:.6f} | "
    f"tau_est = {tau_est*stepsize} | "
    f"condition = {condition}")

# Autocorrelation Plots

for key in rhos.keys():

    rho = rhos[key]

    plt.figure(figsize=(8, 4), dpi=150)

    plt.title("Autocorrelation Function for " + key)

    # full even‐extension
    x = stepsize*np.concatenate((-np.arange(len(rho))[::-1], np.arange(len(rho))))
    y = np.concatenate((rho[::-1], rho))

    # plot the entire curve
    plt.plot(x, y, lw=1.5, label=r'$\rho(\ell)$')

    # fill only between -window and +window
    plt.fill_between(
    x, y,
    where=np.abs(x) <= windows[key],
    alpha=0.3
    )
    
    plt.axvline(tau_ests[key],  color='C1', linestyle='--', lw=2,
            label=fr'$\tau_{{\rm est}}={tau_ests[key]:.1f}$')
    plt.axvline(-tau_ests[key], color='C1', linestyle='--', lw=2)
    plt.axvline(windows[key],   color='C2', linestyle='-.', lw=2, label=fr'$M={windows[key]}$')
    plt.axvline(-windows[key],  color='C2', linestyle='-.', lw=2)

    plt.xlabel('Lag $\ell$')
    plt.ylabel(r'Autocorrelation $\rho$')
    plt.legend(loc='best', frameon=True)
    plt.xlim(-1.5 * windows[key], 1.5 * windows[key])

    plt.tight_layout()
    plt.savefig(f"figs/autocorr_{key}.jpg") 