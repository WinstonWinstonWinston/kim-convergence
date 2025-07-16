#ifdef COMMAND_CLASS
/*  Tell LAMMPS a new style called "mycommand" exists               */
CommandStyle(mycommand,MyCommand)
#else

#include "command.h"

namespace LAMMPS_NS {

class MyCommand : public Command {
 public:
  MyCommand(class LAMMPS *);
  void command(int, char **);      // the only required method
};

}      // namespace LAMMPS_NS
#endif
