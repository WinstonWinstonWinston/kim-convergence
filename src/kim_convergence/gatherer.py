# kim_convergence/gatherer.py
#
# A VERY small loop‑driver: all domain work lives in user‑supplied
# callables.  Gatherer itself knows nothing about simulation details;
# it just runs functions in a fixed order until a predicate says stop.

from __future__ import annotations
from collections.abc import Callable, Iterable
from typing import Any
from kim_convergence.core import KimConvergence

class Gatherer:
    """Main loop driver.

    Parameters
    ----------
    kc
        The shared KimConvergence instance that holds state.
    step_fn
        Function that performs a unit of work (e.g. N MD steps).
    convergence_fn
        Returns True when the run is finished.
    init_callbacks / step_callbacks / cleanup_callbacks ─ iterables of callables
        run (1) once before the loop, (2) after every step, and (3) once at the end.
        Each receives the KimConvergence instance so it can read or mutate state.
        Step callbacks are the usual place to bump kc.step and save whatever
        per-step data the convergence check will inspect.
    """

     # -------------------------------- init ------------------------------
    def __init__(
        self,
        kc: "KimConvergence",
        *,
        step_fn: Callable[["KimConvergence"], Any],
        convergence_fn: Callable[["KimConvergence"], bool],
        init_callbacks: Iterable[Callable[["KimConvergence"], Any]] = (),
        step_callbacks: Iterable[Callable[["KimConvergence"], Any]] = (),
        cleanup_callbacks: Iterable[Callable[["KimConvergence"], Any]] = (),
    ):
        self.kc = kc
        self._step_fn = step_fn
        self._convergence_fn = convergence_fn
        self._init_cbs = list(init_callbacks) if init_callbacks is not None else []
        self._step_cbs = list(step_callbacks) if step_callbacks is not None else []
        self._cleanup_cbs = list(cleanup_callbacks) if cleanup_callbacks is not None else []

    # -------------------------------- helpers ------------------------------
    def _run_cbs(
        self, callbacks: Iterable[Callable[["KimConvergence"], Any]]
    ) -> None:
        for cb in callbacks:
            cb(self.kc)

    # -------------------------------- main loop ------------------------------
    def gather(self) -> None:
        """Run until convergence_fn returns True or kc.max_steps reached."""

        # one‑time initialization
        self._run_cbs(self._init_cbs)

        # iterate
        while not self._convergence_fn(self.kc) and self.kc.step < self.kc.max_steps:
            self._step_fn(self.kc)          # core unit of work
            self._run_cbs(self._step_cbs)   # user hooks 

        # cleanup
        self._run_cbs(self._cleanup_cbs)