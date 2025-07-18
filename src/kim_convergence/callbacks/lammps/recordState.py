from kim_convergence.core import KimConvergence

def _fetchLammps(lmp, x_name):
    """
    Return the current value of a LAMMPS quantity.

    Accepted prefixes (same notation you'd use in an equal style expression):

      v_myvar        => variable  ID  'myvar'
      c_mycompute    => compute   ID  'mycompute'   (scalar index 0)
      f_myfix[3]     => fix       ID  'myfix', col  3
      temp, etotal…  => bare thermo keyword (no prefix)

    For vector/array computes or fixes, tweak the index handling as needed.
    """
    try:
        if x_name.startswith("v_"):               # variable
            return lmp.extract_variable(x_name[2:], None, 0)

        if x_name.startswith("c_"):               # compute (scalar)
            return lmp.extract_compute(x_name[2:], 0, 0)

        if x_name.startswith("f_"):               # fix (allow f_id or f_id[index])
            inner = x_name[2:]
            if "[" in inner:                      # e.g. f_myfix[3]
                fid, idx = inner.split("[", 1)
                idx = int(idx.rstrip("]"))
            else:
                fid, idx = inner, 0
            return lmp.extract_fix(fid, idx, 0, 0)

        # fall back to built‑in thermo keyword (temp, press, etotal, …)
        return lmp.get_thermo(x_name)

    except Exception as err:
        raise RuntimeError(f"cannot fetch '{x_name}': {err}") from err

def recordState(kc: KimConvergence, params):
    for key in params['keys']:
        kc.state[key].append(_fetchLammps(kc.lmp,key))