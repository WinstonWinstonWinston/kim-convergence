from kim_convergence import KimConvergence
import lammps

def logger(kc: KimConvergence, lmp: lammps.core.lammps, nevery, nrepeat, nfreq):
    """
    fix avp all ave/time  ${nevery} ${nrepeat} ${nfreq} c_thermo_press mode vector
    thermo		${nthermo}
    thermo_style custom step temp pe press f_avp[1] f_avp[2] f_avp[3] f_avp[4] f_avp[5] f_avp[6] lx ly lz vol
    thermo_modify norm no
    """