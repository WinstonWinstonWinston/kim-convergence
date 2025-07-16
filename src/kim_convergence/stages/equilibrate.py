# kim_convergence/stages/equilibrate.py
from __future__ import annotations
from kim_convergence.gatherer import Gatherer
from kim_convergence.core import KimConvergence
from kim_convergence.callbacks.mcr import mcr
from kim_convergence.utils import parse_callbacks

def run(kc: "KimConvergence") -> None:
    """
    Equilibration stage driven by Gatherer.
    """

    # ---- echo hyper‑parameters  ------------------
    p = kc.cfg.equilibrate
    kc.log.info(
    f"[equilibrate]: starting equilibrate | key = {p.key} | percent_past_d = {p.percent_past_d} | every = {p.every}"
    )

    # ---- optional callback lists from YAML ---------------------------
    g_cfg        = p.get("gather", {})
    init_cbs     = g_cfg.get("init_callbacks", [])
    step_cbs     = g_cfg.get("step_callbacks", [])
    cleanup_cbs  = g_cfg.get("cleanup_callbacks", [])

    # now parse each group:
    init_cbs,    init_args    = parse_callbacks(init_cbs)
    step_cbs,    step_args    = parse_callbacks(step_cbs)
    cleanup_cbs, cleanup_args = parse_callbacks(cleanup_cbs)
    
    # ───── lambda captures the extra args so Gatherer only sees kc ─────
    if len(p.key) == 1: # try to only check single key
        convergence_fn = lambda kc: mcr(kc.state[p.key], p.percent_past_d, p.every, p.key, kc.log)
    else: # fall back and check all keys
        convergence_fn =  lambda kc: all(mcr(kc.state["position"],  p.percent_past_d, p.every, k, kc.log) for k in p.key)

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

    # ---- save equilibration time to kc --------------------------------------
    kc.equilibration_step = kc.step
    
    kc.log.info(
    f"[equilibrate]: equilibrate complete"
    )
