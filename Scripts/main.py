# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 08:07:04 2025

@author: chri
"""
import json
from abaqus_runner import abaqus_runner
from abaqus_evaluator import abaqus_evaluator
from pre_process import pre_process
import numpy as np

if __name__ == "__main__":

    # unix
    input_json_path = "/home/chri/w/OntOMat/Workflow/OntOMat_Workflow/Scripts/workflow_input_unix.json"

    with open(input_json_path, 'r') as json_file:
        input_json = json.load(json_file)

    # Call  pre process
    pre_process(input_json, input_json_path)

    # Run simulation
    job_path = str(input_json["simulation"]["sim_path"])
    job_name = str(input_json["simulation"]["job_name"])
    abaqus_cores = int(input_json["simulation"]["abaqus_cores"])

    abaqus_runner(job_path, job_name, abaqus_cores)

    # Evaluate odb
    volume_content = float(input_json["fiber"]["volume_content"])
    fiber_radius = float(input_json["fiber"]["radius"])
    RVE_depth = float(input_json["geometry"]["depth"])

    RVE_b = np.sqrt(np.pi*fiber_radius**2 /
                    (2*volume_content*np.tan(30/180*np.pi)))
    RVE_h = RVE_b*np.tan(30/180*np.pi)
    RVE_volume = 4*RVE_h*RVE_b*RVE_depth

    abaqus_evaluator(input_json, RVE_volume)

    # ...

    # OntOMat upload Node

    # ...

    # /home/chri/w/OntOMat
    # /isi/programs/simulia/2023_1/Commands/abaqus
