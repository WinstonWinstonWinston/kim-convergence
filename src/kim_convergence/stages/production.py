# kim_convergence/stages/production.py
from __future__ import annotations
from kim_convergence.gatherer import Gatherer
from kim_convergence.core import KimConvergence
from kim_convergence.callbacks.autocorr import autocorr

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
    g_cfg = p.get("gather", {})
    init_cbs    = g_cfg.get("init_callbacks", ())
    step_cbs    = g_cfg.get("step_callbacks", ())
    cleanup_cbs = g_cfg.get("cleanup_callbacks", ())

    # ───── lambda captures the extra args so Gatherer only sees kc ─────
    if len(p.key) == 1: # try to only check single key
        convergence_fn = lambda kc: autocorr(kc.state[p.key],  p.tol, p.c, p.key, kc, kc.log)
    else: # fall back and check all keys
        convergence_fn =  lambda kc: all(autocorr(kc.state[k],  p.tol, p.c, k, kc, kc.log) for k in p.key)

    # ---- build and run the loop --------------------------------------
    g = Gatherer(
        kc,
        step_fn=kc.step_fn,
        convergence_fn=convergence_fn,
        init_callbacks=init_cbs,
        step_callbacks=step_cbs,
        cleanup_callbacks=cleanup_cbs,
    )

    # ---- save equilibration time to kc --------------------------------------
    kc.equilibration_time = kc.step
    
    g.gather()

    kc.log.info(
    f"[production]: production complete"
    )
