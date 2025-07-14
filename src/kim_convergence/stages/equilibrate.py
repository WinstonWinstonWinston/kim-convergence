# kim_convergence/stages/equilibrate.py
from __future__ import annotations
from kim_convergence.gatherer import Gatherer
from kim_convergence.core import KimConvergence
from kim_convergence.callbacks.mean_in_bounds import mean_in_bounds

def run(kc: "KimConvergence") -> None:
    """
    Equilibration stage driven by Gatherer.
    """

    # ---- echo hyper‑parameters  ------------------
    p = kc.cfg.equilibrate
    print(f"[equilibrate] bounds={p.bounds}")

    # ---- optional callback lists from YAML ---------------------------
    g_cfg = p.get("gather", {})
    init_cbs    = g_cfg.get("init_callbacks", ())
    step_cbs    = g_cfg.get("step_callbacks", ())
    cleanup_cbs = g_cfg.get("cleanup_callbacks", ())
    
    # ───── lambda “captures” the bounds so Gatherer only sees kc ─────
    convergence_fn = lambda kc, b=p.bounds: mean_in_bounds(kc.state["position"], b)

    # ---- build and run the loop --------------------------------------
    g = Gatherer(
        kc,
        step_fn=kc.step_fn,
        convergence_fn=convergence_fn,
        init_callbacks=init_cbs,
        step_callbacks=step_cbs,
        cleanup_callbacks=cleanup_cbs,
    )
    
    g.gather()
