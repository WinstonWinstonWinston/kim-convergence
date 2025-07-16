import numpy as np
from kim_convergence.core import KimConvergence
import matplotlib.pyplot as plt
from typing import DefaultDict
from omegaconf import DictConfig
import collections

def rangeloop(kc: KimConvergence, loopargs:DictConfig, loopkey: str) -> bool:
    if not hasattr(kc, 'loop_states') or kc.loop_states is None:
        kc.loop_states: DefaultDict[str, int] = collections.defaultdict(lambda: loopargs.start - loopargs.step) # type: ignore

    kc.loop_states[loopkey] += loopargs.step

    condition = kc.loop_states[loopkey] >= loopargs.stop

    kc.log.info(
        f"[rangeloop]: loopkey = {loopkey} | itr = {kc.loop_states[loopkey]}| condition = {condition}"
    )

    return condition