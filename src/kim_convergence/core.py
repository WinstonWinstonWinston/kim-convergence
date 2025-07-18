import importlib
from pathlib import Path
from types import ModuleType
from typing import Callable, Any,DefaultDict, List
import collections
from omegaconf import DictConfig, OmegaConf
import numpy as np
import logging

class KimConvergence:
    """
    Driver object that understands the pipeline grammar.

    Expected YAML structure
    --------------------------------------------------------------------
    pipeline:
      stages:
        - stage1
        - loop:
            loopcondition: path.to.callback     # returns bool
            stages:
              - substage1
              - substage2
              - substage3
        - stage2

    Every plain stage name (e.g. "equilibrate") must correspond to a
    top-level section of the same name in the config.  A loop item is a
    mapping with exactly two keys:

      * loopcondition - callback string that returns True when the
        loop should terminate.

      * stages - ordered list of stages executed each iteration.  The
        list can itself contain nested loop blocks.
    """
    def __init__(self, cfg: DictConfig):
        if not isinstance(cfg, DictConfig):
            raise TypeError(
                "KimConvergence expects a Hydra DictConfig.  "
                "Launch it via a @hydra.main‑decorated entry point."
            )

        # Keep both forms handy
        self.cfg: DictConfig = cfg

        # Parse the pipeline section up‑front
        self.pipeline = list(cfg.get("pipeline", {}).get("stages", []))

        # Shared runtime state (can be mutated by callbacks)
        self.step: int = 0
        self.step_fn: Callable[["KimConvergence"], Any]
        self.max_steps: int
        # state is a named time‑series of N‑D NumPy arrays
        #   * key   = str (e.g. "positions", "energy", "temperature")
        #   * value = list of np.ndarray, one entry per step
        self.state: DefaultDict[str, List[np.ndarray]] = collections.defaultdict(list)

        self.log: logging.Logger

    def _run_stage(self, mod_path: str) -> None:
        try:
            mod = importlib.import_module("kim_convergence.stages."+mod_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"Could not import stage module '{mod_path}': {e}")

        if not hasattr(mod, "run"):
            raise AttributeError(f"Module '{mod_path}' does not define a 'run(self)' function.")

        mod.run(self)

    def _resolve_callback(self, mod_path: str) -> None:
        name = mod_path.split("_")[0].split(".")[-1] # callback file is the first element
        try:
            mod = importlib.import_module("kim_convergence.callbacks."+mod_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"Could not import loop check callback '{mod_path}': {e}")
        return getattr(mod, name)
        
    def _execute(self, stages) -> None:
        for item in stages:
            if isinstance(item, str):                         # plain stage
                self._run_stage(item.split("_")[0])           # stage name is the first element

            elif isinstance(item, DictConfig) and "loop" in item:
                loop_cfg = item.loop
                cond: Callable[["KimConvergence"], bool] = self._resolve_callback(
                    loop_cfg.loopcondition
                )
                while cond(self,loop_cfg.loopargs,loop_cfg.loopkey):
                    self._execute(loop_cfg.stages)                  # recurse into loop
            
    # ------------------------------ API ------------------------------
    def run(self) -> None:
        """Execute the pipeline defined in cfg.pipeline.stages."""
        self._execute(self.pipeline)
