from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *

import numpy as np

# odb_path = "W:\OntOMat\periodic\UD\Job-1.odb"
odb_path = r"Periodic_Homogenization_UD.odb"
vol = 45.2**3

odb = openOdb(path=odb_path)

step = odb.steps['HomogStiff-Initial']

region_keys = step.historyRegions.keys()

region_node_normal = step.historyRegions[region_keys[0]]
region_node_shear = step.historyRegions[region_keys[1]]

generic_string = 'RF{} Load case LC-{}-HOMOGSTIFF-INITIAL-E{}'

homogenized_stiffness_voigt = np.zeros((6,6)) # non-normalized Voigt notation

RF_sequence = [1,2,3,1,2,3]
E_sequence = [11,22,33,12,13,23]

for i in range(6):
    for j in range(6):
        specific_string = generic_string.format(RF_sequence[j], int(i+1), E_sequence[i])
        if j < 3:
            stiffness = region_node_normal.historyOutputs[specific_string].data[0][1]/vol
        else:
            stiffness = region_node_shear.historyOutputs[specific_string].data[0][1]/(2*vol)
            
        homogenized_stiffness_voigt[i,j] = stiffness

homogenized_stiffness_mandel = homogenized_stiffness_voigt.copy() # normalized Mandel notation
homogenized_stiffness_mandel[:,3:] *= np.sqrt(2)
homogenized_stiffness_mandel[3:,:] *= np.sqrt(2)

np.savetxt("homogenized_stiffness_voigt.csv", homogenized_stiffness_voigt, delimiter=",")
np.savetxt("homogenized_stiffness_mandel.csv", homogenized_stiffness_mandel, delimiter=",")