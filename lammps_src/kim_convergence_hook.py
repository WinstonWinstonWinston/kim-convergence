import os
from hydra import initialize_config_dir, compose
from lammps import lammps
from kim_convergence.steps.lammps.step_fn import step_fn
from kim_convergence.core import KimConvergence
import logging
from hydra.core.utils import configure_log
from pathlib import Path

log = logging.getLogger(__name__)

def kim_convergence(ptr: int, config_name: str):
    # 1) attach to LAMMPS
    lmp = lammps(ptr=ptr)

    # 2) Where the YAML actually lives on disk
    config_dir = os.getcwd()
    cfg_name = os.path.splitext(config_name)[0]

    # 3) Use initialize_config_dir to point at that absolute folder
    with initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = compose(config_name=cfg_name, return_hydra_config=True)
        # wipe old log
        target = Path(cfg.hydra.runtime.output_dir) / f"{cfg.hydra.job.name}.log"
        try:
            target.unlink()          # remove if it exists
        except FileNotFoundError:
            pass
        configure_log(cfg.hydra.job_logging, cfg.hydra.verbose)

    # 4) Report findings for user
    log.info("Running Kim Convergence")
    log.info(f"LAMMPS ptr = {ptr!r}")
    log.info(f"Loading config = {config_name!r}")

    # 5) Create kc object
    kc = KimConvergence(cfg)
    kc.lmp = lmp
    kc.log = log
    kc.step_fn = step_fn

    kc.max_steps = kc.cfg.stepFn.maxSteps

    # 6) Walk the pipeline
    kc.run()

    identifier = str(*config_name.split(".")[:-1])

    # 7) Tell LAMMPS eq time and taus
    lmp.command(f'print "KimConvergence equilibrated at step {kc.equilibration_step}"')
    biggest_tau = max((getattr(kc, a) for a in dir(kc) if a.startswith("tau_est_")), default=None)
    lmp.command(f'print "KimConvergence estimated tau_est to be {biggest_tau}"')
    lmp.command(f"variable tau_est_{identifier} equal {biggest_tau}")
    lmp.command(f"variable equilibration_step_{identifier} equal {kc.equilibration_step}")

    # 8) Tell LAMMPS you’re finished
    lmp.command(f'print "KimConvergence {config_name} complete"')