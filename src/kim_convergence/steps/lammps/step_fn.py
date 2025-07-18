from kim_convergence.core import KimConvergence

def step_fn(kc: "KimConvergence") -> None:
    kc.lmp.command(f"run {kc.cfg.stepFn.params.substeps}")
    kc.step += kc.cfg.stepFn.params.substeps