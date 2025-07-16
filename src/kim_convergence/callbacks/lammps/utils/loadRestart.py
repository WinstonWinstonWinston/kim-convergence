from kim_convergence import KimConvergence
import lammps

def loadRestart(kc: KimConvergence, lmp: lammps.core.lammps, restart: str):
    lmp.command('read_restart ' + restart)
