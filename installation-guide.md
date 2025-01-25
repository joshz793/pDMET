# Sample Installation Guide: 
Last Edited: 24th Jan, 2025

[24 Jan 2025] This installation guide has been written by Joshua Zhou. This guide is currently written *strictly* for installing pDMET on the Midway3 Cluster at the University of Chicago.

This guide will step the user through installation of each dependency of pDMET. Even if these dependencies are already installed on the user's system, **please follow from the beginning, as dependency versions are critical**.


## Loading the proper modules
As of 24 Jan 2025, the following modules must be loaded. It has yet to be explored how strict these version requirements are, as certain filepaths later are still hard-coded.
```
module load intel/2022.0 mkl/2023.1 lapack/3.10.0
```
To prevent possible conflicts, verify the proper modules are loaded using 
```
module list
```
The following is expected to return
> Currently Loaded Modulefiles:
> 1) slurm/current   2) rcc/default   3) mkl/2023.1   4) intel/2022.0   5) lapack/3.10.0

If there are any unexpected modules loaded, please unload these using 
```
module unload <module_name>
```

## Getting Started
First, we will prepare a directory and clone this repository (if you have not already done so). This repository contains files that will be helpful to create a working installation.
1. Prepare a directory to perform the installation of dependencies. 
   ```
   mkdir pdmet_dependencies
   cd pdmet_dependencies
   dir=$(pwd) # this sets a variable that will be used to navigate later on
   ```
2. Clone this repository
   ```
   git clone https://github.com/joshz793/pDMET.git
   ```
Now, we will perform this installation step-by-step through each dependency.
## Setting up the conda environment

**Before beginning, ensure some flavor of conda/mamba is loaded. Both a custom installation or loaded module *should* work (This has not been thoroughly tested yet though)**

1. Using `pDMET_env.yml` (included in the github), create a new conda environment:
   ```
   conda env create --file=pDMET/pDMET_env.yml
   ```
   This will create a conda environment with the name "pDMET". If an environment already exists with this name, or you would like to install it with a different name, an additional flag may be included:
   ```
   conda env create --file=pDMET/pDMET_env.yml --name <env_name>
   ```
2. Activate the environment
   ```
   conda activate <env_name>
   ```
## Installation of PySCF:
**The currently available version of pDMET is known to be dependent on specific versions of PySCF and PySCF-forge.** This installation guide will provide specific versions to compile which have been found to work. There is no guarantee other versions are compatible at the moment.

1. Clone PySCF. PySCF may be found at https://github.com/pyscf/pyscf. **If you regularly use a different PySCF installation, see *[PySCF Version Swapping](#pyscf-version-swapping)***
   ```
   cd $dir
   git clone https://github.com/pyscf/pyscf.git
   cd pyscf
   git checkout b337109d8 # This is the tag associated with our desired version
   ```
2. Build PySCF using intel compilers
   ```
   cd pyscf/lib/
   mkdir build
   cd build
   CC=icc CXX=icpc cmake -DBLA_VENDOR=Intel10_64lp_seq ..
   make -j 8 # The -j flag parallelizes the build process.
   ```
3. Add PySCF to the PYTHONPATH:
   ```
   export PYTHONPATH=$dir/pyscf:$PYTHONPATH
   ```
4. Test the python installation
   ```
   cd $dir
   python -c 'import pyscf; print(f"pyscf version {pyscf.__version__} installed!")'
   ```
If this returns `pyscf version 2.1.0 installed!`, then we have successfully installed the desired version and made it accessible in python.

## Installation of pyscf-forge:
If you already have an installation of pyscf-forge, you may replicate the instructiosn in [Additional Note 1](#additional-note-1), or simply `git checkout` your existing version and recompile each time (`git checkout -` may be used to return to your previous version).
1. pyscf-forge may be found at https://github.com/pyscf/pyscf-forge. Clone this directory. 
   ```
   cd $dir
   git clone https://github.com/pyscf/pyscf-forge.git
   ```
2. To get a version that has been tested to be compatible:
   ```
   cd pyscf-forge
   git checkout f80d249
   ```
3. Compile pyscf-forge
   ```
   cd pyscf/lib
   mkdir build
   cd build
   CC=icc CXX=icpc cmake -DBLA_VENDOR=Intel10_64lp_seq ..
   make
   ```
4. *Important*: Set the following environment variable to allow PySCF to find pyscf-forge
   ```
   export PYSCF_EXT_PATH=$dir/pyscf-forge
   ```
5. From Step 4, PySCF should be able to properly find pyscf-forge.

## Installation of mrh
The current version of pDMET depends on methods developed by Matthew R. Hermes, found at https://github.com/MatthewRHermes/mrh

**Current maintenance is undergoing to shift away dependency on this library, as needed methods are likely available in more recent PySCF or pyscf-forge versions**

1. Clone mrh
   ```
   cd $dir
   git clone https://github.com/MatthewRHermes/mrh.git
   ```
2. As of 24 January 2025, we (luckily) do not need to change the version of this repository. We may proceed to build:
   ```
   cd mrh/lib/
   mkdir build
   cd build
   CC=icc CXX=icpc cmake -DBLA_VENDOR=Intel10_64lp_seq ..
   make
   ```
3. Add mrh to PYTHONPATH:
   ```
   export PYTHONPATH=$dir/mrh:$PYTHONPATH
   ```
4. And verify proper installation:
   ```
   cd $dir
   python -c "import mrh"
   ```
5. If nothing returns, then installation is successful.

## Install Wannier90 and pyWannier90
[Wannier90](http://www.wannier.org/download) is an open-source code to generate Maximally-Localised Generalised Wannier Functions. 

[pyWannier90](https://github.com/hungpham2017/pyWannier90) is a Python interface for Wannier90 developed by Hung Q. Pham.

1. Download wannier90 either from http://www.wannier.org/download/ or https://github.com/wannier-developers/wannier90. *Important*: If you download from the github, make sure you download the release version 3.1.0. This guide will proceed using the gzipped .tar file
   ```
   cd $dir
   wget https://github.com/wannier-developers/wannier90/archive/refs/tags/v3.1.0.tar.gz
   ```
2. Unzip wannier90
   ```
   tar -xvzf v3.1.0.tar.gz
   ```
   ***DO NOT BUILD WANNIER90 YET***

3. We will now download pyWannier90 from https://github.com/hungpham2017/pyWannier90, and do a little configuration.
   ``` 
   cd $dir
   git clone https://github.com/hungpham2017/pyWannier90.git
   cp pyWannier90/src/wannier_lib.F90 $dir/wannier90-3.1.0/src/wannier_lib.F90
   ```
   If you look through the pyWannier90 files, you will find a line that requests to be modified in `pywannier90.py`. We will (safely) ignore this request by manually setting the PYTHONPATH environment variable.
4. Prepare to build wannier90
   ```
   cd $dir/wannier90-3.1.0
   cp $dir/pDMET/wannier90_make.inc make.inc
   ```
   If you know what you are doing, feel free to modify make.inc as you see fit. Otherwise, this file will create an working installation compatible with the rest of the installation guide.
5. We will need to do both the default `make`, as well as make some libraries. If an error throws in either case, ensure the environment and modules are loaded properly and run `make clean` before running this block again.
   ```
   make -j 8 && make lib
   ```
6. Prepare to build pywannier90
   ```
   cd $dir/pyWannier90/src
   cp $dir/pDMET/pyWannier90_Makefile ./Makefile
   ```
   Run the following code to configure the Makefile according to your directory system. **If you change the location of the files made during the installation guide, you may need to change the `W90DIR` variable in this Makefile**
   ```
   sed -i "s&PLACEHOLDER&$dir/wannier90\-3\.1\.0&g" Makefile
   ```
   If you are a user on a future Midway3 that does not have the version of intel specified by the `LIBDIR` variable, or arefollowing this guide to install pDMET on a different system, you must additionally update `LIBDIR` to point to an available intel library. 
7. Now we build pywannier90
   ```
   make
   ```
   Once again, if there is an error, make sure to `make clean` before attempting again.
8. Add pywannier90 to PYTHONPATH
   ```
   export PYTHONPATH=$dir/pyWannier90/src:$PYTHONPATH
   ```
9. And test the installations
   ```
   cd $dir
   python -c 'import pywannier90' # pywannier90 test
   python -c 'import libwannier90' # wannier90 test
   ```
   If nothing returns from these lines, then we should be good to continue.

## Install Modeling and Crystallographic Utilities (mcu)
*This is an optional installation step.* 

Pham, H. Q. MCU: Modeling and Crystallographic Utilities, 2021 https://github.com/hungpham2017/mcu.

MCU is a package developed by Hung Q. Pham for the analysis of periodic wavefunctions and crystallography.

Included examples of pDMET use this package for visualization purposes. Ensure the relevant lines are removed if you decide to skip this installation.
1. Clone the dev branch from https://github.com/hungpham2017/mcu (the master branch does not have a needed cell.py file)
   ```
   cd $dir
   git clone -b dev https://github.com/hungpham2017/mcu.git
   ```
2. Modify the W90LIB path in mcu/mcu/wannier90/pywannier90_vasp.py
   ```
   sed -i "s&W90LIB =.*&W90LIB = $dir/wannier90-3.1.0&" mcu/mcu/wannier90/pywannier90_vasp.py
   ```
3. Add mcu to PYTHONPATH
   ```
   export PYTHONPATH=$dir/mcu:$PYTHONPATH
   ```
4. Verify mcu installation
   ```
   python -c 'import mcu'
   ```
   If nothing returns, then mcu should be properly installed

## Finally: pDMET Installation
With all the dependencies properly installed, we may now continue with a straightforward installation of pDMET.
1. Create a build directory
   ```
   cd $dir/pDMET/pdmet/lib
   sed -i "s&CONDA_PREFIX&$CONDA_PREFIX&g" CMakeLists.txt
   mkdir build
   cd build
   ```
2. Set some environment variables. ***Important***: Check these paths actually lead to the desired directories. Midway3 modules may be updated, and other systems will not have the same filepaths.
   ```
   export MKLROOT=/software/intel/parallel_studio_xe_2020_update1/mkl/
   export LD_LIBRARY_PATH=$MKLROOT/lib:$LD_LIBRARY_PATH
   ```
3. Build.
   ```
   CC=icc CXX=icpc cmake -DBLA_VENDOR=Intel10_64lp_seq ..
   make
   ```
4. Add pDMET to PYTHONPATH
   ```
   export PYTHONPATH=$dir/pDMET:$PYTHONPATH
   ```
5. Test our installation
   ```
   python -c 'import pdmet'
   ```
   You may see FutureWarnings. If these are the only outputs, then we likely have a successful installation of pDMET!

Before you close the terminal, it is recommended you save your environment variables. A simple way to keep the extensive PYTHONPATH we created during the installation process may be found at [Saving PYTHONPATH](#saving-pythonpath)
## Aditional Notes
### PySCF Version Swapping
If you require a different version of PySCF for other tasks, you may consider the following option to make your life easier:

1. Clone the repository again, save this repository under a separate name, and checkout to the proper version
   ```
   git clone https://github.com/pyscf/pyscf.git pyscf2.1.0 # Clone PySCF into a directory named "pyscf2.1.0"
   cd pyscf2.1.0
   git checkout b337109d8 # This is the tag associated with the desired version
   cd ..
   ```
2. Assuming your previous installation is at a directory `./pyscf`, and your programs find pyscf using a PATH/PYTHONPATH leading to this directory, the following can be done to switch PySCF versions:
   ```
   mv ./pyscf ./pyscf2.7.0 # Replaced the numbers with the corresponding version of pyscf. This is for your own bookkeeping
   ln -s ./pyscf2.1.0 ./pyscf # Creates a symbolic link to our previously made PySCF version
   ```
3. When you are done using pDMET and need to switch back to your other version, do the following:
   ```
   unlink pyscf
   ln -s ./pyscf2.7.0 ./pyscf
   ```
   You may always check which version of PySCF your python finds with the following:
   ```
   python -c 'import pyscf; print(pyscf.__version__)'
   ```

### Saving PYTHONPATH
```
echo $PYTHONPATH > $dir/pythonpath.txt
```
When you need to use pDMET again, you may then set your PYTHONPATH easily with (adjusting the path as necessary).
```
export PYTHONPATH=$(cat pythonpath.txt):$PYTHONPATH
```
This may similarly be done for the PYSCF_EXT_PATH, although this likely a much shorter path than PYTHONPATH
