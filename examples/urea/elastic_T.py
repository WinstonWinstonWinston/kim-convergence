# kim_convergence/step_schemes/brownian_oscillator.py
from __future__ import annotations
import numpy as np
from kim_convergence.core import KimConvergence
from omegaconf import DictConfig
import hydra
import numpy as np
import matplotlib.pyplot as plt
import logging
import lammps

log = logging.getLogger(__name__)

def _init_state(kc: "KimConvergence") -> lammps.core.lammps:
    """
    Create lammps object and run init.
    """
    if not hasattr(kc, "_lmp"):
        p = kc.cfg.step_fn.params
        lmp = lammps(cmdargs=p.cmdargs)
        lmp.file(p.init_fname)
        kc._substeps = p.substeps
        kc._lmp = lmp

def step_fn(kc: "KimConvergence") -> None:
    """
    Advance the lammps simulation by substeps seteps
    """
    _init_state(kc)                       # safe to call every step
    kc.lmp.command(f"run {kc._substeps}")
    kc.state[kc.cfg.step_fn.key].append()
    kc.step += kc._substeps               # Gatherer may rely on this counter

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
    kc.max_steps = cfg.step_fn.max_steps

    kc.run() # walk the pipeline

    values = np.array(kc.state['position'])
    
    plt.plot(values, label=f'Mean: {np.mean(values):.3f}, Mean After EQ {np.mean(values[kc.equilibration_step:]):.3f}',color='k',alpha=0.3)
    plt.plot(np.zeros_like(values),color='k',linestyle='dashed')
    plt.axvline(kc.equilibration_step,color='r',linestyle='dashed')
    plt.ylim(-5,5)
    plt.legend(fontsize=15)
    plt.show()

    print("Eq Step:",kc.equilibration_step)

if __name__ == "__main__":
    main()