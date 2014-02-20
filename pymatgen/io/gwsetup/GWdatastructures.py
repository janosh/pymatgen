#!/usr/bin/env python

"""
Script to test writing GW Input for VASP.
Reads the POSCAR_name in the the current folder and outputs GW input to
subfolders name
"""

from __future__ import division

__author__ = "Michiel van Setten"
__copyright__ = " "
__version__ = "0.9"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "Oct 23, 2013"

import os
import operator

from pymatgen.io.abinitio.netcdf import NetcdfReader
from pymatgen.io.vaspio.vasp_output import Vasprun
from pprint import pprint

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


class GWConvergenceData():
    def __init__(self, structure, spec):
        self.structure = structure
        self.spec = spec
        self.data = {}
        self.name = structure.composition.reduced_formula

    def read(self):
        if self.spec['code'] == 'ABINIT':
            read_next = True
            n = 3
            while read_next:
                output = os.path.join(self.name,  'work_0', 'task_' + str(n), 'outdata', 'out_SIGRES.nc')
                print output
                if os.path.isfile(output):
                    n += 1
                    data = NetcdfReader(output)
                    data.print_tree()
                    self.data.update({n: {'ecuteps': data.read_value('ecuteps'), 'nbands': data.read_value('sigma_nband'), 'gwgap': data.read_value('egwgap')}})
                    data.close()
                else:
                    read_next = False
        elif self.spec['code'] == 'VASP':
            tree = os.walk('.')
            n = 0
            for dirs in tree:
                if self.name in dirs[0] and ('G0W0' in dirs[0] or 'GW0' in dirs[0] or 'scGW0' in dirs[0]):
                    run = os.path.join(dirs[0], 'vasprun.xml')
                    kpoints = os.path.join(dirs[0], 'IBZKPT')
                    data = Vasprun(run, ionic_step_skip=1)
                    parameters = data.__getattribute__('incar').to_dict
                    bandstructure = data.get_band_structure(kpoints)
                    self.data.update({n: {'ecuteps': parameters['ENCUTGW'], 'nbands': parameters['NBANDS'], 'gwgap': bandstructure.get_band_gap()['energy']}})
                    n += 1
                    #print 'gap: ', bandstructure.get_band_gap()['energy'], ' direct : ', bandstructure.get_band_gap()['direct']
                    #print 'cbm: ', bandstructure.get_cbm()['energy'], data.actual_kpoints[bandstructure.get_cbm()['kpoint_index'][0]]
                    #print 'vbm: ', bandstructure.get_vbm()['energy'], data.actual_kpoints[bandstructure.get_vbm()['kpoint_index'][0]]
                    #print 'gap: ', bandstructure.get_cbm()['energy'] - bandstructure.get_vbm()['energy']
                    #print 'direct gap: ', bandstructure.get_direct_band_gap()

    def print_plot_data(self):
        data_list = []
        for k in self.data:
            data_list.append([self.data[k]['nbands'], self.data[k]['ecuteps'], self.data[k]['gwgap']])
        for data in sorted(data_list):
            print data[0], data[1], data[2]


        '''
        [u'space_group', u'primitive_vectors', u'reduced_symmetry_matrices', u'reduced_symmetry_translations',
         u'atom_species', u'reduced_atom_positions', u'valence_charges', u'atomic_numbers', u'atom_species_names',
         u'chemical_symbols', u'pseudopotential_types', u'symafm', u'kpoint_grid_shift', u'kpoint_grid_vectors',
         u'monkhorst_pack_folding', u'reduced_coordinates_of_kpoints', u'kpoint_weights', u'number_of_electrons',
         u'exchange_functional', u'correlation_functional', u'fermi_energy', u'smearing_scheme', u'smearing_width',
          u'number_of_states', u'eigenvalues', u'occupations', u'tphysel', u'occopt', u'istwfk', u'shiftk',
         u'kptrlatt', u'ngkpt_shiftk', u'ecutwfn', u'ecuteps', u'ecutsigx', u'sigma_nband', u'gwcalctyp',
         u'omegasrdmax', u'deltae', u'omegasrmax', u'scissor_ene', u'usepawu', u'kptgw', u'minbnd', u'maxbnd',
         u'degwgap', u'egwgap', u'en_qp_diago', u'e0', u'e0gap', u'sigxme', u'vxcme', u'vUme', u'degw', u'dsigmee0',
         u'egw', u'eigvec_qp', u'hhartree', u'sigmee', u'sigcmee0', u'sigcmesi', u'sigcme4sd', u'sigxcme4sd',
         u'ze0', u'omega4sd']
        '''