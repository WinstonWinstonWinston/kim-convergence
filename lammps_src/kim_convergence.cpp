#include "kim_convergence.h"
#include "input.h"
#include "error.h"

#include <sstream>
#include <string>
#include <cstring>  // for strrchr()

using namespace LAMMPS_NS;

KimConvergence::KimConvergence(LAMMPS *lmp) : Command(lmp) {}

void KimConvergence::command(int narg, char **arg)
{
  if (narg != 1)
    error->all(FLERR,"Syntax: kim_convergence <filename>");

  // 1) Grab the filename
  const std::string fname(arg[0]);

  // 2) Locate your Python hook script alongside this .cpp
  const char *srcfile = __FILE__;
  const char *slash   = strrchr(srcfile,'/');
  std::string helper;
  if (slash) {
    helper.assign(srcfile, slash - srcfile + 1);
    helper.append("kim_convergence_hook.py");
  } else {
    helper = "kim_convergence_hook.py";
  }

  // 3) Register the Python function for later invocation
  //    -- here: function name = kim_convergence
  //    -- input 2 args: SELF pointer + filename string
  //    -- format 'ps' (p=pointer, s=string)
  //    -- load from file helper
  std::ostringstream regCmd;
  regCmd << "python kim_convergence "
            "input 2 SELF \"" << fname << "\" "
         << "format ps "
         << "file \"" << helper << "\"";
  lmp->input->one(regCmd.str().c_str());

  // 4) Invoke it immediately
  std::ostringstream invCmd;
  invCmd << "python kim_convergence invoke";
  lmp->input->one(invCmd.str().c_str());
}
