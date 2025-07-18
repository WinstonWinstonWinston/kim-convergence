#ifdef COMMAND_CLASS
CommandStyle(kim_convergence,KimConvergence)  // registers new keyword “kim_convergence”
#else
#ifndef LMP_KIM_CONVERGENCE_H
#define LMP_KIM_CONVERGENCE_H

#include "command.h"

namespace LAMMPS_NS {

class KimConvergence : public Command {
 public:
  KimConvergence(class LAMMPS *);
  void command(int, char **);
};

}  // namespace LAMMPS_NS

#endif   /* LMP_KIM_CONVERGENCE_H */
#endif   /* COMMAND_CLASS */