#include "mycommand.h"
#include "input.h"
#include "error.h"

#include <sstream>

using namespace LAMMPS_NS;

/* constructor just forwards the pointer */
MyCommand::MyCommand(LAMMPS *lmp) : Command(lmp) {}

void MyCommand::command(int narg, char **arg)
{
  /* syntax:  mycommand file variable */
  if (narg != 2)
    error->all(FLERR,
      "Syntax: mycommand <filename> <lammps‑variable‑name>");

  const char *fname = arg[0];      /* first token after keyword   */
  const char *vname = arg[1];      /* e.g. “alpha” becomes v_alpha */

  /* 1. a friendly greeting                                          */
  lmp->input->one("print \"hello world (from mycommand)\"");

  /* 2. build an ordinary ‘python … file …’ command line             */
  std::ostringstream line;
  line << "python __mycommand_kernel "
       << "input 3 SELF \"" << fname << "\" v_" << vname
       << " format psf  "
       << "file mycommand_kernel.py";

  /* 3. hand the line back to the input processor                    */
  lmp->input->one(line.str().c_str());
}
