# kim_convergence/step_schemes/brownian_oscillator.py
from __future__ import annotations
import numpy as np
from kim_convergence.core import KimConvergence
from omegaconf import DictConfig
import hydra
import numpy as np
import matplotlib.pyplot as plt

def _init_state(kc: "KimConvergence") -> None:
    """
    Attach RNG and trajectory buffers to kc if they're not present yet.
    """
    if not hasattr(kc, "_rng"):
        p = kc.cfg.step_fn.params
        kc._rng           = np.random.default_rng(p.seed)
        kc._theta         = p.k_spring / p.lam
        kc._expdt         = np.exp(-kc._theta * p.dt)
        kc._sigma         = np.sqrt(
            (p.kB * p.temperature / p.k_spring) * (1.0 - np.exp(-2.0 * kc._theta * p.dt))
        )
        kc._substeps = p.substeps
        kc.state["position"].append(np.asarray(p.x_init, dtype=float))
        kc.step = 0

def step_fn(kc: "KimConvergence") -> None:
    """
    Advance the 1-D overdamped Langevin oscillator by **one** time step
    and append the new position to `kc.state["position"]`.
    """
    _init_state(kc)                      # safe to call every step
    for _ in range(kc._substeps):
        x_prev   = kc.state["position"][-1]
        noise    = kc._rng.standard_normal()
        x_next   = kc._expdt * x_prev + kc._sigma * noise

        kc.state["position"].append(x_next)
        kc.step += 1                         # Gatherer may rely on this counter

@hydra.main(version_base=None, config_path="", config_name="brownian_oscillator.yaml")
def main(cfg: DictConfig) -> None:
    """
    Hydra entry-point.  Creates KimConvergence, wires in the step
    function named in cfg.step_fn.fname, then starts the run.
    """
    kc = KimConvergence(cfg)

    # Resolve & attach the per‑step function
    kc.step_fn = step_fn
    kc.max_steps = cfg.step_fn.max_steps

    kc.run() # walk the pipeline

    values = np.array(kc.state['position'])
    running_mean = np.cumsum(values) / np.arange(1, len(values) + 1)
    plt.plot(values, label=f'Mean: {np.mean(values):.3f}')
    plt.plot(running_mean, label='Cumulative Mean')
    plt.plot(np.ones_like(values)*0.1)
    plt.plot(-np.ones_like(values)*0.1)
    plt.xlim(0,kc.max_steps)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()