from kim_convergence import KimConvergence
import lammps

def nvt(kc: KimConvergence, lmp: lammps.core.lammps, method: str, fixid: str, tstart: float, tstop: float, tdamp: float):
    if method == "noseHoover":
        lmp.command(f"fix {fixid} all nvt temp {tstart} {tstop} {tdamp}")
    elif method == "langevin":
        # applies inherent lammps seed, which should be set for every simulation.
        # error should be thrown if there is no lammps seed
        lmp.command(f"fix {fixid} all langevin{tstart} {tstop} {tdamp}" + "${seed}")
    else:
        raise NotImplementedError(f"{method} is not supported in kim-convergence")

    lmp.command()