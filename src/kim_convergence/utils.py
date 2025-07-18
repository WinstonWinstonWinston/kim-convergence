import numpy as np
from omegaconf import OmegaConf
import importlib

def next_pow_two(n):
    """Returns the next power of two greater than or equal to `n`"""
    i = 1
    while i < n:
        i = i << 1 # bitshift
    return i

def auto_window(taus, c):
    m = np.arange(len(taus)) < c * taus
    if np.any(m):
        return np.argmin(m)
    return len(taus) - 1

def autcorr_function_1d(x):
    """Estimate the normalized autocorrelation function of a 1-D series
       Taken from https://github.com/dfm/emcee/blob/main/src/emcee/autocorr.py
    Args:
        x: The series as a 1-D numpy array.

    Returns:
        array: The autocorrelation function of the time series.

    """
    x = np.atleast_1d(x)
    if len(x.shape) != 1:
        raise ValueError("invalid dimensions for 1D autocorrelation function")
    n = next_pow_two(len(x))

    # Compute the FFT and then (from that) the auto-correlation function
    f = np.fft.fft(x - np.mean(x), n=2 * n)
    acf = np.fft.ifft(f * np.conjugate(f))[: len(x)].real
    acf /= acf[0]
    return acf

def parse_callbacks(cb_list):
    types = []
    args  = []
    if cb_list is not None:
        for cb in cb_list:
            # 1) record the callback type
            types.append(cb.type)
            # 2) strip out "type" and rebuild a pure-args DictConfig
            arg_dict = OmegaConf.to_container(cb, resolve=True)
            arg_dict.pop("type", None)
            args.append(OmegaConf.create(arg_dict))
        return types, args
    else:
        return (), ()