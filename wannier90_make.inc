F90 = ifort
#Add next two lines for parallel postw90. Choose the correct name of the mpi f90 wrapper
#COMMS  = mpi
#MPIF90 = mpgfortran #mpif90
FCOPTS = -O3 -fPIC -g
LDOPTS =
LIBDIR =/software/intel/parallel_studio_xe_2020_update1
LIBS = -lpthread -lstdc++ -L$(LIBDIR)/mkl/lib/intel64 -lmkl_core -lmkl_intel_lp64 -lmkl_sequential  -L$(LIBDIR)/lib/intel64 -limf -lintlc