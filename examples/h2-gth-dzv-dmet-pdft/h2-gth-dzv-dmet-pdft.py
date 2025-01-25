import numpy as np
from pyscf import lib
from pyscf.pbc import gto, scf
import pywannier90
from pdmet import dmet
from pdmet.tools import tchkfile
from pyscf import mcpdft

lib.logger.TIMER_LEVEL = lib.logger.INFO

cell = gto.Cell()
cell.atom = '''H 5 5 4; H 5 5 5'''
cell.basis = 'gthdzvp'
cell.spin = 0
cell.verbose = 4
cell.max_memory=5000
cell.a = np.eye(3)*10
cell.build()

kmesh = [1, 1, 1]
kpts = cell.make_kpts(kmesh)

'''================================'''
''' Read the HF wave function'''
'''================================'''
khf = scf.KROHF(cell, kpts=kpts).density_fit()
khf.with_df._cderi_to_save = 'gdf.h5'
khf.exxdiv = None
khf.kernel()
tchkfile.save_kmf(khf, 'chk_HF')

'''================================'''
''' Contruct MLWFs '''
'''================================'''
kmf = tchkfile.load_kmf(cell, khf, kmesh, 'chk_HF')
num_wann = cell.nao
keywords = \
'''
num_iter = 5000
begin projections
random
H: s
end projections
guiding_centres = .true.
'''
w90 = pywannier90.W90(kmf, cell, kmesh, num_wann, other_keywords=keywords)
w90.kernel()
tchkfile.save_w90(w90, 'chk_w90')

'''================================'''
''' Run Gamma-point MC-PDFT '''
'''================================'''

hf = scf.ROHF(cell).density_fit()
hf.with_df._cderi = 'gdf.h5'
hf.exxdiv = None
hf.verbose=4
hf.kernel()

mc = mcpdft.CASSCF(hf, 'tPBE', 2, 2, grids_level=6)
mc = mc.fix_spin_(shift=0.5, ss=0)
mc.verbose = 4
mc.kernel()

'''================================'''
''' Run DMET '''
'''================================'''
pdmet = dmet.pDMET(cell, kmf, w90, solver = 'CASPDFT') #pass an hf object (scf.ROHF(cell).density_fit()), not a khf object i.e. scf.KROHF(cell, kpts).density_fit(). scf.KROHF(cell, kpts).density_fit() prints an output type not compatible with slicing.
pdmet.impCluster = [1]
pdmet._impOrbs_threshold = 10
pdmet.kmf_chkfile = 'chk_HF'
pdmet.w90_chkfile = 'chk_w90'
pdmet.twoS = 0
pdmet.molist = [0,1]
pdmet.cas = (2,2)
pdmet.e_shift = 0.5
pdmet.initialize()
pdmet.one_shot()
