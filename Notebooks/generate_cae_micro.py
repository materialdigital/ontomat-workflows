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

def generate_cae(vol_frac, fiber_rad, interface_ratio, depth, num_rad, num_depth, cae_name, job_name, abaqus_json, plugin_path):
    
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
        abaqus_json['micro']['fiber']['E'], abaqus_json['micro']['fiber']['nu']), ))
    mdb.models['HexFiberArray'].materials['MatMatrix'].elastic.setValues(table=((
        abaqus_json['micro']['matrix']['E'], abaqus_json['micro']['matrix']['nu']), ))
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
 
    abaqus_json_path = input_args[-1]
    
    with open(abaqus_json_path) as f:
        abaqus_json = json.load(f)
    

        
    
    vol_frac = str(abaqus_json["micro"]["fiber"]["volume_content"])
    fiber_rad = str(abaqus_json["micro"]["fiber"]["radius"])
    interface_ratio = str(abaqus_json["micro"]["fiber"]["interface_ratio"])
    depth = str(abaqus_json["micro"]["geometry"]["depth"])
    num_rad = str(abaqus_json["micro"]["geometry"]["mesh"]["num_rad"])
    num_depth = str(abaqus_json["micro"]["geometry"]["mesh"]["num_depth"])
    
    sim_path = str(abaqus_json["simulation"]["sim_path"]).replace('\\', '\\')
    plugin_path = str(abaqus_json["simulation"]["plugin_path"])
    
    os.chdir(sim_path)
    
    cae_name = str(abaqus_json["simulation"]["cae_name"])
    job_name = str(abaqus_json["simulation"]["job_name"])

    
    generate_cae(vol_frac, fiber_rad, interface_ratio, depth, num_rad, num_depth, cae_name, job_name, abaqus_json, plugin_path)
    write_job(job_name)