# Installing kim-convergence

Repo: [https://github.com/WinstonWinstonWinston/kim-convergence](https://github.com/WinstonWinstonWinston/kim-convergence)

```bash
git clone https://github.com/WinstonWinstonWinston/kim-convergence.git
cd kim-convergence
chmod +x setup_kim_convergence_env.sh   # make the install/setup script executable
./setup_kim_convergence_env.sh          # modify as needed for your machine (modules, conda/micromamba, paths)
```

> The `.sh` script may need edits for your environment (e.g., swapping `conda` for `micromamba`, changing module names, CUDA arch, etc. I originally used conda on my mac, but micromamba is reccomended here, I've run into less issues with it).

**Activate the environment before installing LAMMPS:**

```bash
conda activate kc-dev    # or
micromamba activate kc-dev
```

---

## Building LAMMPS with KimConvergence

> **Do not change these instructions.** Commands are kept exactly as provided; only minimal Markdown formatting was added.

---

## Step 1: Clone release branch

```bash
git clone -b release https://github.com/lammps/lammps.git lammps
```

## Step 1.5: Copy KimConvergence command files into LAMMPS

Put the three KimConvergence files into `lammps/src/EXTRA-COMMAND/` on your machine (this matches the upstream path in the LAMMPS repo):

* `kim_convergence_hook.py`
* `kim_convergence.cpp`
* `kim_convergence.h`

## Step 2: Load modules (can change from machine to machine, these worked for me on MSI)

```bash
module purge
module load gcc/8.2.0
module load ompi/3.1.6/gnu-8.2.0
module load cuda/11.2
```

## Step 3: Sanity check

```bash
which nvcc
which mpicxx
which gcc
```

**Expected:**

```
/common/software/install/migrated/cuda/11.2/bin/nvcc
/common/software/install/migrated/openmpi/el6/3.1.6/gnu-8.2.0/bin/mpicxx
/common/software/install/migrated/gcc/8.2.0/bin/gcc
```

## Step 4: Prepare build directory

```bash
cd lammps
mkdir build
cd build
```

**You may also want to add `-DPKG_KIM=ON` (or other MLIP-related packages/flags) to the CMake line if you need them.**

```bash
cmake \
  -C ../cmake/presets/all_on.cmake \
  -C ../cmake/presets/nolib.cmake \
  -C ../cmake/presets/basic.cmake \
  -DPKG_GPU=ON \
  -DGPU_API=cuda \
  -DGPU_ARCH=sm_80 \
  -DPKG_OPENMP=ON \
  -DBUILD_OMP=ON \
  -DPKG_EXTRA-COMMAND=ON \
  -DPKG_PYTHON=ON \
  -DPYTHON_EXECUTABLE=$CONDA_PREFIX/bin/python \
  -DPYTHON_INCLUDE_DIR=$CONDA_PREFIX/include/python3.Ym \
  -DPYTHON_LIBRARY=$CONDA_PREFIX/lib/libpython3.Ym.so \
  -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX \
  -DBUILD_SHARED_LIBS=ON \
  ../cmake
```

## Step 6: Compile

```bash
cmake --build .
```
    