from kim_convergence import KimConvergence
import lammps

# ToDo, should we support extractions which are not variables?
def recordState(kc: KimConvergence, lmp: lammps.core.lammps, keys: list):
    for key in keys:
        kc.state[key].append(lmp.extract_variable(key))