# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import sys
import numpy as np
import os
import json
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

def generate_cae(vol_frac, fiber_rad, interface_ratio, depth, num_rad, num_depth, cae_name, job_name, materials, plugin_path):
    
    # sys.path.insert(46, plugin_path)
    sys.path.append(plugin_path)
    import microMechanics
    from microMechanics.mmpBackend import Interface
    from microMechanics.mmpBackend.mmpInterface.mmpRVEConstants import *
    from microMechanics.mmpBackend.mmpKernel.mmpLibrary import mmpRVEGenerationUtils as RVEGenerationUtils
    Interface.Library.RVEGenerator(rveType='UD_HexPack', rveParameters=((
        'Volume fraction', vol_frac), ('Fiber radius', fiber_rad), ('Interface ratio', 
        interface_ratio), ('Depth', depth), ('Num Rad', num_rad), ('Num Depth', num_depth)))
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    p = mdb.models['HexFiberArray'].parts['HexPackPart']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    mdb.models['HexFiberArray'].materials['MatFiber'].elastic.setValues(table=((
        materials['fiber']['E'], materials['fiber']['nu']), ))
    mdb.models['HexFiberArray'].materials['MatMatrix'].elastic.setValues(table=((
        materials['matrix']['E'], materials['matrix']['nu']), ))
    a = mdb.models['HexFiberArray'].rootAssembly
    a.regenerate()
    a = mdb.models['HexFiberArray'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
    mdb.Job(name=job_name, model='HexFiberArray', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    Interface.Loading.MechanicalModelMaker(constraintType='PERIODIC', 
        drivenField='STRAIN', modelName='HexFiberArray', jobName=job_name, 
        doNotSubmit=True, homogenizeProperties=(True, False, False))
    mdb.saveAs(cae_name)
    
def write_job(job_name):
    mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
    


if __name__ == "__main__":
    
    input_args = sys.argv
 
    materials_path = input_args[-1]
    workflow_input_path = input_args[-2]
    
    with open(materials_path) as f:
        materials = json.load(f)
    
    with open(workflow_input_path) as f:
        workflow_input = json.load(f)
        
    
    vol_frac = str(workflow_input["fiber"]["volume_content"])
    fiber_rad = str(workflow_input["fiber"]["radius"])
    interface_ratio = str(workflow_input["fiber"]["interface_ratio"])
    depth = str(workflow_input["geometry"]["depth"])
    num_rad = str(workflow_input["geometry"]["mesh"]["num_rad"])
    num_depth = str(workflow_input["geometry"]["mesh"]["num_depth"])
    
    sim_path = str(workflow_input["simulation"]["sim_path"]).replace('\\', '\\')
    plugin_path = str(workflow_input["simulation"]["plugin_path"])
    os.chdir(sim_path)
    
    cae_name = str(workflow_input["simulation"]["cae_name"])
    job_name = str(workflow_input["simulation"]["job_name"])

    """
    with open("output3.txt", "w") as f:
        f.write("vol_frac = {}\n".format(vol_frac))
        f.write("type(vol_frac) = {}\n".format(type(vol_frac)))
    """
    
    generate_cae(vol_frac, fiber_rad, interface_ratio, depth, num_rad, num_depth, cae_name, job_name, materials, plugin_path)
    write_job(job_name)