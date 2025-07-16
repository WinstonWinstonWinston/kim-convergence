# Re‑entry point created by the C++ wrapper above ------------------
from lammps import lammps

def __mycommand_kernel(lmpptr, filename, var_value):
    lmp = lammps(ptr=lmpptr)             # reconstruct the C++ handle

    lmp.command(f'print "Python sees file: {filename}"')
    lmp.command(f'print "Variable value : {var_value}"')
