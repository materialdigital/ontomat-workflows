# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 08:07:04 2025

@author: chri
"""
import json
from abaqus_runner import abaqus_runner
from pre_process import pre_process

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

    # ...

    # OntOMat upload Node

    # ...

    # /home/chri/w/OntOMat
    # /isi/programs/simulia/2023_1/Commands/abaqus
