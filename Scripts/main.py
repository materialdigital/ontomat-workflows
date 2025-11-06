# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 08:07:04 2025

@author: chri
"""
import json
from abaqus_runner import abaqus_runner
from abaqus_evaluator import abaqus_evaluator
from pre_process_meso import pre_process_meso
from pre_process_micro import pre_process_micro
import numpy as np

if __name__ == "__main__":

    # unix
    input_json_path = "/home/chri/w/OntOMat/Workflow/OntOMat_Workflow/Scripts/workflow_input_unix.json"

    with open(input_json_path, 'r') as json_file:
        input_json = json.load(json_file)

    abq = input_json["simulation"]["abaqus_path"]
    sim_path = input_json["simulation"]["sim_path"]
    job_name = input_json["simulation"]["micro"]["job_name"]
    eval_script_path = input_json["simulation"]["eval_script_path"]
  
    # micro ...
    print("----- Micro Simulation -----")

    # Call  pre process
    print("\n")
    print("Preprocessing...")
    pre_process_micro(input_json, input_json_path)

    # Run simulation
    job_path = str(input_json["simulation"]["sim_path"])
    job_name_micro = str(input_json["simulation"]["micro"]["job_name"])
    abaqus_cores = int(input_json["simulation"]["abaqus_cores"])

    print("\n")
    print("Starting simulation...")
    abaqus_runner(job_path, job_name_micro, abaqus_cores)

    # Evaluate odb
    volume_content = float(input_json["micro"]["fiber"]["volume_content"])
    fiber_radius = float(input_json["micro"]["fiber"]["radius"])
    RVE_depth = float(input_json["micro"]["geometry"]["depth"])

    RVE_b = np.sqrt(np.pi*fiber_radius**2 /
                    (2*volume_content*np.tan(30/180*np.pi)))
    RVE_h = RVE_b*np.tan(30/180*np.pi)
    RVE_volume = 4*RVE_h*RVE_b*RVE_depth

    print("\n")
    print("Starting evaluation...")
    abaqus_evaluator(abq, sim_path, job_name_micro, eval_script_path, RVE_volume)

    print("\n")
    print("... finished Micro Simulation!")

    # ...

    # OntOMat upload Node

    # ...

    ###### ---------------------------------------------------------

    # meso ...
    print("\n")
    print("\n")
    print("----- Meso Simulation -----")

    # Call  pre process
    print("\n")
    print("Preprocessing...")
    pre_process_meso(input_json, input_json_path)

    # Run simulation
    job_path = str(input_json["simulation"]["sim_path"])
    job_name_meso = str(input_json["simulation"]["meso"]["job_name"])
    abaqus_cores = int(input_json["simulation"]["abaqus_cores"])

    print("\n")
    print("Starting simulation...")
    abaqus_runner(job_path, job_name_meso, abaqus_cores)

    # Evaluate odb
    RVE_volume = 1

    print("\n")
    print("Starting evaluation...")
    abaqus_evaluator(abq, sim_path, job_name_meso, eval_script_path, RVE_volume)

    print("\n")
    print("... finished Meso Simulation!")

    # ...

    # OntOMat upload Node

    # ...




    # /home/chri/w/OntOMat
    # /isi/programs/simulia/2023_1/Commands/abaqus
