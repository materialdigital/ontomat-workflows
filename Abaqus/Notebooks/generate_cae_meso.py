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

def generate_cae(orientations, material_coefficients, cae_name, job_name, plugin_path):

    layers = len(orientations)

    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(-0.5, -0.5), point2=(0.5, 0.5))
    p = mdb.models['Model-1'].Part(name='Cube', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Cube']
    p.BaseSolidExtrude(sketch=s, depth=1.0)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Cube']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']
    p = mdb.models['Model-1'].parts['Cube']
    
    layer_height = 1.0/layers
    
    for i in range(1, layers):
        p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=i*layer_height)

    p = mdb.models['Model-1'].parts['Cube']
    c = p.cells
    
    d1 = p.datums
    for i in range(1, layers):
        p.PartitionCellByDatumPlane(datumPlane=d1[i+1], cells=p.cells)
        
    p = mdb.models['Model-1'].parts['Cube']
    c = p.cells
    
    for i in range(layers):
        cells = c.findAt(((0.5, 0.5, -layer_height/2.0 + (i+1.0)*layer_height), ))
        region = regionToolset.Region(cells=cells)
        orientation=None
        mdb.models['Model-1'].parts['Cube'].MaterialOrientation(region=region, 
            orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, 
            fieldName='', additionalRotationType=ROTATION_ANGLE, 
            additionalRotationField='', angle=orientations[i], stackDirection=STACK_3)

    # material
    
    mdb.models['Model-1'].Material(name='UD')
    mdb.models['Model-1'].materials['UD'].Elastic(type=ANISOTROPIC, table=(material_coefficients, ))
    mdb.models['Model-1'].HomogeneousSolidSection(name='UD_Section', material='UD', 
        thickness=None)
    
    p = mdb.models['Model-1'].parts['Cube']
    c = p.cells

    region = p.Set(cells=c, name='Set-ALL')
    p.SectionAssignment(region=region, sectionName='UD_Section', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
        
    # mesh and assembly
    
    p = mdb.models['Model-1'].parts['Cube']
    p.seedPart(size=0.1, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    
    a = mdb.models['Model-1'].rootAssembly
    a.Instance(name='Cube-1', part=p, dependent=ON)
    
    # job and micro-mechanics plugin
    
    sys.path.append(plugin_path)
    import microMechanics
    from microMechanics.mmpBackend import Interface
    from microMechanics.mmpBackend.mmpInterface.mmpRVEConstants import *
    from microMechanics.mmpBackend.mmpKernel.mmpLibrary import mmpRVEGenerationUtils as RVEGenerationUtils
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    mdb.Job(name=job_name, model='Model-1', description='', 
        type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    Interface.Loading.MechanicalModelMaker(constraintType='PERIODIC', 
        drivenField='STRAIN', modelName='Model-1', 
        jobName=job_name, doNotSubmit=True, homogenizeProperties=(
        True, False, False))

    mdb.saveAs(cae_name)

def write_job(job_name):
    mdb.jobs[job_name].writeInput(consistencyChecking=OFF)

if __name__ == "__main__":

    input_args = sys.argv
    
    abaqus_json_path = input_args[-1]
    
    with open(abaqus_json_path) as f:
        abaqus_json = json.load(f)
        
    mc = abaqus_json["meso"]["material_parameters"]

    orientations = abaqus_json["meso"]["orientations"]
    material_coefficients = (mc["C11"], mc["C12"], mc["C22"], mc["C13"], mc["C23"], mc["C33"], mc["C14"], mc["C24"], mc["C34"], mc["C44"], mc["C15"], mc["C25"], mc["C35"], mc["C45"], mc["C55"], mc["C16"], mc["C26"], mc["C36"], mc["C46"], mc["C56"], mc["C66"])
    
    sim_path = str(abaqus_json["simulation"]["sim_path"]).replace('\\', '\\')
    plugin_path = str(abaqus_json["simulation"]["plugin_path"])
    os.chdir(sim_path)
    
    cae_name = str(abaqus_json["simulation"]["cae_name"])
    job_name = str(abaqus_json["simulation"]["job_name"])
    
    generate_cae(orientations, material_coefficients, cae_name, job_name, plugin_path)
    write_job(job_name)