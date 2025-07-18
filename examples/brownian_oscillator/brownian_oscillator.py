# kim-convergence/examples/brownian_oscillator.py
from __future__ import annotations
import numpy as np
from kim_convergence.core import KimConvergence
from omegaconf import DictConfig
import hydra
import numpy as np
import matplotlib.pyplot as plt
import logging

log = logging.getLogger(__name__)

def _init_state(kc: "KimConvergence") -> None:
    """
    Attach RNG and trajectory buffers to kc if they're not present yet.
    """
    if not hasattr(kc, "_rng"):
        p = kc.cfg.stepFn.params
        kc._rng           = np.random.default_rng(p.seed)
        kc._theta         = p.kSpring / p.lam
        kc._expdt         = np.exp(-kc._theta * p.dt)
        kc._sigma         = np.sqrt(
            (p.kB * p.temperature / p.kSpring) * (1.0 - np.exp(-2.0 * kc._theta * p.dt))
        )
        kc._substeps = p.substeps
        kc.state["position"].append(np.float64(p.xInit))
        kc.state["position_squared"].append(np.float64(p.xInit**2))

def step_fn(kc: "KimConvergence") -> None:
    """
    Advance the 1-D overdamped Langevin oscillator by substeps time steps
    and append the new position to `kc.state["position"]`.
    """
    _init_state(kc)                      # safe to call every step
    for _ in range(kc._substeps):
        x_prev   = kc.state["position"][-1]
        noise    = kc._rng.standard_normal()
        x_next   = kc._expdt * x_prev + kc._sigma * noise

        kc.state["position"].append(x_next)
        kc.state["position_squared"].append(x_next**2)
        kc.step += 1                         # Gatherer may rely on this counter

@hydra.main(version_base=None, config_path="", config_name="brownian_oscillator.yaml")
def main(cfg: DictConfig) -> None:
    """
    Hydra entry-point.  Creates KimConvergence, wires in the step
    function named in cfg.step_fn.fname, then starts the run.
    """
    log.info("Running brownian_oscillator.py")
    log.info(f"Config: {cfg}")

    kc = KimConvergence(cfg)
    kc.log = log

    # Resolve & attach the per‑step function
    kc.step_fn = step_fn
    kc.max_steps = cfg.stepFn.maxSteps

    kc.run() # walk the pipeline

    kc.tau_est = max(kc.tau_est_position,kc.tau_est_position_squared)

    values = np.array(kc.state['position'])
    
    mu_all  = np.mean(values[::int(2*kc.tau_est)])
    mu_post = np.mean(values[kc.equilibration_step::int(2*kc.tau_est)])

    plt.figure(figsize=(10, 4), dpi=150)

    # plot observations and baseline
    plt.plot(values, color='k', alpha=0.4, lw=1.5, label='Observations')
    plt.hlines(0, 0, len(values)-1, color='k', linestyle='--', lw=1)

    # equilibration cutoff
    eq = kc.equilibration_step
    plt.vlines(eq, -10, 10, color='r', linestyle='--', lw=2, label=f'Equil. Step = {eq}')
    plt.axvspan(eq, len(values)-1, color='C1', alpha=0.1)

    # draw vertical line segments at each multiple of tau
    for t in np.arange(eq, len(values), 2*kc.tau_est):
        plt.vlines(
            t,
            -0.5,
            0.5,
            color='C2',
            linewidth=1.5,
            alpha=0.7
        )

    # annotate means
    plt.text(
        0.98, 0.95,
        rf'$\bar{{x}}_{{\rm all}}={mu_all:.3f}$' + '\n' + rf'$\bar{{x}}_{{\rm post}}={mu_post:.3f}$',
        transform=plt.gca().transAxes,
        ha='right', va='top',
        fontsize=12,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.8)
    )

    plt.ylim(-10, 10)
    plt.xlabel('Time Step')
    plt.ylabel('Value')
    plt.title('Time Series with Equilibration Cutoff')
    plt.legend(fontsize=12, loc='upper left')

    plt.tight_layout()
    plt.savefig('plot.png')

if __name__ == "__main__":
    main()