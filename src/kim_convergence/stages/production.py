# kim_convergence/stages/production.py
from __future__ import annotations
from kim_convergence.gatherer import Gatherer
from kim_convergence.core import KimConvergence
from kim_convergence.callbacks.autocorr import autocorr
from kim_convergence.utils import parse_callbacks

def run(kc: "KimConvergence") -> None:
    """
    Equilibration stage driven by Gatherer.
    """

    # ---- echo hyper‑parameters  ------------------
    p = kc.cfg.production
    kc.log.info(
    f"[production]: starting production, tol = {p.tol}, c = {p.c}, key = {p.key}"
    )

    # ---- optional callback lists from YAML ---------------------------
    g_cfg        = p.get("gather", {})
    init_cbs     = g_cfg.get("initCallbacks", [])
    step_cbs     = g_cfg.get("stepCallbacks", [])
    cleanup_cbs  = g_cfg.get("cleanupCallbacks", [])

    # now parse each group:
    init_cbs,    init_args    = parse_callbacks(init_cbs)
    step_cbs,    step_args    = parse_callbacks(step_cbs)
    cleanup_cbs, cleanup_args = parse_callbacks(cleanup_cbs)

    # ───── lambda captures the extra args so Gatherer only sees kc ─────
    if len(p.key) == 1: # try to only check single keyr
        convergence_fn = lambda kc: autocorr(
                                            kc.state[p.key[0]][kc.equilibration_state:],
                                            p.tol, 
                                            p.c, 
                                            p.key, 
                                            kc, 
                                            kc.log)
    else: # fall back and check all keys
        convergence_fn =  lambda kc: all(autocorr(kc.state[k][kc.equilibration_state:],  p.tol, p.c, k, kc, kc.log) for k in p.key)

    # ---- build and run the loop --------------------------------------
    g = Gatherer(
        kc,
        step_fn=kc.step_fn,
        convergence_fn=convergence_fn,
        init_callbacks=init_cbs,
        step_callbacks=step_cbs,
        cleanup_callbacks=cleanup_cbs,
        init_callback_params = init_args,
        step_callback_params = step_args,
        cleanup_callback_params = cleanup_args
    )
    
    g.gather()

    if kc.step < kc.max_steps:
            kc.log.info(
            f"[production]: production complete"
            )
    
    else:
        kc.log.info(
        f"[production]: production failed"
        )
        raise Warning("Increase max steps to allow for system to fully sample")
